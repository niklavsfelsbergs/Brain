# Token-usage audit — per-session static load (2026-05-24)

> Principal cue (dev-brain): *"investigate the brain for unnecessary token usage."* Scope chosen: the **per-session static load** — what lands in context every session, before the first prompt. Highest leverage, because this cost is paid on every session of every actor.
>
> Author: Braindead, sid 93958e4c. Measurements via `Get-Content -Raw .Length` (chars) ÷ 4 for est-tokens; the dev `respawn.md` figure is the real tokenizer count from the Read tool.

## The two cost surfaces

1. **`@import` chain — in the SYSTEM PROMPT, every brain-root session, every turn.** `brain/CLAUDE.md` → `gielinor/CLAUDE.md` → 7 `meta/*.md`. ~**18,120 est tokens**. Higher-frequency than respawn reads (it's the system prompt). Note: prompt caching softens the marginal per-turn cost, but it's still counted, re-paid on cache miss (≥5 min idle / context edits), and consumes context budget regardless.
2. **Respawn-ritual reads — once per session.** Dev-brain: `respawn.md` + latest quest-log. Main-brain: global `keepsake`+`confirmed` (tiny — 240 tok, well-disciplined) + the active player's identity layer.

## Findings, ranked by leverage

| # | Item | Cost | Status |
|---|---|---|---|
| 1 | `developer-braindead/respawn.md` | **~49.5k tok / dev session** | ✅ FIXED this session |
| 2 | `@import` chain (system prompt) | ~18.1k tok / brain-root session | 🟠 Proposal A |
| 3 | Jebrim `examine/confirmed/` (20 files) | ~8.9k tok / Jebrim session | 🟡 Proposal B |

Global `confirmed/`+keepsake = 240 tok total — that layer is well-disciplined; the problem is concentrated, not diffuse.

---

## ✅ #1 — respawn.md collapse (DONE)

410 lines / ~49.5k tok → 42 lines / ~2k tok. **~47.5k saved per dev session, zero information lost.** The file was append-PREPENDed with ~20 stacked `Last updated` blocks ([[S049_17e701eb_visualizer_state_aware_motion_and_action_line|S049]]→[[S072_dbd41cc0_cockpit-fluid-ui|S072]]) + a redundant `Where we are` section (re-summarizing the same sessions) + a `Next step` section thick with obsolete struck-through steps + a ~105-line cross-session lessons tail — all read in full every dev respawn, while the file's *own* discipline said *"Overwritten in place — not append-only. History lives in quest-log/."* The tail navigation (`Files to read first`) was also stale (pointed at [[S052_98d4ec5e_switchboard-rebuild|S052]] switchboard while the head was [[S072_dbd41cc0_cockpit-fluid-ui|S072]] cockpit).

- Lessons tail relocated **verbatim** to `bank/build-lessons.md` (read on demand, not loaded at respawn). Individual lessons can graduate to `examine/I-NNN_*.md` during a reflection pass.
- Stacked blocks + `Where we are` summaries dropped from the file (recoverable from git history + the per-session `quest-log/SNNN_*.md` entries they duplicate).
- Discipline note hardened + a [[D-024_parallel_player_coordination|D-024]] parallel note added: **prepend one line at close, don't overwrite from a stale full copy** (a sibling [[S074_cockpit_switchboard_status_fixes|S074]] close already exercised this correctly).

---

## 🟠 Proposal A — trim the `@import` chain (PROPOSE-ONLY; `meta/` is user-only)

The rulebook is legitimately needed, but it's verbose and overlaps itself. Two tiers:

### Tier 1 — safe, high-confidence (~3–3.5k tok)

- **`communication-protocol.md` (3,525 tok): split rules from rationale.** Keep the terse rules in the imported file (Understanding/Plan format, compression test, intent-narration mechanics, wrong-instance + Guthix-routing *triggers*). Move the *rationale* — "why this rule exists", the born-S038 history/dates, the worked examples, the long per-actor voice tables — to a cued-retrieval `meta/communication-protocol-rationale.md` (NOT imported). Est −1.5–2k.
- **`modes.md` (4,166 tok): move the exhaustive per-role allow/deny path lists out.** The dwarf/gnome/penguin boundaries are spelled out in full here AND in `write-rules.md`'s "Ritual write-reach" table AND enforced by the hook files (the actual source of truth). Keep the conceptual model (two axes, five session modes, 1–2-sentence role intents) in the import; move the exhaustive path bullet-lists to the hooks' docstrings or a single cued `meta/role-write-boundaries.md`. The agent rarely needs the full lists mid-session, and a forbidden write is hook-blocked regardless. Est −1.5k.

### Tier 2 — judgment, medium-confidence (~4.7k tok)

Drop from `@import`, keep a one-line pointer in `gielinor/CLAUDE.md`, read on cue:

- **`layer-routing.md` (2,196):** consulted "when in doubt mid-session" — that's cued by definition. Risk: routing drift if the agent forgets to consult. (Mitigation: the one-line pointer names the trigger — "writing content mid-session? consult layer-routing.")
- **`death-and-spawn.md` (766):** crash-recovery + reset behavior; only relevant at respawn reconciliation (already covered by the respawn ritual) or a rare reset. Low session relevance.
- **`drafts-mechanics.md` (1,074):** consulted during `/drafts` / alching, not general work.
- **`archive-discipline.md` (667):** its core rule (never delete; move to `archive/`) is already a hook + one of the six guarantees in `CLAUDE.md`. The structural detail is cued.

**Net potential: 18.1k → ~10–11k (~40% cut).** Tier 1 alone is the easy win; Tier 2 trades a little discipline-robustness for tokens — the hooks still enforce the hard lines, so the downside is "agent has to remember to read the routing/drafts reference," not "agent can break a guarantee."

**Caveat on caching:** the system prompt is prompt-cached, so the per-turn marginal cost of these tokens is lower than face value — but the cut still helps cache-miss turns, context budget, and any non-cached read. The respawn-read items (#1, #3) are NOT system-prompt-cached the same way, so they're purer wins.

---

## 🟡 Proposal B — tighten Jebrim's `examine/confirmed/` (PROPOSE-ONLY; hook-gated `confirmed/`)

20 files / ~8,930 tok, read in full every Jebrim session (the respawn ritual reads *every* `.md` in `confirmed/`). Two things to know:

- **`current.md` is a 278-char placeholder.** Do NOT "consolidate into current.md and read only it" — that's exactly the [[S038_brain_underutilization_diagnosis|S038]] regression (respawn was *changed* from reading `current.md` to reading the folder because the summary was silently dropping entries; see `bank/build-lessons.md` → [[S038_brain_underutilization_diagnosis|S038]] "frame ≠ root cause"). The summary doesn't reduce load anyway; it adds.
- **The real lever is brevity + pruning, done in a Jebrim alching pass.** The brevity discipline is already on record (claim + anchor + rule; cross-project memory `confirmed_entry_brevity`). A tight entry is ~150–300 chars (~50–75 tok). These are 4–10× over:

  | entry | tok | |
  |---|---|---|
  | audit-finding-vs-ground-truth | 826 | tighten |
  | verify-git-tracked-with-ls-files | 736 | tighten |
  | translation-table-bidirectional-risk | 728 | tighten |
  | cross-project-read-context-as-advantage | 610 | tighten |
  | git-add-scoping-with-parallel-sessions | 588 | tighten |
  | rule-text-becomes-agent-vocabulary | 547 | tighten |
  | check-artifact-mtimes-doc-not-source-of-truth | 540 | tighten |
  | grounding-before-advice | 528 | tighten |

  The 8 entries >500 tok carry elaboration that belongs in the quest-log, not the confirmed entry. Tightening them to claim+anchor+rule saves ~3–4k. Several also look mergeable (multiple Windows/git-substrate lessons; multiple "verify ground truth" lessons) — a merge-to-one-entry + archive-the-rest pass could save more. **Execution: a Jebrim alching session focused on `examine/confirmed/` tightening + pruning** (per-player writes are hook-gated; Braindead can't and shouldn't do it from dev-brain). Bankstanding can also flag Jebrim as overdue.

Same pattern will recur for any player as their identity layer grows — worth a recurring alching cue when `confirmed/` total crosses a token budget.

---

## Recommended order

1. ✅ respawn.md (done).
2. Proposal A Tier 1 (split comm-protocol rationale + trim modes lists) — biggest safe `@import` win.
3. Proposal B (Jebrim alching tighten pass) — needs a Jebrim session.
4. Proposal A Tier 2 — only if the token budget warrants trading some discipline-robustness.
