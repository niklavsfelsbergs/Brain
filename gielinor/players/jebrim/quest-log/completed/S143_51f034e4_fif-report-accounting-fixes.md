# S143 — FIF report fixes from accounting feedback

**Session:** jebrim-51f034e4 · opened 2026-06-02
**Ask:** Apply accounting's two review fixes to the UPS-ORWO FIF report (from the email reply: "this looks good. Could you please just add four more Key-Account-IDs … 9102, 9103, 9104, 9105 … belong to TCG" + "calculate the VAT-amount with net amount and tax-rate according to file … VAT and gross matched the real invoices … apply the same logic").

Anchors: [[S116_7f67fe48_shipping-agent-fif-monthly-skill|S116]] (built the FIF DAG), bank note `2026-05-28-ups-orwo-fif-data-quirks`.

## The two fixes

### 1. Four new TCG key accounts (9102–9105)
Added to the prefix→keyaccount lookup `keyaccountid_refprefix.csv` (both homes):
```
9102,9102,tcg
9103,9103,tcg
9104,9104,tcg
9105,9105,tcg
```
keyaccount_id = the prefix itself (matching the table's existing one-row-per-ID convention, e.g. 9101→tcg, 9001/9002→cruisevision), keyaccount_name = tcg. **They are NOT hypothetical** — April bronze already carries 9102–9105 on 6,655 rows; previously they hit the fallback branch (ID kept = prefix, but **name "ORWO"**). The fix relabels **€9,548.44 net** (4,473 charge lines post-fold) from the ORWO bucket to TCG in April — exactly what accounting asked. Per-ID April net: 9103 €8,015.49 / 9104 €1,224.99 / 9102 €243.48 / 9105 €64.48. Forward months inherit the mapping. Pivot structure unchanged; only the name flips ORWO→tcg (and any future report distinguishes the four IDs).

### 2. VAT rounding-grain fix
Root cause of accounting's €15,99: the report computed per-line `VAT = round(net × 0.19, 2)` then **summed the rounded lines** (~43k lines/month → accumulated rounding drift). Accounting (and the real UPS invoice) compute VAT on the net **subtotal** — `net_subtotal × rate`, rounded once. Same 19% rate; only the grain differed.

Changes (both homes):
- `fold_vat_rows`: per-line VAT now full precision (`net × 0.19`, **no** per-line `.round(2)`), gross = net+vat full precision — matches the Excel's live-formula behavior; the 2dp number format still displays cents. Lets the totals round once.
- `build_pivot`: VAT Total = `(Net Total × rate/100).round(2)` computed on the summed net; Gross Total = Net Total + VAT Total (exactly consistent).

**Verified empirically (April cached parquet, patched standalone):**
| | Before | After |
|---|---|---|
| Net Total | 104,312.29 | **104,312.29** (unchanged) |
| VAT Total | 13,889.34 | **13,873.36** (−15.98 ≈ the €15,99) |
| Gross Total | 118,201.63 | **118,185.65** (= net+vat; 0 inconsistent pivot rows) |

Sheet1 full-precision VAT sum reconciles to 13,873.35 (within a cent of the pivot — both correct). NB the raw bronze `19.000 % Tax` rows sum to €13,831.66 — a *different* figure; accounting's target is net×rate (€13,873.36), NOT the tax-row sum, per their explicit wording. (Verified before coding — avoided the wrong "use the real VAT rows" fix.)

## Files changed (4, both homes kept in sync)
- `bi-analytics-main/NFE/shipping_topics/42_fif_orwo_ups_invoice_file/lookups/keyaccountid_refprefix.csv`
- `bi-analytics-main/NFE/shipping_topics/42_fif_orwo_ups_invoice_file/pipeline.py` (fold_vat_rows, build_pivot)
- `bi-etl/dags/AI_Automations/shipping_nfe/fif_ups_orwo_monthly/docker/src/lookups/keyaccountid_refprefix.csv`
- `bi-etl/dags/AI_Automations/shipping_nfe/fif_ups_orwo_monthly/docker/src/tasks/build_fif.py` (fold_vat_rows, build_pivot)

## Leaving open / next
- **NOT committed** (principal-gated; two separate repos — bi-analytics-main + bi-etl). Awaiting go.
- **Production deploy** to actually deliver the corrected report: rebuild the `fif_ups_orwo` ECR image from the patched `build_fif.py` → push → re-run the DAG (month_summary for April) → overwrites the SharePoint xlsx accounting already has. AWS/ECR + DAG run are principal actions.
- Decision to confirm with accounting (non-blocking): the 4 new IDs render as **4 distinct TCG-named pivot rows** (not merged into the single 9101 line). Data + their wording ("four more Key-Account-IDs") support distinct; flag if they wanted one combined TCG line.
- Debris: `…/42_fif_orwo_ups_invoice_file/_amt.py` left on disk (temp probe) — delete hook blocks tool-side `rm`/`Remove-Item` globally; untracked, won't be committed; remove manually.

## Log
- 2026-06-02: Recon ([[S116_7f67fe48_shipping-agent-fif-monthly-skill|S116]] quest + bank note + both code homes). Diagnosed VAT issue = per-line rounding grain; verified on April parquet (delta €15.98 ≈ €15,99). Applied both fixes to both homes. Re-ran patched standalone April: net unchanged, VAT 13,873.36, gross consistent, 4 new key accounts classify to tcg (€9,548 relabeled). Quest stays in-progress pending commit + deploy.
- 2026-06-02: Principal: commit yes / deploy yes / **single TCG line** (not 4 distinct rows). Changed both lookups 9102-9105 → keyaccount_id **9101** (merge into the one tcg line). Re-verified April: net/VAT/gross unchanged, 0 stray 9102-9105 rows, all under 9101 (tcg net €60,079.14).
- 2026-06-02: Git reality — bi-etl lookup is **gitignored** (`*.csv`), bi-analytics standalone is **fully untracked on main**. Committed only the clean unit: bi-etl `build_fif.py` → `fff01cfff` on `feat/fif-ups-orwo-monthly` (NOT pushed). Lookup ships via image rebuild, not git. bi-analytics standalone left local (dev copy) per recommendation.
- 2026-06-02: DEPLOY — Docker + AWS creds (temp STS) provided. Rebuilt `fif_ups_orwo:latest` from this checkout (both fixes bake in; lookup gitignored but no `.dockerignore` so it's in the build context). **Smoke-tested the IMAGE on April** (synthetic May parquet → April "closed", offline month_summary): image xlsx = net 104,312.29 / VAT 13,873.36 / gross 118,185.65 (=net+vat) / 0 stray / single 9101 tcg line. Pushing to ECR (123038732324.../fif_ups_orwo:latest).
- 2026-06-02: Image pushed to ECR — `fif_ups_orwo:latest` digest `sha256:2fe5feb6`, ECR login scrubbed. DAG pins `:latest` (K8s Always-pull) → next scheduled run uses it.
- 2026-06-02: Principal directives — (a) **un-gitignore the lookup** ("that's important, leave it in"); (b) **push bi-analytics too** ("don't want to lose it"); (c) **skip the April regen** ("we don't recalculate, it's fine").
  - bi-etl: added scoped `!` negation for the lookup, committed it (`530e158da`), pushed `feat/fif-ups-orwo-monthly` (now carries VAT fix `fff01cfff` + tracked lookup).
  - bi-analytics: branched `feat/fif-orwo-standalone` off main, un-ignored the lookup, committed the standalone project 42 (pipeline.py + lookup + sql + CLAUDE.md, `72a8cf0`) from the **staged index only** — the shared tree had heavy parallel-session WIP (S124 `4_automated_shipping_report`, playground deletions) which I did NOT touch. Pushed.
- STATE: both branches on remote, awaiting principal merge→main. April NOT regenerated (principal's call — future months get the fix via the deployed image; April stays as-is). bi-analytics local checkout left on `feat/fif-orwo-standalone` (feature-branch workflow; preserves the local standalone copy).
- Debris in project 42 (untracked, delete-hook-blocked): `_amt.py`, `_mk_may.py`, `_check_xlsx.py`, `_vat_diag.py`, `_verify.py`, `_smoke_data/`, `_smoke_out/`.
- HARVEST candidate: principal correction — config/lookup/mapping files belong in git, not gitignored as "data" (the `*.csv` blanket rule over-excluded a deploy-critical lookup).
- 2026-06-02 [CLOSE]: **No pending external actions** — all commits (bi-etl fff01cfff/530e158da, bi-analytics 72a8cf0) + pushes + ECR push (sha256:2fe5feb6) done. Harvest: 1 examine draft (surface-and-fix-gitignored-config), 1 bank draft (fif-vat-subtotal-grain), 1 memory (gitignored-config-is-a-defect). Quest GRADUATED → completed/ (deliverable shipped + committed + pushed; the only remainder — merging the two feature branches to main — is yours, not an open dep on this work). Veto to carry forward.
