#!/usr/bin/env python3
# Architectural guarantee #2: nothing is destroyed; move to archive/ instead.
# Fires PreToolUse on Bash/PowerShell. Scans the command for delete patterns.
# Blocks broadly — running Claude Code inside gielinor/ means delete intent
# is wrong. Use moves to archive/ instead. See meta/archive-discipline.md.

import json
import re
import sys
from pathlib import Path

# Ritual analytics (Khaan item 11) — best-effort; never breaks the hook.
_SB = Path(__file__).resolve().parents[3] / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k): pass

# Braindead full-access grant (2026-06-02, principal-authorized): the dev-brain
# construction crew has UNRESTRICTED edit reach — including deletes — because
# building/maintaining the brain is his role. The floor stays for every other
# actor (players, Guthix, wisp). Resolve via the hardened helper (status->intent
# anti-race); bypass logged so every override is auditable. See write-rules.md.
_HOOK_DIR = Path(__file__).resolve().parent
if str(_HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOK_DIR))
try:
    from _actor import resolve_actor
except Exception:
    def resolve_actor(sid8, brain_root=None): return ""

DELETE_PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9_-])rm(?:\s+-[A-Za-z]+)*\s", re.IGNORECASE),
    re.compile(r"\bremove-item\b", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_-])del\s", re.IGNORECASE),
    re.compile(r"\berase\s", re.IGNORECASE),
    re.compile(r"\bunlink\s", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_-])ri\s+-", re.IGNORECASE),  # PS alias
    re.compile(r"\brmdir\s", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_-])rd\s+-", re.IGNORECASE),
    re.compile(r"\.unlink\(", re.IGNORECASE),
    re.compile(r"shutil\.rmtree\(", re.IGNORECASE),
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"block-deletes: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Bash", "PowerShell"):
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    sid8 = (payload.get("session_id") or "")[:8]
    if resolve_actor(sid8) == "braindead":
        log_event("block-deletes", "bypass-braindead", sid8=sid8, detail=command[:120])
        sys.exit(0)  # construction crew: unrestricted (principal-authorized)

    # Scope guard (2026-06-12): protect ONLY brain paths. The DELETE_PATTERNS match
    # the command string regardless of where the delete LANDS, so a `git rm` / rm in
    # a work repo (e.g. bi-analytics) tripped the guard even though no brain file was
    # at risk. Allow a delete when its effective directory is an absolute path
    # OUTSIDE the brain AND no absolute brain path appears anywhere in the command
    # (the second clause closes a `cd /tmp && rm <brain-path>` leak). Conservative:
    # a relative or unknown cwd is treated as in-brain and stays gated. Drive forms
    # normalized so git-bash `/c/...` and Windows `C:\...` compare alike.
    brain_norm = str(Path(__file__).resolve().parents[3]).replace("\\", "/").lower()

    def _drive(s: str) -> str:
        s = s.replace("\\", "/").lower()
        return re.sub(r"(?:^|(?<=[\s'\"=]))/([a-z])/", r"\1:/", s)  # /c/ -> c:/

    cmd_norm = _drive(command)
    m = re.match(r"\s*(?:cd|set-location|sl)\s+(?:-path\s+)?['\"]?([^'\"&;|]+)",
                 command, re.IGNORECASE)
    eff = _drive(m.group(1).strip().rstrip("/\\")) if m else _drive(payload.get("cwd") or brain_norm)
    if re.match(r"^[a-z]:/", eff) and not eff.startswith(brain_norm) and brain_norm not in cmd_norm:
        log_event("block-deletes", "allow-outside-brain", sid8=sid8, detail=command[:120])
        sys.exit(0)

    for pat in DELETE_PATTERNS:
        if pat.search(command):
            log_event("block-deletes", "block", sid8=(payload.get("session_id") or "")[:8], detail=command[:120])
            print(
                f"BLOCKED: delete operations are disallowed inside the brain.\n"
                f"  Matched pattern: {pat.pattern!r}\n"
                f"  Command: {command[:200]}\n"
                f"  Use a move into the corresponding archive/ instead.\n"
                f"  See meta/archive-discipline.md.",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
