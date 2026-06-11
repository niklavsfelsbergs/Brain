# [[S209_89e4a123_carrier-overview-v2-rederive|S209]] D1 — dhl_paket carrier_overview_v2 hand reconcile

Dwarf for Jebrim. Rewrite sections/dhl_paket.md to reconcile prose to the freshly regenerated card (UPS entered as 10th offer, engine drift 2.0.0→2.2.0 + fuel refresh). NARRATE-NOT-REDERIVE.

## Turns
- Read card (ground truth), current section, PLAN §4/§5. Card-vs-prose deltas identified:
  - DE Std ≤1 kg: €3.11 (was €2.92) — beats today UPS €3.47.
  - ROW Std ≤1 kg: card €13.35, ✓ beats today (UPS €16.11) — VERDICT FLIP: old prose had €17.50 HOLLOW (+9%); now a REAL win.
  - ROW Std 2–5 kg: €25.53 ✓ beats today (UPS €27.81) — unchanged verdict, number same.
  - ROW Bulky 2–5 kg: €46.00 HOLLOW (+62% UPS €28.32) — same.
  - ROW Bulky 5–10 kg: €63.85 HOLLOW (+80% UPS €35.47) — same.
  - DE Std 1–2 kg: €3.35 (same).
  - DE Std 2–5 kg: €3.42 (same).
  - Competitive (within-10% near-miss): card lists 1 — CH Std ≤1 kg €7.62 (+7.7% vs guell), ✓ beats today UPS €9.52. Old prose listed 2 (Benelux 1–2, FR ≤1) — now gone (DPD took them). CH is NEW on the competitive line.
  - Native envelope: toll_co2 78.2% (old prose 84.1%), peak 33.5%, truck 21.8% (NEW cliff in card), bulky_de 12.8% (same), peak_in_peak 10.1%, bulky_intl 7.4% (same).
  - 7 wins total (same count). Headline brief said "4 ROW segments win" — card confirms ROW ≤1, ROW 2–5 Std, ROW Bulky 2–5, ROW Bulky 5–10 = 4 ROW + 3 DE = 7. ✓
- Rewrote sections/dhl_paket.md in place. Same structure/voice. All €/%/counts narrated from card.
  - Cost-structure section: preserved all engine constants, surcharge €-values, service specs, file-mechanics. Updated the native-envelope LINES (toll_co2 84.1%→78.2%, bulky_de 12.8% confirmed, bulky_intl 7.4% confirmed, peak 33.5%, peak_in_peak 10.1%) to the card's coverage %, since the old "fired on N parcels" framing contradicted the card's % framing and the card is authoritative on coverage. Engine €-values untouched.
  - Resolved contradiction: ROW Std ≤1 kg flipped HOLLOW→REAL win (card €13.35 beats today UPS €16.11; old prose had stale €17.50 +9% hollow). Reframed analyst-take + where-it-wins accordingly.
  - Resolved: competitive near-miss list 2→1 (FR/Benelux gone to DPD; CH Std ≤1 kg new on card, beats today).
- DONE.
