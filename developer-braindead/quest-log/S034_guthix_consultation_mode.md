# S034 — Guthix consultation mode

> Doc-only session. Expanded Guthix from a ritual-only voice to a two-mode deity: consultation (default residence, general questions) + bankstanding (the ritual). Same actor, same sprite — different write authority. Wisp shrinks to "session that has had no prompt yet."

**Started.** 2026-05-22.

## What landed

[[D-022_guthix_consultation_mode]] — Guthix consultation mode. Doc changes across nine files in `gielinor/`:

- `meta/guthix.md` — major rewrite. Two residence modes; invocation contract reframed; refusal narrowed to "writing into a player's house."
- `meta/modes.md` — five session modes (was four). Unscoped narrowed to "no prompt yet"; Consultation block added; consultation→bankstanding flip rule.
- `CLAUDE.md` — `Hey Guthix` bullet reframed as general "ask me anything overall." Wisp's floor narrowed.
- `meta/write-rules.md` — Consultation row added to ritual write-reach table.
- `meta/layer-routing.md` — conversational-question row added.
- `meta/communication-protocol.md` — `guthix.txt` covers both consultation and bankstanding.
- `spellbook/rituals/bankstanding.md` — opening section reflects five modes; flip rule documented.
- `deities/_about.md` — two distinct residence modes; write-reach split.
- `deities/guthix/_about.md` — quest-log section covers `G-NNN_*` (consultation traces) alongside `B-NNN_*`.

Dev-brain:

- `bank/decisions/D-022_guthix_consultation_mode.md` — the decision doc.
- `quest-log/S034_guthix_consultation_mode.md` (this file).

## What didn't ship

- **No hook changes.** `guthix.txt` intent file already triggers the spawn-guthix event; consultation reuses the existing machinery. The hook can't distinguish consultation from bankstanding — intentional.
- **No visualizer changes.** Sprite, building (lorebook-library), float behavior all unchanged.
- **No write-boundary hook.** Consultation's tighter write surface (own deity layers only) is discipline, not architectural enforcement.

## How the conversation went

Niklavs landed in dev-brain mode and stated the ask in one line: *"We need to make guthix more versatile. He should be the guy i go to if i just have an overall question which i want to ask here."* Note: a parallel session was already mid-flight on a different topic; this entry was renamed from S034 → S034 mid-close after the collision surfaced in git status (the visualizer-audit S034 was started 6 min earlier).

I read the current Guthix spec, the deities directory, and the bankstanding ritual to understand existing scope. Proposed the shift as: consultation = default residence, bankstanding = one ritual he runs. Asked three design questions:

1. **Write reach in consultation.** Should consultative Guthix be able to drop bank drafts in his own deity bank during conversation? → **yes**.
2. **Trace shape.** Bankstanding gets `B-NNN`; should consultation get its own counter or stay chat-only? → **yes** (chat-only default; `G-NNN` when conversation produces something lasting).
3. **Where does wisp go?** → **wisp is only if truly nothing was prompted.**

Calls (1) and (2) matched my recommendations. Call (3) was sharper than I'd proposed — I'd suggested "session opener" as the wisp scope; the principal narrowed to literally "no prompt yet." Difference is meaningful: a session opened with no address but immediately receiving a substantive question routes to Guthix consultation, not wisp.

Then the edits, sequenced by file, tracked via task list.

## Observations worth carrying forward

**The redirect-list refusal pattern was a signal that the role was too narrow.** Guthix's previous "What he refuses" section had four bullet points — per-player work, dev-brain construction, single-player continuity, plus the implicit "anything not bankstanding." When an actor's refusal list grows to four items, the role definition is probably the problem, not the requests being declined. The post-S034 refusal is one line ("won't write into a player's house"). Watch for this pattern with other actors.

**"Consultation as default, ritual on cue" is a reusable shape.** Same actor, two modes, write authority varies by mode. The shape would extend cleanly if a second deity ever shows up (e.g., a destruction-focused voice with a `clean-house` ritual + a default "talk through what's stale" consultation). Don't generalize prematurely, but the precedent is now sitting in the meta files for the next deity to inherit.

**The principal's mental model is load-bearing.** When the principal said "he should be the guy I go to for overall questions," the meaning was *role assignment*, not *behavior tweak*. The architectural shift had to be visible in the doc surfaces the agent reads at session start — `CLAUDE.md`, `modes.md`, `guthix.md` — not just internal discipline. A purely-discipline change ("Guthix will now also answer general questions") would have evaporated by the next session because the address-routing rules in `CLAUDE.md` would still describe him as bankstanding-only.

**Wisp's overload was a symptom, not a cause.** Wisp carried "no player active" AND "the system reflecting on itself," and the latter was already moved to Guthix during S028 (bankstanding). What S034 finished was the *other* half — "no player active but principal is asking about the brain." Now wisp carries one job: blank-session opener. The split done in S028 was the harder half (a ritual voice splitting off); S034's split is the easier one (a default conversational target). Pattern: when an actor is doing two unrelated jobs, expect to split both off in sequence, not at once.

**Bankstanding being one mode of Guthix (not all of him) makes future rituals easier.** If we later want a `Hey Guthix, audit lorebook` mode that's lighter than full bankstanding, it's now a third mode on the same actor rather than a forced rebrand. The shape is open.

## Next steps

- **Live test consultation.** Open a fresh session, address `Hey Guthix, what do I have on EU Tender 2026 across the brain?` and observe: (a) intent file `guthix.txt` written, (b) spawn-guthix event fires, (c) Guthix sprite appears, (d) the answer comes back in Guthix voice, (e) no writes to globals or per-player layers, (f) no quest-log entry unless the conversation produces something worth surfacing.
- **Live test the flip.** Start a consultation; mid-chat say "ok, let's bankstand on this." Observe: write authority widens; bankstanding procedure begins; `B-NNN` lands on close.
- **Watch wisp's role over time.** Now that the floor has narrowed, see whether wisp sessions effectively cease to exist or whether the "blank opener" pattern is more common than expected.
- **Observe `G-NNN` cadence.** Empirical question — how often do consultations produce traces?
- **Update `respawn.md`.** S034 doesn't change the next-concrete-step. The visualizer Step 0 from S031 still needs verification. But the open-questions section may want a "post-D-022 live test consultation" item.

## Cascade

- `bank/decisions/D-022_guthix_consultation_mode.md` (new — the decision).
- `quest-log/S034_guthix_consultation_mode.md` (this file).
- `respawn.md` (overwritten at close).
- `comms/active.md` (CLOSING).

## Main-brain changes

Nine doc surfaces in `gielinor/` — pure doc + discipline shift; no hooks, no visualizer, no code.

- `meta/guthix.md` — major rewrite. Two residence modes; invocation menu offering both consultation answers and ritual cues; refusal narrowed to "won't write into a player's house."
- `meta/modes.md` — five session modes (was four). Consultation block added; Unscoped narrowed; consultation→bankstanding flip rule.
- `CLAUDE.md` — `Hey Guthix` reframed as general "ask me anything overall" actor; wisp's floor narrowed.
- `meta/write-rules.md` — ritual table gains a Consultation row above Bankstanding; voice line covers both modes.
- `meta/layer-routing.md` — new conversational-question row (chat-only default; optional `G-NNN_*` trace).
- `meta/communication-protocol.md` — active-actor-by-mode bullet covers both consultation and bankstanding under `guthix.txt`.
- `spellbook/rituals/bankstanding.md` — opening lifts to five modes; flip rule.
- `deities/_about.md` — two-mode residence; write-reach split between consultation and bankstanding.
- `deities/guthix/_about.md` — quest-log section documents `B-NNN_*` and `G-NNN_*` prefixes; inventory mentions consultation use.
