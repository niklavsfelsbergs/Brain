# Reprompting — skill

When the user asks the agent to refine the user's *own* phrasing before acting, rewrite the prompt and offer it back — don't execute the underlying request.

## When this fires

Soft phrase-match anywhere in the user's message (case-insensitive). The reference set:

- "reword this" / "reword my prompt" / "reword what I'm asking"
- "reprompt this" / "reprompt me" / "reprompt my ask"
- "rephrase this" / "rephrase my prompt" / "rephrase what I asked"
- "help me word this better" / "help me phrase this"
- "make this prompt better" / "tighten this prompt"
- "what's a better way to ask this"

The set is illustrative, not exhaustive. The trigger is intent ("user is asking the agent to rewrite the user's wording"), not a literal whitelist. Near-variants count.

## Disambiguation rule

The phrase has to refer to the **user's own request**, not the agent's output. Two failure modes:

- "Reword your last answer" → that's an edit-the-response task. Different skill (output rewriting). Not this one.
- "Rephrase the docs" / "reword this paragraph in the file" → that's a content-editing task. Not this one.

When the referent is ambiguous, the agent asks **one line** before acting: *"Rephrase your ask, or my last reply / the content in X?"* Wait for the answer.

## Behavior on trigger

1. **Do not execute the underlying request** in the same turn. The point of the skill is to gate the work behind a better prompt.
2. **Rewrite the user's prompt — pick one.** Tighter, more specific, with implicit context made explicit. Preserve intent; do not add scope the user didn't ask for. The agent commits to a single best rewrite; offering a menu of two or three phrasings is a punt (see anti-patterns).
3. **Offer it back** in a single code block, then ask: *"use this?"*
4. **On accept** ("yes" / "go" / "use it") — run the rewritten version.
5. **On edit** — user revises inline; run the edited version.
6. **On reject** — drop it, fall back to acting on the original prompt (or ask what they'd prefer).

The rewrite is **a proposal**, not a fait accompli. Same shape as an Understanding/Plan preamble — cheap to correct before the work commits.

**The acceptance gate is on the rewrite, not on action.** The question is "use this rewrite?" (singular, specific) — not "want me to run one of these?" (which conflates picking a phrasing with approving execution and forces the user to do the work the skill exists to do).

**When genuinely torn between two interpretations.** Do not present both as parallel rewrites. Ask one disambiguating question first ("are you after X or Y?"), then propose one rewrite against the answer.

## What "better" means

The headline test: *more answerable, not more articulate.* A rewrite is good when it lets the agent execute without guessing, not when the prose sounds tighter. Natural-language polish that leaves the answerability untouched is not refinement.

A rewritten prompt is *better* when it:

- **Names the artifact.** Specific file paths, function names, table names, column names — not "the thing we were looking at," not "shipping costs."
- **Names the grain.** Per-shipment? Per-month? Per-carrier? Refinement that doesn't pick a grain hasn't refined.
- **Names the action.** "Draft," "summarize," "diff," "rewrite," "decide between X and Y" — not "look at," not "investigate."
- **Names the constraint.** Length, format, audience, deadline — when relevant.
- **Surfaces context the user is carrying implicitly** that the agent would otherwise have to guess at — including knowledge from the active player's `bank/` if it would tighten the rewrite.

A rewritten prompt is *not better* when it:

- **Adds scope.** "Also check Y" is the agent volunteering work — not refinement.
- **Editorializes.** "Carefully and thoroughly" — empty words, drop them.
- **Replaces the user's verb with a fancier one** without changing the meaning. Translation, not improvement.
- **Stays at natural-language altitude.** "Investigate DHL vs UPS costs in Germany, 2025 vs 2026" → "Compare DHL vs UPS shipping costs in Germany, 2025 vs 2026" is a thesaurus pass, not a rewrite. The rewrite is the version that names `fact_shipments`, the cost column, the grain, the carrier labels as they appear in data, and any disambiguation the agent needs.

## Anti-patterns

- **Menu of variants.** Returning two or three alternate phrasings = the agent didn't decide. The skill exists to do that picking *for* the user, not to outsource it back. Pick one. If genuinely torn, ask one disambiguating question (see Behavior step 2) and *then* propose one.
- **"Want me to run one of these?" as the gate.** Conflates "pick a phrasing" with "approve execution." The acceptance gate is "use this rewrite?" on a single specific proposal.
- **Articulate-not-answerable.** Rephrasing the same vague ask in three slightly different vague ways. If the rewrite doesn't make the agent's next move more obvious, it didn't refine.
- **Silently rewriting and acting.** Defeats the purpose; the user can't catch a wrong refinement.
- **Triggering on every "rephrase" mention.** "Can you rephrase that for me?" referring to the *agent's* answer is the output-rewriting skill, not this one. Disambiguate.
- **Asking permission on trivial rewrites.** If the user said "reword: fetch the dwarf logs" and the cleanup is just "Read `quest-log/in-progress/SNNN_dN_*.md` files and summarize" — offer it, but keep it short. Don't ceremonialize a one-line fix.
- **Treating it as a creativity exercise.** This is not "make the prompt cooler." It's "make the prompt more answerable."

## Scope

Global skill. Any player or actor can invoke it. The reprompt itself stays in the active actor's voice — if Jebrim is the principal, the rewrite is phrased as Jebrim would phrase a request to the agent.

## Related

- `meta/communication-protocol.md` — Understanding/Plan preamble is the same family of "catch misunderstandings before commit."
- `meta/modes.md` — the active actor at trigger time stays active through the skill.
