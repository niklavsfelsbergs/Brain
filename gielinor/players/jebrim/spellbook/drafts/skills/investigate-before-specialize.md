# Investigate-before-specialize

When the principal cues "should we build a specialist for topic Y?" (a dedicated agent, a new skill, a persistent scaffold), *resist the immediate yes*. Map the existing chain first — who currently points to Y, at what altitude, with what fidelity. Then run the test the specialist would replace, at the most realistic altitude. The specialist's case is made (or unmade) by what that test reveals.

## Why

- A specialist built before measurement is design without evidence.
- The failure mode of the existing chain is information the specialist can't replace — it tells you *what* to specialize for. Build the specialist first and you lose that signal forever.
- A wrong specialist costs more than a one-callout fix to existing routing. The cheap fix often wins.
- The existing chain might already work. Building the specialist anyway is dead weight and a maintenance liability.

## Pattern

1. Principal: "should we build X for topic Y?"
2. Resist. Surface the question: "what's the existing chain to Y today?"
3. **Investigate the chain.** Trace from a realistic landing point (usually one level above where the topic lives) — read the CLAUDE.md / routing files / entry points at each hop.
4. **Identify the gap explicitly** — name what's missing, not just "it's complicated."
5. **Run the test the specialist would replace** at the realistic altitude. Don't pre-frame, don't hand-feed.
6. Decide:
   - Test passed → no specialist; maybe a one-line pointer is enough.
   - Test failed at hop N → patch hop N. Specialist only if patching is insufficient.
   - Test exposed an expertise problem (agent finds the docs but can't use them) → that's the case for a specialist. The discoverability/expertise distinction matters.

## When to skip the investigation step

If the existing chain is obviously absent (no scaffolding at all for topic Y), the investigation will confirm what's already known and the specialist case starts strong. Don't perform-investigate for ceremony. The skill applies when there *might* already be scaffolding worth measuring.

## Source observation

S015 (2026-05-21). Principal proposed a dedicated shipping-data-mart agent. Investigation found `bi-analytics-main/CLAUDE.md` had no shipping-mart mention; `NFE/CLAUDE.md` pointed only at the lighter `.claude/reference/shipping-data-mart/` docs, never at TTYD. The discoverability gap that a specialist would have masked. Fix turned out to be a one-callout edit to existing routing + a keepsake pin in the brain. Specialist deferred — when the dogfood runs and reveals what *that* artifact does or doesn't carry, the specialist case (if any) will be evidence-driven.

## Related

- `meta/layer-routing.md` — methodology vs domain knowledge distinction.
- (Eventually) bank/notes/ for the discoverability-gap finding once stable.
