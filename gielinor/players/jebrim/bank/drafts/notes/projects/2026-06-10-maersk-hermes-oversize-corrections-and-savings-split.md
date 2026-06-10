# Maersk + Hermes oversize corrections + the DB Schenker savings split

> Draft (harvest, [[S189_e3de8457_maersk-hermes-oversize-corrections|S189]] 2026-06-10). Carrier replies on the EU-tender oversize open questions. Cross-ref [[2026-06-08-eu-tender-db-schenker-reroute-validation]] + [[eu_tender_2026]]. Promote at next Jebrim alch.

**The corrections (carrier replies 2026-06-10):**
- **Maersk `3.1.0`** — confirmed a hard handling ceiling the rate card never stated (closes the S164 "no upper bound" gap): **longest ≤ 175 cm (DE 200) AND girth ≤ 300 cm**, rejecting oversize **even where a per-country surcharge exists**. Before this, `oversize_no_surcharge` only rejected null-surcharge countries, so a surcharge-country parcel was accepted at any size.
- **Hermes `2.1.0`** — retracted the 450 L volume assumption; the real gate is **dimensional**: standard (longest ≤120) W/H≤60 & girth≤300; bulky (120–170) girth≤360. The per-destination bulky surcharges (€57.75 / NL €92.35 / PL €66.72 / …) were **already** in the engine since `2.0.0` — the email re-confirmed them, it didn't add them.

**Headline impact:** tender Q1 saving **€377k → €276,951 (9.4%)**. ~€100k of prior "saving" was oversized parcels Maersk/Hermes can't physically take, over-credited as cheap moves. DB Schenker reroute now moves 6,606 (was 7,593); freight grows 1,076→2,048, must-freight 165→299.

**The savings split (the load-bearing deliverable):** the routing report now splits saving by origin — **DB Schenker reroute = €168,585 (61%), LOW confidence** vs €108,366 (39%) firm. 87% of the total saving lands on the two unvalidatable oversize engines (Maersk-EU + Hermes). *Niklavs' instinct: the DB Schenker reroute is the soft slice — and it's the majority of the headline.* Mechanism: per-parcel today-vs-routed cost grouped by `cur_inc`/routed carrier in `build_final.py` (`saving_split` block).

**The Maersk girth-definition open question (decision-vital, ~€300k/yr swing):** Stefan said "girth 300 cm"; the reading is genuinely ambiguous —
- The Oversized Surcharge table uses precise headers **`L+W+H`** and **`L+2W+2H`** (length+girth) — it **never** says "girth"; Stefan introduced the loose word.
- Three live readings of "300": **pure girth 2(W+H)** [what we encoded], **L+W+H**, or **L+2W+2H**.
- L+2W+2H is **self-contradictory as a ceiling** (would reject Maersk's own DE standard 120×60×60 = l2w2h 360 parcel) — yet "length + length-girth" is the *standard* parcel-carrier limit format (UPS/FedEx/USPS), so it can't be dismissed on convention.
- Maersk fallout swings **845 → 2,819 (99%)** between pure-girth and L+girth. Confirm with Maersk (question drafted, pinned to his column names); proceed pure-girth meanwhile.

**Decisions:** GEL tubes stay on DB Schenker (outside Maersk's ceiling); pure-girth assumed pending Stefan; management deck deferred until girth confirmed.

**Reusable method:** when a carrier states a limit in prose, reconcile the *word* against the rate card's *own column definitions* before encoding — a loose "girth" can mean 3 different measures, and the contract's precise columns (L+W+H vs L+2W+2H) disambiguate better than the prose. Cross-check any candidate ceiling against the carrier's own stated *standard* parcel (a ceiling that rejects the standard parcel is the wrong reading).

**RESOLVED (2026-06-10): Maersk confirmed girth = L+2W+2H** (= `length_plus_girth_cm`), the **downside** reading — and the one I'd initially dismissed as incoherent (the dismissal was wrong; asking was right). Encoded as `maersk-3.2.0` (ceiling `length_plus_girth_cm ≤ 300`). Consequence: most per-country EU oversize surcharges are **unreachable** (l2w2h threshold ≤ the 300 ceiling) → the Maersk EU oversize lane is essentially standard-only. Final tender Q1 saving **€201,916 (6.8%)** (was €276,951 pure-girth, €377k no-ceiling); DB Schenker reroute **€107,684 (53%)**; 4,490 moved off DB Schenker (was 6,606). So the lesson on the "self-contradictory DE standard parcel" argument: it was a real tension, but the carrier's *physical handling limit* legitimately binds tighter than its own *surcharge schedule* — don't assume the ceiling must accommodate the standard parcel.
