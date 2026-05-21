# S014-D3 — TTYD template structural map (2026-05-21)

> Dwarf scope: read-only walk of the TTYD-template tree, per-file action verdicts for adaptation to the Shipping Data Mart how-to artifact. Author: Jebrim-dwarf. Principal: Jebrim.

## Summary

**39 files** total in the template (38 content + 1 `.gitkeep`-flooded skeleton). The biggest single adaptation item is **`how_to.md` (283 lines)** — every one of its 8 sections carries shop-mart vocabulary that has to be re-keyed to shipping. Visualization-studio is structurally generic (only the Next.js Home page hard-codes `sl_gold.fact_shop_daily` / `sl_gold.dim_shops` references, and `STANDARDS.md` carries shop-mart language) — palette tokens, builder scripts, presentation loaders, and CSV parser are copy-as-is. Biggest unknown: **what the canonical shipping fact + dim tables actually look like in `enterprise_silver`** — D1 must surface that before `how_to.md` §4 can be authored. Secondary unknown: whether the visualizer's Home page (`app/page.js`) should be left referencing `sl_gold.*` examples, retargeted to silver shipping tables, or made generic.

## Template-tree shape

```
TTYD-template/
├── .claude/settings.local.json        # permissions sandbox
├── .gitignore
├── AGENTS.md  (Codex entry point)
├── CLAUDE.md  (Claude entry point)
├── GEMINI.md  (Gemini entry point)
├── GROK.md    (Grok entry point)
├── how_to.md                          # PRIMARY DOC — 283 lines, 8 sections
├── db.py                              # shared DB helper, reads creds.env
├── connect_redshift.py                # CLI runner, reads creds.env
├── build_light_html_presentation.py   # 502-line Plotly→HTML builder
├── create_timestamped_presentation.py # Next.js entry scaffolder
├── sample_queries.sql                 # 5 starter queries
├── semantic-layer-draft.json          # 349-line semantic contract draft
├── requirements.txt                   # psycopg2, dotenv, pandas, plotly
└── visualization-studio/              # Next.js 15 app + content scaffolds
```

## Top-level files

| Path | Size | Purpose | Verdict | Confidence | Notes |
|---|---|---|---|---|---|
| `.gitignore` | 10 lines | Standard ignores incl. `creds.env`, `node_modules`, `.next`, `.tmp/`, `.venv/` | **adapt** | high | Swap `creds.env` → `.env` (or keep both — `NFE/.env` lives outside this dir anyway, so the `creds.env` line can stay as defensive ignore but is no-op for shipping). |
| `.claude/settings.local.json` | 27 lines | Claude-Code permissions allow-list (python, git, gh, find, etc) | **copy-as-is** | high | No shipping-specific content. May want to add `Bash(powershell:*)` for our Windows-first ops, but that's a separate ticket. |
| `AGENTS.md` | 19 lines | Codex entry point — "read how_to.md first, store outputs under `codex/`" | **copy-as-is** | high | Per locked scope: all 4 AI entry files kept verbatim; only `how_to.md` carries shipping content. |
| `CLAUDE.md` | 19 lines | Claude entry point — same shape, `claude/` bucket | **copy-as-is** | high | Same as AGENTS.md but per-AI bucket name. |
| `GEMINI.md` | 19 lines | Gemini entry point | **copy-as-is** | high | Same shape. |
| `GROK.md` | 19 lines | Grok entry point | **copy-as-is** | high | Same shape. |
| `how_to.md` | 283 lines | THE deliverable | **adapt** | high | Section-by-section breakdown below. Major rewrite, not a search-and-replace. |
| `db.py` | 61 lines | Shared psycopg2 helper, `_ensure_env()` loads `BASE_DIR / "creds.env"`. Exposes `connect()`, `fetch_rows()`, `fetch_dataframe()` | **adapt** | high | Single swap: `DEFAULT_CREDS_FILE = BASE_DIR / "creds.env"` → point at `NFE/.env`. See adaptation notes below. |
| `connect_redshift.py` | 76 lines | CLI runner. Defaults to `creds.env`. `DEFAULT_QUERY` lists `sl_gold.dim_shops` + `sl_gold.fact_shop_daily` | **adapt** | high | Same creds path swap + change `DEFAULT_QUERY` to list shipping silver tables (e.g. `enterprise_silver.fact_shipment` — exact name TBD by D1). |
| `build_light_html_presentation.py` | 502 lines | Plotly→standalone-HTML builder. Reads JSON spec (primaryDimension, primaryMetric, secondaryMetric, colorDimension, topN, tableColumns, summaryStats, insights, methodology, caveats). Writes `index.html`, `bundle.json`, copied `data.csv`, `spec.json` into a timestamped bundle folder. Palette constants embedded at module top. | **copy-as-is** | high | Fully generic — no shop-mart logic. EUR formatter (`fmt_eur`) hard-codes "EUR" — may want to abstract for shipping cost currency, but EUR is fine for shipping costs too. Palette tokens already match what we want to keep. |
| `create_timestamped_presentation.py` | 80 lines | Scaffolds a Next.js presentation: copies metric/forecast CSVs into `content/generated/<ai>/<slug>/`, writes `content/presentations/<ai>/<slug>.json` from a template payload, stamps `slug`, `generatedOn`, `dataTimestamp` | **copy-as-is** | high | Generic. AI bucket whitelist `{claude, codex, gemini, grok}` already covers our four. |
| `sample_queries.sql` | 25 lines | 4 starter queries against `sl_gold.dim_shops` + `sl_gold.fact_shop_daily`. Contains a column-name bug — uses `order_count` and `"day"` while `how_to.md` documents `orders_count` and `created_date`. | **adapt** | high | Full rewrite. New queries hit `enterprise_silver.<shipment-table>`. List of needed queries: (1) table presence check, (2) preview shipment rows, (3) shipments-per-day in last 30d, (4) shipments-by-source/region/lane in last 30d, (5) cost-or-quantity rollup if available. Resolve column names from D1. |
| `semantic-layer-draft.json` | 349 lines | "Partial semantic layer" — declares `canonicalModel.grain = "shop x day"`, lists `primaryTables`, `joinPolicy` (shop+sourcecode), 8 dimensions, 13 base measures, 3 derived measures (marketing_costs, CM1, CM2), interpretation rules, data-quality caveats, gaps, next steps, 5 review questions for principal. Self-described as `status: "draft_for_review"`. | **defer** | high | Per locked scope — flag in shipping `how_to.md` as "semantic layer V1 follow-up". Schema captured below for future shipping authoring. Copy the file shape but blank the shipping-specific content, OR leave the shop version out and create a stub `shipping-semantic-layer-draft.json` later. Recommendation: don't copy this file at all on first pass — adds noise to the V0 deliverable. |
| `requirements.txt` | 4 lines | `psycopg2-binary`, `python-dotenv`, `pandas`, `plotly` | **copy-as-is** | high | Generic. Note: principal preference is polars; pandas stays because `build_light_html_presentation.py` is pandas-bound and locked-kept. Adding polars later as a parallel addition is fine but not required for V0. |

## visualization-studio/ tree

| Path | Size | Purpose | Verdict | Confidence | Notes |
|---|---|---|---|---|---|
| `STANDARDS.md` | 103 lines | Working rules for visual outputs. Hardcodes `sl_gold.fact_shop_daily`/`sl_gold.dim_shops` in the "Data standard" section (lines 134-140). Palette table verbatim from `globals.css`. References `build_light_html_presentation.py` and `db.py`. | **adapt** | high | Only the "Data standard" section needs swapping (`sl_gold.fact_shop_daily` → shipping silver fact name, `sl_gold.dim_shops` → shipping dim name if applicable). Palette + workflow rules + Plotly constants unchanged. |
| `jsconfig.json` | 5 lines | `baseUrl: "."` | **copy-as-is** | high | Generic. |
| `next.config.mjs` | 9 lines | Sets `outputFileTracingRoot` to repo root | **copy-as-is** | high | Generic. |
| `package.json` | 15 lines | `next 15.3.0`, `react 19.0.0`, scripts: `dev`/`build`/`start` each guarded by `ensure-dev-env.mjs` | **copy-as-is** | high | Generic. |
| `package-lock.json` | 899 lines | Lockfile | **copy-as-is** | high | Generic. Commit as-is so the same Next.js version pins for shipping. |
| `app/globals.css` | 218 lines | Canonical palette + layout primitives | **copy-as-is** | high | This is the palette source-of-truth. Tokens captured below. |
| `app/layout.js` | 12 lines | Root layout; metadata title "Visualization Studio" | **copy-as-is** | high | Could rename `metadata.title` to "Shipping Data Mart — Visualization Studio" — cosmetic, ask principal. Defaulting to copy-as-is. |
| `app/page.js` | 74 lines | Home page. Lists presentations via `loadPresentationIndex()`. **References `sl_gold.fact_shop_daily` and `sl_gold.dim_shops` in the "Option 1" copy block (lines 25-27).** | **adapt** | high | Only the inline `<code>` examples in the "Option 1" panel need swapping to shipping silver tables. Everything else (hero copy, three-option panels, presentation list) is generic. |
| `app/presentations/[slug]/page.js` | 0 lines counted (binary count off — file is ~280 lines, dynamic route renderer) | Dynamic presentation renderer; uses `loadPresentationBySlug`, `formatEur`, `formatPct`, `formatNumber`. | **copy-as-is** | high | Generic — renders whatever JSON spec is loaded. EUR formatter is fine for shipping cost numbers. |
| `app/standards/page.js` | 31 lines | Renders `standards` const from `lib/standards.js` as cards | **copy-as-is** | high | Generic shell — content lives in `lib/standards.js`. |
| `lib/csv.js` | 48 lines | Standalone CSV parser (handles quoted fields, numeric coercion) | **copy-as-is** | high | Generic. |
| `lib/presentation-loader.js` | 60 lines | Walks `content/presentations/` recursively, hydrates entries with metric+forecast CSVs from `content/generated/` | **copy-as-is** | high | Generic. AI-bucket-agnostic — walks all subdirs. |
| `lib/standards.js` | 50 lines | Hardcoded `standards` array rendered by `/standards`. Mentions `sl_gold.fact_shop_daily` + `sl_gold.dim_shops` in the "Simple Questions" bullets. | **adapt** | high | Two table-name swaps in lines 13-14. Otherwise generic. |
| `scripts/ensure-dev-env.mjs` | 31 lines | Auto-runs `npm install` if `node_modules` is missing | **copy-as-is** | high | Generic. |
| `content/light-presentation-template.json.example` | 62 lines | Example spec for `build_light_html_presentation.py`. Uses shop-mart field names (`shop_name`, `ytd_2026_net_eur`, `company`, `cohort`). | **adapt** | medium | Rewrite the example to a shipping-flavored shape: `primaryDimension: "lane"` or `"source_country"`, `primaryMetric: "shipments_count"` or `"shipping_cost_eur"`. Generic enough that this can be done without knowing the exact silver schema — exact field names TBD. |
| `content/_template.json.example` (under `content/presentations/`) | 32 lines | Next.js presentation JSON template with placeholder fields | **copy-as-is** | high | Placeholders are already generic ("Replace with…"). No shop-specific bleed. |
| `content/generated/.gitkeep` + per-AI .gitkeeps (5 files total) | 0 bytes | Folder placeholders | **copy-as-is** | high | Directory shape only. |
| `content/presentations/claude/.gitkeep` + codex/gemini/grok .gitkeeps (4 files) | 0 bytes | Folder placeholders | **copy-as-is** | high | Directory shape only. |
| `content/presentations/codex/20260330-163229--europe-germany-margin-marketing.json` | 137 lines | Real shop-mart sample presentation: ranks European/German shops by CM2 margin, includes a marketing-spend separate ranking. Heavy use of shop-mart business logic. | **drop** | high | This is a shop-mart artifact — should not ship with the shipping template. Replace later with a shipping seed presentation (e.g. "shipments-by-lane-last-30d") as a first authored output, but for V0 just drop. |

## how_to.md section-by-section

### §1 Pipeline Overview (lines 3-28)

- **Current content:** Frames the pipeline as "shop x day" grain. Lists business questions (revenue per shop, orders/items per shop, cost breakdown, shop classification, geo association). Names three layers (Bronze `enterprise_bronze`, Silver `enterprise_silver`, Gold `sl_gold`). Names active Gold outputs (`sl_gold.dim_shops`, `sl_gold.fact_shop_daily`). Legacy note about `revenue_shop_daily`.
- **Verdict:** **adapt** — full rewrite of the prose, same skeleton.
- **Swaps needed:**
  - "Shop Level pipeline" → "Shipping Data Mart"
  - Grain: `shop x day` → `1 row per shipment_id` (or whatever the principal-confirmed grain is — likely per-shipment, possibly with a shipment-day rollup)
  - Business questions: revenue/orders/items → shipments-per-period, shipping cost per shipment/lane, carrier mix, transit times, anomalies
  - Active outputs: drop `sl_gold.*` references; replace with `enterprise_silver.<shipment-fact-name>` plus any auxiliary silver tables
  - **Gold→Silver framing:** title the section "Pipeline Overview", drop the "Active Gold outputs" sub-header, and surface the principal's banner: *"V0 ships against `enterprise_silver`; a Gold-layer migration is a V1 finishing touch — naming TBD."*
  - Drop the legacy revenue_shop_daily note entirely.
- **Confidence:** high on skeleton, **medium** on the exact silver table name — that's a D1 deliverable.

### §2 Data Sources (lines 30-77)

- **Current content:** Lists revenue/order sources (Picturator, PicaAPI, ORWO, Sendmoments), static seed shops (MixPix etc.), excluded sources (MWS), shipping & logistics tables (provider invoice tables — DHL, UPS, FedEx, GLS, Yodel, USPS, DPD), material/labor cost sources (PCS production tables), marketing channels, payment providers, reference/enrichment, ingestion methods.
- **Verdict:** **adapt** — most of the *substance* changes; the section structure stays.
- **Swaps needed:**
  - Revenue/order sources → **shipment-source systems** (likely: Picturator shipping/tracking, PicaAPI shipping, PCS shipping/tracking, MixPix shipping, MWS shipping, Rewallution, Lillestoff — i.e. the same source matrix but the shipping-table cousins of each shop source)
  - "Static seed shops" subsection → drop or replace with "Static seed carriers" if applicable
  - **The shipping & logistics paragraph (lines 49-51) is actually the most useful — it already lists the provider invoice tables (DHL, UPS, FedEx, GLS, Yodel, USPS, DPD, others). For shipping mart, that paragraph becomes the primary content of §2, expanded.**
  - Drop material/labor/marketing/payment provider subsections entirely (out of scope for shipping mart)
  - Keep reference/enrichment (ECB currency rates) — shipping costs need EUR conversion too
  - Keep ingestion methods list verbatim — same patterns apply.
- **Confidence:** medium — exact list of shipping source tables needs D1 confirmation.

### §3 Data Structure (lines 79-109)

- **Current content:** Layered architecture (Bronze/Silver/Gold). Bronze examples: `enterprise_bronze.pict_shops`, `currency_rates`, shipping/marketing/payment tables. Silver: 8 listed tables feeding Gold (`enterprise_silver.revenues`, `order_costs`, `labour_costs_daily`, `marketing_costs`, etc.). Gold: 2 tables. Key transformation patterns: standardization, aggregation, business rules, fallback logic.
- **Verdict:** **adapt**
- **Swaps needed:**
  - Bronze examples → swap to shipping-relevant bronze tables (provider invoice tables, shipping/tracking tables per source)
  - Silver table list → **principal must confirm**: most likely just `enterprise_silver.<shipment-fact>` plus possibly `enterprise_silver.order_costs` (already exists in shop mart's list — shipping mart's own version of cost allocation)
  - Gold sub-header → renamed/dropped per the locked scope (Silver becomes the terminal layer with a Gold-V1 banner)
  - Key transformation patterns: keep the bullet shape; substance changes (standardization across carrier invoices, EUR conversion, lane normalization, fallback from invoice→expected→average cost — that fallback line already exists in shop mart and applies directly to shipping)
- **Confidence:** medium pending D1.

### §4 Gold Layer Reference (lines 111-166) — **rename to "Silver Layer Reference" per locked scope**

- **Current content:** Two table specs. `sl_gold.dim_shops` with 11 columns documented. `sl_gold.fact_shop_daily` with 19 columns documented including grain note ("Revenue is the spine"), interpretation notes ("All currency is EUR", "Cost data is left-joined", suspicious-zero-cost flag, B2B-marketing exception).
- **Verdict:** **adapt** — rewrite both tables for shipping silver. **Add the Gold-V1 banner here.**
- **Swaps needed:**
  - Section heading: "Gold Layer Reference" → **"Silver Layer Reference"** with a banner block: *"V0 of the Shipping Data Mart documents the silver-layer contract. A Gold-layer promotion (name TBD) is a V1 finishing touch."*
  - `sl_gold.dim_shops` → drop entirely OR replace with a shipping dimension (e.g. carriers, lanes, source-systems) — TBD
  - `sl_gold.fact_shop_daily` → `enterprise_silver.<shipment-fact>` with shipping-specific columns. Likely columns: `shipment_id`, `created_date`/`shipped_date`/`delivered_date`, `source_system`, `source_country`, `destination_country`, `carrier`, `service_level`, `weight`, `dimensions`, `expected_cost_eur`, `invoiced_cost_eur`, `final_cost_eur`, `tracking_status`, `_updated_at`
  - Interpretation notes: keep "All currency is EUR" and "Cost data is left-joined" verbatim; the suspicious-zero-cost flag adapts to "flag when invoice cost is missing and fallback used"; drop the B2B marketing exception.
- **Confidence:** medium-low on exact columns — D1 has to surface them.

### §5 Query Reference (lines 168-221)

- **Current content:** Canonical join rule (`shopname + sourcecode`, not IDs). Margin definitions (CM1, CM2 with formulas). "Profit" → CM2 interpretation rule. Example query (last-30-day shop revenue ranking). Good starting questions.
- **Verdict:** **adapt**
- **Swaps needed:**
  - Join rule: drop entirely if shipping mart has no dim table at V0 (single-table queries), OR replace with the shipping-mart join rule (e.g. shipment-fact ↔ carrier-dim or shipment-fact ↔ shop-dim if cross-mart joining is supported)
  - Margin definitions → drop entirely. **This is the biggest semantic delete in §5.** Shipping mart's analog is *cost-coverage metrics*: e.g. invoice vs expected variance, carrier-mix cost-per-shipment, lane-level avg cost. Principal should specify which derived metrics earn a slot.
  - "Profit" interpretation → drop, replace with a shipping-domain shorthand if one exists (e.g. "cost variance" = invoice - expected)
  - Example query → rewrite. Suggested shape: shipments-by-carrier-last-30d with avg cost and count.
  - Good starting questions → rewrite to shipping-domain (top carriers by volume, top lanes by cost burden, transit-time outliers, invoice-vs-expected variance trends)
- **Confidence:** medium — derived metric definitions are a principal call.

### §6 Connecting to Redshift (lines 223-271)

- **Current content:** Connection table (host, port, db, user, schemas), reference to `creds.env`, setup (`pip install -r requirements.txt`), usage commands for `connect_redshift.py`, Windows PowerShell note (`.\connect_redshift.ps1`), shared module section (`db.py`).
- **Verdict:** **adapt**
- **Swaps needed:**
  - Connection details: keep host/port/db/user (likely same Redshift cluster), swap `Schemas: sl_gold` → `Schemas: enterprise_silver` (or whatever schema houses shipping mart). **D4 will surface authoritative connection details.**
  - `Credentials are stored in creds.env` → `Credentials are stored in NFE/.env` (or whatever the principal-confirmed relative path resolves to)
  - Usage examples: keep the three commands shape; replace `sl_gold.dim_shops` example with a shipping table preview
  - PowerShell note: no `connect_redshift.ps1` exists in the template (verified by Glob). Either drop the line or **new-for-shipping** a `.ps1` wrapper. Principal preference TBD — Windows-first ops would favor authoring it.
  - `db.py` usage block: swap `sl_gold.dim_shops` example → shipping silver table name.
- **Confidence:** high on swap mechanics; medium on whether to author `connect_redshift.ps1`.

### §7 Output Modes and Visualization (lines 273-326)

- **Current content:** "Ask first" rule (3 output modes). Per-mode detailed instructions. References `build_light_html_presentation.py`, `create_timestamped_presentation.py`, `visualization-studio/content/generated/<ai>/`, `visualization-studio/content/presentations/<ai>/`. Link convention.
- **Verdict:** **copy-as-is** (almost)
- **Swaps needed:**
  - Line 291: "Flag suspicious zero-cost patterns (except marketing for B2B shops)" → "Flag suspicious zero-cost patterns when invoice cost is missing without fallback annotation" (or similar shipping-domain analog). Single sentence rewrite.
  - Everything else is mode-agnostic and stays.
- **Confidence:** high.

### §8 Artifact Rules (lines 329-401)

- **Current content:** One-folder-per-request rule. Standard folder contents table. Rules. Visual system palette table (verbatim from `globals.css`). App structure tree. `npm run dev` instruction. Example presentation reference (`/presentations/top20-biggest-shops`).
- **Verdict:** **copy-as-is** (almost)
- **Swaps needed:**
  - Line 400: example presentation `/presentations/top20-biggest-shops` → drop the line entirely OR replace with the first shipping seed presentation once one exists (e.g. `/presentations/shipments-by-lane-30d`). Locked scope drops the shop sample JSON, so this line has to drop too on V0.
- **Confidence:** high.

## db.py / connect_redshift.py adaptation notes

**db.py changes (3 edits):**
1. Line 23: `DEFAULT_CREDS_FILE = BASE_DIR / "creds.env"` → resolve to `NFE/.env`. Cleanest implementation:
   ```python
   DEFAULT_CREDS_FILE = (BASE_DIR / ".." / ".env").resolve()
   ```
   Assumes the shipping mart project lives one directory below `NFE/`. If it lives deeper, adjust the relative count, or use a more robust upward-walk (`Path.cwd().resolve()` with a `.env` discovery loop). **Principal call: do we want path-walking magic, or a hardcoded relative path? Hardcoded is simpler and matches the template's posture.**
2. Module docstring (lines 1-12): update the `fetch_dataframe` example to use a shipping silver table instead of `sl_gold.dim_shops`.
3. Optional polars accompaniment: add `import polars as pl` and a `fetch_polars(query)` helper. Not required for V0 — pandas pathway stays because `build_light_html_presentation.py` is pandas-bound. (Defer per locked scope.)

**connect_redshift.py changes (3 edits):**
1. Line 12: same creds-path swap as `db.py`.
2. Lines 13-19: `DEFAULT_QUERY` lists `sl_gold` tables → rewrite to list the shipping silver tables (e.g. `WHERE table_schema = 'enterprise_silver' AND table_name IN ('<shipment-fact>')`).
3. Line 27 (`--creds-file` default): pulls from new `DEFAULT_CREDS_FILE` automatically once line 12 is fixed.

**Env-var names assumed unchanged:** `REDSHIFT_HOST`, `REDSHIFT_PORT`, `REDSHIFT_DB`, `REDSHIFT_USER`, `REDSHIFT_PASSWORD`, `REDSHIFT_SSLMODE`. **D4 must verify `NFE/.env` uses these exact names** — if it uses `RS_HOST` or `DB_HOST` or anything else, `db.py` needs additional rewrites at the `_require_env(...)` calls.

## semantic-layer-draft.json schema capture (for future shipping authoring)

Top-level keys (order matters in the original):
- `version` — string, e.g. `"0.1-draft"`
- `status` — string, e.g. `"draft_for_review"`
- `purpose` — one-line string
- `repoRole` — object with `primaryAssessment`, `semanticLayerAssessment`, `notes[]`
- `canonicalModel` — object with `grain` (string), `currency` (string), `primarySchemas[]`, `primaryTables[]`
  - `primaryTables[]` element shape: `{name, role, grain, description}`
- `joinPolicy` — object with `defaultJoin` (`{factAlias, dimensionAlias, joinType, conditions[]}`), `doNotDefaultTo[]`, `reason`, `deduplicationRule`
- `dimensions[]` — element shape: `{name, source, businessMeaning, confidence?, reviewNeeded?}`
- `baseMeasures[]` — element shape: `{name, table, aggregation, type ("stored"/"modeled"), description}`
- `derivedMeasures[]` — element shape: `{name, aggregation, type ("modeled"), formula, description}`
- `interpretationRules[]` — element shape: `{rule}`
- `dataQualityCaveats[]` — element shape: `{issue, impact}`
- `answeringModes[]` — element shape: `{name, useWhen, requirements[]}` — three modes: `chat_result`, `lightweight_html_presentation`, `nextjs_presentation`
- `artifactPolicy` — object with `aiBuckets[]` and `rules[]`
- `semanticLayerGaps[]` — element shape: `{gap}`
- `recommendedNextSteps[]` — element shape: `{priority, action}`
- `reviewQuestions[]` — element shape: `{id, question}`
- `confidenceNotes[]` — array of strings

**Shipping-mart authoring will need:** grain decision (per-shipment vs shipment-day), join policy if dim tables exist, dimensions enumeration (carrier, lane, source/destination country, service_level, etc.), base measures (shipment_count, invoiced_cost_eur, expected_cost_eur, weight, etc.), derived measures (cost_variance_eur, avg_cost_per_shipment_eur, transit_days, etc.). Defer per locked scope; capture this structural map so V1 authoring is mechanical.

## visualization-studio palette tokens (verbatim from globals.css)

```css
:root {
  --bg: #09090b;
  --panel: rgba(20, 20, 22, 0.92);
  --panel-solid: #141416;
  --ink: #ececef;
  --muted: #a0a0a8;
  --accent: #93c5fd;
  --accent-soft: rgba(147, 197, 253, 0.14);
  --accent-2: #fde68a;
  --accent-green: #86efac;
  --accent-3: #c4b5fd;
  --line: rgba(255, 255, 255, 0.09);
  --shadow: 0 18px 42px rgba(0, 0, 0, 0.35);
}
```

Python Plotly constants (from `build_light_html_presentation.py` lines 19-27 and from `STANDARDS.md` lines 81-91):

```python
PLOT_BG    = "#141416"
PAPER_BG   = "rgba(0,0,0,0)"
TEXT       = "#ececef"
MUTED      = "#a0a0a8"
ACCENT     = "#93c5fd"   # primary / actual series (blue)
ACCENT_2   = "#fde68a"   # secondary / comparison (yellow)
ACCENT_3   = "#86efac"   # tertiary / positive (green) — note: STANDARDS.md calls this --accent-green; build_light_html_presentation.py reuses ACCENT_3 for both green and additional-accent slots
LINE       = "rgba(255,255,255,0.09)"
```

Background gradient (used in both Next.js body and embedded HTML hero):
```css
background:
  radial-gradient(circle at top left, rgba(147, 197, 253, 0.18), transparent 24%),
  radial-gradient(circle at bottom right, rgba(253, 230, 138, 0.14), transparent 28%),
  linear-gradient(180deg, #09090b 0%, #0f1013 100%);
```

Fonts: `Inter, "Segoe UI", Roboto, sans-serif` body; `"Cascadia Code", Consolas, monospace` code.

Chart color mapping (from STANDARDS.md lines 95-100):
- Primary/actual: `--accent` (blue)
- Secondary/comparison: `--accent-2` (yellow)
- Positive/tertiary: `--accent-green` (green)
- Axis/grid: `--line`
- Cutoff/reference: `rgba(255,255,255,0.25)` neutral gray, dashed

**Verdict:** keep verbatim. Only swap the document title (`metadata.title` in `layout.js`) if the principal wants the Studio rebranded for shipping.

## Files needing new-for-shipping authoring

1. **`how_to.md`** — full rewrite per §1-§8 plan above. **Primary deliverable.**
2. **`sample_queries.sql`** — full rewrite. Re-target to shipping silver tables. Fix the column-name bug while at it (`order_count` vs `orders_count`, `"day"` vs `created_date`) by simply not carrying those mistakes forward.
3. **`db.py`** — three edits (creds path, docstring example, optional polars helper).
4. **`connect_redshift.py`** — three edits (creds path, DEFAULT_QUERY, docstring).
5. **`visualization-studio/STANDARDS.md`** — swap the "Data standard" section's table references.
6. **`visualization-studio/app/page.js`** — swap the two `<code>` table references in the Option 1 panel.
7. **`visualization-studio/lib/standards.js`** — swap the two table references in the "Simple Questions" bullets.
8. **`visualization-studio/content/light-presentation-template.json.example`** — rewrite the placeholder field names to shipping-flavored examples.
9. **Optional/V1: `connect_redshift.ps1`** — Windows PowerShell wrapper if the principal wants it (template mentions it but doesn't ship it).
10. **Deferred: shipping `semantic-layer-draft.json`** — schema captured above; not authored in V0.
11. **Deferred: a first shipping seed presentation** under `visualization-studio/content/presentations/<ai>/` to replace the shop-mart Europe/Germany sample that's being dropped.

## Files to drop entirely

- `visualization-studio/content/presentations/codex/20260330-163229--europe-germany-margin-marketing.json` — shop-mart sample, no shipping analog at V0.
- `semantic-layer-draft.json` (the shop-mart version) — per locked scope, semantic layer is V1; don't ship the shop version. Recreate later from the captured schema above.

## Open questions for principal

1. **Shipping silver table name(s)** — what does the canonical shipping fact table get called? `enterprise_silver.fact_shipment`? `enterprise_silver.shipment_daily`? D1 is supposed to surface this; flagging here so the §3/§4 authoring isn't blocked at the last minute.
2. **Grain decision** — per-shipment row, or shipment-day rollup, or both? Affects §1 wording ("1 row per shipment_id" vs "1 row per shipment x day").
3. **Dim tables at V0** — does shipping mart have an `enterprise_silver.dim_carrier` (or `dim_lane`, `dim_source_system`)? If no dims at V0, §5's "join rule" subsection drops entirely. If dims exist, capture the canonical join.
4. **Derived metrics** — shop mart's CM1/CM2 are the centerpiece of §5. Shipping mart needs its own equivalent (cost variance? avg cost per shipment? transit-day buckets?). Principal call before §5 can be authored.
5. **NFE/.env env-var names** — does it use `REDSHIFT_HOST` etc. exactly, or different names? D4 territory; flagged so `db.py` adaptation doesn't ship broken.
6. **`connect_redshift.ps1`** — author a Windows PowerShell wrapper, or drop the reference from §6? Template mentions it without shipping it.
7. **Visualization Studio rebrand** — leave the title "Visualization Studio", or rename to "Shipping Data Mart — Visualization Studio"? Cosmetic; copy-as-is unless the principal wants otherwise.
8. **`requirements.txt` polars addition** — user-global preference is polars, but `build_light_html_presentation.py` is pandas-locked. Add polars as a parallel addition, or leave for later? Leaning leave-for-later; pandas stays as the rendering pipeline's dependency.
9. **Gold-layer V1 banner wording** — confirm the exact phrasing for the banner in §4. Suggested: *"V0 of the Shipping Data Mart documents the silver-layer contract. A Gold-layer promotion (name TBD) is a V1 finishing touch."* Principal-edit before shipping.

## Quest closure note

- Read-only walk completed. No writes outside this quest-log file. No drafts authored. No bank notes created.
- Returning to Jebrim-principal for synthesis. The map is structural and verdict-bearing; actual authoring of shipping `how_to.md` is the next quest, blocked on D1 (Redshift schema) and D4 (connection details).
