---
quest: S248_319db0c2_ups-retention-curve
sid8: 319db0c2
opened: 2026-06-16
status: in-progress (deliverable landed + committed; awaiting principal read)
---

# S248 — UPS volume-retention cost curve (EU tender, no-Hermes v2)

**Ask.** The no-Hermes v2 plan reroutes ~51% of UPS's volume to cheaper carriers.
What does it cost (in forgone annual saving) to keep more on UPS? Five then ten
tiers; "where does the volume come back from."

## What happened (turn arc)

1. **Turn 1 (5 scenarios, Q1, current contract).** Confirmed the frame
   (clawback % of away-volume, cheapest-to-retain first — both via multiple-choice).
   Built `routing/no_hermes/ups_retention_curve.py` (Q1 parcel-grain, two lenses:
   current GRI'd contract + min(keep,offer)). Validated vs build_final flow savings
   (within 4.9%). Finding: cost back-loaded; cheapest ~60% near-free.
2. **Turn 2 (re-based, the real deliverable).** Principal: new folder, **annual**,
   **new UPS offer** basis, reconcile to the v2 card (707,867→347,183/yr, €2.64M),
   **10% increments** + source-carrier mix. Framed concretely + confirmed deliverable
   form (HTML one-pager) and lens (offer only) via multiple-choice.
   - Built on the **same per-parcel frame as the v2 card**: `annual_2026.q1_base.build_pp`
     with FINAL_6:=FINAL_5 + DBS-origin freight pin + per-dest annualization `k`.
     Away-set reconciles to `stats_no_hermes.json` flows **to the parcel** (373,395/yr;
     Maersk 161,599 / DPD-PL 139,856 / DHL Paket 71,904 / DBS 37).
   - **Basis correction mid-build:** offer-only priced the away-set *higher* than the
     current contract (€945k vs €575k/yr) — the 2026 offer is **worse on the lanes UPS
     is losing**. Switched to the v2 convention = **better-of {offer, current contract}**
     per parcel (UPS is KEPT, not replaced) → €493k/yr at 100%.
3. **Turn 3 (interpretation).** Confirmed: retain 50% forgoes €61,738/yr → headline
   €976,024 → **€914,286/yr**. Bookend: full UPS reroute = €493k of the €976k headline.

## Numbers (better-of basis, annual)

| Retain away-vol | Forgone saving/yr | UPS book/yr |
|---|---|---|
| 10% | −€434 (free) | 384,520 |
| 50% | €61,738 | 533,876 |
| 100% | €493,488 | 720,578 |

Marginal rises every step: ~free → **€194,345/yr for the last 10%** (the DHL-Paket
light-EU tail). Cheapest to reclaim = DPD-PL; dearest = DHL Paket.

## Artifacts (bi-analytics `6c30000`)

- `2_analysis/ups_retention/build_retention_curve.py` → `retention_curve.json`
- `2_analysis/ups_retention/build_report.py` → `ups_retention.html` (the deliverable)
- `2_analysis/routing/no_hermes/ups_retention_curve.py` (turn-1 Q1 curve)

## Leaving open

- Principal will **read the HTML later**; may want edits (cell-grain operational
  version, screenshot, or a 5-tier cut). None requested yet.
- Possible bank-note harvest (the "offer isn't the lever on the away-lanes" finding)
  — defer to alching per harvest-after-stable rule.

**Cascade.** None (analysis only; no shared-engine code touched — both scripts are
read-only consumers of build_pp / the cost matrix).
**Main-brain changes.** None.

Resume: `inventory/ups-retention-curve-resume__319db0c2.md`.

---

## [[S263_fd7bcba7_ups-retention-cell-grain|S263]] continuation (fd7bcba7, 2026-06-18) — cell-grain operational version BUILT

Principal picked the parked "cell-grain operational" next-step. Full record →
`quest-log/in-progress/S263_fd7bcba7_ups-retention-cell-grain.md`. In one line: 96% of the
away pool retainable at ≈ the floor (€463k/yr, UPS-dominated cells); the last <1% is
sliver-trapped (€1.94M to flip) → operationally unretainable. NFE committed `1e52a7a`.
