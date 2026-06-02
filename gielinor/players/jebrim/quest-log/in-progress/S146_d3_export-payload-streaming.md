# [[S146_f20d7744_scm-serving-memory-review|S146]] · D3 — Export / large-payload / streaming memory review (SCM serving node)

**Player:** Jebrim · **Role:** read-only review dwarf · **Date:** 2026-06-02
**App:** `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs` (Next.js, EKS pod, **512MB Node heap**, OOM + intermittent 502s)
**Scope (D3):** large-payload construction, response streaming, CSV/export memory — server and client.

Sibling dwarves cover db.ts internals (D1) and the full route scan (D2). This entry is the export/payload-heap slice only.

---

## TL;DR — the single biggest heap bomb

**`/api/export` (`src/app/api/export/route.ts:136-140`) is the dominant single-request OOM risk.** A multi-month, all-carrier export materializes the **entire per-shipment filtered set** into a JS array, then builds the **entire CSV as one string**, then buffers it into **one `NextResponse`** — and en route `rawQuery` **stuffs that same giant array into the 60s query cache**. Three full copies of a multi-million-row payload co-resident in a 512MB heap. One such request can OOM the pod on its own.

Second-worst: **`/api/outliers` (`route.ts:114`)** — also per-shipment, **no LIMIT**, also cached, and additionally **held in client React state**.

---

## Findings

### F1 — CRITICAL · `/api/export` per-shipment SELECT with NO LIMIT → full array in heap
**`src/app/api/export/route.ts:134-136`**

```
const sql = `SELECT ${SELECT_LIST} FROM ${processedPruned(dateFrom, dateTo)} WHERE ${where} ORDER BY order_date, tracking_number`;
const rows = await rawQuery<ExportRow>(sql, ...values);
```

- **Mechanism:** 13 columns per shipment, no `LIMIT`. With only `dateFrom`/`dateTo` supplied (all other filters optional), this is *every shipment in the range*. `c.all()` realizes the full result set into a JS array of plain objects.
- **Why it costs memory (quantified):** processed grain is per-shipment, mart ~13-18M rows. A single month is ~1-2M shipments; a quarter all-carrier is ~4-5M. Each `ExportRow` is a 13-field JS object — strings (tracking/order numbers, country, provider, package, shop, SOG, cost_source) dominate. Conservative **~250-400 bytes/row** as live V8 objects (object header + 13 slots + several heap strings). At **3M rows ≈ 0.9-1.2 GB just for `rows`** — already multiples of the 512MB heap before anything else. A 6-month export is fatal with certainty.
- **Concrete fix:**
  1. **Stream** the CSV via a `ReadableStream` `NextResponse` body. Fetch from DuckDB in chunks (`LIMIT/OFFSET` batches of ~50k, or `duckdb`'s streaming/arrow row-batch reader) and `controller.enqueue` each batch as CSV text — peak heap becomes one batch (~tens of MB), not the whole set.
  2. **Hard row cap** with explicit truncation: pre-count (`SELECT COUNT(*) ... WHERE ...`); if over a cap (e.g. 500k-1M), return **413** with a message ("range too large, narrow the filter") OR stream the cap'd set with a truncation header. Do not silently truncate.
  3. **Set `Cache-Control: no-store`** on the response and keep the underlying query off the shared cache (see F3).
- **Effort:** M (streaming rewrite + cap). The cap alone is S and stops the OOM today.

### F2 — CRITICAL · `rowsToCsv` builds the ENTIRE CSV string in memory (second full copy)
**`src/lib/csv.ts:28-39`** + **`route.ts:137`**

```
const body = rows.map((row) => columns.map(...).join(","));   // array of N strings
return [header, ...body].join("\n");                          // one giant string
```

- **Mechanism:** `rows.map(...)` allocates an **N-element array of per-row strings**, then `.join("\n")` allocates **one contiguous string** holding the whole CSV. Both live simultaneously with `rows` (F1) — and the final string is then handed to `NextResponse` which buffers it again for the socket.
- **Why it costs memory:** CSV text for 3M rows × ~120-180 bytes/line ≈ **400-550 MB** for the joined string alone, plus the transient per-row string array of similar size during the join. Stacked on F1's ~1 GB, this is **2-3 full materializations of the payload** co-resident. This is *the* mechanism that turns a large export into an OOM rather than just a slow request.
- **Concrete fix:** eliminate the whole-string build — emit CSV incrementally inside the F1 stream (a `rowsToCsvChunk(batch, columns)` that returns text for one batch, enqueued and released). The `downloadCsvBlob`/client `rowsToCsv` path (small table exports) can keep the in-memory helper; only the server `/api/export` path needs the streaming variant.
- **Effort:** M (folds into F1's streaming rewrite).

### F3 — CRITICAL · export rows also enter the 500-entry / 60s query cache (third copy, retained)
**`src/lib/db.ts:438-461`** (`rawQuery`) + **`route.ts:136`**

- **Mechanism:** `rawQuery` caches every non-DDL query. The export SQL is a plain `SELECT`, so after the query runs `setCache(ck, converted)` (`db.ts:459`) **stores the entire multi-million-row array in `queryCache` for 60s**. Unlike F1/F2 (freed after the response), this copy is *retained* — and `MAX_CACHE_ENTRIES = 500` means several large exports (or one export + normal dashboard traffic) keep multiple giant arrays alive at once. The LRU eviction (`db.ts:96-108`) only triggers at 500 *entries*, not by byte size, so it offers no protection against a few enormous entries.
- **Why it costs memory:** turns a transient spike into **sustained heap occupancy** — the 60s window overlaps subsequent requests, so a second export (or a breakdown query) lands on top of a still-cached multi-GB array. This is the mechanism most likely behind *intermittent* (not every-time) 502s: OOM only when a second heavy request arrives inside the 60s cache window.
- **Concrete fix:** add a `skipCache` path to `rawQuery` (the signature already special-cases DDL/`BD_CACHE` at `db.ts:447-451` — extend it with an explicit `opts.skipCache`) and call it from `/api/export` and `/api/outliers`. Per-shipment result sets must **never** be cached. Optionally also add a byte-size guard in `setCache` (skip caching arrays over ~N rows).
- **Effort:** S.

### F4 — HIGH · `/api/outliers` per-shipment SELECT, no LIMIT, cached, AND held client-side
**`src/app/api/outliers/route.ts:58-114`** (server) + **`src/components/OutliersTable.tsx:43-59`** (client)

- **Mechanism (server):** selects 9 columns per individual shipment where `cost_for_routing > p99.5`, `ORDER BY ... shipping_cost DESC`, **no LIMIT** (`route.ts:74,110`), through `rawQuery` → cached (`route.ts:114`).
- **Why it costs memory:** p99.5 is ~0.5% of shipments — but 0.5% of a multi-month all-carrier scan is still **tens of thousands to low-hundreds-of-thousands of rows**. Smaller than F1, but the same three-copy pattern (array + JSON serialization + cache entry). The `range` scope (`route.ts:86-110`) additionally runs `PERCENTILE_CONT` over the full range first — DuckDB-side, not heap, but heavy.
- **Mechanism (client):** `setRows(d.rows)` (`OutliersTable.tsx:51`) holds the **entire** unbounded array in React state; `maxPerProvider` slicing (`OutliersTable.tsx:69`) happens *after* the full set is in memory, so the cap is display-only and does not bound the payload or client heap. The whole array is also re-serialized for the CSV download (`OutliersTable.tsx:212`).
- **Concrete fix:** server — add a sane `LIMIT` (e.g. top 5-10k by cost) + 413/truncation note, and `skipCache`. Client — request the bounded set; the per-provider cap should be a server param, not a client `.slice`.
- **Effort:** S (LIMIT + skipCache server-side); M if pushing the per-provider cap to SQL.

### F5 — LOW · breakdown aggregate routes are bounded (no per-shipment materialization) — for the record
**`breakdown/route.ts`, `breakdown-sparklines/route.ts`, `breakdown-buckets/route.ts`, `breakdown-quota/route.ts`**

- All four return **aggregated** results: `GROUP BY` dimension value / month / period. Cardinality is bounded by distinct dimension members (countries × providers × packages × SOGs) and ≤~12 months — hundreds to low-thousands of rows, not per-shipment. These are **not** payload heap bombs.
- **Caveat (out of D3 scope, flag for D1/D2):** `breakdown/route.ts:113-126` `CREATE OR REPLACE TEMP TABLE bd_cache` materializes the filtered per-shipment set (15+ cols) **inside DuckDB** for the wide date window. That's DuckDB memory, not Node heap — but on a 512MB pod the DuckDB `:memory:` instance and Node share the container's RAM, so a wide `bd_cache` competes with Node heap for the same pod limit. Worth D1's eye; not a JS-array finding.
- **Effort:** n/a (no change recommended in D3 scope).

### F6 — LOW · client table-export buttons build full CSV string in browser — bounded by their data source
**`BreakdownTab.tsx:881`, `OutliersTable.tsx:212`, `Deviations/Shifts/Benchmarks/Completeness/etc.`**

- All use the in-memory `rowsToCsv` + `downloadCsvBlob` (`csv.ts:28,42`) — builds the full string + a `Blob` in browser memory. For the aggregate tables (breakdown, benchmarks, deviations) the source arrays are already bounded (F5), so this is fine. **Exception:** `OutliersTable` exports its unbounded `rows` (see F4) — that CSV/Blob can be large client-side, but the browser tab has far more headroom than the 512MB server pod, so it is not the 502 cause.
- The big `/api/export` download is a **navigation** (`CostTrend.tsx:566-572` and `CompletenessGrid.tsx` build a URL and trigger an `<a download>` click), so the browser streams it to disk — **not** held in client heap. Client side is not the OOM; the server `/api/export` is.
- **Effort:** n/a.

---

## Severity roll-up

| # | Route / file | Severity | Mechanism | Fix | Effort |
|---|---|---|---|---|---|
| F1 | export `route.ts:134-136` | **Critical** | per-shipment, no LIMIT, full JS array | stream + row cap + 413 | M (S for cap) |
| F2 | `csv.ts:28-39` + `route.ts:137` | **Critical** | whole CSV string in memory (2nd copy) | incremental CSV in stream | M |
| F3 | `db.ts:438-461` + `route.ts:136` | **Critical** | export array cached 60s (3rd, retained copy) | `skipCache` for export/outliers | S |
| F4 | outliers `route.ts:58-114` + `OutliersTable.tsx:43-69` | **High** | per-shipment, no LIMIT, cached, client-held | LIMIT + skipCache + server cap | S/M |
| F5 | breakdown-* routes | Low | aggregated, bounded (OK) | none | n/a |
| F6 | client `rowsToCsv`/Blob | Low | browser-side CSV build, bounded | none (export is navigation) | n/a |

**Single biggest single-request heap bomb:** `/api/export` over a multi-month all-carrier range — F1+F2+F3 compound into ~2-3× a multi-GB payload co-resident in a 512MB heap.

## Minimum change to stop the OOM today (no streaming rewrite)
1. `/api/export`: pre-`COUNT(*)`, **413 over ~500k rows** (F1 cap half).
2. `rawQuery` `skipCache` flag, used by export + outliers (F3).
3. `/api/outliers`: add `LIMIT` (F4 server half).

These three are all S-effort and remove the retained/compounded copies; the streaming `ReadableStream` rewrite (F1/F2 full) is the proper M-effort follow-up to lift the row cap.
