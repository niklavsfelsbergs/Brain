#!/usr/bin/env python
# close-gate-stop.py — Stop-event close-ritual GATE (plan §X.2; the S154 fix is
# its precondition). Layer 2 of the S115 close-enforcement model: turns the
# discipline-run close_check (a markdown ritual step the agent may skip) into a
# mechanical gate that a CLAIMED close cannot pass while gaps remain.
#
# THE SEAM (Niklavs-flagged 2026-06-02)
#   A Stop hook fires on EVERY turn-end, not just at close — most Stops are a
#   mid-work pause where the agent finished a turn and waits for the principal.
#   So the gate must NOT run on every Stop, or it would false-block all in-flight
#   work. The only in-band signal that a close is intended AND claimed-done is the
#   `wrapped_up` `.mode` marker the close ritual writes as its FINAL action. So:
#
#     marker == "wrapped_up"  -> a close-claim. Verify close_check; block on gap.
#     marker == "closing"     -> mid-wrap (may be a legit pause-for-nod) -> ALLOW.
#     any other / absent      -> ordinary mid-work pause -> ALLOW silently.
#
#   This makes false-blocking of in-flight work structurally impossible: the gate
#   only engages once the agent has explicitly declared the session wrapped.
#   "Session ended with no close ritual at all" is a DIFFERENT failure mode owned
#   by session-end-safety-net.py (layer 3, the SessionEnd auto-CLOSING stub) —
#   clean separation: this gate enforces the QUALITY of a claimed close; the
#   safety-net handles the absence of one.
#
# SEVERITY (principal-chosen 2026-06-02, "Block w/ loop-guard")
#   On a wrapped_up-claim FAIL: BLOCK the Stop (exit 2, gaps on stderr) so the
#   agent fixes them and re-claims. But DEGRADE to warn-only (allow, exit 0) when
#   stop_hook_active is set — the session was already force-continued once by this
#   gate, so a second block risks an infinite continue-loop on a gap the agent
#   can't clear (e.g. a sibling's uncommitted shared-lineage file in this
#   parallel git tree — observed live on b82b0b90). One forceful block + the
#   visible gaps is the intervention; the loop-guard guarantees the gate can never
#   trap a session.
#
# RITUAL SELECTION (dev vs player)
#   resolve_actor() returns "unknown" for dev sessions (the status actor is often
#   'unknown' and short-circuits the intent fallback — the S149 truthy bug), so
#   actor alone can't pick the ritual. Layered discriminator instead, biased to
#   recognise dev (a dev session has run close_check step 9 + posted its CLOSING
#   to dev comms BEFORE writing wrapped_up at step 11, so the dev-comms signal is
#   reliable by the time this gate engages); everything else is a gielinor player
#   close, and run_player itself degrades gracefully (no gielinor artifacts -> its
#   own checks report the gap).
#
# FAIL-OPEN: any unexpected error exits 0. A bug here must never brick a session
# or wedge a close — every other brain hook holds this line.

import json
import os
import subprocess
import sys
from pathlib import Path

# gielinor/.claude/hooks -> brain root
BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CLOSE_CHECK = BRAIN_ROOT / "developer-braindead" / "verification" / "close_check.py"
DEV_COMMS = BRAIN_ROOT / "developer-braindead" / "comms" / "active.md"

# Both intent dirs: dev (Braindead) markers land in the brain-root .claude/intent,
# gielinor player markers in gielinor/.claude/intent — and the location scatters
# with the session's CWD (a dev session has been seen writing to the gielinor
# dir). Check both so close-detection is robust to where the marker actually
# landed; the freshest by mtime wins if both exist.
INTENT_DIRS = (
    BRAIN_ROOT / ".claude" / "intent",
    BRAIN_ROOT / "gielinor" / ".claude" / "intent",
)

CLOSE_CLAIM_MARKER = "wrapped_up"

# Ritual analytics (Khaan item 11) — best-effort; never breaks the hook.
_SB = BRAIN_ROOT / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k):  # noqa: D401 — best-effort no-op
        pass


def _read_mode_marker(sid8: str) -> str:
    """The `<sid8>.mode` value, searching both intent dirs; freshest wins.
    '' if no marker exists (the common mid-work case)."""
    if not sid8:
        return ""
    best, best_mtime = "", -1.0
    for d in INTENT_DIRS:
        p = d / f"{sid8}.mode"
        try:
            if not p.is_file():
                continue
            mtime = p.stat().st_mtime
            val = p.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if mtime > best_mtime:
            best, best_mtime = val, mtime
    return best


def _detect_ritual(sid8: str) -> str:
    """'dev' or 'player', from PER-SESSION signals only. Biased to recognise a
    dev (Braindead) close reliably; everything else routes to the gielinor player
    ritual (which itself degrades gracefully on a non-player sid8).

    Deliberately does NOT consult active-mode.txt: that marker is GLOBAL, so a
    parallel live dev session (active-mode='dev-brain') would misclassify a
    concurrently-closing PLAYER session as dev and spuriously block it. The two
    per-session signals below are sufficient — a dev close has posted its OPEN +
    CLOSING to dev comms BEFORE writing wrapped_up (close_check is step 9, the
    marker is step 11), so the dev-comms signal is reliable by the time this gate
    engages."""
    # 1. Live dev intent anchor (this session's own braindead-<sid8>.txt).
    try:
        if (INTENT_DIRS[0] / f"braindead-{sid8}.txt").is_file():
            return "dev"
    except OSError:
        pass
    # 2. This session posted to dev comms (its CLOSING lands there before wrapped_up).
    try:
        if f"braindead-{sid8}" in DEV_COMMS.read_text(encoding="utf-8", errors="replace"):
            return "dev"
    except OSError:
        pass
    return "player"


def _run_close_check(sid8: str, ritual: str):
    """(exit_code, combined_output). Returns (0, '') if close_check is missing or
    errors — fail-open: an infra problem must never wedge a close."""
    if not CLOSE_CHECK.is_file():
        return 0, ""
    cmd = [sys.executable, str(CLOSE_CHECK), "--sid8", sid8]
    if ritual == "player":
        cmd += ["--ritual", "player"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except Exception:
        return 0, ""
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # unparseable — never wedge a stop

    if payload.get("hook_event_name") not in (None, "Stop"):
        return 0

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    sid8 = sid[:8].lower()
    if not sid8:
        return 0

    # THE SEAM: only a wrapped_up close-claim engages the gate. Every ordinary
    # turn-end (no marker, mid-wrap 'closing', a flavor tag) passes straight
    # through — the gate cannot touch in-flight work.
    if _read_mode_marker(sid8) != CLOSE_CLAIM_MARKER:
        return 0

    ritual = _detect_ritual(sid8)
    code, out = _run_close_check(sid8, ritual)

    if code == 0:
        log_event("close-gate", "allow", actor=ritual, sid8=sid8)
        return 0  # clean close-claim — let it stop

    stop_hook_active = bool(payload.get("stop_hook_active"))
    if stop_hook_active:
        # Already force-continued once by this gate — degrade to warn so a gap the
        # agent can't clear can't trap the session in an infinite continue-loop.
        log_event("close-gate", "degrade", actor=ritual, sid8=sid8)
        sys.stderr.write(
            "CLOSE-GATE (warn -- already continued once): close_check still reports gaps "
            f"for {sid8} ({ritual} ritual). Not re-blocking to avoid a loop, but the close "
            "is NOT clean -- fix these before relying on it:\n" + (out or "(no detail)") + "\n"
        )
        return 0

    # First block: the agent claimed wrapped_up but close_check found gaps.
    log_event("close-gate", "block", actor=ritual, sid8=sid8)
    sys.stderr.write(
        "BLOCKED: you wrote the `wrapped_up` close-claim but close_check reports the "
        f"session is NOT cleanly closed ({ritual} ritual, session {sid8}).\n"
        "Do NOT leave the session declared wrapped with these gaps -- fix them, re-commit "
        "if needed, and the gate clears on the next stop:\n\n" + (out or "(no detail)") + "\n\n"
        "(plan X.2 Stop-gate -- a claimed close can't pass with an unresolved gap. "
        "If a gap is a sibling's in-flight file you can't own, note it and stop again; "
        "the loop-guard releases on the second stop.)\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
