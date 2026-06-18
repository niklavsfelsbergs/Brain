# S260 — overmax 62k-vs-19k reconciliation + shipping-agent spawn-policy false-trigger fix

**Session:** 88c8d323 · 2026-06-18 · Jebrim
**Anchor:** continues this-day workbench (May 2026 TCG shipping-quota outliers, where I produced the €61.7K UPS over-max cluster figure) + the [[S253_5974b4ee_g1_alching|S253]] (5974b4ee) shipping-agent run-yourself policy.

## Ask 1 — reconcile the manager's "62k overmax surcharge May" vs Invoice Details "19k"

Verdict: not a bug — a **label** conflation, two measures of the *same* 47 parcels.

- **€62K** (what the shipping agent told the manager) = **total landed cost** of the 47 UPS over-max parcels (base + fuel + every surcharge), ~€1,313/parcel. NOT the surcharge.
- **€19K** = the over-max surcharge **line item** at an early-June invoice snapshot. Fully invoiced now it's **€22.3K** (the canonical UPS "Demand Surcharge - Over Maximum").

Charge-bucket decomposition (invoiced-only, 47 parcels, €61,732 total; verified via shipping-agent sub-pull over gold mart, bucket invariant ties to the cent):

| Bucket | EUR | /parcel |
|---|---:|---:|
| Oversize/handling (all) | 50,567 | 1,076 |
| — Over-Max Demand Surcharge | 22,325 | 475 |
| — Over-Max Size+Length (dim) | 23,458 | 499 |
| — Large Package | 4,785 | 102 |
| Fuel | 10,002 | 213 |
| Base freight | 1,069 | 23 |
| Other/residential | 56 | 1 |
| **Total landed cost** | **61,732** | **1,313** |

The €19K→€22.3K gap = invoice lag (32 of 47 over-max lines invoiced in May, 15 more in June). "Over-max surcharge" is itself ambiguous: Demand-only €22.3K / full dimensional family (Demand+Size+Length) €45.8K / whole oversize bucket €50.6K. The €19K source almost certainly meant Demand-only at a stale snapshot.

Process miss flagged by principal: I **reflex-spawned the shipping-agent** for this — a one-`GROUP BY` reconciliation — when the [[S253_5974b4ee_g1_alching|S253]] default is run-it-myself. Triggered by the spawn-list naming "charge-bucket decomposition" as a topic.

### Resolution — the €62K vs €56.5K vs €19K, fully reconciled

Principal pushed hard ("47 parcels can't cost 62k if only 19k is over max — something's wrong"). Traced to source through several wrong turns; final triangulated picture:

- **€61,731.94 = total cost of 47 over-max (OVR/OML) UPS parcels, anchored on `shop_order_created_date` (order-month May)** — reproduced to the cent on `shipping_mart.fact_shipments` (real = final cost). This **is** the agent's original number. The agent was correct.
- **€56,444.95 = the SAME cohort anchored on UPS `transactiondate` (ship date) — 43 parcels.** 4 May-ordered parcels shipped/billed outside May drop out. Gold and the raw `enterprise_silver.ups_invoices` agree to €36 (0.06%) on this subset.
- **~€19–21K = the over-max *surcharge line*** (SOV peak-demand €20.4K gross / €19.5K net, or OVR size €17.0K), by invoice date — the manager's Invoice Details report.

The original "something's wrong" = three lens/scope mismatches stacked: total parcel cost vs one surcharge line; order-month vs invoice/transaction date; and "over max" being one of several stacked UPS surcharges (LPS/SOV/OVR/OML/AHC — codes per [[S243_f6d41a0d_ups-lps-oml-2026-surcharge-export|S243]]). No mis-billing; the apparent "2 lines per parcel" on dimensional surcharges = real €499 line + harmless €0.00 companion. Signal that fell out: May over-max parcels cost €1,313 each vs April's €708 — the SOV peak demand surcharge hits May, not April.

**The "where it went wrong" answer for the manager:** the €62K was mislabeled "over-max *surcharges*" — it's the *total cost* of the over-max parcels; the actual over-max surcharge is ~€21K.

### My errors this thread (lessons)

1. **Declared the €62K "unreproducible / an artifact" after testing only ONE date lens (transaction date).** Premature absence-assertion. The order-month lens reproduced it exactly — principal had to suggest it. Lesson: when a derived figure won't reproduce, **vary the date anchor (order-month / ship / invoice) FIRST** before declaring it unreproducible. Sibling of never-assert-absence + name-the-lens. → candidate examine draft.
2. **Anchored the cohort on `Nachfragezuschlag-Über Max.` (SOV = peak demand surcharge), not the true over-max codes (OVR/OML)** — carried the sub-agent's "Demand Surcharge - Over Maximum" headline as the definition. Principal caught it. Lesson: define a population off the stable charge *code* taxonomy, not a relayed label.
3. Inverse of the usual "verify sub-agent findings": here I wrongly *doubted* a correct sub-agent number. Verify both directions — a figure you can't reproduce may be your reproduction that's wrong, not the original.

## Ask 2 — fix so it doesn't recur (principal-cued)

Root cause: the spawn-list named a **topic** ("charge-bucket-first decomposition") that pattern-matches any cost question, overriding the calibration clause under it.

Fix applied to the 2 rule homes that carry the spawn-list prose:
- `players/jebrim/spellbook/skills/calling-the-shipping-agent.md` — re-scoped the methodology bullet from a topic to a **shape** (multi-carrier/-period *sweeps*, compounding basis-risk) + added an explicit **litmus** ("one query after loading the contract → run it yourself; topic ≠ trigger, shape is").
- `players/jebrim/CLAUDE.md` — same litmus, terser, in the spawn bullet.

Not touched: `cue_registry.py` + `bank/domains/shipping-mart.md` (the other 2 [[S253_5974b4ee_g1_alching|S253]] homes) — they don't carry the methodology-bullet prose; nothing to re-scope there.

## State
- Brain change UNCOMMITTED — awaiting commit go (pathspec-scoped to 88c8d323 footprint + comms; never push).
- Mart deliverable was chat-only (no external repo write).
- Candidate examine harvest: "a literal topic phrase in a spawn-list false-triggers; the calibration/shape clause must win" — could generalize to other skills' spawn-lists. Offered to principal.
