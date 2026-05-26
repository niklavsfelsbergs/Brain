# S029 — shipping-agent vocab harvest (NFE + shipping_topics)

**Opened:** 2026-05-22, Jebrim active.
**Ask:** "Dig through the NFE repo to pick up slang regarding shipping and some other interesting stuff. I'm looking for things I should teach the shipping agent."

## Status

**Closed** 2026-05-22 — vocab harvest landed, six trip-up rules applied to `shipping-agent/how_to.md`, db_schenker DQ note applied to `known-dq.md`, alching ritual run on Jebrim's full draft surface (16 items landed).

## Turn log

- **T1.** Confirmed prior harvest scope (S027 cost-vocab, [[S026_2026-05-22_shipping-costs-nextjs-architecture-read|S026]] nextjs-vocab). Identified fresh ground: carrier/lane/corridor language, source-system + production-site + pipeline slang, operations/incoterms/customs/returns/acronyms.
- **T2.** Spawned 3 Explore dwarves in parallel — D1 carrier vocab, D2 source-system / production-site / pipeline slang, D3 ops / incoterms / customs / returns / acronyms. All returned with anchored vocab lists.
- **T3.** Niklavs added `shipping_topics/` to scope. Spawned D4 — Explore dwarf walking `bi-analytics-main/NFE/shipping_topics/` (~41 topic folders, sampled 6–10 deeply) plus `workbench/shipping_topics/` for topics not in NFE. Returned with corporate-identity vocab (TCG, MD, OML, AHS, FXEHD/FXESPPS, FIF Report, Manual Bill, tassenlibling, Rossmann, account 650116, etc.) and business framings.
- **T4.** Summarized to top-10 trip-ups. Niklavs refined:
  - #1 TCG also excludes PCS; Rewallution surface only on explicit ask.
  - #2 (ORWO identity-only) disregarded — under construction.
  - #3 (bucket detail invoice-only) agent already knows.
  - #4 (% invoiced lag) recheck against agent docs — refined threshold to **30 days** (not 90).
  - #5 collapsed to: "shipping cost excludes tax + customs + duties."
  - #6 (`invoice_source` ≠ carrier) keep.
  - #7 (`db_schenker` 100% unclassified by design) keep.
  - #8 collapsed to heuristic-by-cost-magnitude for oversize surcharge sub-types (UPS >€500 → Over max limits, >€100 → large package, smaller/other → AHS or weight).
  - #9 (sperrgut Bernoulli) disregarded.
  - #10 (shipment_id / tracking collisions) disregarded.
- **T5.** Wrote bank draft `shipping_agent_vocab_harvest_2026-05-22.md` — six trip-ups + glossary + negative space + paste-ready proposal for the shipping-agent docs.

## Decisions made in-flight

- Final trip-up count: **six**, not ten.
- Threshold for "low % invoiced is concerning" tightened from "past ~90 days" to **"past 30 days."**
- TCG canonical filter is `source_system IN ('Picturator', 'PicaAPI')` — PCS excluded for being cost-only and small-sample.

- **T6.** Niklavs cued "let's teach the agent about these things." Recon on shipping-agent docs:
  - `how_to.md` §0 already runs eleven cross-cutting rules; rule 9 covers the % invoiced lag broadly; rule 11 covers cost basis + denominator + bucket invoice-only; translation table covers source-system handles. Confirmed rules 3, 9, 11 from the harvest already taught.
  - `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `GROK.md` are tiny pointer files (~1KB each) routing to `how_to.md`. No mirroring needed.
- **T7.** Applied to `shipping-agent/how_to.md`:
  - Header sentence: "Eleven cross-cutting rules" → "Fifteen."
  - Rule 9 tightened with explicit "current 30 days expected / past 30 days concerning" threshold.
  - Rule 12 added: TCG scope (`Picturator + PicaAPI` only; PCS / Rewallution exclusions).
  - Rule 13 added: shipping cost excludes tax/customs/duties; UPS `Manual Bill` / `838xxx` note.
  - Rule 14 added: `invoice_source` granularity ≠ carrier; `dhl_orwo` / `ups_orwo` bulk-bill allocation.
  - Rule 15 added: oversize-surcharge sub-type heuristic (UPS >€500 / >€100 / smaller-or-other).
- **T8.** Applied to `shipping-agent/reference/known-dq.md`:
  - New section: "Charge classification — `db_schenker` 100% `'unclassified'` by design." Stamped 2026-05-22.
- **T9 (commit).** Brain `4647581` (S029 bank draft + quest-log) + bi-analytics-main `c48bac6` (shipping-agent rules) — both pushed.
- **T10–T20 (alching).** Principal-self alching (gnome agent unavailable due to active-mode mismatch from parallel session). 13 pending drafts triaged:
  - **Step 1 — identity drafts:** 6 promoted to confirmed (4 examine + 1 niksis8_character + 1 keepsake pin). 2 new meta-rules surfaced mid-pass and promoted (`drafts-need-lead-with-concrete-example`, `bank-notes-need-as-of-date`).
  - **Step 2 — bank drafts:** 5/5 promoted with as-of stamps + applied-proposal sections trimmed.
  - **Step 3 — quest-log compression:** no new bank candidates.
  - **Step 3a — self-observation sweep:** at cap (4 meta-rules from mid-pass).
  - **Step 4 — current.md budgets:** all under.
  - **Step 5 — rejected/ patterns:** 2 niksis8_character rejections share layer-routing pattern → flagged for next bankstanding.
  - **Step 6 — skill graduation:** 2/2 spellbook skill drafts promoted (`coverage-questions-time-and-source-axis`, `structural-restructure-mechanism-over-shape`).
  - **Step 7 — `last-alched.md`** bumped to 2026-05-22.

## Decisions made during alching

- Drafting protocol formalized in `examine/confirmed/2026-05-22-drafts-need-lead-with-concrete-example.md`: drafts (a) lead with concrete BEFORE/AFTER example, (b) state rule in 1–3 sentences, (c) cap ~20 lines for confirmed entries, (d) when surfaced for review, follow fixed order: nutshell → recommendation+why → content → decide.
- Bank notes need prominent `**As of:** YYYY-MM-DD` stamp at top — `examine/confirmed/2026-05-22-bank-notes-need-as-of-date.md`. Applied retroactively to all 5 bank drafts promoted this pass.
- Quest-log presence rule refined from "always on turn 1" to "open or resume when substantive work crystallizes" (shape B over shape A) — `examine/confirmed/2026-05-21-quest-log-opening-when-work-is-in-additional-working-dir.md`.

## Open

- ORWO trip-up parked, not lost — revisit once ORWO V1-active-build closes.
- 2 niksis8_character rejections (`escalates-symptom-to-system`, `prefers-evidence-over-premature-infrastructure`) flagged for next bankstanding — both likely belong in global `niksis8/`, not Jebrim's character layer.
- examine/confirmed/current.md and niksis8_character/confirmed/current.md are empty despite ~8 confirmed entries each — user-curated rollup; flagged for principal decision next session.

## Related

- [[shipping_mart_cost_vocabulary_2026-05-22]] — sibling draft (cost-column vocab, % invoiced rule, denominator rule).
- [[shipping_costs_monitoring_nextjs_vocab]] — sibling draft (dashboard-side vocab).
- [[shipping_mart_coverage_audit_2026-05-21]] — coverage audit.
