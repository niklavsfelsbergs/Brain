# Agentic-OS gap survey — what comparable systems do that the brain doesn't

> **Provenance.** [[S102_3b333c4d_agentic_os_gap_survey]] (braindead-3b333c4d — SNNN claimed behind the confirmed-taken [[S099_acf8fc80_obsidian_quest_link_migration|S099]]/acf8fc80 + [[S101_transcript_as_sole_comms_surface_feasibility|S101]]/be7867be; sid8 is the unambiguous anchor under heavy parallel load), 2026-05-26. Principal cue: *"reflect on the brain and research agentic operating systems in a similar direction as mine. What is very useful which I am not utilizing?"* — Obsidian (see [[obsidian-fit-and-migration-spec]]) was the worked example of a previously-unknown-but-useful adoption.
>
> **Method.** Three parallel research scouts (WebSearch/WebFetch), each calibrated against the brain's *current* state so findings are **gaps, not echoes**: (A) agent memory & cognitive architectures, (B) personal-AI / second-brain tooling + PKM practice, (C) agentic-dev frameworks & autonomous operation. Synthesised against the layer model + [[D-027_inward_outward_build_imbalance]].
>
> **Sibling context at write time.** Parallel to [[S098]]'s Obsidian link migration (acf8fc80) and a cockpit-transcript feasibility pass (be7867be). Read-only on the brain; this note is the only artifact. Companion to [[2026-05-26-rag-for-the-brain]] (RAG, parked §N) and [[obsidian-fit-and-migration-spec]] (Obsidian, §O).

---

## Headline — the convergent finding

All three scouts, from different literatures, landed on the **same diagnosis**:

> The brain has world-class memory **structure** (it's a near-perfect CoALA instance — semantic/episodic/procedural/working + self-model + user-model) and world-class **governance** (drafts→confirmed gating, archive-never-delete, multi-actor). What it lacks is the **dynamics layer**: scoring, decay, scheduled reflection, resurfacing, and self-evaluation. And almost every missing piece can be added as a **propose-only background pass that respects the existing drafts→confirmed gate** rather than bypassing it.

The sharpest single reframe:

> **The brain is all *inbox*, no *producer*.** Its `drafts/ → confirmed/ (+ rejected/)` flow is structurally *identical* to the "human-in-the-loop agent inbox" pattern the field converged on in 2025 (Accept / Edit / Reject — LangChain agent-inbox, ChatGPT Tasks review loop). The brain built the entire **review** half years early. What's missing is the **autonomous producer** that fills the inbox without a human starting the conversation.

This is the same gap [[D-027_inward_outward_build_imbalance]] names ("manual-invocation-only"), seen from the memory side. It reframes the §C build: the scheduled-trigger *mechanism* is a shared beam under **two** producers — the outward §C shipping-mart check **and** an inward draft-only self-tending pass.

---

## Gap inventory

Value×effort are rough calls. "Brain status" judged against the layer model: **no** / **partial** / **has it**.

### Tier 1 — the missing dynamics layer (high value)

| # | Mechanism | Exemplar (source) | Brain status | Adoption sketch (Claude-Code-native) | V×E |
|---|---|---|---|---|---|
| 1 | **Scheduled / ambient autonomy + agent-inbox** — an autonomous producer fills a review queue; human approves async | LangChain *ambient agents*; ChatGPT Tasks; LangGraph agent-inbox (Accept/Edit/Respond/Ignore) | **partial** — the *review* half exists (`drafts/`→`confirmed/`, `/drafts`, `players/inbox/`); the autonomous *producer* + a one-screen inbox view do not | `cron`/Routine → a Claude run produces drafts/digests; surface a consolidated "everything waiting for you" at respawn. `/drafts` is ~80% of the consumer side already | **High × low–med** |
| 2 | **Retrieval scoring: recency × importance × relevance** — rank what to surface, don't grep-and-guess | Stanford Generative Agents memory stream; ACT-R activation; LIDA's attention step | **no** — retrieval is keyword-relevance only (grep + `[[links]]`); `keepsake/` is the only crude importance signal | `importance:` front-matter + a cheap scorer (git mtime + importance + grep-hit density) ranks `bank/notes/` + recent quest-logs at query/respawn time. **No embeddings** — this is the missing *attention* step, not RAG | **High × med** |
| 3 | **Spaced resurfacing / incremental writing** — periodically re-read confirmed knowledge to keep it live and refine it | SuperMemo incremental reading/writing; Logseq SM-5; digital-garden tending | **no** — the single biggest second-brain gap; confirmed notes are never revisited | `last-reviewed:` field + a weekly ritual surfacing N due notes to *re-read and propose refinements* (interval grows when reaffirmed unchanged, resets when revised). Pairs with #1's schedule | **High × med** |
| 4 | **Self-evaluation by mining the `rejected/` pile** — LLM-as-judge over the preserved rejection corpus | Agent-as-a-Judge / LLM-as-judge (binary scoring best practice); LangSmith Align Evals | **no** — `archive-discipline.md` *explicitly* keeps rejections as drift-detection data, and **nothing reads it back** | A binary judge-gnome ("would this be approved?") scores new drafts vs. the rejected set, catching weak drafts before the human sees them; also scores quest-log trajectories vs. ritual specs. A latent asset sitting unused | **High × med** |

### Tier 2 — cheaper wins, same gate-respecting shape

| # | Mechanism | Exemplar (source) | Brain status | Adoption sketch | V×E |
|---|---|---|---|---|---|
| 5 | **Auto-suggested links between notes** | Obsidian Smart Connections (local embeddings, block-level "related notes"); Reor (link-at-write-time) | **no** | Either drop Smart Connections into the Obsidian vault being adopted (free, local, no un-parking RAG) **or** a Claude "propose `[[links]]`" pass that lands link suggestions as proposals. Improves agentic retrieval directly | **High × low** (plugin) / **med** (pass) |
| 6 | **Periodic reflection synthesis** — auto-draft higher-level insights on a cadence | Generative Agents *reflection*; Reflexion (task-local self-critique) | **partial** — `lorebook/` D-NNN *are* synthesised insights, but human-triggered + scoped to operating-decisions | Threshold trigger (N new quest-logs / M importance-points → reflect) inside #1's pass; drafts cross-cutting insights into `lorebook/drafts/` or `deities/guthix/bank/drafts/`. Makes bankstanding's cross-cutting intent fire automatically | **High × med** |
| 7 | **Evergreen revision + maturity states** — revise notes in place; label maturity | Andy Matuschak evergreen notes; Maggie Appleton seedling/budding/evergreen | **partial / a real tension** — brain leans append-then-archive, not revise-in-place; no link-density discipline | `maturity: seedling\|budding\|evergreen` field; reframe alching to *revise existing notes*, not only add drafts. Closes the append-only-vs-evergreen tension and gives #2/#3 a target | **Med–high × med** |
| 8 | **Temporal fact invalidation (bi-temporal)** — make the archive discipline queryable + auto conflict-detect | Zep / Graphiti bi-temporal KG | **partial** — archive-never-delete *is* the spirit of invalidation, but not machine-readable; conflicts are human-noticed at alching | `valid_from` / `superseded_by` / `invalidated_on` front-matter; consolidation auto-detects a draft contradicting a confirmed note and proposes the dated archive move. No graph DB — the `[[links]]` graph + dates approximate it | **Med × med** |
| 9 | **A standing critic actor** — separate-agent critique before a deliverable surfaces | Reflexion / actor-critic; blackboard critic agents; best practice = *separate* critic, not self-critique, capped retries | **no** (for output quality; memory-reflection exists) | A new sub-agent role (or a Guthix pass) reviews a SQL query / Slack draft against a rubric, 1–2 retries max. Strong fit — the brain is already multi-actor | **Med–high × med** |
| 10 | **Reflexion task-local learning buffer** — carry "what went wrong" into the next attempt of the *same* task | Reflexion | **partial** — quest-logs narrate; no structured per-task correction buffer | On retry, write `inventory/<quest>-lessons.md`; respawn/resume injects it. A fast loop below the slow lorebook loop | **Med × low** |

### Validation (not gaps — confirm the architecture is sound)

- **CoALA** ([arXiv 2309.02427](https://arxiv.org/abs/2309.02427)) — the brain's layer model is a near-perfect instance; it even has self/user-model layers CoALA doesn't formalise. Use as an audit rubric. The one thing CoALA is more explicit about: retrieval as a *scored internal action* in a plan→evaluate loop = exactly gap #2.
- **Agent Skills + progressive disclosure** (Anthropic, open-sourced Dec 2025) — the brain *predates the standard* (CLAUDE.md @imports, `_about.md`-on-first-access, per-player `spellbook/skills/`). Minor tightening available: a metadata-first "when to use this" header on skills so they're discovered by relevance.
- **PARA** (Forte) — quest-log / keepsake+bank / archive is already a PARA isomorphism. Sanity-check only (is a standing "SCM monitoring" an Area, not a perpetual Project?).

---

## What NOT to adopt (already have, or deliberate)

- **RAG / embeddings** — parked §N ([[2026-05-26-rag-for-the-brain]]); correct call. The brain is already an agentic-search system; the dynamics gaps above need *no* embeddings to start.
- **Obsidian graph/backlinks/Dataview** — §O, in progress.
- **Memory taxonomy / multi-agent fan-out / observability** — has it (observability is *over*-built per [[D-027_inward_outward_build_imbalance]]).
- **AGENTS.md cross-tool standard** — Claude-Code-native is a deliberate non-goal; portability isn't wanted. One-line awareness note, no migration.
- **Self-editing identity memory (MemGPT memory blocks)** — the brain's `examine/`/`keepsake/`/`niksis8/` are the "Persona/Human" blocks, but *human-gated by design*. Keep the gate; only a *volatile* working-self block in `inventory/` is a safe net-new self-edit.

---

## The governor — headless billing

Every Tier-1 autonomous pattern runs through a non-interactive trigger, and the brain's own memory records the **headless billing constraint**: `claude -p` / Agent-SDK runs are metered; the interactive terminal stays on subscription (the reason the cockpit drives via a real PTY). Open feature request [anthropics/claude-code#4785](https://github.com/anthropics/claude-code/issues/4785) wants native scheduled hooks — not shipped; OS-cron + headless is the sanctioned workaround today.

Two clean implementation forks (decide deliberately, don't default):
1. **Cheap-model scheduled passes** — run the draft-only/eval passes on Haiku; escalate to interactive only for human review.
2. **PTY-on-a-timer** — drive the scheduled pass through the cockpit's PTY (the same subscription-preserving trick), not headless.

Also note the cron-env gotcha: cron doesn't load the shell profile, so MCP auth/env must be set explicitly (the [[S052]] `CLAUDE_PROJECT_DIR` lesson, again).

---

## Relation to the existing roadmap

- **§C / §F (triggers)** — the scheduled-trigger mechanism this survey keeps pointing at *is* §C.4 / §F.2. Build once; power the outward shipping check **and** an inward draft-only self-tending pass. The inward one is arguably safer to ship first (writes only drafts → zero outward side effect).
- **§J (rituals)** — alching / bankstanding / drafts-triage already write *only proposals*, so they are **safe to run unattended**. The Tier-1 "sleep-time pass" is mostly "run an existing ritual on a timer, draft-only" — only the trigger is missing.
- **§N (RAG)** — gap #2 (retrieval scoring) is a *cheaper precursor*: a heuristic activation score over file metadata, no embeddings. Could satisfy much of §N's intent before any embedding build.
- **§E (gates)** — gap #4 (eval) + #9 (critic) are §E.3 (sub-agent verification) and §E.4 (dry-run), finally with content.

---

## Suggested single first move

If one thing: **the scheduled draft-only "sleep-time" pass feeding a consolidated inbox** (gaps #1 + #3 + #4 together). It's the one build that simultaneously closes the manual-invocation gap, delivers automatic consolidation + resurfacing, and stands up the first eval loop — all inside the existing gate, so it's safe. It also de-risks §C by exercising the trigger mechanism on a zero-side-effect job before pointing it at production data.

---

## Proposed `plan.md` §P stub (deferred — see sibling note)

> **Not landed this session.** `plan.md` is live under acf8fc80's [[S098]] link-rewrite (already 327 rewrites applied; S060-dupe disambiguation pending). Editing it now is the [[D-024_parallel_player_coordination]] Edit-race. Paste-ready text below; land after acf8fc80 CLOSINGs, or hand to them to carry.

```markdown
## §P — Agentic-OS dynamics layer (parked 2026-05-26)

**Status.** `[ ]` parked — surveyed, ranked, parked **behind §C**. Full survey + sources in
`bank/research/2026-05-26-agentic-os-gap-survey.md` ([[S102_3b333c4d_agentic_os_gap_survey]]).

Headline: the brain has the memory **structure** + **gates** but no **dynamics** layer
(scoring, decay, scheduled reflection, resurfacing, self-eval). Reframe: the brain is
**all inbox, no producer** — `drafts/`→`confirmed/` IS the HITL agent-inbox pattern; the
missing half is an autonomous producer in front of it. Shares the §C/§F scheduled-trigger
mechanism. Governor: the headless billing constraint (run cheap-model or PTY-on-a-timer).

- §P.1 `[ ]` **Scheduled draft-only "sleep-time" pass + consolidated inbox** — the flagship; runs an existing ritual (alching/bankstanding) on a timer, draft-only, surfaced at respawn. De-risks §C.
- §P.2 `[ ]` **Retrieval scoring** recency × importance × relevance via `importance:` front-matter + heuristic scorer. Cheaper precursor to §N (no embeddings).
- §P.3 `[ ]` **Spaced resurfacing** of confirmed knowledge — `last-reviewed:` + weekly due-note review.
- §P.4 `[ ]` **Self-eval mining the `rejected/` corpus** — binary LLM-as-judge; first eval loop (§E.3).
- §P.5 `[ ]` Tier-2: auto-suggested links, periodic reflection synthesis, maturity states + evergreen revision, bi-temporal invalidation, standing critic actor.
```

---

## Sources

**Memory & cognitive architectures:** MemGPT/Letta sleep-time ([letta.com/blog/sleep-time-compute](https://www.letta.com/blog/sleep-time-compute)) + memory blocks ([letta.com/blog/memory-blocks](https://www.letta.com/blog/memory-blocks)); Generative Agents ([arXiv 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)); Mem0 ([arXiv 2504.19413](https://arxiv.org/pdf/2504.19413)); Zep/Graphiti ([arXiv 2501.13956](https://arxiv.org/html/2501.13956v1)); Reflexion ([arXiv 2303.11366](https://arxiv.org/abs/2303.11366)); Voyager ([arXiv 2305.16291](https://arxiv.org/abs/2305.16291)); CoALA ([arXiv 2309.02427](https://arxiv.org/abs/2309.02427)); SOAR/ACT-R/LIDA (cognitive-architecture literature).

**Second-brain tooling & PKM:** Khoj automations ([docs.khoj.dev/features/automations](https://docs.khoj.dev/features/automations/)); Smart Connections ([smartconnections.app](https://smartconnections.app/smart-connections/)); Reor ([github.com/reorproject/reor](https://github.com/reorproject/reor)); Mem.ai; Tana supertags; Logseq SM-5 flashcards; Zettelkasten atomicity ([zettelkasten.de/atomicity/guide](https://zettelkasten.de/atomicity/guide/)); Matuschak evergreen notes ([notes.andymatuschak.org/Evergreen_notes](https://notes.andymatuschak.org/Evergreen_notes)); LYT MOCs; Appleton maturity states ([maggieappleton.com/evergreens](https://maggieappleton.com/evergreens)); Dataview health queries ([resurface notes with Dataview](https://efemkay.medium.com/resurface-your-obsidian-notes-with-these-dataview-queries-97f254c6c9c5)); PARA ([fortelabs.com/blog/para](https://fortelabs.com/blog/para/)).

**Agentic frameworks & autonomy:** LangChain ambient agents ([langchain.com/blog/introducing-ambient-agents](https://www.langchain.com/blog/introducing-ambient-agents)); agent-inbox ([github.com/langchain-ai/agent-inbox](https://github.com/langchain-ai/agent-inbox)); ChatGPT Tasks ([help.openai.com](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)); Claude Code headless + scheduled-hooks request ([issue #4785](https://github.com/anthropics/claude-code/issues/4785)); AGENTS.md vs CLAUDE.md ([hivetrail.com](https://hivetrail.com/blog/agents-md-vs-claude-md-cross-tool-standard)); Agent Skills + context engineering (Anthropic eng blog); GitHub Spec Kit ([github.com/github/spec-kit](https://github.com/github/spec-kit)); LLM-as-judge ([langchain.com/articles/llm-as-a-judge](https://www.langchain.com/articles/llm-as-a-judge)); Anthropic multi-agent research system ([anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system)); blackboard multi-agent ([arXiv 2507.01701](https://arxiv.org/pdf/2507.01701)).
