# S254 — EU tender no-Hermes ops report: one service per row

**Player:** Jebrim · **sid8:** 9ced1d5b · **2026-06-17**
Continuation of [[S245_3172630e_eu-tender-no-hermes-routing-ops-coherence|S245]] (the operational dispatch report). Quest closed same session — deliverable shipped + committed.

## Ask

Niklavs, looking at the ops routing report (`routing_report_ops_no_hermes.html`), asked why DE / WICKELVERPACKUNG 30x20 / "all weights" showed **two** DHL services (Kleinpaket 9,665 · Paket DE 1,822) for one dest/package. Then: check it's actually size-driven; show the split; make the fix; ensure the service column always carries exactly one service.

## What happened

1. **First explanation was wrong.** I said the split was size-driven (the `svc_cell` "size-bound → volume shares" branch). Niklavs told me to verify against the data.
2. **Verified against the parquets** (`routing_assignment.parquet` + `population_2026q1.parquet`): WICKELVERPACKUNG 30x20 is a **fixed-dimension** packagetype — d_max 35, volume 3,972.5, L+G 90.4 all constant. The split is purely **weight**: Kleinpaket 0.2–1.0 kg, Paket DE 1.0–5.2 kg — a clean ~1 kg cutoff. The report mislabeled it because routing bands are built on `floor(kg)`; 32 Kleinpaket parcels at exactly 1.0 kg floor into band kg=1, colliding with Paket-DE's 1.0–1.99 kg parcels → the disjointness test failed → volume-share fallback.
3. **Fix, three iterations** (bi-analytics `4c2a43f` → `0286732` → `22ace7d`):
   - `4c2a43f`: tolerate a one-band floor overlap as a clean cutoff (label only). Niklavs corrected the approach — the cut belongs in the **Weight column**, as separate rows.
   - `0286732`: row-builder split — a carrier segment whose products form a clean cutoff expands to one row per band; `svc_cell`→`service_groups` classifier (`single`/`cutoff`/`overlap`); dropped slivers folded into the dominant so the parcels column reconciles.
   - `22ace7d`: detect cutoffs on **real per-parcel weights** (wmin/wmax joined from the assignment parquet), not the integer bands — resolves sub-kg splits (SE Warenpost Std 0.27–0.56 vs Premium 0.61–0.99, both in band kg=0, separate at ~0.6 kg). Two-pass: pass 1 keeps all weight-distinct tiers (a low-count but distinct tier like SE's >1 kg Paket-Intl is a real rule, not a sliver); pass 2 drops slivers then volume shares. Rows grouped per packagetype, weight-ordered.
4. **Verified end state:** service column carries exactly **one** service on all 1,045 rows (was 1 multi-service). DE → 2 rows (≤1 kg Kleinpaket / 1 kg+ Paket DE). Parcels reconcile to 523,685. Report regenerated.

## Decisions

- Cutoff detection on **real weights**, not `floor(kg)` bands — the integer grain can't express sub-kg product boundaries (the root cause of the mislabel).
- **Don't drop low-count tiers when they form a clean weight cutoff** — a 2-parcel weight-distinct band is an accurate dispatch rule; suppressing it would mislabel those parcels. Tradeoff (flagged to Niklavs): tiny rows surface; row count 1,007→1,045. A floor can be re-added if he prefers suppression — *not* committed to.
- Display only — routing and cost are byte-identical across all three commits.

## Pending external actions

None pending. Deliverable shipped + committed (bi-analytics `22ace7d`); `.html` is an untracked generated artifact, regenerate via `python routing/no_hermes/routing_report_ops_no_hermes.py`.

## Cascade

None — self-contained renderer change in `bi-analytics-main/NFE/.../routing/no_hermes/routing_report_ops_no_hermes.py`. No sibling `svc_cell` consumers (grep-confirmed: only this file).

## Main-brain changes

This quest-log entry + the Q5 correction self-observation (`examine/drafts/2026-06-17-explain-derived-output-from-source-not-code.md`). No `confirmed/` or `keepsake` writes.

## Next concrete step

None — quest closed. (Parent ops-coherence thread [[S245_3172630e_eu-tender-no-hermes-routing-ops-coherence|S245]] keeps its own parked items: Q15 smoothing floor, Q16 dim-DQ, Güll density gate.)
