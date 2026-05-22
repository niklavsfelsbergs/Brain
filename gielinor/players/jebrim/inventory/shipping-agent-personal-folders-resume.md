# Shipping-agent personal folders — resume

**Status:** implementation shipped 2026-05-22 in `bi-analytics-main` commit `f892257` (pushed to `origin/main`). Quest stays open for real-use iteration — first run of the new model in a real shipping question is the validation step.
**Where we are:** All 9 design-plan steps landed plus integration work (AI pointer shims, README, harness `--out` flag on all three scripts). The personal-folder model is live; the agent will scaffold workbench items reactively.
**Next concrete step:** Use the agent on a real shipping question and see the new flow (Mode 2 chart → `scratchpad/`, multi-session work → `workbench/` scaffold offer, finding → `memory/` offer). First real session validates the §0 rules 16–28; any rough edge → draft an adjustment.

## Files to read first (load order)

1. `gielinor/players/jebrim/quest-log/in-progress/OPEN_2026-05-22_shipping-agent-personal-folders.md` — design plan + implementation turn-log (T1–T8 of this session).
2. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — HEAD `f892257`, full new model live (§0 28 rules, §7 three modes, §8 outputs-by-tie, §11 personal folders).
3. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/workbench/_about.md` — the per-item template the agent uses when scaffolding.
4. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/README.md` — human-onboarding doc (updated 2026-05-22).

## What landed this session (summary)

- `visualization-studio/` deleted entirely (Next.js app + 5 untracked chart outputs + 3 untracked bundle folders).
- `workbench/` + `memory/` + `scratchpad/` scaffolded with `_about.md` each.
- `.gitignore` allow-lists `_about.md` + `.gitkeep` under the three personal folders.
- `how_to.md` rewritten — §0 rules 16–28 (13 personal-folder rules), §7 three modes (Mode 4 dropped), §8 rewritten, §11 added.
- AI pointer shims (CLAUDE / AGENTS / GEMINI / GROK.md) and README.md sync'd.
- Harness scripts (`build_inline_chart.py`, `build_light_html_presentation.py`, `create_timestamped_presentation.py`) accept `--out` now; default `scratchpad/`. `create_timestamped_presentation.py` marked deprecated.

## Open threads / follow-ups

- **Real-use validation.** First real shipping question against the new model is the proof. Watch for: does the scaffold-offer wording feel natural (rule 16), does the trailing-question save prompt work (rule 17), does the `sql/<YYYYMMDD>-<NN>_<slug>.sql` autosave land cleanly (rule 22), does the `Source:` citation discipline hold for memory entries (rule 24).
- **`build_inline_chart.py --out` smoke-test in real use.** Syntax-checked and `--help` confirms the flag, but a real `python harness/build_inline_chart.py --data <csv> --out scratchpad/ ...` run hasn't happened yet.
- **Cross-user permissions / team scope of `memory/`** — still parked. Default to plain markdown until pushback.
- **`data/` snapshot disk-cost question** — still parked.
- **`create_timestamped_presentation.py` future.** Marked deprecated. Decide later whether to archive or leave callable for legacy template runs.

## Pending drafts

None this session. The implementation was execution-shaped, not observation-shaped.
