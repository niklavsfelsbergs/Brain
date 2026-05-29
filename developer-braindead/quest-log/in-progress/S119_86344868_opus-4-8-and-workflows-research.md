# S119 — Opus 4.8 substrate + dynamic-workflows research

**Session.** sid 86344868. Dev-brain via "lets develop gielinor", mid-conversation. OPEN posted (discussion-only initial scope), UPDATE posted on the pivot to a doc write. Sibling braindead-e0a88f49 (S118, item-6 freshness) flagged stale-intent but principal confirmed **live-but-idle** → no ABANDONED synthesis, steered clear of its surfaces.

## What was asked

Principal asked which model this session runs (→ Opus 4.8, 1M context, `claude-opus-4-8[1m]`), then "what's new in 4.8 vs 4.7," then drilled into **fast mode** (can I use it / setup / drawbacks) and **dynamic workflows** (the new fan-out capability), then asked to research **how workflows are billed**.

## What was done

- **Researched 4.8 vs 4.7** (official Anthropic news + API docs + Claude Code docs, corroborated by launch coverage). Findings: better tool triggering, ~4× fewer self-unremarked code flaws, better long-context/compaction, effort defaults to `high`, fast mode, mid-conversation system messages.
- **Fast mode — corrected my own wrong guess** (I'd assumed it just burns subscription quota faster). Ground truth: on subscription it draws from **usage credits** (billing beyond plan) at the fast rate from the first token; disabled by default for Team/Enterprise (admin-gated — relevant to the corp account); persists once toggled. A pay-extra lever, not a free default. Principal said "disregard that."
- **Dynamic workflows** — sketched the real `Workflow` tool contract (pipeline/parallel/agent over typed sub-agents) against our model; parked as plan **[[§Q]]** with two verify-first unknowns.
- **§Q.1 billing — RESEARCHED + ANSWERED (GREEN).** Official workflows doc: *"Runs count toward your plan's usage and rate limits like any other session."* Rides the subscription; not separately metered; linear cost with agent count. Available on all paid plans incl. Pro. Marked §Q.1 `[x]`.
- **§Q.2 sharpened** — workflow subagents run in `acceptEdits` (permission layer off) → our PreToolUse hooks are the *only* in-workflow write guard; confirming they fire is now load-bearing.

## Artifacts

- `bank/research/2026-05-29-opus-4-8-and-workflows.md` — the durable substrate-knowledge note (the principal's "keep knowledge of 4.8").
- `bank/plan.md` §Q added (capability + 4 fits + 2 unknowns); §Q.1 closed with the billing finding; §Q.2 sharpened.
- This quest-log entry.

## Open / not done

- **NOT committed** (principal: "not yet").
- §Q.2 (do our hooks fire inside a workflow) remains the open empirical gate before any workflow writes brain content — a proper build/verify session.
- Pre-existing carries unchanged: `meta/write-rules.md` "enforced by hook" godly proposal at next bankstanding.

## Notes

- Item 4 (5-lens) turned out built in parallel by S120 (885d6702) — visible as the new five-lens section in `gielinor/meta/communication-protocol.md`; not this session's work.
- Principal's standing concern: he'll forget the workflow capability exists → asked me to surface it when relevant. Delivered as a cross-conversation `feedback` memory (heuristic disposition, not a hook; brain-session-scoped). Declined the global `~/.claude/CLAUDE.md` line.

**Cascade.** `bank/plan.md` (§Q added; §Q.1 billing answered `[x]`; §Q.2 sharpened) · `bank/research/2026-05-29-opus-4-8-and-workflows.md` (new substrate note) · this quest-log entry · `bank/build-lessons.md` (fast-mode inference lesson) · `comms/active.md` (OPEN + UPDATE + CLOSING) · `respawn.md` (S119 prepend). Cross-conversation memory (outside the repo): `~/.claude/projects/.../memory/feedback_suggest_dynamic_workflows_when_fanout.md` + `MEMORY.md` pointer.

**Main-brain changes.** none — no `gielinor/` writes this session (the five-lens edit in `gielinor/meta/communication-protocol.md` was S120/885d6702, not S119).
