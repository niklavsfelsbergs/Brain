# Shipping-agent personal folders — resume

**Status:** in-progress (design complete, implementation pending).
**Where we are:** S029 design conversation landed the full plan. No file work has happened in `bi-analytics-main` yet.
**Next concrete step:** Open `bi-analytics-main` (shipping-agent dir), read the design plan in `quest-log/in-progress/OPEN_2026-05-22_shipping-agent-personal-folders.md`, then start with **step 1 — delete `visualization-studio/`** (confirm with principal first). Then steps 2–9 of the plan in order.

## Files to read first (load order)

1. `gielinor/players/jebrim/quest-log/in-progress/OPEN_2026-05-22_shipping-agent-personal-folders.md` — the design plan with 13 behavior rules + folder structure + CLAUDE.md template + concrete implementation steps.
2. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — current shipped state (HEAD `c48bac6`, includes today's §0 rules 12–15 + rule 9 tighten).
3. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/README.md` — human-onboarding doc.

## Watch-outs

- **Scoped commits only.** `bi-analytics-main` working tree at handoff has uncommitted parallel-session work (`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`/`GROK.md` edits, untracked harness scripts, untracked visualization-studio chart outputs). Don't `git add -A`. Stage specific paths.
- **`visualization-studio/` deletion** confirmed by principal in S029 design conversation. Still — re-confirm before deleting untracked chart outputs that may belong to the parallel session.

## Open threads parked at handoff

- Cross-user permissions / team scope of `memory/` — not resolved. Default to plain markdown.
- `data/` snapshot disk-cost question — deferred until real use.
- AGENTS.md / GEMINI.md / GROK.md sync to new how_to.md content — verify at end of implementation.

## Pending drafts

None. All S029 drafts were promoted in alching.
