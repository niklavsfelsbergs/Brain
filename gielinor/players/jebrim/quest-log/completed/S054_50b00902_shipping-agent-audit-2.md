# S054 — shipping-agent audit (round 2)

**Opened:** 2026-05-23. Session `50b00902`. Jebrim active.
**Quest:** Run the queued audit-2 of `Documents/GitHub/shipping-agent/` (bloat / contradictions / overkill / too-technical), then apply approved fixes.
**Source brief:** `inventory/shipping-agent-audit-2-resume__91ee1383.md`.

## Turn log

- **T1 — respawn.** Loaded globals + Jebrim. No live siblings (22fa153c ended). Posted OPEN to comms. Only in-progress quest on disk was [[S040_1cf1eb75_outlook-mcp-research|S040]] (Outlook MCP, unrelated) — no reconciliation needed for shipping work.
- **T2 — scoped the ask.** Four shipping-agent threads queued; principal picked **audit-2**.
- **T3 — read-only audit pass.** Read full package: how_to.md (495 lines), CLAUDE/AGENTS/GEMINI/GROK shims, reference/ (mart-contract, tables, sources, coverage-audit, known-dq), skills/ (query-patterns, reprompting), harness chart code (build_inline_chart, build_report, _report_style), query_to_csv, settings.json, personal-folder _about.md files. 16 findings (table below).
- **T4 — OK1/OK2 retracted.** Initial "personal folders unused" finding was wrong — Glob respects .gitignore and those folders are gitignored. `find` off disk showed 6 real workbench items + ~35 scratchpad files + Mode-3 bundles in active use. Self-note candidate: don't assert disk-absence from a gitignore-aware search tool.
- **T5 — OK3 shims fixed (DONE).** GROK/GEMINI/AGENTS.md: replaced reliance on `@./how_to.md` import (Claude-only) with an explicit imperative ("first action: read how_to.md in full"). Import line kept as bonus. Auto-load is per-tool: Claude/Codex/Gemini CLIs auto-load their named file; Grok likely falls back to AGENTS.md (no reliable GROK.md convention); plain desktop apps don't fold-walk a repo (need manual attach). Edits local/unstaged in shipping-agent repo.
- **T6 — principal: "do all, ask if needed."** Confirmed C1/C2 scope via grep (each single-spot). Asked 2 decision questions.
- **T7 — decisions + applied all fixes.** Principal: C4 → soften §10 prose (keep settings); BL2 → aggressive (§8 canonical). Applied C1, C2, C3, C4, B1, BL2, BL3, TT1, TT2, TT3 across `how_to.md` (495→479), `skills/query-patterns.md`, `harness/build_report.py` (+legend JS, verified by render), `harness/build_inline_chart.py`, `reference/mart-contract.md`, brain keepsake pin. New latent finding logged (build_report `relative_to` crash on out-of-package `--out` — not fixed, out of scope). Audit report written to `workbench/audits/2026-05-23-audit-2/findings.md`. Examine draft written for the OK1 gitignore-blind-glob miss. All shipping-agent edits local/unstaged — commit pending principal go.

## Findings + fix targets

| # | Fix | File | Triage |
|---|---|---|---|
| C1 | fact_shipments 66→65 cols | skills/query-patterns.md:16 + brain keepsake pin | fix |
| C2 | §10 stale `build_light_html_presentation.py` → `build_report.py` | how_to.md:335 | fix |
| C3 | Mode-3 line charts: add value labels + legend-isolation JS (parity w/ build_inline_chart) | harness/build_report.py (_build_line, render_html) | fix (S049 follow-up) |
| C4 | §10 prose bans ls/dir that settings.json allows | how_to.md §10 or settings.json | DECISION |
| B1 | horizontal-bar labels use x_fmt, should be y_fmt | harness/build_inline_chart.py:120 | fix (real bug) |
| BL1 | how_to.md 495 lines — umbrella, achieved via BL2/BL3/TT* | how_to.md | (no discrete edit) |
| BL2 | output routing stated 4× — consolidate | how_to.md §0 r17-29/§7/§8/§11 | DECISION |
| BL3 | jargon stated twice — shrink rule 2 to pointer | how_to.md §0 rule 2 + table | fix |
| TT1 | §7 exposes JS mechanism — state behavior only | how_to.md §7 | fix |
| TT2 | §0 rule 11 embeds SQL formulas — move to mart-contract, point | how_to.md §0 r11 + reference/mart-contract.md | fix |
| TT3 | §0 rule 7 investigation-shape reads like spec — condense | how_to.md §0 rule 7 | fix |
| OK3 | shim import unreliable — imperative prose | GROK/GEMINI/AGENTS.md | ✅ DONE |

OK1 (personal folders) + OK2 (build_report.py) retracted — both actively used.

## Next concrete step

All fixes applied + verified. **Awaiting principal go to commit** the shipping-agent repo (8 files; its settings deny `git push` → principal pushes). Brain side has uncommitted changes too: keepsake pin (C1), this quest-log, the examine draft, comms. Decide commit scoping (shipping-agent vs brain — separate repos).

Open follow-ups (none blocking):
- Latent: `build_report.py` `output_html.relative_to(BASE_DIR)` crashes on out-of-package `--out`. One-line fix if it ever bites.
- §1 "Personal user content routes to…" is a residual routing restatement — left for a future trim.

## Pending drafts

- `examine/drafts/2026-05-23-disk-absence-needs-non-gitignore-aware-listing.md` (WRITTEN this session) — don't assert disk-absence from a gitignore-aware tool (Glob); use Bash find/ls for gitignored paths. Anchor: T4 OK1 miss. Mirror of confirmed `verify-git-tracked-with-ls-files-not-disk-presence`. Surface at next alching.
