# Research — skill

How to gather and synthesize external information so the output is anchored, navigable, and honest about what's known vs inferred.

## When this fires

**Explicit cues.** *"Let's research X"*, *"scout Y"*, *"look into Z"*, *"what's the state of <topic>"*.

**Implicit triggers.** Any question that needs current external information (post-cutoff news, regulatory state, vendor pricing, library status) or multi-source synthesis (comparing options, building a working model of an external system).

If the answer is one quick lookup, just look it up — don't run the full skill. The skill is for work where the *shape* of the answer matters: source-traceable, navigable later, defensible.

## Two modes — principal-self vs penguin-spawn

The skill is invocable by **both** the principal and a penguin sub-agent. Same methodology, different invocation:

- **Principal-self.** Quick lookups, single-cluster topics, when the principal is already in the right context. The principal runs the skill directly.
- **Penguin-spawn.** Heavy research, parallel clusters, anything that would crush principal context. The principal spawns one or more penguins per `spawning-penguins.md`. Penguins inherit the principal's player by default; cross-player override is explicit (*"have a penguin look into X for Zezima"*).

Heuristic: spawn when the source map looks like it'll need >5 fetches, or when there are ≥2 independent clusters. Otherwise principal-self.

## Tool surface

- `WebSearch` for source discovery and current-state sweeps.
- `WebFetch` for primary-source reads.

Nothing else by default. Adding MCPs is a per-skill amendment.

## Source discipline — pragmatic

Pragmatic means **honest about provenance, not religious about citations**.

- Every claim that *has* a source gets one — URL or repo path, inline.
- Quote-then-summarize for primary sources when exact wording matters (regulations, contract terms, version-pinned docs). Paraphrase otherwise.
- Inference is allowed — but flagged. Use inline markers: *(inferred from X+Y)*, *(recalled, not sourced)*, *(deduction)*. The principal can then choose to probe.
- A claim with no source and no inference flag is a bug. Add the flag or pull the source.

The point isn't bureaucracy. It's that six weeks from now neither the player nor Niklavs should have to guess which line came from where.

## Decomposition — broad → narrow → synthesize

1. **Broad scout.** `WebSearch` the topic. Build a **source map** — what looks load-bearing: which docs, which authors, which dates, which official sources. Don't start summarizing yet.
2. **Narrow reads.** `WebFetch` the load-bearing sources. Pull quotes for anything that will be cited. Note dates and version-pinning where it matters (regulations as of YYYY-MM-DD; library docs at vX.Y).
3. **Synthesize.** Write the findings up. Citations inline. Gaps and open questions called out explicitly — what couldn't be confirmed, what would change the picture, what's a known-unknown.

Skipping the source map and going straight to fetch-and-summarize is the most common failure mode. Without the map, you don't know what you're missing.

## Parallelism

When the source map shows ≥2 independent clusters (regulatory vs vendor vs internal-system, etc.), defer to [[spawning-penguins]] — one penguin per cluster. Each penguin returns its writeup; the principal weaves the synthesis.

Single-cluster research stays single-threaded. Don't spawn for the sake of spawning. And don't use dwarves for external research — that's penguin work; dwarves are repo-scoped.

## Output

Lands in the **active player's** `research/` per `meta/layer-routing.md`. Filename `YYYY-MM-DD-<topic-slug>.md`. No draft gate inside the folder — write freely. (When a penguin is the author, the boundary hook restricts them to this folder anyway; for principals, the discipline is the same.)

Distillation into `bank/drafts/notes/` happens during alching, not at research time. The research file stays as the anchor; the bank note carries the picked-out load-bearing claims. Cross-link the bank note back to the research file when picked.

Body shape (a guide, not a template to fill mechanically):

- **Question.** What was being asked.
- **Date of research.** YYYY-MM-DD (sources age fast; the date matters).
- **Confidence.** High / medium / low — based on source quality and gap size.
- **Sources.** Bulleted list with title, URL, and one-line *"what this is, why it's load-bearing."*
- **Findings.** Prose, bullets, or sections as the material warrants. Inline citations and inference flags.
- **Gaps & open questions.** What couldn't be confirmed. What would change the picture if discovered. Known-unknowns. One line is fine if nothing surfaced.

If the findings are one paragraph, don't pad them into sections. The shape exists to anchor; it does not exist to be filled.

## Anti-patterns

- **Uncited synthesis.** Three paragraphs of conclusions with no URLs. Either find the sources or mark the whole thing as inference.
- **One Google and a guess.** A single search result is a starting point, not research.
- **Source-volume cosplay.** Twelve URLs cited, none read past the first paragraph. Depth beats breadth.
- **Stale-date amnesia.** Pulling 2019 numbers as if they're current. Date-check primary sources.
- **Skipping the source map.** Going straight to summary loses the principal's ability to see what was *not* read.
- **Spawning for the sake of it.** A single coherent cluster doesn't need penguins. The [[spawning-penguins]] heuristic still gates.
- **Writing into bank directly.** Research output goes into `research/`. Bank notes are *picked* from research during alching. A research file that bypasses `research/` and lands in `bank/drafts/notes/` loses the source anchor.

## Related

- `meta/layer-routing.md` — where research outputs land and how distillations get picked into `bank/`.
- `spawning-penguins.md` — the spawn heuristic this skill defers to for parallel work.
- `meta/modes.md` — the penguin write boundary.
- `meta/communication-protocol.md` — Understanding/Plan preamble still applies; research-mode doesn't bypass it.
