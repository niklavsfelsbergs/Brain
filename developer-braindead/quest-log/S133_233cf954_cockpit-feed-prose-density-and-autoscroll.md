# S133 — 2026-05-30 — Cockpit FEED: prose density, per-session filter, thinking blocks, autoscroll fix

**sid** 233cf954 · dev-brain via "lets develop gielinor" (mid-conversation pivot) · OPEN→UPDATE→CLOSING on `comms_append`.

## The ask

Principal: *"The feed is not actually giving much. The steps of thinking [the Understanding/Plan + narration prose, image 2] are not actually popping up as prose. Why?"* Then, after diagnosis, built all three offered fixes. Then a follow-up bug: *"the feed doesn't hold at the bottom — when new messages come in I have to scroll down."*

## Diagnosis (the "why") — not a broken pipe

Verified empirically against live `chat.ndjson` rather than guessing: the say-emit ([[status-sidecar.py]] `_emit_says_from_transcript`, [[S075_d27b2fe0_agent-prose-into-feed|S075]]) **works** — image-2's exact prose blocks were present as `kind:"say"` (jebrim `0b0f2049`, 25 say lines), and the feed *was* rendering say un-chipped. The feed read thin for three real reasons:

1. **Action lines evict prose.** The feed was a flat `_ndjson_tail(chat.ndjson, 250)`; in the live tail, 40 `action` : 15 `say`. Tool calls fire far faster than prose, so prose aged out of the 250-window before the client's `actions` toggle could even act on it — a client-only fix was structurally impossible.
2. **Cross-fleet, newest-last, no per-session filter.** A busy sibling (Guthix bankstanding `97b46aa3`) floods the window and evicts the session you're watching.
3. **Thinking blocks skipped by design + Opus 4.8 changed the mix.** `_emit_says_from_transcript` skips `type:"thinking"`; with interleaved thinking, much of the genuine reasoning now lands there, leaving only short connector sentences as visible `text`.

## What was built

- **#1 backend per-kind reservation** (`cockpit/backend.py::api_feed`). Replaced the flat tail with a 1500-line raw read bucketed by kind, keeping each bucket independently: `action`≤110, `think`≤70, **prose (say/intent/checkpoints) protected ≤220**, final cap 360. The real fix for cause #1 — prose can no longer be evicted by an action flood.
- **#2 per-session "this session" toggle** (`feed.js` + `main.js` passes `selSid8`). Default OFF (stays cross-fleet); keeps `comms` items; filters to the board-selected session when on.
- **#3 thinking surfaced** (`status-sidecar.py` emits `kind:"think"` via new `_emit_chat_think` + `THINK_TEXT_MAX=600`; `feed.js` `thinking` toggle default OFF; `styles.css` `.k-think` dim-italic). The "steps of thinking" on opt-in.
- **Autoscroll fix** (`feed.js`). Root cause: the stick-to-bottom check measured distance-from-bottom *after* appending, against a 160px threshold — and a single tall prose/`say` block exceeds 160px, so one new message disengaged autoscroll (worse now that the feed is proser). Fix: capture pin intent on the user's own `onScroll` (before new content lands; `<60px` = pinned), and snap unconditionally when pinned. `pinned` starts true so first load lands at newest.

## Verification

- node --check (`feed.js`, `main.js`) ✓ · py_compile (`status-sidecar.py`, `backend.py`) ✓.
- Functional harness (temp `CHAT_PATH`): transcript parser emits 1 say + 1 think, **skips sidechain**, offset → EOF; backend reservation keeps **all 10 prose through a 1400-action flood** (actions capped at 110). PASS.
- **RUNTIME-UNVERIFIED** — running backend holds stale Python, WebView holds stale JS; needs the queued `b91.0` cockpit relaunch to eyeball the toggles + autoscroll. Asymmetry: `status-sidecar.py` is a fresh subprocess per hook fire, so **thinking-capture goes live immediately** for any session's next tool call; the cockpit-side changes wait on relaunch.

## Tradeoff (flagged, accepted)

Thinking blocks are now *always* written to `chat.ndjson` (the hook can't know the client toggle state); the client filters them and the backend buckets them at 70, and the existing sweep keeps the file bounded. Stream churns a little faster; contained.

## Co-edit note

`backend.py` was co-edited with `braindead-63750f50` ([[S131_63750f50_construction-side-severity-audit|S131]] build phase): it removed `TERM_FIT_DIAG_PATH` + the `api_termdiag` route (#7a diag-probe strip) and left the file for me to commit, explicitly OK'ing the sweep (attributed here). This commit therefore also lands that clean removal.

**Cascade.** `cockpit/backend.py` (per-kind reservation + [[S131_63750f50_construction-side-severity-audit|S131]] diag-route removal), `cockpit/web/feed.js` (toggles + autoscroll), `cockpit/web/main.js` (`selSid8` prop), `cockpit/web/styles.css` (`.k-think`), `developer-braindead/.claude/hooks/status-sidecar.py` (`think` emit), this quest-log, `respawn.md` prepend, `comms/active.md` CLOSING.

**Main-brain changes.** None — all changes are cockpit + the dev-brain status sidecar; no `gielinor/` writes.
