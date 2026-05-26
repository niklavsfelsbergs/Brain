# S075 — Shipping-agent: production-site (origin) awareness

**Player:** Jebrim · **Session:** b3bb305b · **Opened:** 2026-05-26
**Repo:** out-of-tree `Documents/GitHub/shipping-agent` (picanova/shipping-agent), tree clean @ f02c6e0 at start.

## Ask

Principal: the shipping agent is "basically never aware of the production site" — where the parcel originates from, "very important for shipping." Example: a carrier-tender data pull (`all countries except US/CA, 2026 Q1, packagetype + median dims + avg weight + dest country + shipment count`) where the agent confirmed *vertical* (rule 12, "TCG shops only") but never asked **which production sites** the parcels ship from.

## Diagnosis

Gap is **behavioral, not data**. `production_site` is already a column on `fact_shipments` (17 distinct values), documented in `reference/tables.md` (incl. the "Dimensions you can slice by" catalogue + "Production-site logic"), `sources.md`, `known-dq.md` (`'Other'` LIKE-map caveat), and `skills/query-patterns.md`. What was missing: no §0 rule made the agent *aware that production site = origin* or gave it a reflex to confirm origin scope the way rule 12 confirms vertical.

## Design decision (principal-picked)

Offered the firing-aggressiveness fork via AskUserQuestion (recommendation = A). Principal chose **A — origin-sensitive only**: the gate fires only when origin is load-bearing (tenders/RFQs, carrier rate/lane comparison, cost-per-parcel or transit-by-lane, "where do we ship from"); origin-neutral asks default to all-origins-combined and *state* it. Rejected B (universal, like rule 12 → double-menu / over-fire / re-bloat) and C (awareness-only, no menu → under-delivers vs the tender example). Choice respects the existing over-fire guardrail + the audit-3 anti-bloat discipline.

## Changes — COMMITTED + PUSHED to picanova/main (f02c6e0..47f31de, commit 47f31de)

`how_to.md`:
1. §0 intro line — rule count 36→37; added rule 37 to the enumeration ("governs production-site / origin scope on origin-sensitive work").
2. Rule 12 — appended a one-line pointer: vertical and origin are *independent* scope axes; origin gets its own gate (rule 37) on origin-sensitive work.
3. New **rule 37** subsection (`### Cross-cutting rule — production-site / origin scope (37)`) after rule 36, before the translation table. Scope = origin-sensitive only (conditional, unlike every-mode 35/36). Production site = origin; carriers price by origin→destination lane; surface the interactive pick (*all combined / split / specific*, grouped not all-17) before pulling; required (not optional) scope for a tender; restate + state in assumptions once named; plain-English site names not raw codes; vertical+origin independent (a question can need both gates, one, or neither).

`reference/tables.md`:
4. Added an **Origin note** right after the falsification-cut catalogue table: `production_site` is the parcel's origin, load-bearing scope (not just a cut) for tenders/rate-comparison/lane economics, cross-ref to §0 rule 37.

## Validation (read-only agent-embodiment, 2 parallel dwarves, neutral probes)

Both briefs kept neutral on "origin"/"production site" → genuine spontaneity test (cf. neutral-probe-for-spontaneity memory).
- **D1 (the exact tender prompt):** rule 37 fired spontaneously — surfaced the origin pick before pulling (grouped, not 17), framed as required tender scope, *alongside* the rule-12 vertical pick. Self-audit cited rule 37 + the tables.md note; trigger = literal "carrier tender." PASS.
- **D2 (guardrail — "how many packages did TCG shops ship in April"):** rule 37 correctly did NOT fire (origin-neutral → all-origins default, no origin menu). PASS. (D2 still threw the *vertical* menu on "TCG shops" — pre-existing rule-12 close-call, NOT introduced by this change; audited honestly.)

## Follow-on — B2C/B2B vocab fix (commit 11996a8, pushed 47f31de..11996a8)

Principal caught the **live** deployed agent (screenshot: "show transit times by carrier and destination") — which **confirms rule 37 fires in production** (it surfaced both the vertical pick AND the production-site origin pick) — but the *vertical* menu mislabeled the TCG umbrella as "B2C shops only — The B2C + MerchOne storefronts." Two errors, both **pre-existing** (not introduced by rule 37; rule 37 just made the vertical menu more visible):
- TCG is **not** B2C. TCG = B2C (Picturator) **+ B2B (MerchOne/PicaAPI)**. The umbrella must never be labeled "B2C."
- MerchOne (PicaAPI) is the **B2B** line, not B2C.

Fixed across: `how_to.md` (rule 12 parenthetical; translation table PicaAPI row + source_system row; the Mode-1 worked example, which also self-contradicted — Q "B2C shops" / A "B2C + MerchOne"; the unstated-vertical note) + `reference/sources.md` (PicaAPI heading + inline-assumption template) + `reference/mart-contract.md` (source-platform list). `Picturator = B2C` is correct and untouched. Grepped all `.md` — no umbrella-as-B2C leaks remain. Net menu render now: *"TCG shops only — our B2C storefronts + the MerchOne B2B line."*

## State / open

- shipping-agent edits **made, uncommitted, HELD** for principal go (commit + push to picanova/main; repo IS pushable per [[S062_7f1aecf4_shipping-agent-euro-precision-and-build-report|S062]] correction). Will `git commit -- <pathspec>` (never bare `git add .`) per the shared-index hazard from 006248ef.
- Brain writes: this quest-log + comms OPEN + intent only.
- No bank harvest yet (harvest after the picture stabilizes / on close).
- Possible follow-up if principal wants it: the translation-table could gain plain-English handles for specific site codes (PCS CGN → "our Cologne site", etc.) — deferred, not needed for the rule to work.
