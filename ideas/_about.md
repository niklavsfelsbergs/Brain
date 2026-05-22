# ideas/ — pre-everything capture

A flat folder at brain root for ideas the principal wants to record without designing a home for them. One file per idea. No drafts, no proposals, no promotion ceremony — just a place to drop a thought and move on.

This is **not** a layer in either brain. It's a low-friction sidecar shared between `gielinor/` and `developer-braindead/` (and accessible to Guthix and the wisp). When the principal says "note this idea: X" mid-session, the active actor writes one file here and returns to whatever they were doing.

## File shape

One file per idea. Filename:

```
YYYY-MM-DD-<actor>-<slug>.md
```

- **Date.** When the idea was captured (today's date in the agent's clock).
- **Actor.** Who was in residence when the idea landed — `jebrim`, `zezima`, `braindead`, `guthix`, `unscoped`. Use the active actor of the session at the moment of capture. For Guthix consultation this is `guthix`; for dev-brain this is `braindead`; etc.
- **Slug.** Short kebab-case description, ~3-6 words. Enough to grep for, not a title.

Examples:

- `2026-05-22-braindead-cross-window-focus-fallback-chain.md`
- `2026-05-22-jebrim-rollup-cache-warming-on-stakeholder-cadence.md`
- `2026-05-22-guthix-deity-for-the-niksis8-layer.md`

File body is just the idea, in whatever form the principal said it. No frontmatter required; the filename carries the metadata. If the principal explained context in the same message, capture that too — but **don't elaborate**, don't design, don't expand. Capture verbatim or near-verbatim and move on.

## Capture trigger

When a message contains `note this idea: <text>` (case-insensitive, colon required), the active actor:

1. Resolves a slug from the idea text (3-6 words, kebab-case, lowercase).
2. Writes `brain/ideas/YYYY-MM-DD-<active-actor>-<slug>.md` containing the idea body.
3. Acknowledges in one line (e.g., *"Noted as `2026-05-22-braindead-<slug>`."*) and returns to whatever was active.

**No clarifying questions.** The capture is meant to be free — the principal will triage later. The only acceptable interrupt is a filename collision (rare given the date+actor+slug shape); on collision, append `-2`, `-3`, etc. and proceed.

The trigger can sit anywhere in the message. The principal might say `Hey Jebrim, look at the rollup query, and also note this idea: cache warming on stakeholder cadence` — the capture happens alongside the substantive work, not instead of it.

## Listing trigger

When a message asks for ideas in the principal's voice — patterns like *"what ideas have I had"*, *"list my ideas"*, *"show me ideas"*, *"any ideas from {actor}"*, *"ideas about X"* — the active actor reads the folder and surfaces what's there. Shape:

- Default grouping: **by actor**, newest first per actor.
- One line per idea: `YYYY-MM-DD — <actor> — <slug>` plus a sentence from the body if the slug isn't self-explanatory.
- Filters honored when asked: by actor (*"Jebrim's ideas"*), by recency (*"ideas this week"*), by keyword (*"ideas about the visualizer"*).
- Listing is read-only. Don't propose promotions inline unless the principal asks.

## Who writes here

Any actor in residence when the principal says "note this idea: …" — players, Braindead, Guthix, wisp. **Principals only.** Dwarves, gnomes, and penguins don't capture ideas; if they notice something worth a future idea, it lands in their quest-log entry and the principal can lift it to an idea later.

No hooks gate this folder. The discipline is: principal-prompted captures only, and only via the trigger phrase. The agent does not preemptively capture observations as ideas — that's what drafts (`examine/`, `niksis8/`, `bank/`, `lorebook/`) are for. Ideas are explicitly principal-initiated.

## What ideas are not

- **Not drafts.** Drafts are observation-backed claims aiming for promotion to a canonical surface (identity, bank notes, decisions). Ideas are unrouted thoughts that haven't earned a shape yet.
- **Not quest-log entries.** Quest log is the narrative of work being done. Ideas are not work; they're seeds.
- **Not keepsake pins.** Keepsakes are load-bearing current state. Ideas are speculative.
- **Not decisions.** Decisions (`lorebook/confirmed/D-NNN`, `developer-braindead/bank/decisions/D-NNN`) are settled architectural commitments. Ideas may eventually become decisions; most won't.

If a thought is shaped like one of the above, route it to the right layer per `gielinor/meta/layer-routing.md`. Use `ideas/` for the everything-else case where the principal wants to record the thought before knowing what it is.

## Promotion (manual, later)

There is no automatic promotion ritual. When the principal sees an idea ripe to graduate, they say so:

- *"Promote `2026-05-22-jebrim-rollup-cache-warming` to a Jebrim bank draft"* → write to `gielinor/players/jebrim/bank/drafts/notes/`, archive-move the idea file.
- *"Make `2026-05-22-braindead-…` a decision"* → write `developer-braindead/bank/decisions/D-NNN_<slug>.md`, archive-move.
- *"Drop `2026-05-22-…`"* → move to `ideas/archive/rejected/`.

Per `meta/archive-discipline.md`, ideas are never deleted. Graduated ideas move to `ideas/archive/promoted/<destination-pointer>.md` (a stub that names where the idea went). Rejected ideas move to `ideas/archive/rejected/`.

If the folder grows to the point that browsing becomes painful, a triage ritual can be added then — not now. **Don't pre-build for hypothetical scale.**

## Related

- `gielinor/meta/layer-routing.md` — the row that points here and the surrounding routing table.
- `gielinor/meta/archive-discipline.md` — never-delete rule that governs `ideas/archive/`.
- Brain-root `CLAUDE.md`, `gielinor/CLAUDE.md`, `developer-braindead/CLAUDE.md` — reference the trigger phrase so the active actor in any mode can capture.
