# 01 — Orientation

## What the brain is

A **personal AI agent** whose long-term memory is a structured tree of markdown files.
The agent is not a knowledge vault and not a chatbot with a notes folder — it is modelled
as an entity with a *body* (the host, config, scheduling), a *brain* (the layered markdown
memory), *gates* (the hooks that enforce its rules), *tools* (MCP servers, the shell), and
a *personality* expressed through the characters it operates as.

The memory is organised into **cognitive layers** borrowed from RuneScape terminology —
`bank` (semantic memory), `quest-log` (episodic memory), `spellbook` (procedural memory),
`inventory` (working memory), `examine` (self-model), and more. The theme is not
decoration: it gives every kind of content a named home and makes the metaphors
(alching, bankstanding, respawn) carry real operational meaning. See the
[Glossary](02-glossary.md) to decode the vocabulary.

The agent operates through **players** — coherent characters with their own knowledge,
domain, and voice. Players are not masks worn by the user; they are characters in their
own right who act on the user's behalf. See [Actors & modes](05-actors-and-modes.md).

Authoritative source: [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) → *What you are*.

## The two-brain split

The repository houses **two** brain systems. The distinction is fundamental and is the
first thing the [brain-root router](../CLAUDE.md) resolves on every session.

| | [`gielinor/`](../gielinor/) | [`developer-braindead/`](../developer-braindead/) |
|---|---|---|
| **Role** | The **main brain** — the cognitive system the agent *is* | The **dev brain** — the construction log for *building* the main brain |
| **Nature** | A living cognition; players, rituals, identity | A working notebook; no players, no cognition runs over it |
| **Actor** | Players / Guthix / wisp | Braindead (the construction crew) |
| **Writes to the other?** | Only on explicit principal cue (read), never writes | Reads and writes `gielinor/` freely — that's its job |

A session at the repository root **defaults to the main brain**. Dev-brain mode is entered
only when a message *starts with* `Lets develop gielinor` (strict matching, same as player
address). Returning to the main brain is done by addressing a player at the start of a
message. Full rules: [`CLAUDE.md`](../CLAUDE.md) (root router) and
[`developer-braindead/CLAUDE.md`](../developer-braindead/CLAUDE.md).

This documentation was written from the **dev brain** — it is itself a construction
artifact describing the main brain. See [10 — The dev brain](10-dev-brain.md).

## The design invariants

Five principles run through every layer and ritual. If you understand only these, you
understand the shape of the system.

1. **Agent with a body, not a vault.** The brain has lifetime; behaviour shapes it; the
   principal shapes the agent. Content has a *home* by shape, not a dumping ground.

2. **Identity is gated.** Anything that defines who the agent thinks *it* is, who it thinks
   *the user* is, or what has been *decided* about the system requires the principal's
   sign-off. The agent proposes; the principal approves. See
   [Write discipline](04-write-discipline.md).

3. **Knowledge enters as drafts, graduates on approval.** Observations flow into the brain
   freely as `drafts/`. Promotion to canonical `confirmed/` knowledge happens only through
   review (the alching and bankstanding rituals, or `/drafts`). Draft when in doubt — a
   rejection is cheap, a missed observation is invisible.

4. **Nothing is destroyed.** The agent never deletes content; it *moves* it into an
   `archive/` (superseded) or `rejected/` (never qualified). A wrong move stays recoverable
   forever, and patterns in rejections are themselves data. See
   [Archive discipline](04-write-discipline.md#archive-discipline).

5. **The quest-log is for narrative; everything else has a home.** The session story logs
   itself freely; substantive content (knowledge, methods, self-observations) must be
   *routed* to its proper layer rather than left to drift into the log. See
   [layer-routing](04-write-discipline.md#routing).

## The six architectural guarantees

Five of the invariants above are *philosophy*; these six lines are **enforced by hooks** —
the agent cannot bypass them. They are the difference between discipline (which can slip)
and a gate (which cannot).

1. **No writes to any `confirmed/` path.** Identity is gated at the filesystem level.
2. **No deletes — ever.** Forbidden commands are blocked; the agent moves to `archive/`.
3. **Dwarf write boundary.** Dwarf sub-agents have a restricted, task-local write surface.
4. **Gnome write boundary.** Gnome sub-agents are restricted to the housekeeping surface.
5. **Penguin write boundary.** Penguin sub-agents are restricted to research output.
6. **No sub-spawning from a sub-agent.** Only the principal spawns dwarves/gnomes/penguins.

These are implemented by the enforcement hooks in
[`gielinor/.claude/hooks/`](../gielinor/.claude/hooks/) and wired in `settings.json`. The
full mechanism — including the important detail that role hooks (3–5) are *inert for a
principal session* and the [S085] fix that made the guarantees real gates for brain-root
sessions rather than mere prompt discipline — is in
[08 — Enforcement & hooks](08-enforcement-and-hooks.md).

Authoritative source for the guarantees: [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) →
*The six architectural guarantees*.

---

Next: **[02 — Glossary](02-glossary.md)** — decode the vocabulary before going deeper.
