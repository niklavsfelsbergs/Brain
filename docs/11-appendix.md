# 11 — Appendix

Loose ends, a quick-reference, and the source cross-reference index.

## Ideas capture

A pre-everything capture path, shared across both brains and all actors. When the principal
says `note this idea: <text>` anywhere in a message (case-insensitive, colon required), the
active actor writes **one** file to [`brain/ideas/`](../ideas/) — `YYYY-MM-DD-<actor>-<slug>.md`,
body = the idea text, no elaboration, no clarifying questions — and moves on. Listing is on
cue ("what ideas have I had", "list my ideas", "ideas about X"), grouped by actor, newest
first.

It is **principal-prompted only** — dwarves/gnomes/penguins don't capture ideas, and the
agent doesn't preemptively label observations as ideas. No drafts, no proposals, no
auto-promotion (manual promotion only). Canonical spec:
[`brain/ideas/_about.md`](../ideas/_about.md).

## Body files

The "body" is the substrate-specific configuration, as opposed to the "brain" (the layered
memory). On a [reset](06-rituals.md#death--spawn-what-survives) these are the principal's
choice to keep; on a future [ascension](06-rituals.md#death--spawn-what-survives) they are
what changes while the brain travels intact.

| File | Role |
|---|---|
| [`CLAUDE.md`](../CLAUDE.md) (root) | The brain-root router — resolves main-brain vs. dev-brain. |
| [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) | The main-brain master rulebook (imports `meta/`). |
| [`developer-braindead/CLAUDE.md`](../developer-braindead/CLAUDE.md) | Dev-brain conventions. |
| `CLAUDE.local.md` | Host-local overrides. |
| `.mcp.json` | MCP tool/server config. |
| `ticks.md` | Scheduling (the agent's "heartbeat"). |
| `.claude/settings.json` | Hook wiring + permissions — see [08](08-enforcement-and-hooks.md). |

## Quick layer-routing reference

The full table is in [04 — Write discipline](04-write-discipline.md#routing) (authoritative:
[`layer-routing.md`](../gielinor/meta/layer-routing.md)). The one-line rule:

> **Quest-log is for narrative; everything else has a home.** Before writing, ask *what
> shape is this?* — knowledge → `bank/drafts/`; method → `spellbook/drafts/skills/`;
> self-observation → `examine/drafts/`; resume state → `inventory/`; decision →
> `lorebook/drafts/`. When genuinely ambiguous, ask.

## Source cross-reference index

Each doc page maps to the canonical files it summarises. **If a page and its source
disagree, the source wins.**

| Doc page | Canonical sources |
|---|---|
| [01 — Orientation](01-orientation.md) | [`CLAUDE.md`](../CLAUDE.md), [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) |
| [02 — Glossary](02-glossary.md) | the layer `_about.md` files; this doc set |
| [03 — Layers & memory](03-layers-and-memory.md) | [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) → *Layer index*; per-layer `_about.md`; [`players/_about.md`](../gielinor/players/_about.md) |
| [04 — Write discipline](04-write-discipline.md) | [`write-rules.md`](../gielinor/meta/write-rules.md), [`drafts-mechanics.md`](../gielinor/meta/drafts-mechanics.md), [`archive-discipline.md`](../gielinor/meta/archive-discipline.md), [`layer-routing.md`](../gielinor/meta/layer-routing.md) |
| [05 — Actors & modes](05-actors-and-modes.md) | [`modes.md`](../gielinor/meta/modes.md), [`guthix.md`](../gielinor/meta/guthix.md), [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md), persona files |
| [06 — Rituals](06-rituals.md) | [`spellbook/rituals/*.md`](../gielinor/spellbook/rituals/), [`death-and-spawn.md`](../gielinor/meta/death-and-spawn.md) |
| [07 — Communication](07-communication-and-coordination.md) | [`communication-protocol.md`](../gielinor/meta/communication-protocol.md), [`comms/_about.md`](../gielinor/comms/_about.md) |
| [08 — Enforcement & hooks](08-enforcement-and-hooks.md) | [`gielinor/.claude/hooks/`](../gielinor/.claude/hooks/), [`developer-braindead/.claude/hooks/`](../developer-braindead/.claude/hooks/), the `settings.json` files |
| [09 — The cockpit](09-cockpit.md) | [`cockpit/_about.md`](../cockpit/_about.md), `cockpit/backend.py`, `cockpit/ptybridge.py` |
| [10 — The dev brain](10-dev-brain.md) | [`developer-braindead/_about.md`](../developer-braindead/_about.md), [`developer-braindead/CLAUDE.md`](../developer-braindead/CLAUDE.md), [`respawn.md`](../developer-braindead/respawn.md) |

## Decision references used across these docs

These `D-NNN` / `S-NNN` markers appear throughout and resolve to the lorebook (main brain)
or `bank/decisions/` and `quest-log/` (dev brain):

- **D-016** gnomes · **D-017** explicit-permission writes · **D-018** per-session intent
  files · **D-021** penguins · **D-024** parallel-session coordination · **D-025**
  multiple-choice-with-recommendation · **D-026** switchboard promotion · **D-027**
  inward/outward build gap · **D-028** the cockpit rebuild · **D-029** two-axis state vocab.
- **S038** Guthix routing · **S058** in-voice intent · **S082** mandatory-OPEN · **S085**
  enforcement-wiring + cockpit security hardening.

---

← Back to the **[index](README.md)**.
