#!/usr/bin/env python
# draft-gate-rewrite.py -- the draft-gate input-rewrite (plan S145 §X.3).
#
# THE GAP THIS CLOSES
#   Two of the brain's draft gates are GUIDED-ONLY -- discipline, not hooks
#   (write-rules.md "What's enforced vs guided", L62-63):
#     * bank/notes/      -- the agent is SUPPOSED to write bank/drafts/notes/ and
#                           let alching promote; a direct bank/notes/ write skips
#                           the gate.
#     * spellbook/skills/ -- same: write spellbook/drafts/skills/, alching promotes.
#   The identity gates (confirmed/) are hook-ENFORCED (block-confirmed-writes.py);
#   these two were left as prose. S145's whole thesis is that decided-to-do rules
#   drift while bright-line hooks hold -- so this converts the two guided gates into
#   GUARANTEES, the same move §X.4 made for the keepsake read.
#
# THE MECHANISM (why rewrite, not block)
#   A PreToolUse input-rewrite: when the main agent writes to a gielinor
#   `bank/notes/` or `spellbook/skills/` path, this hook returns `updatedInput`
#   with the path redirected into the matching `drafts/` home (permissionDecision
#   "allow"), so the write simply LANDS in the right place. A block would make the
#   agent stop and re-issue; a redirect just works -- better ergonomics, and it
#   can't be "argued past." The full tool_input is copied and only the path is
#   changed (updatedInput is a FULL REPLACE -- omitting content/old_string would
#   drop them). Idempotent: a path already under `drafts/` is left untouched.
#
# THE BOUNDARY THAT MATTERS -- DON'T BREAK PROMOTION
#   ALCHING legitimately writes bank/notes/ and spellbook/skills/: promotion IS a
#   write to the canonical home (write-rules.md ritual-reach, alching row). A blind
#   redirect would send every promotion back into drafts/, silently breaking the
#   ritual. So the redirect STANDS DOWN for the paths/contexts where a canonical
#   write is correct:
#     * sub-agents (agent_type set)  -- gnomes RUN alching; their bank/notes/
#       writes are promotions. They also carry their own boundary hooks. Out of
#       scope here: §X.3 governs the PRINCIPAL/player main-agent path, which is
#       where the documented "knowledge written straight to bank/notes/" failure
#       lives (parallel to the domain-cue principal-path fix).
#     * braindead (dev-brain)        -- D-032 full access; construction authoring,
#       not player knowledge accrual.
#     * an active ritual `.mode` marker -- alching/drafts/bankstanding/closing/
#       consultation/wrapped_up. During a tending ritual the agent operates
#       deliberately with write-rules in hand; a bank/notes/ write is a promotion,
#       not a casual mid-session note. (alching is the one that actually promotes;
#       the rest are exempted defensively + for robustness to future ritual edits.)
#
#   Failure-mode calculus: exempting too LITTLE (miss a promotion context) breaks a
#   live ritual -- high blast radius; exempting too MUCH just leaves a stray write
#   ungated == today's guided-only status quo -- harmless. So the exemptions bias
#   wide, and every redirect is logged (draft-gate:redirect) so a mis-fire during a
#   marker-less ritual is observable, not silent.
#
# SCOPE: gielinor paths only (developer-braindead/ has no drafts/notes gate and no
# alching -- excluded by the gielinor-root check AND the braindead actor exempt).
# ADVISORY in spirit: exits 0 always; on any error it falls through to a plain
# allow, exactly like the cue hooks -- a bug here cannot brick a write.

import json
import os
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
GIELINOR_ROOT = HOOK_DIR.parents[1]   # hooks -> .claude -> gielinor
BRAIN_ROOT = HOOK_DIR.parents[2]      # -> brain root

WRITE_TOOLS = ("Edit", "Write", "NotebookEdit", "MultiEdit")

# Shared, hardened actor resolution (status file first, intent-file anchor as the
# anti-race fallback -- the S125 / _actor.py contract).
if str(HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(HOOK_DIR))
try:
    from _actor import resolve_actor
except Exception:
    def resolve_actor(sid8, brain_root=None):
        return ""

# Ritual analytics (Khaan item 11) -- best-effort; never breaks the hook.
_SB = BRAIN_ROOT / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k):
        pass

# A live ritual marker => a canonical write is legitimate (alching promotes).
# Mirrors status-sidecar.py MODE_VALUES.
RITUAL_MODES = {"alching", "drafts", "bankstanding", "closing", "consultation", "wrapped_up"}

# (matched-dir, drafts-dir) pairs, separator-agnostic. Trailing separator pins the
# match to a real directory boundary (bank/notes/ not bank/notesX/).
_REDIRECTS = (
    ("bank", "notes"),        # bank/notes/        -> bank/drafts/notes/
    ("spellbook", "skills"),  # spellbook/skills/  -> spellbook/drafts/skills/
)


def redirect_path(fp: str):
    """Return the drafts-redirected path, or None if no redirect applies.
    Idempotent: a path already carrying `<layer>/drafts/<leaf>/` is left alone."""
    for sep in ("/", "\\"):
        for layer, leaf in _REDIRECTS:
            direct = f"{sep}{layer}{sep}{leaf}{sep}"
            drafts = f"{sep}{layer}{sep}drafts{sep}{leaf}{sep}"
            if direct in fp and drafts not in fp:
                return fp.replace(direct, drafts, 1)
    return None


def in_gielinor(fp: str) -> bool:
    try:
        Path(fp).resolve().relative_to(GIELINOR_ROOT)
        return True
    except (ValueError, OSError):
        return False


def mode_marker(sid8: str) -> str:
    if not sid8:
        return ""
    try:
        return (GIELINOR_ROOT / ".claude" / "intent" / f"{sid8}.mode").read_text(
            encoding="utf-8"
        ).strip().lower()
    except OSError:
        return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # cannot parse -- never disrupt a real write

    if payload.get("tool_name", "") not in WRITE_TOOLS:
        return 0

    # Sub-agents (gnomes run alching = legitimate promotion; they carry their own
    # boundary hooks). §X.3 governs the principal/player main-agent path only.
    if payload.get("agent_type"):
        return 0

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        return 0

    new_path = redirect_path(file_path)
    if not new_path:
        return 0  # not a bank/notes or spellbook/skills write

    if not in_gielinor(file_path):
        return 0  # dev-brain / out-of-tree -- no drafts gate there

    sid8 = (payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or "")[:8].lower()

    # Braindead (dev-brain construction crew) -- D-032 full access.
    if resolve_actor(sid8, BRAIN_ROOT) == "braindead":
        log_event("draft-gate", "bypass-braindead", sid8=sid8, detail=file_path)
        return 0

    # Inside a tending ritual a canonical write is a promotion -- stand down.
    marker = mode_marker(sid8)
    if marker in RITUAL_MODES:
        log_event("draft-gate", "bypass-ritual", sid8=sid8, detail=marker)
        return 0

    # Redirect: copy the whole input (full replace), swap only the path key.
    updated = dict(tool_input)
    if "file_path" in updated:
        updated["file_path"] = new_path
    if "notebook_path" in updated:
        updated["notebook_path"] = new_path

    reason = (
        f"draft-gate (§X.3): redirected to the draft home -- {new_path}. "
        f"bank/notes/ and spellbook/skills/ are promotion-only (alching promotes "
        f"from drafts/); fresh knowledge is written to drafts/ by guarantee, not "
        f"discipline (write-rules.md). Your write LANDED at the drafts path above "
        f"-- read it there, not at the original path."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason,
            "updatedInput": updated,
        }
    }
    sys.stdout.write(json.dumps(out))
    log_event("draft-gate", "redirect", sid8=sid8, detail=f"{file_path} -> {new_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
