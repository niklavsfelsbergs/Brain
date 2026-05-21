# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S018]], pre-commit).

## Where we are

[[S018]] shipped the Jebrim layer-utilization audit end-to-end. Eight findings; dominant pattern was `quest-log/in-progress/` absorbing content that belonged in five other layers. Bundle decision: [[D-015]] + gielinor lorebook draft.

Concrete structural changes:

- New `gielinor/meta/layer-routing.md` (content-shape → layer mapping), `@import`ed from `gielinor/CLAUDE.md`.
- Resume state moves from quest-log top to `inventory/<quest-slug>-resume.md`. Close-session step 3 writes it; respawn step 6.h reads it.
- Quest-vs-session split — `completed/` triggers on quest close, not session close. Multi-session quests stay in `in-progress/` across many closes.
- Skills now drafts-gated per-player (`spellbook/drafts/skills/`), parallel to bank. Replaces the old lorebook-routing for skills.
- New alching step 3a — self-observation sweep through `in-progress/` turns since last-alched.
- Alching thresholds tightened: never-alched + day-1+, >5 drafts, >20 turns, >7 days.
- Pre-commit soft-block in close-session: in-progress quest without inventory resume file surfaces gap before commit.
- Per-player `_about.md` parity applied to both Jebrim and Zezima.
- One file move: `bank/drafts/notes/workflow/moving-target-work-decomposition.md` → `spellbook/drafts/skills/moving-target-decomposition.md`.

S015 dwarf attribution is **still untested in the wild** — unchanged status. D-014 chat panel verification (S017 outstanding) also still pending.

## Next concrete step — START HERE

**Step 1 — surface drafts for principal triage.** Several drafts await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md` to canonicalize the audit's structural decisions.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` and `2026-05-21_shipping-data-mart-ttyd.md` — principal pins (or doesn't).
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` — re-routed by S018 file move; awaits skills-promotion at first Jebrim alching.
- Pre-existing `gielinor/players/jebrim/niksis8_character/drafts/` (2 from S017-era) — also await Jebrim alching.

**Step 2 — first Jebrim alching pass under new spec.** Jebrim has never been alched (1+ days old, drafts pending). New respawn step 6.i should fire the threshold recommendation. This pass will exercise: step 3 walks `completed/` (currently empty — should produce zero bank drafts), step 3a walks `in-progress/` turns since spawn (rich substrate — S014's 16 turns + S002 + S001), step 6 skill-graduation triages the migrated draft. Cap discipline matters here — the first sweep will be tempted to over-produce.

**Step 3 — D-014 browser verification (outstanding from S017).** Spawn a real Jebrim Task while live mode is open. Watch for the full chat-event taxonomy. Subsumes S015 attribution verification.

**Step 4 — narration channel shakedown.** Try writing `.claude/narration.txt` at session boundaries / phase transitions and see if the chat line reads well. If it doesn't, iterate cap (currently 200) or styling.

Other live threads:

- **Migration of S014's resume sections.** Per S018 D-015's deferred items: next close-session pass that touches S014 will lift S014's resume sections from the quest-log file into `inventory/S014-ttyd-resume.md`. One-time per quest.
- **Soft-block tuning.** S018's pre-commit soft-block offers three options (write resume / commit anyway / abandon). "Abandon" may be too aggressive for missing-file case — re-evaluate after first fire.
- **Self-observation sweep tuning.** Cap 0–3. Watch first alching pass output; tighten or loosen cap if needed.
- **Cross-player parity for future players.** Jebrim + Zezima are aligned. No template system yet for new players — principal scaffolds future players against the post-S018 spec.
- **Possible `I-NNN` from S018.** The quest-log-as-vacuum pattern is candidate for an examine entry but wasn't drafted in S018 itself. Next bankstanding can surface it.
- **Thread A from S013 — verify visualizer feature set end-to-end.** Still outstanding. Worth re-running once D-014 lands and Step 3 above passes.
- **Thread B — observe the harvest pump.** No code; watch what the next sessions' harvests produce, drift to aspirational drafts, bank drafts-gate friction.

Iteration menu (deferred, no priority assigned):

- **D-014 follow-ups from the decision doc.** Read narration / rollup if reads ever feel invisible. Action target prettification. Chat scroll-lock UX. Actor color taxonomy tightening. Bubble two-line edge cases.
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character.

## Open at the start of next session

- **Drafts triage** — first priority. The audit produced several pending decisions.
- **Jebrim alching pass** — second priority. First-ever, will validate new spec end-to-end.
- **D-014 browser verification** — third priority. Subsumes S015 verification.
- **Narration channel shakedown** — once chat-flow is verified.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S018]] (new): **the quest log is the gravitational center; other layers starve without explicit routing.** Eight-finding audit showed five layers near-empty while quest-log absorbed working memory, self-observations, harvest-pending domain knowledge, and methodology drafts. Fix has to make other layers cheap to land in (drafts-gates everywhere) AND make routing explicit (`layer-routing.md`). Candidate for an `I-NNN` next bankstanding.

From [[S018]] (new): **bundle big structural decisions; resist piecemeal landing.** Q1–Q5 were five separate questions but interlocked (routing requires routing-doc; resume-out requires inventory-in; inventory-in requires close-session writes and respawn reads). Trying to land any one without the others would have produced inconsistent state. The phased execution (A→E with ratification gates) kept the bundle coherent.

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.** Companion to S018's pattern — both surface the same bias: design-time without enough audit-time.

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.** Any future code that reads `state.ndjson` for "who's active" should consult the mode marker first.

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.** Render a reference screenshot mentally before shipping (companion to [[I-002]]).

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.** Smoke test ≠ live test.

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.** Even for ephemeral code, discipline is "no deletes".

From [[S014]] (now five-incident pattern with S018): **the procedure was right; the procedure assumed a state that didn't exist.** Strong enough to draft an `I-NNN` next bankstanding.

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.** Companion to [[I-002]] runtime version.

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.** Confirmed pattern.

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S018_jebrim_layer_utilization_audit.md` — most recent session, the audit.
3. `bank/decisions/D-015_jebrim_layer_audit_outcomes.md` — the bundle decision.
4. `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — the gielinor-side decision draft (awaits canonicalization).
5. `gielinor/meta/layer-routing.md` — the canonical routing table the audit produced.
6. **For the alching pass (Step 2):** `gielinor/spellbook/rituals/alching.md` — updated thresholds + step 3a sweep + skills-drafts path.
7. `quest-log/S017_d014_chat_panel_implementation.md` — for Step 3 verification.
8. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-010_visualizer_intent_narration.md`, `D-009_visualizer_live_mode_v0.md`, `D-008_iso_replay_v0_over_three_js.md`.
9. `experiments/visualizer/index.html` — the artifact.
10. `experiments/visualizer/_README.md`.
11. `.claude/hooks/emit-event.py` (under `developer-braindead/`).
12. `.claude/hooks/emit-commit-event.py`.
13. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009–S017 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

D-014 added `narrate` and `action` events alongside existing `intent`/`move`/`spawn-dwarf`/`despawn-dwarf`. No new DOM node — the existing COMMS panel ingests the new event stream in parallel with the map. All additive — same engine.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
