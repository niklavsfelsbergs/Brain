# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S013]], pre-commit).

## Where we are

[[S013]] installed the **observation harvest pump** at close-session and flipped `bank/` to drafts-gated. The first Jebrim alching pass (gielinor S012, earlier this session) surfaced empty rooms across every layer except quest-log — diagnosis: Pump 2 (per-close harvest) didn't exist, so identity layers and bank had nothing to graduate. Decision in [[D-012]]. Applied to gielinor this session: six edit groups (write-rules, close-session, alching, modes, per-player bank/_about, per-player scaffolds, lorebook draft). First harvest exercise = this session's own close; produced 1 draft (`gielinor/players/jebrim/niksis8_character/drafts/2026-05-21-escalates-symptom-to-system.md`).

Side cleanup: `developer-braindead/CLAUDE.md` had a stale "does not modify gielinor" line; the principal's parallel S012 commit (`ff0ce2c`) already shipped my correction alongside the Braindead work. Asymmetry is now explicit — dev brain → gielinor: full read+write; gielinor → dev brain: read-only on explicit cue.

**ID note.** Mid-session, today's harvest-pump decision and the Braindead decision both collided on D-011 (uncommitted). Final assignments: D-011 retired (never assigned to a landed file), [[D-012]] = harvest pump (this session), [[D-013]] = Braindead character + workshop (S012). The retired ID is not reused.

[[S012]] background: Braindead the construction crew + the Workshop building. Sprite + isoBuilding + active-mode marker. Decision in [[D-013]]. Browser-side rendering not yet eyeballed.

[[S011]] background: intent narration via per-actor sidecars. Decision in [[D-010]]. Browser-side rendering not yet eyeballed in a tab.

[[S010]] background: live-mode v0 via [[D-009]]'s five knobs. Replay + live both work.

## Next concrete step — START HERE

Two parallel threads available — pick by mood:

**Thread A: Verify the visualizer feature set end-to-end.** `python -m http.server 8765` from `developer-braindead/experiments/visualizer/`, open `http://localhost:8765/?live=1`. Confirm: (a) Braindead spawned at the workshop (top-left), (b) speech bubble visible when an agent writes intent, (c) live-mode events render as expected. Same outstanding test from S011+S012. If anything looks off, adjust — workshop position, sprite proportions, bubble styling are all in scope.

**Thread B: Observe the harvest pump in the wild.** The pump fired for the first time this session. Next few sessions are the real calibration window — watch what the harvest produces, what gets promoted at next alch, what gets rejected. Specifically:

- Does the cap of 1–5 hold up? Bias-to-less feels right but only the next 3–5 sessions will tell.
- Are observations actually observation-backed, or am I drifting to aspirational drafts? Patterns in `examine/rejected/` will tell.
- Does the bank drafts-gate add useful friction or annoying friction? Watch the chat-first pattern under the new rule (`bank/drafts/notes/` → alching promotes).
- Does skill graduation surface any candidates? Probably not for several sessions — Jebrim's `examine/confirmed/` is empty and Zezima hasn't had activity.

No code changes needed for Thread B — it's a live experiment. Carry observations into `quest-log/` and let bankstanding evaluate later.

Iteration menu (same as prior respawn, no priority assigned):

- **Idle indicator.** D-009 deferred.
- **Watchdog for non-Claude writes.** D-009 deferred.
- **Smarter active-player inference.** D-009 deferred.
- **SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character for The Inn, Bank, Hall of Mirrors, Keepsake Vault, Inbox Square.
- **Read-event noise tuning.**

## Open at the start of next session

- Visualizer browser-side verification (Thread A).
- Harvest pump observation (Thread B).
- **§C Pilot definition** — data source, "concerning" definition, output channel. Unchanged.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S013]] (new candidate, one incident): **the procedure was right; the procedure assumed a state that didn't exist.** First Jebrim alching ran the alching ritual cleanly and produced near-empty output — because Pump 2 (per-close harvest) hadn't been installed yet. Procedure didn't fail; its substrate did. Pattern-of-incident similar to [[S010]]'s live-vs-replay miss ([[I-002]] cluster). Worth promoting to an I-NNN if a third incident confirms — currently 2 (S010 + S013).

From [[S013]] (separate observation): **uncommitted work occupies the ID space.** D-011 was free in `git log` but occupied on disk by an uncommitted Braindead draft. Today's harvest-pump decision blindly claimed D-011 → had to renumber twice (D-011 → D-012 → finally landed at D-012 once the Braindead branch claimed D-013). Lesson: before claiming a stable ID, check both `git log` *and* the working tree.

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss** — I declared step 3 done without mentally rendering what `?live=1` would actually look like next to the default URL.

From [[S009]] (extension of [[I-002]], still candidate): **mental UI preview must include z-order and all collision targets**, not just the static layout. Two incidents support it now.

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]] (carried, reaffirmed): **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.** Both still candidate `examine/` entries on the main-brain side.

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S013_close_session_harvest_pump.md` — most recent session
3. `bank/decisions/D-012_close_session_harvest_pump.md` — the harvest pump decision
4. `bank/drafts/D-012_main_brain_implementation_spec.md` — the diff packet that was applied this session
5. `quest-log/S012_braindead_character_and_workshop.md` — Braindead session
6. `quest-log/S011_visualizer_intent_narration.md` — intent narration
7. `quest-log/S010_visualizer_live_mode_v0.md` — live-mode substrate
8. `bank/decisions/D-013_braindead_character_and_workshop.md` — Braindead decision
9. `bank/decisions/D-010_visualizer_intent_narration.md` — intent decision
10. `bank/decisions/D-009_visualizer_live_mode_v0.md` — live-mode decision
11. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — iso-vs-3D (still load-bearing)
12. `experiments/visualizer/index.html` — the artifact being iterated
13. `experiments/visualizer/_README.md` — how to run both modes
14. `experiments/visualizer/path-map.json` — shared lookup (hook + renderer)
15. `.claude/hooks/emit-event.py` (under `developer-braindead/`) — the live-mode + intent + mode-marker hook
16. `bank/open-questions/Q-007_gielinor_visualizer.md` — points at D-009; deferred follow-ups
17. `bank/plan.md` — current mission state

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009/S010/S011/S012 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
