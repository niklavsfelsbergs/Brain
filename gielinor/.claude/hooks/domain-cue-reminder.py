#!/usr/bin/env python
# domain-cue-reminder.py — make the domain-knowledge-grounding precondition FIRE,
# for ANY registered domain. The generalized successor to shipping-cue-reminder.py.
#
# Failure class (verified live, S124): the agent did domain work that has a
# canonical knowledge home (the shipping_mart, whose contract lives in
# shipping-agent/reference/) without loading that home — reasoned from memory and
# got it wrong (mislabeled OML surcharges as "billing errors"; speculated about
# whether the mart carries dimensions when tables.md answers it in one line). The
# knowledge guarantee is baked into a SUB-AGENT config or a docs/ folder; the
# PRINCIPAL path has no equivalent trigger, and pointers in keepsake/CLAUDE.md are
# passive. Capture is saturated; **triggering** was the gap — and that exact
# lesson was already in memory (S124 "read the reference") yet recurred, which is
# why the fix is a hook, not another note.
#
# This UserPromptSubmit hook is the trigger. It reads `cue_registry.py` (the
# domain table) and, on any domain's cue match, injects a short, NON-BLOCKING
# reminder to load that domain's knowledge home (or spawn its specialist).
#
# Design (mirrors grounding-cue, per the brain's verify-enforcement-fires ethos):
#   - cue match is the load-bearing path; advisory only (additionalContext), never
#     blocks (exit 0 always). A missed nudge costs nothing; a crash that ate a
#     prompt would be the real harm — so every parse/IO failure exits 0 silently.
#   - per-entry actor scope: an entry skips its own skip_actors (default skips
#     dev-brain / braindead) via the per-session status sidecar.
#   - ONE combined nudge: if several domains match the same prompt, emit a single
#     additionalContext block (the entries joined), not N stacked blocks — stacking
#     is how advisories become wallpaper (grounding-cue's §6 over-trust risk).
#
# DISTINCT from grounding-cue-reminder.py: that one is the *identity* reflex
# (continuation cue -> your OWN past work). This one is the *domain* reflex (topic
# -> its external knowledge home). grounding-cue is left untouched.

import json
import os
import re
import sys
from pathlib import Path

# Ritual analytics — best-effort; never breaks the hook.
_SB = Path(__file__).resolve().parents[3] / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k): pass

# The domain table. Import defensively — a broken/missing registry must not break
# the hook (it just means no domain fires).
try:
    from cue_registry import DOMAINS
except Exception:
    DOMAINS = []

STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"


def _compiled():
    """Compile each domain's patterns once. Bad patterns drop that entry, not the hook."""
    out = []
    for d in DOMAINS:
        try:
            rx = re.compile("|".join(d["patterns"]), re.IGNORECASE)
        except Exception:
            continue
        out.append((d, rx))
    return out


def _actor_for(sid8: str) -> str:
    """Read the per-session status sidecar to learn the active actor. '' if unknown."""
    if not sid8:
        return ""
    try:
        data = json.loads((STATUS_DIR / f"{sid8}.json").read_text(encoding="utf-8"))
        return (data.get("actor") or "").lower()
    except (OSError, ValueError):
        return ""


def _emit(blocks: list) -> None:
    """blocks: list of (name, message). Emit ONE combined additionalContext."""
    if len(blocks) == 1:
        msg = blocks[0][1]
    else:
        msg = "Multiple knowledge-home topics detected — ground each before reasoning:\n" + \
              "\n".join(f"- [{name}] {message}" for name, message in blocks)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # can't parse — never disrupt a real prompt

    if payload.get("hook_event_name") not in (None, "UserPromptSubmit"):
        return 0

    prompt = payload.get("prompt") or ""

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    sid8 = sid[:8].lower()
    actor = _actor_for(sid8)

    blocks = []
    for d, rx in _compiled():
        skip = tuple(d.get("skip_actors", ("braindead",)))
        if actor in skip:
            continue
        m = rx.search(prompt)
        if not m:
            continue
        matched = m.group(0).strip()
        name = d.get("name", "domain")
        try:
            message = d["message"].format(matched=matched)
        except Exception:
            message = d.get("message", "")
        blocks.append((name, message))
        log_event(f"domain-cue:{name}", "nudge", sid8=sid8, detail=matched)

    if not blocks:
        return 0  # ordinary prompt — fast, silent pass-through

    _emit(blocks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
