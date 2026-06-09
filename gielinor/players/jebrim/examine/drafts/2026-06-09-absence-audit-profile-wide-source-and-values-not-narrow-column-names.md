# Auditing for ABSENCE: profile the wide raw source + the VALUES, not narrow column names

**Observed:** S167 (2026-06-09), carrier invoice dimension-coverage audit.

**What happened.** Asked which carriers provide dimension data on invoices. The first shipping-agent pass concluded ~14 carriers (incl. UPS, FedEx, DPD, Yodel, Ambro, DB Schenker) have "no dimension field" — by scanning the **narrow curated silver `*_invoices` tables' column NAMES**. Niklavs pushed back on one instance: *"how does it look for UPS? nothing?"* A deep re-check found UPS carries raw L×W×H in a **254-column bronze source file** the scan never opened, plus **~€998k of oversize surcharges** living in charge-description VALUES (not column names). A 4-agent fan-out then overturned the verdict for FedEx (91% raw dims + €1.86M derived), DPD DE, Yodel (silver 0% but bronze ~45% recent), Ambro, DB Schenker.

**The failure mode.** Auditing for the *absence* of a signal via a single method on a single layer systematically false-negatives. Two specific traps here:
1. **Narrow curated layer ≠ the source.** Silver collapses/drops fields; the raw width lives in the wide bronze source file. A column-name scan on the curated table reaches neither.
2. **Signal in values, not names.** The oversize/handling signal lives in `chargedescription` VALUES (LPS/OVR/OML), not in any column literally named "oversize" or "dim."

**The rule.** When auditing for absence of a field/capability across a multi-entity domain: profile the **widest raw source** per entity (enumerate the catalog, don't trust the curated table), AND profile **column VALUES** (charge codes, description text), not just column names — *before* concluding "none." A clean "not found" from a narrow name-scan is a hypothesis, not a finding.

**Ties to:** [[2026-06-01-verify-the-thing-dont-trust-the-wiring]] (inferred-absence is the trap), the never-assert-absence-against-a-principal-claim reflex (Niklavs's skepticism was the trigger that surfaced the miss), and the don't-generalize-from-a-single-verified-case discipline (each carrier needed per-instance verification — and the *negative* needed it just as much as the positive). The new edge: the brain already had "don't assert absence against a *claim*" — this adds "don't assert absence off a *narrow-method scan*," even unprompted.

**Why it's mine to keep.** I delivered a wrong "mostly none" answer with confidence; the method, not the data, was the bug. The lesson is a standing audit-method check, not a one-off.
