# S105 — Obsidian §O.6 backlink enrichment (prose-ref wrap, both brains)

**Session:** braindead-7c91117c · 2026-05-26 · dev-brain via "lets develop gielinor" (mid-conversation pivot)
**Status:** DONE. Two commits — `5174201` (main pass) + `143c3a0` (sublog fix). Graph verified by principal reload.

## Wrap-up addendum (post-CLOSING)

- **Sublog→parent fix (`143c3a0`).** Principal's graph still looked sparse → measured it the way Obsidian computes (resolve every `[[link]]`): 350 nodes, **1207 edges, 74% connected / 26% isolated**. The first "still sparse" screenshot was a **stale cached graph** (Obsidian hadn't re-indexed the 265-file change); after reload it matched. While diagnosing, found sub-logs were isolated because self-skip keys on `id_of(stem)` so a sub-log's parent-session ref looked like a self-ref — fixed so self-skip fires only when `is_main`. De-isolated ~36 gielinor + dev sub-logs (gielinor no-outbound 174→138; dev →5). Minor residual: `S014-D1`-style hyphen-title sub-logs whose only ref is the hyphenated title (the `-` blocks the match) — left.
- **57 unresolved links audited** — all expected: cross-brain (`D-012`/`D-016`/`S083`, §O.5) + pre-existing hand-authored broken/relative-path `[[links]]`. **Zero broken links from this pass** (resolve-guarded).
- **§O.8 (semantic/topical cross-linking) CONSIDERED + DEFERRED** (plan.md §O.8). The residual 26%-isolated floor won't shrink via ID-wrapping — it needs *topical* links (note→related note by subject), which have no ID to match → embedding-similarity + HITL approval, a build. Recommendation NOT now: inward (D-027), navigational-polish-not-capability (retrieval uses embeddings without materialized links), week-old corpus. Revisit with §N. **Next move stays §C (outward).**

## What this was

[[S104_78e596a8_obsidian_gielinor_link_migration|S104]] handed off §O.6: the gielinor Obsidian graph is verified-but-sparse (350 files, 76% isolated) because notes carry their source-quest anchor as **plain text**, never wrapped. The narrow hand-off was "wrap anchors in gielinor `examine/confirmed` + `bank/notes`." The principal **widened it twice**: first to "a full pass on the whole brain to connect the dots," then explicitly to the **maximal** scope — wrap *every* inline resolvable S/D-ref across **both brains**, quest-log prose included.

## What shipped

New **prose-wrap mode** in `bank/research/obsidian-link-migrate.py` (`--mode prose`), additive — the proven §O.4 `links` mode is byte-identical when unused. It finds UNbracketed resolvable ID tokens in prose and wraps them as `[[stem|ID]]` (display alias → on-page text reads identically; only the graph gains an edge). link-TEXT only, NO renames → hooks/cockpit filename parsing untouched, fully git-reversible. Idempotent (re-runs skip inside-link spans).

Safety design:
- **Resolve-to-a-real-file guard** — only wraps IDs that resolve to a file in scope; everything else stays dangling/left. False-positive net.
- **Prefix whitelist** — only prefixes that actually label a vault file are considered, so `L2448` (line refs), `M365`, `T11`, `Q10`, `CW48`, `FY2025` never enter the report.
- **Self-ref skip** — a file never links its own ID (469 self-refs skipped across both vaults).
- **Per-vault resolution** — cross-brain refs stay dangling per §O.5 (the per-brain-vault model).
- **Scope exclusions** — `inventory/`, `archive/`, `rejected/` (volatile/dead), `comms/`, `experiments/`, `last-alched.md` (operational/runtime), and `CLAUDE.md` + `meta/` + `spellbook/rituals/` + dev `spellbook/` (user-only rulebook/body — read as instructions, wikilink noise for marginal value). These stay valid link TARGETS, just not wrap SOURCES.

### Numbers (applied)

- **Clean wraps: ~2,422** across ~241 in-scope files (gielinor 1,010 / dev 1,417, minus 5 reverted rulebook hits). Knowledge layers + quest-log, both brains.
- **Dupe wraps: 129** (gielinor 52, dev 77) — the 10 ambiguous IDs, disambiguated.

### Dupe disambiguation (the judgment work — encoded in `PROSE_DUPE_RESOLUTION`, vault-local-guarded)

- Same-session copies / clear canonical → one target: **[[S014_visualizer_polish_and_aesthetics_pass|S014]]** → ttyd-howto; **[[S049_17e701eb_visualizer_state_aware_motion_and_action_line|S049]]** → visualizer_state_aware (completed, over the in-progress stub); **[[S060_brain_self_audit_and_plan_reconciliation|S060]]** → brain_self_audit (the [[D-027_inward_outward_build_imbalance|D-027]] source; cockpit in-progress S060s too obscure to be bare-referenced); **[[S076_322cb5c3_cockpit-vscode-rename-and-focus|S076]]** → scm-alert-engine-audit (all in-scope refs are SCM context); **[[D-012_close_session_harvest_pump|D-012]]** → close_session_harvest_pump.
- Namespace collision (`bank/decisions/` vs `bank/main-brain-construction/`): **[[D-001_two_brain_split|D-001]]/[[D-002_folder_name|D-002]]** → subtree rule (construction subtree → its own scheme; else the canonical decision). Verified: `main-brain-construction/_about.md` → phase-1-scaffold, `S099` quest → two_brain_split.
- Genuinely-different sessions, topic-disambiguated: **[[S038_brain_underutilization_diagnosis|S038]]** → brain_underutilization by default (all in-scope refs are the "underutilizing the brain"/Guthix-consultation context), cockpit-vscode files → vscode_claude_focus. **[[S086_e668ec7e_brain-technical-docs|S086]]** → brain-technical-docs by default, [[D-030_worktree_isolation_for_parallel_sessions|D-030]]/build-lessons (edit-race context) → compose-bar. **[[S062_switchboard_lifecycle_feed_persistent_server_peek|S062]]** → citation-leak by default, push/euro-context (push-denial examine, [[S065_bfa95764_cockpit-askuserquestion-hang-fix|S065]]/[[S075_d27b2fe0_agent-prose-into-feed|S075]]) → euro-precision-and-build-report. Spot-checks all confirmed correct post-apply.

## Verification

- Idempotency: re-run prose dry-run → 0 wraps, **0 flagged** both vaults.
- §O.4 gielinor links-mode still clean (0 rewrites, 18 known cross-brain dangling).
- **0 file renames**; diff is link-text-only.
- Topic-exception resolutions spot-checked on disk → all correct.

## Findings / open (NOT in S105 scope)

- **dev links-mode drift: ~103 bare `[[ID]]` bracketed links** still unmigrated — §O.2/O.3 only covered `D-`/`S-` prefixes, never `Q-`/`A-`/`I-`/`R-` (`[[Q-001]]` etc. are broken in Obsidian). Pre-existing in HEAD, confirmed not caused by this pass (prose mode only writes full-stem aliased links + skips already-bracketed). → a future **§O.7 links-mode top-up** (extend the prefix coverage + the same dupe treatment for the 7 flagged). Quick + safe (0 dangling), but re-opens dupe disambiguation, so deferred.
- cf03bfe1's [[S106_cf03bfe1_self-eating-audit-and-d8-enforcement-fix|S106]] left two doc fixes for a gielinor-cwd session: `spawning-gnomes.md:11` (+ penguin/dwarf) name an unreachable `gielinor/.claude/agents/` location; `CLAUDE.md` overclaims guarantees #3–#6. Not §O.6.

## Parallel notes

- Entered mid-conversation; OPEN posted (steps 6–8 fired). One live sibling at entry — **cf03bfe1** (read-only self-eating audit) — CLOSED mid-session (shipped [[S106_cf03bfe1_self-eating-audit-and-d8-enforcement-fix|S106]], committed `5cd2f97`, D8 enforcement-gap fix). It left `comms/active.md` + `respawn.md` unstaged **for me as holder**; I carry them.
- Excluded from my commit (pre-existing WIP / runtime): zezima `S095_f60153e0` quest WIP, `bank/build-lessons.md`, `state.ndjson`, cockpit/switchboard diag. My wraps in those 2 WIP files stay uncommitted for their owner ([[S098_b53fca39_obsidian_fit_and_dlink_migration|S098]]/[[S104_78e596a8_obsidian_gielinor_link_migration|S104]] precedent).
- Strategic next step UNCHANGED — **§C shipping-mart pilot** ([[D-027_inward_outward_build_imbalance]]), the load-bearing OUTWARD build. §O.6 is inward (serves §N GraphRAG).
