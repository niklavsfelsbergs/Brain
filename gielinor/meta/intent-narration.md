# Intent narration & the visualizer sidecars

> **Loaded just-in-time, not eagerly (Phase-1 trim, §X Stage C — see `developer-braindead/bank/plan.md` and [[D-032_braindead_full_access|D-032]]).** This is the *operational* half of the communication protocol — how the active actor writes its per-turn bubble, the `.mode` ritual-lifecycle marker, the system-voice narration channel, and the intent-vs-action discipline that keeps the two channels from echoing. It is **visualizer/cockpit plumbing**, not a per-response behavioral rule, so it does not need to ride in context every turn.
>
> **Re-trigger (R1).** `spellbook/rituals/respawn.md` reads this file at session start — before the first intent line is written — so the mechanics are in context for the whole session the moment the actor begins narrating. The `.mode`-writing rituals (`alching`, `bankstanding`, `drafts-triage`, `close-session`, consultation) also point here for the marker detail. The *behavioral* core (Understanding/Plan preamble, five-lens, copyable-deliverables, wrong-instance, Guthix-routing, multiple-choice) stays always-on in `meta/communication-protocol.md`.

## Intent narration (visualizer sidecar)

After stating the Plan, write the intent line **in the active actor's voice** (1–3 sentences, ≤280 chars) to `.claude/intent/<actor>-<sid8>.txt` at the brain root, where `<sid8>` is the first 8 characters of `CLAUDE_CODE_SESSION_ID` (the env var Claude Code exposes per session). The per-session filename is the **only** sanctioned shape — it prevents two parallel sessions of the same actor from clobbering each other's bubble on disk (see [[D-018_close-session-ritual-adoption]]) AND serves as the on-disk session anchor that lets the hook recover actor attribution after a `state.ndjson` truncation/reset (the disk-fallback path in `current_main_actor`). Applies to **every** actor: players (`jebrim`, `zezima`), Braindead, Guthix, and Wisp. If `CLAUDE_CODE_SESSION_ID` is genuinely unavailable (very rare), surface that to the principal rather than falling back to bare files — bare files have no session ownership and break the recovery path. The visualizer reads the file and renders a speech bubble near the actor (wraps to two lines centered) and also pushes the same string into the COMMS chat panel as `<Actor>: <text>`.

- **Active actor by mode.** Player session → `<player>.txt` (e.g., `jebrim.txt`, `zezima.txt`). Dev-brain session → `braindead.txt`. Unscoped session (no prompt yet) → `wisp.txt`. Consultation or bankstanding (any session, on `Hey Guthix` or `let's bankstand`) → `guthix.txt` (the deity who tends the brain; see [[guthix]] and `modes.md` consultation and bankstanding sections).
- **Voice, not verb-noun ([[S058_1f0ae59a_shipping-contract-corpus-ingest]]).** Write the line **in the active actor's voice** — the COMMS feed should read as live work in character, not a flat log. The old "functional, verb + noun" rule is retired.
- **Content over verbosity.** The ≤280-char budget buys *more content* — what's happening, in skimmable form — never padding. A tight line beats a padded one; don't use the space for its own sake. What each actor packs differs:
  - **Jebrim** — data/steps/state as a skimmable status line (`dim_customer dedup → period sums → reconcile vs Apr. Step 1/3.`). Terse-and-dense *is* his personality; verbosity breaks character.
  - **Guthix** — cross-layer state: counts, contradictions, what he's weighing. Measured, never warm or playful.
  - **Braindead** — build state: what's torn open, what's load-bearing, what he's watching for.
  - **Zezima** — the reflection itself is the content; prose is legitimate here, but still no padding.
  - **Wisp** — almost nothing; stays short and uncommitted.
- **Still present tense, still no "I will now…".** And still abstract enough not to be a bare restatement of the last tool call — the action stream already shows file-level steps. Intent carries the in-voice narrative; action carries the steps. They complement, they don't echo.
- Each actor's full register lives in their **voice card** — `players/<name>/persona.md`, `meta/guthix.md`, and the dev brain's `CLAUDE.md` for Braindead.
- **Update when intent meaningfully changes**, not every micro-action. A turn that's mostly reads with one edit gets one intent line. A turn that pivots — finish one thing, start another — gets two writes in sequence.
- **Dwarves don't write intent files.** The hook attaches the Task call's `description` field as the dwarf's bubble at spawn time; that bubble persists for the dwarf's lifetime.
- **No file → no bubble.** Skipping intent narration in turns that don't run the visualizer is fine; the file is a hint, not a contract. If a turn doesn't write, the previous intent stays up until the actor moves buildings (then it clears).
- **Don't narrate the intent line itself in the visible response.** It's a sidecar — the agent doesn't say "I'm setting my intent to X"; it just writes the file.

### Mode marker sidecar (`.mode`)

Alongside the per-session intent file there is an optional **mode marker** at `.claude/intent/<sid8>.mode` (keyed by sid8 only — it's per-session, not per-actor). It carries a single token the event stream can't infer on its own, so the switchboard can render a ritual-lifecycle chip:

- `alching` — written on entry to a principal-self alching pass, cleared on exit. Row reads `ALCHING`. See `spellbook/rituals/alching.md`.
- `bankstanding` — written on entry to the bankstanding ritual, cleared on close. Row tags `bankstanding`. During Phase 0 the per-player alching sub-pass writes `alching`, then restores `bankstanding` on Phase 0 exit. See `spellbook/rituals/bankstanding.md`.
- `consultation` — written on a `Hey Guthix` consultation entry, cleared on returning to a player or on close. Row tags `consulting`. See [[guthix]] → *Visualizer*.
- `drafts` — written on entry to the drafts-triage ritual, cleared on report/exit. Row tags `drafts`. See `spellbook/rituals/drafts-triage.md`.
- `closing` — written as the *first* action of close-session, when the wrap starts. Row reads `WRAPPING UP` (the mid-wrap phase), or `YOUR MOVE · wrapping up` if the close pauses for a nod. Overwritten by `wrapped_up` as the final action. See `spellbook/rituals/close-session.md`. (S141.)
- `wrapped_up` — written as the final action of close-session. Row reads `WRAPPED UP` ("done, terminal still open") until the process ends; a fresh prompt auto-clears it. See `spellbook/rituals/close-session.md`.

`status-sidecar.py` reads the marker. `wrapped_up` sets base state `done` (shown `WRAPPED UP`); `closing` keeps the base state but the board promotes it to a `WRAPPING UP` main chip (or a sub when a ball-state holds the main); the ritual-flavor markers (`alching` / `bankstanding` / `consultation` / `drafts`) ride as a flavor *tag* on the base state (typically busy) and never hide a `needs_you` / `your_move` block. Like the intent file it's a hint, not a contract — no marker just means no chip. Written by the rituals, not narrated in the visible response.

## Narration channel (system voice)

Alongside the per-actor intent file, there is a single global narration sidecar at `.claude/narration.txt`. Same overwrite semantics as `intent/*.txt` — the file holds the most recent narration line; the chat keeps history. Cap ≤200 chars.

Narration is **system voice**, not actor voice. The agent doesn't speak it in character. Use it for broader-scope context that surfaces above the per-actor flow:

- Session boundaries — *"Session S017 opens — Jebrim active"*.
- Ritual phase transitions — *"Bankstanding phase 0 begins"*, *"Phase 0 complete — back to bankstanding mode"*.
- Mode switches — *"Switching to dev-brain mode"*, *"Returning to gielinor — Zezima active"*.
- Quiet declarations of structural intent that don't fit a single actor's mouth.

Don't write narration for every turn. Most turns don't warrant it. The bubble + chat already carry per-turn intent; narration is for the events *between* them.

## Intent vs action — discipline rule

Two channels for "what's happening now," and they must not mirror each other:

- **Intent** = *why* and *what scope*. "Drafting D-014", "Wrapping up S016", "Bankstanding — phase 0". Authored by the agent. This is **scope-why** — a one-line label of what's underway — and it is a **cockpit-facing status line**, read at a glance off the board. It is not the place for the reasoning behind a plan (see below).
- **Action** = *which file* or *which command*. "Jebrim: editing meta/communication-protocol.md", "Braindead: running git status". Emitted automatically by the hook on Edit/Write/Bash/Glob/Grep.

If the intent line restates what the actions already show ("Editing communication-protocol.md"), the chat doubles itself and intent loses its signal. Keep intent abstract enough that the action stream complements rather than echoes it.

**Render the cut, not the keystrokes.** There is a third thing, distinct from both channels above: **the cut** — the *decomposition reasoning* behind a plan (why six engines and not five, why this split and not that one). In a multi-step turn the cut is the highest-value signal, and it is tempting to pour it into the bubble. Don't. The bubble is a ≤280-char cockpit status surface; it physically cannot carry the reasoning, and forcing it makes the bubble render the keystrokes (what's happening) dressed up as rationale. The cut already has a home where the principal reads it: the **Understanding/Plan preamble** and the **task-list** (`communication-protocol.md` → *Task-list surfacing* — the decomposition surfaces in or just after the Plan line). Put the reasoning there; let the bubble be honestly the scope-status it is. In one line: *the bubble says what scope is underway; the Plan line says why it's cut this way.* (Founding: the §R.3 finding from the Braindead↔Jebrim self-review, landed as a Guthix godly proposal 2026-05-30.)

## Related

- `meta/communication-protocol.md` — the always-on behavioral core (preamble, five-lens, copyable-deliverables, wrong-instance, Guthix-routing, multiple-choice). This file is the operational sidecar half split out of it.
- `spellbook/rituals/respawn.md` — reads this file at session start (the R1 re-trigger).
- Per-player `persona.md`, `meta/guthix.md`, dev-brain `CLAUDE.md` — the voice cards each actor's intent line is written from.
