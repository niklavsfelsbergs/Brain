---
quest: S124_shipping-agent-report
sid8: 61d62e21
ts: 2026-05-29 16:42
---

# Resume — Shipping Agent Report (weekly)

**Status:** in-progress — approach designed, parked for build. Triggering deliberately deferred.

## Where we are

First scheduled-task design. A weekly, **non-deterministic** report (Jebrim driving the **shipping agent**) on what's worth noticing in shipping, built on a **snapshot-diff** so it catches late-arriving invoiced costs, not just last week's shipments. Approach is ~90% locked; build not started; NFE folder not scaffolded.

## Locked decisions (don't re-litigate)

- **Snapshot-diff**, not native load dates — mart tables are truncate-and-reload, so `updated_at`/`dw_timestamp` reset every reload and can't mark cost-arrival.
- **Cohort anchor: `shop_order_created_date`** (NOT `received_by_carrier_date` — carrier-log quality, NULL by design for PCS/Rewallution/ORWO).
- **Window: 120 days.**
- **Segments:** ORWO (`source_system='ORWO'`); TCG (`Picturator`+`PicaAPI`) split by `production_site` → **PCS PL, PCS CMH, Wolfen, Other**. PCS CMH is real (Camp Hill). TCG-Wolfen ≠ ORWO segment.
- **Home:** `NFE\projects\4_automated_shipping_report`.
- **Artifact = skill** (procedure) + parquet snapshots (data) + running noticing-memory.
- **Sizing:** ~1.42M rows/90d, ~20–40 MB/week parquet — size is not a constraint.

## Next concrete step

Two questions to close the approach before build (principal call):
1. **Report output form** — markdown in the project folder (my default) vs email/Slack delivery (ties into triggering)?
2. Confirm the **diff taxonomy + §1/§2/§3 per-segment scaffold** as designed (see quest-log), then the only remaining design item is real **noticing thresholds** (X/Y/Z/N/M/K), which need a few snapshots to set empirically.

Then build phase 1: scaffold `NFE\projects\4_automated_shipping_report`, write the snapshot puller (one parquet to confirm real size), write the diff, draft the skill. **Then** design the trigger.

## Files / paths to read first

- `gielinor/players/jebrim/quest-log/in-progress/S124_61d62e21_shipping-agent-report.md` — full design + diff taxonomy + scaffold.
- Shipping-agent knowledge: `Documents/GitHub/shipping-agent/reference/{mart-contract.md,sources.md,known-dq.md}` — cost vocab, TCG composition, ship-date/anchor DQ.
- `gielinor/players/jebrim/spellbook/skills/calling-the-shipping-agent.md` — how Jebrim spawns the agent.
- `gielinor/players/jebrim/bank/notes/projects/2026-05-27-shipping-mart-gold-lineage-and-access-tiering.md` — mart lineage + access tiers.

## Pending drafts

None held in chat (all design persisted to the quest-log).
