# S099 p2 — Maersk ROW lane / FedEx Poland public surcharges (penguin run-log)

**Role:** penguin (research operative), inheriting Jebrim.
**Brief:** EU Tender 2026 — Maersk ROW lane runs as FedEx Economy via FedEx Poland; surcharge definitions/percentages follow FedEx PL's *public* schedule (Maersk base rates apply). Find public FedEx PL values for fuel, peak/demand, non-standard parcel definition, extended/remote area. Replay window Q1 2026.
**Deliverable:** `gielinor/players/jebrim/research/2026-05-27-maersk-row-fedex-poland-surcharges.md`

## Turn-by-turn

- Read research.md methodology + brief; checked existing Jebrim research/ (no prior FedEx/Maersk file).
- Broad scout: 2 searches (PL + EN fuel surcharge). Source map built — FedEx PL surcharges page (PL/EN), EU fuel PDF, EU demand PDF, PL VASS PDF, TNT Poland, Polish aggregators.
- **Blocker found:** every FedEx-domain WebFetch (HTML + DAM PDFs) returns an access-denied "System Down" error page to the fetcher — geo/bot gate. WebSearch's summarizer CAN read FedEx pages, so pivoted to search-summary + sister-domain (TNT) + trade-press + Polish aggregators that republish FedEx PL verbatim.
- Fuel: confirmed index (USGC jet fuel / EIA, 2-wk lag), cadence (monthly → weekly from 11 May 2026), and the published % range. Hard figures: Export 38.50% / Import 42.75% at $3.99–4.03/gal band eff. 11 May 2026; +2pt export / +2.5pt import structural step on 11 May 2026 (so Q1 2026 export ≈36.5% at $4/gal). Domestic FSC (not applicable) ~20–21.75%.
- **Headline finding:** ~49.50%-published / 24.75%-net does NOT match any FedEx-published *International* FSC table (which sits ~36.5–43%). Flagged 3 hypotheses + recommendation to push back to Maersk.
- Peak/demand: US/standard window 27 Oct 2025 – 18 Jan 2026 (matches Maersk). Relevant intra-Europe Economy demand surcharge = €0.10→€0.15/kg, 20 Oct–21 Dec 2025; steps to €0.15→€0.10/kg 22 Dec 2025–15 Feb 2026 (EU demand PDF). PL "opłata okresowa" is weight-based PLN (0.50–8.80 PLN/kg, min 4.40 PLN) per 2024 aggregator — indicative shape only.
- Non-standard parcel: definition fully captured verbatim (apaczka quotes FedEx PL criteria) — 70kg / 150cm longest / 70cm other edge / <180cm sum-of-two; plus shape/centre-of-gravity/non-cuboid/multi-part/non-machine-sortable triggers; AHS-Weight >25kg; vol weight ÷5000. Rates come from Maersk per brief, so amounts not needed.
- Extended/remote (ODA/OPA): existence + structure confirmed; PLN values blocked (VASS PDF). Low confidence on values.
- Wrote research file + this run-log. Did NOT write to bank (penguin boundary; picking happens at alching).

## Status: research complete. Deliverable written. Confidence medium (mechanism/structure/definitions solid; exact published fuel % and PLN amounts gapped behind FedEx's bot-gated pages — flagged for a human direct-open).

## Key gaps handed back
1. Exact Q1-2026 weekly fuel % — needs a human to open the FedEx EU fuel PDF / FedEx PL page directly (fetcher blocked).
2. 49.50% origin — put back to Maersk; doesn't reconcile with public International FSC.
3. Confirm ROW service = International Economy vs Regional Economy (different fuel index).
4. PLN amounts for handling/periodic/ODA-OPA live in blocked `fedex-rates-vassuis-pl-pl.pdf`.
