# The Brain — technical documentation

> A navigable map of how this system is built: the cognitive layers, the actors that
> operate them, the modes and roles that scope behaviour, the rituals that drive a
> session, the hooks that enforce the rules, and the cockpit you drive it all from.

This folder is the **front door**. The system already self-documents densely — every
layer carries an `_about.md`, the rulebook lives in [`gielinor/meta/`](../gielinor/meta/),
and each ritual has its own file under [`gielinor/spellbook/rituals/`](../gielinor/spellbook/rituals/).
What was missing was a single coherent structure tying those scattered authoritative
files together. That is what `docs/` is.

## Reading principle — this is a map, not a copy

These pages **describe and link**; they are not a second copy of the rulebook. Where a
detail is authoritative somewhere else, the page links there and summarises rather than
restating it verbatim. This keeps the docs from drifting when a ritual or rule changes:
the source file is the truth; this is the index over it.

**If a page and its linked source disagree, the source wins** — and that is a bug in this
doc worth fixing.

## Where to start

New to the system? Read in this order:

1. **[01 — Orientation](01-orientation.md)** — what the brain is, the two-brain split, the design invariants, and the six architectural guarantees.
2. **[02 — Glossary](02-glossary.md)** — the RuneScape→technical decoder. Almost nothing below parses without it; skim it first.
3. **[03 — Layers & memory](03-layers-and-memory.md)** — the data model: the cognitive layers and the memory types they map to.
4. **[04 — Write discipline](04-write-discipline.md)** — how knowledge enters (drafts), gets approved (confirmed), and is never destroyed (archive).
5. **[05 — Actors & modes](05-actors-and-modes.md)** — who operates the brain (players, Guthix, the wisp), and the modes and roles that scope each session.
6. **[06 — Rituals](06-rituals.md)** — the procedures that drive a session: respawn, close, alching, bankstanding, drafts-triage; and what survives a crash or reset.
7. **[07 — Communication & coordination](07-communication-and-coordination.md)** — the response protocol, the visualizer sidecars, and how parallel sessions stay out of each other's way.
8. **[08 — Enforcement & hooks](08-enforcement-and-hooks.md)** — the hook layer: what's a hard gate vs. what's discipline, and the state files the observability hooks emit.
9. **[09 — The cockpit](09-cockpit.md)** — how you actually drive the brain: parallel interactive sessions over a real PTY.
10. **[10 — The dev brain](10-dev-brain.md)** — `developer-braindead/`, the construction log this documentation was written from.
11. **[Appendix](11-appendix.md)** — ideas capture, body files, a quick layer-routing reference, and the source cross-reference index.

## The one-paragraph version

The brain is a personal AI agent whose memory is a structured tree of markdown files,
organised into RuneScape-themed **cognitive layers**. It operates through **players** —
coherent characters (Jebrim, Zezima) with their own knowledge and voice — plus **Guthix**,
a caretaker deity for system-scope work, and a **wisp** for the unscoped state. Knowledge
enters freely as **drafts** and is promoted to **confirmed** identity only with the
principal's sign-off; nothing is ever deleted, only archived. **Hooks** enforce the
non-negotiable lines (no writes to `confirmed/`, no deletes, sub-agent write boundaries).
A second tree, [`developer-braindead/`](../developer-braindead/), is the **construction
log** for building the first — a working notebook, not a cognition. You drive the whole
fleet from the **cockpit**, a desktop console that runs interactive Claude Code sessions
over a real terminal.

Canonical entry points in the codebase: [`CLAUDE.md`](../CLAUDE.md) (the brain-root router),
[`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) (the main-brain master rulebook), and
[`developer-braindead/CLAUDE.md`](../developer-braindead/CLAUDE.md) (the dev-brain conventions).
