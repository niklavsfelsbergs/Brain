# Scope creep during plan execution — silent vs surface

**Drafted:** 2026-05-22 (S030, shipping-agent personal-folders implementation).

## The observation

The design plan for the shipping-agent personal-folders quest listed 9 concrete steps. While executing, T7 (the verification step) surfaced three categories of work the plan didn't enumerate but the implementation required to be coherent:

1. **AI pointer shims** (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `GROK.md`) — each had a one-paragraph reference to the deleted `visualization-studio/` paths. Doc-sync, not behavior change.
2. **README.md** — four references to `visualization-studio/` paths in the human-onboarding doc. Doc-sync.
3. **Harness scripts** — `build_inline_chart.py`, `build_light_html_presentation.py`, `create_timestamped_presentation.py` had hardcoded `visualization-studio/content/charts/claude/` etc. paths, and the new §7 Mode 2 docs *promised* an `--out` flag that didn't exist. Behavior change — needed `--out` argparse flag + default `scratchpad/` resolution.

Categories 1 and 2 got fixed silently as part of step 7 ("verify integration"). Category 3 was surfaced via `AskUserQuestion` with three options before any code touched the scripts.

## The rule

**Silent on doc-sync that the plan implicitly required.** When deleted/renamed structures are referenced from docs, those references are *consequences* of the original change, not new decisions. The plan said "drop all visualization-studio references" — every doc with such a reference is in scope by extension. Acting silently keeps the principal from drowning in confirmations they'd say "yes obviously" to.

**Surface on behavior/code change beyond the plan's enumerated steps.** When the implementation reveals that a *working system requires more than the plan listed* (a script needs a new flag, a config needs a new key, a hook needs a new check), that's a scope question — the principal owns scope decisions. Surface once with options; don't expand silently.

## How to apply

Mid-implementation, when about to make an edit, ask: "Is this a consequence of an enumerated step (doc-sync to a removed path, allow-list a structurally-required file), or is this new behavior?" If consequence → act, log in the turn-log. If new behavior → surface with options before touching.

The escape valve: if it's ambiguous, default to surface. Wrong surface costs one turn; wrong silent expansion costs cleanup later.

## Evidence

- T7 silent doc-sync (AI shims + README): zero principal friction, all four files updated in parallel `Edit` calls.
- T7 harness-script question: principal chose option A ("add `--out` to all three") in one click. Total cost: one `AskUserQuestion` block. Cost if done silently: would have shipped a working system but principal wouldn't have known the scripts changed.

## Adjacent skills

- [[investigate-before-specialize]] — sibling pattern about when to broaden vs narrow inside an action.
- [[moving-target-decomposition]] — sibling pattern for breaking moving targets into steps. The scope-creep rule applies *inside* the execution of any such decomposition.

## Open question

Threshold for "behavior change" is judgment-call. Adding `--out` to argparse is clearly behavior; updating a default value is borderline; reordering function arguments is murky. Re-examine after second occurrence.
