# 04 — Write discipline

How content enters the brain, how it graduates to canonical knowledge, how it is retired,
and where each shape of content belongs. This is the operational heart of the system.

Authoritative sources: [`gielinor/meta/write-rules.md`](../gielinor/meta/write-rules.md),
[`gielinor/meta/drafts-mechanics.md`](../gielinor/meta/drafts-mechanics.md),
[`gielinor/meta/archive-discipline.md`](../gielinor/meta/archive-discipline.md),
[`gielinor/meta/layer-routing.md`](../gielinor/meta/layer-routing.md).

## The principle

> Anything that defines who the agent thinks I am, who the agent (or a player) thinks it
> is, or what has been decided about the system requires my sign-off. Knowledge accumulates
> via drafts that I review.

Observations enter freely as **drafts**. Promotion to canonical knowledge — identity,
character, decisions, and per-player bank — is **gated** behind principal approval.

## The per-layer write table

Each layer falls into one of three disciplines. Full table in
[`write-rules.md`](../gielinor/meta/write-rules.md); summarised:

| Discipline | Meaning | Layers |
|---|---|---|
| **Auto-write** | The agent writes directly, no gate | `quest-log/`, `inventory/`, `research/` |
| **Draft-then-approve** | Agent writes a draft; principal promotes it | `bank/notes`, `spellbook/skills`, `examine/`, `niksis8(_character)/`, `lorebook/`, `keepsake/` (via proposals) |
| **User-only** | The principal edits directly | `meta/*.md`, `spellbook/rituals/*.md`, `keepsake/current.md`, confirmed entries |

### Enforced vs. guided

A critical distinction (see [08 — Enforcement & hooks](08-enforcement-and-hooks.md)):

- **Hooks enforce** the hardest lines: no writes to any `confirmed/` path, no deletes, the
  sub-agent write boundaries, no sub-spawning.
- **CLAUDE.md guides** the rest: the draft-then-approve flow, the `bank/` and `skills/`
  draft gates, treating `meta/` as user-controlled. Hooks can't tell a proposed promotion
  from a routine edit, so the agent must hold these itself.

### "User-only" with explicit permission

The user-only column is a **default, not a prohibition.** When the principal explicitly
authorises a write to `keepsake/current.md`, `meta/*.md`, or a ritual file ("yes, write
it" / "go ahead, apply the fix"), the agent makes the write directly. Ambient agreement
("sounds good") does **not** count — the check is explicit. The hook-enforced lines remain
non-overridable regardless. Founding decision: [D-017].

## The drafts → confirmed lifecycle

Source: [`drafts-mechanics.md`](../gielinor/meta/drafts-mechanics.md).

```
  observe ──▶ drafts/ ──▶ review ──┬──▶ confirmed/   (approved)
                                    ├──▶ confirmed/   (edited, then approved)
                                    └──▶ rejected/    (turned down, with a note)
```

1. **Capture.** The agent writes an observation into `drafts/` whenever it notices
   something worth recording. Bias: **draft when in doubt.**
2. **Review.** The principal surfaces pending drafts via `/drafts`, alching, or
   bankstanding. (Drafts are **not** pushed at session start.)
3. **Decision.** Per draft: approve → `confirmed/`; reject → `rejected/` (kept, not
   deleted — patterns in rejections matter); or edit-and-approve.

**The observation rule.** Drafts must be observation-backed, not aspirational. Not *"I
should be more careful about deletes"* but *"2026-05-12: I proposed deleting the wrong
file because I matched on filename without checking path; confirm full path first."*
Specificity is what makes self-knowledge actionable.

Equivalent flows for the non-`drafts/` layers: `keepsake/proposals/` → pinned into
`current.md`; `lorebook/drafts/` → `lorebook/confirmed/D-NNN_*.md`.

<a id="archive-discipline"></a>
## Archive discipline — nothing is destroyed

Source: [`archive-discipline.md`](../gielinor/meta/archive-discipline.md). Enforced by the
[`block-deletes.py`](../gielinor/.claude/hooks/block-deletes.py) hook.

The agent **never deletes; it moves.** Each layer has an `archive/` that mirrors the
structure of its active content — a file at `bank/notes/x/y/z.md` archives to
`bank/archive/notes/x/y/z.md`, preserving the relative path. Two histories are kept, with
different meanings:

- **`archive/`** = "this used to be true; it isn't anymore." (Mirrors `confirmed/`.)
- **`rejected/`** = "this was proposed; it never qualified." (Mirrors `drafts/`.)

Why: recoverability (a wrong move is reversible forever), pattern memory (rejections reveal
where the agent's model drifts), and trust (the principal can authorise aggressive
reorganisation because it is never destructive). Filenames stay unique in their
destination; on collision, append a timestamp — never overwrite.

<a id="routing"></a>
## Layer routing — what content lands where

The quest-log is the path of least resistance (auto-write, no gate), so content drifts
there unless actively routed. The routing question is always: **what shape is this?**
Full table in [`layer-routing.md`](../gielinor/meta/layer-routing.md); the high-frequency
rows:

| If the content is… | …it lands in |
|---|---|
| Narrative of what happened this session | `quest-log/in-progress/SNNN_<sid8>_<slug>.md` |
| Resume state ("where we are / next step") | `inventory/<quest-slug>-resume__<sid8>.md` |
| Knowledge about a thing (mart, query, stakeholder) | `bank/drafts/notes/` → alching → `bank/notes/` |
| A full research writeup with sources | `research/<date>-<slug>.md`; pick into `bank/` during alching |
| A reusable method / workflow | `spellbook/drafts/skills/` → alching → `spellbook/skills/` |
| Self-observation about a player | `examine/drafts/` → approve → `confirmed/` |
| An observation about Niklavs | `niksis8(_character)/drafts/` → approve → `confirmed/` |
| A load-bearing deadline/commitment | `keepsake/proposals/` → pin to `current.md` |
| A decision about how the agent operates | `lorebook/drafts/` → `lorebook/confirmed/D-NNN_*.md` |
| Construction history (dev-brain only) | `developer-braindead/bank/decisions/D-NNN_*.md` |
| A pre-everything idea (`note this idea:`) | `brain/ideas/YYYY-MM-DD-<actor>-<slug>.md` |

Cross-cutting subtleties worth internalising: **research vs. bank** (the 2,000-word writeup
is research; the four load-bearing sentences picked from it are the bank note);
**methodology vs. domain knowledge** ("how to decompose moving-target work" is a *skill*;
"the EU Tender architecture" is a *bank note*). When genuinely ambiguous — **ask**; a
wrong-layer write costs a cleanup move later (and per archive discipline, never a delete).

## Ritual write-reach

Beyond the per-layer discipline, each ritual can only touch *certain layers at all*. This
matrix (from [`write-rules.md`](../gielinor/meta/write-rules.md) → *Ritual write-reach*) is
covered per-ritual in [06 — Rituals](06-rituals.md), but in brief: **alching** writes only
the active player's layers; **bankstanding** writes only globals (never per-player);
**consultation** writes only Guthix's own deity layers; **close-session** writes drafts /
quest-log / inventory / inbox but never promotes to confirmed.

<a id="naming"></a>
## File & naming conventions

| Pattern | Where | Meaning |
|---|---|---|
| `SNNN_<sid8>_<slug>.md` | `quest-log/in-progress/` | A session's narrative. `sid8` disambiguates parallel sessions ([D-024]). |
| `<quest-slug>-resume__<sid8>.md` | `inventory/` | Resume state for a quest. Legacy un-suffixed names remain readable. |
| `YYYY-MM-DD-<slug>.md` | `drafts/`, `research/` | Date prefix = when the observation/research happened. |
| `D-NNN_<slug>.md` | `lorebook/confirmed/`, dev `bank/decisions/` | A decision. IDs are stable and never reused. |
| `YYYY-MM-DD-<actor>-<slug>.md` | `brain/ideas/` | A captured idea, indexed by the actor at capture time. |

`sid8` = first 8 chars of `CLAUDE_CODE_SESSION_ID`. It anchors per-session files, intent
files, status records, and parallel-session disambiguation throughout the system.

---

Next: **[05 — Actors & modes](05-actors-and-modes.md)** — who operates these layers, and
the modes and roles that scope each session.
