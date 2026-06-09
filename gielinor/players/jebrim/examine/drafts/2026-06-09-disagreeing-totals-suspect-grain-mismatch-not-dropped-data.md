# When two sources disagree on a total, suspect a grain/key mismatch before dropped data

**Observation ([[S174_8a204c6b_fif-may-export-reconciliation|S174]], 2026-06-09).** Reconciling the UPS May portal export against the FIF report, I found a €1,199.79 (1.4%) gap and diagnosed it as **bronze dropping RES lines** via a too-coarse anti-join dedup key — confidently enough to draft a bug report for the ETL team. I was wrong on both halves:

1. The "RES half-missing" evidence came from **joining on charge code across two different UPS code systems** — the portal export labels a charge `RES`; the EDI feed bronze ingests labels the *same* charge `011 / RADJ`. The charges were in bronze the whole time. My join manufactured the gap.
2. The real residual was the **portal export double-counting** charges on 130 trackings (export = exactly 2× bronze) via a package-dimension join fan-out — i.e. the *export* was wrong, not bronze.

The ETL team caught it with ground-truth Redshift checks (reload behaviour, RES-per-100 trend band, pass-through transformer).

**Why it happened.** I confirmed an *architecturally plausible* story (coarse dedup key → dropped lines) with a comparison that was itself contaminated by a grain/taxonomy mismatch — the exact same class of bug I was chasing, in reverse. Plausibility + a confirming-looking number is the trap; I didn't run the cheap disconfirming check (is the *raw export* itself duplicated/relabeled?) before assigning blame downstream.

**How to apply.** When two sources disagree on a summed measure: **first suspect a grain or key mismatch** (a join fan-out, a relabeled code, a different population) — not dropped data. Before blaming a downstream system, verify the *upstream/raw* side is clean: check for duplicate lines, and confirm you're joining on a key that means the same thing on both sides. A code-level join across two taxonomies is guilty until proven innocent. This is the sibling of [[2026-06-02-static-audit-ranking-is-a-hypothesis-until-measured]] and the "verify the thing, don't trust the wiring" reflex — extended to *don't trust your own confirming comparison until you've ruled out that it shares the bug's shape.*
