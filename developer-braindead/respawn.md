# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S021]] — visualizer audit).

## Where we are

[[S021]] delivered the deliberate sweep called for at the end of [[S020]]: a full read-through of `developer-braindead/experiments/visualizer/index.html` (~2933 lines), `developer-braindead/.claude/hooks/emit-event.py` (630 lines), and the state files, producing **[[visualizer-audit-S021]]** at `developer-braindead/bank/research/visualizer-audit-S021.md`. No fixes landed in the audit pass — discipline held: just findings, file:line cited.

The visualizer's accreted state across S008–S020 is now catalogued. **15 bugs, 7 consistency issues, 18 improvements, 4 doc gaps.** The audit is the input to next session's work — pick fixes, build them.

The S020 cascade (gnomes ratification + visualizer integration) remains on disk but still **untested in the wild**. First live gnome spawn is the validation event; it's also the natural pre-work for several audit-flagged dynamics (FIFO race in B1, dev-brain parent inference in B3, attribution fallthrough in B6) that a static read can't fully exercise.

## Next concrete step — START HERE

**Step 1 — pick fixes from the audit, build them.** Read [[visualizer-audit-S021]] first; the triage section near the bottom suggests:

- **Most likely to bite:** B1 (FIFO `pendingAgentBind` misattribution) — first parallel-dwarf-spawn surfaces it.
- **Most easily fixed:** B2 (parse-failure vs window-past sharing one `break` — 2-line change), B13 (`deriveSpeaker` regex `D[1-3]`/`G[1-3]` → `D\d+`/`G\d+` — already relevant: state-dwarves.json at nextId 8), C2 (Braindead missing from COMMS tab/filter/dot/legend — mechanical CSS/HTML).
- **Most architectural:** B7+B8+I4+I5 (despawn-on-crash leak + non-atomic state writes; temp-file-rename pattern + startup GC).
- **Highest-leverage doc:** D1 — `_README.md` rewrite covering D-014, S012, D-016, narration, active-mode marker, sub-agent attribution.

Principal's call which to land first. Suggested approach: bundle B2 + B13 + C2 + D1 in one tight pass (small, low-risk, finishes-the-thought items), then take B1/B7/B8 as a more deliberate second cut. The architectural items deserve their own session — they involve state-file invariants that are worth thinking through, not racing through.

**Step 2 — first live gnome spawn (still deferred from S020).** Combined-test candidate: a Jebrim alching gnome. Single spawn exercises the boundary hook (env→payload fix from S020), the visualizer pipeline (sprite, GNOMES tab, walk, despawn), and surfaces audit-flagged dynamics — B1's preconditions, B3's recency window, B6's silent fallthrough. Order with Step 1 is principal's call:

- **Fixes-then-spawn:** fix the static reads first, then validate live (cleaner; the live test has less noise).
- **Spawn-then-fixes:** let the live run dictate which fixes matter most (more empirical; risks the spawn surfacing issues you have to fix mid-session anyway).

**Step 3 — drafts triage (carried from S018 → S019 → S020).** Several drafts still await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md` to canonicalize the S018 audit's structural decisions.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` (still untouched).
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` — awaits Jebrim skills-promotion at first Jebrim alching (covered by Step 2 if the gnome runs).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + `2026-05-21-prefers-evidence-over-premature-infrastructure.md`) — also covered by Step 2 if the gnome runs.

Note: git status at S021 close shows substantial *un-committed* Jebrim work (drafts moved/created, completed/in-progress quest-log files, `keepsake/current.md` modified, `S014_*.md` completed file edited). Those are from gielinor sessions that ran between S020 and S021; the principal will reconcile them at next gielinor open per the in-progress reconciliation prompt convention.

**Step 4 — D-014 browser verification (carried from S017).** Subsumed by Step 2's combined test if the principal opens the visualizer in live mode while the gnome runs. Also exercised by Step 1's UI items (C2 Braindead COMMS surfaces).

**Step 5 — narration channel shakedown.** Used briefly at S019/S020/S021 opens. Audit I18 recommends a deliberate stress test — multiple narration events at session boundaries, phase transitions, mode switches. Couples naturally with Step 1's COMMS work.

Other live threads (carried, lower priority):

- **Untracked Jebrim files at S019/S020/S021 close.** Inventory files, niksis8_character drafts/confirmeds/rejecteds, spellbook drafts/confirmeds, quest-log in-progress + completed, modifications to keepsake/current.md and S014 completed quest-log, keepsake/archive/proposals. Pickup at next Jebrim respawn via reconciliation prompt.
- **Soft-block tuning** (S018 close-session pre-commit) — three options offered; re-evaluate "abandon" after first fire.
- **Self-observation sweep tuning** (S018 alching step 3a) — cap 0–3; watch first alching pass output (Step 2).
- **Cross-player parity for future players.** Jebrim + Zezima aligned. No template system yet.
- **Possible `I-NNN` from S018** — quest-log-as-vacuum pattern. Candidate for next bankstanding.
- **Possible `lorebook/drafts/` from S020** — *architectural guarantees need a live failure test, not just code review.* Three boundary hooks shipped over multiple sessions all gated on a wrong predicate that "read right." Pattern worth canonicalizing at next bankstanding. Cite [[S020]].
- **Possible `bank/decisions/` from S021** — *cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.* The audit found 6 surfaces enumerating the same 10 buildings. Adding an 11th touches 6 places. Worth thinking about a single config that radiates. Lower priority than the fixes themselves.

Iteration menu (deferred, no priority assigned):

- **D-014 follow-ups.** Action target prettification (I12). Chat scroll-lock UX (I13). Actor color taxonomy rationalization (I1, ties to C1). Bubble two-line edge cases (I14).
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred (I9–I11).
- **Aesthetic backlog from [[S009]].** Per-building character (I15).
- **Tighten gnome hook allowlist** from `/spellbook/drafts/` to `/spellbook/drafts/skills/` for symmetry with D-016 (I17). Phantom risk today.
- **Gnome workshop building (I16).** Defer until the gnome has been used a few times.

## Open at the start of next session

- **Pick + build audit fixes** — Step 1. Triage from `bank/research/visualizer-audit-S021.md`. Suggested bundle: B2 + B13 + C2 + D1 for a tight finishing pass; B1/B7/B8 for a deliberate cut after.
- **First live gnome spawn** — Step 2. Validates the whole S020 cascade. Natural pre-work for Step 1 *or* cross-check after; principal's call.
- **Drafts triage** — Step 3. Largely subsumed if the Jebrim alching gnome runs in Step 2.
- **D-014 + S015 browser verification** — Step 4. Same combined-test candidate as Step 2.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S021]] (new): **the audit-then-validate pattern works for accreted infrastructure.** Static read first, live test second. The audit surfaced things (FIFO race in B1, regex-bound drift in B13) that no live test would have hit yet because the preconditions hadn't fired. The respawn before S021 had it right: do the deliberate sweep first, then validate. Worth canonicalizing for any future "this layer has accreted, time to look" moment.

From [[S021]] (new): **cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.** Six surfaces enumerate the same 10 buildings in the visualizer; all in sync today, but adding an 11th building means touching 6 places. Pattern worth a `bank/decisions/` note at lower priority.

From [[S020]] (still relevant): **architectural guarantees need a live failure test, not just code review.** Three sub-agent boundary hooks (gnome, dwarf, sub-spawn) all gated on env vars Claude Code doesn't propagate. The dwarf hook went undetected for the longest — never tested in the wild. Code review can't catch a wrong predicate when the predicate "reads right." Pattern worth a `gielinor/lorebook/drafts/` entry at next bankstanding. S021 reinforces this — the audit is *also* a "test by reading," and several of its findings (B1, B3, B6) won't *actually* be confirmed until a live spawn fires.

From [[S020]] (still relevant): **the claude-code-guide agent earned its spawn.** Direct domain question, concrete-needed-answer, one-shot. Confirms [[D-014]]'s dwarf-spawn heuristic: scoped, domain-specific lookups are where sub-agent invocation pays off.

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.** Gnome write-boundary uses both — allow-list for housekeeping surface, explicit blocklist for principal-only paths.

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.** Spawn heuristic thresholds in `spawning-gnomes.md`; rituals reference but don't copy.

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.** Layer-routing.md + drafts-gates + inventory promotion fixed this. Candidate for an `I-NNN` next bankstanding.

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.** S019 + S020 follow this; S021 deliberately *splits* — audit lands, fixes wait. The pattern flips when "what to fix" is the open question rather than "how to land it."

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.** Reinforced by S021 B3 — `infer_dwarf_parent` doesn't have the dev-brain override that `current_main_actor` does, so it can walk into the previous gielinor session's intents.

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now six-incident pattern with S018, S020): **the procedure was right; the procedure assumed a state that didn't exist.** S021 audit reinforces — several findings (B3, B4, B14) are "the code works under expected conditions; the conditions aren't always what the code assumes."

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.** S021 found `ensureActorExists` and `setIntent`'s position-guard already embody this; the audit reveals where the self-healing is incomplete (B10, B11, B12).

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `bank/research/visualizer-audit-S021.md` — the audit. **Most load-bearing read for next session.**
3. `quest-log/S021_visualizer_audit.md` — the session that produced it.
4. `quest-log/S020_gnomes_ratification_and_visualizer.md` — prior session; context for why the audit was queued.
5. `developer-braindead/.claude/hooks/emit-event.py` + `experiments/visualizer/index.html` — the audit targets. Read on demand by finding rather than cold.
6. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — the patched enforcement, still untested in the wild.
7. `gielinor/spellbook/skills/spawning-gnomes.md` — operating spec.
8. `gielinor/.claude/agents/gnome.md` — agent config.
9. `gielinor/meta/modes.md` — principal/dwarf/gnome axis with S020 corrections.
10. `gielinor/spellbook/rituals/close-session.md` + `alching.md` — step 0 spawn-decisions for the Step 2 spawn.
11. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-015_jebrim_layer_audit_outcomes.md`, `D-016_gnomes_subagent.md` — prior decisions the audited code builds on.
12. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during fix iteration**. State additions across S009–S020 are layered on top of the dispatch surface, not changes to it. Keep extending; don't rewrite.

D-014 added `narrate` and `action` events alongside `intent` / `move` / `spawn-dwarf` / `despawn-dwarf`. S020 added `spawn-gnome` / `despawn-gnome` to the same dispatch surface — additive. The renderer's sub-agent surface is parameterized: `dwarfNodes` / `gnomeNodes`, `spawnDwarf` / `spawnGnome`, parallel state files, shared `isSubAgentActor` for cross-cutting checks. Audit fixes should preserve this shape — modify within, don't reshape the surface.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
