# EU Tender 2026 — S034 update (delta to existing bank note)

**Source:** S034 audit + remediation session, 2026-05-22.
**Status:** delta to `bank/notes/projects/eu_tender_2026.md` (last touched 2026-05-20).

## What changed since 2026-05-20

**Scorer wired to 9 engines** (was 6). FedEx + DPD PL no longer invisible. 90 decision sets up from 35. F6.

**New cap6 top-5 portfolios (mandatory saving):**

1. `add_hermes` — EUR 397k
2. **`renew_maersk_plus_fedex`** — EUR 377k — **didn't exist in prior scorer**; FedEx as single-entrant add over Maersk renewal is the surprise of the audit
3. `renew_maersk_plus_hermes` — EUR 370k
4. `all_renewals_plus_fedex` — EUR 340k (new)
5. `all_renewals_plus_hermes` — EUR 340k

Greedy 1→9: `hermes → fedex` hits EUR 739k at 99.84% coverage in 2 picks.

## DPD PL — retire-only confirmed by numbers

- F4 bias ratio: **DPD PL full-eligibility 2.957×** (engine prices ~3× current invoice on Picanova mix).
- F6: `renew_dpd_pl` standalone = **−EUR 416k mandatory**.
- The 2026-05-20 reframing of DPD PL as "normal candidate" stays at the framing layer; quantitatively the new offer is a retire-target, not a renew-target. Updated DECISIONS treatment still appropriate (3-state space wired by F6) — the scorer just confirms what the bias number predicts.
- FedEx joins GLS as second unlock for DPD PL retirement: `renew_maersk_drop_dpd_pl_plus_fedex` = EUR 297k (5-active).

## FedEx — the surprise lever

- Full-eligibility bias 1.732× (mid-pack); tail bidder on most lanes but selectively cheap.
- 99.4% coverage; engine heavily provisional (fuel/customs/residential/vol-weight all 0 pending Round 1 reply).
- Even at provisional pricing, `renew_maersk_plus_fedex` ranks #2 — meaning FedEx is meaningfully cheap on a subset of Maersk-renewal residual volume.
- Once Round 1 (sent 2026-05-21) lands, expect FedEx engine to **rise** (fuel + customs + residential all under-priced today). The #2 position is likely a ceiling; could drop several places. Re-score required.

## Methodological finding — doc/code drift

PLAN.md / DECISIONS.md / ASSUMPTIONS.md treated as-if-shipped multiple workstreams that hadn't actually landed in engine code:

- Austrian Post 2026-05-18 entries (CH customs 1.00 EUR / multi-service expansion / line-haul) — engine still `austrian_post-1.0.0`, none of it in code.
- Maersk 2026-05-18 entries (fuel 5% snapshot / AT-DE-DK tolls) — engine still on fuel 10% / no toll modules.

The cascade discipline broke at the "carrier reply → DECISIONS+ASSUMPTIONS landing" step — entries were written as if shipped rather than as deferred targets. F7 rolled them back with additive status headers. Pattern worth flagging in future tender-style work: **DECISIONS entries should match engine state, not target state; target state lives in PLAN.**

## Latent vs active bugs

F2 found the `eligible` gate "fix" was latent — all current always-on surcharges already self-gated via `pl.col("base_rate_eur").is_not_null()`. Totals identical pre/post within float epsilon. The fix shipped anyway as defensive coverage but the headline didn't move. **Distinguishing latent vs active bugs at audit time would have downgraded F2's severity from high to medium.**

## Refresh-when

Re-promote after the next bankstanding or alching pass over Jebrim's project notes. Magnitude shift on cap6 portfolios + DPD PL retire-only + doc-drift methodology are the durable bits to fold into the canonical bank note.

## Related

- Existing `bank/notes/projects/eu_tender_2026.md` (2026-05-20 state)
- `quest-log/completed/S034_d1*..d7*.md` (audit)
- `quest-log/completed/S034_f1*..f8*.md` (fixes)
- `inventory/eu-tender-logic-review-resume.md` (open follow-ups)
