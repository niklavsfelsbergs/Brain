# S088 — 2026-05-25 — Worktree isolation for parallel sessions (decision)

Dev-brain via "lets develop gielinor", mid-conversation; OPEN posted (braindead-f731b4e8). A design talk, not a build.

- **The question.** Principal asked whether parallel multi-session work has *real gates* or relies on agents obeying markdown — and how to make multiple agents work the same problem smoothly. Audited the machinery: collision-avoidance is **almost entirely discipline** (`comms/active.md`, leaks ~70% per the recurring "did not post an OPEN" note) plus one **advisory** signal (the [[D-020_terminal_switchboard]] status sidecar — read to decide, never blocks). The one hard mechanism, session-suffix filenames ([[D-024_parallel_player_coordination]]), only covers **own-file** surfaces. The hard case — two sessions editing the **same shared file** — has no gate, and the log documents it as unworkable (S042/cbbf8de8 Edit-retry-hell; the S057/S059/S060 manual hunk-handoff-over-comms workaround).
- **The direction (principal chose).** Adopt **git worktrees** so parallel agents never share a working file — reconcile at *merge* (visible, resolvable) not at *Edit-tool time* (silent lost hunks). The Agent tool already exposes `isolation: "worktree"`.
- **The load-bearing rule captured:** *isolate what you EDIT (code, hooks, `meta/`), share what you COORDINATE THROUGH (`comms`, intent, status).* Else the comms channel forks per-worktree and the board goes blind.
- **The precondition surfaced:** a hook-path audit — repo-relative hook writes (intent files, `switchboard/state-*`) would make worktree sessions invisible to the cockpit (the [[S052_98d4ec5e_switchboard-rebuild]] `CLAUDE_PROJECT_DIR` lesson resurfacing). This blocks the interactive-session build; sub-agent `isolation:"worktree"` is usable today with zero build.
- **Artifact.** Wrote [[D-030_worktree_isolation_for_parallel_sessions]] capturing diagnostic + decision + precondition + phasing + open questions (comms-sharing mechanism, cockpit worktree awareness, merge convention). Build deferred — principal will pick it up later.

**Cascade.** New `bank/decisions/D-030_worktree_isolation_for_parallel_sessions.md`; `respawn.md` (next-step + Last-updated); `comms/active.md` (OPEN + CLOSING); this quest entry; `.claude/active-mode.txt` toggled dev-brain→unscoped.

**Main-brain changes.** none — no `gielinor/` writes this session (pure dev-brain decision capture).
