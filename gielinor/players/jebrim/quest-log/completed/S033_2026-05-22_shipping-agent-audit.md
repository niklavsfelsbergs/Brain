# S033 — 2026-05-22 — shipping-agent audit

**Player:** Jebrim
**Birth:** S033 open
**Status:** quest-done — closed at S033 session-close (all actionable findings applied + restyled; K1 + Gap 2 deferred)

**Pending external actions:** None. All 3 shipping-agent commits landed and pushed (`4811b2e`, `f5fea20`, `9e63dd5`). All 4 S033 dwarves returned clean. K1 (orphan `__pycache__/db.cpython-313.pyc`) and Gap 2 (agent Write-tool bypass of harness) deliberately deferred per principal call.

## What this quest is

General audit of the `shipping-agent/` package at `Documents/GitHub/shipping-agent/`. Goal: find what would put the agent off course, what's friction, what's bloat, what won't perform well in real use. Read-only by mandate — agent runs in another window; no doc edits during the audit. Two-pass method per `inventory/shipping-agent-audit-resume.md`.

Triggered partly by the S032 caveat harvest (exposed doc structure) and partly by an observed hallucination — running agent freehand-generated stale pre-cutover language despite clean gold-explicit docs.

## Turn-by-turn

- **Open.** Niklāvs confirmed S033 numbering. Pass 1 begins — read everything in the read-order list, no writes to the agent's package, capture tensions/risks/friction as a flat list in this quest log.
- **Decisions locked (post pass-2 surface).** (1) TCG = Picturator + PicaAPI, no PCS. (2) Remove all Mode 4 / `create_timestamped_presentation.py` references + the script itself. (3) `git rm --cached -r workbench/investigations/ups-de-zv-130cm-diversion/` to restore "workbench is gitignored" consistency. (4) Re-verify D1/D2 stamps in-session via the shipping-agent harness.
- **4 dwarves spawned in parallel.** D1 shims-and-import (CLAUDE/AGENTS/GEMINI/GROK.md — A1 + G1). D2 harness-and-scatter (query_to_csv/xlsx + root scatter + remove create_timestamped_presentation.py — C1 code-side, C2 script delete, E1, E2). D3 restamp (coverage-audit.md + sources.md maturity — runs gold probes via harness). D4 doc-sweep (how_to.md + README.md + sources.md TCG + skills/query-patterns.md + 3 _about.md + .gitignore + the `git rm --cached` for H1 — B1, C1 doc-side, C2 doc-side, F1, F2, I1, J1, H1).
- **Pass 1 read.** Walked the package: `CLAUDE.md`, `how_to.md` (469 lines), `README.md`, 5 reference files, `skills/_about.md` + `skills/query-patterns.md`, 3 personal-folder `_about.md`s, 3 per-assistant shims (AGENTS / GEMINI / GROK), `.gitignore`, `harness/` file list, the one in-tree workbench item (`ups-de-zv-130cm-diversion/CLAUDE.md`), and the top-level glob to spot scatter.

## Pass 1 — flat findings (raw observations)

### A. Hallucination root cause (the headline)

- **A1. `how_to.md` is not `@-imported` from `CLAUDE.md`** — it's referenced via markdown link only (`Read [how_to.md](./how_to.md) first`). Claude Code auto-loads `CLAUDE.md` and its `@./path` imports; markdown links do not auto-load. The header of `how_to.md` says "Re-read this file in full every session" but nothing in the harness enforces it. If the agent answers from model prior without first calling `Read` on `how_to.md`, §0 and the rest of the rulebook never land. **This is the most plausible explanation for the S032-close hallucination** (stale "silver-layer mart" / "Sendmoments" language despite gold-explicit docs). Same fix pattern as gielinor master `CLAUDE.md`'s `@meta/*.md` imports.

### B. Internal contradictions (high leverage — agent picks whichever it last read)

- **B1. TCG composition contradiction across three files.**
  - `how_to.md` §0 rule 12: `TCG = source_system IN ('Picturator', 'PicaAPI')` (excludes PCS explicitly — "PCS is cost-only with no revenue and small sample — never report it standalone").
  - `reference/sources.md` § TCG composition: `TCG = Picturator + PicaAPI + PCS`.
  - `skills/query-patterns.md` "average shipping cost per parcel" example: `source_system IN ('Picturator', 'PicaAPI', 'PCS')  -- "TCG"`.
  - Every "TCG headline" answer is wrong on the PCS dimension depending on which file the agent last touched. Highest-leverage doc-level finding in the audit.

### C. Documented-but-missing / undocumented-but-present (drift)

- **C1. `harness/query_to_csv.py` and `harness/query_to_xlsx.py` are undocumented.** They exist on disk. Not listed in:
  - `README.md` § Files at a glance,
  - `how_to.md` §10 allowed bash invocations,
  - `how_to.md` §8 "Before creating a new build script, check the harness first."
  - Agent invoking them is technically a §10 scope violation by the letter of the rule. These were the scripts that produced the seed-finding root-CSVs.
- **C2. "Mode 4" / `create_timestamped_presentation.py` is a phantom.** Mentioned in `README.md` Files-at-a-glance ("Mode 4 presentation scaffold") and in `how_to.md` §8 "Before creating a new build script" list. `how_to.md` §7 documents only Modes 1–3. No mode-4 usage guidance anywhere.

### D. Stamp regime split — pre-gold-cutover content in LIVE files

- **D1. `reference/coverage-audit.md`** `Last verified: 2026-05-21 against the silver-era mart. Re-verify against gold — probes below are gold-shaped but numbers are pre-cutover and may have shifted.` All four "concentrated cost-coverage holes" + the by-month ORWO table are pre-cutover. Agent will quote these as current if asked.
- **D2. `reference/sources.md` source-maturity table** stamped `2026-05-21 (pre-gold-cutover; re-verify when ORWO destination_country and revenue_eur land in gold)`. Same problem, smaller scope (one table).
- **D3.** `mart-contract.md` / `tables.md` / `known-dq.md` / `query-patterns.md` are all `Last verified: 2026-05-22` — current. Two-stamp regime is doing real work (the warnings on D1/D2 are loud), but there's an "untrusted" zone in the otherwise-clean reference layer.

### E. §8 scatter — rule-to-behavior gap (seed finding, confirmed by inspection)

- **E1.** Three artifacts at package root, hidden by `.gitignore` but physically present: `canvas_qty_cost.csv`, `fuel_share_3carriers.csv`, `data/cost_ratio_trend.{sql,csv}`. The `.gitignore` comment explicitly calls them "Scatter from pre-workbench era — query outputs left at package root." Rule was active; behavior violated it.
- **E2.** `harness/query_to_csv.py` has no §8 routing guardrail — `--out` is `required=True` (per resume) but doesn't warn when the path is at package root. The "make it easier to do the right thing" hook is missing.

### F. Doc weight / triplication

- **F1.** Routing for personal folders is described in three places: `how_to.md` §11, `workbench/_about.md` (+ `memory/_about.md` + `scratchpad/_about.md`), and `README.md` "personal workspace" paragraph. The three say the same thing in slightly different framings. Cost: read-tax + drift risk on update.
- **F2.** `how_to.md` is 469 lines / supposedly "always-loaded." Heavy if A1 is fixed and it actually loads every session. The §11 reactive-boot-story sub-section is ~25 lines that could probably collapse into one bullet (it's specifying how the agent answers a user help question — high specificity for a low-occurrence event).

### G. Per-assistant shims

- **G1.** `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `GROK.md` are nearly verbatim — only the first sentence ("You're Claude" / "You're Gemini" / etc.) differs. No drift detected. Maintenance cost: changes to the shim must land in all four. Could collapse to one source-of-truth + one-line pointers.

### H. Workbench-tracked item vs gitignore

- **H1.** `workbench/investigations/ups-de-zv-130cm-diversion/` is committed (in the initial repo push). `.gitignore` says `workbench/**` then `!workbench/_about.md` + `.gitkeep`s — this item shouldn't be tracked under the current rules. Either the item is grandfathered (initial commit predated the gitignore tightening) or it was force-added. `workbench/_about.md` says "Gitignored except this file and `.gitkeep`s — your work here survives `git pull` cleanly" — the live state contradicts the doc.

### I. §10 scope rule — platform-specific phrasing

- **I1.** §10 forbids "Any path that starts with `C:\`, `/c/`, or `..\`." Windows-only literal. If the folder is ever cloned to Linux/macOS (or a Codespaces-style remote), the rule loses its bite. Worth either generalizing ("absolute paths to the OS root") or accepting it as Windows-anchored.

### J. §10 "local-first reach" — overdetermined for the new location

- **J1.** The §10 "Local-first reach" + "Recovery move is closer, not further" sub-sections are extensive and written for the pre-relocation context (when NFE's `CLAUDE.md` was walking into the agent and shared `bi-etl` / `shared/` paths were nearby). Standalone at `Documents/GitHub/shipping-agent/`, there *is* no `shared/` / `lib/` / `bi_etl/` adjacent — those reach-out paths can't accidentally be found. The rule is still correct but reads heavier than the new context warrants. Could compress to 1–2 sentences.

### K. Niche

- **K1.** `__pycache__/db.cpython-313.pyc` at package root (not under `harness/__pycache__/`) suggests `db.py` was imported from `cwd=shipping-agent/` — i.e., someone ran a Python script from agent root that did `from db import …`. The harness pattern is to call `python harness/connect_redshift.py`, which would land the pyc under `harness/__pycache__/` (which also exists). Possibly a one-off; not worth chasing unless it recurs.
- **K2.** No explicit `production_site = 'Sendmoments'` exception in docs — but `known-dq.md` lists `Sendmoments*` as one of the unmapped Picturator LIKE-map values. The S032-close hallucination claimed "Sendmoments" was a separate scope entity, which is wrong. The doc correctly classifies it as an unmapped production-service-provider string — but the agent freehanded the wrong category. Reading `known-dq.md` would have caught it.

