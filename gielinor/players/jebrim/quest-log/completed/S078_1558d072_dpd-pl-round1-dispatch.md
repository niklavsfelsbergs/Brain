# S078 — DPD PL Round 1 dispatch (EU Tender 2026)

**Session:** 1558d072 · **Player:** Jebrim · **Opened:** 2026-05-26
**Quest:** Build the DPD Poland Round 1 carrier dispatch from the contract-engine review's full question list.

## Where we are

Built the curated dispatch from scratch and overwrote the stale Phase 1 pack at
`bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/DPD PL/questions_for_carrier.md`.

- Source: `2_analysis/docs/open_questions/dpd_pl.md` — 17 carrier-facing Qs.
- User picked 14 (dropped review #13 suspended-dest, #14 liability cap, #17 contract-dates — all correct cuts).
- Of the 14, four sub-EUR-25k additional-services items (#7 non-sortable / #8 non-standard / #9 POD / #10 weighing) bundled into a single LOW line (Q11) per user decision.
- **Net dispatch: 11 carrier-facing questions** (8 HIGH / 2 MED / 1 LOW), each with Why + Plan-on-response, status checklist, dropped-table with rationale, cross-links.

## Turn log

- **T1** — Respawn; read keepsake + EU tender bank notes + [[S034_2026-05-22_eu-tender-logic-review|S034]] update. Surfaced where-we-are: review doc done, Keep/Drop/Reframe walkthrough never run, B1 zone fee (EUR 3.04M, 47%) the hanging decision. Flagged DPD PL = quantitatively retire-only but the verdict rides on the pessimistic Blocks.
- **T2** — Showed the two-file structure via Hermes (review doc 15 Qs → dispatch 10, 5 dropped).
- **T3** — User gave 14 picks, asked which are low-impact. Recommended bundling #7–10 (<EUR 60k aggregate, ~0 likely). User chose "bundle into one line."
- **T4** — Wrote the dispatch file (full annotated version, 11 Qs).
- **T5** — Principal: "I need just the questions to send out, like FedEx." Gave the 11 as a plain send-ready numbered list in chat.
- **T6** — Principal: "put them at the top of the dpd pl file so i can normally copy them." Added a `## SEND-READY (copy block)` of the 11 plain questions at the top of `questions_for_carrier.md`, annotated version retained below the divider.
- **T7** — Close-session (this turn). SNNN S078 (dcf97c7a took S077 today). Harvested 1 examine draft + 1 memory. No pending external actions. bi-analytics dispatch file left uncommitted (shared-index hazard).

## Open / next

- **#15 left blank in the user's picks** — confirm whether they meant to add a 15th or it was just end-of-list.
- **Cascade not yet done** (Step 8 of the playbook). Pending user sign-off on the dispatch, then:
  - `OPEN_QUESTIONS.md` — add a `## DPD PL` section + refresh cross-carrier ZAZ (DPD PL = 7th CH treatment).
  - `PLAN.md` — §A DPD PL row + new §B entry for `dpd_pl-2.0.0` rebuild + §B.5 status block + dependency footer.
  - `DECISIONS.md` — 2026-05-26 entry on Round 1 curation + the four bundled/dropped items.
  - `ASSUMPTIONS.md` — Round 1 dispatch tags + locked-ASSUMPTION block for dropped items.
- After dispatch + cascade lands: all 9 dispatchable carriers in reply-waiting; contract-engine review queue empty (UPS still pending offer).

## Note

Per project playbook the agent normally does NOT author `questions_for_carrier.md` — user explicitly instructed "create from scratch," which overrides that default. Old Phase 1 pack preserved in git history.
