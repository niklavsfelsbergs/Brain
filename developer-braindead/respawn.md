# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S011]], pre-commit).

## Where we are

[[S011]] added **intent narration** on top of [[S010]]'s live-mode v0 — agents self-narrate a 2–6 word phrase into `brain/.claude/intent/<actor>.txt` after stating Plan; the hook emits an `intent` event; the renderer hangs a speech bubble over the actor that clears when they walk to a new building. Dwarves narrate via the `Task` description at spawn time. Soft enforcement — protocol guidance in `gielinor/meta/communication-protocol.md`, not a validating hook. Decision in [[D-010]].

Not yet exercised end-to-end. Hook + renderer wiring landed but no live test this session. First test: open `?live=1`, write to `brain/.claude/intent/wisp.txt`, watch bubble appear.

[[S010]] background: live-mode v0 shipped via [[D-009]]'s five knobs (polling, replay-kept-as-default, coalesced reads, wisp default actor, manual launch). All six implementation steps landed across commits `8df30c5` + `59b920d` plus the mid-session visual mode switch. The visualizer can replay git log (default URL) and self-observe in real time (`?live=1`).

## Next concrete step — START HERE

**Test intent narration end-to-end.** Open `developer-braindead/experiments/visualizer/index.html?live=1` in a browser (after `python -m http.server 8765` from the visualizer folder); have an agent write to `brain/.claude/intent/wisp.txt` and confirm the bubble appears within ~500ms. If it works, commit S011's changes. If it doesn't, the hook branch in `emit-event.py:handle_intent_write` is the most likely culprit.

Then continue iterating on the visualizer. The live-mode + intent v0 is feature-complete per D-009 + D-010; subsequent work is polish + deferred follow-ups. Menu of directions, no priority assigned:

- **Idle indicator.** D-009 deferred. When no events arrive for N seconds, fade the actors slightly or add a breathing aura. Cosmetic but signals "the agent is quiet right now" vs "the page is broken."
- **Watchdog for non-Claude writes.** D-009 deferred. Manual edits + git-commit landings don't fire Claude Code hooks. A `watchdog` filesystem listener feeding the same NDJSON would close that gap. Only worth doing if those events turn out to matter visually.
- **Smarter active-player inference.** D-009 deferred. The hook can't see the message-level `Hey Jebrim, …` address cue, so it defaults to wisp for any path that isn't under `players/{name}/`. If the address-routing logic ever writes a session-start sidecar (e.g., `gielinor/.claude/active-player.txt`), the hook could read it and stop misclassifying global writes as wisp work.
- **SSE upgrade.** D-009 deferred. Polling works fine; SSE is smoother. Only worth doing if 500ms-poll feels janky in real use.
- **Aesthetic backlog from [[S009]].** Per-building character for The Inn, Bank, Hall of Mirrors, Keepsake Vault, Inbox Square (only got the height bump in S009; the four landmarks got distinct silhouettes). Camera/focal behavior — subtle pan or scale-on-active-player. More principal review on color balance, label legibility, sky-grass seam, scattered-detail density.
- **Read-event noise tuning.** Coalescing currently only suppresses redundant *moves*. If the read-log spam is too much in real sessions, demote further (collapse consecutive same-actor reads into a single "browsing" line, or skip log entirely for `_about.md` lookups).

The pragmatic default is: **drive a real session, watch what's off, iterate on what surfaces.** S010 fixed the live-vs-replay visual ambiguity by actually opening the page; the next iteration is best driven the same way.

## Open at the start of next session

- Visualizer iteration (above).
- **§C Pilot definition** — data source, "concerning" definition, output channel. Unchanged from prior respawn; visualizer is parallel work.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss** — I declared step 3 done without mentally rendering what `?live=1` would actually look like next to the default URL. Real-mode preview catches static-layout collisions; *cross-mode* preview catches "two URLs visually identical" failures. Extension of S009's note about z-order and collision targets. Worth promoting to an I-NNN if a third incident confirms.

From [[S009]] (extension of [[I-002]], still candidate): **mental UI preview must include z-order and all collision targets**, not just the static layout. Two incidents support it now (S009's label/tree fixes + S010's live-vs-replay).

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]] (carried, reaffirmed): **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.** Both still candidate `examine/` entries on the main-brain side.

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S011_visualizer_intent_narration.md` — most recent session
3. `quest-log/S010_visualizer_live_mode_v0.md` — live-mode substrate
4. `bank/decisions/D-010_visualizer_intent_narration.md` — the intent decision
5. `bank/decisions/D-009_visualizer_live_mode_v0.md` — the live-mode decision
6. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — the iso-vs-3D decision (still load-bearing for the engine principle)
7. `experiments/visualizer/index.html` — the artifact being iterated
8. `experiments/visualizer/_README.md` — how to run both modes
9. `experiments/visualizer/path-map.json` — shared lookup (hook + renderer)
10. `.claude/hooks/emit-event.py` (under `developer-braindead/`) — the live-mode + intent hook
11. `bank/open-questions/Q-007_gielinor_visualizer.md` — points at D-009; covers the deferred follow-ups
12. `bank/plan.md` — current mission state. Visualizer is parallel to plan items.

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. [[S010]] held this — live mode swapped the event *source* (baked array → NDJSON poll), but `applyEvent` and all assets stayed put. State added in [[S009]] (`wispActive`, `currentBuilding`, `LABEL_Y_OFFSET`) plus [[S010]] (`LIVE`, `liveBytes`, `liveBootstrapped`, `data-mode="live"` CSS) are layered on top, not changes to the dispatch surface. If a future session needs to change engine behavior, keep the timeline data structure and `applyEvent` dispatch surface intact — extend, don't rewrite.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
