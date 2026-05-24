# S078 — switchbar status vocabulary: two-axis rebuild (D-029)

**Session:** 959a4c34 · Braindead · dev-brain via "lets develop gielinor".
**Status:** built + backend-validated; **frontend verification (cockpit relaunch) pending.**

## What was asked

Explain the switchbar statuses and when each triggers — "I think it needs some iteration." Walked the full pipeline (status-sidecar.py → manifest → backend → board.js), surfaced the seams, principal chose to **rethink the whole set**. Adopted a two-axis reframe, locked the spec, built it.

## The decision — [[D-029]]

The one `state` enum was doing two jobs: ball-holder state AND activity flavor. The precedence ladder in the sidecar (`alching only over working`, `wrapped_up holds across…`) was the symptom. Split into:

- **Base state (chip):** `busy`, `needs_you`, `your_move`, `stalled`, `idle`, `done` (+ internal `ended`, filtered off-board).
- **Flavor tags (ride on the chip):** `alching`, `crew`, `wrapped`.

Resolved knobs: `STALL_AFTER_SEC=300`; **two distinct pings** (needs_you hot, your_move soft); backend **re-reads state.ndjson per poll** for the action heartbeat.

## What changed (4 files)

1. **`developer-braindead/.claude/hooks/status-sidecar.py`** — `EVENT_STATE` → new tokens (working→busy, Stop→your_move). WAIT_TOOLS Pre→needs_you. SUBAGENT_TOOLS → state stays `busy`, crew becomes a tag. `.mode` marker: `wrapped_up`→state `done`+tag `wrapped`; `alching`→tag only (no state). New `tags` list on the record + crew-tag derived from pending fg spawns. Manifest per-row "awaiting-crew" block rewritten to set the crew **tag** on busy rows, not flip state. **Precedence ladder removed.**
2. **`cockpit/backend.py`** — `STATE_RANK` retokened (`needs_you 0 > your_move 1 > stalled 2 > busy 4 > idle 7 > done 8`). New `_last_action_ts_map()` (capped tail-read of state.ndjson). `build_session_model`: heartbeat = max(last_event_ts, latest action ts); `your_move`+quiet→idle, `busy`+heartbeat-silent→`stalled`; passes `tags`; attention = needs_you|your_move. `LEGACY_STATE` alias map so pre-change tokens render through the transition.
3. **`cockpit/web/board.js`** — `STATE_LABEL` retokened; `TAG_LABEL` added; renders `s.tags` as `.flavor` chips after the state chip.
4. **`cockpit/web/main.js`** — single `beep()` → `_tone()` + `pingHot()` (needs_you, two ascending notes) + `pingSoft()` (your_move, one soft note). Attention effect tracks per-session state transitions (Map), hot-priority. Feed-fallback synthetic rows retokened + `tags:[]`.
5. **`cockpit/web/styles.css`** — `--stalled` color added; `.state-*` selectors retokened; `.flavor` + `.flavor-{alching,crew,wrapped}` chip styles.

## Attention-draw refinement (post-build critique)

Principal asked whether the states are distinguished enough and whether attention lands where it needs to. Found the attention layer was **flat + monochrome**: `.attention` gave needs_you AND your_move the *identical* amber glow + pulse (and its `border-color` shorthand even clobbered needs_you's pink edge to amber), while STALLED had a high sort rank but **no motion at all** — an urgency/pop inversion. Chips were individually fine (filled-warm = actionable, outline = passive, dimmed = done).

Fix (principal chose "2 pulse, 1 static"): moved the glow/pulse **per-state**, tiered by urgency.
- **needs_you** — pink edge + pink glow + pulsing pink dot (top of act-now tier).
- **stalled** — red edge + red glow + pulsing red dot (promoted into act-now tier; motion, not just rank).
- **your_move** — amber edge + soft *static* glow, **no pulse** (your turn, no rush).
- Pulse keyframe parameterized via `--pulse-rgb` per state (added `--answers-rgb`/`--stalled-rgb`/`--waiting-rgb`). `.attention` class kept as the count flag only (no visual). busy/done/idle quiet.

## Validation

- `py_compile` clean (sidecar + backend); `node --check` clean (board.js, main.js).
- **Backend smoke-test against live data:** this session → `busy`; a stale legacy-token session → aliased to busy → **decayed to `stalled`** (heartbeat-silent), proving the crash-detection path end-to-end.

## Open / next

- **Frontend eyeball pending** — relaunch the cockpit (running window holds stale JS): confirm chips/colors, flavor-tag chips, STALLED red, and the two pings actually sound distinct. This is the verification debt to clear next.
- Not committed yet (principal asks before commit).
- Deferred: `bankstanding` as a flavor tag (needs a `.mode` marker the rituals don't write yet); attention glow is amber for both needs_you/your_move (cosmetic).
