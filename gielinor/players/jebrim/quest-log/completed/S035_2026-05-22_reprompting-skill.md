# Reprompting skill — design + ship

**Opened/closed:** 2026-05-22 (S035, single-session).
**Status:** completed.
**Type:** procedural — global skill design.
**Deliverable:** `gielinor/spellbook/skills/reprompting.md`.

## The brief

Principal pitched: shipping-agent should have a "reprompt" skill — user says something like "reprompt this" and the agent offers to rephrase the user's request more effectively before acting.

## Turn log

**T1.** Principal proposed trailing keyword `reprompt` as the trigger, scoped to shipping-agent. Reacted with tradeoffs — trigger shape (keyword vs. command vs. phrase) and scope (shipping-local vs. cross-cutting global). Flagged that prompt-rewriting is meta-work, not shipping-domain work; better as a global skill.

**T2.** Principal asked for a concrete recommendation. Proposed end-of-message `reprompt` keyword + `/reprompt` alias, global scope, behavior = rewrite + offer + wait.

**T3.** Principal redirected: softer trigger, phrase-based — "reword this / reprompt this / rephrase this" family, not a magic keyword. Proposed phrase-set + disambiguation rule (user's ask vs. agent's output vs. content edit) + behavior unchanged.

**T4.** Principal said yes-draft-it. Wrote draft at `gielinor/spellbook/drafts/skills/reprompting.md` after checking shape against `spawning-dwarves.md`.

**T5.** Principal: "make it a skill, no alching" — explicit override of the draft-then-approve gate per `meta/write-rules.md` § "User-only with explicit permission" (also applies to skill drafts as discipline-level rule). Moved file from `drafts/skills/` to `skills/`. Empty `drafts/skills/` folder left behind, harmless.

## Decisions

- **Trigger shape:** soft phrase-match, intent-based, not literal whitelist. Reference set listed in skill file.
- **Scope:** global (`gielinor/spellbook/skills/`), not shipping-agent-local. Any actor can invoke.
- **Disambiguation:** user's own ask vs. agent's output vs. content edit. Ask one line when ambiguous.
- **Behavior:** rewrite → offer → wait. Do not execute underlying request until accept/edit/reject.
- **Direct promotion authorized:** principal explicitly skipped draft gate; same shape as the `meta/`/`rituals/`/`keepsake/` explicit-permission override.

## No pending external actions.

## Pending drafts

None. Harvest produced empty set (skill itself is the deliverable; no additional observations stable enough to draft).
