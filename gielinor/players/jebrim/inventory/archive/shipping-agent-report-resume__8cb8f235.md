---
quest: S124_shipping-agent-report
sid8: 8cb8f235
ts: 2026-06-01 21:00
open_dep: none
---

# Resume — Shipping Agent Report

**Status:** in-progress — design locked (substantially reframed 2026-06-01), build not started. Re-parked deliberately to start the build in a fresh session.

## Where we are

Design is locked. The report is a **senior-analyst review**, not a rules engine: a deterministic harness *prepares evidence + ranks attention* and makes **zero verdicts**; the "is this an issue" judgment is mine each run, gated by a running notebook + materiality. **Two tiers** — weekly big (full analyst memo) + daily small (costs-arrived + a DQ canary), one daily snapshot spine feeding both. Arc: §1 orientation → §2 costs arrived (diff) → §3 the review (my reasoning) → §4 one sized opportunity (PAPER vs DEFENSIBLE) → §5 expected-cost health (at the end — a re-estimation signal, since expected costs are "very off"). Knowledge lives in the project folder; brain keeps lean references. The **shipping agent is first-class** — it operates the harness and the skill calls it every run. Full design in the S124 quest-log, Session-2 section.

## Next concrete step

**First build step (principal's explicit cue): investigate refunds/credits and teach the shipping agent, before anything else.** Refund location varies per carrier and is unknown — UPS uses negative-amount invoice lines (NOT `credit_note`), but *some* carriers do use `credit_note`. So:
1. Through the shipping agent, **map per carrier where refunds/credits actually live** in the mart (`credit_note` column / negative invoice line / both).
2. **Write the per-carrier map into the shipping agent's `reference/known-dq.md`** (teach the agent). The daily DQ canary depends on this — a legit refund must not be mis-flagged as a cost anomaly.

Then the rest of the grounding pass (lane-key feasibility, expected-vs-actual gap profile to quantify "how off", segment baselines), then scaffold `NFE\projects\4_automated_shipping_report\`, write the snapshot puller + diff, draft the skill.

## Files / paths to read first

- `gielinor/players/jebrim/quest-log/in-progress/S124_61d62e21_shipping-agent-report.md` — full design; **read the Session-2 (2026-06-01) section** for the reframe + the locked-decisions list.
- `Documents/GitHub/shipping-agent/reference/{mart-contract.md,sources.md,known-dq.md}` — mart vocab + DQ (known-dq is where the per-carrier refund map gets written).
- `gielinor/players/jebrim/spellbook/skills/calling-the-shipping-agent.md` — how Jebrim spawns the agent.
- `gielinor/players/jebrim/bank/notes/projects/2026-05-27-shipping-mart-gold-lineage-and-access-tiering.md` — mart lineage + access tiers.

## Build progress (Session 3, sid 28d1f778, 2026-06-01)

- **Step 1 DONE — per-carrier refund/credit map.** Investigated live mart; 3 mechanisms found (contractual discounts: fedex→discounts; genuine credits: ontrac/yodel→credit_note; surcharge reversals refund-in-place: ups/dpd_uk→original bucket). usps/maersk/dbs/direct_link/apg/dpd_poland = no observable channel. Written into `shipping-agent/reference/known-dq.md` (new "Refund / credit location by carrier" section). **PUSH PENDING principal nod** — file edited, not committed/pushed.
- Full findings in S124 quest-log Session-3 section.
- **MCP gotcha:** Redshift MCP validator rejects `DATEADD`/`CURRENT_DATE` — use literal dates.

- **Grounding pass DONE** — gap profile (TCG expected +5–8% under-bias, fat tail; ORWO poorly calibrated but tiny-€), lane-key GREEN (92 lanes / 99.88%), segment baselines (table in quest-log Session-3 + seeded into running-notebook).
- **Scaffold + snapshot spine + diff harness BUILT & VERIFIED** in `bi-analytics-main/NFE/projects/4_automated_shipping_report/`. First snapshot proven (1.94M rows, 49 MB). Diff self-tested clean + synthetic-tested. Connection = full-access `tcg_nfe` from `NFE/.env`. Files: `lib/db.py`, `sql/snapshot.sql`, `lib/pull_snapshot.py`, `lib/diff_snapshots.py`, `notebook/running-notebook.md`, `README.md`. NOT committed (NFE = principal repo).

## Next concrete step (remaining build)

1. **Draft the skill** — the weekly/daily analyst playbook (snapshot cols, diff logic, noticing checklist, §1–§5 scaffold, scope gating, the running-notebook discipline) → `players/jebrim/spellbook/drafts/skills/`. The real durable artifact.
2. **Report builder** §1–§5 + **daily DQ canary** (zero-row segment = silent load fail, coverage regress, null spike) in the project `lib/`.
3. **Retention policy** — 49 MB/day ≈ 18 GB/yr if all kept → thin (keep ~30 daily, weekly thereafter).
4. **Real diff test** needs a 2nd daily snapshot (tomorrow). Triggering deferred.

**Gotchas:** Redshift MCP validator rejects `DATEADD`/`CURRENT_DATE` (use literals); connectorx needs `protocol="cursor"` on Redshift; cast EUR Decimal cols to f64 before ratio math.

## Pending drafts

None held in chat (all design persisted to the quest-log).
