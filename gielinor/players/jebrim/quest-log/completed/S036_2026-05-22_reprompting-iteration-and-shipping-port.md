# Reprompting skill — iteration + shipping-agent port + load-on-cue hook

**Opened/closed:** 2026-05-22 (S036, single-session continuation of S035).
**Status:** completed.
**Type:** procedural — skill iteration + cross-repo port.
**Deliverables:**
- Patched `gielinor/spellbook/skills/reprompting.md` (single-proposal rule + "more answerable not more articulate" headline + new anti-patterns).
- New `shipping-agent/skills/reprompting.md` (full port in shipping-agent house style, worked DHL/UPS example).
- Updated `shipping-agent/skills/_about.md` (index row).
- New "Skill triggers — load on cue" subsection in `shipping-agent/how_to.md` between rule 16 and the (17–29) header — the load mechanism for any load-on-cue skill, currently one entry for reprompting.

## The brief

Post-S035 live test: a separate shipping-agent session triggered with *"rephrase this - investigate dhl vs ups in germany costs in 2025 vs 2026"* and produced a menu of three natural-language variants + a *"want me to run one of these?"* gate. Two failure modes: menu instead of single proposal, and articulate-not-answerable rewrites. Iteration loop kicked off.

## Turn log

**T1.** Principal showed the failed live response. Diagnosed: menu of variants is the punt, *"run one of these"* gate conflates picking a phrasing with approving execution, all variants stayed at natural-language altitude (none named table / grain / currency / destination filter). Proposed tightening the skill.

**T2.** Patched gielinor skill: (a) Behavior step 2 made explicit ("pick one"), (b) new paragraph on acceptance gate being on the rewrite not on action, (c) new paragraph on what to do when genuinely torn (single disambiguation question, then one rewrite), (d) "What better means" got a headline test (*more answerable, not more articulate*) plus "names the grain" bullet plus "stays at natural-language altitude" failure-mode bullet with the DHL/UPS example baked in, (e) three new anti-patterns up top.

**T3.** Principal said "we fucked up — this was supposed to land in shipping-agent, not gielinor; keep gielinor too." Located shipping-agent at `C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent` (separate repo). Read shipping-agent house style — Audience/Status/Last verified header, plain-English voice, *(Esc to reframe.)* parenthetical.

**T4.** Wrote `shipping-agent/skills/reprompting.md` in shipping-agent's style, adapted "what better means" to shipping-domain examples (cost source, ship-to country, currency, EUR/USD, net vs gross, invoiced vs expected), baked the DHL/UPS exchange in as the worked example with both wrong (menu) and right (one tightened proposal with deferred runtime disambiguation) responses side-by-side. Added index row to `skills/_about.md`.

**T5.** Principal showed a *second* live test that also produced a menu. Diagnosed: the skill exists but never loads because `skills/_about.md` says skills are *"loaded on cue; not always-in-context"* and `how_to.md` is the only always-loaded file. The agent has to be *told* to look at the skill at the moment the trigger phrase shows up — there has to be a load hook in the always-loaded surface.

**T6.** Proposed two fixes: (1) add a trigger hook to `how_to.md`, cheap; (2) inline the skill into `how_to.md`, heavier. Principal chose (1).

**T7.** Added `### Skill triggers — load on cue` subsection to `how_to.md` between rule 16 and the (17–29) header. One bullet for reprompting, lists the trigger phrases, the disambiguation rule, and the load instruction (*"stop, read `skills/reprompting.md` in full, follow its behavior section — one rewrite proposal, no menu, acceptance gate on 'use this?'"*). Designed as an extensible surface — more load-on-cue skills can add bullets here later.

**T8.** Principal tested the trigger inline (*"rewrite this my terminal corrupted"*). Skill fired correctly this turn — single proposal, acceptance gate on *"use this?"*, no menu. Live test passed.

## Decisions

- **Skill load mechanism for shipping-agent is `how_to.md` hooks**, not skill self-loading. Skills are load-on-cue (per `skills/_about.md`); the always-loaded `how_to.md` is where the trigger registry lives. Pattern: each new load-on-cue skill adds one bullet to `### Skill triggers — load on cue`.
- **Same skill, two repos, two voices.** `gielinor/spellbook/skills/reprompting.md` keeps the system-namespace framing (any actor, any session). `shipping-agent/skills/reprompting.md` is in shipping-agent's plain-English voice with shipping-specific examples and refs to the mart's reference files. They're synced in substance, not in prose. Future iterations have to land in both.
- **Live test on a real prompt is the right validation.** Without the second live test (which exposed the load-mechanism gap), we'd have shipped a skill file the agent never read.

## No pending external actions.

## Pending drafts

- `players/jebrim/bank/drafts/notes/shipping-agent-skills-loading.md` — durable knowledge about how shipping-agent's skill loading works (load-on-cue, gated by `how_to.md` triggers).

## Carry-forward flags

- **S031 inventory resume still missing** — same flag as S035. Cleanup belongs to a fresh Jebrim session that opens S031 with the findings in head.
