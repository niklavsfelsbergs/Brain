# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-22 (end of [[S041]] — design-only session. Drafted [[D-024]] parallel-player coordination after principal flagged the disk-side gap D-019 deferred. Closing this session itself hit the exact collision D-024 is about: respawn.md was rewritten by parallel S039 then S040 sessions while S041 was mid-close. Prior carries: [[S040]] `brain/ideas/` folder; [[S039]] switchboard GC; [[S038]] promote/consult loop; [[S033]] visualizer audit; [[S034]] Guthix consultation; [[S037]] switchboard Phase 3.).

## Where we are

[[S041]] drafted [[D-024]] — parallel player coordination. Proposes shared `gielinor/comms/active.md` (one file, all players + Guthix), liveness via the D-020 status sidecar (not intent-file mtime), session-suffixed `inventory/<topic>__<sid8>.md` and `quest-log/in-progress/SNNN_<sid8>_<slug>.md`, plus a respawn rule for inventory recovery (own sid8 first, else surface live-sibling candidates). Drafts stay plain — comms OPEN announces topic territory. Tolerated: SNNN race window, draft filename collisions. Deferred: cross-brain (player ↔ Braindead) coordination. **Decision-only — nothing scaffolded.** Open items: scaffold `gielinor/comms/` (file + `_about.md`), update `gielinor/spellbook/rituals/respawn.md` and `close-session.md`, update `gielinor/meta/layer-routing.md` for suffixed inventory/quest-log shape. Live proof of the problem: S041's own close hit a respawn.md collision twice (S039 then S040 rewrote it mid-close); S041 abandoned its overwrite and minimally inserted instead.

[[S040]] shipped a new top-level capture surface at `brain/ideas/`. Principal asked for low-friction ideas-noting (*"I just want to be able to say note this idea and then move on"*); existing routing table had no home for pre-everything thoughts (not drafts, not quest-log narrative, not keepsake, not decisions). Three load-bearing choices (location at brain root, one-file-per-idea with `YYYY-MM-DD-<actor>-<slug>.md`, phrase-trigger interface only) elicited via `AskUserQuestion`. New `brain/ideas/_about.md` is the canonical spec. New "Capturing ideas" sections wired into both `gielinor/CLAUDE.md` and `developer-braindead/CLAUDE.md`. New row in `gielinor/meta/layer-routing.md`. No D-NNN, no hooks — discipline-only. Live-test pending (no idea captured via the trigger yet); next session that fires `note this idea: …` is the real test of trigger matching and actor attribution across mode transitions.

[[S039]] fixed switchboard actor resolution and instance-slot drift. Diagnosed three compounded symptoms: (1) `_detect_actor` returned `unknown` on 0-match (no narration yet) or multi-match (stale intent file from mode switch); (2) `state-actors.json.byId` accumulated dead-session entries plus orphan top-level `wisp`/`guthix` scalars; (3) `UserPromptSubmit` fires *before* the agent writes intent for the turn, so `actor=unknown` lands in the status file at turn-start and sticks through working-state until `Stop`. Fixes shipped in `status-sidecar.py`: `_detect_actor` is now a cascading resolver (single intent file → newest by mtime → `state-instances.json` byId fallback → unknown); `_write_manifest` re-detects actor per session at write time without touching canonical status files, so any session resolves on any *other* session's next sidecar fire (5-30s); new `_live_session_ids` + `_gc_state_actors` + `_gc_intent_files` run on `UserPromptSubmit` only, using `~/.claude/status/<sid8>.json` (state ≠ ended, `last_event_ts` < 1h) as ground truth — drops dead byId entries, dead `_*_session_id` markers, the unowned `guthix` top-level scalar (wisp left alone, markerless), and archives `*-<dead_sid>.txt` intent files. `emit-event.py:resolve_instance` now allocates the lowest free integer rather than monotonic `next`; one-time compaction snapped current live sessions back to 1..N. Mini-respawn in `gielinor/spellbook/rituals/respawn.md` gained step 2 (archive outgoing actor's intent file on switch). Verified live — all 5 sessions resolve correctly in the manifest. Ghost sprites at the old high instance numbers will fade within 5 min via idle-despawn.

[[S038]] closed the promote/consult loop. The principal opened with Jebrim ("we are underutilizing a lot of things in the brain") then flipped to dev-brain mid-session. Four-dwarf recon (D1 drafts inventory; D2 in-progress audit; D3 ritual-vs-evidence; D4 Guthix usage trace) surfaced the load-bearing bug: 12 Jebrim confirmed entries existed on disk but never loaded at respawn because step 6.e read `current.md` instead of the folder. The complaint *felt* like tempo (promotion is heavy, doesn't happen); the root was structural. Phase 1 shipped the structural fixes (commit `150e238`): respawn reads folder; 5 stale-done quests walked to `completed/`; 3 ready drafts promoted; 2 missing resume files written; 2 orphan untracked quest-logs caught up. Phase 2 shipped the habit-shaping (commit `607eeb4`): `/drafts` + ritual; close-session step 4 + step 8 enhancements; Guthix routing heuristic. Jebrim's `in-progress/` 18 → 10; identity layer 0 → 14 loading entries. The reflexive proof: this very session asked Jebrim a system-scope question that Guthix's consultation mode exists for — the Guthix routing heuristic born of the conversation mis-routing itself. Deferred (intentional): turn-reflexive bank capture (Jebrim's "B" root cause) — sized large, lowest urgency, reach for it once the new mechanisms have run for a few sessions and the promote/consult tempo is verifiably back.

[[S037]] landed Phase 3 of the terminal switchboard ([[D-020]]) — click-to-focus from the visualizer sidebar to a VS Code window. New mechanism: `status-sidecar.py` walks the process tree via `CreateToolhelp32Snapshot` ctypes on first fire and records `claude_pid_chain` (every ancestor up to depth 20). New `focus-window.ps1` (~150 lines, pure ASCII) iterates the chain to find the first live `Code.exe` with `MainWindowHandle != 0` and brings it forward with `SetForegroundWindow` + `AttachThreadInput`. New `register-claude-focus.ps1` registers the `claude-focus://<sid8>` URL scheme in HKCU; sidebar row click now does `window.location.href = 'claude-focus://' + sid8` (shift-click falls back to copy-sid8). Settings.json sidecar registration also re-enabled at the option-1 shape — `UserPromptSubmit` + `Stop` + `SessionEnd` (3 fires/turn). The terminal-rendering glitch from S032 did not recur in fresh terminals; Step 0 obsolete. Mechanism self-tested via the log (`SetForegroundWindow returned True` against this session's chain); visual confirmation against a *second* VS Code window still pending — with only one VS Code window open the focus call is a no-op. Quest-log entry in `quest-log/in-progress/S037_*.md` carries the open items.

[[S033]] audited the visualizer (live mode + hooks) and shipped 12 fixes across three files. **index.html**: deleted dead day-night code from S031 (`DAY_NIGHT_ANCHORS` / `currentHour` / `dayNightFill` / `updateDayNight`); `despawnPlayerInstance` fades bubble alongside sprite instead of snapping; `ensureActorExists` strips legacy `<actor>-<8hex>` suffix so `braindead-ed610cbe`-shaped historical events resolve to bare `braindead`. **emit-event.py**: `BASH_SUBTASK_TABLE`'s `echo` pattern requires `>` redirect to `.claude/<sidecar>`; `handle_session_end` clears the ending session's keys from every `state-actors.json` `byId` map (was accumulating dead entries) and clears `_mode_session_id` when owned. **status-sidecar.py**: `_detect_actor` scans `*-<sid8>.txt` instead of hardcoded roster; intent carry-forward only when prev actor matches; new `_sweep_stale_tmp()` cleans `<base>.<ext>.tmp.<digits>` leftovers; `_detect_instance(actor, sid)` pulls real instance from `state-instances.json` so sidebar renders Braindead·2 vs Braindead·1; `_write_manifest` excludes `state == "ended"`. Deferred per ruling: state.ndjson unbounded growth (#4), gc_stale_subagents per-call cost (#12). **Live-verification of the new turn-resolution switchboard UX + Braindead·1/·2 disambiguation is the load-bearing next step (folded into S037's Step 1b).** Quest entry in `quest-log/S033_visualizer_audit_live_mode_and_hooks.md`.

[[S034]] expanded Guthix from a ritual-only voice to a two-mode deity: **consultation** (default residence — general questions, cross-cutting lookups, system-shaped reflection) and **bankstanding** (the ritual). Same actor, same sprite; different write authority. Wisp shrinks to "session that has truly had no prompt yet" — any substantive question without a player address now routes to Guthix consultation. Nine doc files in `gielinor/` touched: `meta/guthix.md` (major rewrite), `meta/modes.md` (lifted to five session modes), `CLAUDE.md`, `meta/write-rules.md`, `meta/layer-routing.md`, `meta/communication-protocol.md`, `spellbook/rituals/bankstanding.md`, `deities/_about.md`, `deities/guthix/_about.md`. Decision is [[D-022]]; live test pending (Step 7). No hooks, no visualizer, no code — discipline change on top of existing `guthix.txt` machinery. The S032 origin story ("Hey Guthix" used as a general design surface) was itself the use case that motivated this — the architecture now matches the principal's mental model.

Carried forward — [[S032]] still has its sidecar registration shape decision open (Step 1); the terminal-rendering issue may not recur in fresh terminals so Step 0 may be obsolete.

[[S032]] shipped a new instrumentation layer for parallel-session operation. Started as a Guthix-mode design conversation ("how do I know which of N Claude Code terminals is waiting for me right now"), pivoted into dev-brain, landed [[D-020]] + Phases 1 + 2 of the three-phase build:

1. **D-020 designed.** Three states (`working` / `waiting_for_user` / `idle` / `ended`) derived from `UserPromptSubmit` / `PreToolUse` / `PostToolUse` / `Stop` / `SessionEnd`. Reader-derives-idle from `last_event_ts`. User-global path at `~/.claude/status/<sid8>.json`. Hook decoupled from `emit-event.py` for failure isolation. Three-phase build order — sidecar → sidebar → click-to-focus.

2. **Phase 1 — status sidecar.** `developer-braindead/.claude/hooks/status-sidecar.py` (new, ~180 lines). Maps event → state, writes atomic per-session JSON, 24h sweeper into `~/.claude/status/archive/`. Actor detection by intent-file lookup. Validated live across 6 concurrent sessions on first run — all three states caught in the wild.

3. **Phase 2 — visualizer sidebar.** New `<aside class="switchboard">` in `experiments/visualizer/index.html`, third flex child of `.world` right of COMMS. ~280px wide, OSRS-themed. Polls `state-switchboard.json` every 2s, re-renders ages every 1s. Pulsing yellow dot for `waiting_for_user` is the attention-grab signal. Click copies sid8 to clipboard (Phase-3 hook point). `?sid8=<value>` URL param highlights "this" session with a gold outline. The status sidecar also writes the manifest snapshot to the viz dir (architectural call: browser can't reach `~/.claude/status/` directly; mirror is the minimum-disruption bridge).

4. **Settings.json wired then partially rolled back.** Initially registered the sidecar for all five event kinds. Mid-session diagnosis of a stuck DEC-Special-Graphics terminal state (Claude Code chat output rendering `m` → `┘`, `r` → `┤` in VS Code's integrated terminal) ruled hook frequency out as the root cause but left the four high-frequency registrations *paused* defensively. **Only `SessionEnd` remains registered** — sidecar code is on disk and works; only the per-turn / per-tool-call fires are gone. A `_comment_status_sidecar` field in settings.json documents the pause inline.

Carried forward — [[S031]], [[S030]], [[S029]] context preserved below:

[[S031]] shipped a visualizer overhaul touching `experiments/visualizer/index.html`: world scaled 1.4×, side-by-side layout (`.topbar` hidden, chat rail on right at 380px), day-night overlay deleted, bubbles 2×, per-actor accent color, sprites ~1.7×, thought-trail bubbles (4 cream circles replacing pointer + dashed leader), and **lane-based bubble layout (UNVERIFIED — Step 1 below)**.

[[S030]] shipped the third functional sub-agent role — **penguins**, the research operatives. New per-player `research/` layer distinct from bank. [[D-021]] for the design.

[[S029]] shipped parallel Braindead instances + the dev-to-dev comms channel ([[D-019]]). My session validated this end-to-end in passing — S031 (f39b5b3f) and S030 (ab5ad0df) shipped *in parallel* with S032, and the comms channel + sibling detection functioned correctly (one ABANDONED-candidate false-positive surfaced by the sidecar itself).

## Next concrete step — START HERE

**Step 0 — Open a fresh VS Code terminal.** ~~Carried from S032.~~ ✅ Confirmed in S037: the terminal-rendering corruption did not recur in fresh terminals. This step is now obsolete; remove next pass.

**Step 1 — Sidecar registration shape decision.** ✅ Landed in S037 as **option 1** (`UserPromptSubmit` + `Stop` + `SessionEnd`). `_comment_status_sidecar` in `brain/.claude/settings.json` documents the rationale inline. Hot-reload confirmed working — first user prompt after the edit populated the new fields without a Claude Code restart. Lorebook draft on hook-fire-rate-as-budget still pending — write it next bankstanding pass alongside the ASCII-PS lesson from S037.

**Step 1b — Click-to-focus, the rest of the cases.** S038 confirmed the **in-window** case (terminal pane focus via `niksis8.claude-focus` VS Code extension) works live. The **cross-window** case (focus a different VS Code window) is still mechanism-only — never lived against a real two-window setup. Remaining work, deferred until the principal actually opens a second window:

- Open a second VS Code window (`Ctrl+Shift+N`), start a fresh `claude` session, send any prompt to populate `claude_pid_chain`.
- From *this* window's visualizer, click that row. With current wiring (`vscode://niksis8.claude-focus/...` only), the extension will surface *"no terminal in this window matches"* — the URI lands on whichever window owns the URI handler, which may not own the target terminal.
- Wire the cross-window fallback: try `vscode://` first, then `claude-focus://` on failure (or fire both — the OS handler is a no-op when the window is already foreground). Either way involves a small change in `experiments/visualizer/index.html` click handler.

Old-format sessions (last hook fired before S037's chain capture) have only `claude_pid`, no chain. Either send a prompt in them or spawn fresh ones.

**Step 2 — Verify S031's lane-based bubble layout** (carried from S031). Open the visualizer in live mode and trigger a multi-sprite cluster (2–3 dwarves at the same building, or Jebrim + dwarves at quest-hall). Watch:

- Each bubble in the cluster appears in its own X lane above the cluster, not stacked vertically at the cluster center.
- Each bubble's thought-trail (the 4 cream-fill circles) runs diagonally from its own sprite to its own bubble.
- No trail circle crosses another bubble's rect (the trail layer is BELOW the bubble layer, but visual confirmation needed).
- Single-bubble cases still place the bubble directly above the sprite (cluster.length === 1 branch).
- Inter-cluster fallback: two clusters near each other (e.g., quest-hall and keepsake-vault both populated) still resolve via the upward push.
- Clusters near map edges — leftmost/rightmost bubbles should not clip the viewBox.

Failure mode to watch for: when `xOff` is small (sprites very close in X), the diagonal is almost vertical and trail circles overlap on the diagonal — may look identical to pre-lane version. Acceptable.

Fallback knobs: PAD (currently 12), CLUSTER_RADIUS (currently 140), STOPS array in renderIntent's trail.

**Step 3 — Live test penguins** (carried from S030). Spawn a penguin from a Jebrim session with a small research brief (e.g., *"current state of polars 0.20 changelog"* or *"EU CBAM effective date and applicable goods"*). Watch:

- Task tool with `subagent_type: "penguin"` routes through ROLE_CONFIG; spawn-penguin event lands with id `P1`, color `penguin-1`, at parent's building or iceberg fallback.
- Penguin sprite renders at the Iceberg — tuxedoed silhouette, scarf in arctic blue, ID badge "P1". COMMS shows the PENGUINS tab.
- Write attempts: penguin can write to `players/jebrim/research/<YYYY-MM-DD>-<slug>.md`; any other write path blocked by `penguin-write-boundary.py`.
- Despawn after Task completes; idle GC (1h) via shared `gc_stale_subagents` machinery.

Failure modes: iceberg STAND too close to map edge, tint contrast against dark map background, ROLE_CONFIG generalization breaking dwarf/gnome paths (regression check).

**Step 4 — Live test parallel Braindead** (carried S029, *partially validated*). Cross-session validation happened naturally during S032 — three Braindeads (S032/a989e89a, S031/f39b5b3f, S030/ab5ad0df) ran concurrently and the visualizer + comms channel held up. **Remaining: tint-2 hue-rotate visual check, instance-badge position, gather-slot offset at the workshop when two crews stand there.**

**Step 5 — Cross-repo sidecar rollout (D-020 follow-up).** To get true cross-machine session visibility, move the status-sidecar hook registration from `brain/.claude/settings.json` to `~/.claude/settings.json` (user-level). The status file path is already designed for this; only the registration needs to migrate. Separate decision — sanity-check Step 1's lower-frequency design first.

**Step 6 — D-020 Phase 3 (VS Code click-to-focus).** ~~Deferred.~~ Built across S037 (OS-level handler, cross-window) and S038 (extension, in-window). S038 is live-confirmed; S037 still pending a real two-window scenario (see Step 1b). The window-title-matching plan in the original design didn't pan out (`$Host.UI.RawUI.WindowTitle` in VS Code's integrated terminal sets the *tab* title, not the *window* title); pivoted to process-tree walk via `CreateToolhelp32Snapshot` for the OS path, and to `vscode.window.terminals` + `terminal.processId` matching for the in-window path. **Remaining: D-020 doc update** covering both halves — §"Hook wiring" registration shape, §"Phase build order" Phase 3 done, new §"Process tree walk" subsection (S037), new §"In-window focus via extension" subsection (S038, including the `claude_pid_chain` matching rationale).

**Step 7 — Live test Guthix end-to-end** (carried from S028, extended by [[S034]]). Replay-mode demos worked; live-mode demo still pending for both modes:

- **Consultation** ([[D-022]] / [[S034]]). Address `Hey Guthix, what do I have on EU Tender 2026 across the brain?` or similar. Observe: `guthix.txt` intent file written, spawn-guthix event fires, Guthix sprite appears at lorebook-library, answer comes back in Guthix voice, **no writes to globals or per-player layers**, no quest-log entry unless conversation produces something worth surfacing. The consultation→bankstanding flip: start in consultation, mid-chat say "ok, let's bankstand on this", observe write authority widening and `B-NNN` landing on close.
- **Bankstanding** (carried). `let's bankstand` from a player session; full ritual through Phase 0 + global synthesis.

**Step 8 — Subtask debounce decision** (carried from S028). Default to no debounce if bubble stays alive without strobing.

**Step 9 — Replay-mode demo arcs** (carried from S028). Subtask + Guthix demos + parallel-Braindead in EVENTS.

**Step 10 — Drafts triage** (long-carried S018 → S027):

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md`.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md`.
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` (Jebrim alching).
- `gielinor/players/jebrim/niksis8_character/drafts/`.

**Step 11 — Audit follow-up notes** (carried S027):

- `bank/decisions/`: *recon dwarves should cross-check audit findings against intervening commits before bundling.*
- B1 day/night cadence — 87s/day may be too fast.
- B9 hook D-018 read race.

**Step 12 — First live gnome spawn** (carried S020+).

**Step 13 — Q-008 visualizer aliveness pick** (carried). S028 subtask + S029 parallel-instances + S031 thought-trails subsume some of this; remaining urgency lower.

**Step 14 — Recover Jebrim session 58f8e88a** (carried from S028). Probably resolves itself on next respawn of that session.

## Open at the start of next session

- **S040 live observation** — first session that captures via `note this idea: …` is the real test. Watch (1) does the trigger fire mid-message or only at start? (2) does the active actor resolve correctly across mode transitions (player→Guthix, Braindead-from-gielinor, unscoped capture)? (3) does the listing surface group cleanly when there are entries from multiple actors? Tighten `brain/ideas/_about.md` if any misfire.
- **S039 live observation** — confirm the cascading resolver + write-time refresh hold up across a full day of parallel sessions; spot any session that lingers at `unknown` to learn whether the fallback chain has gaps. The visual ghost period (sprites at old instance numbers) should clear within 5 min of S039's compaction.
- **Lorebook draft pair (Windows substrate gotchas)** — S032 hook-fire-rate-as-budget + S037 ASCII-PS for `.ps1` + S039 BOM-free encoding for JSON written from PS. Three lessons that compose into one draft. Carried for next bankstanding.
- **Lorebook draft (deferred-branches debt)** — S039's instance-monotonic comment + S029's D-017 deferred branches surface a pattern: comments noting "we chose not to do X" become user-visible bugs on their own timeline. Worth one draft.
- **Cross-window click-to-focus** — Step 1b. Wire the `vscode://` → `claude-focus://` fallback chain in the switchboard click handler, then live-confirm against a second VS Code window. Defer until the principal actually opens one.
- **D-020 doc update** — §"Hook wiring" + §"Phase build order" + §"Process tree walk" (S037) + §"In-window focus via extension" (S038). Do this before the next D-020 surface lands.
- **Verify S031 lane-based bubble layout** — Step 2. Still untested visually.
- **Live test penguins** — Step 3.
- **Parallel Braindead visual tuning** — Step 4 (function validated by S032).
- **Cross-repo sidecar rollout** — Step 5.
- **Live test Guthix** — Step 7 (now covers both consultation [[S034]] and bankstanding).
- **Subtask debounce** — Step 8.
- **Replay demos** — Step 9.
- **Drafts triage** — Step 10.
- **Audit follow-ups** — Step 11.
- **First live gnome spawn** — Step 12.
- **Q-008 pick** — Step 13.
- **Jebrim 58f8e88a recovery** — Step 14.
- **`ensureActorExists` braindead-{sid8} suffix-strip miss** — small follow-up from S031. Console shows `visualizer: ensureActorExists has no spawn path for actor braindead-ed610cbe`. Find the path that didn't strip; align with `NON_PLAYER_SUFFIX_ACTORS` from S028.
- **Dead code from S031 cleanup** — `updateDayNight()` / `dayNightFill()` / `DAY_NIGHT_ANCHORS` / `currentHour()` in `experiments/visualizer/index.html`. The `#day-night` rect they target was deleted in S031; JS no-ops via `if (el)` guard. Sweep next bankstanding pass.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

> **SNNN-collision note (2026-05-22).** Two dev-brain sessions named themselves `S038`: this file's brain-underutilization work and a parallel vscode-claude-focus session. The close-session SNNN-determination is racy across truly parallel sessions — whoever closes first grabs the lower number; whoever closes second sees the lower number is taken and bumps, but only if their close-session ran *after* the first commit landed. Mine and the parallel one collided. Both committed under "S038" subjects already; renumbering after the fact is invasive. **Surfacing for bankstanding** — either ratify a sub-suffix convention (`S038a`, `S038b`) or extend close-session SNNN-determination to walk *recent commit history* in addition to `quest-log/`, since closed-quests get committed before they show in any `find` walk. Below, S038 entries are disambiguated by topic-suffix in the label.

From [[S038]] brain-underutilization (new): **frame ≠ root cause.** Jebrim's "promotion gate stalled" was correct as a symptom but missed the load-bearing bug — promoted knowledge wasn't loading because respawn read `current.md` instead of the folder. 12 confirmed entries had been sitting invisible. The symptom *felt* like tempo (promote step is heavy, doesn't happen); the root was structural (even when promotion ran, the load surface was wrong). **Discipline:** when a complaint reads as habit/tempo, look for a structural bug underneath before retraining habits. Generalizable to any "X is underused" diagnosis — check whether X is *reaching* the load surface at all before concluding X needs more invocations.

From [[S038]] brain-underutilization (new): **manual aggregation steps that nobody owns rot.** Identity layers were built assuming someone curates `current.md` from `confirmed/` entries. No ritual owned that step. Fix wasn't "add a ritual that aggregates" — it was "read the folder directly, make `current.md` optional." **Design pattern:** load surfaces should match write surfaces; manual reshape steps between them decay. When a discipline rule requires manual aggregation, the right fix is usually to remove the aggregation requirement, not to add a ritual that does it.

From [[S038]] brain-underutilization (new): **recon dwarves report stale snapshots.** D1 said 5+ ready drafts; on-disk reality was 3. D2 referenced an `S034_g2` quest that existed but was untracked (so it appeared in `??` not in the in-progress `ls`). The brain moves between sessions; dwarf recon ages between task start and report time. **Discipline:** ground-truth dwarf counts before acting on them — re-glob the actual file state. Pair with the S027 "recon dwarves should cross-check audit findings against intervening commits before bundling" carryover; same family of lesson.

From [[S038]] brain-underutilization (new): **structural fixes before habit retraining.** Phase 1 was three structural fixes (respawn reads folder; promote drafts; move stale-done quests). Phase 2 was four habit-shaping aids (`/drafts`, close-session step 4 scan, step 8 catch, Guthix heuristic). **Order:** fix the bug that lets the habit fail, then add the habit-shaping aid. Structural fixes are cheaper and don't drift; habits drift. Reverse order leaves the bug in place + adds heuristic that fires against a broken surface.

From [[S038]] brain-underutilization (new): **the brain's own underutilization was the test fixture for diagnosing the brain's own underutilization.** This session reached for Jebrim instead of Guthix for a system-scope question. The Guthix routing heuristic shipped in 2d is born of literally this conversation mis-routing itself. **Meta:** when designing a heuristic to surface an underused option, look for whether the heuristic's design conversation itself reached for that option. If it didn't, you have a proof case for shipping the heuristic.

From [[S038]] brain-underutilization (new): **cascade approvals when proposing many small writes.** Initial over-gating ("approve per-file") was corrected on principal cue ("thats too blocking"). The right shape for many small writes: ask once for the cascade ("go all"), reserve per-item approval for identity-shaping decisions. Aligns with the elicitation-with-default-surfaced skill we promoted this same session — the skill was load-bearing the moment it shipped.

From [[S038]] vscode-claude-focus (new): **"works in the log" ≠ "user saw it work" — twice in two sessions.** S037 closed on `SetForegroundWindow True` self-tests without checking the user's actual window topology. S038 vscode-claude-focus found click-to-focus was a no-op end-to-end because all sessions share one workspace HWND. The mechanism wasn't wrong; the deployment shape was untested. **Discipline:** a focus/navigation feature must be tested against the user's actual topology, not the design's assumed topology. Pair with the S037 ASCII-PS lesson and the S032 hook-fire-rate lesson as a combined Windows-substrate lorebook draft.

From [[S038]] (new): **OS-level URL schemes hit a ceiling at the window boundary.** Application-internal objects (VS Code terminal panes) have no HWND — `SetForegroundWindow` can't reach them. Protocol handlers (cross-application / cross-window) and extensions (in-application) compose cleanly: handler for the outer layer, extension for the inner. The two URL schemes (`claude-focus://` + `vscode://niksis8.claude-focus`) coexist in the codebase without conflict; chaining them on click is the obvious next move when the principal opens a second VS Code window.

From [[S038]] (new): **`claude_pid_chain` is the right matching surface, not a single PID.** VS Code's `terminal.processId` exposes the shell PID (chain depth ~3 on this machine). Hook fires from deeper. Matching against the whole chain absorbs the depth asymmetry. The chain-capture-at-fire-time pattern from S037 paid off again, for a different reason — generalize: *if you'll need to match a process tree later from a possibly-distant vantage point, capture the whole chain at write time.*

From [[S037]] (new): **Windows PowerShell 5.1 reads `.ps1` files as cp1252 unless a UTF-8 BOM is present.** A single em-dash in a `Write-Log` string broke the parse — the three UTF-8 bytes got read as three cp1252 characters, swallowing the closing quote and cascading errors through the rest of the file. **Discipline: pure ASCII for `.ps1` scripts, or write with UTF-8 BOM.** Worth a lorebook draft paired with the hook-fire-rate-as-budget lesson (both Windows substrate gotchas).

From [[S037]] (new): **walking the process tree at hook fire time is the right shape for "I need an ancestor PID later" on Windows.** `os.getppid()` from a hook subprocess points at a short-lived wrapper (two layers of `bash.exe` on this machine) that exits seconds after the hook returns. `Get-Process -Id <dead>` returns nothing; PIDs may get recycled. Capturing the full ancestor chain *while everyone is still alive* via `CreateToolhelp32Snapshot` sidesteps all of it. Same pattern fits other instrumentation that needs to retain process-tree facts across time.

From [[S037]] (new): **"it works in the log" ≠ "the user saw it work."** First user feedback was "still just opens a terminal" — the focus mechanism was correct end-to-end, but with one VS Code window the visible effect was zero. Build the visible-effect setup *into the test plan*, not after.

From [[S037]] (new): **the conhost flash is the protocol handler's tax, not a script bug.** Browser-triggered local actions via a URL scheme always flash a conhost briefly even with `-WindowStyle Hidden`. Plan for it explicitly; suppression would require switching the handler to `wscript.exe` or a compiled launcher.

From [[S034]] (new): **a four-bullet refusal list is a signal that the actor's role is too narrow.** Guthix's pre-S034 "What he refuses" had four items; post-S034 it has one ("won't write into a player's house"). When an actor declines a category of work, ask whether the role definition is the cause before defending the boundary.

From [[S034]] (new): **"consultation default, ritual on cue" is a reusable shape.** Same actor, two modes, write authority varies by mode. If a second deity ever shows up, the precedent now sits in the meta files. Don't generalize prematurely — but the shape is there to inherit.

From [[S034]] (new): **the principal's mental model is the architecture, even when it's an addition.** The shift had to land in the doc surfaces the agent reads at session start (`CLAUDE.md`, `modes.md`, `guthix.md`), not internal discipline alone. A purely-discipline change would have evaporated by next session because the address-routing rules would still describe the old role.

From [[S034]] (new): **wisp's role evolution is the same pattern as the S028 split, one degree further.** S028 took the system-curation half away from wisp; S034 takes the general-question half away too. Pattern: when an actor does multiple unrelated jobs, expect to split each off in sequence, not at once. Final wisp = "blank session opener," nothing more.

From [[S032]] (new): **high-frequency hooks on Windows + VS Code's integrated terminal are a hazard, even when silent.** `status-sidecar.py` was added at 2N+3 fires per turn without a frequency budget check against `emit-event.py`'s ~N rate. The added rate didn't cause the specific terminal-corruption incident this session (disabling didn't fix it), but it widened the surface for timing-sensitive renderer bugs. Treat hook-fire rate as a constrained resource on this substrate. Worth a lorebook draft.

From [[S032]] (new): **decoupled hook scripts pay off in failure isolation.** Pausing one script's registrations didn't disturb the other; the visualizer kept running through the diagnosis. The "shared file, separate processes" pattern is strictly better than "one script does everything." Phase 3's window-focus helper, when it lands, should also be a separate script.

From [[S032]] (new): **status sidecar is a strictly stronger sibling-liveness signal than intent-file mtime.** At respawn I flagged ab5ad0df as a `ABANDONED` candidate (intent-file 9min stale); the sidecar showed them very-much-alive. The comms ritual's sibling-detection check ([[D-019]] §3) could swap to `status state ≠ ended AND last_event_ts <5min` once the sidecar stabilizes — strictly stronger.

From [[S032]] (new): **"cross-repo visibility" is a registration question, not a file-path question.** Putting status files at `~/.claude/status/` was correct, but only sessions whose hook *fires* can populate the dir, and the hook only fires for sessions whose settings.json includes it. The visibility scope is the *intersection* of "where the file lives" and "where the hook runs"; the latter binds.

From [[S032]] (new): **Guthix mode bridges naturally into dev-brain construction.** The principal opened with `Hey Guthix` outside of bankstanding, got a design, then pivoted into dev-brain to build it. The design memory carried via chat, not a bankstanding `proposals/` entry. Not a problem — just a transition pattern. Document if it recurs.

From [[S031]] (still relevant): **browser cache can hide a fix and read as a bug not fixed.** Ask for hard refresh sooner when the user reports a fix didn't take.

From [[S031]] (still relevant): **CSS source-order trumps specificity for same-class rules.** Edit the original rule when overriding, don't pile on.

From [[S031]] (still relevant): **scaling a world is mostly mechanical, but the gotchas live in the inline literals.** Wrap dense decorations in a single `transform="scale(N)"` when their internal coords are dense.

From [[S031]] (still relevant): **a separate SVG layer for connectors lets you stack-paint cleanly.** When element A should "live behind" B but is owned per-instance, put A in its own layer rendered before B.

From [[S031]] (still relevant): **"design tradeoff" answers are sometimes the deliverable.** Three-option answers with knowable tradeoffs cost ~30 lines but bound the implementation once the option is picked.

From [[S030]] (still relevant): **discipline rules pay off when consulted.** The `players/_about.md` "don't pre-create speculative players" rule routed work to the right shape (skill + sub-agent role, not new player).

From [[S030]] (still relevant): **predictive comments in code pay off.** `emit-event.py` line 65's "generalize to a mapping if a third kind lands" became a checklist two sessions later when penguins landed.

From [[S030]] (still relevant): **source vs picking — research/bank split.** Research as source material, bank notes as picked claims; picking-during-alching operationalizes the split.

From [[S030]] (still relevant): **five-chunk bundle held together because of pre-flight survey.** For large bundles: read the cascade before writing.

From [[S029]] (still relevant): **D-017's deferred branches age fast.** D-NNN docs with "out of scope for first cut" sections accumulate latent work on a slower clock. Bankstanding could surface deferred-branches-over-30-days. **Met again in S032** — D-020's Phase 3 is already a deferred branch; how long will it sit?

From [[S029]] (still relevant): **coordination is asymmetric across actor classes.** Each new instanced actor warrants a separate decision about coordination.

From [[S029]] (still relevant): **append-only files dodge concurrent-write design entirely.** The principle is wider than the comms channel.

From [[S029]] (still relevant): **"seems ambitious" reads as a green light, not a hedge.**

From [[S028]] (still relevant): **subtask exposes architecture/intuition mismatches that quieter channels papered over.**

From [[S028]] (still relevant): **silent suffix-strip bugs hide until the surface gets busy.**

From [[S028]] (still relevant): **the "bare intent file" fallback was never load-bearing — only confusing.** Worth a lorebook draft on *"defaults that exist only for absent inputs accumulate hidden coupling — prefer a hard surface."*

From [[S027]] (still relevant): **recon dwarves should cross-check audit findings against intervening commits before bundling.**

From [[S027]] (still relevant): **a multi-fix audit pass converts the audit doc from a primer into a verification checklist.**

From [[S023]] (still relevant): **shared global state at brain root is hostile to parallel Claude sessions.** Cumulative incident pattern spans S014, S022, S023, S027, S028, S029, S032.

From [[S023]] (still relevant): **watching-it-run finds bugs the audit-and-validate phase missed.**

From [[S022]] (still relevant): **audit-then-validate finds different bugs than either alone.**

From [[S021]] (still relevant): **the audit-then-validate pattern works for accreted infrastructure.**

From [[S021]] (still relevant): **cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.**

From [[S020]] (still relevant): **architectural guarantees need a live failure test, not just code review.**

From [[S020]] (still relevant): **the claude-code-guide agent earned its spawn.**

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.**

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.**

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.**

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.**

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.**

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now twelve-incident pattern with S018, S020, S022, S023, S027, S028, S029, S032): **the procedure was right; the procedure assumed a state that didn't exist.**

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.**

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file).
2. `quest-log/S038_vscode_claude_focus_extension.md` — what just shipped (in-window terminal-pane focus via VS Code extension).
3. `experiments/vscode-claude-focus/extension.js` + `README.md` — the new extension; ~70 lines of JS plus install/verify notes.
4. `quest-log/in-progress/S037_terminal_switchboard_phase_3_click_to_focus.md` — the OS-level half S038 complements (still in in-progress because its own self-test passed but the multi-window scenario it targets hasn't been lived against).
5. `quest-log/S034_guthix_consultation_mode.md` — Guthix two residence modes; doc-only across nine `gielinor/` files.
6. `bank/decisions/D-022_guthix_consultation_mode.md` — full decision including before/after table, open questions.
4. `gielinor/meta/guthix.md` — the load-bearing spec post-S034 (two residence modes; consultation as default).
5. `gielinor/meta/modes.md` — five session modes definition; consultation block.
6. `quest-log/S032_terminal_switchboard_phases_1_and_2.md` — prior session: Phases 1 + 2 of D-020, terminal-rendering diagnosis.
7. `bank/decisions/D-020_terminal_switchboard.md` — full design including state machine, contract, phase order, open questions.
4. `.claude/hooks/status-sidecar.py` — the sidecar script (currently only registered on SessionEnd).
5. `brain/.claude/settings.json` — see the `_comment_status_sidecar` note explaining the paused registrations.
6. `experiments/visualizer/index.html` — Phase 2 sidebar lives here. Search `class="switchboard"` for markup, `class=".sb-` for CSS, `initSwitchboard` for JS.
7. `experiments/visualizer/state-switchboard.json` — the snapshot manifest the browser polls.
8. `comms/active.md` — recent OPEN/UPDATE/CLOSING entries (S030/S031/S032 ran in parallel; the channel got real-world traffic).
9. `quest-log/S031_visualizer_world_scale_layout_and_bubble_redesign.md` — visualizer overhaul; lane layout still untested (Step 2).
10. `quest-log/S030_penguins_subagent_and_research_folder.md` — penguins, still untested live (Step 3).
11. `quest-log/S029_parallel_braindead_and_comms_channel.md` — parallel sessions design, mostly validated in S032.
12. `bank/decisions/D-019_parallel_braindead_and_comms_channel.md` — full design including open questions.
13. `comms/_about.md` — coordination layer protocol.
14. `spellbook/respawn-ritual.md` + `spellbook/session-close.md` — entry/exit rituals with sibling detection + comms steps.
15. `.claude/hooks/emit-event.py` — visualizer hook (untouched in S032; reference for the high-frequency-hook lesson).
16. `bank/decisions/D-017_parallel_player_instances.md` — parent decision for instance routing.
17. `bank/decisions/D-018_parallel_session_substrate_isolation.md` — the per-session intent-file mandate.
18. `bank/decisions/D-021_penguins_research_subagent.md` — penguin design.
19. `gielinor/meta/guthix.md` — bankstanding deity (relevant to the S032 origin story).
20. `bank/open-questions/Q-008_visualizer_aliveness.md` — parked.

## Note on the visualizer's engine

Untouched in S032. The Phase 2 sidebar layered as a third flex child of `.world` and a self-contained IIFE poller; engine surface (event timeline, applyEvent dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is unchanged. The sidebar reads a separate JSON file via its own fetch; doesn't touch `state.ndjson` or any of the existing visualizer state files. Keep extending; don't rewrite.

New events in S032: none — the switchboard channel is orthogonal to the visualizer's event stream.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then `http://localhost:8765/?live=1`. Append `&sid8=<your-sid8>` to highlight "this" session with a gold outline in the new switchboard pane. For parallel-Braindead testing, open two Claude Code windows at brain/ root.
- **Switchboard reads.** Lives at `~/.claude/status/<sid8>.json` (per-session) + `~/.claude/status/archive/` (>24h-old, swept). The visualizer's mirror snapshot lands at `experiments/visualizer/state-switchboard.json` on every sidecar fire — currently only `SessionEnd` fires. To stress-test the sidebar with live data, decide Step 1.
