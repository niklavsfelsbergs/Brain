# Migrate the judgment layer of NFE's CLAUDE setup into the brain

*Drafted 2026-06-09 (consultation cue, not a bankstanding pass — Niklavs asked Guthix what to pull out of the NFE setup now that the brain exists, then to plan the refactor).*

> **STATUS — PARTIALLY LANDED (2026-06-09, [[S165_e0f6de1a_nfe_reference_judgment_layer_to_brain|S165]], Braindead on [[D-034_guthix_executes_on_explicit_authorization|D-034]] authorization).**
> - **Authority prerequisite:** [[D-034_guthix_executes_on_explicit_authorization|D-034]] written (Guthix executes on explicit authorization) + `meta/guthix.md` & `meta/write-rules.md` amended.
> - **Wave 0 ✅** — `NFE/CLAUDE.md` Coding Preferences + Boundaries collapsed to a pointer at the global.
> - **Wave 1 ✅** — four global skills created: [[report-design-language]], [[commentary-methodology]], [[chart-house-style]], [[date-and-timezone-discipline]]; five NFE reference docs (report/commentary/house-style/date-handling/notebook) given canonical-pointer headers.
> - **Wave 2 ⏳ follow-up** — mart-semantics single-source-of-truth (Jebrim bank canonical; NFE → thin pointer). Touches Jebrim's namespace → a Jebrim/alching session.
> - **Wave 3 ⏳ follow-up** — harvest NFE topic findings into Jebrim bank, then retire `analysis-save-finding`/`recall`/`prior-work-researcher`. Incremental harvest project.

## 1. Observation

`bi-analytics-main/NFE/` carries a mature pre-brain CLAUDE setup: `CLAUDE.md` + `.claude/` with skills, agents, hooks, and 13 `reference/*.md` docs (~6,200 lines) plus two HTML templates in `lib/templates/`. Read against what the brain now holds (Jebrim's `bank/notes/`, the spellbook methodology skills, the shipping-agent reference, alching), three things landed on the wrong side of the workshop/mind line:

- **Verbatim duplication.** `NFE/CLAUDE.md` `## Coding Preferences` (polars/parquet/f-strings/pathlib/sql-in-folders) and `## Boundaries` (ask-before-commit, never-drop-tables, don't-refactor) are exact copies of `~/.claude/CLAUDE.md`, which already loads in every repo including NFE. Dead duplication that can drift from the canonical copy.

- **A judgment layer trapped in a single repo.** Several `reference/` docs fuse two layers: a **judgment layer** (how Niklavs decides things look/work — palette, what-tool-when, traceability discipline, hard-won gotchas) and a **wiring layer** (which `lib.` import, which path, this repo's config). The judgment layer transfers to *anything* he builds — the cockpit, the brain visualizer, the next repo — but trapped in `NFE/.claude/reference/` it only fires in bi-analytics sessions. The HTML templates are the clearest case: HTML gets built in the cockpit and the visualizer too, yet the design language lives only in NFE.

- **A superseded findings-memory.** NFE has its own primitive memory: `analysis-save-finding` / `analysis-recall` skills, the `prior-work-researcher` agent, and findings scattered across topic `CLAUDE.md`/`FINDINGS.md`. That is a weaker version of what the brain now does properly (bank/notes + alching + quest-log + drafts gating). Two memories of the same shipping domain.

## 2. Proposed change

A four-wave refactor. **The organizing rule: the brain owns the judgment layer (how we decide/make/know); NFE keeps the wiring layer and points at the brain.** Migration is mostly *splitting* a doc, not moving it whole.

A second axis decides *where* in the brain: **craft is cross-player → global `spellbook/`; domain knowledge is shipping → Jebrim.** Chart style, report design, and the commentary methodology are agent-wide craft, not Jebrim's shipping knowledge — they belong in global `spellbook/skills/` (a craft skill can embed its reference constants, e.g. the palette hexes, inline). Mart semantics and topic findings are Jebrim's.

### Wave 0 — free dedupe (no brain work, do first)

Delete `## Coding Preferences` and `## Boundaries` from `NFE/CLAUDE.md`. The global `~/.claude/CLAUDE.md` already carries them everywhere. Zero risk, removes a drift source.

### Wave 1 — judgment-layer migration (the meat)

Split each doc; the judgment half becomes a brain skill/asset, the NFE doc shrinks to its wiring half + a canonical pointer.

| NFE source | Judgment layer → brain destination (scope) | Wiring stays in NFE |
|---|---|---|
| `lib/templates/documentation.html` + `report.html` | **global `spellbook/skills/`** — report/doc *design language* skill, templates inlined or referenced as the one source | `lib/docs.py` loader |
| `reference/report-patterns.md` | fold into the same global design-language skill — audience→tool matrix, lead-with-a-bold-observation, distinctive fonts (avoid Inter/Roboto/Arial), center content, 1px-gap KPI grids, staggered fade-ins | `analysis_config.json`, reference-impl path |
| `reference/commentary-patterns.md` | **global `spellbook/skills/`** — the two-layer *deterministic-analysis-then-editorial-narrative* methodology (every number traces to source; the LLM never touches raw data). Highest-value item: a reusable analytical principle, already Jebrim's traceability discipline | `analyze.py` / `generate_commentary.py` scaffolding |
| `reference/house-style.md` | **global `spellbook/skills/`** — chart house style: palette hexes + font hierarchy (reference values, inlined), violins-over-box, the legend-grows-upward / margin reasoning | `lib.style` `workbench` template wiring |
| `reference/date-handling.md` | **global `spellbook/skills/`** (or bank-note style if kept as pure reference) — timezone/UTC discipline (CET trap, UTC-methods rule, ISO-string compare, "partial weeks always dropped") | `--simulate-date` parquet-filter bit |
| `reference/notebook-patterns.md` (taste subset only) | fold into the design-language skill — decimals-to-2, bullets-over-tables in callouts, sections-first-filters-second | marimo cell scaffolding (stays) |

Each migrated NFE doc gets a standard header: `> Canonical: brain → spellbook/skills/<X>. This file keeps only the NFE wiring that implements it.`

### Wave 2 — domain-knowledge single source of truth

`reference/shipping-data-mart/{overview,tables,sources}.md` overlaps Jebrim's mart knowledge (`shipping-mart-gold-lineage-and-access-tiering`, the shipping-agent reference, silver→gold lineage). Make **Jebrim's bank canonical for domain semantics** (column meaning, source priority, the gold contract, DQ gotchas). NFE keeps a thin *repo-pull pointer* — which silver tables, how to query them here — citing the brain rather than restating it. Not a move-and-delete (see §6).

### Wave 3 — retire the findings-memory (biggest, a harvest project)

Harvest durable shipping findings from NFE topic `FINDINGS.md`/`CLAUDE.md` into Jebrim's `bank/drafts/notes/` via alching. Once the brain is where Niklavs reaches for "what do we know about X," NFE's `analysis-save-finding` / `analysis-recall` / `prior-work-researcher` stop being the durable memory and keep only *topic-local build state* (this dashboard's pipeline steps, this topic's decisions).

### Stays in NFE untouched (pure wiring, no transferable judgment)

`docker-patterns`, `nextjs-dashboard-patterns`, `nextjs-state-patterns`, `recharts-gotchas`, `streamlit-patterns`, `duckdb-api-patterns`, `pipeline-patterns` scaffolding, the `lib/` loaders, the `/workflow:*` pipeline, `schema-scout`. (Note: some war wounds from these *already* harvested correctly — the CSS height-match note, the SCM OOM modes are in Jebrim's bank. That is the pattern working.)

## 3. Reasoning

- **Reuse.** A brain skill fires across every surface (cockpit, visualizer, future repos); an NFE reference doc fires only in bi-analytics. The HTML template is the proof — already needed in three places, sourced from one.
- **Single source of truth.** Each place NFE *restates* rather than *points at* the brain is a future contradiction. Niklavs has been bitten by exactly this (the [[S171_c4e56024_ups-fuel-basis-and-gri-sensitivity|S171]] fuel-pct code-comment, the S150 code-comment-vs-data beats). The principle: NFE describes how to build; the brain describes what's true and how we judge.
- **The brain already does memory better.** Wave 3 is not new machinery — it is letting the stronger system absorb a function the weaker one was improvising.
- **Cost to land:** Wave 0 minutes; Wave 1 self-contained and low-risk (a handful of new global skills + NFE pointer-rewrites); Wave 2 careful; Wave 3 an ongoing harvest, run incrementally through normal alching.

## 4. Scope of impact

- **Who executes what.** Guthix drafts this and stops — he does not write into Jebrim's house or the NFE repo. Brain-side writes (global `spellbook/` skills, Jebrim `bank/notes/`) run through a player/alching session as drafts → promotion. NFE-side edits (delete sections, shrink docs to pointers) run in a session opened in `bi-analytics-main`.
- **Cross-repo.** NFE and the brain load in different contexts; an NFE coding session does not load the brain. Hence pointers, not deletes (see §6).
- **Surfaces touched:** global `spellbook/skills/` (new), Jebrim `bank/notes/` (additions), `NFE/CLAUDE.md` + `NFE/.claude/reference/*` (shrink + pointer headers), eventually NFE's findings skills/agent.
- **Backfill:** Wave 3 harvest is the only large backfill; it is incremental, not a one-shot.

## 5. Alternatives considered

- **Move-and-delete the reference docs wholesale.** Rejected — strips NFE coding sessions of the wiring they need and the inline craft they currently load; the split + pointer keeps both repos functional.
- **Leave everything; just dedupe (Wave 0 only).** Rejected — concedes the reuse win and leaves the design language single-repo-bound, which Niklavs explicitly pushed back on.
- **Home the craft skills under Jebrim.** Rejected — chart style, report design, and commentary methodology are cross-player craft, not shipping domain; Jebrim-scoping them would re-trap them. Global `spellbook/` is the correct home.
- **One mega-skill vs several.** Lean toward a small set: a *design-language* skill (report/doc/notebook taste + templates), a *commentary-methodology* skill, a *chart-house-style* skill, a *date/timezone-discipline* skill. Splitting beats one sprawling doc for just-in-time loading.

## 6. Risk if landed wrong

- **Drift between the brain canonical and the NFE pointer** if a pointer silently re-grows into a restatement. Mitigation: the standard pointer header names the canonical path; treat any NFE doc that restates brain content as a defect.
- **NFE sessions losing context** if a doc is deleted before its pointer is written. Mitigation: Wave order — write the brain skill first, then shrink the NFE doc to a pointer, never the reverse.
- **Premature Wave 3** — retiring `analysis-recall` before findings are harvested would orphan domain knowledge. Mitigation: harvest first (alching), retire the machinery last, and only after the brain demonstrably holds the findings.
- **Over-scoping the craft skills** — copying NFE wiring into the brain skill instead of just the judgment. Mitigation: the skill carries taste + reference constants (palette, fonts), never `lib.` imports or paths.
