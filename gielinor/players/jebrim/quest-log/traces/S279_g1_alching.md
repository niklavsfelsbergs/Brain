# [[S279_6fbdcee1_orwo-tender-roadmap-and-ups-base-validation|S279]] — gnome g1 alching trace (Jebrim)

**Ritual:** alching (Guthix bankstanding Phase 0). **Player:** Jebrim. **Gnome:** g1. **sid8:** d371d189. **Date:** 2026-06-19.
**Spawned because:** all 3 alching heuristics fired (>20 harvest turns since 2026-06-17; >10 pending drafts [21 examine + 11 non-ORWO bank]; ~2 days heavy activity).

This is a *trace*, not a quest ([[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]]). Principal folds keepers; disposable after. Full result in `last-alched.md`.

## Steps walked
- **0** spawn-decision: gnome (all 3 fired). Read write-rules / modes / alching / spawning-gnomes / last-alched.
- **1** examine drafts: 21 surfaced, read all, per-draft promote/edit/fold recommendation + twin-flags (8 warm-MEMORY twins). Gnome cannot write confirmed/ → recommend only.
- **2** bank drafts: 11 non-ORWO promoted (git mv drafts→notes, subpath preserved); 4 ORWO left as drafts (excluded); 0 rejected; 1 note-vs-note supersession surfaced (not archived). Staleness scan: 0 archives (bias-to-less; live tender).
- **2b** domain-coverage detector run + reported. `/bank/domains/` writes gnome-blocked (6th time) → recommend only. 2 STALE (both mv-mtime false positives), 1 new-digest candidate (uk-yodel).
- **3/3a** 0 quest graduation + 0 new self-obs (value already in the 11 banks + 21 examines).
- **4** examine current.md 6526 B OVER (user-only rewrite, 6th flag); keepsake + niksis8_char OK.
- **5** rejected pattern holds (Jebrim examine = analytical, not introspective).
- **6** 0 skill drafts (drafts empty; candidates below threshold/already codified).
- **7** last-alched.md updated → 2026-06-19, pass closed.

## Moves performed (11 git mv, drafts/notes → notes)
2026-06-17-uk-yodel-tier-caps-and-coverage; projects/{2026-06-18-scm-shift-processed-tier-baseline-prune, 2026-06-18-ups-carrier-expected-cost-multipliers, 2026-06-18-ups-retention-cell-grain-operational-ceiling, 2026-06-19-shipping-mart-ro-grant-surface, 2026-06-19-uk-offshore-dpd-ups-cost-blowout, 2026-06-19-uk-yodel-negotiation-levers, 2026-06-19-non-orwo-expected-understatement-parked}; scm/{2026-06-18-resizable-table-columns, 2026-06-18-shift-query-tiering-and-processed-fallback}; tooling/2026-06-18-redshift-mcp-readonly-cte-materialization. New subdirs: notes/scm, notes/tooling.

## Anomalies for principal
- /bank/domains/ hook gap (6th). examine over-budget (6th). 37 in-progress files (stale backlog). 2 STALE digests = mv-mtime false positives (detector blind spot). 8 examine↔MEMORY twins → bankstanding step 8.
