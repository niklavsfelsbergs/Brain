# Dwarf-spawn heuristic — when to go parallel

**Observed:** 2026-05-21 (S003), anchored on the S002 scoping moment 2026-05-20 plus this session's execution.

**Observation.** In S002 (2026-05-20), I scoped the Shipping Data Mart V1 gap audit and proposed a serial attack order (ClickUp → repo → redshift → synthesize, all in main context). Niklavs surfaced the heuristic himself with the meta-question: *"How will you do this? It's a lot of work. You will have to spawn dwarves. Would you have known that?"* I admitted no — I would have gone serial.

In S003 (2026-05-21), I spawned 3 Jebrim-inherited dwarves per the pre-agreed plan. They ran independently; each returned a tight bounded deliverable; main-context absorbed three summaries instead of three full investigations. Wall-time clearly compressed; the synthesis context wasn't crushed by tool outputs.

**The trigger I miss by default.** Three simultaneous conditions:

1. **Scope size** — the work has multiple distinct surfaces (here: ticket tree + repo + live data).
2. **Independent paths** — each surface can be read without the others' output as input.
3. **Wall-time pressure or context-window pressure** — serial would either miss the deadline or push the main context past the point of reliable synthesis.

When all three hold, the work is dwarf-shaped. Default to proposing parallel spawns in the plan, not as an afterthought.

**Counter-trigger — when NOT to spawn.** If the surfaces depend on each other's output to scope the next read, parallelism is fake — each dwarf either blocks waiting or guesses wrong. Serial is correct then. Example: "find the canonical ORWO HTML" required first checking the ticket comments, then deciding where in the repo to look. That's serial discovery, not parallel investigation.

**How to apply.** When the principal hands me a task, the **Plan** line of the Understanding/Plan preamble should explicitly name the dwarves if the heuristic fires — per the dwarf-spawn annotation rule now in `meta/communication-protocol.md`. That surfaces the decision before it commits, and gives the principal a cheap correction window if the heuristic fires wrong.

**Self-correction record.** The S002 scoping turn-log marked this as worth drafting after the dwarves actually ran — so the observation could cite both moments. It now does. Both moments confirm the same shape: the heuristic catches a real recurring failure mode (going serial under wall-time pressure), and parallelism produced tighter outputs than serial would have.

**Related.** Couples to whatever `spellbook/skills/spawning-dwarves.md` becomes (the communication-protocol now references it). If it doesn't exist yet, that's a separate skill-file to draft.
