# D-030 — 2026-05-25 — Worktree isolation for parallel sessions

> **Status: direction decided, build deferred.** Principal chose worktree isolation as the way to make multiple agents work the same problem; implementation is a follow-on session against this spec. This doc captures the diagnostic, the design, and the precondition so the build starts from a decided shape rather than re-deriving it.

## Context — what's actually gated vs. what's discipline

The trigger question (principal, S088 design talk): *do we have real gates making parallel multi-session work smooth, or are we relying on agents obeying markdown?*

Honest audit of the parallel-coordination machinery:

| Mechanism | Gate or discipline? | Covers |
|---|---|---|
| `comms/active.md` OPEN/CLOSING/`→ @`/UPDATE | **Discipline** (markdown) | Announcing territory, asking before touching. Leaks ~70% — the recurring *"did not post an OPEN"* note across the channel is the evidence. |
| Status sidecar `~/.claude/status/<sid8>.json` ([[D-020_terminal_switchboard]]) | **Real data, advisory** | Liveness (working / your_move / ended). You *read* it to decide to back off; nothing *blocks* on it (S042 used it to pivot off a hot file). |
| Session-suffix filenames `__<sid8>`, `SNNN_<sid8>_` ([[D-024_parallel_player_coordination]]) | **Real mechanism** | Clobber-proofs **own-file** surfaces only — inventory, in-progress quest-log. Each session gets its own file. |
| The six boundary hooks (deletes, confirmed, dwarf/gnome/penguin, sub-spawn) | **Real gates** | Write *surface* and *destruction*. **None addresses cross-session collision.** |

So collision-avoidance is almost entirely discipline plus one advisory signal. The one hard mechanism (suffixing) only covers surfaces where a session writes *its own* file. The genuinely hard case — **two sessions editing the same shared file** (`gielinor/meta/`, `CLAUDE.md`, `cockpit/web/switchboard.js`, `styles.css`, hooks) — has **no gate at all**, and the build log documents it as unworkable:

- **S042 / cbbf8de8:** three Edit attempts against `index.html` failed back-to-back as a sibling wrote between Read and Edit. Recorded lesson: *"interactive concurrent editing of the same file is unworkable with the current toolchain."*
- **The workaround that emerged (S057 / S059 / S060):** the session that lands hunks in a shared file can't `git add -p` non-interactively, so it applies its hunks to the shared working tree, *doesn't commit them*, and pastes the exact hunks into comms asking the sibling to carry them in their commit — *"re-land from this entry if a full-file rewrite drops them."* That is two agents hand-signaling across a shared workbench, not a gate.

[[D-024_parallel_player_coordination]] explicitly left "hook enforcement" and the same-file race out of scope; this decision picks up that thread.

## Decision — adopt git worktrees, with one split that must hold

Use git worktrees so parallel agents never share a working file. They reconcile at **merge** (git's job, where a real conflict is *visible and resolvable*) instead of at **Edit-tool time** (where it was never built to, and a lost hunk is silent).

**The load-bearing rule: isolate what you EDIT; share what you COORDINATE THROUGH.**

- **Isolate (the win):** `cockpit/`, `.claude/hooks/`, `gielinor/meta/`, `gielinor/spellbook/`, `CLAUDE.md`, `docs/` — the shared *code and structure*. This is precisely the Edit-retry-hell surface above. Two Braindeads on separate worktrees editing the same file no longer collide.
- **Keep shared (the friction):** `comms/active.md`, `.claude/intent/*.txt`, `~/.claude/status/*.json`. Comms exists for *live cross-session awareness* — if each worktree holds its own copy, siblings can't see each other's OPENs until merge, which defeats the channel. The sidecar is already shared + absolute (`~/.claude/`). **Intent files are repo-relative** — in a worktree, `.claude/intent/` is the *worktree's* dir, so the cockpit reading the main tree would not see that session at all.

## Precondition — the hook-path audit (the real cost)

The intent-file point above is the [[S052_98d4ec5e_switchboard-rebuild]] `CLAUDE_PROJECT_DIR` lesson resurfacing: *hooks that write repo-relative paths silently no-op when cwd isn't the main tree* (that bug is exactly why a subdir-launched session never showed on the board). **Worktree adoption is blocked on auditing every hook for repo-relative writes and pinning them to one absolute shared location** (the main tree, or `~/.claude/`). Until that audit lands, a worktree session would be invisible to the board and would fork the comms channel.

Audit targets (the writers): `status-sidecar.py`, `emit-event.py`, `emit-commit-event.py`, `rename-intercept.py`, and the `switchboard/state-*` mirror destinations. The `~/.claude/status/` writes are already safe; the repo-relative ones (`switchboard/state-*`, `.claude/intent/`) are the suspects.

## Phasing — now vs. needs-a-build

1. **Fan-out sub-agents — available today, zero build.** The Agent tool already accepts `isolation: "worktree"`. When fanning out dwarves that *edit* shared code (not just read it, as the S085/S086 recon dwarves did), spawn them isolated; each works a clean copy and changes return. Adopt as immediate practice; needs nothing from us.
2. **Parallel *interactive* sessions (principal in N terminals) — needs the build.** Requires: the hook-path audit (above); deciding how comms/intent stay shared across worktrees (OS junction to the main tree's file vs. hook-config absolute paths); teaching the cockpit that a session may live in a worktree (PTY cwd, state mirror-back); and a merge/branch-hygiene convention (`git worktree add ../brain-wt-<topic> -b <topic>`, merge on topic close). This is the deferred build.

## Out of scope / open questions (for the build session)

- **Comms-sharing mechanism.** Junction/symlink the worktree's `comms/active.md` + `.claude/intent/` back to the main tree, *or* reconfigure the hooks to write absolute main-tree paths. Junction is less invasive but Windows-junction-fragile; hook-config is cleaner but touches every emitter. Undecided.
- **Cockpit worktree awareness.** Does the cockpit launch PTYs into worktrees, or only ever drive the main tree while sub-agents use worktrees? Likely the latter first.
- **Merge workflow for markdown.** The brain is mostly append-only/suffixed already, so true conflicts should be rare and concentrated in the shared code/meta files — exactly where git conflict resolution is *wanted*.
- **Cross-brain.** Still no `comms` bridge between `gielinor/` and `developer-braindead/` ([[D-024_parallel_player_coordination]] out-of-scope); worktrees don't change that.

## Related

- [[D-024_parallel_player_coordination]] — parallel player coordination (comms + suffix); left the same-file race and hook enforcement out of scope. This is the follow-on.
- [[D-019_parallel_braindead_and_comms_channel]] — parallel Braindead + comms channel; the discipline layer this hardens.
- [[D-018_parallel_session_substrate_isolation]] — per-session substrate isolation (intent files, state-actors); the per-sid8 precedent.
- [[D-020_terminal_switchboard]] — status sidecar; the liveness signal that stays the shared coordination source under worktrees.
- [[D-027_inward_outward_build_imbalance]] / [[D-028_switchboard_cockpit_rebuild]] — the inward-build context; this is more inward infrastructure, justified because it removes a documented, recurring tax on every multi-session build.
- `comms/_about.md` — the channel this decision keeps shared rather than isolating.
