# S192 · DB Schenker reroute — package dimensions + savings realism

**Player:** Jebrim · **sid8:** 384c1c27 · **Opened:** 2026-06-10

## Ask
Niklavs: for the EU tender's final routing, which packages switch off DB Schenker → Maersk/Hermes, and how realistic are the savings? Then dive into the actual package dimensions — constant or varying? — and scope what we can route on.

## What happened (turn log)
- Pulled the DB Schenker reroute population + per-type savings. Initially read the `validation/db_schenker/` artifacts (move_population.parquet, validation_stats.json) — these were dated 13:00, the **3.1.0 / pure-girth** state (6,606 moved, ~€161.7k). Presented package economics + confidence tiers off those.
- Niklavs steered into three threads: zV (is the dim really constant?), CUSTOM_OVERSIZED (can we route on these dims?), GEL (leave on DBS).
- **Dimension provenance finding** (holds regardless of routing version): profiled `population_2026q1.parquet` — CUSTOM_OVERSIZED genuinely varies (858 distinct shapes, real measurements); zV is templated (99.4% two flat templates, dims don't track weight); GEL fully constant (1 tuple). `volume_cm3` == L×W×H exactly → no independent dim cross-check.
- Niklavs caught a casing trap (ZV / Zv variants). Re-checked: 3 casing variants of cut-to-size; my "UPS measures it, DBS defaults" claim was **wrong** (picked the one varying pocket). Templating is packagetype-wide on both carriers; casings likely mark different source systems.
- Captured the operational constraint: routing commits per (dest × packagetype) cell, not per parcel (`build_final.py:8`) — carrier must absorb the full dim range in a cell.
- **Stale-numbers catch (close ritual):** comms tail revealed the Maersk girth question was answered L+2W+2H at ~17:25 (sibling S189-cont, commit a96e449, maersk-3.2.0). Re-derived on current HEAD: **4,490 moved (Hermes 4,463 / Maersk 27), ~€99.7k** (committed routing report: €107,684). Maersk oversize lane collapsed; GEL 0 move; zV → Hermes is 85% of the switch saving.

## Decisions
- GEL stays on DB Schenker (already what the engine does — 0 move). Closed.
- CUSTOM_OVERSIZED routable (real dims); Maersk-ceiling risk resolved unfavorably → effectively closed.
- zV dim provenance is now the dominant open question on the whole DB Schenker saving (€85k rests on a template dim).

## Cascade.
None — read-only on bi-analytics (no content writes, nothing committed there). The corrected numbers match the committed a96e449 state; no doc updates owed.

## Main-brain changes.
Bank draft (DB Schenker reroute dims + savings) + examine draft (verify-HEAD-before-derived-artifacts) + this quest-log + inventory resume + comms. No confirmed/ promotions.

## No pending external actions.
