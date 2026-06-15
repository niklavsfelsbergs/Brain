# USPS NA rate-vs-mix — definitive upstream pull (off gold contract)

**Spawned:** shipping-agent mart specialist (emulation), 2026-06-15. Principal: Niklavs via Jebrim.
**Brief:** Resolve whether the +€1.05/parcel NA USPS step (Jan-Mar €6.14 -> Apr €6.52 -> May €7.19) is a genuine rate increase or a mix effect. Gold collapses all USPS to one key and can't separate service level, so authorized upstream pull under maintainer profile.

## Scope / tier
- OFF the gold contract. Upstream source: `enterprise_silver.usps_invoices` (maintainer `CLAUDE.local.md` present, user `tcg_nfe`, read-only). Confirmed wider perimeter before reaching upstream.

## Turn log
- Confirmed maintainer overlay exists (gitignored) -> upstream authorized.
- STEP 1: located source. `enterprise_silver.usps_invoices` carries every rate driver: service (`assessed_mail_class_name`), billed weight (`ca_assessed_weight`/`manifest_weight`), `zone`, dest/entry ZIP, `base_postage` (per-piece base USD), surcharge/nonstandard-fee cols, `final_postage_eur/usd`, `mailing_date`. One row per `impb` (parcel), `transaction_type='PURCHASE'`, zero NULLs on service/weight/zone.
- KEY: service mix is constant -> 100% USPS Ground Advantage every month. No service shift possible. Matched cohort reduces to weight x zone.
- STEP 2 matched cohort (service const x weight band x zone): within every held-constant cell, base rose ~11-14% Jan-Mar->May. Consistent across cells (e.g. 0-1lb Z04 +12.0%, 1-2lb Z04 +11.2%, 2-3lb Z04 +12.0%).
- Decomposition (fixed Jan-Mar weight x zone mix): JanMar €6.14 base-eur -> Apr matched 6.58 vs actual 6.58 (all rate, zero mix) -> May matched 7.05 vs actual 7.26. Of +€1.11 total: ~+€0.91 matched rate (+14.8%), ~+€0.20 mix (heavier/farther May parcels).
- Surcharge check: nonstandard fee flat (~$0.9); no new oversize/peak/residential surcharge. Surcharge rise is proportional fuel on a bigger base.
- Coverage: raw lines reconcile to 94-107% of gold USPS NA by parcels and euros each month; gold May = €127.7k invoiced (matches ~€128k target). Sample representative.

## Headline result
The +17% step is REAL RATE, not mix. ~85-90% of the step is a genuine USPS rate increase on an unchanged package (~+12-15%, well above a normal mid-single-digit GRI). ~€0.20 (~15-20%) is mix (heavier/marginally-farther May parcels). Service mix is a non-factor (single service). No new surcharge.

## Caveats / open
- Base figures in USD; FX stable (~1.17 usd/eur, no drift) so EUR step is not currency.
- Upstream = off curated gold contract: no bucket-collapse guarantees, raw vocab. Reconciles to gold within timing noise (gold dates on received-by-carrier, raw on mailing_date).
- Why USPS GRI reads ~12% vs typical ~6%: likely a USPS rate-card change effective ~Apr 2026 plus possible zone/dim-pricing table refresh; not separable further within the lines beyond what's shown. Flag for finance: this looks like a real off-cycle or above-trend USPS increase, worth a rate-card confirmation with the carrier.

## Deliverables (outside brain)
- Chart: `Documents/GitHub/shipping-agent/workbench/investigations/usps-na-rate-vs-mix-2026/outputs/20260615-104854--usps-na-same-package-base-rate-climbed-12-jan-mar-to-may-2026.html`
- SQL: `.../sql/20260615-01_matched_cohort_rate_vs_mix.sql`
- Data: `.../data/20260615-01_matched_base_by_weightband.csv`
