# Proposed pin — Shipping Data Mart routing

**Proposed:** 2026-05-21 (S015, post-S014-close)
**Pin text (what surfaces every Jebrim session):**

> **Shipping Data Mart — routing.** Primary how-to: `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/how_to.md` — AI-facing deep how-to (pipeline overview, sources, structure, silver-layer reference, queries, Redshift connection harness, output modes, artifact rules, DQ). Navigation map: `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/` (`overview.md` / `tables.md` / `sources.md`) — lighter sibling for table/source lookups. Ground truth: `Documents/GitHub/bi-etl/dags/enterprise_silver/shipping_data_mart/` (per-folder READMEs — `git pull origin main` before reading the code). Outputs land per TTYD §7–§8 conventions (`visualization-studio/content/generated/<ai>/YYYYMMDD-HHMMSS--<slug>/`). When new gotchas / recipes / NULL classifications emerge from real work, update `how_to.md` (AI consumption) and `.claude/reference/shipping-data-mart/recipes.md` (human consumption, create if missing).

## Why this qualifies for keepsake

- **Frequent standing topic.** Principal stated in S015: "I will now be frequently working on the shipping data mart with you, Jebrim." Not quest-bounded — ongoing working context.
- **Three sources of truth, easy to land on the wrong one.** Reference docs are the lighter navigation map; TTYD `how_to.md` is the deeper AI-facing how-to with output conventions; bi-etl per-folder READMEs are ground truth for what's actually shipped. All three authoritative for different purposes. Without the keepsake, an agent reading `NFE/CLAUDE.md` alone would never find TTYD — discoverability gap directly verified in S015.
- **Cheap to keep loaded.** One paragraph, low decay risk — paths are stable.

## Rotation criteria

Rotate out when:
- TTYD `how_to.md` restructures, gets renamed, or is superseded by a different artifact, **or**
- The shipping data mart stops being a frequent working topic.

## Supersedes

`2026-05-21_shipping-data-mart-ttyd.md` — the temporary mid-quest pin for S014 progress. S014 closed in S019; per that proposal's own rotation criteria ("Rotate out when S014 closes — deliverable shipped, bank-note harvest done"), it's now stale. This proposal replaces it as the standing surface for shipping-data-mart sessions.

## Source

S015 investigation — read of `bi-analytics-main/CLAUDE.md`, `NFE/CLAUDE.md`, `NFE/.claude/reference/shipping-data-mart/overview.md`, `NFE/projects/3_shipping_data_mart_TTYD/{CLAUDE,how_to}.md`. Discoverability gap (NFE/CLAUDE.md does not point to TTYD) sized in same investigation; sibling fix lands as one-line edit to `NFE/CLAUDE.md`'s Shipping Data Mart section in this turn.
