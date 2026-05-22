# Layer routing — what content lands where

> **Purpose.** A short, scannable mapping from *the shape of content the agent is about to write* to *the layer it belongs in*. When in doubt mid-session, consult this table before defaulting to "I'll just put it in the quest log."

The brain's layers are differentiated by *what they store*, not *when they're written*. The quest log is the path of least resistance — auto-write, no draft gate, no promotion ceremony — so content drifts there by default unless the agent actively routes it elsewhere. This file is the routing reference.

## The routing table

| If the content is shaped like… | …it lands in |
|---|---|
| **Resume state** — "where we are," "next concrete step," open tasks/decisions to carry across turns or sessions | `inventory/<active-quest>.md` (per-player) |
| **Narrative of what happened** — the session story, what was asked, what was done, decisions made in-flight, turn-by-turn append | `quest-log/in-progress/` (per-player) |
| **Knowledge about a thing** — a mart, a query, a project, a stakeholder, a data source, an external system | `bank/drafts/notes/` (per-player) → alching promotes to `bank/notes/` |
| **Full research writeup** — sources, quotes, findings with inline citations, gaps. Penguin-authored or principal-authored when running the research skill | `research/<YYYY-MM-DD>-<topic-slug>.md` (per-player). No draft gate inside. Distillations get *picked* into `bank/drafts/notes/` during alching; the research file stays as the anchor |
| **Procedure for how to do a class of work** — a recurring method, a decomposition pattern, a recon-spawn pattern, a reusable workflow | `spellbook/drafts/skills/` (per-player) → alching promotes to `spellbook/skills/` |
| **Self-observation about the player** — bias, pattern, correction, how-they-work tendency | `examine/drafts/` (per-player) → principal approves to `confirmed/` |
| **Observation about Niklavs through the player's relationship-lens** | `niksis8_character/drafts/` (per-player) → principal approves to `confirmed/` |
| **Currently load-bearing project, deadline, stakeholder commitment** | `keepsake/proposals/` (per-player) → principal pins to `current.md` |
| **System-level self-observation** (about the agent as a whole, not any one player) | `examine/drafts/` (global) → principal approves to `confirmed/` |
| **Universal Niklavs observation** (true regardless of which player saw it) | `niksis8/drafts/` (global) → principal approves to `confirmed/` |
| **Cross-player always-surface pin** | `keepsake/proposals/` (global) → principal pins |
| **Decision about how the agent operates going forward** | `lorebook/drafts/` → principal approves to `lorebook/confirmed/D-NNN_*.md` |
| **Construction history of the brain itself** (only writeable in dev-brain mode) | `developer-braindead/bank/decisions/D-NNN_*.md` |
| **Conversational question or reflection in Guthix's voice** — overall question, cross-player lookup, system-shaped musing. Default to chat-only; capture only if it produces something worth surfacing next respawn | optional: `deities/guthix/quest-log/in-progress/G-NNN_YYYY-MM-DD_<slug>.md`. Genuine cross-cutting observation that emerges → `deities/guthix/bank/drafts/notes/` |
| **Cross-cutting knowledge about the brain itself** — patterns, drift observations, recurrent themes Guthix notices during bankstanding | `deities/guthix/bank/drafts/notes/` → next bankstanding promotes to `deities/guthix/bank/notes/` |
| **Bankstanding ritual trace** — what one pass covered, proposed, flagged | `deities/guthix/quest-log/in-progress/B-NNN_*.md` → moves to `completed/` on clean ritual close |
| **In-progress bankstanding state** — phase tracker, mid-pass carry-forward | `deities/guthix/inventory/B-NNN-resume.md` |
| **System-level pin for Guthix specifically** (always surface to him on respawn) | `deities/guthix/keepsake/proposals/` (Guthix-scope) → principal pins to `deities/guthix/keepsake/current.md` |
| **Godly proposal** — proposed change to anything in the system (meta rules, rituals, hooks, architecture, Guthix himself), drafted only during bankstanding | `deities/guthix/proposals/` → principal lands, edits, or rejects. Rejections preserved in `deities/guthix/proposals/rejected/`. See `deities/guthix/proposals/_about.md`. |

## The principle

**Quest log is for narrative; everything else has a home.** When the agent is mid-session and notices it's about to write content, the first question is: *what shape is this?* If the answer fits any row above other than "narrative," route there. The quest log captures the *story* of the session — turns, decisions, hand-offs — and intentionally does not carry the *content* that would otherwise persist into one of the other layers.

This is why the quest log appears in two columns of `write-rules.md` (auto-write) while most other layers require drafts: the layers requiring discipline are the *substantive* ones. The quest log is the by-product.

## Operational consequences

- **Resume state.** The `Where we are` / `Next concrete step` blocks that have historically lived at the top of quest-log files should live in `inventory/` instead. Close-session writes them to inventory; respawn reads them back. Quest log keeps the turn log and decisions.
- **Methodology vs domain knowledge.** A note titled "how to decompose moving-target work" is a *skill* (spellbook), not a bank/note. A note titled "the EU Tender 2026 architecture" is a *bank note*, not a skill. Domain knowledge is *about* the work; skills are *how to do* the work.
- **Research vs bank.** A 2,000-word writeup of *"what's the state of the EU Carbon Border Adjustment Mechanism as of 2026-05"* with twelve sources is a **research** file. The four sentences that come out of it — *"CBAM applies to <list>, effective <date>, fees calculated as <formula>; risk for our clients: <line>"* — is a **bank note**. The research stays as the anchor; the bank note carries the picking. The picking flow runs during alching: walk recent `research/` files, propose `bank/drafts/notes/` entries that capture the load-bearing claims (with cross-link back to the source research file), principal approves.
- **Self-observations.** If the agent notices a correction-worthy pattern in how the player works mid-session, that observation is a draft in `examine/drafts/` — even if it also gets a sentence in the quest-log turn for context. The quest-log mention is incidental; the draft is the durable record.
- **The active-quest convention for inventory.** When there's exactly one in-progress quest, inventory has one file per resume topic. When there are multiple in-flight quests, name files clearly — e.g., `inventory/S014-ttyd-resume.md`, `inventory/eu-tender-resume.md`.

## When the routing is genuinely ambiguous

Ask. A wrong restatement is cheap; a wrong-layer write requires a cleanup move later (and per `archive-discipline.md`, never a delete). The user is the tiebreaker.

## Related

- `write-rules.md` — what discipline applies once the layer is chosen.
- `archive-discipline.md` — what happens when content needs to leave a layer.
- `drafts-mechanics.md` — the draft → confirmed promotion flow.
- `modes.md` — which layers each ritual is allowed to write to.
- `communication-protocol.md` — the Understanding/Plan preamble and intent narration.
