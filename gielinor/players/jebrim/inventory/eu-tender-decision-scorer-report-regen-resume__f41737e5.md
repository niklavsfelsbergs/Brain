# RESUME — EU Tender decision_scorer + report regen (S118, session f41737e5)

**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`. Tender HEAD `96bc47f` (S117, local-only, unchanged this session — only gitignored parquet + HTML regenerated).

## Done this session
- Re-ran `decision_scorer.py` → `data/scenarios.parquet` (90 sets, do_nothing sanity €0.00 PASS). No code change needed.
- Re-ran `report.py` → `decision_report.html` (dated 2026-05-28, 90 sets, new ranking).

## Ranking (decision-relevant, ≤6 active carriers, Q1 mandatory saving)
all_renewals_plus_gls €201k · all_renewals_plus_austrian_post €196k · renew_maersk_drop_dpd_pl_plus_gls_dhl_express €196k (0 uncov) · renew_maersk_plus_gls €206k · add_dhl_express €2.6k mand/€129k migration. renew_dpd_pl −€9.8k (over-prices its own incumbent). Decision basis still full-year (parked); this is Q1 unit-cost.

## Open / next
1. **Report does not surface the 2 material S117 assumptions** — dpd_pl CH customs €484k, gls EFTA €278.9k (both collapse under consolidated customs). Only Hermes caveat is in the HTML. Fix = add to `docs/REPORT_NOTES.md` + report.py caveat prose (confirm-with-draft; never auto-write docs/*). RECOMMENDED next step.
2. **Commit** scorer/report outputs + brain-side S117+S118 records — pathspec-scoped, local-only, NEVER bare `git add` (~80+ unrelated WIP files). Principal-gated.
3. Brain-side S117 records STILL uncommitted (carried from d1a3b803).
4. FedEx + DHL Paket HELD (round-2). Sub-region routing (GLS Q11) residual.
5. decision_report.html review — eyeball in browser (not done in-session; no GUI).

## Run commands
`cd .../2_analysis && PYTHONUTF8=1 python decision_scorer.py` then `... python report.py`.
