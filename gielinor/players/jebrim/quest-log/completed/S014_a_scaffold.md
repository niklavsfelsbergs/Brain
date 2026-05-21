# S014-A — Stream A scaffold (2026-05-21)

## Summary
Scaffolded the Shipping Data Mart TTYD project from the TTYD-template tree. All mechanical work landed: 8 verbatim copies, 4 adapted files at project root, 4 adapted files inside `visualization-studio/`, fresh `how_to.md` skeleton with §5–§8 fleshed and §1–§4 carrying TBD placeholders for principal-Jebrim's Stream B. Smoke test (`python -c "import db"`) passes clean.

## Files created

### Copied verbatim (8)
- `.claude/settings.local.json`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `GROK.md`
- `requirements.txt`
- `build_light_html_presentation.py`
- `create_timestamped_presentation.py`
- (plus the entire `visualization-studio/` tree copied first, then 4 files within it edited — see below)

### Adapted (8)
- `.gitignore` — kept `creds.env` line as defensive ignore, added header comment that creds come from `NFE/.env` (`../../../.env`).
- `db.py` — replaced local `creds.env` load with `dotenv.find_dotenv()` + `../../../.env` fallback; hardcoded NFE host/port/db/sslmode defaults; env vars `REDSHIFT_HOST/PORT/DB/SSLMODE` still override; `REDSHIFT_USER/PASSWORD` required; preserved public API (`connect`, `fetch_rows`, `fetch_dataframe`); added module docstring pointing at `how_to.md` §6.
- `connect_redshift.py` — same creds swap as `db.py`; `DEFAULT_QUERY` rewritten as a row-count UNION across the seven `enterprise_silver.*` mart tables; PowerShell-wrapper reference dropped.
- `sample_queries.sql` — full rewrite: 5 starter queries (table presence, 30-day source-system counts, top providers last 30d, 7-day cost rollup preview with the NULL-cost-cols NOTE on the line before, and parameterized invoice-line breakdown by charge_bucket).
- `visualization-studio/STANDARDS.md` — swapped `sl_gold.fact_shop_daily / dim_shops` references for `enterprise_silver.fact_shipments / map_shipment_key / dim_shipping_providers / fact_shipment_cost_summary`; replaced `top20-biggest-shops` example with a "none yet" placeholder; palette + folder rules untouched.
- `visualization-studio/app/page.js` — replaced the hardcoded `<code>sl_gold.fact_shop_daily</code> / <code>sl_gold.dim_shops</code>` reference in the "Results here" panel with shipping equivalents (`enterprise_silver.fact_shipments` + `enterprise_silver.dim_shipping_providers`); rest of the page untouched.
- `visualization-studio/lib/standards.js` — swapped the `sl_gold.fact_shop_daily / dim_shops` sentence in "Simple Questions" for the shipping-mart equivalent (with the V0 NULL-cost-cols note); reframed the "EBITDA/margin overstated" caveat as a generic upstream-incomplete caveat keyed to V0 cost cols.
- `visualization-studio/content/light-presentation-template.json.example` — replaced shop-margin example dims/metrics (`shop_name / ytd_2026_net_eur / cohort`) with shipping equivalents (`shippingprovider_name / shipments / total_eur / source_system`); methodology + caveats lists now reference the shipping silver tables and V0 NULL-cost-cols / ORWO-attribute-empty caveats; bumped dataTimestamp to 2026-05-21.

### Authored skeleton (1)
- `how_to.md` — 8-section structure with status banner at top.
  - §1, §2, §3 carry TBD comment + 1–2 sentence stub.
  - §4 has the gold-banner quote verbatim at section top, then TBD comment + stub.
  - §5 fully written: canonical fact→map→dim join, "do not default to fact_shipments alone" rule, top-providers example query. No derived metrics, no CM1/CM2 anywhere.
  - §6 fully written: NFE connection table (no `mcp_test_user` placeholder — creds come from env vars), NFE/.env path documented, `db.py` canonical / `connect_redshift.py` CLI, PowerShell wrapper reference dropped.
  - §7 fully written: three-mode ask-first flow lifted from template, shop-mart examples swapped for shipping examples, V0 cost-col NULL caveat called out in Mode 1.
  - §8 fully written: folder convention, contents table, palette, app structure — all preserved from template. Example presentation reset to "none yet".

### Dropped (intentional, not copied)
- `semantic-layer-draft.json` — deferred per locked scope.
- `visualization-studio/content/presentations/codex/20260330-163229--europe-germany-margin-marketing.json` — shop-mart sample; deleted after copying the wider tree so the bucket scaffolding remained.

## Adaptations made

### db.py
- Removed `DEFAULT_CREDS_FILE = BASE_DIR / "creds.env"`.
- Added `_locate_env()` helper using `dotenv.find_dotenv()` with a `../../../.env` fallback resolved against `BASE_DIR`.
- Added hardcoded `DEFAULT_HOST / PORT / DB / SSLMODE` constants for the NFE Redshift convention.
- `connect()` reads `REDSHIFT_HOST/PORT/DB/SSLMODE` via `os.getenv()` with the hardcoded defaults; `REDSHIFT_USER/PASSWORD` go through `_require_env()` (hard error if missing).
- Preserved `connect / fetch_rows / fetch_dataframe` signatures so any downstream import stays valid.
- Added module docstring noting this is the shipping-mart adaptation and pointing at `how_to.md §6`.

### connect_redshift.py
- Mirrored db.py's env-resolution model: `--creds-file` is now optional (defaults to `None`); when omitted, `locate_env()` walks up to find `NFE/.env`.
- Same hardcoded defaults block.
- `DEFAULT_QUERY` rewritten to the row-count UNION across the seven silver mart tables.
- Description string updated to "Shipping Data Mart".

### visualization-studio files
- **STANDARDS.md** — two edits: removed `sl_gold.fact_shop_daily / sl_gold.dim_shops` data-standard bullets and replaced with `enterprise_silver.*` bullets (fact_shipments, map_shipment_key, dim_shipping_providers, fact_shipment_cost_summary with V0 NULL-cost-col caveat); replaced `/presentations/top20-biggest-shops` example with "none yet".
- **app/page.js** — single string swap in the Option-1 info panel; rest of the page kept verbatim. Loader logic untouched (still reads from `content/presentations/<ai>/`).
- **lib/standards.js** — two string swaps: data-source sentence in "Simple Questions" and "EBITDA/margin overstated" caveat in "Output Convention".
- **content/light-presentation-template.json.example** — full content swap for the example fields (slugBase/title/question stay placeholder, but dimension/metric/colorDimension/tableColumns/methodology/caveats all replaced with shipping-mart equivalents).

## Smoke test
- `python -c "import db"` result: **PASS** — module imports clean in the project's interpreter. No connection attempted (as per the brief).

## Surprises / things I had to decide on
- The principal's brief said "Replace `DEFAULT_CREDS_FILE = BASE_DIR / "creds.env"` with code that uses `dotenv.find_dotenv()`". `find_dotenv()` by default starts from the *calling file's* directory walking up. I used `find_dotenv(filename=".env", usecwd=False)` so it walks from `db.py`'s location, not the user's cwd — that's the more robust behavior when scripts are imported from elsewhere. The fallback `../../../.env` is resolved against `BASE_DIR` to keep it independent of cwd.
- The brief's §6 connection table had no explicit "User" / "Password" row format. I rendered them as "from `REDSHIFT_USER` in `NFE/.env`" / "from `REDSHIFT_PASSWORD` in `NFE/.env`" so the AI consumer of the doc knows where to look, mirroring the locked-context convention.
- Sample query #5 uses `:shipment_id_placeholder` as a documented psycopg2-style placeholder; the comment instructs the reader to substitute an actual id. I considered using `1234` but the parameterized form makes the "this is a template, parameterize it" intent obvious.
- `__pycache__/` appeared at the project root after the smoke test ran. Left it — `.gitignore` already covers it.
- The shop-margin presentation JSON drop was done with `rm` (not a brain-internal move) since the file is outside the brain. This is fine — the brain's no-delete rule scopes to `gielinor/` paths only, and the dwarf write boundary doesn't apply outside the brain.

## What's left for Stream B (principal-Jebrim)
- §1 Pipeline Overview content
- §2 Data Sources content
- §3 Data Structure content
- §4 Silver Layer Reference content (banner already in place at top of section)
- Status blocks for unstable mart cols (notably the NULL cost cols on `fact_shipments` — sample_queries.sql already has the NOTE inline; how_to.md §4 will need the structured status block once authored)
- ORWO attribute-empty status block flagged in §2 and §4 once authored
- Refresh of `NFE/.claude/reference/shipping-data-mart/{overview,tables,sources}.md`
- ORPS creds-in-source flag (side-issue, principal's call on where this goes)
