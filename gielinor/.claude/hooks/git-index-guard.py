#!/usr/bin/env python3
"""
git-index-guard.py — PreToolUse gate on Bash/PowerShell (severity-audit S1).

Closes the #1 finding: the shared git index is fully ungated. One tree, one
index, N parallel Claude sessions. A bare `git add -A` stages every dirty file
across ALL sessions (124 dirty when the audit ran); `git commit -a` sweeps a
sibling's staged WIP into the wrong commit (the S118 shared-index clobber).

Design — NARROW and high-precision by doctrine. A guard that false-blocks gets
routed around and is worse than none. It blocks only the unambiguous
"stage everything" footguns and ALLOWS everything else, including the normal
`git commit -m "..."` (which commits only what's already staged) and any
explicit-pathspec `git add`.

BLOCK (exit 2) only:
  * `git add` with -A / --all / a bare `.` pathspec / `:/`
    (`git add -A`, `git add --all`, `git add .`, `git add -- .`, `git add -A .`)
  * `git commit` with -a / --all / -am / -a -m (stages+commits all tracked)

ALLOW (exit 0) everything else:
  `git add <explicit path>`, `git commit -m "..."` without -a,
  `git commit -- <pathspec>`, git status/log, any non-git command, and any
  command where `git add -A` etc. appears only inside a commit MESSAGE.

Detection: split the command into segments on && / ; / | (chaining like
`cd x && git add -A`), then test each segment's LEADING git invocation —
anchored on the git subcommand + flags, not arbitrary substring — so
`git commit -m "git add -A in the message"` does NOT match on the message text.

ESCAPE: env var GIT_BARE_OK=1 stands the guard down (mirrors
comms-append-guard's COMMS_ROTATE) — for the rare legitimate `git add -A`.

Fail-OPEN on any malformed payload — a guard must never hard-block real work on
a parse fluke.
"""
import sys
import json
import os
import re

# --- ritual analytics (item 11, S121); never let logging break the hook ---
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "switchboard"))
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k):
        pass


def _sid8():
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    return sid[:8] if sid else ""


def _payload():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return None


# A segment that *starts* with a git add whose flags/pathspec stage everything.
# ^\s* — only the leading invocation of the segment (anchored, not substring).
# Then `git add`, then any run of options, and somewhere in the option run an
# -A / --all / a bare `.` / `:/` pathspec.
_GIT_ADD_ALL = re.compile(
    r"""^\s*git\s+add\b           # leading `git add`
        (?=                       # the rest of the invocation must contain...
            (?:\s+\S+)*            #   ...somewhere in its tokens
            \s+(?:-A\b|--all\b|\.(?=\s|$)|--\s+\.(?=\s|$)|:/\b)
        )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# A segment that *starts* with a git commit carrying -a/--all/-am (stage-all).
# Matches `-a`, `--all`, `-am`, `-amend`-style only if it's the -a/-m cluster,
# and combined short clusters like `-am`. Anchored on the leading invocation.
_GIT_COMMIT_ALL = re.compile(
    r"""^\s*git\s+commit\b
        (?=
            (?:\s+\S+)*
            \s+(?:
                --all\b                       # --all
                | -[A-Za-z]*a[A-Za-z]*\b      # any short cluster containing 'a' (-a, -am, -ma, -av)
            )
        )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# Strip single/double-quoted spans so a commit message can never be scanned for
# flags or pathspecs: `git commit -m "git add -A"` must read as a plain commit.
# Replace each quoted span with a single space (token boundary preserved).
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")


def _strip_quotes(s):
    return _QUOTED.sub(" ", s)


def _segments(command):
    # Split on chaining/sequencing operators so each segment's first token is
    # the actual command being run, not text inside a prior command's quotes.
    # We split on && || ; | & — the leading-anchor regex then guards against
    # matching anything that isn't the segment's leading git invocation.
    parts = re.split(r"&&|\|\||[;|&]", command)
    return [p for p in parts if p.strip()]


def _danger(command):
    """Return the offending segment if the command stages-everything, else None."""
    for seg in _segments(command):
        # Test against a quote-stripped copy so message text never false-matches,
        # but report the original segment for a readable error.
        bare = _strip_quotes(seg)
        if _GIT_ADD_ALL.search(bare) or _GIT_COMMIT_ALL.search(bare):
            return seg.strip()
    return None


def main():
    payload = _payload()
    if payload is None:
        sys.exit(0)  # malformed -> allow (fail-open)

    tool = payload.get("tool_name", "")
    if tool not in ("Bash", "PowerShell"):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command", "")
    if not command:
        sys.exit(0)

    # Escape — a deliberate stage-everything, opted into per command.
    if os.environ.get("GIT_BARE_OK"):
        sys.exit(0)

    seg = _danger(command)
    if not seg:
        sys.exit(0)

    log_event("git-index-guard", "block", sid8=_sid8(), detail=seg[:120])
    sys.stderr.write(
        "\n[git-index-guard] Blocked a stage-everything git command. The git "
        "index is SHARED across all parallel sessions in this one tree — a bare "
        "`git add -A` / `git add .` / `git commit -a` stages every dirty file "
        "across every session and clobbers siblings' WIP into the wrong commit "
        "(the S118 shared-index clobber).\n"
        "Stage explicitly instead:\n"
        "  git add <path> [<path> ...]        # only your files\n"
        "  git commit -m \"...\"                # commits only what's already staged\n"
        "  git commit -- <pathspec>           # commits a specific path\n"
        f"  offending segment: {seg}\n"
        "If you genuinely need to stage everything, re-run with GIT_BARE_OK=1 set.\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
