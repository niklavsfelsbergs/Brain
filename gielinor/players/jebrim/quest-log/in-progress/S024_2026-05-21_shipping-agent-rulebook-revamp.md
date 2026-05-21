# S024 — Shipping-agent rulebook revamp

**Opened:** 2026-05-21 (retroactively — see Discipline note below)
**Player:** Jebrim
**Trigger:** Principal flagged a real overkill in the shipping-agent: a simple "show me a chart" request had produced a full Next.js bundle (request folder + `index.html` + `bundle.json` + `spec.json` + viewer link) where an inline chart in chat would have sufficed. Asked Jebrim to rework how the HTML/Next.js paths get proposed — inline by default, bundles as confirmed escalations.

## Scope

Mutate the shipping-agent's `how_to.md` to:

1. Replace the three-mode visualization model (chat / HTML bundle / Next.js) with a four-mode model where **Mode 2 = inline HTML** is the new visual default and bundles are confirm-before-build escalations.
2. Add a minimal Python builder for the inline-mode artifact.
3. Tighten §10 scope enforcement after a couple of real overreach incidents (`ls` permission prompts; attempted read into `NFE/.claude/reference/`).
4. Add cross-cutting rules that came out of real friction: acknowledge briefly, don't over-research canonical questions, default visual breakdowns are an offer not a default.
5. Translation table: Picturator → "B2C", PicaAPI → "MerchOne" (per Niklavs' definition mid-session).

All edits land in `Documents/GitHub/bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/`.

## Turn log

### T1 — framing + design proposal (2026-05-21)

Principal showed the overkill screenshot. Diagnosed: §0 lines 80–84 and §7 wire the HTML-bundle path as the lightest visual escalation; no inline-chart tier exists between chat and bundle. Proposed three concrete changes — §0 rewording, §7 reshape to four modes, §8 carve-out for inline mode. Asked PNG-in-folder vs side-panel HTML.

### T2 — design clarified

Principal chose: single bare `.html` file (title + description + one chart), small enough to write quickly, opens in Claude Code side panel. Revised proposal accordingly — `visualization-studio/content/charts/claude/YYYYMMDD-HHMMSS--<slug>.html`, single-file, no spec/bundle/sql sidecars.

### T3 — implementation

Wrote `build_inline_chart.py` (~140 lines): pandas + plotly, CLI args (`--data --title --description --chart-type bar|line --x --y` + optional `--orientation --color --slug`), CDN-loaded Plotly JS so the output is one self-contained file. Auto-picks horizontal vs vertical bar by category count.

Edited `how_to.md`:
- §0 "Output mode" subsection rewritten: Mode 2 inline HTML is the new default visual; Modes 3/4 are escalations requiring confirmation.
- §7 reshaped from three modes to four. Mode 2 carries no confirmation requirement; Modes 3 and 4 each carry "confirm before building" lines.
- §8 carve-out: "one folder per request" applies to bundle modes only; Mode 2 is flat-file.
- Script reference and app-structure tree updated.

### T4 — scope-discipline incident (ls permission prompt)

Principal screenshotted a permission prompt for `ls C:\Users\...\shipping-agent\`. Root cause: §10 said "Don't run `ls`, etc. against paths *outside this folder*" — the qualifier was the loophole, and the agent reached for `ls` inside the folder. Tightened §10:
- Banned `cat / ls / find / grep / cd` regardless of path; named `Glob/Read/Grep` tools as the right substitutes.
- Added Windows-specific note: no trailing backslash on paths in bash invocations (parses as escaped quote).
- Added `build_inline_chart.py` to the harness allowlist callouts.

### T5 — narration discipline (the "spewing useless stuff" incident)

Principal showed the shipping-agent narrating "I'll check the table reference for date columns and what source_system values represent TCG shops, then run the query." — multi-sentence pre-action plan narration. Added cross-cutting rule #7: "Acknowledge briefly; don't narrate the plan." One acknowledgment line ("On it.", "Pulling that now."), then silent execution.

### T6 — latency discussion

Principal asked about 2-min response time on a chart request. Root causes diagnosed: (a) over-research at the front — reading reference/ for canonical questions whose answer is already in how_to; (b) re-pulling same-day artifacts that already exist with matching scoping. Added:
- Cross-cutting rule #8: "Don't over-research canonical questions" — how_to is enough for top-N / monthly trends / cost breakdowns; reference/ is for edge cases.
- §7 Mode 2 step 1: check `visualization-studio/content/charts/claude/` for a same-day reusable artifact with matching scoping before re-querying.

### T7 — acknowledgment refinement

Principal pointed out that "On it." is *too* sparse — followed by silent tool calls, it reads as a freeze. Refined rule #7: opening line must restate the scoping plus the action verb. "Top 10 countries by volume, TCG shops, 2025 — pulling now." Compresses Understanding/Plan into one line. Generic "On it." is now sub-target.

### T8 — out-of-perimeter read attempt

Principal showed a permission prompt for `NFE/.claude/reference/shipping-data-mart/overview.md` — agent reaching for a "reference" folder *outside* the shipping-agent. Diagnosed: existing settings.json deny rules use `../**` (relative) patterns which don't match absolute paths; Claude Code's working-dir boundary caught it, but the *behavioral* rule in §10 didn't stop the reach. Tightened §10 with two new lines:
- "Any path that starts with `C:\`, `/c/`, or `..\` is outside this folder by definition."
- "'Reference' means the in-folder `reference/`" — explicit list of the three reference files, ban on reaching for `.claude/reference/`, `NFE/.claude/reference/`, `bi-etl/reference/`, etc.

### T9 — real-world test pass

Principal shared a shipping-agent session transcript: "how much to ship a 20×30 canvas to Germany?" → clean one-line scoping ack ("Pulling avg shipping cost for 20×30 canvas to Germany — TCG production lines, last 12 months."), then silent tool calls, then €2–3 median answer with assumptions in parens. Follow-up: "show cost trends by canvas count" → built `20260521-205041--canvas-20x30-bundle-cost.html` (flat folder, single file, Mode 2 working as designed). Answer included the business insight: marginal shipping cost of a second canvas is 2 cents, strongly supporting a "buy 2" promo. Audit verdict: rules landed cleanly. Two minor nits — Picturator/PicaAPI internal names exposed in parens; turn 1 slightly long due to auto-breakout by sub-platform.

### T10 — naming swap + nit fixes

Principal defined Picturator = B2C, PicaApi = MerchOne. Asked Jebrim to swap and apply the called-out nits. Edits:
- §0 translation table: Picturator → "B2C", PicaAPI → "MerchOne".
- §2 source-systems table rows updated to match.
- `reference/sources.md` section headers updated.
- Rule #3 tightened: "Breakdowns are an offer, not a default" — "how much" questions get one number + assumptions, sub-platform splits surface as a follow-up offer.
- Stale "Six cross-cutting rules" lead-in now reads "Nine cross-cutting rules" after the two adds.

### T11 — quest-log discipline gap surfaced

Principal asked about open quests. Surfaced seven in-progress entries; called out that this session itself had no quest-log entry — substantive work happened in shipping-agent (additional working dir), nothing wrote to gielinor, the lapse was invisible to disk. Principal cued session close with retroactive log + handover note that shipping-agent iterations are still ongoing.

## Decisions

- **Inline HTML as the new visual default** — confirmed with principal in T2. Bundle modes shift to "ask before building."
- **Translation table replaces long phrases with single business names** — `B2C` / `MerchOne` instead of "our main EU shop platform" / "our newer customer-facing platform." Shorter, more aligned with how Niklavs actually refers to them.
- **Behavioral fix > settings.json deny tightening** for out-of-perimeter reads — settings.json deny rules use relative-path patterns and can't catch absolute paths without also denying the working dir. The behavioral rule in §10 is the load-bearing fix; deny patterns are backstop only.
- **Did not backfill old generated artifacts** (`visualization-studio/content/generated/claude/20260521-120000--tcg-2025-shipments-by-country/`) that still carry the pre-swap "main EU shop platform" phrasing. Those are historical bundles; not worth touching.

## Discipline note — quest-log open lapse

The whole session ran without an in-brain quest-log entry. Per `gielinor/meta/death-and-spawn.md`, every turn should append to `quest-log/in-progress/` of the active player. The lapse:

- Session opened with `hey jebrim` at message start (T0). Jebrim activated cleanly per the address rule.
- All substantive work landed in the **additional working directory** (`shipping-agent`), not in `gielinor/`. No edits to gielinor → no on-disk evidence that a Jebrim session was active.
- The lapse was invisible until T11 when principal asked.

This entry is the retroactive open. The turn log above is reconstructed from in-context recall (no transcript), so it captures shape and decisions but not every micro-action. The harvest below records the lesson.

## Pending drafts

None at close.
