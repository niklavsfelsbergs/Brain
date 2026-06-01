---
quest: S124_shipping-agent-report
sid8: 45954b41
ts: 2026-06-01 22:55
open_dep: build incomplete — report builder §1-§5 + daily DQ canary + retention not yet built; analyst skill DRAFTED (awaits alching promotion)
---

# Resume — Shipping Agent Report

**Status:** in-progress — design locked, **build underway**. Foundation built & verified (prior session). Analyst skill drafted this session. Report builder + canary remain.

## Where we are

The senior-analyst shipping report (design in S124 quest-log Session-2). Foundation (Session-3, sid 28d1f778): NFE project scaffolded, snapshot spine PROVEN (1.94M rows, 49 MB/day), diff harness VERIFIED, refund map pushed. **This session (45954b41): drafted the analyst skill** — the durable playbook.

**Drafted this session:**
- `players/jebrim/spellbook/drafts/skills/running-the-automated-shipping-report.md` — the weekly/daily senior-analyst playbook (what-it-is, two streams, two-tier cadence, harness run + spine + diff taxonomy, segmentation, §1–§5 arc, DQ canary, notebook discipline, refund map, caveats). Awaits alching promotion to `spellbook/skills/`.

**Live, on disk in `bi-analytics-main/NFE/projects/4_automated_shipping_report/` (committed + pushed, `a632653`):**
- `lib/db.py`, `sql/snapshot.sql`, `lib/pull_snapshot.py`, `lib/diff_snapshots.py`, `notebook/running-notebook.md`, `README.md`. (Snapshot parquets gitignored.)

## Next concrete step

1. **Report builder §1–§5** + the **daily DQ canary** (zero-row segment = silent load fail, coverage regress by-carrier, null spikes, stale reload) in the project `lib/`. The skill is the contract — implement against it.
2. **Retention/thinning** — 49 MB/day ≈ 18 GB/yr if all kept → keep ~30 daily, thin to weekly.
3. **Real diff test** needs a 2nd daily snapshot (run `pull_snapshot.py` on a later day, then `diff_snapshots.py --prev … --curr …`).
4. **Triggering** — deferred (design the approach first).

## Files / paths to read first

- `gielinor/players/jebrim/quest-log/in-progress/S124_61d62e21_shipping-agent-report.md` — full design (Session-2) + build log (Sessions 3–4).
- `players/jebrim/spellbook/drafts/skills/running-the-automated-shipping-report.md` — the skill = the build contract.
- `bi-analytics-main/NFE/projects/4_automated_shipping_report/` — README, lib/, sql/, notebook/.
- `shipping-agent/reference/known-dq.md` → "Refund / credit location by carrier".

## Gotchas (carried)

- Project lives at `Documents/GitHub/bi-analytics-main/NFE/...` (one level up from brain), NOT under brain/.
- Redshift **MCP validator** rejects `DATEADD`/`CURRENT_DATE` → literal dates for MCP probes (real Redshift via connectorx/pull_snapshot.py is fine — snapshot.sql uses CURRENT_DATE correctly).
- connectorx on Redshift needs `protocol="cursor"`.
- Cast EUR Decimal cols to Float64 before ratio/delta math.
- Don't infer row-existence from nullable business cols — use explicit presence flags in the diff.

## Pending drafts

1 skill draft (this session, above). Plus carried: 1 examine harvest (`2026-06-01-verify-diffs-both-ways-and-explicit-presence-flags`). None held in chat.
