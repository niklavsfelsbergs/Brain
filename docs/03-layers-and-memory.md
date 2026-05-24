# 03 — Layers & memory

The brain's memory is differentiated by **what it stores**, not when it's written. Each
layer maps to a kind of memory and carries an `_about.md` stating its job and conventions —
**read the `_about.md` on first access to any layer.** This page is the map of the layers;
the write rules that govern them are in [04 — Write discipline](04-write-discipline.md).

## Global vs. per-player

Layers exist at two scopes:

- **Global layers** apply to the agent as a whole, regardless of which player is active.
- **Per-player layers** belong to one character. Each player (`gielinor/players/<name>/`)
  carries a full set; players don't read each other's per-player layers during normal work.

A third scope, **deity layers** (`gielinor/deities/guthix/`), belongs to Guthix — bank,
quest-log, inventory, keepsake, and proposals at system scope.

## Global layers

Source: [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) → *Layer index*.

| Layer | Path | Holds |
|---|---|---|
| **examine** | [`gielinor/examine/`](../gielinor/examine/) | The agent's self-model at the system level. |
| **niksis8** | [`gielinor/niksis8/`](../gielinor/niksis8/) | What the agent knows about Niklavs universally. |
| **keepsake** | [`gielinor/keepsake/`](../gielinor/keepsake/) | Always-surface pins (cross-player). |
| **lorebook** | [`gielinor/lorebook/`](../gielinor/lorebook/) | The self-improvement log — decisions about how the agent operates (`D-NNN`). |
| **spellbook** | [`gielinor/spellbook/`](../gielinor/spellbook/) | Rituals (fixed procedures) and cross-player skills. |
| **meta** | [`gielinor/meta/`](../gielinor/meta/) | The current rulebook. User-controlled. |
| **players** | [`gielinor/players/`](../gielinor/players/) | The characters the agent embodies, plus an `inbox/` for unscoped captures. |
| **deities** | [`gielinor/deities/`](../gielinor/deities/) | System-scope actors (Guthix). |

> **Construction history note.** The lorebook is the agent's log of changes to *itself*.
> The history of *building* the brain lives in the dev brain, not here — see
> [10 — The dev brain](10-dev-brain.md).

## Per-player layers

Source: [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) → *Layer index* (per-player), and
[`gielinor/players/_about.md`](../gielinor/players/_about.md).

| Layer | Memory type | Holds |
|---|---|---|
| **bank** | Semantic | What the character knows. Notes are gated behind drafts → alching. |
| **research** | Source material | Full research writeups (penguin- or principal-authored). Bank notes are *picked* from here. |
| **quest-log** | Episodic | Per-session narrative — `in-progress/`, `completed/`, `archive/`. |
| **spellbook** | Procedural | How *this* character does things — skills (gated behind drafts). |
| **inventory** | Working | What's carried now. Volatile; lost on reset. |
| **examine** | Self-model | This character's self-knowledge. |
| **niksis8_character** | User-model | What this player knows about Niklavs through their relationship. |
| **keepsake** | Pinned priority | This character's always-surface pins. |

The current roster is in [`gielinor/players/`](../gielinor/players/) — **Jebrim** (work /
analytics) and **Zezima** (personal / reflection). Their domains and voices are described
in [05 — Actors & modes](05-actors-and-modes.md).

## The memory-type framing

The layer names map onto a cognitive-memory model:

```
                 ┌─ semantic   → bank        ("what I know")
   long-term ────┼─ episodic   → quest-log   ("what happened")
                 └─ procedural → spellbook   ("how I do things")

   working      → inventory                  ("what I'm holding now", volatile)

                 ┌─ self       → examine      ("who I think I am")
   identity  ────┼─ user       → niksis8(_character) ("who I think you are")
                 └─ decisions  → lorebook     ("what I've decided about myself")

   priority     → keepsake                    ("what must always surface")
```

The split that matters most operationally: **identity layers are gated** (examine,
niksis8, niksis8_character, lorebook, keepsake) while **working and episodic layers are
free** (inventory, quest-log). Knowledge (bank, skills) sits in between — written freely as
drafts, promoted under review. The next page makes this precise.

## Internal structure of a gated layer

A gated identity layer keeps four sub-folders with distinct meanings:

```
examine/
  drafts/      # proposals awaiting review
  confirmed/   # approved, currently in force   ← hook-protected, never written by the agent
  archive/     # mirrors confirmed/ — "this used to be true; it isn't anymore"
  rejected/    # mirrors drafts/   — "this was proposed; it never qualified"
```

`confirmed/` may also carry a `current.md` executive summary alongside the atomic entries.
The respawn ritual reads everything in `confirmed/`; it does **not** read `drafts/`. See
[04 — Write discipline](04-write-discipline.md) for the full flow and
[archive-discipline](04-write-discipline.md#archive-discipline) for the archive/rejected
distinction.

---

Next: **[04 — Write discipline](04-write-discipline.md)** — how content enters, graduates,
and is retired.
