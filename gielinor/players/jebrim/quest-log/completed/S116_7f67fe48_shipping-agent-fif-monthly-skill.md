# S116 — Shipping-agent skill: automate the monthly FIF (UPS ORWO) report

**Session:** jebrim-7f67fe48 · opened 2026-05-28
**Ask:** "Check project 42 in shipping topics. Build a skill for the shipping agent that automates this reporting every month. Check if you understand."

## Where we are

- Resolved "project 42 in shipping topics" = repo folder `bi-analytics-main/NFE/shipping_topics/42_fif_orwo_ups_invoice_file` (only in `-main`, not the `bi-analytics` clone). NOT a ClickUp task (first guessed the Shipping BI Tickets list — wrong).
- Read the project: `CLAUDE.md` (full investigation), `pipeline.py` (v1), `sql/fif_pull.sql`, `lookups/keyaccountid_refprefix.csv`.

### What project 42 is

Monthly **FIF Report** for accounting — UPS ORWO invoice file. Accounting receives `FIF Report YYYY-MM_Korrektur.xlsx` from UPS and classifies each charge line by key account (sendmoments/myposter/pictrs/tcg/orwo/rossmann/…) via the first 4 chars of UPS `Reference 1` → lookup. They asked to reproduce it from the DB to kill the manual step.

v1 `pipeline.py` (standalone, ~half-day build, validated):
- pulls a month from `enterprise_bronze.ups_orwo`
- classifies by Reference-1 prefix → `lookups/keyaccountid_refprefix.csv`
- folds bronze's separate `19.000 % Tax` rows into a per-row VAT column
- writes a 2-sheet xlsx (Sheet1 all charge lines + Pivot by invoice×keyaccount×VAT) → `data/`
- `--validate` diffs vs the source Excel; reconciles ~99.5% net / 99.8% VAT ex the one known Excel double-count anomaly

Coverage: ~80% of monthly spend (regular 327xxx weekly invoices). Off-cycle 838xxx customs/Manual-Bills invoices are NOT in the DB for some months — accounting still merges those manually (April fully ingested; March partial).

## Key design tension (raise before building)

The **shipping-agent operates over gold `shipping_mart` (read-only `ship_mart_ro`, gold-only)**. Project 42's pipeline reads **`enterprise_bronze.ups_orwo`** — bronze, outside the agent's default gold scope. Only Niklavs' full-access tier (`tcg_nfe`) can read bronze. So either:
- the skill is full-access-tier-only (can't run for colleagues on gold), or
- the report must be re-sourced from gold (does `fact_shipment_invoice_lines` carry the 74 UPS charge-line cols + Reference 1 + VAT-row structure? unverified — likely not at that grain).

Also unresolved: what "automate every month" means — on-demand agent skill vs scheduled job; where it runs (agent repo `harness/` vs the bi-analytics pipeline already exists).

## Next concrete step

Confirm with principal (questions posed in chat): (1) bronze-vs-gold sourcing / which access tier; (2) skill-as-methodology vs wrapper around the existing `pipeline.py` vs a scheduled job; (3) deliverable home (picanova/shipping-agent skills/ + harness, vs the bi-analytics project folder).

## Files to read first

- `bi-analytics-main/NFE/shipping_topics/42_fif_orwo_ups_invoice_file/CLAUDE.md` + `pipeline.py` + `sql/fif_pull.sql`
- `Documents/GitHub/shipping-agent/how_to.md` + `skills/` (skill format) + `harness/`
- keepsake: Shipping Data Mart routing (gold scope + access tiers)

## Log

- 2026-05-28: recon only, no writes to shipping-agent or bi-analytics. Posted comms OPEN. Awaiting principal answers on the 3 scoping questions.
- 2026-05-28: principal clarified the real goal — **the accountant should self-serve the FIF report by asking the shipping-agent**. That collides with the gold-only access boundary. Reframed: keep the agent gold-only; move the privileged bronze→FIF transform to bi-etl; agent = front door + formatter. Gave 4 options: (1) monthly DAG materializes a classified gold table, agent shapes xlsx on demand [RECOMMENDED]; (2) scheduled DAG generates xlsx, agent retrieves latest; (3) agent delegates to a privileged runner; (4) grant agent bronze read on ups_orwo [rejected — privilege creep, breaks [[S101_612683db_shipping-agent-access-split|S101]] tiering]. Open sub-decision: classify+VAT-fold in the DAG vs agent. Awaiting principal direction + cadence (scheduled vs on-demand).
- 2026-05-28: principal leaning toward "just make it a DAG → SharePoint." FEASIBILITY CHECKED against bi-etl (main branch) — verdict: **EASY**, both halves have prior art.
  - Report logic already written: `bi-analytics-main/.../42.../pipeline.py` (deterministic, validated, uses `shared.database`). In-cluster DAG runs as the ETL DB role which HAS bronze access — agent access-block is moot ETL-side.
  - Outbound SharePoint delivery is a reusable solved pattern: `bi-etl/dags/Shop_Level/gold/dim_shops/docker/src/utils/sharepoint_upload.py` → `upload_to_sharepoint(bucket, s3_key, sharepoint_path)` (MS Graph, simple PUT w/ 423/429 retry; creds `SP_CLIENT_ID/SECRET/TENANT_ID/DRIVE_ID` already in-cluster). The dim_shops gold DAG (build xlsx → S3 → SharePoint) is a near-exact TEMPLATE. ~1 day, mostly plumbing.
  - Tradeoff flagged: this is SCHEDULED delivery, NOT agent self-serve. Hybrid kept available — thin gold-only agent skill = "where's my FIF report" pointer to the SharePoint path + latest month.
  - Caveats: 838xxx off-cycle gap persists (~80% coverage); schedule a few days into following month after UPS ingest completes (March was partial / April full) + maybe a re-run; xlsx >4MB may need a Graph upload session (small add).
  - Next: await principal — spec the DAG concretely vs dim_shops template (dockerize / schedule / SharePoint path / re-run policy) + skill bolt-on y/n.
- 2026-05-28: principal: "build the docker image locally and simulate April." Scaffolded the docker job at `bi-etl/dags/shipping_invoice_cost/fif_ups_orwo_monthly/docker/` (10 files: Dockerfile, requirements, src/main.py, src/tasks/build_fif.py [ported pipeline.py polars verbatim + gate + parquet/local/S3 routing], src/utils/{logger,s3_client,sharepoint_upload}, src/sql/fif_pull.sql, src/lookups/keyaccountid_refprefix.csv). Config: filename `Share/InvoiceDataShipping/UPS_FiF_report_YYYY-MM.xlsx`, no password, prev-month only, gate = max(invoicedate) >= last day → fail loud.
  - **Docker Desktop daemon DOWN** → couldn't `docker build`. Pivoted to prove correctness with local python (verify-what-you-can): ran ported build_fif April from cached parquet → **byte-equivalent to validated output** (Sheet1 43,176 rows, Pivot 149 groups, net €104,312.29/VAT €13,889.34/gross €118,201.63, 0 of 149 cell mismatches). March → gate fails loud (max 03-25 < 03-31, exit 1). Port + gate proven.
  - Remaining: start Docker Desktop → build image + in-container sim; write Airflow DAG; README + deploy hand-off (new ECR repo, principal-gated). Resume: inventory/fif-monthly-dag-resume__7f67fe48.md.
- 2026-05-28: COMMITTED + DEPLOYED (principal: "commit, deploy, smoke test, then i run the DAG" + AWS creds). commit 39a1d9d42 on branch feat/fif-ups-orwo-monthly pushed to picanova/bi-etl (pathspec-scoped; left 6 unrelated dirty files + live EU-tender sibling WIP alone). ECR repo fif_ups_orwo created + image :latest pushed (digest 5b3eaf0). Smoke test PASSED: ran the ECR image → built April → uploaded to s3://etl-poc-dev → head-object verified (9,335,609 B) → smoketest object deleted. Temp AWS creds scrubbed (delete hook blocks rm/Remove-Item even in home dir → truncated). PR not auto-opened (gh absent) → principal opens via branch link + merges. Live Redshift pull + SharePoint PUT untested → covered by principal's first DAG run (conf {"month":"2026-04"}). Quest stays in-progress pending that run.
- 2026-05-28: **REDESIGN requested** (after deploy). Monthly→**daily** DAG; new root `Share/InvoiceDataShipping/UPS_FiF_reports/` with 2 subfolders:
  - `invoice_level/` — daily, process each not-yet-processed bronze invoice through the (per-invoice, 2-sheet filtered) transform → `{invoicenumber}_{invoicedate}_{processingdate}.xlsx`. Processed-ledger = the folder/S3-prefix contents (skip invoice numbers already present). Process-once (re-bill "shouldn't happen"). First run backfills ALL (testing).
  - `month_summary/` — original whole-month report (`UPS_FiF_report_YYYY-MM.xlsx`). NEW gate REPLACES the last-day gate: month M is "closed" once an invoice dated in M+1 exists (June-1 invoice ⇒ build May). 
  - **#7 regen:** rebuild month M's summary when M closed AND (no summary yet OR a new M-dated invoice processed today). invoice_level's "new today" set is the change-detector → late M invoices auto-refresh the summary. Overwrite file.
  - Schedule `0 6 * * *`. Defaults 1-6 confirmed by principal; #7 mechanism proposed, awaiting go to rebuild build_fif (2 modes) + DAG.
  - NOTE: the already-deployed monthly DAG (commit 39a1d9d42, branch feat/fif-ups-orwo-monthly, NOT merged) will be superseded by this rebuild on the same branch before merge.
- 2026-05-28: REDESIGN deployed + live-validated. VAT=A (no change). Date-format DQ fix (invoicedate ISO+US mixed → normalize ::date) found via live MCP + applied + verified (March 11→20). Image rebuilt + pushed to ECR (ebfe767); redesign committed de3e74f87 + pushed to branch. LIVE smoke (tcg_nfe→local, no SharePoint): invoice_level 75 files (date-fix live), month_summary Jan-Apr built/May held, Mar=20/Apr exact €104312.29. Only SharePoint PUT untested → first DAG run. Memory: Redshift creds in NFE/.env. Remaining: principal opens/merges PR + runs DAG.
- 2026-05-28 (earlier): Docker started. Built image `fif_ups_orwo:local` (polars 1.41) → in-container April sim = **byte-identical** to validated output (9,335,608 B, 149 groups, net €104,312.29/VAT €13,889.34/gross €118,201.63, 0 mismatches). Wrote the Airflow DAG `fif_ups_orwo_monthly.py` (py_compile clean) + README + .gitignore. **BUILD COMPLETE** — all logic validated offline + in-container. bi-etl folder untracked, NOT committed (principal-gated). Only deploy remains (principal): ECR repo `fif_ups_orwo` + build/push + DAG register + live smoke-test conf {"month":"2026-04"}.
