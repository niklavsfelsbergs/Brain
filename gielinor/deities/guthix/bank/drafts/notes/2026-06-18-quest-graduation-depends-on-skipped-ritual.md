# Quest graduation is discipline-gated, and the ritual that does it is being skipped

**Observed:** bankstanding [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]] (2026-06-18), prompted by a principal question.

## The drift

Jebrim's `quest-log/in-progress/` holds **73 files** (2026-06-18). Most are not live:
- **Stale-done** — shipped + committed work whose comms entry posted a CLOSING ([[S243_f6d41a0d_ups-lps-oml-2026-surcharge-export|S243]], S244, S251, [[S259_5463f8a7_shipping-quota-three-way-archived-anchored|S259]], [[S261_c2f15e55_uk-yodel-oog-cap-correction|S261]], [[S263_fd7bcba7_ups-retention-cell-grain|S263]], [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]], and a long [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]]–[[S236_a7ea5300_eu-tender-cleanup-and-nfe-commit-rule|S236]] tail) but the quest file never moved to `completed/`.
- **Sub-agent traces** (~25) — `S_shipagent_*`, `S_dwarf_*`, `penguin_*`, `recon_*`, `S256_shipping-agent_*` — sub-agent run-logs that have **no graduation path at all**; they just accumulate.
- **Genuinely-open umbrella quests** (a minority) — [[S248_319db0c2_ups-retention-curve|S248]], S250, [[S245_3172630e_eu-tender-no-hermes-routing-ops-coherence|S245]] deliberately kept in-progress across sessions.

## Why

Quest promotion (`in-progress/` → `completed/`) is **ritual discipline, not hook-enforced**. Two paths, both currently leaking:

1. **Mid-session graduation** — the owning session must consciously `git mv` on quest-close. Many Jebrim sessions are "late OPEN … posting at close per the entry gate": they enter mid-flow, do the work, commit their pathspec footprint, and stop **without running the full `close-session` ritual**. So the per-session graduation never happens.
2. **[[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] all-players auto-graduation** (`close-session` step 6) is the safety net built for exactly this ([[D-029_auto-graduate-unambiguous-complete-ready-quests]] — its own note records Jebrim once hit "5 stale-done over 18 in-progress"). But it only fires *inside* a real close-session pass. Skipped ritual → skipped net.
3. **The [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] parallel-safety guard** ("orphans NOT mine; NOT sweeping") correctly stops a session clobbering a sibling's files — but as a side effect, no session ever cleans up another's leftover. Accumulation is the equilibrium.

Sub-agent traces are a separate, unhandled class: nothing graduates or archives them.

## Implication / proposed fix (dev-brain or principal call)

- **Immediate:** a deliberate `close-session` pass on Jebrim (or a gnome) once [[S265_17290ea4_scm-resizable-columns|S265]] frees the namespace — its [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] scan graduates the unambiguous shipped+committed quests as one vetoable batch; sub-agent traces archived.
- **Durable (candidate dev-brain proposal):** the gap is that graduation rides a ritual that fast sessions skip. Options: (a) a lightweight in-progress-accumulation **detector** (mirror of `lesson-store-check.py`) that flags when a player's `in-progress/` exceeds N, surfaced at respawn; (b) make even a fast/late-OPEN close run the [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] scan; (c) a defined archive path for sub-agent traces so they don't count as in-progress quests. Bankstanding can't fix this itself — it cannot write per-player layers.

Mirrors the MEMORY.md finding from the same pass ([[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]]): a store grows monotonically through use because the prune step is discipline, not enforcement, and the discipline lapses under load.
