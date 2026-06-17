# S250 · UPS routing investigation (per-country) — Jebrim

**Session:** bd2469b9 · 2026-06-17 · player: Jebrim
**Quest:** EU-tender follow-up → reframe UPS-negotiation work into a per-country routing-validation investigation; deliverables in `bi-analytics-main`.

## What this was
Opened as "EU tender, no-Hermes, final portfolio — UPS gives up ~half its volume; find where it goes / what it costs to keep UPS." Evolved over the session into a structured **per-country routing investigation** of the no-Hermes plan, aimed at an ops-ready routing table at dest×packagetype×weight grain.

## Turn-by-turn (condensed)
- **Where does UPS volume go.** Pulled the no-Hermes `migration` flows: of UPS's 149,041 Q1 parcels (~€1.13M net), ~54% leave — Maersk 39.5k, DPD-PL 28.9k, DHL 11.3k, DBS 0.2k; keeps 69.1k. Richest per-parcel saving is the DHL slice (€2.65/pc); DPD-PL near-parity (€0.59/pc).
- **Q1 vs annual reconciliation.** The "80k" was *parcels* leaving (Q1), annualizes ~×4.82; the "300k" he half-remembered = 347,183 parcels/yr UPS *retains* in the v2 card. Cleared the parcels-vs-euros / Q1-vs-annual equivocation.
- **Cohort deep-dives (UPS→DHL).** CH (83%) + AU (13%). CH: UPS *bids* (offer Standard) and loses light parcels to DHL on price; keeps heavy/bulky. AU: UPS *can't bid* (offer EU-only, no WW-Economy); held at current contract; 49% still switches. **Correction:** the remembered "WW-ECO/AU stays on UPS" rule is wrong — investigated, not trusted.
- **Restructure discussion.** Agreed: country is the primary axis (not carrier-pair); all carriers per country; validate-and-refine the existing `routing_rules.csv` grid (it already IS the ops table), don't rebuild; cell = dest×packagetype×weight; fat/thin partition at floor 50 (~98% of volume in ~466 fat cells); thin tail stays visible at carrier level; margin backbone (D7) to find runner-ups + swing candidates.
- **CH pilot built** → `routing_investigation/CH.md` (migration flow, 4-tier fat-cell grid, carrier max-envelope table, thin tail, mechanics, questions log).
- **Carrier limits.** Read each engine's eligibility caps; added the per-country max-envelope table. L+girth is the binding constraint in CH.

## Decisions / findings
- **UPS keep-cost = actual invoice × 1.05 GRI, NOT the UPS engine price** (engine over-prices UPS ~50%). This validated the "UPS keeps the heavy tail" cells (engine-cheapest ≠ routing-choice was correct). Any margin work must use the invoice basis. → the reason the D7 backbone must *instrument* `build_final.py`, not reimplement.
- Stale-artifact catch: the flat `data/cost_matrix.parquet` is the May-28 2025 track; the live matrix is partitioned `data/cost_matrix_2026q1/`. Joining the stale one drops Warenpost + under-matches.
- Warenpost envelope, the 43 Premium, the carrier caps — all in CH.md.
- Saved a harness-memory feedback: markdown tables must always be column-aligned (`feedback_md_tables_always_formatted`).

## Pending external actions
None pending.

## Cascade
None (no brain rules/hooks changed; all work in the bi-analytics repo + harness memory).

## Main-brain changes
None to gielinor rules. Added: a Jebrim harness-memory feedback entry (md-table formatting). Deliverables live in `bi-analytics-main` (uncommitted, separate repo).

Resume + locked decisions + next step: `inventory/ups-routing-investigation-resume__bd2469b9.md`.
