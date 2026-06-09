#!/usr/bin/env python
# keepsake-forced-read.py -- the forced-read injection (plan S145 §X.4).
#
# THE GAP THIS CLOSES
#   The respawn ritual SAYS "read keepsake/current.md + the active resume" -- but a
#   ritual step is DISCIPLINE, and discipline drifts (S145: the brain gets dumber as
#   it gets richer; bright-line rules hold, decided-to-act rules drift). The proof is
#   regression case 7 (S145): a scout reported keepsake "empty" and it was repeated
#   WITHOUT opening the file -- inside the very session auditing that failure. Naming
#   a read does not force it. The just-shipped `Reading:` line (§X.10) only NAMES the
#   read at the Plan line (R3, visible-not-enforced). THIS hook is its enforced
#   pairing: it injects the keepsake CONTENTS into context (a guarantee, not a name)
#   + a directive to read the relevant resume. The "+39% memory-tool forcing" analog
#   from the field research -- inject the directive, the behavior follows.
#
# TWO ARMS (both ADVISORY -- additionalContext, exit 0 ALWAYS; a bug cannot brick a
# session, exactly like grounding-cue / domain-cue):
#   SessionStart      -> inline the GLOBAL keepsake (player-agnostic, known now) +
#                        the forcing directive. Fires for every session start
#                        (startup/resume/clear/compact); self-conditional for
#                        dev-brain (the actor is unknown at SessionStart).
#   UserPromptSubmit  -> ONCE per session, when the actor is resolvable, inline the
#                        ACTIVE player's keepsake/current.md AND their always-read
#                        bank/domains/_index.md work-domain map (§Z.B). This is the
#                        genuine force for the player layer -- the content is literally
#                        in context, so "this layer is empty" becomes a checkable claim.
#
# THE DOMAIN-INDEX ARM (§Z.B -- the "just knows the map" guarantee). A player's
# bank/domains/_index.md is the always-read map of their work domains (one line each);
# the per-domain DIGESTS are cue-loaded separately (§Z.C). Like the keepsake, the index
# is force-inlined every session so the player always knows the lay of their own land.
# Per-player (resolvable only once the actor is named) -> it rides the UserPromptSubmit
# arm beside the keepsake, in the SAME single emission, under the same once-per-session
# sentinel. Budget-capped (INDEX_BYTE_CAP): an over-cap index has bloated into
# digest-territory -> fall back to NAMING it (the digests belong cue-loaded, not here).
#
# WHY a second arm: SessionStart cannot know the player (the address arrives in the
# first message, after SessionStart). The global keepsake is player-agnostic so it
# loads at SessionStart; the per-player keepsake loads on the first prompt once
# resolve_actor() (the S125 hardened status->intent path) can name the actor.
#
# SCOPE: gielinor players (jebrim/zezima) + Guthix bear a keepsake; unscoped/wisp
# carry only the global one (covered at SessionStart); Braindead (dev-brain) is
# skipped -- it has no keepsake, respawn.md governs it.
#
# PAIRING: complements domain-cue (topic -> external knowledge home) and
# grounding-cue (continuation -> own past work). This one = standing context (pins +
# resume) forced in at session start. Fill keepsake/current.md to make the forced
# read worth obeying -- principal/alching work, not this hook's job.

import json
import os
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
BRAIN_ROOT = HOOK_DIR.parents[2]  # gielinor/.claude/hooks -> brain root

# Shared, hardened actor resolution (status file first, intent-file anchor as the
# anti-race fallback -- the S125 / _actor.py contract; reading status alone would
# re-open the S124 sidecar-lag race).
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

STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"
GLOBAL_KEEPSAKE = BRAIN_ROOT / "gielinor" / "keepsake" / "current.md"

# Actors that bear a keepsake (beyond the global one) -> their current.md.
PLAYER_KEEPSAKE = {
    "jebrim": BRAIN_ROOT / "gielinor" / "players" / "jebrim" / "keepsake" / "current.md",
    "zezima": BRAIN_ROOT / "gielinor" / "players" / "zezima" / "keepsake" / "current.md",
    "guthix": BRAIN_ROOT / "gielinor" / "deities" / "guthix" / "keepsake" / "current.md",
}

# The always-read domain map rides beside the keepsake (§Z.B). An index over this cap
# has bloated past a map into digest-territory -> name it instead of inlining (the
# digests load cue-side, §Z.C). The _about.md budget is "one line per domain".
INDEX_BYTE_CAP = 4000

# Actors with no per-player keepsake (global, injected at SessionStart, suffices) --
# distinct from "" (unresolved, retry) so we don't keep re-firing on these. They
# still get NO sentinel set, so a later player-address (mini-respawn) can inject.
NO_PLAYER_KEEPSAKE = {"unscoped", "wisp", "guthix-wisp"}

DIRECTIVE = (
    "FORCED-READ (S145 §X.4 -- the hook half of the `Reading:` line). Before "
    "substantive work in a gielinor player / unscoped / Guthix session: read the "
    "active player's keepsake/current.md (its pins are in force this session) AND the "
    "most recent relevant inventory/*-resume file for the work in hand. Treat any "
    "claim that a layer is empty / absent as a HYPOTHESIS to verify against the file "
    "before repeating it (regression S145 case 7 -- a scout's 'keepsake empty' was "
    "echoed without opening the file, which was full). Dev-brain (Braindead) sessions "
    "follow developer-braindead/respawn.md instead."
)


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _keepsake_block(label: str, body: str) -> str:
    """Render a keepsake for injection. An empty/placeholder file is surfaced AS
    present-but-empty -- that itself counters a false 'this layer is absent' claim
    (and self-heals the moment the principal fills it: this reads the file live)."""
    is_empty = (not body) or ("*(empty" in body) or ("*(empty—" in body)
    if is_empty:
        return f"[{label} keepsake/current.md -- present, no pins yet]"
    return f"[{label} keepsake/current.md -- pinned, in force this session]\n{body}"


def _domains_index(kp: Path) -> Path:
    """The active player's domain map lives beside the keepsake:
    <player_root>/keepsake/current.md -> <player_root>/bank/domains/_index.md.
    Deriving it (vs a second map) means a new domains layer needs no hook edit."""
    return kp.parents[1] / "bank" / "domains" / "_index.md"


def _domains_block(label: str, body: str) -> str:
    return (f"[{label} bank/domains/_index.md -- your always-read work-domain map; "
            f"per-domain digests load on cue]\n{body}")


def _emit(event: str, text: str) -> None:
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}
    sys.stdout.write(json.dumps(out))


def _session_start(payload: dict, sid8: str) -> int:
    # Sub-agent SessionStart (--agent) gets no keepsake injection -- sub-agents read
    # the brief, not the principal's standing context.
    if payload.get("agent_type"):
        return 0
    gk = _read(GLOBAL_KEEPSAKE)
    _emit("SessionStart", DIRECTIVE + "\n\n" + _keepsake_block("Global", gk))
    log_event("forced-read", "session-start", sid8=sid8)
    return 0


def _user_prompt(payload: dict, sid8: str) -> int:
    # No user-prompt path for sub-agents; defensive skip.
    if payload.get("agent_type"):
        return 0
    sentinel = (STATUS_DIR / f"{sid8}.fread") if sid8 else None
    if sentinel and sentinel.exists():
        return 0  # already injected this session

    actor = resolve_actor(sid8, BRAIN_ROOT)
    # Unresolved (sidecar race) or non-keepsake actor -> stay silent and DO NOT set
    # the sentinel, so a later turn (actor settled, or a mid-session player switch)
    # still gets its inject.
    if actor in ("", "braindead") or actor in NO_PLAYER_KEEPSAKE:
        return 0
    kp = PLAYER_KEEPSAKE.get(actor)
    if kp is None:
        return 0  # unknown actor -> global (SessionStart) already covered it

    label = actor.capitalize()
    blocks = [_keepsake_block(label, _read(kp))]

    # Domain-index arm (§Z.B): inline the player's always-read work-domain map in the
    # SAME emission, budget-capped. Missing file (zezima/guthix with no domains yet) ->
    # _read returns "" -> skipped cleanly. Over-cap -> name it, don't inline.
    di_body = _read(_domains_index(kp))
    if di_body:
        if len(di_body.encode("utf-8")) <= INDEX_BYTE_CAP:
            blocks.append(_domains_block(label, di_body))
            log_event("forced-read", "domain-index", sid8=sid8, detail=actor)
        else:
            blocks.append(f"[{label} bank/domains/_index.md -- present but over "
                          f"budget ({len(di_body.encode('utf-8'))}B); read it directly]")
            log_event("forced-read", "domain-index-overbudget", sid8=sid8, detail=actor)

    _emit("UserPromptSubmit", "\n\n".join(blocks))
    log_event("forced-read", "player-inject", sid8=sid8, detail=actor)
    try:
        if sentinel:
            sentinel.parent.mkdir(parents=True, exist_ok=True)
            sentinel.write_text("1", encoding="utf-8")
    except OSError:
        pass
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # cannot parse -- never disrupt a real prompt / session

    event = payload.get("hook_event_name")
    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    sid8 = sid[:8].lower()

    if event == "SessionStart":
        return _session_start(payload, sid8)
    if event in (None, "UserPromptSubmit"):
        return _user_prompt(payload, sid8)
    return 0


if __name__ == "__main__":
    sys.exit(main())
