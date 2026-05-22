# S034 F3 — billable-weight rate-lookup regression fixtures

**Role:** dwarf (spawned by Jebrim principal)
**Scope:** Austrian Post + Hermes engines
**Status:** fixtures landed; F3 bug confirmed live; tests fail loudly with named signal

## What was done

1. **Added inline comment** at the `lookup_rate_asof` call in both engines:
   ```
   # RATE LOOKUP USES weight_kg; FLIP TO billable_weight_kg WHEN VOL-WEIGHT FLIPS (S034 F3)
   ```
   - `2_analysis/carriers/austrian_post/calculate.py` (immediately before line 139)
   - `2_analysis/carriers/hermes/calculate.py` (immediately before line 139)

2. **Added regression test modules** (new files, sit alongside existing `test_engine.py`):
   - `2_analysis/carriers/austrian_post/tests/test_f3_billable_lookup.py`
   - `2_analysis/carriers/hermes/tests/test_f3_billable_lookup.py`

   Each module exposes two pytest-discoverable tests and a standalone `main()`:
   - `test_baseline` — confirms current `mode="gross"` behavior (rate band = gross weight band). Passes.
   - `test_f3_regression_signal` — monkeypatches `add_chargeable_weight` (resolved via `importlib.import_module` because the package `__init__.py` shadows the submodule name with the re-exported function) to force `mode="max"` on a dim-heavy parcel (1 kg gross, 100×50×10 cm → 10 kg dim at divisor=5000). Asserts the rate band matches the 10 kg billable band. **While F3 is unresolved, this test fails with the message:**
     > `S034 F3 REGRESSION: rate=4.2329 matches 1 kg gross band, NOT the 10 kg billable band (7.3129). Rate lookup is keyed on weight_kg; fix calculate.py:~143 (weight_col="billable_weight_kg").`
     The failure IS the regression signal — there is no XFAIL tag; this test is meant to be red until F3 is fixed.

3. **Test runner outcomes** (from `2_analysis/`):
   - `python -m pytest carriers/austrian_post/tests/ carriers/hermes/tests/` → 2 passed, 2 failed (the two F3 regression assertions, both naming the fix location).
   - Existing engine spot-check suites untouched: AP 14/14 pass, Hermes 19/19 pass (confirming the inline comments didn't perturb anything).

## Engine behavior surprises / notes

- **`add_chargeable_weight` does not accept `"volumetric"`.** Only `{"gross", "max"}`; unknown modes raise `ValueError`. The brief's monkeypatch language was honored by using `mode="max"` with a parcel where `max(gross, dim) == dim` — semantically the volumetric case. This is documented at the top of both new test modules.
- **Package-level shadowing.** `carriers.austrian_post.__init__.py` does `from .calculate import calculate`, so attribute access `carriers.austrian_post.calculate` resolves to the function, not the submodule. Same for Hermes. The monkeypatch needs the submodule namespace (to swap the imported `add_chargeable_weight` symbol that `_supplement` actually calls). Used `importlib.import_module("carriers.austrian_post.calculate")` to grab the real submodule.
- **Hermes lookup uses `(service, destination_country_code)` whereas AP uses `(service,)` only.** Both still key on `weight_col="weight_kg"` — the F3 bug is identical in shape on both engines, fix is the same one-character change in each `_attach_rate_tables`.
- **Engine accepts no `mode` override at the top level.** Engines hard-code `mode="gross"` inside `_supplement`. We did NOT add a guard that raises when MODE is volumetric (the brief's fallback option) because the monkeypatch path already exists and the failing test is a louder signal than a guard at the same level of intrusiveness. If we wanted belt-and-braces, a `MODE`-level guard would live in `_supplement` next to the `add_chargeable_weight` call — adding that is a one-line follow-up if Jebrim wants it.

## Files touched

- `2_analysis/carriers/austrian_post/calculate.py` (comment only, before line 139)
- `2_analysis/carriers/hermes/calculate.py` (comment only, before line 139)
- `2_analysis/carriers/austrian_post/tests/test_f3_billable_lookup.py` (new)
- `2_analysis/carriers/hermes/tests/test_f3_billable_lookup.py` (new)

## Fix instructions (for whoever resolves F3)

In each engine's `_attach_rate_tables`, change:
```python
weight_col="weight_kg",
```
to:
```python
weight_col="billable_weight_kg",
```
Then flip the `add_chargeable_weight(df, mode="gross")` call in `_supplement` to `mode="max"` (which will also require attaching `dim_weight_kg` via `add_dim_weight(df, divisor=<carrier divisor>)` first). Re-run pytest; the F3 regression tests should both flip to PASS with the "F3 RESOLVED" message. At that point, retire the two `test_f3_billable_lookup.py` modules and clear the inline `# RATE LOOKUP USES weight_kg…` comments.
