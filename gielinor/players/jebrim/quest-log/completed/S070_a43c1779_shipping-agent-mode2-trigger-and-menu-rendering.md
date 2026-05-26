# S070 — Shipping-agent: Mode 2 trigger sharpening + interactive-menu rendering

**Opened/closed:** 2026-05-25 (single session)
**Player:** Jebrim
**Working dir:** `Documents/GitHub/shipping-agent/` (additional working dir — maintainer work; this entry is the on-disk evidence per the [[S024_2026-05-21_shipping-agent-rulebook-revamp|S024]] lapse lesson)
**Trigger:** Principal observed the shipping-agent *sometimes* opens with clarifying selection menus (scope + what-metric) and sometimes doesn't — asked why, then asked to make the good behavior fire more reliably and render as a clickable menu.

## What it was

A real-prompt diagnosis + two-part rulebook fix in `how_to.md`. Started as a portability question (does the agent work on other AIs — yes, four shims `CLAUDE/AGENTS/GEMINI/GROK.md` → one `how_to.md`; only §10 tool-names + `.claude/settings.json` are Claude-shaped), pivoted into the menu-behavior fix.

## Diagnosis

Two separate inconsistencies, kept apart:

1. **Whether it decomposes at all (Mode 2 firing).** Mode 2's trigger examples were all *obviously* fuzzy ("how are we doing?"). The principal's prompt — *"outlier shipping charges in april/may which I should be aware of"* — was *covertly* fuzzy: undefined metric ("outlier") + discovery frame ("which I should be aware of"), but looked answerable, so it read as borderline-Mode-1 and coin-flipped. This is the documented "full rigor present, doesn't self-trigger on the fast path" root ([[S059_9369b3f2_shipping-agent-limit-testing|S059]]→[[S067_6ccc2220_shipping-agent-bucket-first-harvest|S067]]), here at mode-selection.
2. **How it presents the decomposition (menu vs prose).** The interactive menu is the harness question tool (`AskUserQuestion` in Claude Code). `how_to.md` said "surface readings in plain English / numbered selection" — content, not mechanism — so the model rendered prose sometimes, menu other times.

## Edits to `how_to.md` (§0)

- **Mode 2 trigger** — added two named covert-fuzzy cases (undefined metric; discovery framing) that force Mode 2 over Mode 1, with a **guardrail** ("named metric with confident default stays Mode 1; fires only when picking the definition/axis silently would be a guess — not because an answer *could* be sliced further, that's rule 3's offer").
- **Mode 2 rendering** — present picks via the interactive selection menu (`AskUserQuestion`, auto-"Other"); fall back to numbered prose only if the harness lacks the capability (portability guard for non-Claude harnesses).
- **Rule 12** — one-line pointer so scope picks render the same way.

## Verification (live, principal-driven — the only test that counts here)

- Probe `for TCG, which shipping charges in april/may stand out?` → fired Mode 2 on "stand out", surfaced 3 correct axes (per-parcel jumps / surcharge-mix shifts / individual large charges), scope menu correctly suppressed (TCG named), no rule leak, didn't echo "outlier". **Trigger pass.**
- After the rendering edit, same probe → rendered as the **clickable menu**. **Rendering pass** (principal: "works").
- Control (`cost per parcel for TCG in April` must just answer) was offered but principal stopped at "works" — guardrail not adversarially confirmed this session; low risk but flagged below.

## Decisions

- **Lean toward asking in the fuzzy zone, guardrail is load-bearing.** The trigger sharpening cuts against rules 7/8 (answer-first, don't over-research) which exist because the agent was once too chatty — the guardrail clause is what prevents regression. Shipped *with* it, never without.
- **Interactive menu over prose for picks**, harness-guarded for portability.
- Diagnosis isolated the fix to the **what-metric** menu; rule 12 scope menu already fired correctly, left mechanically unchanged beyond the rendering pointer.

## Watch / open

- **Guardrail not adversarially tested** — the control prompt (well-defined ask must NOT throw a menu) wasn't run. If real use shows over-firing (menus on confident-default asks), tighten the guardrail or promote it to a standalone cross-cutting rule.
- Cross-repo skill-sync caveat unchanged — this edit is `how_to.md`-only; no `gielinor/spellbook` twin to keep in sync.

## Commits — HELD (push at the end after all changes, post-demo)

Principal ruling: *"we will push in the end after all changes."* The shipping-agent demo is **2026-05-26** and two sibling sessions (006248ef demo-read, 363fdec7 DPD-harvest) deliberately froze `how_to.md` until after it. Nothing committed this session.

- `shipping-agent` — how_to.md, 3 edits **applied, uncommitted in working tree** (Mode 2 trigger + Mode 2 rendering + rule 12 pointer). Push batched post-demo with the other pending how_to.md work (363fdec7's held dimension-scan rule).
- `brain` — this quest-log entry + quality-assessment harvest **written, uncommitted**. Batched into the same end push.

**Discipline gap (noted, not excused):** no OPEN posted to `comms/active.md` at session start — siblings didn't know I was in `how_to.md`. Closed with a CLOSING entry recording the uncommitted edits so 363fdec7's post-demo rule-landing accounts for them.

## Related

- [[shipping-agent-quality-assessment-2026-05-24]] — harvested there (the "doesn't self-trigger on the fast path" root; this is a fix at the mode-selection layer).
- [[stress-testing-an-agent-by-embodying-it]] — methodology.
