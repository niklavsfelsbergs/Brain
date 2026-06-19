# B-021 — bankstanding (2026-06-19)

**Actor:** Guthix. **Cue:** "Hey Guthix, bankstand and alch jebrim" (sid8 d371d189). **Mode:** bankstanding (globals) + Phase 0 alch (Jebrim, delegated to gnome g1).

## Phase 0 — Jebrim alch (gnome g1, run-log [[S279_d371d189_g1_alching|S279]] trace)
- **Spawn:** all 3 alching heuristics fired (>20 harvest turns since 2026-06-17; >10 drafts; ~2d heavy). 5th consecutive gnome-run Jebrim alch.
- **Live-sibling exclusion (principal-confirmed):** jebrim-6fbdcee1 (ORWO tender) LIVE → 4 ORWO bank drafts + `orwo-tender-resume__abfcf511.md` + ORWO in-progress quests untouched. Verified post-pass: 4 ORWO drafts still drafts; resume shows only the live session's ` M`.
- **Promoted:** 11 non-ORWO bank drafts → `bank/notes/` (git mv, subpaths preserved; new subdirs `scm/`, `tooling/`). 0 rejected. 1 note-vs-note supersession surfaced (non-orwo-expected-understatement *supersedes the scalar-fix framing* of ups-carrier-expected-cost-multipliers; both kept, cross-linked).
- **Examine (recommend-only — gnome can't write `confirmed/`):** 21 drafts triaged; g1 ranked promote / fold / hold. Examine over budget → recommend folding the strongest 4–6, holding the rest (incl. `relayed-unverified-subagent-claim`, held again as a `verify-subagent-findings` near-twin). **Principal git-mv's the chosen ones.**
- **Step 2b BLOCKED (6th occurrence):** `gnome-write-boundary.py` still no `/bank/domains/` whitelist. 2 STALE digests (carrier-contracts, eu-tender) are likely **mv-mtime false positives** from the uncommitted 06-09/06-12 wave — verify content before re-synth, else just bump `synthesized:`. UK-yodel = strongest new-digest candidate (3 notes). ~11 uncovered = the just-promoted batch → fold into existing digests. **Principal-self applies.**

## Globals (steps 1–9)
- **1/2:** inbox + all global drafts empty. Nothing.
- **3 (cross-player, N=2 active):** drafted **global** `examine/drafts/2026-06-19-read-the-source-cold-not-from-recall.md` (Zezima read-doc-cold + Jebrim read-domain-cold/mart-from-memory → read the canonical source cold, not from recall). Declined the niksis8 collaborative-layer fact (principal call).
- **4/5:** global current.md all under budget (examine 2.8K / niksis8 0.3K / keepsake 2.4K); rejected folders empty.
- **6 (quest-graduation):** Jebrim **35–37 in-progress** (soft cap 15), 1 `open_dep: none` graduatable + 1 stray trace. **4th escalating leak** ([[B-004_2026-05-23_fourth-bankstanding|B-004]] 15→3, [[B-007_2026-05-25_seventh-bankstanding|B-007]] 15→5, [[B-010_2026-05-29_tenth-bankstanding|B-010]] 22→0, now ~35) despite [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]]. Bankstanding can't move per-player → **recommended a close-session/gnome graduation pass on Jebrim** (principal chose recommend, not spawn).
- **8 (lesson funnels):** `MEMORY.md` over working cap (20K), ~72B under hard cap (24.4K); **0 unlinked drift** (34 dupes all cross-linked → keep-both lever exhausted). Acted: trimmed 2 over-length index lines to the rule; retired `reference_remember_word_banana` (test cruft) → `memory/archive/`. 24328→24283B. **Structural finding:** keep-both ([[B-015_2026-06-01_scoped-examine-graduation-and-store-drift|B-015]]) has no eviction mechanism → MEMORY grows monotonically into the cap; a dedicated tightening / cap-raise is owed (beyond a-few-per-pass).
- **9 (confirmed-scan):** semantic pass — [[D-026_graduate-complete-ready-quests-in-session|D-026]]/[[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] = refinement not contradiction; [[D-021_lorebook-folder-naming-correction|D-021]]/[[D-022_lorebook-folder-naming-correction-expanded-scope|D-022]] = clean supersession; dpd-pl 06-09/06-12 = likely two-scenarios (flag for Jebrim alch); rerating bank/examine = intended both-funnels split. 8 DANGLING + 7 UNDATED HARD flags all floor/per-player → flag-and-recommend (lorebook bare-ID cross-brain danglers = dev-brain fix; 7 UNDATED bank notes want as-of dates at next alch).
- **7 (lorebook):** no behavioral change this round → no entry.

## Carried flags (for the principal / future passes)
1. Examine promotions: principal git-mv's g1's ranked picks (fold 4–6, hold rest).
2. Domain digests: principal-self applies (gnome-blocked) — verify STALE = mv-bump vs drift; new UK-yodel digest candidate.
3. `gnome-write-boundary.py` `/bank/domains/` gap — dev-brain fix (6th occurrence).
4. `examine/confirmed/current.md` 6526B over budget — user-only rewrite (6th+ flag).
5. Jebrim quest backlog ~35–37 — graduation pass owed.
6. MEMORY keep-both eviction mechanism — dedicated pass / cap-raise.
7. mtime-vs-content digest-staleness detector blind spot — stands.

## Commit
Bankstanding-owned, pathspec-scoped to this session's footprint + comms, ORWO + sibling churn excluded. Pending principal go (incl. the stale 06-09/06-12 wave decision). Never push.
