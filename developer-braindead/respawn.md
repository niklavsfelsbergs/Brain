# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S012]], pre-commit).

## Where we are

[[S012]] gave the dev brain its own character — **Braindead** — with a sprite (quirky tinkerer: head wrap, goggles, hammer, blueprint, slate-blue robe), a new building (**The Workshop**, top-left of the map at `(140, 140)`), and a session-mode marker (`brain/.claude/active-mode.txt`) that the hook reads to spawn / despawn him on dev-brain mode transitions. Path-map reordered so `/developer-braindead/` routes to the workshop (with `/developer-braindead/experiments/` still going to spellbook-tower); actorRule `/developer-braindead/` → braindead; hook overrides default actor to braindead when mode is `dev-brain`. Hook-side firing confirmed by inspecting `state.ndjson` — `spawn-braindead` event landed and `state-actors.json` shows `_mode: dev-brain`. Decision in [[D-013]].

Browser-side rendering not yet eyeballed in a tab. Same status as [[S011]]'s intent narration — the wiring is there, but no live browser check this session.

[[S011]] background: intent narration via per-actor sidecars + `spawn-dwarf.intent` field. Renderer hangs speech bubbles over actors that clear on building change. Decision in [[D-010]].

[[S010]] background: live-mode v0 via [[D-009]]'s five knobs. Replay + live both work.

## Next concrete step — START HERE

**Test S011 + S012 end-to-end in a browser.** `python -m http.server 8765` from `developer-braindead/experiments/visualizer/`, open `http://localhost:8765/?live=1`. Confirm: (a) Braindead spawned at the workshop (top-left) via bootstrap-from-tail replaying the existing spawn-braindead event, (b) the speech bubble "Building Braindead's workshop" is visible over him. If both render, the visualizer feature set is complete for now. If anything looks off, adjust — workshop position can move, sprite proportions can shift, bubble styling can tighten.

Then continue iterating on the visualizer. Live-mode + intent + Braindead is feature-complete per D-009 + D-010 + D-013; subsequent work is polish + deferred follow-ups. Menu of directions, no priority assigned:

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
2. `quest-log/S012_braindead_character_and_workshop.md` — most recent session
3. `quest-log/S011_visualizer_intent_narration.md` — intent narration
4. `quest-log/S010_visualizer_live_mode_v0.md` — live-mode substrate
5. `bank/decisions/D-013_braindead_character_and_workshop.md` — the Braindead decision
6. `bank/decisions/D-010_visualizer_intent_narration.md` — the intent decision
7. `bank/decisions/D-009_visualizer_live_mode_v0.md` — the live-mode decision
8. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — the iso-vs-3D decision (still load-bearing)
9. `experiments/visualizer/index.html` — the artifact being iterated
10. `experiments/visualizer/_README.md` — how to run both modes
11. `experiments/visualizer/path-map.json` — shared lookup (hook + renderer)
12. `.claude/hooks/emit-event.py` (under `developer-braindead/`) — the live-mode + intent + mode-marker hook
13. `bank/open-questions/Q-007_gielinor_visualizer.md` — points at D-009; covers the deferred follow-ups
14. `bank/plan.md` — current mission state. Visualizer is parallel to plan items.

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. [[S010]] held this — live mode swapped the event *source* (baked array → NDJSON poll), but `applyEvent` and all assets stayed put. State added in [[S009]] (`wispActive`, `currentBuilding`, `LABEL_Y_OFFSET`) plus [[S010]] (`LIVE`, `liveBytes`, `liveBootstrapped`, `data-mode="live"` CSS) are layered on top, not changes to the dispatch surface. If a future session needs to change engine behavior, keep the timeline data structure and `applyEvent` dispatch surface intact — extend, don't rewrite.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
