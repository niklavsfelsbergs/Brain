# shipping-agent audit (round 2) — resume

**Status:** queued. Birth-session this one (S049, 2026-05-23).

## Where we are

Niklāvs queued a second general audit of `shipping-agent/` at the close of S049, after two more chart bugs surfaced from real use (S045 follow-up: EUR-label collapse + legend-isolation labels) and were fixed in flight. Pattern is *"every time the principal uses the agent in anger, something falls out"* — small but recurring. Time for another structural pass.

The first audit was queued at S032-close (2026-05-22) — its resume file is at `inventory/archive/shipping-agent-audit-resume.md`. Whether that audit ever fully ran or was partially absorbed into subsequent S045 / S049 fixes is unclear from disk; respawn should read both files and judge.

## Location

`Documents/GitHub/shipping-agent/` — its own git repo at `https://github.com/niklavsfelsbergs/shipping-agent`. Latest commit on `main` is the S049 push (`84ad74e` — chart polish: focus flag + EUR precision + legend isolation).

## Next concrete step

Run a general audit of the shipping-agent package. Niklāvs' framing (verbatim):

> *"another audit of shipping agent - whats bloating it, contradictions, overkill, too technical stuff, etc etc"*

The keywords this time are **bloat**, **contradictions**, **overkill**, **too-technical**. Different lens from S032's *"will it perform well, what's friction"* — same package, asking *"what's now in the way of itself."*

## Possible angles

Pick on read — not exhaustive:

- **Document weight.** `how_to.md` has grown across S045 + S049 (chart hygiene block, `--focus` rule, magnitude-aware EUR precision rule, legend-isolation rule). Is it still readable end-to-end on a fresh session, or has the always-loaded surface tipped past its budget?
- **Rule overlap and contradictions.** §0 cross-cutting rules + §7 Mode 2 chart hygiene + §10 scope guardrails — any pairs that say the same thing twice, or say different things and pretend they're the same? Especially after the two recent additions, is the *Direct value labels* bullet now carrying three different cases (single-trace, --focus, legend-isolation) that should split into a small table?
- **Overkill.** Anything documented in painstaking detail that no real call site exercises? Workbench scaffolding, bundle conventions, post-render JS bullets — are they each carrying their weight, or pet-feature drift?
- **Too-technical layer.** The agent's job is *answers about shipping costs* for a non-engineer principal. Are there places where the docs read like engineering specs (post-render JS, dtype-driven overrides, focus-flag mechanics) when a one-line natural rule would do? Same for reference docs — `coverage-audit.md`, `known-dq.md` — useful or noise?
- **Skill / harness coupling.** `harness/build_inline_chart.py` and `harness/build_report.py` now have parallel-but-not-identical multi-series line code (build_report.py still lacks pre-computed text on traces and the legend-isolation JS — flagged as follow-up in S049's resume). Either consolidate into a shared figure-builder or document the gap deliberately.
- **Hallucination surface (carry-over from audit 1).** S032's trigger was the agent freehand-generating stale silver-layer language. Has that recurred? Are the gold-only guardrails in §11 and the schema-discipline rule in `keepsake/current.md` strong enough now, or is the agent still drifting on the source-of-truth question?
- **Per-assistant shims.** `AGENTS.md` / `GEMINI.md` / `GROK.md` (if they still exist) — drift check.

## Files / paths to read first

All paths at `Documents/GitHub/shipping-agent/` unless noted.

1. This file.
2. `inventory/archive/shipping-agent-audit-resume.md` — the S032 audit brief, for comparison.
3. `shipping-agent/CLAUDE.md` — the entry shim.
4. `shipping-agent/how_to.md` — full read.
5. `shipping-agent/harness/build_inline_chart.py` + `harness/build_report.py` + `harness/_report_style.py` — the chart system (S045 + S049 surface).
6. `shipping-agent/skills/` — query patterns + anything else that has accreted.
7. `shipping-agent/reference/` — coverage audit, known DQ, sources.
8. Latest git log on `shipping-agent` main — sense of what's landed since the first audit.
9. (Brain side) `gielinor/players/jebrim/keepsake/current.md` — Shipping Data Mart routing pin, ground-truth pointers.

## Pending drafts

None — this is a hand-over file, not a worked draft.

## Output shape

Audit report should land in `shipping-agent/workbench/audits/2026-05-XX-audit-2/` (matching the S032 audit-1 location if it exists, or create the folder if not). Findings grouped by the four keywords above (bloat / contradictions / overkill / too-technical), each with a recommendation (drop / merge / rewrite / leave). Principal triages the recommendations.
