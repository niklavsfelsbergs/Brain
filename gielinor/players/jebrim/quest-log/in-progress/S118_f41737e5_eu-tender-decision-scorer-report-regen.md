# S118 — EU Tender 2026: decision_scorer + report regen

**Session:** jebrim-f41737e5 · 2026-05-28 · player Jebrim
**Continuation of:** S117 (d1a3b803, ended clean ~1min before respawn, same terminal). Adopted resume `inventory/eu-tender-engine-builds-resume__d1a3b803.md`.

## Ask
Principal: "continue on EU tender." Confirmed via multiple-choice → run `decision_scorer.py` + report regen (Q1 portfolio scoring across the 6 rebuilt engines).

## Turn log

**T1 — respawn + ground.** Loaded Jebrim layers; sibling check (sole live sibling jebrim-7f67fe48 = S116 FIF, different repo, no overlap). No pending drafts → no alching due. Posted OPEN. Confirmed scope with principal (multiple-choice → "decision_scorer + report").

**T2 — verify inputs (scorer needs no code change).**
- `cost_matrix.parquet` fresh (today 13:24, all 9 engines incl. dpd_pl-2.0.0 `5998ef6` / gls-2.0.0 `96bc47f`).
- `_decision_sets.py` carrier set already current (dpd_pl, gls, all 6 entrants present; no edit needed).
- `scenarios.parquet` was STALE (2026-05-22, pre-rebuild) → re-run required.

**T3 — ran `decision_scorer.py`.** Clean. 4,757,535 adjusted matrix rows / 528,615 shipments. UPS adj: OML dropped 106 (€135,955 baseline removed), LPS halved on 646 (€37,151). **90 decision sets** scored (was 35 in May — carrier set expanded). `scenarios.parquet` rewritten (90×13). **Sanity: do_nothing mandatory_saving = €0.0000 (PASS).**
  - Decision-relevant (≤6 active carriers): `all_renewals_plus_gls` €201k (1 uncov), `all_renewals_plus_austrian_post` €196k, `renew_maersk_drop_dpd_pl_plus_gls_dhl_express` €196k (0 uncov), `renew_maersk_plus_gls` €206k (4 uncov), `add_dhl_express` €2.6k mand / €129k migration (0 uncov).
  - `renew_dpd_pl` −€9.8k mandatory (engine over-prices vs DPD's own incumbent invoice on its parcels) — consistent w/ DPD PL being cheap as an *addition* but not a like-for-like renewal win.
  - Diagnostic sets with 7–11 active exceed CARRIER_CAP=6 (validate() warns, still scored) — upper-bound only, not decision options.

**T4 — ran `report.py`.** Clean (EXIT=0). `decision_report.html` regenerated (211KB, 13:40), dated 2026-05-28, references "90 decision sets". Reflects the new ranking.

## Open / gap (surface to principal)
- **Report does NOT flag the two material S117 assumptions.** Only per-engine caveat prose in the HTML is the older hardcoded Hermes 11-assumptions block. The dpd_pl CH-customs €484k (@44/parcel opt-1) and gls EFTA €278.9k (@25/parcel CH/NO) levers — both collapsing under consolidated customs — are baked into engine costs but invisible to a decision-maker reading the report. Per project doc system these belong in `docs/REPORT_NOTES.md` → drained into report.py prose (confirm-with-draft; never auto-write docs/*).
- decision_scorer.py + report.py needed **no code change** — pure re-run against the S117-regenerated cost_matrix.
- Commit (scorer/report outputs + brain-side records) HELD — principal-gated, pathspec-scoped, local-only.
- FedEx + DHL Paket still HELD (round-2 pending).

## Outputs touched (out-of-tree tender repo, uncommitted)
- `2_analysis/data/scenarios.parquet` (regenerated, gitignored)
- `2_analysis/decision_report.html` (regenerated)
