# Bank notes need a prominent "as of" date stamp

## Before / after

**Before (S029 alching, Bank Draft 1):** the dashboard-convergence note had *"Drafted 2026-05-22 (S026)"* as a subtitle line. Functional, but easy to miss when skim-reading. Future sessions reading the note couldn't see at a glance that the convergence directions, cost-basis alignment, and coverage-hole status are a **snapshot from a specific date** — they could rot silently.

**After:** every bank note carries an **`As of:` YYYY-MM-DD** line near the top, formatted bold so the date is unmissable. When the world has clearly moved since (e.g. cutover landed, decisions changed), the line is updated and a short *"superseded by"* / *"check before relying"* note is added.

## The rule

Bank notes are snapshot knowledge. They age. Every `bank/notes/*.md` file (and every draft destined for there) must open with a prominent `**As of:** YYYY-MM-DD` line within the first 5 lines — same shape as `last-verified` in the shipping-agent's `reference/known-dq.md`.

When a future session reads the note and finds the underlying state has shifted, the stamp gets updated (or the note is archived and replaced).

## How to apply

When drafting: include `**As of:** YYYY-MM-DD (SXXX)` at the top, under the title.

When surfacing during alching: if the draft is missing a date stamp, edit-add it before approving.

When reading an existing bank note: the `As of:` is the first thing to check. If it's > 30 days old and the topic is in active flux (e.g., a recent cutover or in-flight decision), don't quote it as canonical — re-verify or flag staleness.

## Anchor

S029 alching, Bank Draft 1. Niklavs: *"give a date stamp so we know that this might be outdated info."*
