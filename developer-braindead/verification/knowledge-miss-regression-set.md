# Knowledge-miss regression set — Phase 0 eval

**Purpose.** A fixed set of *real* cases where the brain HAD relevant knowledge (or a rule) on disk and failed to load/apply it. This is the pass/fail bar for the anti-deterioration plan ([[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]], `plan.md` §X): every later fix must move coverage here, and no fix may regress a case already covered. Built 2026-06-02; cases drawn from the S125/[[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]] audits, the quest-log, and confirmed memory.

**How to score a case.** For each, ask: *given the current live mechanisms, would the right knowledge have been forced into view before the agent acted?* `caught` = a live hook/gate fires on it; `partial` = fires only under a narrower condition (e.g. a continuation cue that may be absent); `miss` = nothing fires.

**Live mechanisms today (the scorers):**
- `grounding-cue` — UserPromptSubmit nudge on continuation cues / artifacts (own past work). Artifact-detection is UNVERIFIED.
- `domain-cue` — UserPromptSubmit nudge on a registered domain's topic cues (external knowledge home). Today only the **shipping** row is live; EU-tender/FIF/SCM are a commented stub.
- *(none else pushes knowledge — respawn reads identity layers but not bank/research/lorebook; no forced-read of resume state; no Stop-gate.)*

**Plan mechanisms that would catch the misses (the targets):**
- `[DOM]` domain-cue registry row (Phase 2, cheap — one dict)
- `[GND]` grounding-cue (exists; widen/verify artifact path)
- `[FRD]` SessionStart forced-read of keepsake + active resume (Phase 2)
- `[LOR]` load applicable lorebook decisions in player sessions (Phase 1/2)
- `[CRIT]` critic/verify step — judgment rule, NOT hookable (Phase 2 #6 / discipline)

---

## Coverage scorecard

| # | Case (session) | Knowledge that existed | Today | Caught by |
|---|---|---|---|---|
| 1 | Shipping report from memory (S124) | `shipping-agent/reference/{mart-contract,tables}.md` | **caught** ([[S144_9b67aceb_domain_grounding_cue_registry|S144]] domain-cue; fired 14× in 30d — obedience unmeasured) | `[DOM]` ✓ |
| 2 | "cost NULL = load in flight" misread as quality gap ([[S091_remove_leftover_windows_toast_notifier|S091]]) | jebrim `bank/notes/...quality-assessment` | partial | `[DOM]`+`[FRD]` |
| 3 | Property analyzed as "new/third" ([[S066_7f5db8c5_cockpit-sweep|S066]]) | zezima `research/`+`bank` on [[S056_e433ac17_switchboard-osrs-chatbox|S056]] apartments | partial (needs a continuation cue) | `[GND]` |
| 4 | "the message I prepared" grepped in repo, was in bank ([[S076_322cb5c3_cockpit-vscode-rename-and-focus|S076]]) | jebrim `bank/notes/` onboarding msg | **caught** (grounding-cue "prepared") | `[GND]` ✓ |
| 5 | Uploaded folio re-derived cold ([[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]]) | zezima `research/` [[S066_7f5db8c5_cockpit-sweep|S066]] deep-dive | **miss** (artifact-detect unverified) | `[GND]`(artifact) |
| 6 | Claimed a pipeline behavior that was fiction ([[S113_b072b8df_bankstander-question-and-godly-proposal-flow|S113]]) | the corpus / git record | **miss** | `[CRIT]` |
| 7 | Scout said keepsake empty; repeated unverified ([[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]], this session) | the actual `keepsake/` files | **miss** | `[CRIT]` |
| 8 | Schema-add filtered views 500'd ([[S098_b53fca39_obsidian_fit_and_dlink_migration|S098]]) | jebrim `bank/notes` schema-add ordering | **miss** | `[DOM]`+`[FRD]` |
| 9 | FIF deploy-critical config under blanket ignore (S143) | jebrim `bank/notes` FIF lookup | **miss** | `[DOM]` |
| 10 | Applicable lorebook decision unread in a player turn (general) | `lorebook/confirmed/D-NNN` (~30, never loaded) | **miss** | `[LOR]` |

**Today: 2 caught / 3 partial / 5 miss (of 10).**
**Plan target:** `[DOM]` rows close 2/8/9 + firm up 2; `[FRD]` closes the resume/own-note misses (2/8); `[GND]` artifact-verify closes 5; `[LOR]` closes 10; `[CRIT]` (6/7) is the irreducible judgment residue a hook can't catch — those need the critic step or stay discipline. **Reachable: ~8/10 mechanically; 2/10 are judgment.**

---

## Case detail

**1 — S124 shipping report from memory.** Built the automated report as Jebrim-principal without loading the shipping-agent reference; *speculated whether the mart carries dimensions* when `tables.md` answers in one line. Knowledge home: `shipping-agent/reference/`. The guarantee was baked into the shipping-agent SUB-agent config; the principal path had no trigger. **Now caught** by the [[S144_9b67aceb_domain_grounding_cue_registry|S144]] domain-cue (`shipping`/`mart`/carrier cues). Live-fire from a real Jebrim mart prompt still pending.

**2 — [[S091_remove_leftover_windows_toast_notifier|S091]] cost-NULL misread.** Had the signal that a NULL cost = a shipment in flight (transient), but read it as a data-quality gap. The note saying so was in jebrim `bank/notes`. Domain-cue would surface the reference; a forced-read of the relevant bank note is the firmer catch. *Partial today* (domain-cue points at the reference, not the specific note).

**3 — [[S066_7f5db8c5_cockpit-sweep|S066]] property "new third".** Analyzed an apartment as a new, third property before recognizing it as [[S056_e433ac17_switchboard-osrs-chatbox|S056]] apartment #1. Prior analysis was in zezima `research/`+`bank`. Grounding-cue catches this *if* the prompt carried a continuation cue ("again", "back to"); a cold fresh framing slips. *Partial.*

**4 — [[S076_322cb5c3_cockpit-vscode-rename-and-focus|S076]] "the message I prepared".** Grepped the working repo for a prepared message; it was in jebrim's own `bank/notes`. Grounding-cue fires on "prepared earlier" → **caught.** (This is the case that motivated grounding-cue; it's the proof the pattern works.)

**5 — [[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]] folio cold.** Opened an uploaded folio and re-derived the whole analysis before recognizing it as Gate 2 of the [[S066_7f5db8c5_cockpit-sweep|S066]] deep-dive. The catch would be grounding-cue's artifact-detection path — but that path is UNVERIFIED against the real payload, so today this is a **miss**. Fixing the artifact path (or a forced "map the upload to prior work" step) closes it.

**6 — [[S113_b072b8df_bankstander-question-and-godly-proposal-flow|S113]] fiction pipeline.** Asserted the system picks up Guthix's suggestions through a pipeline that didn't exist — a design story stated without checking the record. No topic cue; the failure is *asserting without verifying*. **Miss**, and not hookable — this is the `[CRIT]`/judgment residue (the brain's own "check the record before defending a design story" lesson).

**7 — [[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]] keepsake (this session).** A scout reported global+player keepsake "empty"; I repeated it as a cheap-win recommendation without opening the files (they were mostly full). Same class as #6: a claim asserted without verification. **Miss**, judgment residue. Notable because it happened *inside the session auditing this exact failure* — the strongest possible argument that prose rules don't self-enforce.

**8 — [[S098_b53fca39_obsidian_fit_and_dlink_migration|S098]] schema-add 500.** A serving change filtered on a new column before the data was regenerated; filtered views 500'd while "All" worked. The ordering rule was in jebrim `bank/notes`. **Miss** today; domain-cue (a "deploy"/"schema" domain row) + forced-read of the relevant note would catch.

**9 — S143 FIF gitignored config.** A deploy-critical lookup caught by a blanket `*.csv`/data ignore was nearly architected-around instead of fixed. The "gitignored config is a defect" lesson + the FIF note existed. **Miss**; an FIF/deploy domain row catches the topic.

**10 — lorebook decisions unread (general).** ~30 `lorebook/confirmed/D-NNN` decisions are not per-player-scoped and never load at respawn. A player mid-task can miss an applicable system decision made in a prior session. **Miss**; closing it means surfacing applicable decisions in player sessions (`[LOR]` — by topic-cue or a forced index read).

---

## Notes & honesty

- Cases 6/7 are the **irreducible residue**: "verify before asserting" is judgment, not a bright line — a hook can't grep it. They belong to the critic-step / reasoning-prose bucket, and are the cases that prove *not everything can be hooked* (so the plan must not pretend otherwise).
- This set is **deliberately small and fixed.** It is an eval, not a survey — its job is to make each fix's payoff legible (move the scorecard), not to catalogue every miss.
- Re-score this table after each Phase 2/3 build. A fix that doesn't move it (or regresses a `caught`) hasn't earned its place.
- **Re-score log.** §X.5 @import-trim **Stage A** ([[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]]), **Stage B** ([[S147_79b03308_import_chain_trim_stage_b|S147]], `modes`+`write-rules` → JIT), and **Stage C** ([[S148_4d020f31_import_chain_trim_stage_c|S148]], the `communication-protocol` split — operational sidecars → new JIT `meta/intent-narration.md`) all left the scorecard **unchanged at 2/3/5** — expected, since they are load-order changes (what's *eagerly* expanded), not retrieval-mechanism changes (what *pushes* knowledge into view). No case here depends on `modes.md`/`write-rules.md`/intent-narration being eager. The trim's payoff is the cumulative weight cut (chain 23.3k→11.9k, ~49%) proven *not to regress* coverage — exactly the "smaller without getting dumber" bar.
- **Re-score log (§X.10, the `Reading:` preamble line, [[S148_4d020f31_import_chain_trim_stage_c|next session]]).** Scorecard **unchanged at 2/3/5** — and this is the *honest* result, not a disappointment. The `Reading:` line is **R3-tier (visible, not enforced)**: it surfaces the agent's grounding plan at the Plan line but does **not force** the read, so by this table's scoring rule (*would the right knowledge have been forced into view before the agent acted?*) it catches nothing new. Its value is **orthogonal to this scorecard**: it makes cue-obedience *observable* on the cases already marked `caught` (1, 4) — where a hook fires but obedience is unmeasured (#1 domain-cue "fired 14× in 30d — obedience unmeasured"). A future `ritual-stats` arm parsing the `Reading:` line against the hook's nudge is what would turn that observability into a number; the line itself is the precondition. CORE grew 3,722→4,036 tok (chain 11,899→12,213, +314) — the acceptable cost of a per-turn behavioral rule. The actual coverage move is **X.4** (the `SessionStart` forced-read), which this line *complements, not replaces*.
- **Re-score log (§X.5 @import-trim Stage D — `task-lists` split + R3 rule-index, same session).** Scorecard **unchanged at 2/3/5** — load-order again, not retrieval. `task-lists.md`'s *threshold* (the load-bearing per-turn decision + the durable-`inventory`-mirror trigger) stayed in the always-on CORE; only the *mechanics* (two-homes table, lifecycle, anti-patterns, scope → new JIT `meta/task-lists-mechanics.md`) left the eager chain. No regression case depends on task-list mechanics being eager. Net chain effect across X.10 + Stage D: `task-lists.md` 1,415→721 (−694) offset X.10's +314, so the chain landed **11,886 tok — fractionally below the 11,899 session-start** while *adding* the `Reading:` rule + the R3 rule-index. "Smaller without getting dumber" held a fourth time.
