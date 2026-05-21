# S014-D4 — Connection harness audit (2026-05-21)

## Summary

The template harness (`db.py` + `connect_redshift.py`) is a clean psycopg2 + python-dotenv pattern that reads **five** Redshift settings from a `creds.env` sibling file: `REDSHIFT_HOST`, `REDSHIFT_PORT`, `REDSHIFT_DB`, `REDSHIFT_USER`, `REDSHIFT_PASSWORD` (plus optional `REDSHIFT_SSLMODE`, default `require`). The principal's `NFE/.env` (and repo-root `.env`) only carries `REDSHIFT_USER` and `REDSHIFT_PASSWORD` — host/port/db are not in the file. Existing NFE connection code (`SHIPPING-COSTS/shared/database/__init__.py`) hardcodes host/port/db and uses `redshift_connector`, not psycopg2. Easiest bridge: keep the template's psycopg2 path, point `load_dotenv()` at `NFE/.env`, and either (a) hardcode `REDSHIFT_HOST/PORT/DB` as constants in the adapted `db.py` (matching the NFE convention) or (b) extend `NFE/.env` with the three missing keys.

## Template harness

### db.py
- **Env vars expected:** `REDSHIFT_HOST`, `REDSHIFT_PORT`, `REDSHIFT_DB`, `REDSHIFT_USER`, `REDSHIFT_PASSWORD` (all required, raises `SystemExit` if missing); `REDSHIFT_SSLMODE` (optional, default `"require"`).
- **Hardcoded fallbacks:** none for the five required vars. Only `REDSHIFT_SSLMODE` has a default. Creds file path defaults to `BASE_DIR / "creds.env"` where `BASE_DIR = Path(__file__).resolve().parent`.
- **Connection shape:** `psycopg2.connect(host=..., port=..., dbname=..., user=..., password=..., sslmode=...)`. Standard kwargs, no DSN string.
- **Verbatim public API:**
  - `connect(creds_file: str | Path | None = None) -> psycopg2.extensions.connection` — opens a new connection. Module-level `_loaded` flag means `load_dotenv` only fires once unless a `creds_file` is explicitly passed (in which case it reloads each call). **One-shot connections, no pool.**
  - `fetch_rows(conn, query) -> list[dict]` — uses `conn.cursor()` context; returns rows as dicts keyed by `cur.description[i].name`.
  - `fetch_dataframe(query, conn=None) -> pd.DataFrame` — uses `pd.read_sql_query`. If `conn` is None, opens a fresh connection and **closes it** in a `finally`. If passed a `conn`, leaves it open.
- **Pandas, not polars** — `fetch_dataframe` returns `pd.DataFrame` and `requirements.txt` pins pandas, not polars. (Worth flagging to principal: brain global pref is polars.)

### connect_redshift.py
- **CLI args:**
  - `--creds-file <path>` (default `BASE_DIR / "creds.env"`).
  - `--query <inline SQL>`.
  - `--query-file <path to .sql>`.
  - Mutually exclusive: passing both raises `SystemExit("Use either --query or --query-file, not both.")`.
- **Default query (if neither flag given):** lists `sl_gold.dim_shops` and `sl_gold.fact_shop_daily` from `information_schema.tables`.
- **Behaviors:**
  - Loads `--creds-file` via `load_dotenv` (does NOT use `db.connect`; reimplements the connect block with its own `require_env` helper).
  - Prints results tab-separated: header row, then data rows, then `\nRows returned: N`. None values render as empty string.
  - Closes connection in `finally`.
  - Uses `cursor.description[i].name` (same psycopg2 column-meta access as `db.py`).
- **Note:** `connect_redshift.py` and `db.py` duplicate the connect-and-require-env logic. Adapting both means changing both, OR refactoring `connect_redshift.py` to import from `db.py` (out of scope but worth noting).

### requirements.txt
- `psycopg2-binary>=2.9.9,<3.0.0`
- `python-dotenv>=1.0.1,<2.0.0`
- `pandas>=2.2.3,<3.0.0`
- `plotly>=5.24.1,<6.0.0`

## NFE creds

### NFE/.env (`bi-analytics-main/NFE/.env`, 301 bytes, confirmed exists)
Key names present (values redacted):
- `REDSHIFT_USER`
- `REDSHIFT_PASSWORD`
- `ORACLE_USER`
- `ORACLE_PASSWORD`
- `ANTHROPIC_API_KEY`
- `TCGPT_USERNAME`
- `TCGPT_PASSWORD`

**Missing relative to template:** `REDSHIFT_HOST`, `REDSHIFT_PORT`, `REDSHIFT_DB`, `REDSHIFT_SSLMODE`.

### bi-analytics-main/.env (parent dir, exists)
This is a **template/placeholder file**, not a real creds file. Comment at top: *"Template — copy this to your analyst folder (e.g. NFE/.env) and fill in your credentials. Do NOT put real credentials here."* All values are empty strings. Key names:
- `REDSHIFT_USER`
- `REDSHIFT_PASSWORD`
- `ORACLE_USER`
- `ORACLE_PASSWORD`

Same gap — no host/port/db keys defined as standard.

### bi-analytics-main/NFE/.env.example
**Does not exist.** No `.env.example` anywhere in `NFE/`. The repo-root `.env` (above) effectively serves as the example.

## NFE existing connection pattern

- **Example file (canonical):** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\SHIPPING-COSTS\shared\database\__init__.py`
- **Library used:** `redshift_connector` (not psycopg2).
- **Loading pattern:** **Hardcoded** host/port/db/user as module-level constants; password from a `pass.txt` file in the same directory (one secret per line, first non-empty wins). **Does not use python-dotenv.** Does not read `REDSHIFT_*` env vars at all.
- **Connection-block snippet (values shown as constants because they are hardcoded in the source, not env vars — password reading shown abstractly):**
  ```python
  import redshift_connector
  from pathlib import Path
  from typing import Optional

  HOST = "bi.c5lrs7vtwcpl.eu-central-1.redshift.amazonaws.com"
  PORT = 5439
  DBNAME = "bi_stage_dev"
  USER = "tcg_nfe"

  _connection: Optional[redshift_connector.Connection] = None

  def _read_password() -> str:
      path = Path(__file__).parent / "pass.txt"
      # reads first non-empty line from pass.txt
      ...

  def get_connection(force_new: bool = False) -> redshift_connector.Connection:
      global _connection
      if _connection is not None and not force_new:
          return _connection
      _connection = redshift_connector.connect(
          host=HOST,
          database=DBNAME,
          port=PORT,
          user=USER,
          password=_read_password(),
      )
      return _connection
  ```
- **Module-level cached connection** (`_connection` global) — reused across calls. Different from template's one-shot connections. Has `close_connection()` helper.
- **Higher-level helpers exposed:** `pull_data(query, as_polars=True)`, `execute_query(query, commit=True)`, `push_data(df, table_name, if_exists=...)`. Polars-first.
- **Other NFE Python that touches DB directly** — `NFE/projects/1_shipping_data_mart/investigation/ORPS_sources/pull_samples.py` and `_probe.py` — connects to **ORPS Postgres (not Redshift)** with a fully hardcoded DSN string (host, user, password all in source). Not a credential pattern to follow; flagged below.

**Takeaway:** there is no single canonical NFE Redshift-connection helper at `NFE/lib/`. The SHIPPING-COSTS module is the closest thing to a reference pattern, and it diverges from the template on three axes: library (`redshift_connector` vs `psycopg2`), credential storage (`pass.txt` vs dotenv), and config locality (hardcoded constants vs env vars).

## .gitignore status

- **Template `.gitignore`** (`NFE/projects/3_shipping_data_mart_TTYD/TTYD-template/.gitignore`): contains `creds.env` explicitly. Does NOT list `.env` — but the template never reads a file named `.env`, only `creds.env`.
- **NFE `.gitignore`**: does not exist as a separate file. NFE inherits from the repo-root `.gitignore`.
- **Repo-root `.gitignore`** (`bi-analytics-main/.gitignore`): contains `.env` under a `# Secrets` section (line 28). Also ignores `pass.txt` (line 27). Covers the whole tree including `NFE/`.
- **Confirmed safe:** any file named `.env` anywhere in the repo is gitignored. `creds.env` inside the template is gitignored locally. `pass.txt` (SHIPPING-COSTS pattern) also gitignored.

## Adaptation plan for db.py

1. **Resolve creds path.** Change `DEFAULT_CREDS_FILE` from `BASE_DIR / "creds.env"` (sibling to `db.py`) to point at `NFE/.env`. Two options:
   - **Relative walk-up:** find the nearest `.env` ancestor of `db.py` (a `find_dotenv()` from python-dotenv would do this, or a manual walk to the project root marker). This is what the repo-root template `.env` comment implies ("database modules search for .env upward from cwd"). Robust to where the script is invoked from.
   - **Explicit constant:** `DEFAULT_CREDS_FILE = Path(__file__).resolve().parents[N] / "NFE" / ".env"` — fragile if the template is copied elsewhere.
   - Recommend option (a) using `find_dotenv` so the harness travels with the principal's repo layout.
2. **Cover the four missing env keys.** `NFE/.env` lacks `REDSHIFT_HOST`, `REDSHIFT_PORT`, `REDSHIFT_DB`, `REDSHIFT_SSLMODE`. Two options:
   - **Add them to `NFE/.env`.** Cleanest, keeps `db.py` env-driven. Values come from SHIPPING-COSTS constants — host `bi.c5lrs7vtwcpl.eu-central-1.redshift.amazonaws.com`, port `5439`, db `bi_stage_dev`. Requires a tiny doc update in the template README.
   - **Hardcode HOST/PORT/DB in `db.py` and only require USER/PASSWORD from env.** Matches the NFE pattern in SHIPPING-COSTS, so it'll feel native to the analyst. Drops three `_require_env` calls.
   - Recommend the hardcode (option b) for the AI-facing how-to artifact — fewer env keys for the AI to discover, mirrors the prevailing in-house convention.
3. **Confirm library: psycopg2 stays.** Template already pins `psycopg2-binary`. NFE's SHIPPING-COSTS uses `redshift_connector`, but switching libraries is out of scope and would change the public API surface (cursor description shape, error types). Stick with psycopg2 unless principal wants alignment.
4. **Public API unchanged.** `connect()`, `fetch_rows()`, `fetch_dataframe()` signatures stay the same; only the body of `connect()` changes. Backwards-compatible.
5. **Optional: consider polars.** `fetch_dataframe` currently returns `pd.DataFrame`. Brain global pref is polars. Add a `fetch_polars(query) -> pl.DataFrame` sibling (or change the default), and keep `fetch_dataframe` for pandas-only consumers. Flag to principal — not a blocking change.

## Adaptation plan for connect_redshift.py

1. **Same creds-path swap as `db.py`.** Change `DEFAULT_CREDS_FILE` to resolve to `NFE/.env` (via `find_dotenv` or constant).
2. **Refactor to import from `db.py`.** Replace the local `require_env` + `psycopg2.connect(...)` block with `from db import connect; connection = connect(args.creds_file)`. Eliminates the duplication; one source of truth for connection logic.
3. **Default query.** Currently probes `sl_gold.dim_shops` and `sl_gold.fact_shop_daily`. Confirm `sl_gold` is the right schema for the Shipping Data Mart in the principal's setup — if SHIPPING-COSTS uses `bi_stage_dev` as the DB, the schema name probably still applies, but worth double-checking against D1's output.
4. **Keep CLI surface identical.** `--creds-file`, `--query`, `--query-file` stay. Output format (tab-separated) stays.

## Risks / surprises

- **No NFE-wide canonical Redshift helper.** I expected one under `NFE/lib/` but it's only `analysis.py`, `docs.py`, `quality.py`, `report.py`, `style.py`, `templates/` — no DB helper. The closest reference is buried in `NFE/SHIPPING-COSTS/shared/database/__init__.py`, a migrated standalone repo. If the principal eventually wants a unified NFE connection layer, the TTYD template's `db.py` could become it.
- **Two parallel credential patterns in NFE.** dotenv (`.env`) for new code, `pass.txt` for SHIPPING-COSTS. Both are gitignored. The adapted `db.py` will introduce dotenv to NFE proper for Redshift for the first time — minor inconsistency the principal should be aware of.
- **ORPS investigation scripts hardcode full Postgres DSN string (including password) in source.** Files: `NFE/projects/1_shipping_data_mart/investigation/ORPS_sources/{pull_samples.py,_probe.py}`. Not the template's problem and out of scope, but the password is committed-to-disk-in-cleartext-shaped (whether the file is gitignored or not — I did not verify the commit history). Worth surfacing to principal as a separate concern. **I did not include the actual DSN here, but the file paths above will let principal find it.**
- **Library mismatch.** `psycopg2` vs `redshift_connector`. They handle Redshift's flavor of Postgres differently (e.g., result paging, prepared statements, cursor `.description` shape). Code calling `cur.description[i].name` works in both, but consumers downstream of `fetch_rows` may have library-specific assumptions if they were copy-pasted from SHIPPING-COSTS.
- **Module-level dotenv caching (`_loaded` flag in `db.py`).** If `connect()` is called once without a `creds_file`, then later with one, the second call DOES reload — but if called once with explicit `creds_file=path_A` then again with `creds_file=path_B`, dotenv merges into `os.environ` and `path_A` keys may leak. Probably a non-issue for the single-creds-file Shipping Data Mart use case, but worth knowing.
- **Pandas vs polars.** Template returns pandas; user preference is polars. Not blocking but worth surfacing in the AI-facing artifact.
- **No `.env.example` in NFE.** Means the AI-facing artifact will need to spell out the key names (and which are required) verbatim, since there's no template file the AI can crib from.
