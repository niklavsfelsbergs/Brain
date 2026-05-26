# Investigate-before-specialize

When the principal cues "should we build a specialist for topic Y?" (dedicated agent, new skill, persistent scaffold), resist the immediate yes. The failure mode of the existing chain is information the specialist can't replace — it tells you *what* to specialize for. Build the specialist first and you lose that signal forever.

## Pattern

1. Resist the yes. Surface: "what's the existing chain to Y today?"
2. Trace from a realistic landing point — read CLAUDE.md / routing / entry points at each hop.
3. Name the gap explicitly, not "it's complicated."
4. Run the test the specialist would replace, at the realistic altitude, without pre-framing or hand-feeding.
5. Decide:
   - Test passed → no specialist; one-line pointer may suffice.
   - Test failed at hop N → patch hop N. Specialist only if patching is insufficient.
   - Test exposed an *expertise* problem (agent finds docs but can't use them) → that's the specialist case. Discoverability ≠ expertise.

## When to skip the investigation

If the existing chain is obviously absent (no scaffolding for Y at all), investigation only confirms what's known. Skill applies when scaffolding *might* exist worth measuring.

## Source

[[S015_2026-05-21_ttyd-review-and-dry-run|S015]] (2026-05-21). Principal proposed a shipping-data-mart specialist. `bi-analytics-main/CLAUDE.md` had no shipping-mart mention; `NFE/CLAUDE.md` pointed only at the lighter reference, never at TTYD. Discoverability gap a specialist would have masked. Fix: one-callout edit + keepsake pin. Specialist deferred until the dogfood run produces evidence.

## Related

- `meta/layer-routing.md` — methodology vs domain knowledge distinction.
