---
quest: S124_shipping-agent-report
sid8: 28d1f778
ts: 2026-06-01 22:40
open_dep: build incomplete — analyst skill + report builder §1-§5 + DQ canary not yet built
---

# Resume — Shipping Agent Report

**Status:** in-progress — design locked, **build underway**. Grounding done; project scaffolded; snapshot spine + diff harness built & verified. Report builder + skill remain.

## Where we are

The senior-analyst shipping report (design in S124 quest-log Session-2). This session (28d1f778) did the build's foundation: pushed the per-carrier refund map to the shipping-agent, ran the full grounding pass, and scaffolded + proved the data spine.

**Live, on disk in `bi-analytics-main/NFE/projects/4_automated_shipping_report/` (committed + pushed, `a632653`):**
- `lib/db.py` — full-access `tcg_nfe` connection (gold default, raw reachable for §5).
- `sql/snapshot.sql` — 25-col per-shipment snapshot (gold `shipping_mart`, `shop_order_created_date` anchor, `{window_days}` param).
- `lib/pull_snapshot.py` — polars+connectorx puller (`protocol="cursor"`). First snapshot proven: **1.94M rows, 49 MB/day**.
- `lib/diff_snapshots.py` — T-1→T event taxonomy, **verified** (self-diff=0 + synthetic positive test).
- `notebook/running-notebook.md` — seeded "what's normal" (baselines + accepted states).
- `README.md`. (Snapshot parquets are gitignored.)

## Next concrete step

1. **Draft the analyst skill** → `players/jebrim/spellbook/drafts/skills/` — the weekly/daily playbook (snapshot cols, diff logic, noticing checklist, §1–§5 scaffold, scope gating, running-notebook discipline). The durable artifact.
2. **Report builder §1–§5** + the **daily DQ canary** (zero-row segment = silent load fail, coverage regress, null spikes) in the project `lib/`.
3. **Retention/thinning** — 49 MB/day ≈ 18 GB/yr if all kept → keep ~30 daily, thin to weekly.
4. **Real diff test** needs a 2nd daily snapshot (run `pull_snapshot.py` on a later day, then `diff_snapshots.py --prev … --curr …`).

## Files / paths to read first

- `gielinor/players/jebrim/quest-log/in-progress/S124_61d62e21_shipping-agent-report.md` — full design (Session-2) + this session's build log (Session-3).
- `bi-analytics-main/NFE/projects/4_automated_shipping_report/` — README, lib/, sql/, notebook/.
- `shipping-agent/reference/known-dq.md` → "Refund / credit location by carrier" (the map taught this session).

## Gotchas (carried)

- Redshift **MCP validator** rejects `DATEADD`/`CURRENT_DATE` → use literal dates (real Redshift via connectorx is fine).
- connectorx on Redshift needs `protocol="cursor"` (default `COPY (SELECT…)` is rejected).
- Cast EUR Decimal cols to Float64 before ratio/delta math (Decimal scale overflow).
- Don't infer row-existence from nullable business cols (uncosted rows have NULL cost_source) — use explicit presence flags in the diff.

## Pending drafts

None held in chat. 1 examine harvest draft written this session (diff-verification + existence-flag lesson).
