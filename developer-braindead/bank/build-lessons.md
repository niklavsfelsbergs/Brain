# build-lessons.md — carried build wisdom (relocated from respawn.md)

> Relocated from `respawn.md`'s tail on 2026-05-24 (token-usage audit) so it stops
> costing ~50k tokens of session-start load on every dev respawn. This is reference
> material — read on demand, **not** loaded at respawn (per `spellbook/respawn-ritual.md`
> step 4: "Don't pre-load `bank/`").
>
> Cross-session lessons distilled at each session close. An individual lesson can
> graduate to `examine/I-NNN_*.md` (the dev self-model) during a bankstanding/reflection
> pass — that's the canonical home for a durable insight. Until then they live here as a
> digest. The "Open at start of next session" carry-list below is a historical snapshot
> (S072); the live next-steps moved to respawn.md.
>
> Everything below this line is verbatim from respawn.md's tail as of S072.

---

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
- ~~**`ensureActorExists` braindead-{sid8} suffix-strip miss** — small follow-up from S031.~~ Obsolete — `ensureActorExists` removed with the map in S052.
- ~~**Dead code from S031 cleanup** — `updateDayNight()` / `dayNightFill()` / `DAY_NIGHT_ANCHORS` / `currentHour()` in `experiments/visualizer/index.html`.~~ Obsolete — file moved + map code excised in S052.
- **Cleanup pass on `developer-braindead/experiments/visualizer/`** — post-S052 dead-weight inventory: `sprites/` (PNG sprite sheet + slices), source PNGs, `slice.py`, `slice_tileset.py`, `subtask_smoketest.py`, plus the sibling `experiments/vscode-claude-focus/` extension. First four are pure map-era artifacts; `subtask_smoketest.py` is orphan tooling; `vscode-claude-focus/` is a separate VS Code extension that may still be relevant (in-window click-to-focus from S038). Decide per-item — archive sprites + slice scripts, retire `subtask_smoketest.py` to archive, promote or retire `vscode-claude-focus/`. Bankstanding territory; never delete.
- **Simplify `emit-event.py` path classifier.** `path-map.json` carried over to `switchboard/` but is now vestigial — only the hook's classifier reads it to humanize file paths into building names, and no map renders. Either drop the classifier (emit raw paths to chat.ndjson) or repurpose path-map as a chat-prose helper. Defer until the chat humanizer's first real-use pass surfaces what's needed.
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
