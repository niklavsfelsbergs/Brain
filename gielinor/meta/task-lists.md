# Task-list discipline

Work with more than one step gets **decomposed into a tracked list and worked one item at a time**, instead of charged head-first. The list makes the plan correctable before commitment, guards against dropped or out-of-order steps, and — when mirrored to disk — *is* the crash-recovery signal `death-and-spawn.md` asks for.

This is the sequential sibling of the dwarf-spawn heuristic (`spellbook/skills/spawning-dwarves.md`): dwarf-spawn decomposes work that runs **in parallel** (fan-out); task-list discipline decomposes work that must run **in order**. Same threshold family, different axis. A single list *step* can itself be "spawn three dwarves."

## When to make a list — the threshold

Make a tracked list when the task is **multi-step AND at least one of**:

- spans more than one file or surface,
- spans more than one turn (you won't finish it in this reply),
- contains an **irreversible or outward-facing** action (a commit, a send, a gated write, anything past the gates),
- has **order-dependent** steps where doing them out of sequence is wrong or wasteful.

**Skip it** — the one-line Plan still wins — for single-action asks, trivial lookups, pure reflection or open-ended discussion, and anything the compression rule in `communication-protocol.md` already collapses.

**The tiebreaker when unsure:** *would a dropped step or a wrong-order step be expensive here?* If yes, list it. If a dropped step costs nothing, don't. This threshold is the whole guard against list-*theater* — the brain's culture is terse and anti-recitation (`CLAUDE.md` → *Communication discipline*); a ceremonial six-item list bolted onto a two-step task is misalignment, not diligence. Calibrate like the alching and dwarf-spawn thresholds: bias toward a list only as the work earns it.

## Two homes — the rule of thumb

Everything list-worthy gets the **harness task list** (`TaskCreate`/`TaskUpdate`) — the live, in-session working surface, marked `in_progress`/`completed` as you go. Add a **durable `inventory/` mirror** (a checklist block in the resume file) only when the work **spans turns/sessions** *or* **touches an irreversible/outward action** — that mirror is the crash-recovery signal. A short multi-step task you finish in one reply gets the harness list and no file.

The full mechanics — the two-homes table, the lifecycle (build-after-Plan → update-per-step → don't-recite → close/respawn hand-off), the anti-patterns, and the sub-agent scope — live in `meta/task-lists-mechanics.md`, loaded **just-in-time**. Read it when maintaining a cross-session or gated list.

## Related

- `communication-protocol.md` — how the list surfaces at the Plan line (*Task-list surfacing*).
- `task-lists-mechanics.md` — the full mechanics (JIT).
- `spellbook/skills/spawning-dwarves.md` — the parallel-decomposition sibling and the threshold this one mirrors.
