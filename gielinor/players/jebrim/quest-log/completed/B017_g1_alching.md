# [[B-017_2026-06-03_seventeenth-bankstanding|B-017]] Phase 0 — gnome alching run-log (Jebrim)

**Ritual:** alching (Phase 0 of bankstanding [[B-017_2026-06-03_seventeenth-bankstanding]]). **Run by:** gnome g1 (system-namespace). **Date:** 2026-06-03.
**Player in scope:** Jebrim. **Spawned because:** >10 pending drafts (13: 9 examine + 3 bank + 1 skill); player day-old, last alched 2026-06-01 ([[B-014_2026-06-01_fourteenth-bankstanding|B-014]] partial).

**Mode: PROPOSE-ONLY.** A live-idle Jebrim terminal (`e59202cf`) lingers in his namespace — confirmed dirty: CSS draft (`MM`), S124 quest + shipping-report skill draft (`M`), untracked inventory resumes. To avoid a write collision AND keep the promotion gate with the principal, this gnome moved NOTHING to `confirmed/`/`bank/notes/`/`rejected/`/`spellbook/skills/` and did NOT touch `last-alched.md`. All dispositions below are recommendations; the principal executes approved promotions. Only additive `*-drafts/` files written, with unique names.

## Step 1 — identity drafts (9 examine; niksis8_character/keepsake proposals empty)

All 9 are genuine, observation-backed, distinct corrections from [[S143_51f034e4_fif-report-accounting-fixes|S143]]–[[S149_ebe0a532_scm-transit-times-rework|S149]]. No duplicates against `examine/confirmed/` (checked vs current.md + 38 dated entries). They form a tight "verify against ground truth / verify the instrument ran" family that extends the existing confirmed family — additive, not redundant.

1. `2026-06-02-live-evidence-beats-a-confident-chat-diagnosis.md` — a code-grounded diagnosis is a hypothesis; get the live signal (pod state/logs) before asserting root cause. Anchor [[S146_f20d7744_scm-serving-memory-review|S146]]+[[S147_dcb495a7_scm-perf-audit|S147]]. **REC: y.** Strong, two-session recurrence, reinforces instrument-dont-reguess family.
2. `2026-06-02-revalidate-borrowed-constants-for-new-use.md` — a constant borrowed across a purpose boundary (TAIL=14 display-cap → percentile-fidelity cap) is an assumption; validate vs the NEW use. Anchor [[S147_dcb495a7_scm-perf-audit|S147]]. **REC: y.** Clean, in MEMORY.md already.
3. `2026-06-02-static-audit-ranking-is-a-hypothesis-until-measured.md` — rank perf fixes by measured cost not inferred mechanism; a pre-agg only retires a scan if its population matches the filter. Anchor [[S147_dcb495a7_scm-perf-audit|S147]]. **REC: y.** Distinct from #1/#5 (perf-audit-specific, two concrete rules).
4. `2026-06-02-surface-and-fix-gitignored-config.md` — a gitignored deploy-critical config is a defect to fix (scoped `!`), not a constraint to route around. Anchor [[S143_51f034e4_fif-report-accounting-fixes|S143]]; verbatim Niklavs correction. **REC: y.** In MEMORY.md.
5. `2026-06-02-synthetic-pass-hides-population-and-small-n-bugs.md` — a clean synthetic/mechanism pass hides population + small-n bugs; run live old-vs-new, bias generator adversarial. Anchor [[S147_dcb495a7_scm-perf-audit|S147]] sess-4. **REC: y.** In MEMORY.md. Sibling to #2; both worth keeping (different failure axis: borrowed-constant vs synthetic-data-shape).
6. `2026-06-02-use-pathspec-commit-from-the-first-commit.md` — `git commit -- <pathspec>` from the first commit; never `git add` then bare commit with live siblings; porcelain line-count ≠ file count. Anchor [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]]+[[S147_dcb495a7_scm-perf-audit|S147]]. **REC: edit-then-y.** Overlaps the existing confirmed `2026-05-22-git-add-scoping-with-parallel-sessions`. Recommend the principal either (a) promote as the sharper successor and archive the older 05-22 entry, or (b) fold this draft's two new mechanisms (shared-index sweep across brains; porcelain-collapses-untracked-dir) into the existing entry. Same family, materially sharper — don't promote as a naive duplicate.
7. `2026-06-02-verify-the-toolchain-actually-ran.md` — a zero exit is meaningless if a trailing echo masked it or the binary never resolved; capture EXIT=$? / confirm invocation. Anchor [[S146_f20d7744_scm-serving-memory-review|S146]]. **REC: y.** In MEMORY.md (check-real-exit). Distinct shell-verification instance.
8. `2026-06-03-css-height-match-needs-absolute-fill-not-flex1.md` — match-sibling-height needs the absolute-fill trick, not flex-1, when panel A has the larger content. Anchor [[S149_ebe0a532_scm-transit-times-rework|S149]]. **REC: y, but LOW-STAKES.** Self-labels "frontend/CSS technique, player-scope, not a working-style lesson." It's a domain technique, not a behavioral correction — borderline for `examine/`; arguably a `bank/drafts/notes/` frontend note instead. NOTE: this file is `MM` (staged+unstaged) under the live sibling — defer any move until `e59202cf` closes.
9. `2026-06-03-rescan-for-companion-files-in-a-multi-file-drop.md` — re-list a multi-file drop right before concluding; prefer the covering email for mechanic-confirmations; treat "did you see X?" as a missed-file signal. Anchor [[S148_104c786b_eu-tender-dhl-paket-round2|S148]]. **REC: y.** In MEMORY.md (rescan-companion-files). Strong, verbatim-correction-backed.

Flag: #2 and #5 are siblings (both "a validation that encodes my assumptions only confirms them") but address different axes — keep both. #6 is the only near-duplicate of an existing confirmed entry; handle per the edit/merge rec above.

## Step 2 — bank drafts (3) + staleness scan

1. `bank/drafts/notes/projects/2026-06-02-fif-vat-subtotal-grain.md` — VAT computed on net subtotal (round once at aggregate grain), not per-line; ~€16/mo drift. Anchor [[S143_51f034e4_fif-report-accounting-fixes|S143]]. **REC: promote.** Concrete, source-anchored, companion to confirmed `2026-05-28-ups-orwo-fif-data-quirks`. Settled domain knowledge.
2. `bank/drafts/notes/projects/scm_serving_node_oom_mode.md` — SCM's THIRD OOM mode: the serving-node uncapped DuckDB (cgroup OOM → 502). Anchor [[S146_f20d7744_scm-serving-memory-review|S146]]. **REC: promote.** Extends (does NOT contradict) the existing `scm_nextjs_duckdb_oom_modes` (pipeline modes 1&2) — complementary third mode. Fix shipped. NOTE: filename has no date prefix (unlike convention `YYYY-MM-DD-<slug>`); recommend rename to `2026-06-02-scm-serving-node-oom-mode.md` on promote.
3. `bank/drafts/notes/shipping/merchone-us-holiday-volume-peaks.md` — MerchOne US 2025 gift-holiday volume peaks (Christmas >> Mother's > Valentine's > Father's). Anchor [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]]. **REC: promote.** Well-scoped, basis-stated, source CSV anchored. Single-year/moderate-confidence caveat is in the note itself.

Staleness scan of `bank/notes/` (26 files): no new staleness this pass. Watch (carry-forward, not action): `eu_tender_2026.md` + `eu_tender_2026_S034_update.md` are pre-Round-2 and the engines have since moved (DHL Paket→2.0.0 [[S148_104c786b_eu-tender-dhl-paket-round2|S148]], FedEx→2.0.0 in live e59202cf); the *defensive* numbers in those notes may now be superseded — but the canonical tender knowledge lives in the bi-analytics docs by design, so these are lean refs. Re-verify-before-quoting (per `bank-notes-need-as-of-date`), not archive. Flag for next bankstanding if the brain-side refs drift further.

## Step 3 — quest-log compression (completed/ only)

Walked `quest-log/completed/` ([[S001_2026-05-20_repo-orientation|S001]]–[[S149_ebe0a532_scm-transit-times-rework|S149]] + dwarf/penguin/shipping-agent siblings). **0 new graduation drafts proposed.** Rationale: the recent finished quests ([[S143_51f034e4_fif-report-accounting-fixes|S143]]/[[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]]/S145/[[S146_f20d7744_scm-serving-memory-review|S146]]/[[S147_dcb495a7_scm-perf-audit|S147]]/[[S149_ebe0a532_scm-transit-times-rework|S149]]) already either (a) graduated their domain knowledge into the 3 bank drafts above, or (b) by design keep tender/engine domain knowledge in the bi-analytics repo docs with lean brain refs (per Jebrim's `bank-growth` convention). No crystallized cross-quest lesson is sitting un-captured. Bias-to-few honored.

## Step 3a — self-observation sweep (in-progress turns since 2026-06-01)

Read recent turns in `quest-log/in-progress/` ([[S148_104c786b_eu-tender-dhl-paket-round2|S148]] both sessions incl. the live e59202cf FedEx-rebuild continuation, S145 transit-SLA, S124) and the [[S149_ebe0a532_scm-transit-times-rework|S149]] completed entry. **0 new self-obs drafts proposed.** Every correction/pattern visible in those turns is already captured by the 9 step-1 drafts: companion-file rescan ([[S148_104c786b_eu-tender-dhl-paket-round2|S148]]→draft 9), CSS-height ([[S149_ebe0a532_scm-transit-times-rework|S149]]→draft 8), synthetic-pass + borrowed-constant + perf-ranking + live-evidence ([[S147_dcb495a7_scm-perf-audit|S147]]→drafts 1/2/3/5), toolchain-ran ([[S146_f20d7744_scm-serving-memory-review|S146]]→draft 7), pathspec/gitignored-config ([[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]]/[[S143_51f034e4_fif-report-accounting-fixes|S143]]→drafts 6/4). No uncaptured correction in the swept turns. Cap respected (0 ≤ 3).

## Step 4 — budgets

- `examine/confirmed/current.md`: ~722 words ≈ ~960 tokens vs ~3k budget. **OK.**
- `niksis8_character/confirmed/current.md`: ~37 words. **OK** (far under).
- `keepsake/current.md`: ~685 words ≈ ~910 tokens vs ~2k budget. **OK.**

No rotations proposed. (After step-1 promotions land, current.md gains ~9 bullet lines — still well within ~3k. No action.)

## Step 5 — rejected patterns

- `examine/rejected/` (3): all probe-design / reviewing-from-inside entries from S022–S025 (`reviewing-from-outside-a-system-i-am-inside`, `primed-probe-contaminates-spontaneity-test`, `probe-design-dont-suppress-tested-behavior`). Pattern: probe/meta-cognition self-obs got over-drafted during the early eval-design sessions; the keeper (`2026-05-25-probe-design-must-not-contaminate-tested-behavior`) was confirmed and the near-duplicates rejected. Not a live miscalibration — these are >1wk old and the family is settled. Report-only.
- `niksis8_character/rejected/` (2): `escalates-symptom-to-system`, `prefers-evidence-over-premature-infrastructure` (both [[S021_2026-05-21_alching-and-rule-fix|S021]]). Pattern: early niksis8_character drafts that were really *system/agent* observations, not Niklavs-through-Jebrim's-lens observations — rejected for wrong-layer. Settled. Report-only.

No new rejection-pattern draft warranted; both clusters are old and resolved.

## Step 6 — skill graduation

- `spellbook/drafts/skills/running-the-automated-shipping-report.md`: **HELD — confirmed stays held.** S124 (`61d62e21`) is still in-progress (the live-idle sibling is editing this very draft, `M`). Per [[B-014_2026-06-01_fourteenth-bankstanding|B-014]]'s hold rationale (mid-quest evolving build contract; promote at S124 close). NOT promoted.
- Confirmed-layer scan for ≥2x named-pattern skill candidates: **0 new drafts.** The [[B-013_2026-06-01_thirteenth-bankstanding|B-013]]/[[B-014_2026-06-01_fourteenth-bankstanding|B-014]] skill-watch ("trust-gate every rate engine against its own actuals; report PAPER vs DEFENSIBLE") is now anchored by two confirmed examine entries (`2026-05-31-rerating-trust-gate-grain-and-cost-basis`, `2026-05-31-rerating-mirage-guard-capability-and-noise`) plus the bank note `2026-05-31-shipping-savings-rerating-trust-gate.md` — it has the substance to become a skill, but it has NOT recurred in a NEW quest since [[B-014_2026-06-01_fourteenth-bankstanding|B-014]] ([[S143_51f034e4_fif-report-accounting-fixes|S143]]–[[S149_ebe0a532_scm-transit-times-rework|S149]] were FIF/transit/perf/CSS, not re-rating). **Skill-watch stays flagged** (carry-forward); one more re-rating recurrence earns the skill draft. Cap respected.

## Carry-forward for principal / next bankstanding
- Draft #6 (pathspec) needs an edit-or-merge decision against the existing `2026-05-22-git-add-scoping-with-parallel-sessions` confirmed entry — not a naive promote.
- Draft #8 (CSS-height) is borderline examine-vs-bank; principal call on layer.
- Bank draft #2 (scm serving OOM) wants a date-prefix rename on promote.
- `last-alched.md` NOT updated — principal closes it after approving this pass.
- The live-idle `e59202cf` sibling has dirty Jebrim files (CSS draft, S124 quest, shipping-report skill draft, inventory resumes); let it close before any move touching those paths.
- Skill-watch (re-rating trust-gate) and the eu_tender bank-ref-drift watch both carried forward.
