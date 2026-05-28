# 2026-05-21 — Layer routing codified; resume state moves to inventory; skills drafts-gated

## What changed

**New meta doc.** `gielinor/meta/layer-routing.md` codifies which layer each shape of content belongs in (resume state, narrative, knowledge-about-a-thing, procedure, self-observation, observation-about-Niklavs, load-bearing pin, decisions, construction history). `@import`ed from `gielinor/CLAUDE.md`.

**Resume state moves to inventory.** Per-player `inventory/` is promoted from "ephemeral working memory" to **primary resume surface.** Close-session writes `inventory/<quest-slug>-resume.md` per in-flight quest; respawn reads it back as the resume foreground. The `Where we are` / `Next concrete step` / `Files to read first` blocks no longer live at the top of the quest-log file — they live in inventory. Quest log keeps narrative + decisions + turn log only.

**Quest-vs-session split.** `quest-log/completed/` now triggers on **quest close** (deliverable shipped, principal cues done), not on session close. Multi-session quests stay in `in-progress/` across many session closes. Per-player `quest-log/_about.md` updated for Jebrim and Zezima; close-session step 4 reframed; respawn reconciliation prompt rewritten.

**Skills drafts-gated.** `spellbook/skills/` now mirrors the bank-drafts pattern: agent writes to `spellbook/drafts/skills/`, alching promotes. Replaces the earlier heavyweight routing (skills went through `gielinor/lorebook/drafts/`). Per-player `spellbook/_about.md` updated for Jebrim and Zezima; `gielinor/meta/write-rules.md` row updated.

**Bank ≠ methodology.** Per-player `bank/_about.md` clarified: bank holds knowledge *about* the work; methodology / procedures / how-to go to `spellbook/drafts/skills/`. The example case (Jebrim's `moving-target-work-decomposition.md`) was re-routed by C-phase file move during S018.

**Alching recommendation thresholds tightened.** Respawn ritual now surfaces a one-line recommendation when: `last-alched.md` is "Never" AND player > 0 days old, OR >5 drafts pending, OR >20 quest-log turns since last alched, OR >7 days since last alched, OR `current.md` over budget. Old thresholds (>10 drafts, >30 days, >15 entries) were too sleepy for early-life players.

**New alching step — self-observation sweep.** Step 3a walks the player's `quest-log/in-progress/` turns since `last-alched.md` and proposes `examine/drafts/` entries. Self-observations don't depend on quest-close (principal's harvest-rule applies to domain knowledge, not character-self-knowledge). Cap 0–3 per pass.

**Pre-commit soft-block in close-session.** If a player has files in `quest-log/in-progress/` but no matching `inventory/*-resume.md`, close-session surfaces the gap and asks the principal before commit (write resume file / commit anyway / abandon).

## Why

S017 closed with an explicit Niklavs handover: "Jebrim has done a lot of work but his `inventory/` is empty. For each apparently-underused layer, the question is binary: do we not need it, or are we just not utilizing it?" S018 (this audit) executed against that ask, scoped to Jebrim only, main brain only, streaming findings.

The audit found eight findings; the dominant pattern was that **five of Jebrim's layers were starving while `quest-log/in-progress/` ate everything**. The quest log is the path of least resistance (auto-write, no draft gate, no promotion ceremony); everything else requires either discipline or principal action. Concretely, the [[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]] quest-log file (16 turns spanning 3 sessions) carried working-memory content, self-observations, mart-domain knowledge waiting to harvest, and recurring procedures — all in the same file, instead of in their proper layers.

The fix isn't to make the quest log smaller; it's to make the other layers cheaper to land in (drafts-gates everywhere with consistent promotion paths), make routing explicit (`layer-routing.md`), and make the inventory layer load-bearing for resume so quests can actually span sessions cleanly.

## What triggered it

Concrete moment: 2026-05-20→2026-05-21. Jebrim ran [[S001_2026-05-20_repo-orientation|S001]], [[S002_2026-05-20_shipping-data-mart-v1-gap-analysis|S002]], [[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]]. [[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]] spanned [[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]]/[[S015_2026-05-21_ttyd-review-and-dry-run|S015]]/S016 without ever moving to `completed/`, and accumulated the resume sections, the working memory, the harvest-pending domain knowledge, and the methodology draft all in one quest-log file. Niklavs flagged the inventory-is-empty pattern at S017 close. S018 opened in dev-brain mode to audit, found the broader pattern, and proposed the bundled fix.

The five binary questions Niklavs answered to direct the audit (Q1: quest vs session, Q2: enforcement, Q3: collapse spells/skills, Q4: where the self-observation sweep lands, Q5: alching trigger thresholds) collapsed into one structural decision because they're interlocked: routing requires a routing doc; routing the resume state out requires inventory to be the resume surface; making inventory the resume surface requires close-session to write there and respawn to read from there; etc.

## What was affected

- `gielinor/meta/layer-routing.md` (new file)
- `gielinor/meta/write-rules.md` (skills row updated; discipline note added; cross-ref to layer-routing.md)
- `gielinor/CLAUDE.md` (`@import` of layer-routing.md added)
- `gielinor/players/jebrim/quest-log/_about.md` (quest-vs-session split; resume state routed out)
- `gielinor/players/jebrim/inventory/_about.md` (promoted to primary resume surface)
- `gielinor/players/jebrim/bank/_about.md` (bank ≠ methodology)
- `gielinor/players/jebrim/spellbook/_about.md` (drafts/skills/ path; replaces lorebook routing)
- `gielinor/players/zezima/{quest-log,inventory,bank,spellbook}/_about.md` (parity patches)
- `gielinor/spellbook/rituals/close-session.md` (steps 3, 4, 5, 8 updated)
- `gielinor/spellbook/rituals/respawn.md` (steps 6.h + 6.i added; reconciliation prompt rewritten; step 9 updated)
- `gielinor/spellbook/rituals/alching.md` (thresholds updated; step 3 scoped to completed/; new step 3a self-observation sweep; step 6 path fixed)
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` (moved from `bank/drafts/notes/workflow/`)
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` (new)
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_shipping-data-mart-ttyd.md` (new)

## Supersedes / superseded by

Supersedes [[D-019_harvest-pump-installation]] in the narrow sense that:
- The harvest-pump entry routed skill drafts to `spellbook/skills/drafts/<slug>.md`; this entry corrects to `spellbook/drafts/skills/<slug>.md` (drafts-folder-first convention, parallel to bank).
- The harvest-pump entry left skill drafts going through `gielinor/lorebook/drafts/` for promotion; this entry routes them through per-player drafts + alching promotion, like bank.

Otherwise additive — extends the three-pumps frame with explicit routing.

## Anchor

- [[D-015]] in dev brain — full design rationale, alternative options offered to principal, the eight findings, the five-question decision packet.
- [[S018]] in dev brain — the audit session.
- `developer-braindead/respawn.md` — the dev-brain side will track follow-up: cross-player parity (Zezima `_about.md` patches landed alongside Jebrim in this session — both players are now consistent), migration of [[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]]'s resume sections on next close-session pass, watching whether the new soft-block fires usefully.
