# S106 — "Is the system eating itself?" audit + D8 enforcement-gap fix

**Session:** braindead-cf03bfe1, 2026-05-26. Dev-brain via "Lets develop gielinor" (mid-conversation; OPEN posted at 22:42). SNNN bumped to S106 — 7c91117c claimed S105 (§O.6).

## What was asked

Principal handed an external-review audit prompt (8 dimensions: ceremony-per-component, inward/outward ratio, discipline-leak rate, draft/archive growth, persona delta, two-brain duplication, theming tax, hooks-in-name-only), written by someone who **only read the documentation**, with the standing instruction: look at it critically, including criticizing the prompt's own premises.

## How it ran

3 read-only evidence sub-agents in parallel (file census; inward/outward classification; discipline-leak + persona) + I did the judgment dimensions (two-brain, theming, hooks) + empirical hook testing. Deliverable: `bank/research/2026-05-26-is-the-system-eating-itself-audit.md`.

## Headline findings

- **Reframe that breaks the prompt:** the system is **6 days old** (born 2026-05-20). Every "last 90 days / 60 days / N weeks / 5 random sessions per player" assumes a mature system that doesn't exist. The prompt hunts the failure mode of a *bloated* system; this is a *high-velocity, self-pruning* one.
- **Not eating itself:** drafts decay outpaces accumulation (3 pending drafts brain-wide; folders near-empty from aggressive triage), 8 bankstandings + same-day alching, layers mostly used. The "draft/archive growth without decay" hypothesis (D4) is **false** — nothing to compact.
- **🔴 The real bug (D8):** 4 of 6 "architectural guarantees" (dwarf/gnome/penguin write-boundaries + no-sub-spawn) are **inert from brain root** — the cockpit's launch dir. They gate on `payload.agent_type ∈ {dwarf,gnome,penguin}`; no `dwarf` config exists, and `gnome`/`penguin` live in `gielinor/.claude/agents/` which isn't loadable at brain root. So real spawns are `general-purpose` → no match → exit 0. S085-class gap, uncaught (S085 only re-tested the two path-based hooks).
- **🟠 Inward/outward (D2):** ~65% inward; the single most expensive build (cockpit/visualizer line) exists to *watch the agent work*. D-027 borne out and live.
- **Inversions worth noting:** Zezima (3 sessions, the cut candidate) has a *larger* persona delta than Jebrim (D5). Disciplines with a reliable trigger are followed; only OPEN (trigger bypassed on mid-conv entry) leaks (D3). Two-brain split pays rent; only the shared SNNN counter + dual D-NNN namespace are real tax (D6). Theming tax is real only at 3 routing-ambiguity points; dual-naming, not stripping (D7, respects the documented playfulness preference).

## Empirical D8 work (the load-bearing part)

- **Proven firing from brain root:** real `rm` BLOCKED (block-deletes), real Write to `confirmed/` BLOCKED (block-confirmed-writes). Guarantees #1, #2 are real gates.
- **Direct-invocation harness (11 cases):** role hooks correctly block on `agent_type ∈ {dwarf,gnome,penguin}`, correctly allow on `general-purpose`/absent.
- **Definitive payload probe (principal-authorized):** registered a passive exit-0 PostToolUse logger in `settings.local.json`, spawned a real `general-purpose` sub-agent, captured: principal calls have `agent_type:<ABSENT>`; **sub-agent calls carry `agent_type:"general-purpose"`, `agent_id` present**. So Claude Code DOES stamp `agent_type` = the subagent_type string. Probe reverted. → the hooks are correct; the only defect is config-unreachability. **Fix = register configs at brain root** (option 1); the `agent_id`-fallback rewrite (option 2) is unnecessary.

## What I changed (the fix)

Registered 3 agent configs at **brain-root `.claude/agents/`**: `gnome.md` + `penguin.md` (verbatim copies of the gielinor versions) + newly-authored `dwarf.md` (none existed). Brain-root `.claude/agents/` is outside the live §O.6 sibling's rewrite scope — no collision.

**Verification deferred — and the failure is the proof:** spawning `subagent_type="gnome"` this session returned `Agent type 'gnome' not found` → (a) live demonstration of the gap, (b) agent configs don't hot-reload, so the fix applies to the **next** brain-root session. Hand-off: in a fresh cockpit session, confirm gnome/penguin/dwarf are spawnable and a gnome's write to `confirmed/`/`meta/` is BLOCKED.

## Coordination

- Live sibling at entry: braindead-78e596a8 (§O.4 Obsidian) — ENDED mid-session (wrapped S104, applied §O.4). Then braindead-7c91117c spawned (S105 §O.6 link-rewrite across gielinor+dev-brain `.md`). Posted a `→ @7c91117c` heads-up: my fix surface (brain-root `.claude/agents/`) is outside their scope; staying read-only on gielinor/; appended via `>>` to dodge the link-rewrite race.
- Steered fully clear of cockpit/*, hooks (read-only), gielinor/ writes, switchboard/state-*.

## Open / hand-off

1. **Fresh-session verification of the D8 fix** (above).
2. **Two gielinor/ doc fixes** (deferred — 7c91117c's surface): `spawning-gnomes.md:11` (+ sibling skills) point at the unreachable `gielinor/.claude/agents/` location; `CLAUDE.md` overclaims #3–#6 as un-bypassable guarantees.
3. **The audit's two real problems** beyond D8: build the outward half (§C / D-027); land the deferred OPEN hook (D3).
4. Decide Guthix consultation's fate — a whole mode, 0 uses ever (D1).

Strategic next step UNCHANGED — §C shipping-mart pilot ([[D-027_inward_outward_build_imbalance]]).
