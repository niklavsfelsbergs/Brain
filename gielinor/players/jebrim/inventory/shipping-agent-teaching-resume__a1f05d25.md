---
quest: S274_shipping-agent-teaching-pass
sid8: a1f05d25
ts: 2026-06-19 09:46
open_dep: principal decisions pending (demo/ disposition, ship_mart_ro grant for dim_transit_time_sla+mart_status, rule-16 reconcile) + menu item C unbuilt
---

# Resume — shipping-agent teaching pass

**Status:** in-progress (ongoing teaching thread; this pass shipped 4 commits, pushed).

**Where we are:** SCM literacy + screenshot skill, update-notifier hook, rule 38 + accounting-complete boundary, and the known-dq departure_ts note are all committed AND pushed to `origin/shipping-agent main`. The capability menu is partly worked.

**Next concrete step (principal decisions, then build):**
- **Decide `demo/`** in the shipping-agent repo — 3.8MB of binaries (incl. a 2.6MB .pptx), still untracked. Commit / gitignore / move out?
- **Grant decision:** grant `ship_mart_ro` SELECT on `dim_transit_time_sla` + `mart_status`? If yes → I draft the grant + document them + update rules 16/36 (SLA-aware on-time analysis; deterministic freshness/reload).
- **Rule 16** reconcile: it claims "no agreed SLA" but `dim_transit_time_sla` exists.
- **Menu item C (next teachable):** the re-rating trust gate — reconcile-vs-actuals, only TRUSTED engines as destinations, service-lane grain, PAPER-vs-DEFENSIBLE → extend `skills/savings-investigation.md`. This is the meaty one left after A.

**Files to read first (next session):**
- `Documents/GitHub/shipping-agent/how_to.md` §0 (rules 37/38 + skill triggers), `reference/scm.md`, `reference/mart-contract.md` (§ Analytics-complete).
- `players/jebrim/quest-log/in-progress/S274_a1f05d25_shipping-agent-teaching-pass.md` (this session's narrative).
- `players/jebrim/bank/notes/projects/2026-05-31-shipping-savings-rerating-trust-gate.md` (source material for menu item C).

**Note:** all teaching work lives in the **external** `shipping-agent` repo, not this brain tree. Pushing needs the Bash sandbox disabled (GCM cred store) — see memory `reference_git_push_needs_sandbox_disabled`.
