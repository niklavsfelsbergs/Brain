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
    """The on-disk session anchor -- the `<actor>-<sid8>.txt` intent bubble the
    agent writes. Actor names carry no hyphen, so rsplit on the trailing -<sid8>
    is safe.

    Reads BOTH intent dirs (S181 fix): intent `.txt` files scatter between
    brain-root `.claude/intent` (dev/Braindead, written with CWD=brain root) and
    `gielinor/.claude/intent` (gielinor player markers) exactly as the `.mode`
    markers do -- status-sidecar.py already learned this with MODE_INTENT_DIRS
    (S155). Reading one dir silently missed a bubble in the other, leaving the
    intent fallback half-dead. **Freshest by mtime wins** across both dirs: a
    mid-session actor switch (jebrim -> braindead pivot) leaves two bubbles for
    one sid8, and the newest one is the CURRENT actor."""
    if not sid8:
        return ""
    dirs = (brain_root / ".claude" / "intent",
            brain_root / "gielinor" / ".claude" / "intent")
    best_actor, best_mtime = "", -1.0
    for intent_dir in dirs:
        try:
            for f in intent_dir.glob(f"*-{sid8}.txt"):
                actor = f.name[:-4].rsplit("-", 1)[0].lower()  # drop '.txt', take prefix
                if not actor:
                    continue
                try:
                    mt = f.stat().st_mtime
                except OSError:
                    mt = 0.0
                if mt > best_mtime:
                    best_actor, best_mtime = actor, mt
        except OSError:
            continue
    return best_actor


def resolve_actor(sid8: str, brain_root: Path = BRAIN_ROOT) -> str:
    """Intent-anchor first, status file as the fallback. Returns '' only when
    genuinely unresolved.

    **Flipped from status-first 2026-06-09 (S181).** The sidecar-written status
    is a lagging heuristic: when a session has no intent bubble yet, the sidecar
    falls to a `state-instances.json` byId lookup whose tiebreaker is *highest
    instance number*, which mis-picked `braindead`(4) over `jebrim`(3) for a
    "Hey Jebrim" session that had pivoted -- then the gate trusted that wrong
    status over the agent's own intent declaration and blocked writes against
    the wrong comms. The intent bubble is the agent's authoritative, real-time
    self-identification; status only fills the gap before the bubble is written.
    This aligns the shared resolver WITH status-sidecar.py's own intent-first
    `_detect_actor` ordering rather than diverging from it."""
    return actor_from_intent(sid8, brain_root) or actor_from_status(sid8)
