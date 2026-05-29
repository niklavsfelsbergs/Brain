# S120 — Khaan item 4: the five-lens decision scaffold (tight doctrine)

**Session:** dev-brain (Braindead), sid `885d6702`. Entered mid-conversation via "lets develop gielinor, lets continue with khaan". 2026-05-29.

## What was asked

Continue the Khaan thread. Per the [[S118_e0a88f49_khaan-item-6-freshness-header|S118]] hand-off, the dev-buildable carries were nearly exhausted: the `meta/write-rules.md` "enforced by hook" line is a *bankstanding* job (godly proposal, not a Braindead edit), which left **item 4 — the 5-lens decision scaffold** as the only remaining dev-buildable Khaan item.

## Decision (WITH the principal, multiple-choice)

Offered three options: (A) tight doctrine, (B) hold it like item G, (C) flip to Guthix for the write-rules carry instead. **Principal chose (A) tight doctrine.**

The honest tension I surfaced: three of Khaan's five lenses already exist as separate working rules (wrong-instance check = Contrarian, anchor-referent = Recall, the over-build lessons = Minimal-action), so the question was whether *naming them as one frame* pays rent or just adds ceremony — exactly what item 4's own Minimal-action lens guards against. Verdict: the genuinely-new value is naming **Contrarian + Minimal-action** as a standing brake; the other three become cross-links.

## What was built

A doctrine subsection **"The five-lens read — for genuinely ambiguous or high-blast-radius asks"** in `gielinor/meta/communication-protocol.md`, inserted between *Compression for trivial requests* and *Copyable deliverables* — completing a depth gradient (default preamble → trivial/shallow → ambiguous-or-high-blast-radius/deep).

- Five lenses: **Literal / Identity-shaped / Recall-shaped / Contrarian / Minimal-action.**
- Framed as an **internal** check that fires *only* on genuinely-ambiguous or high-blast-radius asks — **not per-turn, not shown to the principal.** It shapes the Plan line + the multiple-choice options, nothing more.
- Recall→anchor-referent, Contrarian→*Wrong-instance check*, Minimal-action→over-build lessons (the three cross-links); Contrarian + Minimal-action named as the standing brake.
- Cross-linked to [[D-025_offer-multiple-choice-with-recommendation|D-025]] (the surface the lens-divergence feeds).

**`meta/` is user-only — principal explicitly authorized ("do it"); I applied the edit directly** per [[D-017_user-only-with-explicit-permission|D-017]]. Same adaptation move as items 5/6/G (take Khaan's mechanism, fit it to our substrate — now 4-for-4 on adapt-don't-port-literally).

`bank/plan.md` §P.8 → `[x]`. **The Khaan dev-buildable sequence is now CLOSED** — only the `meta/write-rules.md` "enforced by hook" godly proposal remains (a bankstanding/Guthix job); everything else is later-phase or polish.

## Sibling collision — surfaced, not synthesized

On respawn, sibling detection flagged `braindead-86344868` as live-ish (intent fresh at 12:07). By 12:55 its intent file was 48 min stale with no CLOSING — which *looked* abandoned, but **the principal confirmed that terminal is still open (just idle)**, so it is NOT abandoned and gets **no** ABANDONED synthesis. The lesson: a stale intent file is noise, not proof of death (the respawn ritual says exactly this). That session had, before going idle:
- added a new **§Q** (Opus 4.8 deterministic-workflows capability survey) to `plan.md`, **uncommitted**;
- claimed **S119** in the §Q prose (the "what's new in 4.8" consultation, sid 86344868) — but **never created an S119 quest file**.

It also declared "discussion only, no file targets" in its OPEN, yet had in fact edited `plan.md` and claimed an SNNN — a reminder that a sibling's declared OPEN scope can drift from what it actually wrote; check disk/git, not just the OPEN.

Resolution (surfaced to the principal, per the respawn ritual — did not synthesize unilaterally): I took **S120** (leaving the §Q `[[S119]]` reference intact so it doesn't mis-resolve to my quest), and added §P.8 via a targeted Edit that does not touch §Q. The §Q is real parked work owned by the still-open sibling; **principal confirmed I should carry it in this commit** rather than leave it uncommitted (it may keep editing §Q on its end — that will show as a later diff).

## Open / not done

- `meta/write-rules.md` "enforced by hook" godly proposal — next `Hey Guthix, bankstand`.
- Optional: a gielinor `lorebook/drafts/` D-NNN to anchor the five-lens doctrine the way gielinor's [[D-025_offer-multiple-choice-with-recommendation|D-025]]/[[D-027_plain-text-deliverables-for-terminal-copy|D-027]] anchor theirs (separate principal-gated write; not done) — the *gielinor* lorebook decisions (multiple-choice + plain-text-deliverables), cross-vault and dangling per §O.5, NOT the dev brain's same-numbered decisions (which is exactly what the born-link hook first wrongly auto-wrapped a bare token to — hence the full bracketed stems here).
- §Q's two empirical unknowns (billing, hook-firing inside workflows) remain `[ ]` — the still-open sibling's parked work, not this session's.
- `braindead-86344868` is still open (principal-confirmed) — no ABANDONED synthesis needed; it owns §Q / S119 and may continue on its end.

**Cascade.** `developer-braindead/`: [[S120_885d6702_khaan-item-4-five-lens-doctrine|S120]] quest-log (this file); `bank/plan.md` §P.8 `[x]` (+ carried the still-open sibling's uncommitted §Q); `respawn.md` Last-updated prepend; `bank/build-lessons.md` (sibling-OPEN-scope-drift lesson); `comms/active.md` OPEN + CLOSING.
**Main-brain changes.** `gielinor/meta/communication-protocol.md` — added "The five-lens read" doctrine subsection (item 4; principal-authorized `meta/` edit per [[D-017_user-only-with-explicit-permission|D-017]]).
