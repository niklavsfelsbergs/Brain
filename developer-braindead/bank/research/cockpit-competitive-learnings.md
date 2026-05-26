# Cockpit — competitive learnings & parked backlog

> Parked 2026-05-24 (dev-brain session, sid 89f41770). Principal asked: *"what could we learn from the other solutions that would improve mine?"* then *"park these ideas."* Not committed to build — candidate features for the `cockpit/` line ([[D-028_switchboard_cockpit_rebuild]]), to weigh against the [[D-027_inward_outward_build_imbalance]] inward/outward imbalance (don't out-build the commodity fleet board; spend beams on the world layer).

## Context

The multi-session agent cockpit is a crowded 2026 category. **Anthropic shipped the board half themselves** — Claude Code **Agent View** (research preview, May 2026): CLI dashboard, one row per live session, four signals (session id / waiting-on-you / last assistant response / last-interaction timestamp), answer-inline-and-resume, `/bg` + `claude --bg` background sessions; plus the **desktop redesign** (Apr 2026): multi-session sidebar, drag-drop layout, integrated terminal + file editor. Our board's four signals are nearly identical. Third-party: **Conductor** (macOS, parallel Claude/Codex, worktree-per-agent, inline diff review, reuses existing login = zero extra cost), **Vibe Kanban** (BloopAI, OSS; task-card kanban → launchpads, worktree isolation, in-UI diff review + PR), **Claude Squad**, **Crystal**, etc.

Strategic frame: the generic fleet view is now commodity Anthropic will maintain for free on subscription. Steal only what's a low-cost win **or** serves our world-model (players / Guthix / in-voice COMMS) — the part no other tool has.

## The four real steals

**1. Git worktree isolation — for *construction* sessions only.** (Conductor / Vibe Kanban / Agent Teams)
Each agent gets its own worktree + branch; no filesystem collisions. This directly kills the documented [[D-024_parallel_player_coordination]] shared-tree tax — "ceded the client files to the sibling's commit," uncommitted hunks riding the shared tree, [[S057_switchboard_awaiting_crew_state|S057]]→[[S067_5294143e_cockpit-terminal-interior-and-header-align|S067]] hand-offs via `comms/active.md`, SNNN renumbering races. **Precise cut:** worktree-isolate **dev-brain construction sessions** (Braindead siblings editing `cockpit/` + hooks — that's where ~all collisions are); keep the **shared tree for brain-content sessions** (players in separate namespaces rarely collide, and the shared tree is load-bearing for the one-world COMMS model). Highest-leverage, lowest-risk.

**2. In-cockpit diff review.** (Conductor / Vibe Kanban)
Review an agent's diff inline — click a line, comment, agent iterates — before push. We have read-only transcript peek but no diff surface, and every session ends in a commit-on-ask. A review mode on the third column = approve changes from the bridge instead of dropping to `git`. High fit; our flow already gates commits on principal approval.

**3. Inline-answer for WAITING rows.** (Agent View)
Answer a paused session from the board row without opening its terminal; row flips WAITING→WORKING. We have the WAITING state + bell already; missing half is piping a typed reply to that session's stdin. Across 10 sessions this is the "glance and clear" win. Cheap, high-frequency.

**4. Forward task queue.** (Vibe Kanban)
Cards = *queued tasks* carrying acceptance criteria + architectural constraints, drag-to-prioritize, launched into an agent. Our board is live-sessions-only. Backing store already exists (`quest-log`, `comms`); a queue column that spawns a pre-briefed session is mostly UI. Most "product-y," least urgent.

## Already ahead — don't let anyone sell these back

- **Compound learning.** Osmani's headline ("keep an AGENTS.md that accumulates patterns so each session improves the next") is the entire premise of gielinor — CLAUDE.md, banks, lorebook, voice cards. The field is reinventing a flat file; we have layered memory with promotion gates.
- **Specialization.** His "each agent only sees files it owns" = our dwarf/gnome/penguin write surfaces + player namespaces, hook-enforced. Worktrees would add the *physical* layer under a *conceptual* one we already run.

## Billing trap

Conductor/Vibe Kanban lean on **background** agents (`claude --bg`, headless workspaces). Post-2026-06-15 that's the **metered** path — headless `-p` / Agent SDK draws the capped API-credit pool, not the subscription. If we add background dispatch, keep it a **background interactive PTY** session (subscription), not headless. Same constraint that drove [[S066_7f5db8c5_cockpit-sweep|S066]]'s PTY pivot.

## Suggested sequence (if/when built)

1. Worktrees-for-construction (kills a recurring tax, pure win)
2. Inline-answer (cheap, daily)
3. Diff review (bigger build, high value)
4. Task queue (nice, least urgent)

## Sources

- Claude Code Agent View — https://claudefa.st/blog/guide/agents/agent-view ; https://pasqualepillitteri.it/en/news/2384/claude-code-agent-view-cli-dashboard-sessions-2026
- Claude Code desktop redesign — https://miraflow.ai/blog/claude-code-desktop-redesign-parallel-sessions-routines-workspace-guide
- Conductor — https://codepick.dev/en/guides/conductor-build-intro
- Vibe Kanban — https://vibekanban.com/ ; https://github.com/BloopAI/vibe-kanban
- Addy Osmani, The Code Agent Orchestra — https://addyosmani.com/blog/code-agent-orchestra/
- Claude Code worktrees docs — https://code.claude.com/docs/en/worktrees

## Related

- [[D-028_switchboard_cockpit_rebuild]] — cockpit rebuild (the build line these would extend)
- [[D-027_inward_outward_build_imbalance]] — inward/outward build imbalance (the lens: don't out-build the commodity board)
- [[D-024_parallel_player_coordination]] — parallel-session coordination (the shared-tree tax steal #1 targets)
- headless billing constraint (2026-06-15 metering) — the trap above
