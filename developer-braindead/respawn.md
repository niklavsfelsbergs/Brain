# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S017]], pre-commit).

## Where we are

[[S017]] shipped [[D-014]] end-to-end across hook, renderer, protocol, and gitignore — chat panel built by evolving the existing COMMS logbox (rather than adding a parallel surface as the design doc literally said), action events on Edit/Write/MultiEdit/NotebookEdit/Bash/Glob/Grep, narration channel via `.claude/narration.txt`, two-line bubble at cap-100, intent + action both pushed into chat with per-actor color cascade. Main-brain `gielinor/meta/communication-protocol.md` updated with the new cap, narration channel, intent-vs-action discipline rule, and the `wisp.txt` → `braindead.txt` drift fix. Chatbox restyled to classic OSRS look — light tan panel with black body text, dark wood header, darker per-actor username tints, Trebuchet MS bold at 14px for smooth-but-period-correct feel, box height doubled to 340px.

S015 dwarf attribution is **still untested in the wild** — same status as the start of this session. D-014 was implemented assuming it works; if the assumption is wrong, the dwarf chat path needs a fix on top.

## Next concrete step — START HERE

**Step 1 — layer-utilization audit.** Niklavs queued this as the explicit handover topic. The brain has many layers per player + global (`bank/`, `quest-log/`, `inventory/`, `examine/`, `niksis8_character/`, `keepsake/`, `spellbook/`, plus per-player `bank/drafts/`, `bank/notes/`, etc.), and **some are not getting used proportional to the work flowing through them**. Concrete example he flagged: Jebrim has done a lot of work but his `inventory/` is empty. For each apparently-underused layer, the question is binary: *do we not need it*, or *are we just not utilizing it*?

Suggested approach (deferred to the session for refinement):

1. **Inventory the layers** — both per-player and global, across `gielinor/` and `developer-braindead/`. List the layers, current contents, last-touched date.
2. **Crosswalk against actual session work** — for each player, did their last N sessions produce material that *should* have landed in each layer but didn't? Where did it land instead (chat-only? quest-log? bank/drafts?)?
3. **Per-layer disposition** — one of:
   - **Used as designed** — leave alone.
   - **Under-used because we forgot it exists** — fix discipline (likely surface in respawn ritual, or in alching).
   - **Under-used because it's the wrong shape** — redesign the layer or its trigger.
   - **Not needed** — archive (per archive-discipline.md, not delete).
4. **Surface findings to Niklavs** — recommend changes; let him decide. The audit itself is read-only across players (bankstanding-style reach), but any *changes* to per-player layers would have to happen in each player's alching session, not in this audit pass.

The audit crosses both brains (gielinor's per-player layers + dev-brain's `bank/`, `examine/`, etc.). Probably warrants its own session; might generate multiple `I-NNN`-style observations and possibly a `D-NNN` if a layer's shape changes structurally.

**Step 2 — verify D-014 end-to-end in browser.** Outstanding from S017 close. Spawn a real Jebrim Task while live mode is open. Watch for: spawn-dwarf chat line, `* D1 spawned by jebrim — desc` muted-italic, intent bubble appearing on the dwarf sprite, intent + action chat lines from the dwarf in the right color (dwarves amber), `* D1 walks to <building>` on building changes, `* D1 returns to jebrim` on completion. This subsumes the S015 verification that's been pending since that session — D-014's chat path will surface any S015 attribution bug visibly.

**Step 3 — narration channel real-world shakedown.** Once the audit is in-flight, try writing `.claude/narration.txt` at session boundaries / phase transitions and see if the chat line reads well. If it doesn't, iterate the cap (currently 200) or styling.

Other live threads:

- **Thread A from S013 — verify visualizer feature set end-to-end.** Still outstanding. Worth re-running once D-014 lands and Step 2 above passes.
- **Thread B — observe the harvest pump.** No code; watch what the next sessions' harvests produce, drift to aspirational drafts, bank drafts-gate friction.

Iteration menu (deferred, no priority assigned):

- **D-014 follow-ups from the decision doc.** Read narration / rollup if reads ever feel invisible. Action target prettification (common-prefix shortening). Chat scroll-lock UX (scroll-up locks auto-scroll). Actor color taxonomy tightening. Bubble two-line edge cases (single-word overruns, dwarf-bubble during slide).
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character.

## Open at the start of next session

- **Layer-utilization audit — first priority** (Niklavs' explicit handover topic).
- **D-014 browser verification** — second priority. Subsumes the long-outstanding S015 verification.
- **Narration channel shakedown** — once chat-flow is verified.
- Visualizer Round 3 iteration (S014 candidates).
- Harvest pump observation (Thread B).
- **§C Pilot definition** — data source, "concerning" definition, output channel. Unchanged.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S017]] (new): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.** [[D-014]] called for a "new `#chat-panel` div" when the COMMS panel already provided that surface. Pattern: when designing renderer-side changes, the design phase should include a "what's already there" scan.

From [[S017]] (new): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.** `infer_dwarf_parent`'s 600s recency window picked up a stale Jebrim intent from a prior gielinor session and attributed a dev-brain Bash to it. Fixed by hard-preferring Braindead when `active-mode.txt == dev-brain`, but the broader bias is worth holding: any future code that reads `state.ndjson` for "who's active" should consult the mode marker first.

From [[S017]] (new): **emulating a specific UI's look means font and palette must change together.** Half-measures (dark bg + smooth font, or pixel font + non-OSRS palette) read as uncanny. Required two restyle iterations after first ship. Cheap if caught early — render a reference screenshot mentally before shipping (companion to [[I-002]]).

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.** First read landed on the comm-protocol meta-doc; principal corrected to the on-screen surface. Cheap correction this time; worth holding the bias next time someone says "communication" while the visualizer is the active artifact.

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.** Smoke test ≠ live test.

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.** Used `rm -f` on a probe script without thinking; block-deletes hook is gielinor-scoped. Even for ephemeral infrastructure code, discipline is "no deletes".

From [[S014]] (two-incident pattern strengthening): **the renderer needs to be self-healing because the hook stream is a lossy substrate.** Pattern: **don't assume the upstream emitted what you'd render against — defend in the renderer too.** Companion to [[I-002]] — runtime version: render assuming partial data.

From [[S014]] (one incident): **tool renames upstream are silent regressions.** `Task → Agent` broke the brain-root hook with no error message.

From [[S013]] (still candidate, four incidents now): **the procedure was right; the procedure assumed a state that didn't exist.** Four-incident pattern — strong enough to draft an `I-NNN` if/when bankstanding next runs.

From [[S013]]: **uncommitted work occupies the ID space.** Confirmed pattern.

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S017_d014_chat_panel_implementation.md` — most recent session
3. `bank/decisions/D-014_visualizer_chat_panel.md` — implemented this session
4. **For the audit (Step 1):** start with `gielinor/CLAUDE.md` § Layer index and walk each player's folder; cross-reference `developer-braindead/_about.md` for the dev-brain layer table.
5. `quest-log/S016_visualizer_chat_panel_design.md`
6. `quest-log/S015_dwarf_attribution_via_agent_id.md`
7. `bank/decisions/D-010_visualizer_intent_narration.md` — the contract D-014 extends
8. `bank/decisions/D-009_visualizer_live_mode_v0.md`
9. `bank/decisions/D-008_iso_replay_v0_over_three_js.md`
10. `experiments/visualizer/index.html` — the artifact
11. `experiments/visualizer/_README.md`
12. `.claude/hooks/emit-event.py` (under `developer-braindead/`) — now emits intent + action + narrate alongside move + spawn-dwarf
13. `.claude/hooks/emit-commit-event.py` — post-commit emitter for COMMITS lane
14. `bank/plan.md` — current mission state

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009–S017 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

D-014 added `narrate` and `action` events alongside existing `intent`/`move`/`spawn-dwarf`/`despawn-dwarf`. No new DOM node — the existing COMMS panel ingests the new event stream in parallel with the map. All additive — same engine.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
