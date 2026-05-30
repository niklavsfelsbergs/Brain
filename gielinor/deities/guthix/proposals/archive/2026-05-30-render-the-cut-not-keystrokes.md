# Proposal — render the cut, not the keystrokes

**Drafted.** 2026-05-30, bankstanding (scoped, Guthix). Surfaced by the §R.3 finding from the principal-staged Braindead↔Jebrim conversation in the dev brain (the "self-review via in-character dialogue" pass; dev-brain plan §R, hand-off carried through to the dev S130 close). This is the third and last of the three findings that conversation produced — the first two (comms append-lock, graduation = clerk-not-nanny) are built and live; this one targets a user-only meta surface, so it routes here.

## 1. Observation

The intent bubble (`.claude/intent/<actor>-<sid8>.txt`, rendered on the cockpit and pushed into COMMS) is meant to carry *why/scope*, with the action stream carrying *which file*. In practice the bubble drifts into rendering **what is happening** — a prose echo of the keystroke stream the hook already emits — when the load-bearing signal in a multi-step turn is **why it was cut this way**: the decomposition reasoning (why six engines and not five, why this split and not that one).

The existing rule already half-sees this. `meta/communication-protocol.md` → *Intent vs action — discipline rule* (lines 200–207) says intent ≠ action and "if the intent line restates what the actions already show… intent loses its signal." But it frames intent as a single undifferentiated "why," which is the blur: it does not distinguish the **scope-why** the bubble *can* hold from **the cut** (the reasoning) the bubble *cannot* hold in ≤280 chars. With that distinction missing, the agent keeps trying to make the bubble carry the reasoning, and the result reads as keystrokes-dressed-as-rationale.

The reasoning already has a home where the principal actually reads it: the **Understanding/Plan preamble** and the **task-list** (*Task-list surfacing*, lines ~83–92 of the same file, already says "the decomposition surfaces in or just after the Plan line"). The proposal makes that division explicit so the bubble stops doing a job it can't.

## 2. Proposed change

One refinement to `meta/communication-protocol.md` → *Intent vs action — discipline rule*: tighten the **Intent** bullet to name *scope-why* as cockpit status, and add a short paragraph naming *the cut* and pointing it at the Plan line. Diff-shaped (additions marked `+`):

```
 ## Intent vs action — discipline rule

 Two channels for "what's happening now," and they must not mirror each other:

-- **Intent** = *why* and *what scope*. "Drafting D-014", "Wrapping up S016", "Bankstanding — phase 0". Authored by the agent.
+- **Intent** = *why* and *what scope*. "Drafting D-014", "Wrapping up S016", "Bankstanding — phase 0". Authored by the agent. This is **scope-why** — a one-line label of what's underway — and it is a **cockpit-facing status line**, read at a glance off the board. It is not the place for the reasoning behind a plan (see below).
 - **Action** = *which file* or *which command*. ... Emitted automatically by the hook on Edit/Write/Bash/Glob/Grep.

 If the intent line restates what the actions already show ("Editing communication-protocol.md"), the chat doubles itself and intent loses its signal. Keep intent abstract enough that the action stream complements rather than echoes it.
+
+**Render the cut, not the keystrokes.** There is a third thing, distinct from both channels above: **the cut** — the *decomposition reasoning* behind a plan (why six engines and not five, why this split and not that one). In a multi-step turn the cut is the highest-value signal, and it is tempting to pour it into the bubble. Don't. The bubble is a ≤280-char cockpit status surface; it physically cannot carry the reasoning, and forcing it makes the bubble render the keystrokes (what's happening) dressed up as rationale. The cut already has a home where the principal reads it: the **Understanding/Plan preamble** and the **task-list** (*Task-list surfacing* above — the decomposition surfaces in or just after the Plan line). Put the reasoning there; let the bubble be honestly the scope-status it is. In one line: *the bubble says what scope is underway; the Plan line says why it's cut this way.*
```

No other file changes. The voice cards (`players/*/persona.md`, `meta/guthix.md`, the dev brain's `CLAUDE.md`) already describe the bubble as a skimmable in-voice status line — this proposal is consistent with them and needs no edits there.

## 3. Reasoning

- **It resolves a live blur, not a missing rule.** The "don't echo actions" half is already written; what's missing is *where the reasoning goes instead*. Naming scope-why vs the-cut gives the agent a positive target (the Plan line) rather than only a prohibition.
- **It matches the substrate.** A 280-char overwrite-on-change sidecar is structurally a status surface, not a notebook. The rule should ask of each channel only what it can deliver.
- **It is cheap.** A few lines in one section; backward-compatible; no migration. The existing *Task-list surfacing* and *Understanding/Plan* sections already hold the reasoning — this just points at them.

Cost to land: one principal edit (or my edit under D-017 explicit permission) to a user-only file.

## 4. Scope of impact

- **Surface touched:** `meta/communication-protocol.md`, the *Intent vs action — discipline rule* section only.
- **Actors affected:** every actor that writes an intent line (Jebrim, Zezima, Braindead, Guthix, Wisp) — but only as a clarification of existing discipline; no actor's behavior is newly constrained, the reasoning simply lands in the Plan line it already occupies.
- **Migrate/backfill:** none. No prior intent files or quest-logs need changing.
- **Cockpit/hooks:** untouched. The bubble's rendering and the event taxonomy do not change; this is doctrine, not code.

## 5. Alternatives considered

- **Do nothing — the existing "don't echo actions" rule covers it.** Rejected: it covers the prohibition, not the redirection. The recurrence (the bubble still drifts to keystrokes) is evidence the prohibition alone hasn't held.
- **Make the bubble carry the cut (raise the char budget).** Rejected: the cut is often a paragraph of reasoning; no sane bubble budget holds it, and the cockpit wants a glanceable status, not an essay. Wrong surface.
- **Add a separate "reasoning" sidecar channel.** Rejected as over-building (the *Minimal-action* lens): the Plan line + task-list already are that channel, and the principal reads them in the transcript, not on the board. A new channel is structure without a need.

## 6. Risk if landed wrong

Low. Worst case the new paragraph reads as redundant with the existing "don't echo" sentence and adds a few lines of doctrine no one needed — a cosmetic cost, reversible by a one-line edit (no-deletes makes it a `git mv`/revert away). There is a mild risk of *over-correction* — an actor stripping the bubble to a bare verb because "reasoning goes elsewhere" — so the proposed text explicitly preserves the in-voice scope-status the voice cards require. No data, no history, and no enforced invariant is touched.
