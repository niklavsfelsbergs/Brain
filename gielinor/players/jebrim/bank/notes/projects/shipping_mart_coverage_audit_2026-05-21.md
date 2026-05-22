# Shipping Data Mart — coverage audit (2026-05-21)

**As of:** 2026-05-21 (S023 — pre-cutover, pulled costs from `fact_shipment_cost_summary.total_eur`. Cost-column wiring on `fact_shipments` landed 2026-05-22; re-verify holes against gold before quoting).

**Source of truth (external):** `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/coverage-audit.md` — durable mart-wide cost & revenue coverage matrix with regenerate-on-demand probes.

**Quest:** S023 — `players/jebrim/quest-log/in-progress/S023_2026-05-21_shipping-mart-coverage-audit.md`.

## Headline (2025-01-01+ window)

- **Mart-wide cost coverage ~85%**, not the ~73% another agent suggested from a shop-scoped read.
- **Four concentrated holes** account for almost all the missing 15%:
  1. ORWO POST — 568K shipments, structural 0% (no bulk-bill source).
  2. Picturator `POST_DVF` — 170K shipments, 0% (no carrier-invoice source, Germany-concentrated).
  3. Picturator MAERSK — 98K shipments, 68.9% (weakest in Sweden 17.4%, France 67.6%, UK 72.6%).
  4. Picturator `ASENDIA` (not "USA") — 5.8K shipments, 0% (likely stale carrier label).
- **Wolfen carrier-cost wiring is in place**, contrary to the other agent's framing. ORWO DHL = 97-99% Nov 2025 → Apr 2026. ORWO UPS was broken Nov-Dec 2025 (4-12%), recovered Jan 2026 (now 98%+). Current-month dips are invoice lag, not wiring.
- **ORWO `destination_country` = 100% blank** — country slicing on ORWO is impossible until the S002 wiring thread lands.
- **how_to §9 dim-coverage subsection** was stale (bare-DHL / UPSWWE story); patched 2026-05-21 to reflect post-`356a565b6` refactor (current unresolved is POST_DVF + USPS + NULL-extkey, not the old variant family).

## Methodology breadcrumb

The lesson — coverage questions get a time slice and a source axis — is captured as a skill draft: `players/jebrim/spellbook/drafts/skills/coverage-questions-time-and-source-axis.md`.

The same rule was added to the shipping-agent's `how_to.md` as §0 rule 7, and a "Source maturity (V1 status)" subsection was added to §2.

## Why this note exists in Jebrim's bank

The durable matrix lives in `bi-analytics-main` (external repo); this is the Jebrim-side breadcrumb so future sessions know to look there rather than re-deriving. The breadcrumb is here, not in the matrix, because Jebrim's brain has to remember **what work happened and where the artifact landed** — the matrix itself belongs with the shipping-agent that owns it.

Promote during alching when (a) the audit has been re-verified at least once and the methodology has been used on a second coverage question, or (b) the shipping-agent has independently re-run the matrix and the breadcrumb's path still resolves.
