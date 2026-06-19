# Read the canonical source cold — don't operate from recall

**Observation (bankstanding [[B-021_2026-06-19_bankstanding|B-021]], 2026-06-19, step-3 cross-player synthesis).** The same reflex has stabilized independently in two players, which is the bankstanding signal to graduate it to the global layer:

- **Zezima** — [[2026-05-26-read-doc-cold-recurrence]]: read the document cold each time it recurs; a remembered gist is not a re-read.
- **Jebrim** — [[2026-05-29-read-domain-knowledge-before-proposing-mechanism]]: read the canonical domain reference before proposing a column/anchor/value, not the raw schema or memory. Reinforced in his own body file (`players/jebrim/CLAUDE.md` → *Don't reason about the mart from memory* — its contract/schema live in `shipping-agent/`, stale-by-default, re-read don't recall).

**The pattern.** When acting on a source the agent has seen before — a contract, a mart schema, a doc, a reference file — the default pull is to answer from the remembered shape of it. The reflex is to **re-open and read it cold first**, because the stored gist drifts from the live file (the file changed, the memory compressed lossily, or the recall is of a *different* instance). The cost of the cold read is one tool call; the cost of acting on stale recall is a wrong answer delivered with confidence.

**Why global, not per-player.** It is not about shipping data (Jebrim's frame) or personal docs (Zezima's frame) — it is about the agent's relationship to *any* external source-of-truth. It sits next to, but is distinct from, the keepsake grounding reflex (*"complete the cheap grounding precondition first"* — read the active **context** before output): this one is narrower and sharper — *the specific source you're about to cite, re-read it; don't cite from memory.*

**Rule.** Before citing or acting on a known external source, re-read it cold. Treat a remembered version as a hypothesis about the current file, not the file. Stale-by-default for anything outside the brain's own tree.

**Anchors.** [[2026-05-26-read-doc-cold-recurrence]] (Zezima), [[2026-05-29-read-domain-knowledge-before-proposing-mechanism]] (Jebrim), `players/jebrim/CLAUDE.md` shipping-mart precondition #2. Related warm-memory twins: `feedback_read_domain_knowledge_before_proposing`, `feedback_check_own_memory_before_working_repo`.
