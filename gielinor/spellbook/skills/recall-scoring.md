# Recall scoring — skill

Scored retrieval over the brain's markdown memory: a heuristic *attention signal* so an important note surfaces even when it doesn't match a keyword or sit in `keepsake/`. No embeddings, no manual tagging — every input is already on disk. Backed by the script `recall-scoring.py` in this folder.

## Why this exists

The brain retrieves by grep + `[[link]]`-following, and the model ranks relevance in its head. That works, but it has no cheap way to tell which note *matters most* across 435+ files — so a well-referenced but unpinned, quiet note silently never resurfaces. This adds the missing rank. It's the "attention step" the agentic-OS gap survey named (dev brain, [[S102_6217a8d5_eu-tender-fedex-reply-review|S102]]) — the cheaper precursor to any embedding/RAG layer, built first because it needs none.

## When this fires

**On-demand, principal- or Guthix-invoked.** Not a per-turn tool. Reach for it when the question is *"what across the brain is worth my attention right now"* rather than *"find me the file about X"* (grep already wins the latter):

- **Guthix consultation** — *"what important things haven't I revisited?"*, *"what do I have on X, ranked?"*
- **Bankstanding** — pick resurfacing candidates; spot high-centrality notes drifting unmaintained.
- **Pre-alching** — a player deciding which of its own durable notes are due a re-read.

If you already know the file, just open it. This is for ranking, not locating.

## Wiring status

**On-demand only (decided S126, 2026-05-29).** Not wired into any ritual. The validation pass found the `--surface` payoff (staleness) dormant on the young corpus, so auto-wiring into respawn/bankstanding buys little today — it'd add ritual load for a centrality ranking that partly overlaps what respawn already loads. **Revival trigger:** wire `--surface` into bankstanding Phase 0 once staleness differentiates — i.e., once durable notes routinely go quiet for weeks and the rank stops being centrality-dominated. Until then, invoke by hand or on a Guthix cue.

## The two modes

Recency pulls opposite ways depending on the job, so there are two:

```
python spellbook/skills/recall-scoring.py --surface [--top 15]
python spellbook/skills/recall-scoring.py --query "shipping cost mart" [--top 15]
```

- **`--surface`** (proactive). *"What important thing have I not looked at lately?"* Ranks **durable** knowledge (`bank/notes`, `*/confirmed`, `lorebook/confirmed`, `spellbook/skills`) by **centrality × staleness**, skipping already-pinned notes (they surface anyway) and the volatile floor (`archive`/`inventory`/`drafts`/`rejected`/`quest-log`). This is the gap the model can't fill in-session — it can't survey every file each respawn.
- **`--query "terms"`** (recall). Ranks notes **matching** the terms by **relevance × centrality × recency**. A pre-ranker for the consultation "what do I have on X" path.

## The signals

| Signal | Source | Meaning |
|---|---|---|
| **centrality** | backlink degree in the `[[link]]` graph | a note many others reference is important. The Obsidian densification (24%→74% connected) is what makes this real. |
| **recency** | git last-commit-time, exp-decay (30-day half-life) | recent = fresh. Uses *git* time, not filesystem mtime — a checkout stamps whole clusters with one time and collapses the signal. |
| **staleness** | `1 − recency` | old = due for a revisit. |
| **pinned** | stem appears as a `[[link]]` in any `keepsake/current.md` | already-surfaced; excluded from `--surface`, a small boost in `--query`. |
| **relevance** | query-term hit density | `--query` only. |

Output shows the component signals per result, so you can see *why* a note ranked — never a black box.

## Honest limits

- **Heuristic, not truth.** It's a spotlight, not a judgment. Read the notes it surfaces; don't act on the rank alone.
- **Staleness is dormant on a young corpus.** Validated 2026-05-29 (S126): at 9 days old, every durable note had changed within ~6 days, so `staleness` barely differentiated and `--surface` was effectively a centrality ranking. This is a *maturity gap*, not a bug — the staleness half activates on its own as notes start going quiet for weeks. Don't tune the half-life down to manufacture spread (that's fitting weights to noise).
- **No semantics.** Centrality and grep are structural/lexical; a topically-related note with no shared words and no link won't surface. That's the embedding/RAG layer (parked, dev brain §N), deliberately not built here.
- **Weights are tunable** — the constants at the top of the script (`W_SURFACE`, `W_QUERY`, `HALFLIFE_DAYS`). Recalibrate as the corpus matures.

## Related

- `recall-scoring.py` — the script (self-contained, stdlib only, read-only; no dev-brain import so a ritual can call it).
- The agentic-OS gap survey + this build's trace live in the dev brain (`developer-braindead/bank/research/`, [[S102_6217a8d5_eu-tender-fedex-reply-review|S102]] + S126).
- Companion skills: [[research]] (gathering external knowledge), [[spawning-penguins]] (heavy research fan-out).
