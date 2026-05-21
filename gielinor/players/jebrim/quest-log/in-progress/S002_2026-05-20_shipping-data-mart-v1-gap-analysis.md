# S002 — 2026-05-20 — Shipping Data Mart V1: gap analysis for ETL check-in

**Status:** in-progress
**Principal:** Niklavs (BI analyst, lead on Shipping Data Mart by shipping-domain specialty)
**Player:** Jebrim
**Born:** 2026-05-20 (scoping in S001 session); resumed 2026-05-21 for execution (S003 audit + synthesis); resumed again 2026-05-21 PM (S008) for principal-driven design challenges + ClickUp reopen.
**External actions:** all **completed**. 3 dwarf spawns (D1 ClickUp, D2 bi-etl, D3 Redshift) from S003. 2 ClickUp comments posted in S008: NGE-6129 sentat→order_produced_ts (id `90120220911315`), NGE-6127 reopen with ORWO mapping + repo gap (id `90120220913597`). Principal flipped NGE-6127 status manually. **No pending external actions.**

## The ask

V1 launch is 2 days out. Tomorrow morning Niklavs has an ETL-team check-in. Deliverable for that check-in: a gap-analysis brief + a task list (grouped by area, with estimated owner per task) covering:

1. What's open in ClickUp under epic NGE-6120 — ground truth on what the team is tracking.
2. What's actually in the mart right now — found by querying it directly via the redshift MCP.
3. What the bi-etl repo says is built — DAG code + per-table READMEs + `.html` open-pointer reports the engineers commit alongside.
4. Gaps **not yet ticketed** — issues surfaced by the redshift probe that nobody's caught.

Task list is **not** to be created in ClickUp yet — draft to chat, Niklavs triages, then he pushes.

## Where we are

S003 (audit session, earlier 2026-05-21): All three dwarves ran cleanly in parallel. D1 walked 93 ClickUp tickets; D2 scanned bi-etl at HEAD `c450d24fb`; D3 probed live `enterprise_silver.*`. Synthesis landed as HTML at `bank/notes/projects/shipping_data_mart_v1_gap_analysis.html`.

S008 (this session, 2026-05-21 PM): Principal-driven design challenges. Three threads opened and closed:
1. **ORWO `sentat` semantic.** Currently mapped to `received_by_carrier_ts`; should be `order_produced_ts` (direct equivalent of PCS `SHIPPING_TRACKED`). Posted to NGE-6129, tagged Satya. Pending Satya's call.
2. **NGE-6127 reopened.** Two gaps: (a) 30 ORWO extkeys NULL on all 4 enrichment columns; (b) the 285 existing PICT/PicaAPI/PCS classifications were applied directly to Redshift by hand and live nowhere in git. Proposed ORWO mapping in comment: DHL/UPS/POST/OTHER 4-bucket (DHL 70.8% / UPS 6.2% / POST 22.7% / OTHER 0.4% of ORWO `fact_shipments`). Awaiting principal decision on ad-hoc UPDATE vs CASE WHEN in `upsert_to_silver.sql` + the seed-file question.
3. **NEW thread: ORWO product SKU / article number missing.** Principal flagged this as the next investigation. Confirmed `revenue_eur` = NULL on all 89.6M ORWO orderitem rows + `product_key` = NULL on the same (`dw.dim_products` matches 0.02% — open follow-up #2 in NGE-6129 HTML). Glob found candidate sources in NFE: `bi-analytics-main/NFE/shipping_topics/29_ORWO_sperrgut_tcg_and_orwo_shops/sql/orwo_order_products.sql` (primary suspect) + `orwo_package_dims.sql` + `bi-analytics-main/NFE/shipping_topics/9_DHL_orwo_avg_costs/sql/orwo_calculated_cost.sql`. Principal believes the right PTS data source for ORWO products lives in this area and should expose product-level detail (kitchen calendars, etc.). **Not investigated yet — handover material for next session.**

Synthesis HTML at `bank/notes/projects/shipping_data_mart_v1_gap_analysis.html` is now slightly stale on two points — ORWO `received_by_carrier_ts` coverage (will flip from 99.9987% to 0% by design once the swap lands) and Area 9 should note the dim_shipping_providers repo gap. Patch on next pass.

Dwarf sibling files (`S002_d1_*.md`, `S002_d2_*.md`, `S002_d3_*.md`) remain in `quest-log/in-progress/` until this quest completes; they move with this file into `completed/` when we close out.

## Next concrete step — for next session

Three threads carry forward. Priority for next session (top first):

1. **ORWO product SKU investigation.** Read `bi-analytics-main/NFE/shipping_topics/29_ORWO_sperrgut_tcg_and_orwo_shops/sql/orwo_order_products.sql` first — likely the PTS-side source Niklavs used previously. Identify the actual ORWO product/article column + source table. Cross-reference against `dw.dim_products` schema to see whether the 0.02% match is a key-shape issue or a true catalog separation. Output: a 1-page note `bank/notes/projects/orwo_product_source.md` summarising where ORWO product data lives, how it keys, and what the dim_products extension path would look like. This feeds NGE-6129 follow-up #2 (Data Platform owns the dim extension; Jebrim provides the discovery).

2. **ORWO classification decision.** Principal returns with answer on (a) ad-hoc UPDATE vs (b) CASE WHEN in `upsert_to_silver.sql` for the 30 ORWO extkeys, and (c) whether to dump current dim contents to a versioned seed `.sql`. If (a) — Jebrim drafts the 30 UPDATEs. If (b) — Jebrim drafts the SQL patch + the one-time backfill. (c) is independent and almost certainly worth doing regardless.

3. **ETL check-in reconciliation** (originally the primary resume hook). Principal returns with what the team agreed on at the 2026-05-22 AM check-in. Update this entry with the agreed task list + assignments. Niklavs pushes the agreed tasks to ClickUp himself. Decide whether V1 ships with the carve-outs (Rewallution / SLA-breach / PCS timestamps / ORWO known-NULLs — see Area 9 in the HTML).

If V1 ships clean and all three threads close: move this quest to `completed/` (sibling dwarf files move with it). Otherwise retitle and keep in-progress.

## Files / paths to read first — for next session

1. **This file** — resume context.
2. `bank/notes/projects/shipping_data_mart_v1_gap_analysis.html` — the canonical synthesis. Open in browser; sticky-nav. Note the two stale spots above.
3. **For ORWO products thread (priority 1):** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\shipping_topics\29_ORWO_sperrgut_tcg_and_orwo_shops\sql\orwo_order_products.sql` + `orwo_package_dims.sql` + `bi-analytics-main\NFE\shipping_topics\9_DHL_orwo_avg_costs\sql\orwo_calculated_cost.sql`.
4. **For ORWO classification thread:** `bi-etl\dags\enterprise_silver\Shipping_Data_Mart\dim_shipping_providers\sql\upsert_to_silver.sql` + `README.md` in the same folder.
5. `quest-log/in-progress/S002_d1_clickup_subtree.md` / `S002_d2_bi_etl_state.md` / `S002_d3_redshift_coverage.md` — dwarf detail if a specific finding needs re-checking.
6. `players/jebrim/CLAUDE.md` + `_about.md` + `persona.md` — character context if respawn didn't preload.
7. `quest-log/in-progress/S001_2026-05-20_repo-orientation.md` — sibling. Picks #3/#4/#5 unresumed.

## Constraints (from principal, this session)

- **ORWO is required for V1.** Not an optional source. NGE-6129's 4 open ORWO follow-ups are V1-blocking material unless verified otherwise.
- **NGE-6120 is the V1 epic.** No sibling epics to widen to. Walk the subtask tree.
- **NFE planning docs are stale** — do not treat them as authority for project status. Specifically: `NFE/projects/1_shipping_data_mart/README.md`, `CLAUDE.md`, `next_session.md`, `investigation/investigation.md`, the data model doc. They reflect intent, not reality.
- **NFE `claude/reference/shipping-data-mart/`** — "a bit outdated, but a good map in general." Skim as a navigation index only. Not assigned to a dwarf — principal-Jebrim does this last as a sanity check.
- **bi-etl `main` is the source of truth on the implementation side.** `git pull origin main` before reading. The DAG code + READMEs carry the commentary.
- **Redshift MCP is connected** (config landed in `brain/.mcp.json` last session; this session's MCP probe confirmed it's available as `mcp__redshift__*`).
- **ClickUp MCP works.** Tested this session — `clickup_get_task`, `clickup_get_task_comments` return full payloads. **HTML attachments in comments are fetchable** via `WebFetch` on the attachment URL — no auth wall on `t9012440763.p.clickup-attachments.com`. Tested on `orwo_open_pointers.html` on NGE-6129; returned full content cleanly.
- **HTML pattern in the team:** engineers (Satya, Łukasz) attach `.html` "open pointers" reports to comments AND commit canonical copies into `bi-etl/dags/enterprise_silver/Shipping_Data_Mart/`. When both exist, **prefer the in-repo version** — the ticket attachment may be stale by a few commits.
- **Output grouping:** task list grouped **by area** with **estimated owner** per task. Not by owner.

## Dwarf plan — 3 dwarves, all Jebrim-inherited, parallel wave 1

Hook-enforced write boundary: `bank/notes/`, `quest-log/in-progress/`, `quest-log/completed/`, `inventory/`. No drafts. No spellbook/rituals. No sub-dwarf spawning.

Each dwarf writes its findings into this quest-log entry's folder under a per-dwarf section, OR — if size is an issue — into a sibling file under the same SNNN. Decide at spawn time based on expected output size; my bet is per-dwarf sibling files are cleaner.

Proposed sibling-file layout:

```
quest-log/in-progress/
  S002_2026-05-20_shipping-data-mart-v1-gap-analysis.md   ← this entry (synthesis lives here)
  S002_d1_clickup_subtree.md                              ← D1 output
  S002_d2_bi_etl_state.md                                 ← D2 output
  S002_d3_redshift_coverage.md                            ← D3 output
```

(Once V1 ships and we synthesize the gap doc into `bank/notes/projects/shipping_data_mart_v1_gap_analysis.md`, the dwarf sibling files move with the main entry into `completed/`.)

### D1 — NGE-6120 subtree mapper

**Reads:** ClickUp epic NGE-6120 + every subtask + every comment + every linked task. WebFetch any HTML attachments encountered; when a comment says a canonical version lives in the repo, flag the repo path and skip the attachment fetch (note the URL anyway).

**Deliverable** (`S002_d1_clickup_subtree.md`):

- Tree shape — epic → subtasks → (recurse).
- Per ticket: custom_id, name, status, assignees, due_date, priority, last-update date, blocking flags, attachment list (with URLs + canonical repo paths if known), linked-tasks list.
- For each ticket, a 2–4 line **state summary** drawn from the latest comments + description. Highlight: what's done, what's open, what's blocked, what's awaiting Niklavs.
- A **V1-relevance flag** per ticket: `V1-blocking` / `V1-followup` / `out-of-scope` / `unclear`. Bias toward `unclear` when uncertain — better to surface than to filter out.
- Explicit list of action items already assigned to Niklavs across the tree.

**Out of scope:** repo reads, redshift queries, NFE doc reads.

### D2 — bi-etl repo state scanner

**Reads:** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-etl\`. `git pull origin main` first (the mart moves fast on this side; stale checkout would mislead). Then walk both `dags/enterprise_silver/shipping_data_mart/` AND `dags/enterprise_silver/Shipping_Data_Mart/` (case variations seen in NGE-6129 comments — verify which is real). Also any sibling DAG dirs that feed into the 8 mart tables.

**Deliverable** (`S002_d2_bi_etl_state.md`):

- Per-table state matrix for the 8 mart tables (`map_shipment_key`, `fact_shipments`, `fact_shipment_orderitems`, `fact_shipment_invoice_lines`, `fact_shipment_cost_summary`, `fact_truck_charges`, `dim_shipping_providers`, `dim_carrier_sla`):
  - DAG file present? Last-modified commit + date + author.
  - SQL file(s) present? Last-modified commit.
  - README freshness — last commit + summary of what it says about V1 state.
  - `TODO` / `FIXME` / `HACK` / `XXX` markers in SQL + DAG code. Quote the comment + path:line.
  - Any `.html` files in the dir (open-pointer reports) — list them, summarize each briefly.
- Per source_system × table coverage as claimed by READMEs: Picturator / PicaAPI / PCS / Rewallution / ORWO — for each cell, does the README claim it's wired in?
- Recent commit log on the mart dirs (last 6 weeks) — grouped by ticket prefix where possible (commit messages use `(NGE-NNNN)/...` per the NGE-6129 pattern).
- Anything in the repo that looks abandoned / half-built (folders without DAGs, SQL files not referenced by any DAG, etc.).

**Out of scope:** ClickUp reads, redshift queries, NFE doc reads.

### D3 — Redshift coverage prober

**Reads:** Live `enterprise_silver.*` schema via `mcp__redshift__*` tools. Read-only.

**Deliverable** (`S002_d3_redshift_coverage.md`):

For each of the 8 mart tables:

- **Row count by `source_system`** (where the column exists) — Picturator / PicaAPI / PCS / Rewallution / ORWO.
- **Recency** — `MAX(loaded_at)` or equivalent column; if no such column, max of any date column.
- **% NULL on V1-critical columns** — at minimum: `shipment_id`, `cost_source`, `final_shipping_cost_eur`, `destination_country`, `weight_kg`, `received_by_carrier_ts`, `delivered_by_carrier_ts`, `revenue_eur`, `product_key`. Per source_system where applicable.
- **FK joinability** — `map_shipment_key` ↔ each fact, `dim_shipping_providers` ↔ `fact_shipments`, `dim_carrier_sla` joinability for SLA-breach calc.
- **Anomalies** — anything that breaks a V1 assumption. Examples: source_systems missing from a fact that should carry them, cost_source distributions that don't match expected (real/expected/avg), zero rows in a table that should have rows, suspiciously stale `MAX(loaded_at)`.
- **SLA-breach feasibility check** — can `sla_breach_flag` and `days_vs_sla` be computed at query time? Probe `dim_carrier_sla` for coverage.

Briefing note: per S001's quest log, baseline mart schemas are `enterprise_silver` (curated) with bronze at `enterprise_bronze`. `sl_gold` and `ol_gold` hold curated downstream. Source priority order (from NFE design but verified usable): `enterprise_silver` → `enterprise_bronze` → `poc_landing` → `dw` legacy.

**Out of scope:** ClickUp reads, repo reads, NFE doc reads. If something is found that needs ticket context to interpret, flag it; principal-Jebrim bridges it.

## Synthesis wave (principal-Jebrim, after dwarves return)

1. Read all three dwarf outputs.
2. Skim NFE `claude/reference/shipping-data-mart/` as a nav-only sanity check. Flag where its picture disagrees with the dwarves'.
3. Cross-check tickets-vs-reality. Specifically: any ticket claiming "done" that redshift disagrees with; any redshift anomaly with no ticket.
4. Build the V1 gap matrix:
   - Done & verified.
   - Done per ticket, unverified in mart.
   - In progress with named owner.
   - Blocked + on whom.
   - Open follow-ups (incl. NGE-6129's 4 — carrier classification, dim_products extension, destination_country, ORWO expected shipping cost).
   - **Surprises** — gaps the dwarves found that aren't ticketed.
5. Draft the task list grouped by area with estimated owner per task. Areas likely: spine (`map_shipment_key`), wide fact (`fact_shipments`), items fact, cost (`invoice_lines` + `cost_summary`), truck (`fact_truck_charges`), dims (`dim_shipping_providers` + `dim_carrier_sla`), SLA computation, source-system integration (ORWO closure), DQ + diagnostics, docs.
6. Draft both (gap matrix + task list) to chat. Niklavs approves. Then write to `bank/notes/projects/shipping_data_mart_v1_gap_analysis.md`.

Niklavs takes the task list into the ETL check-in. Whatever gets agreed in the check-in, he pushes to ClickUp himself afterward.

## Carry-forward from S001 (useful, not duplicated work)

- **Repo paths (verified):**
  - NFE: `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\`
  - bi-etl: `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-etl\`
  - bi-analytics (legacy sibling): `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics\`
- **Workflow conventions (still in force):**
  - Reads need no approval; writes do.
  - Drafts go to chat first; principal approves; only then write to `bank/notes/`.
  - bi-etl `git pull origin main` before any read.
- **The shipping data mart landing-note draft from S001** (under S001's "Pending drafts" section) is **superseded** by this quest's eventual output. Once `bank/notes/projects/shipping_data_mart_v1_gap_analysis.md` lands, S001's pending draft block can be cleared. Don't write the S001-era landing note as a separate file.

## Self-observation worth saving later

Without the principal's prompt, I would not have proposed dwarves on this scope. Default attack would have been serial (ClickUp → repo → redshift → synthesize, all in main context), which would have crushed the window and dragged wall-time.

The trigger I missed: **scope size × independent paths × wall-time pressure (V1 in 2 days)** is dwarf-shaped, every time. Worth a draft to `examine/drafts/` next session — observation-backed, specific.

Not drafting it this session because (a) close-session is firing, (b) the observation surfaces cleaner when re-evaluated against the actual dwarf-spawn execution next session — I'll know more about whether the cuts were right, and the draft can cite both moments.

## Turn log (history; reference only)

- T1: Address opens session, Jebrim active. Respawn ran. Surfaced S001's in-progress entry for reconciliation.
- T2: Principal redirected — new quest for Shipping Data Mart V1, ignore NFE planning docs, ground truth from ClickUp NGE-6120 + bi-etl + redshift MCP. Check-in tomorrow morning. Asked: can I read HTML in ClickUp?
- T3: Discussed scope, proposed attack order, asked 5 clarifying questions, flagged the HTML uncertainty pending capability test.
- T4: Principal pointed at NGE-6129 as a concrete example with an HTML attachment in comments.
- T5: Loaded ClickUp + WebFetch tool schemas. Pulled NGE-6129 task + 14 comments. Found `orwo_open_pointers.html` attachment URL. WebFetch'd it successfully — full content returned, no auth wall. Reported pattern (engineers commit canonical copies into bi-etl repo; ticket attachments may be stale). Bonus finding: NGE-6129 is fully merged across all 6 steps; 4 open ORWO follow-ups remain, 2 of which are Niklavs's.
- T6: Principal answered the 5 clarifying questions: ORWO required for V1, NGE-6120 is the epic, repo carries the commentary, bi-etl `main`, task list grouped by area + estimated owner. Asked the meta-question: "How will you do this? Its a lot of work. You will have to spawn dwarves. Would you have known that?"
- T7: Answered honestly — no, I'd have gone serial without the prompt. Proposed the 3-dwarf plan above. Asked for go-ahead.
- T8: Principal: "lets close the session and do this in a new spawn." Close-session ritual fires.
- T9 (2026-05-21): New spawn. Principal cues "lets get to the shipping data mart audit." Jebrim active. Read S001 + S002 for resume context. Spawning 3 Jebrim-inherited dwarves in parallel per S002 plan: D1 (ClickUp NGE-6120 subtree), D2 (bi-etl mart-dir scan), D3 (Redshift coverage probe). Each writes to its sibling file under `quest-log/in-progress/S002_dN_*.md`. Pending until dwarves return.
- T10 (2026-05-21): All three dwarves returned. D1 walked 93 tickets (16 V1-blocking, 18 V1-followup, 4 out-of-scope, 3 unclear). D2 confirmed 7 of 8 mart tables wired in repo; `dim_carrier_sla` absent. D3 confirmed 7 of 8 tables present + fresh in Redshift; SLA-breach not computable; ORWO 100% NULL on destination + delivered_ts + revenue; Rewallution structurally unusable; `fact_shipment_cost_summary` is wired and fresh but main README still calls it "v2 not built." Three dwarf spawns marked completed.
- T11 (2026-05-21): Synthesized the V1 gap matrix (sections A–F: Done & verified · Tickets vs reality · In progress + owner · Blocked · Open follow-ups · Surprises not ticketed) and the 12-area task list with estimated owners + severity flags. Drafted to chat.
- T12 (2026-05-21): Principal asked for HTML deliverable instead of `.md`. Wrote `bank/notes/projects/shipping_data_mart_v1_gap_analysis.html` — self-contained, sticky-nav, color-coded severity. Principal cued close.
- T13 (2026-05-21, close): Close-session ritual. Tightened resume sections. Surfaced one self-observation as `examine/drafts/` (dwarf-spawn heuristic; observation-backed by S002 scoping turn + this session's execution). SNNN = S003. Commit pending.
- T14 (2026-05-21, new session): Principal asked what's new on NGE-6129 + contents of `orwo_open_pointers.html`. Pulled live comments + WebFetch'd the canonical HTML (in-repo path claimed by D1 / Satya does not exist locally — only `orwo_integration_walkthrough.html` lives at `dags/enterprise_silver/Shipping_Data_Mart/`; the `orwo_open_pointers.html` Satya cited at commit `9af27d823` is not in git history under that path). Reported on the 4 open follow-ups + the bug-#3 resolution by Łukasz (`7e552464f`, NGE-7146, auto-deployed 2026-05-21 04:00 UTC).
- T15 (2026-05-21): Principal challenged the design: ORWO `sentat` being used as `received_by_carrier_ts` — should be `order_produced_ts` instead. Verified in `fact_shipments/sql/insert_to_silver.sql` L580, L919; confirmed semantic mismatch (PCS `SHIPPING_TRACKED` already maps to `order_produced_ts` per the same file's L7 glossary + L748 wiring). Drafted comment, principal approved, posted to NGE-6129 as comment id `90120220911315`. Tagged Satya. **Completed.** This is a new V1-blocking semantic correction not in the original S003 synthesis — propagate into the gap matrix on next pass (will flip ORWO `received_by_carrier_ts` coverage from "99.9987%" to "0% (by design)" in Area 9 of the HTML, and surface ORWO `order_produced_ts` as a new column to populate).
- T16 (2026-05-21): Asked about ORWO carriers in `dim_shipping_providers` + ORWO revenue. Confirmed via Redshift MCP (now loaded as `mcp__redshift__*`): 30 ORWO rows exist with all 4 enrichment columns NULL; `revenue_eur` 100% NULL on 89.6M ORWO orderitem rows. Read `dim_shipping_providers/sql/upsert_to_silver.sql` + README — design is INSERT-only with manual UPDATEs for enrichment per Niklavs 2026-05-04 call.
- T17 (2026-05-21): Principal proposed simplifying ORWO carriers to 4 groups (DHL / UPS / POST / OTHER). Pulled live per-extkey row counts from `fact_shipments` for ORWO. Built the mapping (15 POST extkeys, 4 DHL, 4 UPS, 7 OTHER); coverage breakdown DHL 70.8% / UPS 6.2% / POST 22.7% / OTHER 0.4%. DHL2 alone is 64.23% of all ORWO; top 6 extkeys carry ~96%. Five ambiguous extkeys flagged (FKBRING/FKBRINGPARCEL/CIRRO/WPOST3/WPOST4 → POST per best guess; GUELL/TD/UNITEDPRINT → OTHER; UNITEDPRINT may be a production-system code mis-routed into the carrier field — separate concern).
- T18 (2026-05-21): Principal asked why ad-hoc UPDATEs instead of SQL — challenged the existing design. Verified via Redshift: PICT 116/124, PicaAPI 88/89, PCS 81/83 classifications are filled in live, but `git log` shows only 2 commits ever to the dim_shipping_providers folder and only 1 `UPDATE enterprise_silver.dim_shipping_providers` in the entire bi-etl repo (README template line 171). **The 285 PICT/PicaAPI/PCS classification UPDATEs were applied directly to Redshift by hand and do not exist anywhere in version control.** This is a real process gap — surfaced to principal as "manual-in-table-and-undocumented-anywhere-in-git is worse than either pure option (all-in-SQL or all-hand-applied-with-seed-backup)."
- T19 (2026-05-21): Principal decided to reopen NGE-6127. Drafted comment covering both the ORWO classification gap + the version-control gap, with the proposed ORWO mapping table embedded (service_type=NULL, truck_provider=NULL, has_truck_cost=FALSE for all ORWO since ORWO uses PTSLive not PCS truck allocation). Principal approved. Posted to NGE-6127 as comment id `90120220913597`. **Completed.** Status not flipped from `production` → in-progress in this turn (comment-only); principal can flip via UI or ask in a follow-up.
