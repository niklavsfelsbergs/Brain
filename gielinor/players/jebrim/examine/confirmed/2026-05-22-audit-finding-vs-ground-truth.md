# Audit findings are hypotheses, not ground truth

**Date observed:** 2026-05-22 ([[S034_2026-05-22_eu-tender-logic-review|S034]] — EU tender logic review)
**Anchor:** [[S034_2026-05-22_eu-tender-logic-review|S034]] D1 (Maersk audit dwarf) vs [[S034_2026-05-22_eu-tender-logic-review|S034]] F1 (Maersk fix dwarf) on the IT/ES oversize trigger.

## The observation

In [[S034_2026-05-22_eu-tender-logic-review|S034]] I spawned 7 audit dwarves (D1-D7) in parallel to find calc bugs + wrong/missing assumptions across the EU tender Phase 2 codebase. D1 reported (high severity) that the Maersk IT oversize encoding was wrong — `max_height=170` from "Height 170-240 cm" was compared against `d_min` (unreachable), making the height check vestigial.

I propagated that framing into my synthesis to the principal as if it were established.

Then F1 (fix dwarf for the same area) actually wrote the patch. F1's verdict: **the trigger encoding was correct.** Engine convention treats the "Max" column as the surcharge trigger band, not a hard cap — consistent with AT (175→23.20 EUR), BG (175→12.77 EUR), DE (120→21.00 EUR). The bug was purely the null `oversize_surcharge_eur` value on IT/ES/BE/LU rows, not the trigger semantic.

The recovered magnitude — +EUR 37,543 Q1 across 3,400 parcels — was real. But D1's root-cause claim was wrong, and I had passed it on without checking.

## What this means for me

**Audit-only dwarves can be confidently wrong** about root causes when they read code without exercising it. The patterns they spot are real (null surcharge values were missing); the root-cause attribution they assign may not match how the engine actually interprets them.

The fix-dwarf cycle catches this because writing the patch forces reading the offer text AND the engine convention together. The audit-only cycle doesn't have that forcing function.

## How to apply

When relaying audit-dwarf findings to the principal:

1. **Distinguish "symptom observed" from "root cause inferred"** in the synthesis. The symptom (IT rejects as `oversize_no_surcharge` instead of pricing) is the durable fact; the root cause (trigger semantic vs surcharge value) is a hypothesis.
2. **For high-severity findings, hold the root cause as provisional** until either (a) I personally read the relevant code+offer together, or (b) a fix dwarf has verified the diagnosis by acting on it.
3. **Multi-dwarf parallel audits are still the right pattern for breadth.** This isn't a critique of D1's value — D1 found the right area; D1 just got the framing wrong. The parallelism was correct; the verification step was missing.
4. **When the audit-then-fix loop fires in the same session (as in [[S034_2026-05-22_eu-tender-logic-review|S034]]), trust the fix dwarf's framing over the audit dwarf's** when they disagree. The fix dwarf had to actually solve the problem.

## Why this matters

Jebrim's authority is repo-grounded — Niklavs reads my conclusions and acts on them. If I confidently relay a root cause that doesn't survive the fix step, I burn that authority. The cost of "audit found symptom X; root cause provisional pending verification" is cheap; the cost of "audit found root cause Y" turning out wrong is expensive.

This is also a calibration finding: when N dwarves run independent audits in parallel, the prior on any individual root-cause claim should be lower than the prior on any individual symptom claim, because root-cause reasoning is the part of the audit that didn't get cross-checked.
