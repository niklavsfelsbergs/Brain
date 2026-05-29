# Opus 4.8 + dynamic workflows — substrate knowledge

> **What this is.** Reference knowledge about the model substrate the brain runs on, captured [[S119]] (2026-05-29, dev-brain consultation, sid 86344868) when the principal asked "what's new in 4.8." Anchors plan [[§Q]] (dynamic workflows as a fan-out engine for the brain). Sources at the foot — all official Anthropic docs unless noted.

## The model we run on

Opus 4.8 (`claude-opus-4-8`), released **2026-05-28**. The real Opus, not a downgrade; this session runs the **1M-context** variant (`claude-opus-4-8[1m]`). Builds on Opus 4.7, **same standard pricing** ($5/$25 per MTok). 128k max output, adaptive thinking, same tools/platform features as 4.7.

### What changed vs 4.7 (relevant to how we operate)

- **Better tool triggering** — less likely to skip a tool call the task required (a real 4.7 complaint). *Directly hits our chronic failure mode:* the discipline layer is tool/hook-dependent (posting the OPEN, intent files, ritual steps). Fewer skipped required calls = fewer missed ritual steps.
- **~4× less likely to let its own code flaws pass unremarked** — the headline honesty/quality gain. Aligns with the brain's verify-it-fires / test-the-claim culture; fewer broken hooks shipped.
- **Better long-context + compaction handling** — fewer derailments after a compaction. Matters for our long build/quest sessions on 1M context.
- **Adaptive-thinking calibration** — wastes fewer thinking tokens at the same effort by deciding per-turn whether to think.
- **Lower misaligned-behavior rates** (deception/misuse), reportedly near Claude Mythos Preview.

### Levers

- **Effort defaults to `high`** on all surfaces incl. Claude Code. This is the **free** speed knob: lower effort = faster + less quota burn, at some quality cost on hard tasks. Reach for it on grunt work; keep high for design/debugging. (Contrast fast mode below, which costs extra.)
- **Fast mode** (`/fast`, research preview) — same Opus, up to ~2.5× output tokens/sec. **NOT free on subscription:** draws from **usage credits** (billing *beyond* the plan), charged at the fast-mode rate ($10/$50 MTok on 4.8) from the first token, even with plan usage remaining. Requires usage credits turned on; **disabled by default for Team/Enterprise** (admin must enable) — likely relevant on the `@tcgroup.com` corporate account. Persists across sessions once toggled (unless org sets `fastModePerSessionOptIn`). Enable at session *start* (mid-conversation flip pays fast-rate for the whole existing context). Falls back to standard automatically when credits/rate-limit run out. **Verdict: a pay-extra-for-speed lever, not a free default.**
- **Mid-conversation system messages** — `role:"system"` after a user turn; append instructions late without restating the system prompt, preserving prompt-cache. API-builder feature; minor for the interactive brain.

## Dynamic workflows (the `Workflow` tool) — the genuinely new capability

A `Workflow` tool runs a **JavaScript orchestration script** in the background, spawning many subagents under deterministic control flow. The plan lives in script variables, not the context window — only the final answer returns to the session. The scripted-fan-out engine the brain has hand-rolled (the [[S110_144c0ca2_brain_full_audit|S110]] 5-crew audit, §O migration sweeps, bankstanding Phase 0).

- **Primitives:** `agent(prompt, opts)` (one subagent; opts: `schema` for validated structured return, `agentType` to target our typed crew — dwarf/gnome/penguin/Explore/shipping-agent — `model`, `isolation:'worktree'`), `parallel([thunks])` (concurrent, barrier), `pipeline(items, …stages)` (per-item streaming, no barrier — the default), `phase()`/`log()`, `workflow()` (nest one level).
- **Limits:** ≤16 concurrent agents, 1,000 total per run. Requires Claude Code **v2.1.154+**. Research preview.
- **Triggering:** the word `workflow` in a prompt; or `/effort ultracode` (= `xhigh` + automatic workflow orchestration every substantive task). Bundled `/deep-research` is one. Runs are saveable as `/<name>` commands (`.claude/workflows/` or `~/.claude/workflows/`).
- **Resumable** within the same session (completed agents return cached results); exiting Claude Code restarts it fresh.
- Scripts are plain JS and **cannot** call `Date.now()`/`Math.random()` (would break resume) — pass timestamps via `args`.

### BILLING (the §Q.1 gate — answered, GREEN)

Official doc, verbatim: **"Runs count toward your plan's usage and rate limits like any other session."** Workflow subagents **ride the subscription quota** — NOT metered separately, NOT the headless `claude -p` path (the post-2026-06-15 metering is about how Claude is *launched*; a workflow launched from the interactive cockpit PTY rides the plan). 

**Caveat (cost, not a blocker):** cost scales **linearly with agent count** — "a single run can use meaningfully more tokens than working through the same task in conversation." A 200-agent fan-out burns the Pro/Max quota fast. Control: route routine stages to a smaller model (`/model`), scope workers tightly, lower per-stage effort. **Available on all paid plans incl. Pro** (enable via `/config` → Dynamic workflows; an early secondary source wrongly said Max/Team/Enterprise-only — the official doc overrides).

### The open governance question (the §Q.2 gate — still open)

Workflow subagents **"always run in `acceptEdits` mode and inherit your tool allowlist, regardless of your session's mode. File edits are auto-approved."** So the permission layer is OFF inside a workflow → **our PreToolUse hooks are the only remaining write guard.** Whether `require-open-on-entry.py` (D-033) + the 4 write-boundary hooks fire inside a workflow (do they see `payload.agent_type`?) is now load-bearing, not nice-to-have. PreToolUse hooks *should* still fire under acceptEdits (that mode governs prompting, not hook execution) — but this is exactly the verify-it-fires case to confirm empirically before letting a workflow write brain content. See plan [[§Q]].

## Sources

- Introducing Claude Opus 4.8 — https://www.anthropic.com/news/claude-opus-4-8
- What's new in Claude Opus 4.8 (API docs) — https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8
- Speed up responses with fast mode (Claude Code docs) — https://code.claude.com/docs/en/fast-mode
- Orchestrate subagents at scale with dynamic workflows (Claude Code docs) — https://code.claude.com/docs/en/workflows
- Secondary (corroborating): TechCrunch, VentureBeat, MarkTechPost launch coverage (2026-05-28/29).
