# RAG for the brain — field survey + fit

> Read 2026-05-26 ([[S097]]?, dev-brain mid-conversation via "lets develop gielinor"). Principal asked: *what is a RAG system and how could it be utilized in my brain?* This is the survey + an honest fit assessment. **Conclusion up front: the brain is already an agentic-search retrieval system, which is the architecture the frontier coding agents converged on after trying and dropping RAG. If RAG comes in, it comes in narrow and additive — not as a grep replacement.**

## What RAG is

**Retrieval-Augmented Generation** — fetch relevant external text *before* the model answers and staple it into the prompt. Three stages:

1. **Embed** — chunk documents, turn each chunk into a vector (numbers encoding *meaning*), store in a vector DB (FAISS, Chroma, LanceDB, DuckDB-VSS, Pinecone).
2. **Retrieve** — embed the query the same way, pull top-*k* chunks by semantic similarity (often blended with keyword/BM25 = "hybrid"), optionally rerank.
3. **Generate** — feed query + retrieved chunks to the LLM so the answer is grounded in real source text, not the model's frozen weights.

Payoff: answers reflect *your* corpus, stay current without retraining, and are auditable (you can see which chunk fed the answer). It is the #1 enterprise LLM pattern as of 2025–26.

## Variants (and how each maps onto things the brain already has)

| Flavor | What it adds | Brain parallel |
|---|---|---|
| **Naive RAG** | keyword/embedding top-*k*, static index | — |
| **Agentic RAG** | an agent plans, picks retrievers, *iterates* queries | **the brain already does this** (grep → read → follow `[[link]]` → re-query) |
| **GraphRAG** | extracts entities/relations into a knowledge graph, traverses it | the `[[wiki-links]]` (`D-NNN`, `S-NNN`) **are already a graph** |
| **Agent memory** | working / episodic / semantic memory that learns over sessions | the layer model — `inventory/` / `quest-log/` / `bank/` |

Microsoft's **LazyGraphRAG** (2025) cut GraphRAG indexing cost to ~0.1% of full, making graph approaches practical at scale.

## The twist that matters for *this* brain

The brain runs inside **Claude Code**. Claude Code's creator has said early versions used RAG with a local vector DB — and **agentic search (grep, find, read, follow imports) beat it, so the vector DB was removed.** Cursor and Devin landed the same place. Reasons given:

- **No stale index** — searches the live corpus as it exists right now.
- **No embedding pipeline** to maintain, no security copy of content sitting in a vector store.
- **Follows reference chains** — grep can walk handler → utils → jwt; vector top-*k* can't follow an edge.
- In a SWE-bench study, grep/find were *sufficient and not the bottleneck* even where embeddings were expected to win.

So: **the brain is already an agentic-search retrieval system.** `@`-imports eager-load the rulebook; respawn loads `confirmed/` + `keepsake/current.md` + the latest quest-log; `layer-routing.md` is literally a *router*; `_about.md`-on-first-access is lazy retrieval; `[[links]]` are a graph traversed by reading. That is the architecture the frontier converged on *after* trying RAG. For a corpus this size, the brain is on the winning side of that bet.

## Where RAG would actually earn its keep here

Three spots where grep genuinely falls down and a semantic index adds something real:

1. **Bankstanding's cross-cutting pattern detection.** Its whole job is "the same underlying thing said three different ways across Jebrim, Zezima, and globals." That's *semantic* similarity — grep needs the exact word; embeddings find "differently-worded but about-the-same." **Strongest single fit.** (See [[D-027_inward_outward_build_imbalance]] — the inward/outward gap; this is an inward-capability sharpening, not the outward hands that gap is really about.)
2. **"What do I have on X" recall as the bank grows.** Today: grep + the operator remembering the right keyword. As `research/` and `bank/notes/` grow, grep misses relevant-but-differently-worded notes. Semantic recall fixes exactly that miss.
3. **Exploiting the link graph already built.** GraphRAG over the `[[D-NNN]]`/`[[S-NNN]]` web — the edges already exist; nothing mines them as a retrieval structure. "Everything two hops from D-027" is a graph query, not a grep. **Cheapest, most brain-native experiment** — parse-only, no embeddings, no API.

## Where it'd be the wrong beam to nail in

- **Small corpus, fast reader.** This is the regime where agentic grep wins; a vector DB now is weight for no lift.
- **Staleness vs. the write pattern.** Quest-logs append *every turn*; the never-delete rule means the corpus only grows. A vector index needs near-constant re-embedding to stay current. Grep is always live.
- **The gates would leak.** The architecture is *what you may read in which mode* (confirmed vs draft vs rejected; per-player; consultation-reads-all vs alching-reads-one). Naive similarity search flattens that unless layer/player/mode are encoded as metadata filters and enforced — real work, easy to get subtly wrong.
- **Substrate/billing.** Embeddings = a metered API call or a local model dependency. Given the headless-billing constraint (the cockpit drives a real PTY to stay on subscription), an embedding pipeline reintroduces the metered/extra-dependency surface the brain has been steering around.

## Recommendation

Don't replace grep. If RAG enters, **narrow and additive**: an optional semantic-recall index over the *stable, read-everything* surfaces (`bank/notes/`, `research/`, `confirmed/`), used as a **recall aid inside bankstanding and Guthix consultation** — the two modes that already read across everything and where "find the conceptually-related thing" is the actual job. Metadata-filter by layer/player so it respects the gates. Keep agentic grep primary everywhere else. **Poke the GraphRAG-over-`[[links]]` angle first** — cheapest, no embeddings, exploits structure that already exists.

## Plan (parked 2026-05-26) — phased adoption, gated on the Obsidian revamp

Parked, not building. Tracked as [[plan.md]] §N. The principal is mid-revamp to **enable Obsidian**, speced live in the parallel session **braindead-b53fca39** (`bank/research/obsidian-fit-and-migration-spec.md`). That session is not a vague "substrate" — its output is **literally Phase 1's input**. See the *Interlink* subsection below.

- **Phase 0 — gate: braindead-b53fca39's link migration applies (NOT merely "Obsidian installed").** The migration spec found stock Obsidian resolves `[[links]]` by **exact filename**, so the brain's dominant `[[D-027_inward_outward_build_imbalance]]`/`[[SNNN]]` links (files are `D-027_<slug>.md`) show as **phantom — only ~9% resolve out of the box**. b53fca39 **DECIDED Option A: a one-time full-stem link-TEXT rewrite** (`[[D-027_inward_outward_build_imbalance]]`→`[[D-027_inward_outward_build_imbalance]]`, no plugin, no file renames). Until that migration runs, Obsidian's link graph is ~91% phantom and **useless as a retrieval structure**. Phase 1 is gated on the migration, not on Obsidian being present.
- **Phase 1 — GraphRAG over `[[links]]` (cheapest, do first).** Post-migration, Obsidian maintains resolved-links + backlinks; "N hops from X" traversal for **bankstanding + Guthix consultation** reads *that* index (or the post-migration resolved link text). **No embeddings, no API, no billing surface.** Phase 1 **inherits b53fca39's classification semantics rather than rebuilding them** — `[[SNNN]]` resolving to many sub-entries (`_dN`/`_pN`/`_gN`, `-resume`) is a *by-design cluster*, not ambiguity; cross-brain/code-ref/dangling links are deliberately unresolved. **Per-brain vaults** (their decision: `gielinor/` and `developer-braindead/` separate) ⇒ graph traversal is per-brain; the 4% cross-brain links stay unresolved, so **"N hops" cannot cross the brain boundary**.
- **Phase 2 — semantic-recall index (only if Phase 1 proves the need).** Local embeddings (LanceDB / Chroma / DuckDB-VSS) over the *stable, read-everything* surfaces (`bank/notes/`, `research/`, `confirmed/`). Scoped to bankstanding + consultation. **Metadata-filter by layer/player/mode so the gates don't leak.** Prefer a local embedding model over an API call (headless-billing constraint). Evaluate an Obsidian community plugin (Smart Connections) as the build-vs-buy alternative before writing our own pipeline.
- **Phase 3 — wire as an MCP tool (additive).** Expose `semantic_recall(query, scope)` / `graph_neighbors(node, hops)` via `.mcp.json` so the agent calls retrieval *explicitly* and grep stays primary. Fits the existing MCP wiring + the Obsidian-vault substrate.

**Carried constraints:** respect the gates (metadata filter); handle staleness (Phase 1 leans on Obsidian's live cache; Phase 2 needs incremental re-index on write); keep billing off-meter (local model); **never replace grep — additive only.**

**Open decisions when unparked:** build-our-own vs an Obsidian plugin; local embedding model + vector store choice; re-index trigger; whether bankstanding auto-uses recall or the agent opts in per query.

## Interlink with the live Obsidian session (braindead-b53fca39)

The Obsidian revamp and this RAG plan are **the same graph approached from two ends.** Exact coupling, so neither session redoes the other's work:

1. **Their migration *is* my Phase 0/1 input.** Phase 1 "GraphRAG over `[[links]]`" reads the resolved-link/backlink index that only exists *after* b53fca39's Option-A full-stem rewrite. No migration ⇒ ~91% phantom links ⇒ nothing for Phase 1 to traverse. The gate is their migration applying, not Obsidian being installed.
2. **Their classification algorithm is my graph model.** The spec's resolver rules (ID-prefix→main entry; `_dN`/`_pN`/`_gN`/`-resume` as a by-design cluster under one session; cross-brain/code-ref/placeholder/dangling left unresolved) *define what a node and an edge mean*. Phase 1 inherits this, doesn't reinvent it.
3. **Per-brain vaults bound my retrieval scope.** Two separate vaults ⇒ per-brain graph; cross-brain links (4%) deliberately unresolved ⇒ "N hops from X" cannot cross the `gielinor/`↔`developer-braindead/` boundary. (Corrects this note's earlier singular-"the vault" phrasing.)
4. **Option A *helps* my agentic-grep path too.** Because the resolved graph lives in plain link *text* (no plugin), post-migration `grep "D-027_inward"` and Obsidian's backlinks agree — the markdown-as-index and the graph-recall paths reinforce each other instead of diverging. (Had they picked Option B / alias-plugin, the graph would've been locked behind a plugin and invisible to grep — worse for RAG.)
5. **Shared root: [[A-002]] + [[Q-001]].** A-002 ("wiki-links are load-bearing for *associative retrieval*") says replace-when-Q-001-lands. The two arms A-002 named are exactly these: **markdown-as-index** (b53fca39's link migration — being built now) and **embeddings** (this note's Phase 2 — parked). They are not competitors; the migration realizes the cheap arm first, and Phase 1 sits on top of it.
6. **Forward convention is shared integrity.** b53fca39's "IDs unique per brain, stop linking code files, sub-entries intentional" rules keep the graph clean — which is precisely what keeps a graph-recall index trustworthy. If link hygiene rots, *both* their backlinks and my Phase-1 traversal degrade together.
7. **Wait for their D-NNN.** The spec says a `D-NNN` will formalize the migration mechanism + convention. §N.0/§N.1 depend on *that* decision; until it lands, this plan references `obsidian-fit-and-migration-spec.md` directly.

**Net:** b53fca39 is doing Phase 0 right now under a different name. When their migration lands, Phase 1 becomes *parsing an index that already exists* — the cheapest possible start. Don't start Phase 1 before their D-NNN; don't build a link parser they're effectively already building.

## Decisions / assumptions this could inform

- A future decision on whether bankstanding gets a semantic-recall aid (currently pure read-across + agent judgment).
- The neuron-overlay / observability line — a link-graph parse is shared infrastructure between GraphRAG retrieval and any graph *visualization*.
- Does **not** move [[D-027_inward_outward_build_imbalance]]'s load-bearing gap (outward operability / the §C pilot). This is inward-capability research; flag if it ever competes for build time with the outward hands.

## Sources

- [IBM — What is RAG](https://www.ibm.com/think/topics/retrieval-augmented-generation)
- [Pinecone — Retrieval-Augmented Generation](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Agentic RAG: A Survey (arXiv 2501.09136)](https://arxiv.org/html/2501.09136v4)
- [From RAG to Agent Memory — Leonie Monigatti](https://www.leoniemonigatti.com/blog/from-rag-to-agent-memory.html)
- [Agentic RAG vs Traditional RAG — Mem0](https://mem0.ai/blog/agentic-rag-vs-traditional-rag-guide)
- [Why Cursor, Claude Code, and Devin use grep, not vectors — MindStudio](https://www.mindstudio.ai/blog/is-rag-dead-what-ai-agents-use-instead)
- [Why grep beat embeddings in our SWE-bench agent — Jason Liu / Augment](https://jxnl.co/writing/2025/09/11/why-grep-beat-embeddings-in-our-swe-bench-agent-lessons-from-augment/)
- [Building an Obsidian RAG with DuckDB and MotherDuck](https://motherduck.com/blog/obsidian-rag-duckdb-motherduck/)
- [MCP-Markdown-RAG — semantic search over markdown (GitHub)](https://github.com/Zackriya-Solutions/MCP-Markdown-RAG)
