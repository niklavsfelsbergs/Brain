# 10 — The dev brain (`developer-braindead/`)

The second of the [two brains](01-orientation.md#the-two-brain-split). Where the main brain
(`gielinor/`) is the cognition, the dev brain is the **construction log** for building it —
design conversations, decisions, experiments, false starts, build context. A working
notebook, **not** a cognitive system: no agent runs cycles over it, there are no players,
no alching, no bankstanding.

Authoritative sources: [`developer-braindead/CLAUDE.md`](../developer-braindead/CLAUDE.md),
[`developer-braindead/_about.md`](../developer-braindead/_about.md),
[`developer-braindead/respawn.md`](../developer-braindead/respawn.md).

## The actor: Braindead

In the dev brain the agent operates as **Braindead** — the construction crew that builds
and maintains `gielinor/`. Light persona (gruff, plainspoken build-state; voice card in the
dev `CLAUDE.md`); mostly the work is structural. The deliverable is well-considered changes
to the main brain's structure plus supporting design notes.

- **Reads** dev-brain content freely.
- **Writes** dev-brain layers per their `_about.md`, and **writes `gielinor/` freely** —
  that is the whole job. (The asymmetry: `gielinor/` does not write back to the dev brain
  and reads it only on explicit principal cue. See the [root router](../CLAUDE.md).)

## Entering and leaving dev-brain mode

- **Enter:** a message that *starts with* `Lets develop gielinor` (strict matching, same as
  player address). On entry, run the dev-brain entry sequence — read `respawn.md` first,
  then operate under dev conventions. This is a mini-respawn, symmetric to mid-session
  player switching.
- **The entry sequence is not lighter-weight when reached mid-conversation.** It includes
  **sibling-detection and posting an `OPEN`** to
  [`comms/active.md`](../developer-braindead/comms/active.md). Skipping the `OPEN` is the
  system's most common discipline leak; the [S082] fix made it mandatory on every entry.
- **Leave:** address a player at the start of a message (`Hey Jebrim, …`) to re-enter
  `gielinor/`. Without an address, dev-brain mode is **sticky**.
- **Visualizer marker:** on entry, write `dev-brain` to `.claude/active-mode.txt` so the
  hooks spawn Braindead; on close, write `unscoped`.

## The layer set — a stripped-down mirror

The dev brain borrows the RuneScape layer names for coherence but cuts what a notebook
doesn't need ([D-006]):

| Layer | Holds |
|---|---|
| `bank/` | Semantic: decisions (`D-NNN`), assumptions, open questions, risks, research, the plan, drafts |
| `quest-log/` | Episodic: per-session entries `SNNN_<slug>.md`, titled at session close |
| `spellbook/` | Procedural: dev rituals — `respawn-ritual.md`, `session-close.md` |
| `examine/` | Self-model: the dev-agent's evolving postures |
| `player/` | User-model: Niklavs's preferences and working agreements |

**Cut** vs. the main brain: `inventory/` (no working memory), `keepsake/` (no runtime
priority), and `lorebook/` — because *the whole dev brain is the main brain's lorebook*.

Conventions worth noting: stable entry IDs (`D-NNN`, `A-NNN`, `Q-NNN`, `R-NNN`, `I-NNN`)
that are never reused; wiki-links `[[ID]]` that are load-bearing across docs; a single-file
living plan at [`bank/plan.md`](../developer-braindead/bank/plan.md); and the same
never-destroy discipline (superseded entries move to `archive/`).

## How the dev brain relates to this documentation

This `docs/` tree was written *from* the dev brain — it is a Braindead construction
artifact describing the main brain. The dev brain's own `respawn.md`, `quest-log/`, and
`bank/decisions/` remain the canonical narrative of *how the system came to be the way it
is*; `docs/` is the synthesised reference for *what it is now*.

## The strategic state (as of writing)

A standing self-assessment in the dev brain ([D-027], the S060 self-audit) is worth
surfacing because it frames where the project is: the brain has been built **inward** —
observability, the cockpit, the visualizer — and has not yet built outward **hands**. The
agent is still manual-invocation-only; the first outward action (a scheduled
shipping-mart freshness pilot, `bank/plan.md` §C) is the identified highest-value next step.
Check [`developer-braindead/respawn.md`](../developer-braindead/respawn.md) for the live
"where we are / next concrete step."

---

Next: **[Appendix](11-appendix.md)**.
