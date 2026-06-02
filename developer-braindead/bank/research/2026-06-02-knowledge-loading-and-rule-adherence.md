# Knowledge-loading & rule-adherence — audit + online research

**Session.** [[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]] (dev-brain, 2026-06-02, sid 543c6caf). Niklavs: *"We have tons of knowledge but it does not get loaded when necessary. Tons of md instructions; they are often not followed. Audit that — and suggest what can become a hook, what else. Do full research online on how to make an AI brain actually use its knowledge and abide by rules."*

**Method.** Lighter agent-assisted (Niklavs' pick): 3 read-only internal-audit scouts (knowledge-loading, rule-adherence leaks, hook surface) + 2 web-research scouts (agent memory/retrieval SOTA; rule/instruction-adherence SOTA), then synthesis. This file is the durable deliverable; the ranked build backlog lives in `plan.md` §X.

**Relation to [[S144_9b67aceb_domain_grounding_cue_registry|S144]].** A session earlier the same day (9b67aceb) independently diagnosed the *knowledge-loading* half and shipped the first fix — the domain-cue registry (`plan.md` §W). It did **no online research** and was scoped to one hook. This audit confirms [[S144_9b67aceb_domain_grounding_cue_registry|S144]]'s diagnosis against the field, then widens it to the rule-adherence half and a full intervention menu. [[S144_9b67aceb_domain_grounding_cue_registry|S144]]'s hook was re-verified and hardened this session (see *Build outcome* below).

---

## 1. The unifying diagnosis

Niklavs named two problems. They are **one failure** in two costumes:

> **Knowledge and rules that depend on the agent *deciding* to act drift. Knowledge and rules bound to a *deterministic trigger* hold.**

- **Internal proof.** Every hook-enforced line (no `confirmed/` writes, no deletes, the four sub-agent write-boundaries, `block-sub-spawn`) has **zero leaks since birth** (S125 live-fire: 8/8 blocked; 0 deletes ever). Every discipline-only rule drifts: the OPEN-post leak (≥3 gielinor leaks even post-fix), the respawn/comms size caps (regrew past cap in 2 days; 10+ sessions of "WATCH" no-ops), and the trigger for this whole audit — Jebrim built the shipping report *from memory* without loading `shipping-agent/reference/`, while his own `CLAUDE.md` and skill both said "load it first." Knowledge present, rule present, **trigger absent.**
- **The brain's own prior words.** S125 finding #2: *"hook-blocking enforcement holds cleanly; discipline-nudge / manual-deferred enforcement drifts."* §W: *"library-rich, reflex-poor… the only mechanism that actually changes behaviour is the hook; discipline-only rules fire ~30%."*
- **External consensus (independent confirmation).** The 2025–2026 Claude Code engineering literature states the identical thesis almost verbatim: *"Hooks guarantee behaviour; prompts suggest it"* — a prompt rule is followed *probabilistically* and decays; a code rule is deterministic and *"cannot be bypassed, forgotten, or reasoned around."* The brain reached the field's conclusion on its own.

**The non-obvious corollary** (and the one most worth holding): when the brain misbehaves, the reflex is to *add another rule file*. The research says that is often the wrong move — adding eagerly-loaded prose makes **every** rule less likely to be followed (see §3). The fix is to move the rule to a trigger and *remove* it from the eager load.

---

## 2. Knowledge-not-loaded — audit findings

- **Respawn loads only identity-shaped layers** (`examine/confirmed`, `keepsake`, persona, player `CLAUDE.md`). **~80 files of semantic memory** are deferred to "the agent will fetch when needed": Jebrim ~29 bank notes / 8 research / 17 skills; Zezima ~5 / 18 / 1; plus ~30 `lorebook/` decisions that are **not** per-player-scoped and never loaded. There is **no automatic fetch trigger** mid-session — retrieval is entirely the agent's voluntary decision.
- **`keepsake/current.md` (the always-surface tier) is empty.** The one cheap, already-built "force this into every session" surface is unused.
- **`recall-scoring`** (centrality × staleness ranker) exists but is **wired into nothing** (decided on-demand-only at [[S126_c0dd1afb_cockpit-brain-graph-bubble-map|S126]] — staleness was dormant on a 9-day-old corpus; revive when notes routinely go quiet for weeks).
- **`layer-routing.md` is a *write* map, not a *read* index.** It tells the agent which layer to write a given shape to; it does not prompt reading on entry.
- **The fixes the brain already invented are the right pattern.** `grounding-cue-reminder.py` (identity reflex — continuation cue → your own past work, [[D-028_grounding-precondition-needs-a-trigger|D-028]]) and the [[S144_9b67aceb_domain_grounding_cue_registry|S144]] `domain-cue-reminder.py` (domain reflex — topic → external knowledge home) are textbook **just-in-time re-injection**. Weakness: each fires on hard-coded cues, so coverage is only as wide as the cue table.

---

## 3. Rules-not-followed — audit findings

- **The `CLAUDE.md` `@import` chain expands all 8 `meta/*.md` files inline every session.** The research is blunt about why this backfires:
  - **Constraint-count collapse.** Instruction-following falls from ~81% (1–2 simultaneous constraints) to ~37% (4–8) — a 44-point drop; even Claude 3.5 Sonnet tops out ~55% at the high end (arXiv 2505.07591). Beyond ~10 constraints models "break down" (RECAST, 2505.19030). The import chain encodes *dozens*.
  - **Lost-in-the-middle.** Attention is U-shaped — content at the start/end is used; content buried mid-document is dropped first, *even in long-context models* (Liu et al., TACL 2024). A rule in the middle of a 10-import chain is in the worst position.
  - **Dilution.** *"Anything in a system prompt is basically gone in a conversation of 100K tokens."* Front-loaded once, salience near-zero 80K tokens later.
  - **Context rot** (Chroma, 18-model study): every model degrades as input grows, *well before* the window limit (~50K on a 200K model), and worsens with distractors. A bloated always-on context **actively causes** the "has it but ignores it" failure.
- **Most-violated rules are the guided-not-enforced ones**: OPEN-post, the `bank/notes` & `spellbook/skills` draft gates (discipline-only per `write-rules.md`), "load domain knowledge first." All behavioral `communication-protocol.md` rules (Understanding/Plan, grounding-before-advice, wrong-instance check, Guthix routing) are unenforceable prose.
- **Telemetry measures events, not adherence.** `ritual_log.py` logs allow/block/nudge fires; it does *not* compute "% of sessions that posted an OPEN," and is gitignored (no history). Drift is invisible until it's a leak.

---

## 4. What can become a hook vs. what can't

The organizing principle from Anthropic's own Jan-2026 Constitution shift (*reasoning-based instructions beat rule-based ones* — for judgment) plus the hooks doctrine (*bright lines belong in code*) gives a clean two-bucket split:

| Rule type | What moves the needle |
|---|---|
| **Bright-line, mechanically checkable** ("never write `confirmed/`", "always post an OPEN", "load the reference before mart SQL") | **Code / hooks.** Prose just adds tokens and is followed ~probabilistically. |
| **Judgment-shaped** ("match the register", "don't over-formalize", "is this an issue?") | **Reasoning-based prose with an observation anchor** — `examine/` / `lorebook/`. A hook would be wrong; you can't grep taste. |

What merely *adds tokens*: prose restating a bright-line rule the model keeps breaking (→ make it a hook), and rules with neither a *why* nor checkability (→ neither enforceable nor generalizable). The brain already carries the meta-rule: *evaluate rules on whether they pay rent*.

### Claude Code hook capability reference (verified against current docs)

The enforcement channels that matter:
- **`PreToolUse`** — block a tool (`permissionDecision:"deny"` / exit 2), **rewrite** the call (`updatedInput`), or inject (`additionalContext`).
- **`UserPromptSubmit` / `SessionStart`** — inject context into the turn (`additionalContext`); the **only** events that push text the model reliably attends to (user-message slot, not tool output).
- **`Stop` / `SubagentStop`** — `decision:"block"` to **prevent the agent ending its turn** → the substrate for forced self-verification.
- **`PostToolUse`** — block *after* a tool ran, feeding the reason back to the model.

Mechanism note: the nudge hooks emit `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"…"}}` to stdout, exit 0. Text-only, pattern-triggered, no persistence across turns, fail-open. (Pin to the installed Claude Code version before wiring newer events like `TaskCompleted`/`PostToolBatch`.)

---

## 5. Ranked intervention menu

Ranked by leverage. Rec #1 is **done** ([[S144_9b67aceb_domain_grounding_cue_registry|S144]] §W); the rest are the backlog (`plan.md` §X).

**→ HOOKS**
1. **Config-driven domain-knowledge loader** — ✅ **shipped as [[S144_9b67aceb_domain_grounding_cue_registry|S144]]** (`cue_registry.py` + `domain-cue-reminder.py`; the Nth domain is one row). Hardened + re-verified this session.
2. **Stop-hook ritual gate** — bind `close_check.py --ritual` to the `Stop` event so a session cannot end with an unposted OPEN or an unresolved `pending`. Kills the #1 leak class. ⚠️ **Fix `close_check`'s known continuation false-FAIL first** (a Stop hook that false-blocks is worse than an advisory that false-warns).
3. **Draft-gate as `PreToolUse` input-rewrite** — auto-redirect a write to `bank/notes/` → `bank/drafts/notes/` (`updatedInput`); turns two guided-only gates into guarantees, no friction.
4. **`SessionStart` forced-read injection** — the forcing step that took Claude's memory tool from "has it" to "uses it" (+39% on Anthropic's eval): inject "read `keepsake/current.md` + the relevant `inventory/*-resume` before substantive work." And **fill keepsake** (it's empty).

**→ NOT hooks (other mechanisms)**
5. **Trim the import chain → thin router + JIT layer-index.** Highest-leverage *non-hook* change and the contrarian one: stop eagerly expanding all of `meta/`; keep a short always-on core + `layer-routing.md` as the map; load the specific rule file JIT when it's in play (delivered by the topic-cue hook). Architecture, user-only → a Guthix godly proposal. *This directly attacks the §3 constraint-count/lost-in-the-middle root cause.*
6. **Critic sub-agent at close** for judgment rules you can't grep-check (register, "did it reconcile definitions before numbers?"). A reviewer gnome.
7. **Adherence telemetry upgrade** — make `ritual_log` persist + compute compliance *rates* (% sessions posting OPEN, etc.) so drift is visible before it leaks.
8. **mem0-style ADD/UPDATE/DELETE/NOOP reconciliation in alching** — when an alching candidate overlaps an existing `bank/note`, force the explicit supersede/merge/reject decision (reflection-as-ritual already exists; borrow the reconcile step).

**→ Authoring discipline**
9. **Two-bucket every rule** — bright-line → hook and *stop restating it in prose*; judgment → keep/strengthen the *why*. A one-pass audit of `meta/` + `communication-protocol.md`.

---

## 6. Build outcome this session

- **Verified [[S144_9b67aceb_domain_grounding_cue_registry|S144]]** independently (the `_comment_domain_cue` *claimed* boundary-verified; now re-confirmed): 7/7 synthetic cases — shipping-cue→emit, carrier-name→emit, non-shipping→silent, bare report/cost→silent (wallpaper guard), malformed→exit 0, wrong-event→silent, braindead→skip.
- **Hardened `domain-cue-reminder.py`** — it read the status sidecar directly (`_actor_for`), the very status-only path that `_actor.py`'s contract forbids (*"any new actor-needing hook MUST call `resolve_actor`"*) because it re-opens the S124 sidecar-lag race (during lag a dev session would wrongly get a domain nudge). Routed it through the shared `resolve_actor` (status → intent-file anchor fallback). Verified: `py_compile` + the 7 boundary cases + a 4-case isolated unit test of the intent-fallback resolution. **Open:** live-fire from a real player entry (the next Jebrim mart prompt) — committed + registered, so it loads for the next fresh session.

---

## 7. The big strategic recommendation

The brain's architecture is already aligned with SOTA on the big calls: agentic grep over a structured, ID-linked corpus (not RAG — Anthropic abandoned RAG in Claude Code for exactly this corpus shape); durable resume/quest-log state ("assume interruption"); reflection-as-ritual (alching/bankstanding); importance pinning (keepsake). **Two gaps the research points at hardest:**

1. **The always-on import chain is heavier than the hybrid ideal** (rec #5) — and per §3 the weight is not neutral, it *degrades adherence to every rule*. This is the single most counter-intuitive, highest-leverage change.
2. **Make "load the map/keepsake/resume first" a forced step, not a guideline** (rec #4) — the one forcing move that flipped Claude's memory tool from "has it" to "uses it."

The S124→[[S144_9b67aceb_domain_grounding_cue_registry|S144]] pattern is the brain proving the thesis on itself: a confirmed note (*"read the reference first"*) sat in memory and the failure recurred anyway, until it became a hook. **Smartness = the right knowledge firing at the right moment, not more notes.**

---

## Sources

Agent memory / retrieval: Anthropic *Effective context engineering for AI agents*; *Managing context on the Claude Developer Platform*; Claude *memory tool* + *context editing* docs; Claude Code *memory (CLAUDE.md)* docs; MemGPT/Letta; mem0 (arXiv 2504.19413); Generative Agents (Park et al., arXiv 2304.03442); Chroma *Context Rot*; Liu et al. *Lost in the Middle* (arXiv 2307.03172); Cherny on Claude Code abandoning RAG; Cline *Memory Bank*.

Rule adherence / hooks: Claude Code *Hooks* reference & *Best practices*; Anthropic *Claude's Constitution* (Jan 2026); *system-reminders* analysis; NeMo Guardrails (arXiv 2310.10501); Guardrails AI; constraint-following (arXiv 2505.07591, 2505.19030, 2410.06458); IF-CRITIC (arXiv 2511.01014); spec-driven development commentary.

*(Full URLs in the two web-research scout transcripts, [[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]].)*
