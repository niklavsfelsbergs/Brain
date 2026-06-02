---
quest: S124_shipping-agent-report
sid8: e3bb38c4
ts: 2026-06-02 10:40
open_dep: REBUILD pending — current report is a static template that "tells nothing"; principal wants it rebuilt delta/exception-driven + investigation-led + contract-aware. Knowledge-loading fix shipped this session.
---

# Resume / kickoff brief — REBUILD the shipping report

**Status:** in-progress. The report harness exists and runs, but the principal judged the output near-useless ("this is shit, tells me nothing"). The decision (2026-06-02) is **rebuild the reporting from concepts** in a fresh session — not patch. This brief IS the rebuild prompt. The knowledge-loading fix that makes a fresh session start *right* shipped this session.

## Read first (in this order — do NOT skip; this is the whole lesson)

1. `shipping-agent/how_to.md` §0 + `reference/{mart-contract,tables,known-dq}.md` — the mart contract. **Loading this is mandatory before any mart reasoning.** The `domain-cue-reminder.py` hook will nudge you on the shipping cue; obey it. Better: **spawn the shipping-agent** (`subagent_type: shipping-agent`) to do the mart work — it loads the rulebook by construction. (See `players/jebrim/CLAUDE.md` → "Shipping / mart work" + the `calling-the-shipping-agent` skill.)
2. `shipping-agent/reference/known-dq.md` → **"UPS oversize surcharges — LPS / OML"** (taught this session) — the refund logic that reframes the headline finding.
3. `players/jebrim/quest-log/in-progress/S124_61d62e21_shipping-agent-report.md` — full design + build log + this session's turns.
4. The contract corpus for cross-checking suggestions: `players/jebrim/bank/notes/projects/shipping-contract-corpus.md`, `2026-05-23-package-dimensions-carrier-envelopes.md`, `eu_tender_2026.md`.
5. The current harness: `bi-analytics-main/NFE/projects/4_automated_shipping_report/` (lib/, README, notebook/running-notebook.md).

## Why the current report fails (the critique to fix — principal's 4 points)

1. **Static, not delta.** Everything runs on a 120d trailing window, so §1/§5 barely move day to day — Groundhog Day. **The fresh signal is the DELTA** (what cost arrived / what moved since last snapshot), not the level. Two time bases: cost-arrival keeps the 120d cohort + snapshot-diff (late invoices need the tail); **volume/mix migration needs a SHORT recent window vs baseline** — that cut does NOT exist yet.
2. **Findings not interpreted against the contract.** The €1,300 "UPS overbilling" was almost certainly **OML surcharges** (expect-full-refund), mislabeled because the contract wasn't loaded. Every cost finding must be read against carrier-contract terms (refund expectations, rate cards).
3. **Template, not investigation.** The report ran canned calcs and wrote a paragraph. It must **investigate**: spot what moved, then *query the mart* to explain it. Target ~30 min of real querying, not 3. It must answer two questions: **(a) did new cost come in and is it OK?** **(b) is volume for a package/country/weight corridor moving to a different carrier?**
4. **Suggestions uncrosschecked.** §4 "opportunities" (e.g. DB Schenker lanes) must be checked against the contract + reality (DB Schenker PCS PL is heavy freight, avg billed wt 88.6 kg — high €/parcel is mostly legitimate; ~€230k was PAPER).

## Mart facts you now have (were the knowledge gap — verified in tables.md this session)

- **Dims ARE in the mart:** `length_cm/width_cm/height_cm`, `volume_cm3`, **`length_plus_girth_cm`** → LPS(>325)/OML(>419) verifiable from data (NULL on ORWO/external).
- **Charge text:** `fact_shipment_invoice_lines.charge_description` / `_english` + `oversize_overweight` bucket → confirm the surcharge band + track refund-in-place reversals (sign of `charge_amount_eur`).
- **Corridor cuts all present:** `packagetype`(235), `weight_kg`+dims→bands, `destination_country`/zip-prefix, `shipping_provider_group`/`extkey`, `production_site`(origin/lane).
- **`is_returned` is a trap** — populated but semantics unconfirmed; do NOT use for return-rate. LPS return-rate must come from snapshot-diffing the oversize_overweight reversals.

## Next concrete steps (the rebuild)

1. **Spawn the shipping-agent. Step 1: VERIFY the OML/LPS hypothesis on live data** — are the ~86 standing PCS PL UPS rows (~€111k over expected) actually OML? Check `length_plus_girth_cm > 419` + `charge_description`; split LPS vs OML; confirm the −€91.6k reversals are refunds-in-place. This decides whether the headline is "€111k receivable to monitor" (likely) vs "billing error." **The current report asserts this UNVERIFIED.**
2. **Design the report shape**: lead with a plain-English **Bottom line** (status + the one action + the real number); demote evidence to "supporting detail." (Today's report.md was reworked this way as a sketch — keep that, but make the body delta-driven.) HTML deliverable, **golden theme already built** (`lib/render_html.py` — dark+gold, stolen from the dev-brain doc skin; works).
3. **Build the corridor-movement cut** — recent ~14 ship-days vs prior ~8 weeks, flag carrier-share shift > ~10pp on material-volume corridors. **(Window/materiality NOT finalized with principal — confirm.)**
4. **Cross-check any §4 suggestion against the contract corpus** before sizing; PAPER vs DEFENSIBLE honesty tag.
5. Remaining harness to-dos from before: retention/thinning (small), triggering (deferred — design first).

## Built/shipped THIS session (so don't redo)

- **Knowledge-loading fix (DONE):** mart work now triggers a load nudge via `domain-cue-reminder.py` (generalized from a shipping-cue prototype; shipping is entry #1 in `gielinor/.claude/hooks/cue_registry.py`) + spawn-the-shipping-agent is the documented default in `players/jebrim/CLAUDE.md` + `calling-the-shipping-agent` skill.
- **Taught the agent (DONE):** LPS/OML section added to `shipping-agent/reference/known-dq.md`.
- **HTML + golden theme (DONE):** `lib/render_html.py`; build_report + dq_canary emit `.html`+`.md`.
- **First real T-vs-T-1 run ran clean** (159,052 changed; canary 0/0). Snapshots `snapshot_2026-06-01/02.parquet` on disk (T-1 + T available for the verify query).

## Open decisions for the principal

- Corridor-movement window + materiality bar (step 3).
- Whether to commit/clean the orphaned `gielinor/.claude/hooks/shipping-cue-reminder.py` (superseded by domain-cue — archive it).
