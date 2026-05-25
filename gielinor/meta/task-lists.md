# Task-list discipline

How the agent handles work that has more than one step: **decompose it into a tracked list and work the list**, instead of charging the whole thing head-first. The list makes the plan correctable before commitment, guards against dropped or out-of-order steps, and — when mirrored to disk — *is* the crash-recovery signal `death-and-spawn.md` asks for.

This is the sequential sibling of the dwarf-spawn heuristic (`spellbook/skills/spawning-dwarves.md`): dwarf-spawn decomposes work that can run **in parallel** (fan-out); task-list discipline decomposes work that must run **in order** (one actor, ordered steps). Same threshold family, different axis. A single list *step* can itself be "spawn three dwarves."

## When to make a list — the threshold

Make a tracked list when the task is **multi-step AND at least one of**:

- spans more than one file or surface,
- spans more than one turn (you won't finish it in this reply),
- contains an **irreversible or outward-facing** action (a commit, a send, a write the principal must approve, anything past the gates),
- has **order-dependent** steps where doing them out of sequence is wrong or wasteful.

**Skip it** — the one-line Plan still wins — for single-action asks, trivial lookups, pure reflection or open-ended discussion, and anything the compression rule in `communication-protocol.md` already collapses.

**The tiebreaker when unsure:** *would a dropped step or a wrong-order step be expensive here?* If yes, list it. If a dropped step costs nothing, don't.

This threshold is the whole guard against list-*theater*. The brain's culture is terse and anti-recitation (`CLAUDE.md` → *Communication discipline*); a ceremonial six-item list bolted onto a two-step task is misalignment, not diligence. Calibrate like the alching and dwarf-spawn thresholds — bias toward a list only as the work earns it.

## Two homes — complementary, not competing

| Home | What it is | Use it for |
|---|---|---|
| **Harness task list** (`TaskCreate`/`TaskUpdate`) | Live, in-session, visible to the principal, low-friction, **ephemeral** | Every list-worthy task. The working surface — mark items `in_progress`/`completed` as you go. |
| **`inventory/` checklist** (durable mirror) | A checklist block in the resume file (`inventory/<quest-slug>-resume__<sid8>.md`), **survives a crash** | Work that **spans turns/sessions** *or* **touches irreversible/outward actions**. This is the recovery signal. |

**Rule of thumb:** everything list-worthy gets the **harness list**; add the **durable mirror** only when the work outlives the turn or carries risk. A short multi-step task you finish in one reply gets the harness list and no file. A task that will run across sessions, or that commits/sends/promotes, gets both.

The durable mirror is not new structure — `inventory/_about.md` already names "open task list" as resume-state content, and `layer-routing.md` already routes it there. This rule just says *when* the agent is obliged to populate it. The pending-before-execution discipline in `death-and-spawn.md` is the same idea at action grain; the checklist is it at task grain. An item left `in_progress` in inventory after a crash is exactly what the next session's reconciliation prompt keys on.

## Lifecycle

1. **Build the list after Understanding/Plan, before executing.** Surfaced in or just after the Plan line so the principal can correct the *decomposition* before the agent commits to it — the Plan-preamble rationale ("a wrong restatement is cheap; a wrong implementation is not") at finer grain. See `communication-protocol.md` → *Task-list surfacing*.
2. **Update status at each step**, not in a batch at the end. The harness list reflects current state; the intent line narrates the active step in-voice.
3. **Don't recite the full list back in prose every turn.** The harness list and the intent line carry it. Re-narrate only what changed.
4. **At session close**, the durable mirror's remaining items are the resume foreground — close-session already writes inventory. **At respawn**, an in-progress checklist is read back as resume state.

## Anti-patterns

- **List-theater.** Padding a trivial or genuinely single-shot task into a ceremonial list. The threshold exists to prevent this; when in doubt, the cost test decides.
- **List as narrative.** The list is *state* — what's done, what's next. The session *story* (turns, decisions, hand-offs) stays in the quest-log. Don't let the checklist duplicate the quest-log, or vice versa.
- **Silent re-planning.** If the decomposition changes mid-task (a step splits, a new dependency appears), update the visible list — don't quietly diverge from the plan the principal saw.

## Scope

Applies to **every actor** in a principal session — players, Guthix (consultation and bankstanding), Braindead (dev-brain), wisp. Voice adapts; the discipline does not.

Sub-agents (dwarves, gnomes, penguins) operate from a fixed brief, not a principal dialogue. They may use the **harness list** internally to track a multi-step brief, but their durable trace is the quest-log entry per their write boundaries (`modes.md`) — they are not obliged to maintain an inventory mirror.

## Related

- `communication-protocol.md` — how the list surfaces relative to the Understanding/Plan preamble.
- `layer-routing.md` — the `inventory/` resume file is the durable home.
- `death-and-spawn.md` — the crash-recovery discipline the durable mirror serves.
- `spellbook/skills/spawning-dwarves.md` — the parallel-decomposition sibling and the threshold this one mirrors.
- `modes.md` — per-mode behavior and the sub-agent write boundaries.
