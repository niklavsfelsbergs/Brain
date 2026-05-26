# [[S033_2026-05-22_shipping-agent-audit|S033]] D2 — harness-and-scatter

**Role:** Jebrim dwarf, spawned by principal Niklavs in gielinor [[S033_2026-05-22_shipping-agent-audit|S033]].
**Scope:** shipping-agent audit fixes — D2 lane (root scatter moves, §8 guardrail in `query_to_csv.py` / `query_to_xlsx.py`, removal of phantom Mode 4 script).
**Working dir:** `C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent\`
**Status:** completed at [[S033_2026-05-22_shipping-agent-audit|S033]] close. No pending external actions.

## Actions

### Task 1 — Move root scatter into `scratchpad/`

- [completed] move `canvas_qty_cost.csv` → `scratchpad/canvas_qty_cost.csv`
- [completed] move `fuel_share_3carriers.csv` → `scratchpad/fuel_share_3carriers.csv`
- [completed] move `data/cost_ratio_trend.sql` → `scratchpad/cost_ratio_trend.sql`
- [completed] move `data/cost_ratio_trend.csv` → `scratchpad/cost_ratio_trend.csv`
- `data/` is now empty (left in place per instructions; principal sweeps on commit)

### Task 2 — Add §8 root-path guardrail

- [completed] edit `harness/query_to_csv.py` — added `import sys`, `--force-root` flag, root-path guardrail (exit code 2 if `--out`'s parent resolves to the agent root and `--force-root` not set)
- [completed] edit `harness/query_to_xlsx.py` — same change applied; preserved existing `--sheet` arg ordering

### Task 3 — Remove phantom Mode 4 script

- [completed] `git rm harness/create_timestamped_presentation.py` (output: `rm 'harness/create_timestamped_presentation.py'`; staged as `D` in `git status`)

## Observations

- `scratchpad/` doesn't appear in `git status` after the moves — it's git-ignored (expected for an output sink). The 4 scatter files left the tree as far as git's concerned; the on-disk move is the durable record. Same effect as a delete-from-git plus a fresh write under `scratchpad/`, but no information lost.
- The two harness edits show as unstaged `M ` — correct, principal commits.
- Other dwarves' work also visible in `git status` (AGENTS/CLAUDE/GEMINI/GROK shims, `reference/coverage-audit.md`) — not my lane, not touched.
- `data/` directory left in place per instructions, now empty.

## Guardrail excerpt (csv, xlsx is parallel)

```python
out_path = Path(args.out).resolve()
agent_root = Path(__file__).resolve().parent.parent
if out_path.parent == agent_root and not getattr(args, "force_root", False):
    print(
        f"WARNING: --out path '{args.out}' is at the shipping-agent package root.\n"
        f"§8 says outputs should land in scratchpad/ or workbench/<type>/<slug>/outputs/.\n"
        f"Pass --force-root if you really meant the package root.",
        file=sys.stderr,
    )
    sys.exit(2)
```

Exit code 2 = guardrail tripped. `--force-root` is the bypass.
