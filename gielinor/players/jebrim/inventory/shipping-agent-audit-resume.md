# shipping-agent audit — resume

**Status:** queued. Birth-session next.

## Where we are

Niklāvs queued a general audit of the `shipping-agent/` package at the close of S032, after a long harvest session that integrated 17 caveats into the agent's reference docs (see `bi-etl-shipping-mart-harvest-resume.md`). The trigger was partly the harvest itself (it exposed how the agent's docs are structured and routed) and partly a late-session observation that the running shipping-agent hallucinated pre-cutover language ("silver-layer mart," "7 silver-layer tables," "Sendmoments" as an entity scope) despite the docs being gold-explicit.

## Location

**The agent now lives at `Documents/GitHub/shipping-agent/`** (relocated at S032 close, 2026-05-22). The move was a copy — the old location at `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/` is **still present and tracked in bi-analytics-main**, pending principal-authorized removal. See *Pending actions* below.

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

## Pending actions (from the relocation)

These need to happen before or during the audit — non-blocking on the audit itself, but worth doing early:

1. **Initialize the new location as a git repo.** `cd Documents/GitHub/shipping-agent && git init && git branch -M main`. Stage everything respecting `.gitignore` (personal folders + `.env` + cruft like `__pycache__`, loose CSVs at root, `data/`). First commit: `Initial commit — extracted from bi-analytics-main/NFE`.
2. **Create the GitHub remote.** Suggested: `picanova/shipping-agent` (private). Empty repo on github.com, then `git remote add origin ... && git push -u origin main`.
3. **Remove the old location from `bi-analytics-main`.** `git rm -r NFE/projects/3_shipping_data_mart/shipping-agent`, commit (`Move shipping-agent out to its own repo`), push. **Do this only after** the new repo is pushed and confirmed working, so there's no window where the agent has no canonical home.
4. **Audit the new top level for leftover scatter.** The copy carried over `__pycache__/`, `data/`, `canvas_qty_cost.csv`, `fuel_share_3carriers.csv` at the package root — those are §8-violation files that should either be gitignored or relocated to `scratchpad/` before first commit. Per `how_to.md` §8 "Don't scatter files outside the personal folders."

## Birth-session SNNN

To be assigned when the audit quest is opened (next session).
