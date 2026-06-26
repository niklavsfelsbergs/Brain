# Confirm an external figure's scope before anchoring a correction on it

From [[S370_0643e962_ups-retention-and-lps-treatment]] (truck-cost thread).

**What happened.** The principal relayed Andrea (logistics): UPS truck cost is miscalculated, "1 truck/day, €374/weekday." I checked the gold `fact_truck_charges` UPS lane, found corroborating shape (119 truckloads/64 days, phantom 17-parcel loads), and built toward a "we're overstating ~2–5×" conclusion — sized the €374 impact, discussed an ETL revamp, started a correction. Then Andrea corrected himself: **the €374 figure was about ORWO, not the UPS EU tender.** The whole truck-revamp direction reverted; UPS truck cost stays as-is.

**The tell I walked past.** Andrea's €374/weekday and the system's own €1,025/truckload-row disagreed by a large factor; "1/day" vs the data's 1.86/day likewise. I read that gap as "the system is wrong" and ran with it — but a large factor-discrepancy between an external figure and the system's own data is **also a scope-mismatch signal**: the figure may describe a different entity/population. ORWO and UPS share the same truck-table structures and the same person (Andrea) works both tenders, so the cross-wire was easy.

**Rule.** When a third party's number arrives via the principal, its **scope/entity is a hypothesis**, not a given — confirm it applies to the current analysis's entity before anchoring a correction (or sizing impact, or drafting a handover) on it. Especially when sibling projects share data structures and personnel. A big figure-vs-system discrepancy should first ask *"are we even describing the same thing?"* before *"the system is wrong."* Cheap one-line confirm; the cost of building the wrong correction is a turn+. (Sibling of the wrong-instance / verify-the-thing reflexes; and "don't generalize from a single verified case".)

**What I did right:** kept caveating "my own gold read independently shows…" and changed no files, so the revert was clean (no rework). The miss was velocity toward a conclusion, not a committed error.
