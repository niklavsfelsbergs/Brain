# S174 — FIF report: UPS May export vs our calculation reconciliation

**Session:** jebrim-8a204c6b · opened 2026-06-09
**Ask:** "What did we last do on the FiF report — did we add the 5 new accounts + VAT logic?" → then: "I posted the UPS export vs our calculation for May in `…/42_fif_orwo_ups_invoice_file/compare_may`. Check how they match."

Anchors: [[S143_51f034e4_fif-report-accounting-fixes|S143]] (the 4-account + VAT-grain fixes), bank notes `2026-06-02-fif-vat-subtotal-grain`, `2026-05-28-ups-orwo-fif-data-quirks`.

## Part 1 — recap ([[S143_51f034e4_fif-report-accounting-fixes|S143]])
Confirmed from the record: accounting asked for **four** new Key-Account-IDs 9102–9105 (not five — flagged the count). Per Niklavs's call they merge into the **single TCG line** (`keyaccount_id`→9101), verified 0 stray rows. VAT fix = compute on the net **subtotal** rounded once (the €15,99 per-line-rounding drift). Both shipped + deployed (ECR `fif_ups_orwo:latest` sha256:2fe5feb6).

## Part 2 — May reconciliation (the work)
Decrypted the UPS portal export (`FIF_export.xlsx`, password-protected OOXML — pattern `UPS@<6-digit acct>`, brute-forced the 3 masked digits locally). Both files = same 21 invoices.

**Headline:** export net €83,005.35 vs our report (= bronze non-tax net) €81,805.56 → **−€1,199.79 (1.4%)**. VAT by-design (19%×net, [[S143_51f034e4_fif-report-accounting-fixes|S143]]). Our report reproduces bronze **to the cent**.

### The arc — I was WRONG first, then corrected
**Wrong diagnosis (floated to Niklavs + drafted an ETL bug report):** bronze drops RES lines via the `insert_to_bronze.sql` anti-join, keyed on the too-coarse 4-tuple `(invoicenumber, trackingnumber, chargecategorycode, chargecategorydetailcode)`. "Evidence": export 6,059 RES lines / €2,639 vs bronze 3,332 / €1,332 (~half).

**ETL team pushed back (solid Redshift checks):** no invoice reloads with net effect (anti-join dedups identical re-sends correctly); RES-per-100-trackings = 27.9, in the all-year 22–30 band; transformer is pure pass-through; bronze RES matches mine exactly. Conclusion: bronze complete; the discrepancy is in how the raw export is counted.

**They were right. Corrected with two findings:**
1. **"RES half-missing" = a taxonomy artifact, not loss.** The €0.48 "RES" charge IS in bronze — under a different code. Same tracking, same €0.48: portal export labels it `RES`; the EDI feed bronze ingests labels it `011 "TB Standard Änderung" / category ADJ-RADJ` (RADJ = residential adjustment). I joined on charge code across **two different UPS code systems**, manufacturing a fake gap. Every one of those €0.48 charges is present in bronze (verified: 2,692 "missing-RES" trackings all present in bronze with the charge under 011/RADJ).
2. **The real €1,199.79 = the portal export DOUBLE-COUNTS charges on 130 trackings (€1,188).** Export net = exactly **2× bronze** on these. Mechanism = **package-dimension fan-out**: these are single-package shipments (`# Packages`=1) carrying **two conflicting dimension records** (Length/Width/High — a re-measure / billed-vs-actual). The portal export is built by joining each charge line to the package-dimension table, so 2 dim rows × each charge → every charge emitted twice. Duplicate pairs are **identical except L/W/H**. 93% of doubled trackings have ≥2 dimension-sets; clean trackings have exactly 1.

### Verdict
**Our FIF report and bronze are CORRECT.** The raw UPS **portal export** over-states by ~1.4% (duplicate-line fan-out). Nothing to fix in the pipeline or bronze; the anti-join is structurally fragile (worth hardening defensively, per the ETL guy) but is **not** causing this — delete-then-insert would recover nothing. Any fix belongs to whoever generates the portal export (de-dup the package-dimension join).

**My error (the lesson):** confirmed an architecturally-plausible root cause with a comparison contaminated by cross-taxonomy code joins, and never checked the raw export for duplicate lines before blaming downstream. Same grain/fan-out class as the bug I was chasing — in reverse. When two sources disagree on a total, suspect a grain/key mismatch before suspecting dropped data.

## Files
- No brain code or repo files changed. Analysis only (python + fastexcel/msoffcrypto + Redshift via `shared.database.pull_data` and the redshift MCP).
- **Debris (manual cleanup needed):** `…/42_fif_orwo_ups_invoice_file/compare_may/_dec.xlsx` — decrypted UPS billing data, unencrypted on disk. The delete-hook blocks tool-side removal; delete manually.

## Pending external actions
None pending. No commits to bi-analytics/bi-etl, no sends.

## Cascade
None — no canonical docs/status-tables touched.

## Main-brain changes
None.

## Leaving open (optional, none blocking)
- Corrected note back to the ETL team (acknowledge their analysis + the 130-duplicate-tracking / RES-vs-011-RADJ specifics) — offered, not yet written.
- Manual delete of `_dec.xlsx`.

## Log
- 2026-06-09: Recap [[S143_51f034e4_fif-report-accounting-fixes|S143]] (4 accounts→9101 merge + VAT subtotal-grain). Decrypted UPS portal export. Reconciled May: report/bronze €81,805.56 vs export €83,005.35 (−€1,199.79). Mis-diagnosed as bronze dedup dropping RES; drafted ETL bug report. ETL team rebutted with Redshift checks. Re-verified against ground truth: (1) RES "loss" = RES-vs-011/RADJ code-taxonomy artifact, charges present in bronze; (2) real residual = portal export package-dimension fan-out double-counting 130 trackings (€1,188), export=2×bronze, dup pairs differ only in L/W/H. Verdict: report+bronze correct, portal export inflated. Retracted the bug report. Quest in-progress pending the optional corrected ETL note.
