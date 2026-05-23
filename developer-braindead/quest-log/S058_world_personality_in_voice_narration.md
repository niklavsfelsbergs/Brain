# S058 — 2026-05-23 — World personality: in-voice intent narration

Principal opened in Guthix consultation ("our world has no personality — make the players talk more lively and different each, not flat like this"), then pivoted to dev-brain. Two asks; the second (a waiting-on-subagents status) was already shipped by sibling [[S057]], so this session was the personality half.

- **Diagnosis — the flatness was a rule.** [[communication-protocol.md]] mandated intent narration be "functional, verb + noun, ≤100 chars." Personas were distinct only in terminal *responses*; the world surface (COMMS chat + row subtitle, post-S052 — map/bubbles gone) only ever saw the flat line. Leverage point: the COMMS feed renders every intent line as `<Actor>: <text>`, so making those in-voice livens chat + subtitle at once.
- **Length, corrected mid-design.** First longer examples padded prose; principal pushed back — "using the space for the fuck of it." Reframed: longer = more *skimmable content*, not more words. Jebrim especially → terse dense status line. Saved as a feedback memory ([[feedback-content-over-verbosity]]).
- **Hooks (caps).** `INTENT_MAX_LEN` 100→280, `SUBTITLE_MAX_LEN` 100→280, `CHAT_TEXT_MAX` 200→320 in both [[status-sidecar.py]] and [[emit-event.py]], so intent runs 2–3× longer end-to-end.
- **Rule + voice cards.** `communication-protocol.md` retires the functional verb-noun rule for in-voice narration + a content-over-verbosity clause + a per-actor content table. Voice cards added to `jebrim/persona.md` (skimmable data status line), `zezima/persona.md` (reflection is the content), `meta/guthix.md` (cross-layer state, kept "never warm/playful"), and dev-brain `CLAUDE.md` (Braindead build-state) — each defines *what kind of content* it packs.
- **D-024 lived (again).** Sibling **braindead-e433ac17** (S056) was live on the 3 switchboard client files (confirmed via its status file — working, 61s). Stayed entirely off them; did the length work in the uncontested hooks + gielinor docs. Deferred the one shared tweak (`.sb-intent` line-clamp 2→~4) to a post-S056 pass; pinged them in comms. Impl commit **4af5279**.

**Cascade.** This quest entry; `respawn.md` head + Where-we-are + carried-open; comms `OPEN`/`CLOSING` + e433ac17 ping; impl commit 4af5279 (caps + rule + cards); dev-brain `CLAUDE.md` Braindead voice card.

**Main-brain changes.** `gielinor/meta/communication-protocol.md`, `gielinor/meta/guthix.md`, `gielinor/players/jebrim/persona.md`, `gielinor/players/zezima/persona.md` — the in-voice rule + four voice cards.
