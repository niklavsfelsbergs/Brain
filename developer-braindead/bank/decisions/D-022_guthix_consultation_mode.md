# D-022 — 2026-05-22 — Guthix consultation mode (general-question deity)

**Context.** Guthix has been a ritual-only voice since [[D-016]]-adjacent S028 work (subtask channel + Guthix landing) and the meta/guthix.md shipped soon after. He existed *only* during bankstanding — the ritual was his entire purpose. Anything outside that shape was refused with a redirect.

The friction surfaced in S034: Niklavs wanted a place to go for *general overall questions* about the brain — *"what do I have on X across the brain?"*, *"is anything in lorebook contradicting itself?"*, *"help me think about this design"*. The actor for those questions was undefined. Wisp (unscoped mode) was the default fallback, but wisp has no curation lens, no system-aware framing, no continuity. The principal's mental model — *"the brain's caretaker should be the actor I ask about the brain"* — didn't match the architecture.

**Decision.** Expand Guthix from a ritual-only voice to a **two-mode deity**: a consultation residence (default) and a bankstanding residence (the ritual). Same actor, same voice, same sprite; different write authority.

## The two modes

| Aspect | Consultation | Bankstanding |
|---|---|---|
| **Trigger** | `Hey Guthix, ...` with anything other than a ritual cue. `Hey Guthix` alone opens with a menu offering both. | `Hey Guthix, bankstand` / `let's bankstand` / `Hey Guthix, triage drafts` / `Hey Guthix, audit {layer}` |
| **Reads** | everything | everything |
| **Writes** | only his own deity layers (`bank/drafts/notes/`, `inventory/`, `quest-log/in-progress/G-NNN_*`) | globals (drafts/proposals) + own deity layers + `proposals/` for godly proposals |
| **Trace** | chat-only by default; quest-log entry `G-NNN_*` only when conversation produces something worth surfacing next respawn | always lands `B-NNN_*` on ritual close |
| **Refusal** | won't write into a player's house (alching's job); won't do dev-brain construction | same refusals, applied during the ritual |

## What the user can ask in consultation

- *"What do I have on X across the brain?"* — cross-player or cross-layer lookup.
- *"Is anything in {layer} contradicting itself?"* — drift check.
- *"Help me think about {design question}."* — system-shaped reflection.
- *"What's overdue?"* — pending drafts, aging alchings, stale entries.
- Anything else that isn't player-scoped and isn't dev-brain construction.

Consultation can *flip into* bankstanding on explicit cue ("ok, let's bankstand on this") when the conversation surfaces enough work to warrant the ritual.

## Wisp shrinks

Wisp's territory narrows to "session that has truly had no prompt yet." The moment the principal speaks substantively without addressing someone specifically, route to Guthix (consultation) — questions about the brain are Guthix's now, not the wisp's. This was the principal's explicit call in S034 ("wisp is only if truly nothing was prompted").

The implication: most sessions that used to default to wisp will now default to Guthix the moment the first real question lands. Wisp persists as the "blank session" actor only.

## What changed on disk

- `gielinor/meta/guthix.md` — major rewrite. New "Two residence modes" section. "Invocation contract" reframes to consultation-default with rituals as opt-in. "What he refuses" narrows from a four-bullet redirect list to a one-line discipline ("writing into a player's house").
- `gielinor/meta/modes.md` — lifts session-mode count from four to five. Adds Consultation mode block. Narrows Unscoped mode prose. Adds the consultation→bankstanding flip rule.
- `gielinor/CLAUDE.md` — `Hey Guthix` bullet reframed: general "ask me anything overall" actor; rituals on cue. Narrows the no-address bullet to clarify wisp's new floor.
- `gielinor/meta/write-rules.md` — ritual write-reach table renamed to Ritual/Mode and gains a Consultation row above Bankstanding.
- `gielinor/meta/layer-routing.md` — new row for conversational question / overall reflection, pointing at `deities/guthix/quest-log/in-progress/G-NNN_*` (optional) and `bank/drafts/notes/` (when an observation emerges mid-chat).
- `gielinor/meta/communication-protocol.md` — active-actor-by-mode bullet extended so `guthix.txt` covers both consultation and bankstanding.
- `gielinor/spellbook/rituals/bankstanding.md` — opening section lifts to five session modes; adds the flip rule.
- `gielinor/deities/_about.md` — new "two distinct modes" section; write-reach split between consultation and bankstanding.
- `gielinor/deities/guthix/_about.md` — quest-log section now describes both `B-NNN_*` and `G-NNN_*` prefixes; inventory section mentions consultation use.

## Why this shape

Three reasons:

1. **Mental-model match.** The principal already thinks of Guthix as "the brain's caretaker." Limiting him to bankstanding made the architecture surprise the user every time a system-level question arose. Expanding the role to "consultation default, ritual on cue" is the cheaper fix vs inventing a second system-level deity.
2. **No new infrastructure needed.** Guthix already has a sprite, a building (lorebook-library), intent-file machinery, spawn/despawn hook events, and write-boundary discipline. Consultation reuses every one of those. The change is doc-only on disk plus a behavioral discipline at runtime.
3. **Wisp gets a clean role.** Wisp was overloaded: "no player active" AND "the system itself, reactively." Splitting that — wisp = blank session, Guthix = consulted on questions — gives each actor a single clear job. Parallels the prior split in S028 (wisp → Guthix for bankstanding); this is the same split extended one degree further.

## What it doesn't do

- **No new hook.** The `guthix.txt` intent file already triggers the spawn-guthix event; consultation reuses it. The hook cannot distinguish consultation from bankstanding, and that's intentional — the visualizer just shows Guthix in residence.
- **No new write-boundary enforcement.** Consultation's tighter write surface (own deity layers only, no globals) is discipline, not architectural. If discipline slips and Guthix starts auto-writing to globals during consultation, that's worth a hook later — for now the same shape applies as the bank-drafts gate.
- **No retired files.** Nothing moves to archive. The shift is in scope and discipline, not in structure.
- **No visualizer change.** The sprite/building/float behavior all stay as-is.

## Open questions

- **How often does consultation produce a `G-NNN` trace?** Empirical question — observe over the next few sessions. If most consultations leave nothing, the `G-NNN` prefix earns its place by being rare. If consultations routinely produce traces, the discipline of "only when worth surfacing" needs sharper criteria.
- **Should consultation-discovered bank drafts trigger an alch recommendation?** When Guthix in consultation drafts a cross-cutting observation into his own bank, that's a signal worth surfacing. Maybe at session-close. Defer.
- **Consultation in dev-brain mode.** `Hey Guthix` from a dev-brain session should still work (the cue is global). Behavior should be identical — Braindead becomes the outgoing actor in a mini-respawn, Guthix descends, and the consultation runs against `gielinor/`. Confirm in live use.
- **Sticky after consultation.** If a session goes Player → `Hey Guthix` (consultation) → no further address, does the next message stick with Guthix or fall back to the player? Per `gielinor/CLAUDE.md`, no-address is sticky on whatever actor is active — so the next message stays with Guthix until an address says otherwise. Worth watching whether that's the right default.

## Related

- [[D-013]] — Braindead character and workshop (the original "non-player actor" pattern Guthix followed).
- [[D-016]] — Gnomes sub-agent (precedent for splitting roles by function).
- [[D-018]] — Per-session intent files (the substrate consultation reuses).
- [[D-019]] — Parallel Braindead + comms channel (precedent for two actors sharing infrastructure with different roles).
- [[D-021]] — Penguins research sub-agent (the "outward-facing" role; Guthix consultation is the "inward-facing across the whole brain" complement).
- `gielinor/meta/guthix.md` — the load-bearing spec post-S034.
- `gielinor/meta/modes.md` — the five-modes definition.
