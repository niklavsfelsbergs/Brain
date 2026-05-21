# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S022]] — visualizer audit fixes).

## Where we are

[[S022]] landed the full audit-fix pass [[S021]] queued: **15 bugs**, **7 consistency findings**, **4 doc gaps** addressed across 4 files. Three findings deferred with documented reasons (B5 design tradeoff, B9 race with self-heal, B15 working-as-designed per [[D-014]]); three confirmed as non-findings (C5/C6/C7). Plus two real bugs the audit didn't catch but the validation pass exposed: **Bash writes to sidecar files** were bypassing the active-mode / intent / narration handlers, and **`active-mode.txt` is shared across parallel Claude sessions**, so a dev-brain marker set here bled into a parallel Jebrim session's Bash attribution. Both fixed in-session.

The S020 cascade (gnomes ratification + visualizer integration) is **finally validated in part** — the active-mode marker, intent sidecar, and narration channel were live-exercised when the Bash-dispatch fix landed and replayed the missing `spawn-braindead` event for this session. The first **live gnome spawn** is still deferred.

Future visualizer "aliveness" work captured as [[Q-008]] (idle sprite breath, per-building ambient particles, day/night cycle, NPC wanderers, trail echoes). Parked, not started.

## Next concrete step — START HERE

**Step 1 — first live gnome spawn (deferred from S020 and S021).** Still the natural validation event for the boundary hook (S020's env→payload-field fix, untested in the wild), the visualizer's gnome render path, and the audit fixes that only fire under sub-agent activity (B1 LIFO under multi-spawn, B3 dev-brain parent override, B6 stderr trail, B7 GC threshold, B8 atomic writes under crash). Combined-test candidate: a Jebrim alching gnome. One spawn exercises a wide cross-section.

**Step 2 — drafts triage** (carried from S018 → S019 → S020 → S021). Several drafts still await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md` to canonicalize the S018 audit's structural decisions.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` (still untouched).
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` — awaits Jebrim skills-promotion at first Jebrim alching (covered by Step 1 if the gnome runs).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + `2026-05-21-prefers-evidence-over-premature-infrastructure.md`) — also covered by Step 1 if the gnome runs.

Note: git status at S022 close shows substantial **un-committed Jebrim work** from a parallel gielinor session (`S023_shipping-mart-coverage-audit` in-progress, modified `keepsake/current.md`, new drafts folders). The principal reconciles those at next gielinor open per the in-progress reconciliation prompt convention.

**Step 3 — D-014 + S015 browser verification** (carried from S017). Subsumed by Step 1's combined test if the visualizer is open in live mode while the gnome runs.

**Step 4 — narration channel shakedown** (carried from S021's audit I18). Used heavily across S019–S022 opens and at S022's Bash-dispatch repair. A deliberate stress test still warrants its own session — multiple narration events at boundaries, phase transitions, mode switches.

**Step 5 — pick from [[Q-008]]** when ready to make the world feel alive. Recommendation in the entry: idle sprite breath + per-building ambient particles first, gated behind `prefers-reduced-motion`. Don't start until Step 1 lands.

Other live threads (carried, lower priority):

- **Untracked Jebrim files at S019/S020/S021/S022 close.** Inventory files, niksis8_character drafts/confirmeds/rejecteds, spellbook drafts/confirmeds, quest-log in-progress + completed, modifications to keepsake/current.md and S014 completed quest-log, keepsake/archive/proposals, new S023 in-progress entry. Pickup at next Jebrim respawn.
- **Soft-block tuning** (S018 close-session pre-commit) — three options offered; re-evaluate "abandon" after first fire.
- **Self-observation sweep tuning** (S018 alching step 3a) — cap 0–3; watch first alching pass output (Step 1).
- **Cross-player parity for future players.** Jebrim + Zezima aligned. No template system yet.
- **Possible `I-NNN` from S018** — quest-log-as-vacuum pattern. Candidate for next bankstanding.
- **Possible `lorebook/drafts/` from S020** — *architectural guarantees need a live failure test, not just code review.* S022 reinforces this twice over: the audit was itself a "test by reading," and two of its biggest fixes (Bash sidecar dispatch, cross-session attribution) only surfaced once the audit fixes were *running*. Pattern worth canonicalizing.
- **Possible `bank/decisions/` from S021** — *cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.* Lower priority than the fixes themselves.
- **Possible `bank/decisions/` from S022** — *audit-then-validate finds different bugs than either alone.* See S022's bullet 5. Worth a note at next bankstanding.

Iteration menu (deferred, no priority assigned):

- **[[Q-008]] visualizer aliveness picks.** Idle breath, ambient particles, day/night, wanderers, trail echoes.
- **Action target prettification** (audit I12). Bash commands show raw command text; could pattern-match common verbs (mv, cp, git, python -m http.server) and prettify.
- **Chat scroll-lock UX** (audit I13). `logEl.scrollTop = logEl.scrollHeight` defeats user read-history intent. Only auto-scroll when already at bottom.
- **Bubble two-line edge cases** (audit I14). `wrapBubbleText` hard-slices single long tokens at 50 chars; multi-word edge cases unverified.
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred (audit I9–I11).
- **Tighten gnome hook allowlist** from `/spellbook/drafts/` to `/spellbook/drafts/skills/` for symmetry with [[D-016]] (audit I17). Phantom risk today.
- **Gnome workshop building** (audit I16). Defer until the gnome has been used a few times.
- **Path-based dev-brain override narrowing.** S022 narrowed only the Bash side of the cross-session bleed. The path-based override in `handle_write_or_read` still fires for any in-brain path without a player rule match — a parallel non-dev-brain session editing `gielinor/meta/*` would still attribute to Braindead. Lower-volume than the Bash leak; revisit if it surfaces in practice.

## Open at the start of next session

- **First live gnome spawn** — Step 1. Validates the whole S020 cascade plus the S022 audit fixes that only fire under sub-agent activity.
- **Drafts triage** — Step 2. Largely subsumed if a Jebrim alching gnome runs in Step 1.
- **D-014 + S015 browser verification** — Step 3. Same combined-test candidate as Step 1.
- **Narration shakedown** — Step 4. Deliberate stress test, separate session.
- **[[Q-008]] pick** — Step 5. After Step 1 lands.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S022]] (new): **audit-then-validate finds different bugs than either alone.** Two of the highest-impact fixes (Bash sidecar bypass, cross-session active-mode bleed) only surfaced once the audit fixes were running and the stream behavior could be observed live. Static reads found 15 bugs; running validation surfaced 2 more that no static read could have caught. Worth canonicalizing as a pattern next bankstanding.

From [[S022]] (new): **shared global state is hostile to parallel Claude sessions.** `active-mode.txt` at the brain root was designed for one session at a time; with parallel sessions the marker leaks. The cheap fix (prefer recency over the marker for Bash attribution) shifts the load-bearing convention to "every turn writes intent regularly." Architectural fix would need a per-session signal (PID, payload `session_id`) that wasn't worth the lift now.

From [[S021]] (still relevant): **the audit-then-validate pattern works for accreted infrastructure.** Static read first, live test second. S022 reinforces — the audit's findings were correct AND incomplete; running the fixes was the second pass that closed the loop.

From [[S021]] (still relevant): **cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.** Six surfaces enumerate the same 10 buildings in the visualizer. C1 color taxonomy was the first to consolidate (CSS vars across chat/tab/legend); building list could be next. Pattern worth a `bank/decisions/` note at lower priority.

From [[S020]] (still relevant): **architectural guarantees need a live failure test, not just code review.** S022 makes this a three-incident pattern (sub-agent boundary hooks, Bash sidecar dispatch, cross-session attribution).

From [[S020]] (still relevant): **the claude-code-guide agent earned its spawn.** Direct domain question, concrete-needed-answer, one-shot. Confirms [[D-014]]'s dwarf-spawn heuristic.

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.** Gnome write-boundary uses both — allow-list for housekeeping surface, explicit blocklist for principal-only paths.

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.** Spawn heuristic thresholds in `spawning-gnomes.md`; rituals reference but don't copy.

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.** Layer-routing.md + drafts-gates + inventory promotion fixed this. Candidate for an `I-NNN` next bankstanding.

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.** S022 follows this — six bundles + two follow-up fixes shipped in one pass rather than chained over multiple sessions.

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.** Reinforced by S022's cross-session attribution work — the same root cause (single global state, multiple sessions) shows up in active-mode.txt sharing too.

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now seven-incident pattern with S018, S020, S022): **the procedure was right; the procedure assumed a state that didn't exist.** S022's Bash sidecar fix is the canonical case: the active-mode handler worked correctly when invoked from WRITE_TOOLS, the respawn ritual just never invoked it via WRITE_TOOLS.

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.** S022 added more self-healing surfaces (B7 GC, B4 stale-marker detection, B1 LIFO+warning, atomic state writes) — incomplete-but-improving.

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S022_visualizer_audit_fixes.md` — the session that just closed.
3. `bank/research/visualizer-audit-S021.md` — the audit that drove S022. Status changes per bug noted by the S022 quest-log; the file itself is left as a historical record.
4. `bank/open-questions/Q-008_visualizer_aliveness.md` — newly parked. Read before picking aliveness work.
5. `developer-braindead/.claude/hooks/emit-event.py` + `experiments/visualizer/index.html` — the patched targets. Read on demand by finding rather than cold.
6. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — boundary hooks, still untested in the wild.
7. `gielinor/spellbook/skills/spawning-gnomes.md` — gnome operating spec.
8. `gielinor/.claude/agents/gnome.md` — agent config.
9. `gielinor/meta/modes.md` — principal/dwarf/gnome axis.
10. `gielinor/spellbook/rituals/close-session.md` + `alching.md` — step 0 spawn-decisions for the Step 1 spawn.
11. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-015_jebrim_layer_audit_outcomes.md`, `D-016_gnomes_subagent.md` — prior decisions the patched code builds on.
12. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during fix iteration**. S022 followed this discipline — every fix layered on top of the dispatch surface, never reshaped it. Keep extending; don't rewrite. [[Q-008]] aliveness ideas all preserve this discipline (additive CSS/SVG, no engine touch).

D-014 added `narrate` and `action` events alongside `intent` / `move` / `spawn-dwarf` / `despawn-dwarf`. S020 added `spawn-gnome` / `despawn-gnome` to the same dispatch surface — additive. S022 added nothing new to the event vocabulary; only refined existing handlers.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
