#!/usr/bin/env python
# shipping-cue-reminder.py — make the shipping-agent-knowledge precondition FIRE.
#
# Failure class (verified live, S-this): the agent did mart work (the automated
# shipping report) as Jebrim-PRINCIPAL without loading the shipping-agent's
# reference — speculated about whether the mart even carries dimensions when
# `tables.md` answers it in one line. The knowledge guarantee is baked into the
# shipping-agent SUB-AGENT config ("Read first: how_to.md in full"); the PRINCIPAL
# path has no equivalent trigger, and the keepsake pointer is passive. Capture is
# saturated (the whole shipping-agent reference/ exists); triggering was the gap.
#
# This UserPromptSubmit hook is the trigger — a direct sibling of
# grounding-cue-reminder.py. On a shipping/mart cue it injects a short,
# NON-BLOCKING reminder to load the rulebook (or spawn the shipping-agent, which
# loads it by construction) before writing SQL or interpreting any mart figure.
#
# Design (mirrors grounding-cue, per the brain's verify-enforcement-fires ethos):
#   - cue match is the load-bearing path; advisory only (additionalContext), never
#     blocks (exit 0 always). A missed nudge costs nothing; a crash that ate a
#     prompt would be the real harm.
#   - gielinor-scoped: skips dev-brain (actor == "braindead") via the per-session
#     status sidecar — Braindead builds the brain, not mart analysis.
#   - narrow cue set on purpose: a false positive costs one advisory line, but
#     over-firing makes the reminder wallpaper (grounding-cue's §6 over-trust risk).

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

STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"

# Shipping/mart cue patterns (case-insensitive, word-boundaried where it matters).
# Narrow on purpose. Bare "report" / "cost" are deliberately EXCLUDED — too broad,
# that's how a nudge becomes wallpaper.
_CUE_PATTERNS = [
    r"\bshipping\b",
    r"\bshipment",                       # shipment, shipments
    r"\bmart\b", r"shipping[_ -]?mart",
    r"\bcarrier",                        # carrier, carriers
    r"\bparcel",
    r"\bfreight\b",
    r"\bsurcharge",
    r"\bgirth\b", r"\boversize",
    r"\btender\b",                       # EU carrier tender work
    r"\b(LPS|OML)\b",
    # carrier names — unambiguous tokens, word-boundaried
    r"\b(UPS|DHL|DPD|GLS|USPS|FedEx|Maersk|Asendia|OnTrac|Yodel|Hermes|Schenker|ORWO|Picturator|PicaAPI)\b",
]
_CUE_RE = re.compile("|".join(_CUE_PATTERNS), re.IGNORECASE)


def _actor_for(sid8: str) -> str:
    """Read the per-session status sidecar to learn the active actor. '' if unknown."""
    if not sid8:
        return ""
    try:
        data = json.loads((STATUS_DIR / f"{sid8}.json").read_text(encoding="utf-8"))
        return (data.get("actor") or "").lower()
    except (OSError, ValueError):
        return ""


def _emit(matched: str) -> None:
    msg = (
        f'Shipping/mart topic detected ("{matched}"). Before writing SQL or '
        "interpreting any shipping_mart figure: load `shipping-agent/how_to.md` §0 "
        "+ `reference/{mart-contract,tables}.md`, OR spawn the shipping-agent "
        "(subagent_type: shipping-agent), which loads the rulebook by construction. "
        "Don't reason about the mart from memory — the contract holds the cost-basis "
        "rules, schema (incl. dims / length_plus_girth_cm), and DQ quirks. "
        "(sibling of grounding-cue; see skill calling-the-shipping-agent.)"
    )
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

    # Scope: skip dev-brain (Braindead builds the brain, not mart analysis).
    if _actor_for(sid8) == "braindead":
        return 0

    m = _CUE_RE.search(prompt)
    if not m:
        return 0  # ordinary prompt — fast, silent pass-through

    matched = m.group(0).strip()
    _emit(matched)
    log_event("shipping-cue", "nudge", sid8=sid8, detail=matched)
    return 0


if __name__ == "__main__":
    sys.exit(main())
