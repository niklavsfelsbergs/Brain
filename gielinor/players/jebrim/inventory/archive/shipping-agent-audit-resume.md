# shipping-agent audit — resume

**Status:** queued. Birth-session next.

## Where we are

Niklāvs queued a general audit of the `shipping-agent/` package at the close of S032, after a long harvest session that integrated 17 caveats into the agent's reference docs (see `bi-etl-shipping-mart-harvest-resume.md`). The trigger was partly the harvest itself (it exposed how the agent's docs are structured and routed) and partly a late-session observation that the running shipping-agent hallucinated pre-cutover language ("silver-layer mart," "7 silver-layer tables," "Sendmoments" as an entity scope) despite the docs being gold-explicit.

## Location

**The agent now lives at `Documents/GitHub/shipping-agent/`** (relocated at S032 close, 2026-05-22) and is its own git repo at **https://github.com/niklavsfelsbergs/shipping-agent** (initial commit `ba3d998` on `main`). The old location at `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/` is **still present and tracked in bi-analytics-main**, pending principal-authorized removal. See *Pending actions* below.

## Next concrete step

Run a general review of the shipping-agent package at `Documents/GitHub/shipping-agent/`. Goal: identify what would put the agent off course, what's friction, what's bloat, what won't perform well in real use.

Niklāvs' framing (verbatim):

> *"an audit of the shipping agent. Generally to review it, will it perform well, whats not great, whats too much, whats gonna put it off course, whats gonna cause friction, etc, etc"*

Possible angles (not exhaustive — pick on read):

- **Document weight vs read-cost.** `how_to.md` is now 469 lines with 29 cross-cutting rules. Anything redundant, contradictory, or low-leverage enough to remove? Is the always-loaded surface too heavy for the value it provides?
- **Rule conflicts and stale cross-refs.** After the recent renumbering and additions, do all the "see §0 rule N" pointers still resolve correctly? Are rules 1-15 (answer-shape) actually orthogonal, or do some collapse together?
- **Hallucination surface.** Why did the agent freehand-generate stale layer language when the docs are gold-explicit? Is the §11 boot story underspecified? Are there other places where the agent would default to prior-knowledge over reading docs (TCG composition? source priority list? bucket vocabulary?)?
- **Onboarding ergonomics.** First-session experience — does the agent know where to start? Is `how_to.md` actually the first thing it reads (per `CLAUDE.md`'s pointer), or does its model-prior win? The hallucination is one data point that the answer is "model-prior wins."
- **Operational surface.** Personal folders (workbench / memory / scratchpad) — clean conceptually but is the structure actually used well? Any anti-patterns in how the agent routes work into them?
- **Reference layer signal-to-noise.** `coverage-audit.md`, `known-dq.md`, `sources.md` — are the LIVE-vs-STABLE markings and `last-verified` stamps doing real work, or theater?
- **Scope guardrails.** `how_to.md` §10 is strict on perimeter. Does it actually hold when the agent is under pressure to answer? Any cases where the agent might step outside?
- **Skills coverage.** `skills/query-patterns.md` — sufficient for the common cases? Is the agent likely to reach for it when it should, or default to freehand SQL?
- **Per-assistant shims.** `AGENTS.md` / `GEMINI.md` / `GROK.md` — do they all cleanly point at `how_to.md`, or has drift crept in?

## Files / paths to read first

All paths below are at the new location `Documents/GitHub/shipping-agent/`.

1. This file.
2. `bi-etl-shipping-mart-harvest-resume.md` — context on what just landed in the docs.
3. `Documents/GitHub/shipping-agent/CLAUDE.md` — the entry shim.
4. `Documents/GitHub/shipping-agent/how_to.md` — full read; the load-bearing rules + index.
5. `Documents/GitHub/shipping-agent/README.md` — the human-facing summary.
6. `Documents/GitHub/shipping-agent/reference/_about.md` + the 5 reference files (`mart-contract.md`, `tables.md`, `sources.md`, `known-dq.md`, `coverage-audit.md`).
7. `Documents/GitHub/shipping-agent/skills/_about.md` + `skills/query-patterns.md`.
8. Each `*_about.md` for the personal folders (`workbench/`, `memory/`, `scratchpad/`).
9. `Documents/GitHub/shipping-agent/AGENTS.md` / `GEMINI.md` / `GROK.md` — verify the per-assistant shims point cleanly at `how_to.md`.

## Method shape (proposal — open to revision when the quest opens)

Two-pass audit:

1. **Read everything once** without writing anything. Build a mental model. Note tensions, redundancies, hallucination risks, friction points, and "this is going to bite" patterns as a flat list in inventory.
2. **Cluster + rank** the findings by leverage. Each finding becomes a one-line proposal with location + fix shape. Surface in chat for Niklāvs to triage (recommend / maybe / probably not, same pattern that worked for the S032 caveat harvest).

Don't propose fixes during pass 1 — that biases the reading. Pass 2 is where the synthesis happens.

## Watch-outs

- **Don't touch the docs during the audit.** Read-only until findings are validated. The harvest just made changes; an audit that immediately makes more changes muddies the diff.
- **The agent runs in another window.** Niklāvs uses the shipping-agent as a working tool. Don't disrupt anything operational — audit findings go to the brain (this resume + quest-log); the agent's package is read-only during the audit unless a fix is explicitly approved.
- **Resist new-file bias.** The harvest already taught the lesson: read the routing rule before recommending new files. Same for the audit — findings route into existing files first, new files only when no existing home fits.
- **Hallucination as a category, not a bug.** S032 ended with an observed hallucination (stale layer language despite clean docs). Treat that as one data point of a broader category — *where else might the agent default to model-prior over docs?* — not a single bug to swat.

## Seed findings (pre-audit, surfaced at S032 close)

One concrete §8 violation pattern observed before the audit even opened — worth investigating as a finding category.

### §8 scatter at package root — the rule isn't holding in practice

Three artifacts at the agent's package root, all created within the last 24 hours despite `how_to.md` §8 ("Don't scatter files outside the personal folders") being in force:

| File | Created | What it is |
|---|---|---|
| `canvas_qty_cost.csv` | 2026-05-21 23:50 | 13-row breakdown — canvases-per-parcel × shipments × avg cost |
| `fuel_share_3carriers.csv` | 2026-05-22 00:53 | 31-row monthly fuel surcharge % series |
| `data/cost_ratio_trend.sql` + `.csv` | 2026-05-22 10:46 | Gold-schema-aware reusable query + its output |

**Mechanism.** `harness/query_to_csv.py` has `--out` as a mandatory `required=True` flag — no default destination. Whoever invoked it explicitly typed `--out canvas_qty_cost.csv` (root) instead of `--out scratchpad/<slug>.csv` or `--out workbench/<item>/data/<slug>.csv`. The §8 violation was an active routing choice, not a harness default leaking out.

**Two hypotheses for the audit to disambiguate:**

1. **Agent-in-session violation.** The agent ran the harness in response to a "give me a CSV" ask and defaulted `--out` to a convenient root-level path instead of:
   - Defaulting Mode 1 (chat only, no file), or
   - Routing to `scratchpad/<timestamp>--<slug>.csv` per §8 + §0 rule 22, or
   - Asking *"save it?"* and routing to scratchpad on yes (the canonical §0 rule 18 pattern).
   - If true, the audit should examine: does the agent actually internalize §8 when invoking harness tools? Is there a gap between the rule text and the agent's behavior? Are there other §8-violation patterns elsewhere (e.g., the agent writing notes to repo root rather than `memory/`)?
2. **Niklāvs operating the harness directly** — typed `python harness/query_to_csv.py --out canvas_qty_cost.csv` from package root without going through the agent. The agent rules don't bind a human; this would be human-cwd-convenience.
   - If true, the harness itself could help with a §8 guardrail: validate `--out` and warn when the path is at package root (*"--out path is at the package root — §8 says outputs should go to `scratchpad/` or `workbench/<item>/`. Pass `--force-root` if you really meant it."*). Friction-reducing rather than blocking.

**Either way, two broader audit angles fall out of this:**

- **Rule-to-behavior gap as a category.** If §8 isn't holding in practice, what other rules might be paper-only? §0 rule 16 (transit/delivery DQ caveats — just added) is a candidate to spot-check. §0 rule 10 (schema perimeter) less so, since `ship_mart_ro` enforces it architecturally. The audit should look for the pattern, not just instances.
- **Harness ergonomics as enforcement.** Where the rule is hard to follow, the harness can make it easier. `--out` requiring explicit path is good (forces a decision); not warning on root-path destinations leaves the §8 escape hatch wide open. Other harness scripts (`build_inline_chart.py`, `build_light_html_presentation.py`) have `--out`-equivalent flags — same scrutiny applies.

## Pending actions (from the relocation)

Done at S032 close (kept here for traceability — `~~strikethrough~~` = done):

1. ~~**Initialize the new location as a git repo.**~~ DONE — `git init -b main`; initial commit `ba3d998`.
2. ~~**Create the GitHub remote.**~~ DONE — repo at `niklavsfelsbergs/shipping-agent` (personal account, not Picanova org). Remote added, pushed.
4. ~~**Audit the new top level for leftover scatter.**~~ DONE — added 4 entries to `.gitignore` (`.claude/settings.local.json` + `canvas_qty_cost.csv` + `fuel_share_3carriers.csv` + `data/`). All four were ad-hoc query outputs from before the workbench/ pattern was in force; kept local. The `data/cost_ratio_trend.sql` is well-formed and gold-schema-aware — flagged for possible promotion into `skills/` or `memory/` if it earns it during normal use.

Still pending — principal-authorized when ready:

3. **Remove the old location from `bi-analytics-main`.** `git rm -r NFE/projects/3_shipping_data_mart/shipping-agent`, commit (`Move shipping-agent out to its own repo`), push. **Safe to do now** — the new repo is pushed and working. Held only because it's a destructive action on a shared repo and the principal hasn't explicitly green-lit it.

Possible audit-time consideration:

- **Org vs personal account.** Repo lives at `niklavsfelsbergs/shipping-agent` (personal). If Picanova ownership matters (other analysts using it, succession, governance), transfer to the `picanova` org via GitHub settings → Transfer ownership. Low-priority unless the team grows around the tool.

## Birth-session SNNN

To be assigned when the audit quest is opened (next session).
