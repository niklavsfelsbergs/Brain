# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-22 (end of [[S032]] — terminal switchboard, D-020 Phases 1 + 2). **Sidecar registrations partially paused after a terminal-rendering incident — Step 0 decides whether to re-enable on a lower-frequency design or leave parked.**

## Where we are

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

**Step 0 — Open a fresh VS Code terminal.** The current terminal's render state is corrupted (DEC Special Graphics escape sequence stuck without reset). Close the broken tab, open a new one with `` Ctrl+Shift+` ``. The corruption is Claude Code's chat-stream rendering only; shell commands and file I/O are unaffected. **Confirm before doing other work** that Claude Code text renders cleanly in the new terminal.

**Step 1 — Decide the status-sidecar registration shape (D-020 Phase 1 wrap-up).** Three options:

1. **Re-enable with lower-frequency design (preferred).** Register for `UserPromptSubmit` + `Stop` + `SessionEnd` only. Three fires per turn instead of 2N+3 — well below `emit-event.py`'s rate. UserPromptSubmit sets `state=working` at turn start; Stop sets `state=waiting_for_user` at turn end; SessionEnd sets `state=ended`. Loses per-tool-call age granularity but the switchboard UX only needs turn-resolution freshness.
2. **Leave fully paused.** Sidebar would stale-out quickly because only SessionEnd fires; useful only as a "session-ended log." Unsatisfying.
3. **Revert further** — remove the SessionEnd registration too, and consider whether the sidecar wants a different transport (e.g., periodic batched write driven by a single long-running process rather than per-event subprocess spawns).

Recommendation: **option 1**, with the lesson codified in [[D-020]] + a lorebook draft.

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

**Step 6 — Phase 3 of D-020 (VS Code click-to-focus).** Deferred until Phase 2's UX is lived-with for a week. If alt-tab from the sidebar list proves sufficient, Phase 3 stays unbuilt. If not, the "one-VS-Code-window-per-session" convention flavor is the lowest-effort path — set `$Host.UI.RawUI.WindowTitle = "claude-$sid8-<actor>"` in `$PROFILE`, then a PowerShell helper using `user32.dll`'s `FindWindow` + `SetForegroundWindow` brings the matching window forward on row click.

**Step 7 — Live test Guthix end-to-end** (carried from S028). Replay-mode demos worked; live-mode demo of `Hey Guthix` + `let's bankstand` still pending.

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

- **Fresh terminal first** — Step 0. Confirm Claude Code text renders cleanly before anything else.
- **Sidecar registration shape decision** — Step 1.
- **Verify S031 lane-based bubble layout** — Step 2. Still untested visually.
- **Live test penguins** — Step 3.
- **Parallel Braindead visual tuning** — Step 4 (function validated by S032).
- **Cross-repo sidecar rollout** — Step 5.
- **D-020 Phase 3 click-to-focus** — Step 6 (deferred, decide after living with Phase 2).
- **Live test Guthix** — Step 7.
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
2. `quest-log/S032_terminal_switchboard_phases_1_and_2.md` — what just shipped (Phases 1 + 2 of D-020, with the terminal-rendering diagnosis).
3. `bank/decisions/D-020_terminal_switchboard.md` — full design including state machine, contract, phase order, open questions.
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
