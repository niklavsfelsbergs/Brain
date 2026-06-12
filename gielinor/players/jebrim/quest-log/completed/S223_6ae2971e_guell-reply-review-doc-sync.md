# S223 — Güll Round-1 reply review + EU-tender doc sync

**Player:** Jebrim · **sid8:** 6ae2971e · **Born:** S223

## What was asked

Niklavs (Jebrim) flagged a PDF from Güll in `carrier_responses_to_open_questions/Gull/` — check whether it answers the open questions we'd dispatched. Then: update all relevant docs and report whether a blocker remains. Then: draft a handover prompt for the next session (first task = investigate Güll's portfolio fit). Then a reorder discussion (build engine first?), a scope check (Güll AT/CH only?), and close.

## What happened

- Located the reply: `bi-analytics-main/NFE/projects/2_EU_tender_2026/carrier_responses_to_open_questions/Gull/Proposal_..._Complementary information_2026_20260610.pdf` (6 pp, Thomas Jepsen). Extracted via `pdftotext -layout` (the Read tool's pdftoppm path is unavailable on this box). 12 numbered points, 1:1 to our 12-question dispatch.
- **Verdict: 11/12 resolved, 1 partial (Q11).** Headline favourable — Güll renegotiated its AT carrier into **fixed** surcharges: AT fuel 27.7% variable → **15% fixed 12-mo**; Maut 0.30 → **0.32 fixed**. CH customs fear retired (40 EUR declaration is per-truck, parcel-count-independent → near-zero/parcel; ZAZ waives the 2%). CH energy is variable-monthly (Q1 months below the engine's flat 0.04). FX = per-month strongest-CHF (Commerzbank). New AT oversize tail surfaced: ~4k items/yr → 2nd AT carrier @ 45 EUR (currently hard-rejected).

## Decisions made in-flight

- **No carrier blocker remains.** Güll moves from "last carrier with zero reply" to deterministic-ready for Q1; `guell-2.0.0` rebuild unblocked (PLAN §B.21). Residuals (Q11 per-pallet specifics, internal density assumptions, un-wireable shape branch) are non-blocking — same posture as Austrian Post.
- **Build-first, not triage-first** (Niklavs' call, agreed). Güll already sits in the leading ≤6-active set (`renew_maersk_plus_guell`) on the OLD over-priced engine, so the rebuild can't be wasted, and the honest portfolio answer needs the regenerated cost-matrix — a hand-adjusted triage on stale numbers is the proxy trap. Handover reordered to: build `guell-2.0.0` → regenerate matrix/scorer/report → portfolio-fit read falls out.
- **Scope confirmed against ground truth:** Güll is AT + CH (+ LI on the CH lane) — per `carriers/guell/constants.py:14` (`# Country scope (AT/CH lanes only; LI piggy-backs on CH`) and the offer title. That's the *offer* scope, not Güll's hard ceiling (it's a Lindau forwarder, floated ex-PL trailer consolidation), but anything else would be a fresh carrier ask. So portfolio replace/complement candidates are AT/CH players only (Austrian Post; CH legs of DPD PL / GLS / Maersk / DHL Paket).

## Artifacts produced (all in bi-analytics-main, NOT the brain repo)

- **new** `Gull/REVIEW_CONCLUSIONS.md` — full 12-Q review + verdict + engine-work queue.
- **new** `1_offers/picanova/Güll/questions_round2.md` — the Q11 outbound per-pallet follow-up.
- `questions_for_carrier.md` — status table flipped (11 RESOLVED / 1 PARTIAL).
- `open_questions/guell.md` — REPLY UPDATE header + B1–B4/C1/C2/C3/C5/F1 status flips.
- `ASSUMPTIONS.md` — Güll constants table rewritten to confirmed values.
- `OPEN_QUESTIONS.md` — Güll section unblocked + cross-carrier ZAZ Güll leg resolved.
- `PLAN.md` §B.21 — unblocked; constants/structural locked to reply; rollup line updated.
- `CROSS_CARRIER_OVERVIEW.md` — Güll row + CH-customs theme updated.

**These bi-analytics-main edits were committed** at `5399d7f` (main, pathspec-scoped to the 8 files; sibling `.claude/reference/*` + `final_report/*` left untouched; not pushed) on Niklavs' go after the first close.

## Pending external actions

None pending.

Cascade. None — work confined to the EU-tender repo + this quest-log/inventory.
Main-brain changes. None to `gielinor/` beyond this quest-log entry, the inventory resume, and one examine draft.

---

## Continuation 2026-06-12 — guell-2.0.0 BUILD + portfolio-fit read (same session, sid8 6ae2971e)

The planned next phase ran: built the engine, regenerated the chain, answered the payoff question. Survived two laptop crashes mid-build; all artifacts verified intact on disk after each.

**Engine (`bi-analytics-main/.../2_analysis/carriers/guell/` → guell-2.0.0, 19/19 fixtures):** fuel 0.2727→0.15 on base+B2C+bulky (not Maut); Maut 0.30→0.32; CH energy flat→per-month `CH_ENERGY_CHF_BY_YM` (Jan-25→Jun-26 from the reply PDF); FX single-point→per-month `CHF_TO_EUR_BY_YM` mechanism (flagged 1.08 proxy — reply gave the mechanism not the values); PEAK=0; 4 new line-haul surcharges (inbound sprinter 955÷1200≈0.80, line_haul_at 24.50÷150, line_haul_ch 40÷150, ch_declaration 40÷800); new 4th service `at_oversize` (45 EUR 2nd-carrier recovery, ~4k/yr, was a hard reject); engine now requires `shop_order_created_date`.

**Chain regenerated:** cost_matrix rebuilt (31.6M rows, 2025 full-year, all guell-2.0.0); decision_scorer → scenarios.parquet; decision_report.html (also edited report.py: removed guell from HELD_ENGINES → trustworthy; rewrote Güll verdict + open-items row + held-engine prose); bias_table.md refreshed (repointed _refresh_bias_table.py to load_cost_matrix(), column-pruned to avoid OOM). Docs: PLAN §B.21 `[x]`, engine CLAUDE.md version-history + surcharges table, ASSUMPTIONS verdict line.

**Mishap + recovery worth noting:** a careless `git archive | tar -x --strip-components=5 -C .` extracted guell-1.0.0 INTO carriers/guell/ (overwriting my 2.0.0 working files; tar can't delete so the 4 NEW 2.0.0-only modules survived), then `mv guell guell_v1` renamed the hybrid away. Restored carriers/guell to clean 2.0.0 by Read-then-Write of the 6 clobbered files (all content was in-conversation), re-verified 19/19. Lesson: never tar-extract a git path into a live package dir — extract to /tmp first.

**THE ANSWER (read off the regenerated scorer + bias):** "cheaper Güll" is **FALSE**. Clean v1→v2 isolation (same full-year pop, guell_v1 restored from HEAD): engine +30% (+€330.8k), like-for-like **+14.5%**; CH PostPac €7.08→€8.37 (+18%), AT €4.33→€4.97 (+15%). Line-haul outweighs the fuel/Maut/energy cuts — exactly as DECISIONS.md 2026-05-19 predicted. **Verdict (c) HOLD:** within-matrix marginal +€163,897 (was ~€255k apparent on v1); strengthens renew_maersk_plus_guell by +€186k but set stays −€629k (Maersk-alone is the destroyer); **displaces Austrian Post** (Güll > AP €105k; bias winning-slice AP wins 8,803→486); does NOT unlock CH-leg retirements (Güll's CH got dearer). Brand-new-carrier caveat front-and-centre (no parity, fixtures only). Confound flagged: raw scenario absolutes also moved because the whole 12-engine matrix refreshed to current code — so the clean signal is the within-matrix marginal + the per-parcel isolation.

## Pending external actions (continuation)

- **bi-analytics-main edits are UNCOMMITTED** (engine + report.py + bias + PLAN + ASSUMPTIONS + CLAUDE.md) — Niklavs to give the commit go (separate work repo, pathspec-scoped).
- Round-2 Q11 outbound per-pallet follow-up drafted (`questions_round2.md`); Commerzbank strongest-CHF FX-value pull still open. Both non-blocking.
