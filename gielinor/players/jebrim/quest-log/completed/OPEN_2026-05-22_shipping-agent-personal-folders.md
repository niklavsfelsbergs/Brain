# Shipping-agent personal folders + reproducibility — design plan

**Opened:** 2026-05-22 (handoff from [[S029_2026-05-22_shipping-agent-vocab-harvest|S029]]).
**Status:** in-progress — implementation landed 2026-05-22 (this session), awaiting commit + push.
**Type:** project (multi-session work in the shipping-agent core).

## Implementation turn-log (2026-05-22, current session)

**T1.** Respawned Jebrim, surfaced resume foreground from `inventory/shipping-agent-personal-folders-resume.md`, principal confirmed "yee lets tackle all the planned changes."

**T2.** State-checked `bi-analytics-main` working tree — confirmed parallel-session artifacts at agent root (`harness/query_to_csv.py`, `query_to_xlsx.py`, root-level CSVs, `data/cost_ratio_trend.*`, `__pycache__/`) and inside `visualization-studio/content/` (untracked chart + bundle outputs). Created 9 tasks.

**T3 (Step 1).** Re-confirmed `visualization-studio/` deletion scope with principal (tracked Next.js app + 5 untracked chart HTML files + 3 untracked bundle folders). Principal: "Yes — delete everything." Removed `visualization-studio/` recursively. Verified absent.

**T4 (Step 2).** Scaffolded the three personal folders with `_about.md` each — `workbench/_about.md` (full structure + per-item template + Tier 1/2 reproducibility + type heuristics), `memory/_about.md` (Tier 3 citation contract + entry shape), `scratchpad/_about.md` (no-tier transient + promotion offer). Added `.gitkeep` files in `workbench/projects/`, `investigations/`, `analysis/`.

**T5 (Step 3).** Updated `.gitignore`. Removed the obsolete `visualization-studio/node_modules/`, `visualization-studio/.next/`, `visualization-studio/.npm-cache/` lines. Added the personal-folders block with allow-listed `_about.md` and `.gitkeep` files.

**T6 (Steps 4–6, 8).** Rewrote `how_to.md` in five surgical edits:
- §0 intro: "Fifteen cross-cutting rules" → "Twenty-eight cross-cutting rules".
- §0 added rules 16–28 (scaffolding / saving / reproducibility / session-end / promotion / cleanup) per the design plan's 13 rules.
- §0 Translation table: added 4 new rows for `workbench/` (+ subfolders), `memory/`, `scratchpad/`, and `sql/`/`outputs/`/etc. inside a workbench item.
- §0 Output-mode subsection: paths swapped from `visualization-studio/content/charts/claude/` to `workbench/<type>/<slug>/outputs/` (tied) or `scratchpad/` (one-off).
- §7 rewritten to three modes (dropped Mode 4 Next.js); added a "Where output files land" table; Mode 2 step list updated to pass `--out` to `build_inline_chart.py`; Mode 3 bundle path now `workbench/<type>/<slug>/outputs/<bundle-slug>/`.
- §8 entirely replaced — naming, destinations, rules, visual system (palette now lives inside the harness scripts as defaults, no more `STANDARDS.md`).
- §11 added — personal folders + per-item structure + `CLAUDE.md` template + type heuristics + reproducibility tiers + memory-entry shape + reactive boot-story + active-workbench-item tracking.

**T7 (Step 7).** Verification grep found leftover `visualization-studio/` refs in CLAUDE.md / AGENTS.md / GEMINI.md / GROK.md (per-AI pointer shims), README.md (4 refs), and three harness scripts. Surfaced the harness-script question to principal — chosen: "Add `--out` flag (default `scratchpad/`) to all three." Updated:
- All four AI pointer shims (one-line replacement: visualization-studio paragraph → personal-folders pointer to §7/§8/§11).
- README.md: opening paragraph, "what this folder is", "how to use it", "files at a glance" table (3 rows: visualization-studio → workbench/_about.md, memory/_about.md, scratchpad/_about.md).
- `harness/build_inline_chart.py`: `CHARTS_DIR` → `DEFAULT_OUT_DIR = BASE_DIR / "scratchpad"`; added `--out` argparse flag; main() resolves `out_dir` from `args.out` or default.
- `harness/build_light_html_presentation.py`: `GENERATED_DIR` → `DEFAULT_OUT_DIR`; added `--out`; main() resolves `out_root` and uses it for bundle creation. Kept the "spec already inside bundle" short-circuit logic.
- `harness/create_timestamped_presentation.py`: top-level docstring marks deprecated (Mode 4 dropped); added `--out` so legacy template runs still work.
- Final `visualization-studio` grep returns only the deprecation note inside `create_timestamped_presentation.py` (intentional).
- §1 Where-to-find-things: added 3 rows for memory / workbench / §11 personal-folders; reworded "Routing for new content" to split shared agent docs (maintainer-only) from personal user content (workbench / memory / scratchpad).
- Syntax-checked all three harness scripts (`ast.parse` clean). `python harness/build_inline_chart.py --help` confirms `--out` wired.

**T8 (Step 9 — pending).** Commit + push. Scope: only paths under `NFE/projects/3_shipping_data_mart/shipping-agent/`. Working-tree has parallel-session changes elsewhere — staging by-path, not `-A`.

**T9 (Step 9 done).** Staged the 41 scoped paths (`git add -u shipping-agent/` for tracked deletions plus the new `_about.md` + `.gitkeep` files). Initial stage failed because `.gitignore` `workbench/**` block was suppressing the subfolder `.gitkeep`s — fixed by adding `!workbench/<sub>/` directory negations before the file negations, then re-staged. Commit `f892257` on `origin/main`, pushed cleanly (GitHub flagged 145 unrelated dependabot vulnerabilities on default branch, unrelated to this work). 41 files changed, +547/-2144.

**T10 (post-implementation: DB Schenker meeting prep).** Principal pivoted to drafting a meeting question on DB Schenker — meeting in 25 min, anchored on `bi-analytics-main/NFE/shipping_topics/38_ups_de_cost_investigation_apr_2026/`. Read project 38 CLAUDE.md (last touched 2026-05-11, ends with "too early to call" post-May-8 routing-change check). Found untracked post-May-11 work: `dbs_carrier_migration.py` + `data/dbs_carrier_migration_since_may9.xlsx` (run 2026-05-15). Recovered the May-15 conclusion from the xlsx: of 523 DBS shipments since May 9, only 13% migrated from UPS, 37% were already DBS, 46% are new baskets with no pre-Dec-8 predecessor → the May-8 routing change probably did *not* dump UPS-DE volume into DBS as intended. Drafted a context-loaded refresh question covering three reads (did UPS-DE drop, where did the flow actually go, what's the cost on the new home) — phrased as scaffolding an investigation at `workbench/investigations/zv-130cm-routing-aftermath/`. **This is the first real-use cue for the new personal-folders model.** Question is in chat for principal to fire at the shipping-agent before the meeting.

**T11 (close-session).** Ran the ritual. Spawn-decision: principal-self (below all thresholds). No pending external actions. Resume file updated. Harvest produced 1 skill draft for Jebrim — "scope creep during plan execution" — capturing the silent-doc-sync vs surface-on-code-change calibration from T7. Surfaced. Committing now.

**T12 (alching pass).** Light alching pass post-close. Identity drafts empty; bank notes current; budgets fine. Created 1 examine draft (`2026-05-22-check-artifact-mtimes-doc-not-source-of-truth.md`) anchored on T10's project-38 stale-CLAUDE.md catch. Held the scope-creep skill draft in drafts/ — single-occurrence, below the ≥2 threshold. Updated `last-alched.md`. Committed `d53056d`.

**T13 (real-use validation — first instance).** Principal returned from meeting (or partway through) with a real shipping-agent session bug: a basket-build query joined `fact_shipment_orderitems` and `LISTAGG`'d without pre-aggregating by SKU. Output rendered as `CVS0750501F2 x1; CVS0750501F2 x1; ...` instead of `5 x CVS0750501F2`. The other agent caught and fixed in-line, but the gap was that the shipping-agent's docs didn't carry the basket-construction pattern at all. Patched core docs:
- `skills/query-patterns.md`: new section "Example — building a basket string per shipment (or per order)" with canonical shipment + shop-order SQL, format rules (`; ` separator, `qty x SKU`, desc-by-qty sort), the bucketing rule (default = full SKU), and a rationale paragraph naming the unit-vs-line grain variation by `source_system`.
- `reference/tables.md`: added gotcha under `fact_shipment_orderitems` — `quantity` per row is not reliable as the per-SKU count; same SKU can appear in multiple rows (unit-level split vs line-level rollup, varies by source); always pre-aggregate `SUM(quantity)` grouped by `(shipment_id, sku)` or `(shop_ordernumber, sku)` before formatting / matching / counting. Cross-references `skills/query-patterns.md`.

This is the **first real-use validation** of the new shipping-agent model — exactly the validation arc the inventory resume predicted ("First real session validates §0 rules 16–28; any rough edge → draft an adjustment"). The rough edge wasn't a §0 rule — it was missing reference content. The model worked correctly (the agent attempted the work, the principal noticed the bug, the maintainer-Jebrim is patching the docs from outside). System loop closing as designed.

**T14 (next-session investigation noted).** Same shipping-agent session also surfaced a second DQ correlation worth investigating: shipments with `trackingnumber LIKE 'temp%'` have ~25% missing orderitems (vs 0.08% on real tracking). Cross-carrier, varies by source (Picturator `temp*` ~26-30% missing; PicaAPI `temp*` 40-69%, PicaAPI × MAERSK worst at 68.8%). Working theory from the other agent: `temp*` is a placeholder before real carrier label assignment; orderitems backfill once real tracking posts; spine lands first, items follow. Principal asked this be noted for next-session investigation. Probe ordernumber: `MFA19911824351`. Full follow-up brief lives in `inventory/shipping-agent-personal-folders-resume.md` § Open threads. Two possible deliverables flagged: (a) confirm/refute the backfill theory by tracking `temp%` shipments over 24/48/72h, and (b) the other agent offered to add a `tracking_is_temp` boolean to its export or update the broader DQ reference doc — principal didn't pick. Surface again when investigation opens.

## Where we are

[[S029_2026-05-22_shipping-agent-vocab-harvest|S029]] ran a design conversation that landed a complete plan for converting the shipping-agent into a **standalone product** with **personal user folders**. The plan is below — implementation hasn't started. The next session opens fresh in `bi-analytics-main` and does the file work.

## The model

The shipping-agent is a standalone product. Niklavs builds and ships the **core**; other users pull updates. Each user has **local-only personal folders** inside the agent that survive `git pull` cleanly (gitignored).

## Folder layout to build

```
shipping-agent/
├── how_to.md, reference/, skills/, harness/, README.md, CLAUDE.md  ← CORE
│
├── workbench/                  ← PERSONAL — active work (gitignored)
│   ├── _about.md               ← shipped (template/rules)
│   ├── projects/               ← long, structured, ongoing
│   ├── investigations/         ← open-ended diagnostic
│   └── analysis/               ← bounded studies, date-stamped slugs (`20260522-tcg-uk-rates/`)
│
├── memory/                     ← PERSONAL — durable findings (gitignored)
│   └── _about.md               ← shipped
│
└── scratchpad/                 ← PERSONAL — transient one-offs (gitignored)
    └── _about.md               ← shipped
```

**Gone:** `visualization-studio/` — delete entirely. Outputs colocate with the workbench item that produced them (`workbench/<type>/<slug>/outputs/`) or land in scratchpad.

## Each workbench item structure

```
workbench/<type>/<slug>/
├── CLAUDE.md           ← reproducibility doc — load-bearing (see template below)
├── sql/                ← every query used, date-stamped (`20260522-01_baseline.sql`)
├── data/               ← snapshots only for comparative findings (else skip)
├── notebooks/          ← marimo / scripts / pipeline.py
└── outputs/            ← final charts, bundles, reports
```

**CLAUDE.md template per item:**

```markdown
# <item title>

**As of:** YYYY-MM-DD
**Status:** open | parked | closed
**Type:** project | investigation | analysis

## What this is
One paragraph — the question, the deliverable, who's asking.

## Method
- Data source: shipping_mart.* (cost_source distribution at run time)
- Time window
- Filter scope
- Key transformations
- Queries used (paths)

## Findings
- Headline numbers, hypothesis confirmed/refuted.

## Reproduction recipe
Stepwise instructions to re-run. Expected runtime, expected output match.

## Decisions made
The load-bearing choices (rule references, scope choices, framing).

## Open / next probe
Empty when closed; populated when parked or open.
```

## Reproducibility tiers (target by save location)

| Save location | Tier | What's captured |
|---|---|---|
| `scratchpad/` | None — promote if reproducibility matters |
| `workbench/<item>/` | **Tier 2** minimum (queries + decisions + summary) up to **Tier 1** (with snapshot data) |
| `memory/` | **Tier 3** minimum — citation inline: `Source: workbench/.../sql/X.sql @ YYYY-MM-DD` |

Snapshot data only when the finding is comparative (e.g., "April spiked vs March"). Current-state findings rely on recipe + live mart.

## Agent behavior rules (add to `how_to.md` §0 — likely as rules 16+ on top of today's 15)

**Scaffolding / saving:**

1. **Multi-session work → offer a workbench scaffold.** Detection is heuristic — user language signals (*"investigate," "look into," "figure out why," "project,"* etc.) or work that touches multiple queries on the same subject. Don't scaffold silently — but if it's obvious, do.
2. **Less prompting, more action.** When the destination is obvious (e.g., user asks for a chart and there's an active workbench item), act silently. When confirmation is needed, **trailing question after the response, not blocking before:** *"saving this into [active investigation X] — say if you want it elsewhere."*
3. **User-facing language stays plain.** Don't ask *"scratchpad or analysis?"* — ask *"save it?"* (default scratchpad). If the work is clearly bigger: *"this looks like an investigation — start a folder for it?"* The internal classification is the agent's job.
4. **Durable findings → offer a memory entry** with the same trailing-question pattern. *"…and I'll note this in memory if you want it next session."*
5. **Outputs colocate with workbench items.** Tied to active work → inside that item. One-off → ask once *"save it?"* (default chat-only / scratchpad).
6. **Quick one-offs default to chat (Mode 1).** No file written unless asked.

**Reproducibility (writes happen silently):**

7. **Every query on workbench-tied work saves to `sql/<date>-<NN>_<slug>.sql`** automatically. Header comment names the question.
8. **CLAUDE.md updates mid-session, silently.** Findings + Decisions sections grow as findings land. No review prompt — too blocking.
9. **Memory entries cite source** inline at bottom: `Source: workbench/.../sql/X.sql @ YYYY-MM-DD`.
10. **Snapshot data only for comparative findings.** Else recipe + live mart suffices.

**Session-end detection:**

11. **Agent watches for session-close cues** and offers wrap-up at that moment (Claude doesn't know when the conversation ends).
    - **Cues:** *"thanks," "great," "ok cool," "lets stop here,"* substantive deliverable lands with no follow-up, user pivots to an unrelated topic.
    - **On cue:** *"this feels like a closing point for [topic X] — wrap up the docs?"* If yes → fill CLAUDE.md (Findings, Reproduction recipe, As-of stamp), commit any promotions.
    - If user keeps going, re-test for next cue. No nagging.

**Promotion:**

12. **Scratchpad → workbench/memory promotion** when the agent notices a scratchpad file referenced repeatedly. Promotion **retro-fills metadata** — asks for context once, creates `sql/` + `CLAUDE.md` shell, then moves the file.

**Cleanup:**

13. **Scratchpad is user-managed.** No auto-sweep, no close-session prompts. User cleans when they want.

## Boot story (reactive)

No proactive onboarding on fresh clone. Triggered on user help-language: *"how do I use this?"*, *"what can this do?"*, *"where do I start?"*, *"help."* On trigger, agent surfaces:
- The three personal folders + what each is for.
- The offer-not-block scaffolding pattern.
- "Ask me anything about shipping" prompt.

Otherwise the agent acts normally — no first-run prompts.

## `.gitignore` to add at agent root

```
workbench/**
!workbench/_about.md
!workbench/projects/.gitkeep
!workbench/investigations/.gitkeep
!workbench/analysis/.gitkeep

memory/**
!memory/_about.md

scratchpad/**
!scratchpad/_about.md
```

## Workbench-type heuristics

| Shape | Triggers | Examples |
|---|---|---|
| **`projects/`** | Multi-stakeholder, deliverable-driven, weeks-to-months | "TCG-UK lane redesign" |
| **`investigations/`** | Question-driven, hypothesis-iterative | "Why did DB Schenker break in December?" |
| **`analysis/<date>-<slug>/`** | Bounded, single deliverable | "Compare DHL vs UPS April 2026" |

Promotion between types is fine when scope shifts.

## Concrete next steps (in order)

The next session opens in `bi-analytics-main` (working directory the shipping-agent), reads this plan, then:

1. **Delete `visualization-studio/`** entirely (including any untracked content under it from parallel sessions — confirm with principal first).
2. **Scaffold the three personal folders** with `_about.md` files in each:
   - `workbench/_about.md` + subfolders `projects/`, `investigations/`, `analysis/` (each with `.gitkeep`).
   - `memory/_about.md`.
   - `scratchpad/_about.md`.
   The `_about.md` files explain the folder's purpose, the conventions (date stamps, slug naming), and the agent's behaviors that use the folder.
3. **Add `.gitignore` entries** at the shipping-agent root per the block above.
4. **Rewrite `how_to.md` §7 (output modes) and §8 (artifact rules)** to:
   - Drop all `visualization-studio/` references.
   - Point at `workbench/<item>/outputs/` for tied outputs.
   - Point at scratchpad for one-offs.
   - Reorganize Mode 2/3/4 paths accordingly.
5. **Add §0 cross-cutting rules 16–28** (or similar numbering) for the 13 personal-folder behavior rules above.
6. **Add a §11 (or wherever fits) routing block** describing the three personal folders, the workbench item structure, the CLAUDE.md template per item.
7. **Verify the routing rule changes integrate** with existing rules (especially rule 2 / translation table — the new folders should not be exposed in user-facing text by their internal names; users see "saved" / "filed" / "noted" not "workbench/investigations/<slug>").
8. **Update the translation table** if needed to handle workbench/memory/scratchpad user-facing language.
9. **Commit + push** as `shipping-agent: personal folders + reproducibility model` (or similar).

## Files to read first when picking up

1. This quest-log entry — the plan.
2. `players/jebrim/inventory/shipping-agent-personal-folders-resume.md` — sibling resume.
3. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — the current core to rewrite.
4. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/README.md` — human onboarding.
5. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/_about.md` — what reference/ holds.

## What NOT to touch in `bi-analytics-main`

The bi-analytics-main working tree at handoff time has uncommitted/untracked work from a parallel "shipping cost rework" session. These are NOT part of this quest — leave them alone, scope commits carefully:

- ` M AGENTS.md, CLAUDE.md, GEMINI.md, GROK.md` (parallel session edits to pointer files)
- `?? harness/query_to_csv.py, query_to_xlsx.py` (parallel session's helper scripts)
- `?? visualization-studio/content/charts/claude/*`, `content/generated/claude/*` (parallel session's chart outputs — these get deleted with the visualization-studio removal, but confirm with principal first)

Use `git add` with specific paths under `shipping-agent/` for the personal-folder work; don't `git add -A`.

## Decisions locked during [[S029_2026-05-22_shipping-agent-vocab-harvest|S029]] design conversation

- Standalone agent product model (core vs personal split).
- 3 personal dirs: workbench / memory / scratchpad. visualization-studio removed.
- workbench has 3 subfolders: projects / investigations / analysis (with date-stamped slugs for analysis).
- Per-workbench-item structure with `CLAUDE.md` as reproducibility load-bearer.
- Reproducibility tiers defined per save location (Tier 1 / 2 / 3).
- AI summary writes silently (no review prompt).
- Snapshot data only for comparative findings.
- Memory entries carry inline `Source:` citation.
- Promotion from scratchpad retro-fills metadata.
- Session-end detection cue list.
- Scratchpad user-managed (no auto-sweep).
- Onboarding reactive (triggered on help-language), not proactive.
- First-scaffold-offer wording: leave natural (no fixed template).

## Open considerations to surface during implementation

- **Cross-user permissions / team scope.** Mentioned in [[S029_2026-05-22_shipping-agent-vocab-harvest|S029]], not resolved. Whether memory/ might need encryption or just stays plain markdown. Probably plain markdown for now; flag if a user pushes back.
- **The `data/` snapshot disk-cost question.** Comparative snapshots in `data/` could grow. If it becomes a real issue, add a cleanup rule. Defer until real use.
- **AGENTS.md / GEMINI.md / GROK.md sync.** Today they're tiny pointer files routing to how_to.md. When how_to.md grows substantially (which it will), check whether the pointers need updating to mention the new personal folders.

## Why this lives in Jebrim's quest-log

The shipping-agent is Jebrim's working surface (per `keepsake/current.md` routing pin). All design + implementation work on it accumulates here. When this quest closes, it'll graduate to `quest-log/completed/` with SNNN prefix, and any durable methodology might bank-graduate at next alching.

## Related

- `bank/notes/projects/shipping_agent_vocab_harvest_2026-05-22.md` — [[S029_2026-05-22_shipping-agent-vocab-harvest|S029]] vocab harvest already applied to the agent.
- `bank/notes/projects/dashboard_and_shipping_agent_convergence.md` — sibling note on dashboard vs agent.
- `examine/confirmed/2026-05-22-drafts-need-lead-with-concrete-example.md` — drafting protocol applied during the design conversation.
- [[S029_2026-05-22_shipping-agent-vocab-harvest|S029]] quest-log (completed) — the design conversation context.
- bi-analytics-main `c48bac6` — last shipped state of the agent before this quest.
