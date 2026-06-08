# UPS — Current-Invoice Charge Profile (Ground Truth)

**Question.** For the EU-tender UPS contract assessment (Picanova, Germany): what does UPS *actually* bill us today, line by line? Goal — catch charge types not in our cost model (unknown-unknowns) and empirically check the fuel surcharge, before finalizing a question round to UPS.

**Date of analysis.** 2026-06-08. **Source:** live gold `shipping_mart` (`fact_shipment_invoice_lines`, validated against `fact_shipments` spine). Read-only.

**Cost basis.** Invoiced cost only (every figure is real carrier invoice lines, `charge_amount_eur`). Tax + customs/duty buckets are excluded from all freight figures and shares (they are not freight). Oversize is reported on a **net** basis (applied minus UPS's refund-in-place reversals) with the gross/reversed split shown where it matters.

---

## Headline

Over the last 12 months UPS billed us **~€5.03M in freight** across the regular UPS invoice stream (726,748 distinct shipments, ~2.72M charge lines). The structure:

- **Base transport rate — ~72%** (€3.64M). The service products: TB Standard, Domestic Standard, WorldEase Worldwide Standard/Express Saver, Economy DDP.
- **Fuel surcharge — ~13%** (€669K). **Effective fuel runs ~18-21% of base, NOT ~35%.** The contract's flat 35% is well above what we're actually billed at the blended carrier level (see Effective fuel %).
- **Oversize/handling — ~9% net** (€452K net; **€981K applied, €528K reversed** — UPS claws back ~54% via refund-in-place).
- **Residential — ~4%** (€201K).
- **Other / unclassified / peak / remote — ~1.4% combined** (€69K). This is where the unknown-unknowns live.

**Reconciliation verdict.** The base + fuel + residential + oversize core (~95% of spend) IS explained by the cost model. **~€235K/12mo (~4.7% of freight) is billed by charge types the model does NOT contain** — chiefly peak/demand surcharges (which stack on base, residential, AND oversize), plus a tail of fee types (Address/Shipping Correction, Presentation Fee, Paper Commercial Invoice Surcharge, Access Point Hold, Saturday Delivery, Remote Area) and a genuinely-undescribed "unclassified" residue. These are the additions for the UPS question round (detail below).

---

## Scope & filters

- **UPS identifier.** Carrier keyed as `shipping_provider_group = 'UPS'` (uppercase) on the spine — 2,384,136 shipments all-time. On the invoice-lines table UPS appears as two `invoice_source` values: **`ups`** (the regular stream) and **`ups_orwo`** (Wolfen photo-lab bulk-bill allocation, a separate vertical). **The headline uses `ups`**; `ups_orwo` is reported separately below.
- **Spine validation.** A bounded month-join (May 2026) confirms `invoice_source = 'ups'` lines map **100%** to `shipping_provider_group = 'UPS'` shipments. The anchor is sound. (The full 12-month spine join aborts on scan size; the invoice-source filter on the lines table is the equivalent, validated anchor.)
- **Vertical mix of the `ups` stream** (Mar-May 2026 sample): ~96% TCG (Picturator B2C + PicaAPI/MerchOne), ~2.4% ORWO that bills through the regular stream, trace PCS. So the `ups` stream is essentially our **TCG-shop UPS volume** — the right population for the tender.
- **Window.** `invoice_date` from **2025-06-08 to 2026-06-07** (last 12 months; max invoice_date in mart = 2026-06-07). Date column used: `invoice_date` on the invoice lines. This captures a full peak season (Sep 2025-Jan 2026).
- **Counts (`ups`, in window):** 2,717,552 charge lines; 726,748 distinct shipments; 756 distinct invoices; €5,032,182 net freight (tax/customs excluded); €53,798 in excluded tax+customs buckets.
- **Query shape.** `SELECT charge_bucket [, charge_description_english], COUNT(*), SUM(charge_amount_eur) FROM shipping_mart.fact_shipment_invoice_lines WHERE invoice_date BETWEEN '2025-06-08' AND '2026-06-07' AND invoice_source = 'ups' GROUP BY ...`. Fuel% via conditional sums of fuel vs base buckets by `DATE_TRUNC('month', invoice_date)`.

---

## Charge-bucket table (the vocabulary, EUR-weighted)

`ups` stream, 12 months, net EUR. Shares are of the €5,032,182 freight total (tax/customs excluded).

| Charge bucket | Lines | Sum EUR (net) | % of freight | Avg / line | Notes |
|---|---:|---:|---:|---:|---|
| Base transport rate | 1,141,551 | 3,641,133 | 72.4% | 3.19 | Service products + a -103,720 "Transportation Charge" reversal |
| Fuel surcharge | 728,373 | 669,085 | 13.3% | 0.92 | -100K of reversals inside |
| Oversize / handling | 50,819 | 452,159 | 9.0% | 8.90 | **Net.** 981K applied - 528K reversed |
| Residential | 554,347 | 200,540 | 4.0% | 0.36 | Incl. peak "Surge Fee - Residential" 49K |
| Other | 19,267 | 34,187 | 0.7% | 1.77 | Fee tail — see reconciliation |
| Unclassified | 157,183 | 24,501 | 0.5% | 0.16 | 157,179 lines have NO description |
| Peak / demand | 7,004 | 7,955 | 0.16% | 1.14 | Surge/Demand - Commercial |
| Remote area | 52,480 | 2,620 | 0.05% | 0.05 | Remote Area Surcharge - Delivery |
| *(Customs/duty — excluded)* | 6,461 | 52,986 | — | 8.20 | Not freight |
| *(Tax — excluded)* | 67 | 811 | — | 12.11 | Not freight |

**Base-rate sub-detail** (service split): TB Standard 1.66M, Domestic Standard 1.06M, WorldEase Worldwide Standard 398K, WorldEase Express Saver 205K, **Economy DDP 133K**, Worldwide Standard 98K, plus "...Change" re-bill lines (106K). The -103.7K "Transportation Charge" line is a refund-in-place reversal landing in base_rate.

**Oversize sub-detail** (the LPS/OML monitoring surface): Large Package Surcharge 268K, **Demand Surcharge - Large Package 88K**, Over Maximum Size 43K, **Demand Surcharge - Over Maximum 38K**, Additional Handling 1.8K (26K lines, near-zero each), Demand Surcharge - Additional Handling 0.4K, WorldEase oversize variants ~17K, plus reversals (Over Maximum Length -5.1K). Per known-DQ: UPS claws these back in batches; monitor net, and verify the dim (`length_plus_girth_cm`) before treating any "Over Maximum" charge as legitimate — prior S124 work found these landing on sub-threshold parcels (dispute basis).

---

## Effective fuel % (the empirical check)

Fuel ÷ base, `ups` stream, by invoice month:

| Month | Fuel EUR | Base EUR | Fuel % of base |
|---|---:|---:|---:|
| 2025-06 | 29,384 | 161,618 | 18.2% |
| 2025-07 | 49,115 | 235,853 | 20.8% |
| 2025-08 | 46,965 | 247,531 | 19.0% |
| 2025-09 | 47,185 | 264,390 | 17.9% |
| 2025-10 | 56,342 | 263,796 | 21.4% |
| 2025-11 | 45,579 | 272,746 | 16.7% |
| 2025-12 | 125,947 | 740,021 | 17.0% |
| 2026-01 | 53,772 | 314,800 | 17.1% |
| 2026-02 | 35,684 | 326,974 | 10.9% |
| 2026-03 | 46,127 | 251,634 | 18.3% |
| 2026-04 | 66,727 | 257,914 | 25.9% |
| 2026-05 | 53,142 | 254,149 | 20.9% |
| 2026-06 (partial) | 13,117 | 49,707 | 26.4% |

**Full-window: ~18.4% net / ~20.5% gross** (fuel gross 769K ÷ base gross 3.75M). It moves month-to-month (10.9%-26.4%), consistent with UPS's weekly fuel *index* rather than a flat rate — so the contract's quoted flat 35% is doubly wrong: wrong level (we're billed ~20%) and wrong shape (it's an index, not flat).

**Caveat on the comparison (this is a measurement; the cause is a guess).** The ~20% measured here is fuel-bucket ÷ base-rate-bucket at the carrier-blended level. The published ~35% is fuel-as-%-of-transportation-charge on a *specific lane/service*. The gap could mean (a) our negotiated effective fuel genuinely runs ~20% over this lane mix, or (b) our `base_rate` bucket denominator is wider than UPS's fuel base (it includes WorldEase/DDP service base and re-bill "Change" lines that may not all attract fuel), inflating the denominator. **The reconciliation point for the question round: ask UPS to confirm the fuel-surcharge base and the index, because what we pay (~20% of base) is materially below the 35% the offer quotes** — if 35% is real and applies to a narrower base, our cost model under-prices fuel; if our ~20% is the true effective, the 35% in the offer is a worst-case the contract should cap.

---

## Surcharge presence & share (explicit checklist)

| Surcharge type | Present on UPS invoices? | 12-mo Sum EUR | Materiality |
|---|---|---:|---|
| Residential | Yes — heavy | 151K (excl. peak-residential) | Core. Residential Delivery 139K + WorldEase residential 12K |
| Peak / demand | **Yes — across 3 buckets** | **~191K** | Surge/Demand-Commercial 8K + Surge-Residential 49K + Demand-on-oversize 134K |
| Free-Domicile / DDP | Yes (Economy DDP) | 133K | In base_rate; a service product, not a separate surcharge line |
| Duties / brokerage / customs | Yes | 53K | **Excluded from freight.** WWE Import Customs, Customs Duty, Brokerage, Int'l Processing |
| Address correction | Yes | ~10.5K | Address Correction + Shipping Correction Fee (in `other`) |
| Large package | Yes | 268K (+ 88K demand) | Net of reversals; gross higher |
| Over-maximum | Yes | 43K (+ 38K demand) | Net; verify dim before treating as fair |
| Additional handling | Yes | 1.8K | 26K lines, near-zero each |
| Print / GBS | **Not seen as a distinct line** | — | No "GBS"/print-billing charge in the UPS stream |
| Unclassified / other | Yes | 58.7K | 24.5K unclassified (no description) + 34.2K other |
| Remote area | Yes | 2.6K | Remote Area Surcharge - Delivery |

---

## Reconciliation — charges NOT explained by our cost model

The model = billable-weight base rate (zone×weight) + fuel + residential (0.40) + Free-Domicile/DDP (5.35) + seasonal Base-Rate-Surcharge (0.20) + Large-Package/Over-Max/AddlHandling + line-haul.

**Explained (~95.3% of freight, ~4.80M):** base_rate (incl. DDP), fuel, residential (flat), oversize (LPS/OML/AddlHandling). These map cleanly to the model.

**NOT explained — the unknown-unknowns for the question round (~235K / ~4.7% of freight):**

1. **Peak / demand surcharges — ~191K, the biggest gap.** The model has no demand component, but UPS bills demand/surge in *three* places:
   - Demand Surcharge stacked on oversize: Large Package 88K, Over Maximum 38K, Additional Handling 0.4K, WorldEase variants ~7K (~134K total) — sits inside the oversize bucket, easy to miss.
   - Surge Fee - Residential 46K + WorldEase Surge-Residential 3K (~49K) — peak residential, on top of the flat 0.40 residential the model has.
   - Surge/Demand - Commercial 8K — the standalone peak bucket.
   **Action:** the model's flat residential and flat oversize miss the seasonal demand multiplier entirely. Ask UPS for the peak/demand schedule (rates + active weeks) — this is the single largest modelling gap.

2. **`other` fee tail — 34K.** None of these are in the model:
   - Address Correction 8.0K + Address Correction (service variants) ~2.5K
   - Shipping Correction Fee 7.1K
   - **Presentation Fee 6.8K** (UPS DDP/brokerage presentation)
   - **Paper Commercial Invoice Surcharge 5.5K** (paper-docs penalty — avoidable with electronic docs)
   - UPS Access Point Hold Service 0.9K, Saturday Delivery 0.1K, Monopoly Fee, Import Preparation, Missing Package Information Fee, etc.
   **Action:** confirm which are avoidable (paper-invoice, missing-info, address-correction are process-fixable) vs contractual.

3. **Unclassified — 24.5K (157,179 lines, no description).** UPS sends these lines with no charge-description text, so we genuinely cannot say what they are. Small but a true unknown. **Action:** ask UPS to itemize what the undescribed lines on our invoices are.

4. **Remote Area Surcharge - Delivery — 2.6K.** Not in the model. Small; note it.

5. **Seasonal Base-Rate-Surcharge (0.20) — not located as a distinct line.** The model lists it but I found no matching standalone description; it may be folded into base_rate "Change"/re-bill lines or simply absent on our lanes. **Action:** confirm with UPS whether it applies.

**Bottom line for the offer:** the rate card covering only a negotiated subset and stating "exclusive of any additional charges" maps to a real ~235K/yr of charge types beyond base+fuel+residential+oversize. The peak/demand family (~191K) is the material one and is invisible if you only look at the headline buckets — it hides inside oversize and residential. Get the demand schedule, the fuel base/index, and the undescribed-line itemization into the question round.

---

## ups_orwo (Wolfen photo lab — separate, reported for completeness)

Bulk-bill allocation, 415,171 lines in window. Buckets: base 328K / **tax 47K (excluded — DHL-style VAT line items)** / fuel 46.5K / other 18.6K / residential 6.8K / customs 5.3K (excl) / peak 0.4K / unclassified 0.2K / oversize 0.1K / remote 0.03K. Effective fuel ~14% of base. **Not part of the TCG-tender headline** — different vertical, bulk-allocated, and carries VAT as line items (unlike the regular `ups` stream).

---

## Coverage / DQ caveats

- **Cost basis is invoiced-only by construction** — invoice lines ARE the invoiced subset. No estimated/uncosted blending here; this is what UPS actually billed. (The mart-wide `cost_source` split — ~68% invoice / ~27% expected / ~5% uncosted — applies to the shipments fact, not to this line-level profile.)
- **Net vs gross on oversize and fuel.** UPS reverses charges *in-place* (negative line keeps its original bucket). Oversize especially: 981K applied, 528K reversed (~54%). All bucket totals above are net (what we keep paying). Reporting gross would overstate exposure ~2x on oversize. The fuel and base buckets also carry reversals (-100K fuel, -114K base incl. the -103.7K Transportation Charge line).
- **Tax + customs excluded from every freight figure and share.** The regular `ups` stream carries 53.8K of these; the UPS "Manual Bill" sub-stream (invoice numbers starting `838`, 10,213 lines in window) is customs/duty/VAT recharge, correctly routed into the excluded buckets — not freight.
- **Unclassified is a description gap, not missing money** — 24.5K of lines UPS sends without description text. The mapping can't bucket them; surfaced as `unclassified` (~0.5% of spend). Real charges, unknown type.
- **`ups` vs `ups_orwo` split.** ~2.4% of the regular `ups` stream is ORWO volume that bills through the regular invoice (not `ups_orwo`). The headline includes it (it's <3% and TCG-dominant otherwise); a strict TCG-only cut would shave it but wouldn't move the structure.
- **Live-query caveat.** Every figure is from a live `shipping_mart` query on 2026-06-08; the current month (2026-06) is partial (invoice lag) — the 2026-06 fuel% row rests on ~3.5 weeks of invoices. Invoiced cost backfills as bills arrive, so the most recent 1-2 months will firm up.
- **Full 12-mo spine join not run** (scan-size abort); spine identity validated on a bounded month sample instead. The invoice-source anchor is the equivalent and is the right grain for per-charge-line work regardless.

---

## Cross-links

- **UPS assessment:** `bi-analytics-main/NFE/1_offers/picanova/UPS/CLAUDE.md` — feed the reconciliation (the ~235K of un-modelled charge types) into the UPS question round.
- **Published surcharge book:** `brain/gielinor/players/jebrim/research/2026-06-08-ups-germany-2026-published-surcharges.md` — compare the demand/peak schedule and fuel mechanism there against the ~20% effective fuel and the ~191K peak/demand actuals measured here.
