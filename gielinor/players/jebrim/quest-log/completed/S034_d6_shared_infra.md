# S034 D6 — Shared infra audit
**Spawned by:** Jebrim, 2026-05-22

Audit scope: `2_analysis/` shared infra — `pipeline.py` (population pull), `capability.py`, `cost_matrix.py`, `invoice_adjustments.py`, `carriers/_base/*`, `carriers/__init__.py`, `sql/population.sql`. Spot-checked engines: maersk, dhl_paket, gls, dhl_express.

All paths absolute under `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\2_EU_tender_2026\2_analysis\`.

## TL;DR

The shared infra is **structurally correct but architecturally hollow**. The math primitives (forward-asof, sorted dims, fuel application, exclusivity-group resolution) all work and the engines that consume them produce consistent per-shipment costs. The hollowness is at the contract layer: `capability.py` is dead code that no engine calls (every engine re-implements eligibility inline); the DEPENDENT surcharge phase is declared but never invoked; `apply_min_billable_weights` is exported but never called; engine output schemas diverge by carrier so the cost matrix is sparse-by-construction. The most consequential live issue I found is **`apply_surcharges` does not gate on `eligible`** — surcharge cost columns carry nonzero values on rejected rows, masked only at the `cost_total_eur` finalize step. The most consequential silent assumption is the **forward-asof rate lookup nulls rate when weight exceeds the max band**, relying on eligibility's `over_max_weight` check to fire first; if any engine ever sets `MAX_WEIGHT_KG` > the largest band edge (or forgets the check), heavy parcels return `no_rate_found` instead of being priced. The SANITY_CHECK-flagged items (DEPENDENT empty, min_billable_weight unused, capability bypass) all still hold; this audit confirms them plus adds the eligibility-gate gap, schema-divergence in the cost matrix, and a `classify()` bucket-edge bug.

## pipeline.py / _base/ — calc bugs / silent assumptions / OK

### HIGH — `apply_surcharges` does not gate on `eligible` (`_base/pipeline.py:33-44`, `_base/pipeline.py:67-86`)

**What's wrong.** The standalone and exclusivity-group surcharge loops evaluate `surcharge.conditions()` against the full DataFrame with no `eligible` predicate. For surcharges whose `conditions()` returns `pl.lit(True)` (e.g. Maersk's `Overpack`, AT-Maut, DK-Toll-GLS — all the always-on additive flat fees), the cost column gets the full surcharge value on every row including `over_max_weight` / `country_not_served` / `oversize_no_surcharge` rejects.

**Expected.** Surcharge cost columns should be 0 (or null) on rejected rows.

**Mitigation today.** `_finalize` in every engine masks `cost_total_eur` via `pl.when(eligible).then(total)`, so the headline total is correct.

**Magnitude.** Zero on `cost_total_eur`. Non-zero on raw `cost_<surcharge>` columns, which the report layer (`report.py`, `cross_carrier_view.py`) may sum component-wise. Worth grepping component-level aggregations downstream — a `cost_overpack.sum()` over a Maersk slice includes 0.40 EUR × every rejected row.

### HIGH — Forward-asof returns null silently when weight > max band (`_base/pipeline.py:125-169`)

**What's wrong.** `lookup_rate_asof(strategy="forward")` matches the smallest weight band ≥ the parcel's weight. For a parcel above the rate-card's largest band, the asof returns null. The downstream code expects `over_max_weight` eligibility to fire first so the null never matters.

**Silent assumption.** Every engine must independently enforce `MAX_WEIGHT_KG ≤ largest weight_band_kg in the rate table`. There is no validator on this. If the rate card's largest band is 30 kg but `MAX_WEIGHT_KG = 31.5`, parcels at 30.5 kg silently reject as `no_rate_found` instead of being priced or rejected at the eligibility-defined reason.

**Magnitude.** Latent. Not currently broken; would be a structural footgun on the next rate-card update.

### MED — `apply_min_billable_weights` is exported, has no callers (`_base/pipeline.py:93-118`, `_base/__init__.py:12,28`)

**What's wrong.** Helper exists, surface area for `min_billable_weight` lives on the Surcharge ABC (`_base/surcharge.py:80`), but no engine calls it. FedEx considered Approach A (using this helper, two-pass lookup) and chose Approach B (pre-compute in `_supplement`, single-pass) — see `carriers/fedex/calculate.py:122`. The helper is now vestigial across the whole codebase.

**Expected.** Either remove the helper + the `min_billable_weight` attribute (dead surface) or document it as the canonical pattern in `_base/CLAUDE.md` so future engines reach for it instead of pre-computing.

**Magnitude.** Zero today; codebase clarity / future-engine drift.

### MED — DEPENDENT phase declared everywhere, never invoked (`_base/pipeline.py:19-44`, every `carriers/<x>/calculate.py`)

Already in SANITY_CHECK. Confirmed. Every engine's `surcharges/__init__.py` exports a `DEPENDENT = [s for s in ALL if s.depends_on is not None]` list that is empty. No engine ever calls `apply_surcharges(df, DEPENDENT)`. If a maintainer adds a surcharge with `depends_on=...` thinking the framework wires it for them, **it will silently never apply** — `apply_surcharges` is only ever called with the BASE list, and the `_finalize` step sums over `ALL` so the cost column would exist as null/zero and contribute 0.

**Expected.** Either:
- Every engine's `calculate()` should call `apply_surcharges(df, DEPENDENT)` after BASE (no-op when empty), so a future dependent surcharge attaches automatically; or
- Remove the BASE/DEPENDENT split entirely until it's actually needed.

The current state is "looks wired, isn't" — the worst footgun shape.

### MED — `apply_fuel_pct_of_subtotal` exported, no callers (`_base/pipeline.py:189-199`, `_base/__init__.py:14,31`)

**What's wrong.** Helper for the ontrac-style "fuel on subtotal" pattern. Every EU engine uses `apply_fuel_pct_of_base` or computes fuel inline. The ontrac-style helper is dead surface.

**Magnitude.** Zero today; same codebase-clarity tax as the min-billable helper.

### LOW — `in_period` accepts `billing_lag_days` but no caller uses it (`_base/surcharge.py:14-38`)

**What's wrong.** The `billing_lag_days` parameter shifts the date forward before the month-day comparison. Every caller (dhl_paket peak / peak_in_peak / gls peak / hermes peak) passes the default `0`. If any carrier ever applies peak by invoice date rather than ship date, the parameter exists but is hidden from carrier engine authors.

**Magnitude.** Latent; if a future engine needs it and the engine author doesn't read `_base/surcharge.py`, they may re-implement the offset inline.

### LOW — `lookup_rate_asof` row_id stable-sort fragility (`_base/pipeline.py:155-168`)

**What's wrong.** The helper attaches `_row_id` via `with_row_index`, sorts by `by_cols + weight_col`, asofs, then sorts back by `_row_id`. Polars `join_asof` requires the right side sorted by `by + on`; the left side it sorts internally. Should work, but the `drop` block (`weight_band_col` if it's in output and isn't `weight_col`) is over-defensive — `weight_band_col` is renamed via `select` at line 146-150 (it stays as `weight_band_kg`) and isn't the `weight_col`, so it should always be dropped when present. Confirmed correct but slightly opaque; a comment would help.

**Magnitude.** Zero.

### OK

- Exclusivity-group resolution (`_base/pipeline.py:67-86`) — priority-sorted, exclusion-masking. Provably one-winner. Tested via GLS bulky group + DHL Express oversize group.
- `_cost_expr` (`_base/pipeline.py:47-50`) — scalar/Expr coercion is correct.
- `add_sorted_dims` (`_base/supplement.py:23-54`) — math is right (`d_mid = lwh_sum - d_max - d_min`, `length_plus_girth_cm = d_max + 2*(d_mid + d_min)`). 1-decimal rounding before threshold comparison matches the ontrac fix. ~6% of rows have `width > length` per the population doc; this is the only safe path.
- `add_dim_weight` / `add_chargeable_weight` — both correct, "gross"/"max" modes well-named.
- `validate_surcharges` — actually called at import time from each engine's `surcharges/__init__.py`; catches `depends_on` typos and allocation-flag inconsistencies. Good.
- `stamp_version` — trivial, correct.

## capability.py — calc bugs / architectural concerns / OK

### HIGH — `capability.evaluate()` is dead code (`capability.py:68-96`)

**What's wrong.** Every engine re-implements eligibility inline in its own `_decide_eligibility`. No engine imports `capability`. Grep confirms: only docs reference the module. The "pure-rules layer" architectural choice (`CLAUDE.md` Three-Layer Architecture §1) exists in name only.

**Consequences.**
1. Eligibility rules drift between the registry and the engines — e.g., `_register(Capability(carrier="maersk", service="eu_hd", countries=_MAERSK_EU_COUNTRIES, max_weight_kg=30.0, weight_basis="gross"))` at `capability.py:152-158` is **never consulted**. The engine's `_decide_eligibility` (`carriers/maersk/calculate.py:221-267`) re-derives the country set from the EU rate-card join.
2. `build_matrix` (`capability.py:99-124`) and the `__main__` CLI (`capability.py:348-379`) would produce eligibility tables that disagree with what the engines actually compute on the rejected slice. Anyone running `python capability.py` gets a coverage report based on a parallel logic tree.
3. `Capability.excluded_packagetypes` is wired through `evaluate()` but never populated — `packagetype` filtering is dropped at SQL (`population.sql:60-61`) and the field is unused.

**Magnitude.** Cosmetic on output today (engines win). Maintenance debt: anyone reading the architecture doc and trusting the layer abstraction will be misled. **The "capability matrix" parquet artefact described in `CLAUDE.md:241` may not exist or may be stale.**

### MED — Registry built at import time reads parquet files (`capability.py:162-166`, `:204-205`, `:234-237`)

**What's wrong.** `_MAERSK_ROW_COUNTRIES`, `_DHL_INTL_ZONES`, `_DHL_EXPRESS_TDI_COUNTRIES`, `_DHL_EXPRESS_DDI_COUNTRIES` are all derived from `pl.read_parquet(...)` at module import. If any rate-table parquet is missing or has a renamed column, importing `capability` raises — and since `cost_matrix.py` doesn't import it, no one notices until the (also unused) `__main__` is run.

**Magnitude.** Bit-rot risk; not blocking today.

### MED — `evaluate()` `when` chain leaks `over_max_weight` checks against the wrong column (`capability.py:80-86`)

**What's wrong.** `weight_col = "weight_kg" if cap.weight_basis == "gross" else "billable_weight_kg"`. The function requires the caller to supply `billable_weight_kg` for billable-basis Capabilities. The CLI block (`capability.py:361-365`) constructs this with a crude `max(gross, dim/5000)` regardless of carrier (Maersk ROW = 5000, GLS EBP = 6000, FedEx air = 5000, etc.). So the CLI-rendered capability matrix uses 5000 for everyone — wrong for GLS EBP. Reinforces the deadness diagnosis: nobody runs the CLI for ground truth.

**Magnitude.** Zero in production (no consumers); confusing for anyone running the CLI to audit.

### OK

- Reject-reason constants well-defined (`capability.py:38-40`).
- `Capability` is `frozen=True` (`:47`) — good.
- `build_matrix` cross-join semantics are correct in concept; just no consumers.

## cost_matrix.py — calc bugs / silent assumptions / OK

### MED — `classify()` weight-band edge convention misalignment (`cost_matrix.py:49-50`, `:84-87`)

**What's wrong.** `WEIGHT_BAND_EDGES = [1.0, 2.0, 5.0, 10.0, 15.0, 20.0]` with labels `["<1 kg", "1-2", "2-5", "5-10", "10-15", "15-20", "20-30"]`. The label `"20-30"` is a misnomer — `cut` puts any weight ≥ 20 into the last bucket, including a parcel at 35 kg (which would have been rejected by every engine's `MAX_WEIGHT_KG` ≤ 40, but the rejected rows are still in the matrix with `cost_total_eur=null`). A 35-kg GLS-rejected parcel reads as a `20-30` shipment in any band-faceted view.

**Expected.** Add an explicit `>=30` band or relabel to `20+` to surface the heavy tail honestly.

**Magnitude.** Small but real — Maersk + AustrianPost cap at 30, GLS at 40, DHL Express at 70, DHL Paket at 31.5. The rejects above 30 kg get hidden in band-faceted scoring.

### MED — `dim_envelope` looks at `length_plus_girth_cm` from engine pass-through (`cost_matrix.py:88-94`)

**What's wrong.** `classify()` reads `d_max` and `length_plus_girth_cm` from `matrix`. These columns are added by `add_sorted_dims` inside each engine. Since `run_engines` does `pl.concat(parts, how="diagonal")`, the columns are present on every row — but their values come from whichever engine produced the row. All engines call `add_sorted_dims` with the same default `length_cm`/`width_cm`/`height_cm`, so values agree. Still, the dependency is implicit: if any future engine skips `add_sorted_dims` or routes via a different supplement, `classify()` silently produces `dim_envelope = "standard"` for nulls because `pl.when(null > 100)` evaluates to null which then falls into `.otherwise("standard")`.

**Expected.** Either move `add_sorted_dims` into `cost_matrix.main()` (run once on `pop`, not per-engine), or document the contract in `cost_matrix.py`.

**Magnitude.** Latent. Not broken today; brittle.

### MED — Schema divergence across engines, masked by diagonal concat (`cost_matrix.py:98-110`)

**What's wrong.** Each engine emits its own `cost_<surcharge>` columns (e.g., Maersk has `cost_overpack`, `cost_at_toll`, `cost_de_toll`, `cost_dk_toll_gls`, ...; DHL Paket has `cost_toll_co2`, `cost_peak`, `cost_peak_in_peak`, `cost_bulky_de`, ...; DHL Express has its own). `pl.concat(how="diagonal")` unions schemas and fills missing columns with null. The matrix ends up with **N × M surcharge columns** where most are null per row — fine for storage, but:

- The schema lacks a stable contract. A downstream consumer can't ask "what's the fuel cost on this row" via a single column name — `cost_fuel` is consistent across engines, but the surcharge components aren't.
- The `components_json` column promised in `CLAUDE.md:264` ("Returns `cost_eur` per row plus a `components_json` column breaking down base / surcharges / fuel") **does not exist** in any engine output. I grepped — no engine produces it.

**Expected.** Either build the `components_json` aggregation in `run_engines` (one canonical column, structured payload) or document that the matrix is wide-and-sparse.

**Magnitude.** Cosmetic at the matrix level; signal-loss if reports try to sum surcharges across carriers.

### LOW — `pl.concat` `how="diagonal"` over many engines silently allows column-name collisions to share types (`cost_matrix.py:110`)

**What's wrong.** If two engines emit a column with the same name but different polars dtypes (e.g., one Int32, one Int64), `how="diagonal"` raises. If they share a name and dtype but mean different things (unlikely with the `cost_<name>` prefix convention but possible for `service` / `eligible` / `reject_reason`), values silently union. The convention holds today; not a current bug.

### OK

- `_ENGINES` list (`cost_matrix.py:58-68`) is explicit and ordered.
- `eligible.sum()` count surfaces the count cleanly.
- `engine_version` stamp is recorded per engine row.

## invoice_adjustments.py — bugs / assumption issues / OK

### MED — OML/LPS thresholds are observed cluster boundaries, not contract terms (`invoice_adjustments.py:15-21`, `:29-32`)

**What's wrong.** `OML_THRESHOLD_EUR = 500`, `LPS_LOWER_EUR = 50` — comment says "observed cluster boundaries in 2026 Q1". This means a UPS LPS at EUR 49 silently passes through as non-LPS and stays in the baseline at full cost; a UPS LPS at EUR 501 gets misclassified as OML and the entire parcel drops.

**Expected.** Document the empirical-cluster basis in `docs/ASSUMPTIONS.md`; better, replace with a UPS-billing-line identifier if available in the mart. Otherwise the headline depends on a magic constant that has no contract anchor.

**Magnitude.** Per the docstring, ~106 OML parcels + ~645 LPS parcels in Q1. EUR 500 threshold is well inside the cluster gap, so misclassification risk is small — but the dependency on Q1 empirics could break on Q2/Q3 data without anyone noticing.

### MED — `LPS_PAID_SHARE = 0.5` is a negotiated discount that's hardcoded (`invoice_adjustments.py:31`)

**What's wrong.** The 50% LPS pay rate is a negotiation outcome. If the negotiation changes (UPS contract roll), the constant needs updating and there's no doc anchor to surface it.

**Expected.** Move to `docs/DECISIONS.md` reference with a comment back-pointer from `invoice_adjustments.py`. (Already documented elsewhere likely — but the file should cite the decision id.)

### LOW — `oml_eur_removed` stat double-counts? (`invoice_adjustments.py:54-63`)

**What's wrong.** `oml_ships = flagged.filter(_oml).unique("shipment_id")` — good, deduped. `oml_ships["real_oversize_eur"].sum()` is the sum of OML oversize charges; `oml_baseline_removed` is the sum of full `real_total_eur` removed. Both are computed on the deduped shipment-level frame so they don't double-count. **OK on re-read** — no bug, but the variable name `oml_eur_removed` is slightly misleading vs `oml_baseline_removed` (the former is just the oversize component, the latter is the full row total). Document.

### LOW — `LPS` adjustment subtracts `0.5 * osz` from `real_total_eur` on every row of an LPS shipment (`invoice_adjustments.py:67-71`)

**What's wrong.** Functionally correct — the adjusted `real_total_eur` should be applied identically to all carrier-rows of the same shipment. But there's no guard against the function being called twice on the same matrix; the second call would subtract another 0.5 * osz. Idempotency would be a nice safety.

**Magnitude.** Operator-error class; not a current bug.

### OK

- Function returns `(adjusted_matrix, stats)` — clean.
- Filtering on `shipping_provider_group == "UPS"` correctly excludes other carriers from these UPS-specific adjustments.

## Population SQL — drops, NULL handling, hidden filters

### MED — Three NULL drops compounded silently (`sql/population.sql:51-61`)

**What's wrong.** The SQL drops:
- Rows missing `weight_kg`/`length_cm`/`width_cm`/`height_cm` (line 51-54) — pre-rate-engine; engines couldn't price anyway.
- Rows missing `cs.total_eur` (line 58) — the 1.9% drop documented in SANITY_CHECK.
- Rows missing `packagetype` (line 60-61) — 0.35% drop.

Compounded ≈ 2.25%+ of raw Q1 volume drops before any engine sees a row. The headline EUR is on the 97.75% slice. Documented in SANITY_CHECK (1.9% only mentioned) but the cumulative drop isn't surfaced in `docs/DATA_NOTES.md` or the report.

**Expected.** Aggregate drop count + EUR magnitude documented at one place. The methodology footnote in v2 promised by `CLAUDE.md:318` may already cover this; not visible from the SQL.

### MED — `packagetype IS NOT NULL` filter exists for a Capability feature that's never used (`sql/population.sql:60-61`)

**What's wrong.** The comment says "Capability rules can reference packagetype, so a NULL would silently miscategorise." But no `Capability` instance has `excluded_packagetypes` populated, and no engine consults `packagetype` either (grepped). The filter is conservative — dropping 0.35% to prevent a categorization that nobody does.

**Magnitude.** Tiny — the drop is small. But the filter encodes a contract with an architectural layer that doesn't exist.

### MED — Country whitelist is hardcoded in SQL (`sql/population.sql:67-76`)

**What's wrong.** The 18-country whitelist is in SQL, not in a parquet config or a docs constant. CLAUDE.md says "in-scope countries finalised when capability matrix lands" — the matrix never landed (see capability.py findings); the SQL is the de facto source of truth. AU/NZ are explicitly included as "above threshold"; per-carrier capability matrices reject them as `country_not_served` for non-Maersk/non-DHL Paket lanes — fine, just a one-place-to-update issue.

**Magnitude.** Maintenance overhead.

### LOW — `cs.* IS NULL` rows on `LEFT JOIN` — drop interaction (`sql/population.sql:46-58`)

**What's wrong.** `LEFT JOIN ... USING (shipment_id)` plus `WHERE cs.total_eur IS NOT NULL` is an INNER JOIN in disguise. Could be written explicitly. Cosmetic.

### OK

- `CAST(... AS FLOAT8)` block (`:20-45`) — handles the polars Decimal-mixing issue documented in `pipeline.py:23-24`. Correct prophylactic.
- Date range half-open `>=` / `<` — correct Q1 boundary semantics.

## Architectural concerns / drift

### HIGH — The "Three-Layer Architecture" claim no longer matches reality

`CLAUDE.md:238-271` describes three layers: capability rules → rate engines → cost matrix. Reality:

1. **Capability layer is bypassed entirely.** Engines re-implement eligibility. The registry (`capability.py:131-341`) is dead. See above.
2. **Engines don't share an output schema.** Each emits its own surcharge cost columns; no canonical `components_json`. The "cost matrix" is a long-format diagonal-concat with N×M sparse columns.
3. **Cost matrix is a column-union, not a contract.** Downstream views (decision_report, cross_carrier_view) have to know per-engine column names.

The pattern wins from ontrac (BASE/DEPENDENT, exclusivity groups, dim rounding) **did** transfer; the contract-layer wins (declared eligibility, unified components) did not.

### MED — `apply_invoice_adjustments` isn't called from `cost_matrix.py`

The adjustment function exists; nothing in this audit set imports it. Whichever downstream (decision_scorer.py, report.py, scenarios.py) applies it has to remember to. The file docstring says "Apply once at the top of any downstream that consumes real_total_eur" — load-bearing manual discipline.

### MED — Two `pipeline.py` files, very different roles, easy to confuse

- `2_analysis/pipeline.py` — population-pull script (SQL → parquet).
- `2_analysis/carriers/_base/pipeline.py` — engine-orchestration helpers.

Naming collision. New contributors hitting "pipeline.py" in search results have to disambiguate.

### LOW — `ENGINE_VERSION` is stamped per engine output but not validated against the rate-table file timestamps

Each engine's `constants.ENGINE_VERSION` is a hand-maintained string. No CI check that bumping a rate table re-stamps the version. The pattern works as long as the maintainer is disciplined.

## Notes

- DEPENDENT-phase-empty observation: **still holds**, all 9 engines.
- `min_billable_weight`-plumbing-unused observation: **still holds**, plus FedEx explicitly chose Approach B (pre-compute in supplement) over the helper.
- New since SANITY_CHECK: **surcharges fire on rejected rows** (high-impact only if component aggregations are run), **`classify()` weight-band labelling buries >30 kg rejects in `20-30`**, **schema divergence in the cost matrix** (no `components_json` exists), **the country whitelist is in SQL not config**.
- DPD PL and FedEx engines are added (post-SANITY_CHECK) and follow the same pattern as the original 6 — confirms the drift hasn't been corrected even as new engines shipped.
- Engine contract consistency (spot-checked maersk, dhl_paket, gls, dhl_express): all follow the same `_supplement → _attach_rate_tables → _decide_eligibility → apply_surcharges(BASE) → _apply_fuel → _finalize → stamp_version` skeleton. Pattern adherence is good; what they all collectively skip (`capability.evaluate`, DEPENDENT, `apply_min_billable_weights`) is the architectural concern.
