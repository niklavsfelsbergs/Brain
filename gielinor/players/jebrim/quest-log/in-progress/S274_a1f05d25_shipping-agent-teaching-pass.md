# S274 · Shipping-agent teaching pass — SCM literacy, update-notifier, rule 38

**Session:** a1f05d25 · **Player:** Jebrim · **Date:** 2026-06-19

Principal asked what else we could teach the `picanova/shipping-agent` to make it smarter / more like Jebrim, with SCM-screenshot literacy already a named want. Turned into a multi-build pass against the external shipping-agent repo (all work committed + **pushed** there, not in this brain tree).

## What shipped (all in `Documents/GitHub/shipping-agent`, pushed to origin/main)

1. **SCM literacy + screenshot ingestion** (`42645e3`) — `reference/scm.md` (dashboard surface → exact mart definitions: order-month lens, `cost_for_routing`, quota formula, tabs/panels incl. Cost Drivers, deep-link URL contract, US-vs-NA scope trap, refresh/stale-partition caveats) + `skills/scm-screenshot.md` (disambiguate → read tile+scope → **reproduce from mart on matching basis** → reconcile → investigate). Wired via a `how_to.md §0` skill-trigger + indexes. Grounded in a live dwarf scan of `bi-analytics-main/.../shipping_costs_monitoring_nextjs` (branch main).
2. **Update-notifier hook** (`88fbd4a`) — `.claude/hooks/check_repo_updates.py` + `settings.json` SessionStart hook (matcher `startup|resume`). Best-effort non-interactive `git fetch` (`GCM_INTERACTIVE=never` + `GIT_TERMINAL_PROMPT=0` + timeout, fail-silent), compares `HEAD..@{u}`, emits a notify-don't-pull directive listing rulebook commits. Tested both paths via throwaway worktree.
3. **Rule 38 + accounting-complete boundary** (`3e5162a`) — every-mode rule 38 (two same-labeled figures disagree → suspect date-lens/scope/population/grain mismatch FIRST) + `reference/mart-contract.md` "Analytics-complete, not accounting-complete" (mart cost won't tie to invoice/GL; agent states the boundary, mart-only).
4. **known-dq departure_ts note** (`cde5aa3`) — landed a prior-session uncommitted note (departure_ts is modeled, not a real truck-departure event).

## Decisions / findings

- **Menu of candidate teachings** surfaced from a full read of Jebrim `examine/` (~90 reflexes) + `bank/` (~100 notes) via two Explore passes. Principal picked: A (reconciliation reflex) ✅ built; B (dimension-trust map) skip; C (re-rating trust gate / PAPER-vs-DEFENSIBLE) **not yet built**; D (carrier mechanics) skip; E (timing semantics) → **no-build** (already in `known-dq.md`).
- **Live grant check (ship_mart_ro):** schema has **7** objects but the role is granted only the **4 documented facts**. `fact_truck_charges`, `dim_transit_time_sla`, `mart_status` exist but are **NOT readable** by the agent. So the four-fact contract is exactly right; E was redundant.
- **Rule 16 half-stale:** `dim_transit_time_sla` (per-lane `sla_days`) now exists — contradicts rule 16's "no agreed SLA." Agent can't read it, so the rule's operational guidance still holds, but the factual claim is dated.
- **Wrong call corrected:** I concluded "can't push, hand off" from in-sandbox auth failures; principal pushed back; disabling the Bash sandbox let GCM reach the Windows cred store and the push (4 commits) succeeded. Captured as a learning (memory + examine draft).

## Turn-by-turn (condensed)
- Surveyed agent's current 37 rules + reference/skills; offered tiered menu; principal chose SCM first.
- Built SCM files (dwarf-scanned the live dashboard), wired indexes, committed.
- Designed + built the update-notifier hook (claude-code-guide confirmed the SessionStart contract); diagnosed the GCM headless-hang; tested via worktree; committed.
- Deep examine+bank read → extended grounded menu; principal scoped to mart-only (no raw invoice tables) and picked A + E.
- Verified live schema/grants → E no-build; built A (rule 38 + accounting-complete); committed known-dq note.
- Committed all (4 commits) one-by-one; push initially mis-called as blocked, then succeeded with sandbox disabled.

## Pending external actions
None pending. All four commits pushed to `origin/main` (verified `939b073..cde5aa3`, in sync).
