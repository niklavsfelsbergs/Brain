# S024 resume — shipping-agent rulebook revamp

**Status:** in-progress. **Iterations on the shipping-agent are still ongoing** — this session shipped a Phase 1 batch of rule changes but more friction will surface as real shipping-agent sessions run against the new wording.

## Where we are

Phase 1 of the shipping-agent rulebook revamp landed clean:

- **Mode 2 (inline HTML) is the new default visual.** `build_inline_chart.py` writes a single bare HTML file (title + description + chart) to `visualization-studio/content/charts/claude/YYYYMMDD-HHMMSS--<slug>.html`. Bundle and Next.js modes are now confirm-before-build escalations.
- **§10 scope tightened.** Bans `cat/ls/find/grep/cd` regardless of path; bans the "reach for parent project's reference folder" pattern explicitly; calls out the Windows trailing-backslash parse trap.
- **Three new cross-cutting rules** in §0 (total nine): rule #3 strengthened ("breakdowns are an offer, not a default"); rule #7 ("opening line restates the scoping; then silent"); rule #8 ("don't over-research canonical questions").
- **Translation table swap.** Picturator → "B2C"; PicaAPI → "MerchOne". `reference/sources.md` section headers and §2 source-systems table updated to match.

Real-world test pass came back clean in T9 — a "how much to ship a 20×30 canvas to Germany" + follow-up bundle-economics chart ran end-to-end with the new rules visibly working (one-line scoping ack, silent tool calls, Mode 2 single-file artifact, business-insight answer).

## Next concrete step

Watch for residual friction in the next few shipping-agent sessions. Specifically the regressions worth scanning for:

- **Pre-action narration creeping back.** Rule #7 says one scoping-restating line; check that the agent doesn't drift into "I'll do A, then B, then C" multi-sentence plans.
- **Auto-breakout by sub-platform.** Rule #3 says breakdowns are an offer, not a default. If the agent splits "how much" answers by B2C / MerchOne / source without the user asking, rule #3 isn't biting hard enough.
- **Latency creep.** Rule #8 (don't over-research) and Mode 2 step 1 (check for same-day reusable charts) target a 30–60s saving on canonical asks. Time the first few "show me a chart" turns; if they're still 90s+, something's not landing.
- **Scope-perimeter reaches.** §10 was tightened twice this session. If a third out-of-perimeter incident shows up, the behavioral rule is insufficient and the next move is rewriting `settings.json` deny patterns to handle absolute paths without denying the working dir.

When new friction surfaces, the move is the same as this session: principal flags via screenshot, Jebrim diagnoses the root cause in the rulebook, proposes targeted wording, edits.

## Files / paths to read first

- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — §0 (cross-cutting rules + translation table), §7 (four modes), §8 (artifact carve-out), §10 (scope).
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/build_inline_chart.py` — the new Mode 2 builder.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/.claude/settings.json` — current deny patterns (relative-path `../**` only; absolute-path absent — would need rewriting if §10 behavioral rule doesn't hold).
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/sources.md` — section headers carry the new B2C / MerchOne naming.

## Pending drafts

None pending; one observation about quest-log open discipline written to `examine/drafts/` this session — see step 7 of close.
