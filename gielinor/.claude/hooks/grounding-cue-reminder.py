#!/usr/bin/env python
# grounding-cue-reminder.py — make the grounding-precondition FIRE (B-009 land of
# the B-008 godly proposal; decision D-028).
#
# The grounding-precondition (read active context + confirm the referent before
# producing substantive output) is confirmed globally (examine "G1"), graduated
# at B-007 from two independent player instances, and stored in memory — yet it
# reproduced 3x (S066/S076/S095), every time on a session/turn that opened with a
# CONTINUATION CUE ("again", "back to", "the X I prepared earlier"). Capture is
# saturated; triggering was the gap. This UserPromptSubmit hook is the trigger:
# on a cue match it injects a short, NON-BLOCKING reminder to check the player's
# own bank/notes/research/quest-log before analyzing.
#
# Design (per the proposal + the brain's verify-enforcement-fires ethos):
#   - cue match is the LOAD-BEARING path; artifact detection (S192, VERIFIED)
#     matches the upload PLACEHOLDERS Claude Code inserts into the prompt text —
#     see the _ARTIFACT_RE note for the verification trail.
#   - advisory only: emits additionalContext, never blocks (exit 0 always).
#   - gielinor-scoped: skips dev-brain (actor == "braindead") via the per-session
#     status sidecar; everything else (players, Guthix, wisp) fires.
#   - defensive by construction: any parse/IO failure exits 0 silently. A missed
#     nudge costs nothing; a crash that ate a prompt would be the real harm.

import json
import os
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

STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"

# Continuation-cue patterns (case-insensitive, word-boundaried where it matters).
# Narrow on purpose — a false positive costs one advisory line; over-firing makes
# the reminder wallpaper (the proposal's §6 over-trust risk).
_CUE_PATTERNS = [
    r"\bonce again\b",
    r"\bagain[,\s]",
    r"\bback to\b",
    r"\bsome more\b",
    r"\bafter\s?all\b",
    # prepared/earlier-content forms: "the report I prepared earlier", "the deck I built before"
    r"\bthe\b.{0,30}\b(prepared|made|wrote|built|created|drafted)\b.{0,25}\b(earlier|before|last time|already|previously)\b",
    r"\b(resum(e|ing)|continu(e|ing)|pick(ing)? up|where we left off)\b",
]
_CUE_RE = re.compile("|".join(_CUE_PATTERNS), re.IGNORECASE | re.DOTALL)

# Artifact detection — VERIFIED against the real payload (S192, regression case 5).
# The original ARTIFACT_KEYS payload-field guess (attachments/files/pasted_contents/
# attached_files) was DEAD CODE: the shipped binary constructs the UserPromptSubmit
# input as {...base, hook_event_name, prompt, session_title} — no attachment field
# exists (claude.exe: `f={...X9(q),hook_event_name:"UserPromptSubmit",prompt:H,
# session_title:...}`). What the prompt TEXT does carry are the placeholders the TUI
# inserts for uploads — the binary's own grammar (its paste/image builders):
#   [Pasted text #N] / [Pasted text #N +M lines] / [Image #N] /
#   [...Truncated text #N +M lines...]
# Receipt that these reach hooks: switchboard/chat.ndjson (written by a
# UserPromptSubmit hook from its payload) carries "[Image #1]" inline in real
# Jebrim prompts (sid 36b49f0c). The dragged-file arm (absolute path with a
# document extension) is plausible-but-unobserved in 411 transcripts — kept narrow,
# honestly unverified; the placeholder arms are the verified core.
# Artifact-ONLY matches fire once per session (sentinel): screenshot-heavy debug
# sessions would otherwise turn the nudge into wallpaper. Cue matches are rarer
# and keep their every-match behavior.
_ARTIFACT_PATTERNS = [
    r"\[Image #\d+\]",
    r"\[Pasted text #\d+(?: \+\d+ lines)?\]",
    r"\[\.\.\.Truncated text #\d+ \+\d+ lines\.\.\.\]",
    # dragged file: absolute Windows path ending in a document/data extension
    # (in-tree code/md paths are relative in practice — kept out on purpose)
    r"[A-Za-z]:\\[^\s\"'<>|]{2,200}\.(?:pdf|xlsx?|docx?|pptx?|csv|png|jpe?g|webp|heic|eml|msg)\b",
]
_ARTIFACT_RE = re.compile("|".join(_ARTIFACT_PATTERNS), re.IGNORECASE)


def _actor_for(sid8: str) -> str:
    """Read the per-session status sidecar to learn the active actor. '' if unknown."""
    if not sid8:
        return ""
    try:
        data = json.loads((STATUS_DIR / f"{sid8}.json").read_text(encoding="utf-8"))
        return (data.get("actor") or "").lower()
    except (OSError, ValueError):
        return ""


def _artifact_marker(prompt: str) -> str:
    """The upload placeholder found in the prompt text, or ''."""
    m = _ARTIFACT_RE.search(prompt)
    return m.group(0).strip() if m else ""


def _emit(matched: str) -> None:
    msg = (
        f'Grounding cue detected ("{matched}"). Before producing substantive output: '
        "search the active player's bank/notes/, research/, and quest-log/ for this subject; "
        "map any uploaded artifact to where prior work left off; confirm the referent's identity. "
        'Treat "this is new" as a hypothesis to disprove. '
        "(examine G1; recurred S066/S076/S095; D-028.)"
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

    # Scope: skip dev-brain (Braindead's construction work has different cue
    # semantics). Players / Guthix / wisp / unknown all fire.
    if _actor_for(sid8) == "braindead":
        return 0

    m = _CUE_RE.search(prompt)
    matched = m.group(0).strip() if m else None
    if matched is None:
        marker = _artifact_marker(prompt)
        if marker:
            # Artifact-only fires once per session — screenshot-heavy sessions
            # would otherwise wallpaper the nudge (cue matches stay every-match).
            sentinel = (STATUS_DIR / f"{sid8}.gcue-artifact") if sid8 else None
            if sentinel and sentinel.exists():
                return 0
            matched = f"uploaded artifact: {marker}"
            try:
                if sentinel:
                    sentinel.parent.mkdir(parents=True, exist_ok=True)
                    sentinel.write_text("1", encoding="utf-8")
            except OSError:
                pass
    if matched is None:
        return 0  # ordinary prompt — fast, silent pass-through

    _emit(matched)
    log_event("grounding-cue", "nudge", sid8=sid8, detail=matched)
    return 0


if __name__ == "__main__":
    sys.exit(main())
