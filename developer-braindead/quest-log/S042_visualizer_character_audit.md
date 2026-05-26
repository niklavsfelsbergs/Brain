# S042 — 2026-05-22 — visualizer character audit ("fix the map once and for all")

**Status.** Audit complete; 4 of 6 ranked fixes landed (#1, #3, #5, #6); 1 deferred to f9da453a (#2 sprite anchors — their domain); Tier-3/4 carried as carryforward. [[D-025_visualizer_character_audit_findings]] captures the full bug list with code refs.

## What happened

- **Principal cued the audit** with: *"We need to fix the map once and for all. Sprites and speech bubbles keep getting stuck or things not appearing. We need a full audit on the behaviour and bugs of the characters."* Entered dev-brain mode mid-conversation via *"lets develop gielinor"* (per the brain-root router).

- **Three parallel recon dwarves** (D26/D27/D28 — general-purpose agents). D1 mapped every character class's full lifecycle (spawn/walk/intent-bubble/despawn) across `index.html`. D2 traced event flow from `emit-event.py` and `status-sidecar.py` through state files to the visualizer's consumers. D3 verified every visualizer-related carryforward in `respawn.md` against the current tree, plus health-checked every state file on disk. All three returned self-contained reports with `file_path:line_number` on every claim.

- **Audit converged on 6 ranked bugs.** Two load-bearing (#1 suffix-strip propagation, #2 sprite anchor mismatch under PNG-scale migration). Two confirmed live in current state files (#3 manifest collapses parallel Braindeads to instance:1; #6 state-instances.json byId never cleaned on crash). Two defensive (#4 actor:unknown on UserPromptSubmit-first-turn; #5 idle GC missing for sub-agents). Plus 8 Tier-3 latent items and 4 Tier-4 housekeeping items — full list in [[D-025_visualizer_character_audit_findings]].

- **Three parallel Braindead sessions in residence simultaneously** — f9da453a (sprite migration, parked at `waiting_for_user` for ~80min during audit), a163241a (designed `brain/ideas/`, closed during my recon as the *other* S040), 4508bd10 (drafted [[D-024_parallel_player_coordination]] parallel-coordination, closed as S041). My session inherited S042 after the SNNN collision protocol (S038 precedent) — S040 and S041 taken, next free.

- **Phase 1 — status-sidecar.py fixes (no collision).** Bugs #3 + #6 landed cleanly in commit `cd402d6`. Refactored `_detect_instance` to return `Optional[int]` (None when uncertain) so callers fall through to prev value instead of regressing real instance N→1. Added `_gc_state_instances(live_full)` paralleling `_gc_state_actors`, wired into the `UserPromptSubmit`-only GC pass. Both compile clean.

- **Phase 2 — index.html fixes.** Tried bug #1 first; three Edit attempts failed back-to-back as f9da453a's writes landed between every Read and Edit (line numbers shifted +13 then more as they rewrote `spawnPenguin` to PNG-side mid-attempt). Stepped off, wrote [[D-025_visualizer_character_audit_findings]] decision doc while waiting. When their status file showed `state=waiting_for_user` (file stable), retried — landed cleanly. Both #1 (stripSid8Suffix hoisted to module scope, applied at top of applyEvent) and #5 (despawnIdleInstances extended to sweep dwarves/gnomes/penguins) ~50 lines together.

- **Joint commit.** index.html commit bundles my audit fixes alongside f9da453a's substantial PNG sprite migration + switchboard CSS overhaul (~1100 lines diff, ~20 hunks). Principal authorized the joint shape since waiting for f9da453a's CLOSING was uncertain-duration. Comms entries credit both bodies of work.

## Observations to carry

- **Audit-then-fix is a reusable shape.** Three dwarves on non-overlapping scopes → principal synthesis → tier-ranked triage → fix loop with sign-off. Same shape used for S027 (11 fixes), S033 (12 fixes), this S042 (4 fixes ranked, 2 deferred). Worth promoting the *shape* to `gielinor/spellbook/skills/` — "cross-cutting subsystem audit." Penguins do this for outward-facing research; this is the inward-facing equivalent. Recon under 5min wall-clock, synthesis under 10min, fix loop scales with bug count.

- **"Proceed in parallel" works for non-overlapping commits, NOT interactive concurrent editing.** Principal told me to proceed in parallel for index.html despite the f9da453a collision. The failure mode wasn't merge pain at commit time — it was Edit-tool retry hell against a moving file. Edit tool requires file stability between read-anchor and write; that doesn't hold under live concurrent writes. The fix was to wait for f9da453a's session to enter `waiting_for_user` (a status I can poll via `~/.claude/status/<sid8>.json`), then race a Read+Edit in their parked window. Worth folding into [[D-024_parallel_player_coordination]] as a discipline rule: "interactive concurrent editing of the same file is unworkable; defer until the other session is parked or closed."

- **Status sidecar's state machine is more useful than just the sidebar.** I used `state=waiting_for_user` as a "safe to edit" signal — first time the substrate enabled a coordination decision rather than just rendering it. Generalizable: any future "should I touch X right now" check can lean on the sidecar before bothering comms. Add a one-liner skill: *"before touching a file modified by another session, check ~/.claude/status/<their_sid8>.json — if `state == working`, wait or pivot."*

- **Frame ≠ root cause** (echoing [[S038]] brain-underutilization). "Stuck sprites" sounds like a visual bug; the load-bearing cause is event-key-pollution in pure JS state-mapping (#1: actor-key suffix not stripped propagating to `actorPositions[]`, `intents[]`, `currentBuilding[]` maps). The symptom is visual; the bug is invisible. Same lesson recurring in two consecutive sessions — fold both into one lorebook draft on diagnostic discipline.

- **The respawn carry-forward list ages fast.** D3's verification pass found 3 carry-forwards already-fixed but still listed (S031 dead day-night code, S033's despawnPlayerInstance bubble-fade, S033's ensureActorExists strip — partially fixed). Carry-forward debt accumulates on its own clock. A respawn-section "verify still-pending" pass every N sessions would help. Could be a bankstanding step — Guthix walks respawn.md and re-checks each open item against the tree.

- **The sidecar's `_write_manifest` refresh-on-read pattern is the right shape and should generalize.** I extended it to also refresh `instance` per-row. The principle: "for two-layer state where the inner layer is captured at irregular points (per-session sidecar fire) and the outer layer is read on demand (manifest), refresh-on-read beats write-back." (S039 already wrote a version of this; this session ratifies it.) Worth folding into a Windows-substrate/parallel-session lorebook draft along with the deferred S032/S037/S039 lessons.

- **SNNN collision protocol got load-tested.** Three S040+ sessions today (mine S042, a163241a's S040 ideas, 4508bd10's S041 D-024). Whoever closes first grabs the lower number; I closed last, so I got S042. The protocol works but is rough — the just-drafted [[D-024_parallel_player_coordination]] proposes a sub-suffix convention (S040a/S040b) as an alternative. Live data point for D-024's case.

## Files touched

### Hooks (S042 commit `cd402d6`)
- `developer-braindead/.claude/hooks/status-sidecar.py` — `_detect_instance` refactored to `Optional[int]`; new `_gc_state_instances(live_full)`; per-row instance refresh in `_write_manifest`; wired into `UserPromptSubmit`-only GC.
- `developer-braindead/comms/active.md` — OPEN + @-mention to f9da453a + UPDATE explaining the live D-024 collision.

### Visualizer + carry-forward (final S042 commit, joint with f9da453a's sprite migration)
- `developer-braindead/experiments/visualizer/index.html` — my changes: (a) `SID8_SUFFIX_ACTORS` constant + `stripSid8Suffix(actor)` helper hoisted to module scope; (b) `ensureActorExists` calls the helper instead of inlining strip; (c) `applyEvent` applies `ev.actor = stripSid8Suffix(ev.actor)` at top before any case-branch; (d) `despawnIdleInstances` extended to sweep `dwarfNodes` / `gnomeNodes` / `penguinNodes` on the same 5min idle threshold. **Also in this commit:** f9da453a's PNG sprite migration + switchboard CSS overhaul (~1100 lines diff, ~20 hunks, NOT my work).
- `developer-braindead/bank/decisions/D-025_visualizer_character_audit_findings.md` — full audit findings with tier-ranked bug list and code refs for future sessions.
- `developer-braindead/quest-log/S042_visualizer_character_audit.md` — this entry.

## What's still pending

- **Bug #2 sprite anchor recalibration.** Deferred to f9da453a per @-mention in comms. `SPRITE_HEAD_Y` and `GATHER_SLOTS.bubbleY` need a per-actor table or compute-from-bbox approach. Their sprite migration owns this.
- **Audit Tier-3 items #7-#14.** Triaged opportunistically when adjacent code is touched. Full list in [[D-025_visualizer_character_audit_findings]].
- **Audit Tier-4 housekeeping.** Garbled-path files at brain root (don't touch — archive-discipline); dead procedural-building helpers; zombie session shells in state-dwarves.json; stale respawn.md carry-forward about day-night code.
- **All prior carried respawn items unchanged.** S031 lane bubbles (still untested — Step 2); penguin live test; parallel-Braindead visual tuning; cross-repo sidecar rollout; cross-window click-to-focus (Step 1b); D-020 doc update; Guthix live test (consultation + bankstanding); subtask debounce; replay demos; drafts triage; audit follow-ups; first live gnome spawn; Q-008.
- **Live-verify the S042 fixes.** Open visualizer in live mode; should see (a) parallel Braindeads disambiguated as ·1/·2/·3/·4 in the switchboard sidebar; (b) no console warning `no spawn path for actor braindead-<sid8>`; (c) any legacy `braindead-<sid8>` event in state.ndjson now correctly renders a bubble (it'll route through the bare `braindead` sprite).
- **Sprite anchor fix verification.** After f9da453a lands #2, eyeball the thought-trail and bubble pointer alignment on each scaled actor class. Specifically Guthix — pre-fix, his trail anchors ~80px below his floating sprite.

**Cascade.** `quest-log/S042_visualizer_character_audit.md` (this entry); `bank/decisions/D-025_*.md`; `respawn.md` refresh.

**Main-brain changes.** None this session.
