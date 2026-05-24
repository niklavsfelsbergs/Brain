# 02 — Glossary

The system speaks RuneScape. The theme is load-bearing — each term names a real layer,
ritual, or actor. This page is the decoder; skim it before reading anything else.

## The world

| Term | What it actually is |
|---|---|
| **Gielinor** | The main brain — the cognitive system the agent *is*. The world the agent inhabits. ([`gielinor/`](../gielinor/)) |
| **The dev brain / Braindead** | `developer-braindead/`, the construction log for building the main brain, and the actor who works it. |
| **Respawn** | Session start. The load ritual that reads durable identity and surfaces in-flight work. |
| **Death** | Session end — either a crash (interrupted) or a deliberate reset. Governs what survives. |
| **Ascension** | Future: migrating the brain to a new host/substrate. Not yet built. |

## The cognitive layers (memory)

| Term | Memory type | Holds |
|---|---|---|
| **Bank** | Semantic | What a character *knows* — facts about projects, systems, stakeholders, data sources. |
| **Quest-log** | Episodic | What *happened* — the per-session narrative, turn by turn. |
| **Spellbook** | Procedural | *How* to do a class of work — rituals (fixed) and skills (per-character methods). |
| **Inventory** | Working | What's *carried now* — volatile session state; lost on reset. |
| **Examine** | Self-model | What a character/the agent knows about *itself*. |
| **Keepsake** | Pinned priority | Always-surface pins — load-bearing deadlines, commitments, focus. |
| **Lorebook** | Self-improvement log | Decisions the agent made about *how it operates* (`D-NNN`). |
| **Research** | Source material | Full external-research writeups; bank notes are *picked* from here. |
| **niksis8 / niksis8_character** | User-model | What the agent knows about Niklavs — universally, or through a player's relationship-lens. |
| **Meta** | Rulebook | The in-force operating rules. User-controlled. ([`gielinor/meta/`](../gielinor/meta/)) |

Detail: [03 — Layers & memory](03-layers-and-memory.md).

## The rituals (procedures)

| Term | What it does |
|---|---|
| **Alching** | Per-player *tending* — review drafts, promote knowledge, archive stale notes, for **one** player's own layers. (From "high alchemy" — turning items into value.) |
| **Bankstanding** | System-level cross-cutting tending — triage the inbox, graduate cross-player patterns to globals, log behavioural changes. Voiced as Guthix. |
| **Drafts-triage** | A lightweight cut of alching's promotion gate. The `/drafts` command. |
| **Close-session** | The wrap-up ritual — reconcile, persist resume state, harvest observations, commit. |
| **Mini-respawn** | The partial reload that runs when the active actor switches mid-session. |

Detail: [06 — Rituals](06-rituals.md).

## The actors

| Term | What it is |
|---|---|
| **Player** | A coherent character the agent operates as (Jebrim, Zezima). Own knowledge, domain, voice. |
| **Guthix** | The brain's caretaker *deity* — the system-scope actor for consultation and bankstanding. Not a player. |
| **The wisp** | The unscoped state — the actor of a session that has had no prompt yet. Narrow by design. |
| **Principal** | The interactive role with full capability — introspects, proposes identity changes, spawns sub-agents. |
| **Dwarf** | A sub-agent for repo-bound functional work. Restricted write surface. |
| **Gnome** | A sub-agent for structural housekeeping (running rituals). System-namespace. |
| **Penguin** | A sub-agent for external research. (RuneScape lore: penguins are intelligence operatives.) |

Detail: [05 — Actors & modes](05-actors-and-modes.md).

## The machinery

| Term | What it is |
|---|---|
| **Cockpit** | The desktop console you drive the fleet from — interactive Claude Code over a real PTY. ([`cockpit/`](../cockpit/)) |
| **Switchboard** | The earlier name and still the directory ([`switchboard/`](../switchboard/)) where hooks write fleet state. The cockpit reads it. |
| **Hooks** | Python scripts fired by Claude Code on tool events — either *enforcement* gates or *observability* emitters. |
| **Intent file** | A per-session sidecar (`.claude/intent/<actor>-<sid8>.txt`) holding the actor's in-voice "what I'm doing" line for the visualizer. |
| **Comms / `active.md`** | The append-only log where parallel sessions announce work and avoid collisions. |
| **sid8** | The first 8 characters of `CLAUDE_CODE_SESSION_ID` — the per-session anchor used everywhere for attribution. |

## ID and filename conventions

| Pattern | Meaning |
|---|---|
| `SNNN` | A session number (e.g. `S084`). Quest-log files: `SNNN_<sid8>_<slug>.md`. |
| `D-NNN` | A decision — `lorebook/` in the main brain, `bank/decisions/` in the dev brain. |
| `A-NNN / Q-NNN / R-NNN / I-NNN` | Dev-brain entry IDs: assumption / open-question / research / idea. |
| `B-NNN / G-NNN` | Guthix-scope: bankstanding trace / consultation note. |
| `__<sid8>` suffix | Disambiguates parallel-session files (resume files, quest-logs) — see [D-024]. |

Full naming reference: [04 — Write discipline](04-write-discipline.md#naming).

---

Next: **[03 — Layers & memory](03-layers-and-memory.md)** — the data model in detail.
