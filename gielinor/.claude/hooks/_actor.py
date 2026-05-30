#!/usr/bin/env python
"""_actor.py -- shared session-actor resolution for actor-keyed PreToolUse hooks.

Extracted from require-open-on-entry.py (the S125 fix) so the hardened
resolution is ONE reusable path instead of being re-implemented per hook.

THE RACE THIS CLOSES (S124 / 61d62e21)
  The status file (~/.claude/status/<sid8>.json) is written by a SEPARATE
  sidecar that can LAG the first write of a "Hey Jebrim"-straight-into-task
  session. A hook that resolves the actor from the status file ALONE gets ''
  during that window, and an actor-keyed gate then fails open SILENTLY (the
  S124 hole: 3 brain files written, no OPEN, zero telemetry). The per-session
  intent file `.claude/intent/<actor>-<sid8>.txt` is the documented on-disk
  session anchor (communication-protocol.md -> Intent narration); recover the
  actor from its filename prefix before giving up.

CONTRACT FOR NEW HOOKS
  Any new hook that needs the session actor MUST call resolve_actor() rather
  than reading the status file directly -- reading status alone re-introduces
  the S124 race (audit finding #2, the actor-race class). resolve_actor()
  returns '' only when genuinely unresolved; the CALLER should log a
  skip-noactor event on '' so the fail-open stays VISIBLE (instrument, don't
  re-guess), exactly as require-open-on-entry.py does.

  Boundary hooks (dwarf/gnome/penguin/shipping-agent) gate on payload
  `agent_type`, NOT on the session actor, so they do not need this helper and
  have no empty-actor hole -- left as-is by design.
"""
import json
import os
from pathlib import Path

# gielinor/.claude/hooks/_actor.py -> brain root
BRAIN_ROOT = Path(__file__).resolve().parents[3]
STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"


def actor_from_status(sid8: str) -> str:
    """Authoritative once the sidecar has settled; '' while it lags."""
    if not sid8:
        return ""
    try:
        data = json.loads((STATUS_DIR / f"{sid8}.json").read_text(encoding="utf-8"))
        return (data.get("actor") or "").lower()
    except (OSError, ValueError):
        return ""


def actor_from_intent(sid8: str, brain_root: Path = BRAIN_ROOT) -> str:
    """Disk fallback -- the per-session intent file is the on-disk session
    anchor. Actor names carry no hyphen, so rsplit on the trailing -<sid8> is
    safe."""
    if not sid8:
        return ""
    try:
        intent_dir = brain_root / ".claude" / "intent"
        for f in intent_dir.glob(f"*-{sid8}.txt"):
            actor = f.name[:-4].rsplit("-", 1)[0].lower()  # drop '.txt', take prefix
            if actor:
                return actor
    except OSError:
        return ""
    return ""


def resolve_actor(sid8: str, brain_root: Path = BRAIN_ROOT) -> str:
    """Status file first (authoritative when settled), intent-file anchor as the
    anti-race fallback. Returns '' only when genuinely unresolved."""
    return actor_from_status(sid8) or actor_from_intent(sid8, brain_root)
