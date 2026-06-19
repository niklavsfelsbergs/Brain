# Redshift MCP: multi-reference CTE -> "transaction is read-only"

**Source:** [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]] continuation (sid 64902bef, 2026-06-18). Two read-only acceptance queries
against the live mart failed with `Error: transaction is read-only` even though they were pure
`SELECT`s. The common factor: a `WITH` CTE **referenced 2+ times** (`base` used by three later
CTEs; `boxrate_src` used by both `boxrate` and `boxrate_fam`).

**Mechanism (inferred, not isolated):** Redshift materializes a CTE that is referenced more than
once (its automatic CTE-materialization), which writes an internal temp table -- and the MCP's
read-only transaction rejects the write. A single-reference CTE, or independent inline subqueries,
stay non-materialized and run fine. This is the same family as the resume's existing "CTE-JOIN-of-
aggregates rejected" note, and consistent with the `CREATE TEMP TABLE` rejection (temps = writes
in a read-only txn).

**Fix that worked:** rewrite so **no CTE is referenced more than once** -- use independent inline
subqueries in `FROM`/`JOIN`, each scanning the base table fresh. Window functions
(`COUNT(*) OVER (...)`) are fine; they were NOT the cause (removing the window didn't help; removing
the CTE reuse did). The acceptance quota query went green once `base`/`boxrate_src` reuse was
unwound into self-contained subqueries.

**When it bites:** any read-only validation of mart logic that naturally wants a shared CTE
(calibrate-once-use-twice, a base filter feeding several aggregates). For production ETL SQL this
doesn't matter (it runs in a writable txn and uses real `CREATE TEMP TABLE`); it only constrains
**read-only MCP testing**. Test pattern: independent subqueries, accept the repeated base scans.

Belongs with the [[shipping-mart]] / [[bi-etl]] tooling notes; promote at alch into the redshift-MCP
quirks list alongside the reserved-alias / positional-GROUP-BY / STDDEV / SIMILAR-TO rejections.
