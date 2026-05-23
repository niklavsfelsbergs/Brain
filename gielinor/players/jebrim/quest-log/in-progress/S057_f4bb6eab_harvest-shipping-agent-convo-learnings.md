# S057 — Harvest learnings from shipping-agent quota-reduction conversation

**Session:** jebrim-f4bb6eab · 2026-05-23
**Shape:** learning-harvest (not investigation). Principal pasted a shipping-agent conversation and cued: "pick learnings from that."

## What the conversation was

A shipping-agent (out-of-tree) session: "find a way to drop the shipping cost quota 20% → 15%." Agent built a baseline + decomposition, a 11-move lever menu, then a presentation. The principal pushed twice — "where are the actual suggestions" (sizing vs moves) and then the decisive catch: **"are you taking package dimensions into consideration for [UPS-DE → DHL Paket]? DHL only takes up to 60×60×120."** Agent re-pulled: the €460K/6mo "high-confidence, already-audited" lever was 70 of 124,777 parcels eligible (0.06%) — TCG ships canvas (~98×71×5 cm) that busts the envelope. Effectively €0, and the blind spot infected the whole lever menu.

## Learnings picked + routed (all drafts — pending alching)

1. **Bank** `bank/drafts/notes/projects/2026-05-23-package-dimensions-carrier-envelopes.md` — carrier dimensional envelopes (DHL Paket 60×60×120 / 31.5 kg) × TCG's canvas-shaped parcels; `shippingprovider_extkey` carries DHL product tier. *Re-verify dim column names against gold flagged.*
2. **Skill** `spellbook/drafts/skills/dimension-gate-carrier-swap-savings.md` — gate candidate volume on the destination carrier's dimensional envelope before sizing any swap; report before/after-dim-filter columns; ineligible remainder changes shape, not dead.
3. **Examine** `examine/drafts/2026-05-23-inherited-confidence-not-own-confidence.md` — don't inherit an upstream investigation's confidence rating without checking what it gated on.
4. **Examine** `examine/drafts/2026-05-23-money-figures-state-their-period.md` — every money figure states its period; the €4.4M/6mo mislabelled "/year" (real €8.4M/yr) slip.

## T2 — principal pushed: "did we teach the agent?" + "is that all?"

Two corrections from the principal, both right:

1. **Capturing ≠ teaching the agent.** T1 wrote brain drafts (Jebrim's memory). The shipping-agent's `how_to.md` — the file it actually reads at runtime — was untouched, so the agent would repeat the blind spot. Teaching the agent = editing `how_to.md`.
2. **Under-harvested.** Dimension-gating wasn't the only lesson. Re-read surfaced 4 more, including the principal's *first* pushback in the convo which T1 missed entirely.

### Full teachable set (5)

| # | Rule | Brain | Agent how_to.md |
|---|---|---|---|
| 1 | Dimension-gate carrier-swaps before sizing | skill + bank (T1) | rule 30 |
| 2 | Lead with moves, not sizing ("where are the actual suggestions") | skill (T2 — was missed) | rule 31 |
| 3 | Net out lever overlap before headlining a stacked total | skill (T2 — was missed) | rule 32 |
| 4 | Every money figure states its period (€4.4M/6mo → €8.4M/yr) | examine (T1) | rule 33 |
| 5 | Don't inherit an upstream finding's confidence | examine (T1) | rule 34 |

### Landed in T2

- **Brain:** new skill `spellbook/drafts/skills/savings-investigation-deliverable-shape.md` (covers #2 + #3). Brain total now 5 drafts: 1 bank, 2 skills, 2 examine.
- **Agent (out-of-tree `shipping-agent/how_to.md`):** new §0 subsection "Cross-cutting rules — investigation & savings work (30–34)" with all five rules; §0 intro count updated 29→34. No renumber of existing rules (new rules are investigation-only, given their own labeled block). Edits made, **not committed** (awaiting principal sign-off; the repo also denies push by config).

## Open / follow-ups

- **how_to.md rulebook update (out-of-tree, needs principal nod):** the dimension-gating rule should land in `shipping-agent/how_to.md §0` so the agent itself never repeats the blind spot. Not done — separate repo write.
- **Recurring intent flagged by principal:** "it's time to take the convos I'm having with the agent and pick learnings." This was one. Pattern may warrant a repeatable harvest skill if it recurs.
- **Not harvested (point-in-time, lives in the investigation):** the 19.2% baseline / ~4pp drift / lever €-sizings — they go stale; they belong in the workbench investigation, not the bank.
