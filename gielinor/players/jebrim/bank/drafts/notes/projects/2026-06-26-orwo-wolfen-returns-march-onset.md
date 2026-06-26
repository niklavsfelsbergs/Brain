# ORWO/Wolfen returns — March-2026 program onset + attribution wall

Durable findings from [[S372_0888690d_orwo-wolfen-returns|S372]] (2026-06-26). Anchor: NFE `shipping_topics/51_orwo_wolfen_returns/` (findings.md + the real May export). Cross-link [[shipping-mart]], [[carrier-contracts]], the ORWO tender arc [[2026-06-19-orwo-tender-wolfen-spine-and-reprice-engine]].

## Returns are NOT in the gold mart — read raw silver invoices
The gold `shipping_mart` has no returns section: UPS RTS is **redistributed onto the original outbound parcel** and >90d-old RTS dropped; `is_returned` unconfirmed. So return cost = raw `enterprise_silver.{ups_orwo_invoices, dhl_orwo_invoices}`. **Return signal:** UPS `chargecategorycode='RTN'` (detail `RS`=Rückholservice prepaid return-pickup = the driver; `RTS`=failed-delivery); DHL `prod` joined to `shipping_charge_bucket_mapping` (carrier_name='dhl', `charge_bucket='other'`, desc ~ retoure/rücksend/return).

## The finding: a return PROGRAM switched on ~March 2026 (both carriers)
Return **rate** (returns ÷ outbound parcels) jumped ~0.2% → **6.5/8.5/11.5/9.2%** Mar–Jun on DHL, and 0.02%→~10-12% on UPS, **same months**, while outbound volume fell. New prepaid return products appear from €0 in March (DHL "RETOURE (GK) up to 31,5 kg" + "RETOURE Online"; UPS "Rückholservice"); pickups concurrent with invoicing (not a backlog). Two independent carriers, same month ⇒ deliberate **ORWO-side return-program launch**, not volume / quality / billing-lag. Failed-delivery RTS stayed flat & tiny. **Combined ~€105k Mar–Jun (DHL ~€86k + UPS ~€19k) → ~€300–350k/yr.**

## Attribution wall — customer/product NOT recoverable from shipping data
White-label pooling: ORWO bills every brand's returns under its OWN UPS/DHL accounts, and the return is a fresh parcel that doesn't reference the outbound order. Proven 4 ways: return tracking→outbound order ≈2% match; DHL `shippers_reference` 96% masked `(Y)` even in **bronze**; UPS `sendercompanyname` uniformly "ORWO PHOTOLAB GMBH", single account 0R6D51, 305 scattered consumer postcodes (top 06766=Wolfen). Vertical lives only on the outbound order (mart `source_system` / PTS `orwo_pts_parcelfinish.senderkeyaccountid` → `orwo_shop_mapping.mandant`). Best proxy = outbound DE brand mix (**Rossmann ≈ half**), labelled inference (assumes uniform return rate). The real answer needs ORWO ops / their order system.

## Scope trap (re-confirmed)
`shipping_ups_returns_addition` (€245k) = the **Picanova PCS-PL** UPS book, NOT Wolfen (verify by account: ORWO=0R6D51). Don't use it for ORWO returns. [[feedback_verify_entity_scoping_key_not_named_field]].
