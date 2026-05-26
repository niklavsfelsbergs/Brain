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

From [[S098]] (new): **Obsidian is a lens over a vault we already are — but stock Obsidian resolves `[[ ]]` by *exact filename*, so the `[[ID]]` convention ([[D-004_stable_ids]]) renders ~91% of links phantom until migrated to full-stem.** Adoption = per-brain vaults (a single combined vault manufactures cross-brain `D-NNN` collisions that per-vault scoping avoids). Spec: `bank/research/obsidian-fit-and-migration-spec.md`.

From [[S098]] (new): **model the resolver, don't eyeball the GUI.** To answer "will Obsidian even resolve our links," I replicated its resolution rules (exact-filename / shortest-path / aliases-not-honored) in a script and counted against all ~1,130 links — authoritative + repeatable, no GUI. Instrument-don't-guess applied to a "will it work" question, not just a "why did it break" one.

From [[S098]] (new): **name your modelling assumption — the topology *was* the answer.** First pass modelled one combined repo-root vault → "9% resolve, 91% broken" (alarming). Principal corrected: the brains are per-vault scoped → 71% clean. A 10× swing from one unstated assumption (the vault boundary). State the assumption before reporting the number.

From [[S098]] (new): **don't mistake convention for debt.** The "ambiguous" links were almost all deliberate structure — sub-agent run-logs (`SNNN_dN/_pN/_gN`) and quest+resume pairs share the session ID *by design*. Renumbering them would have shattered the filing system. Verify what a "collision" actually *is* before proposing a cleanup.

From [[S098]] (new): **evaluate a rule on whether it still pays rent, not its age.** I treated [[D-004_stable_ids]] ("short ID alone is canonical") as a blocker on reflex; principal pushed — early decision, does it actually stand in the way? It didn't (guarded a near-nonexistent, recoverable slug-rename). Right move: surface the contradiction (don't silently break a founding decision) *and then amend it* — the brain is built for decisions to evolve. (Also → cross-conversation memory `evaluate-rules-pay-rent`.)

From [[S098]] (new): **a mechanical convention-rewrite corrupts the doc that *describes* the convention.** My full-stem script ran over the spec doc's own illustrative `[[D-027]]` examples (Option A/B went identical) — caught in diff review. The exclude-list for any syntax-rewrite must include the spec + `_about` + `entry-formats` + historical decision records. And: a link-TEXT rewrite ≠ a file rename — only the latter threatens the hook/cockpit filename parsers, so don't price them the same.

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

From [[S032]] (new): **status sidecar is a strictly stronger sibling-liveness signal than intent-file mtime.** At respawn I flagged ab5ad0df as a `ABANDONED` candidate (intent-file 9min stale); the sidecar showed them very-much-alive. The comms ritual's sibling-detection check ([[D-019_parallel_braindead_and_comms_channel]] §3) could swap to `status state ≠ ended AND last_event_ts <5min` once the sidecar stabilizes — strictly stronger.

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

From [[S083]]: **when N attempts at the same *parameter* fail identically, the bug is elsewhere — stop varying it, instrument.** Shift+Enter burned 6 sessions cycling the newline BYTE (`\n`, `\x1b\r`, `\\\r`, CSI-u, bracketed-paste) — all submitted. The byte was never wrong (`\n`/Ctrl+J is correct per the docs); xterm's `return false` wasn't stopping the hidden textarea from ALSO emitting a `\r`. `e.preventDefault()` fixed it on the first try after we got authoritative info + added a keystroke diagnostic. The (N+1)th move after repeated identical failures should be research + instrumentation, not guess N+1.

From [[S083]]: **no hook fires on a Claude Code Esc-interrupt** (Stop fires only on natural completion; no `UserPromptCancel` event — issues #45289/#9516). Any hook-based "busy" stamp sticks forever on a cancelled turn. For *interactive* state, use the signal you actually have rather than a timeout: the cockpit can't see a hook but it CAN see the Esc keystroke in its own PTY terminal → clear busy→idle instantly, with a timeout-decay (90s) only as the backstop for sessions it can't observe. A "correct" fix that feels slow (the first 90s-only attempt) is still wrong for the user.

From [[S083]] (the regression I shipped, then reverted): **a documented tradeoff is not a verified-acceptable one — and a heuristic that infers intent from absence-of-signal is the wrong tool when a ground-truth signal exists.** For "cancelled turn sticks at BUSY," the precise fix was the cockpit seeing the Esc keystroke (ground truth → instant clear). I *also* shipped a backend 90s timeout that decayed any heartbeat-silent busy→idle, writing off its false-trip in my own commit as "soft, self-correcting" — with zero evidence it was rare. It instantly false-tripped a live Jebrim session genuinely working (long think / long MCP query showed IDLE). Lesson: a self-named failure mode is a BLOCKER until evidenced rare; don't bolt a redundant guess onto a precise signal; be extra-conservative changing how *live* sessions are displayed (a false signal on real work erodes trust worse than the annoyance being fixed). The keystroke fix should have stood alone.

From [[S083]]: **autonomous work without the ability to verify = prove the testable layers, instrument the rest, don't churn load-bearing untestable code.** With no GUI eyeball, the wins were: a 32-assertion backend regression gate + a headless aiohttp route smoke (proved the data/server layers), a gated `window.__TERMDIAG` instrument for the visual unknowns, and *deliberately not touching* the just-stabilized S080 manifest/PID gate or the high-blast-radius ptybridge UTF-8 path (untestable blind). Hand off with a precise relaunch checklist + a build-tag breadcrumb (`b83.N`) so the principal can confirm fresh code loaded.

From [[S084]]: **a UI indicator that *never* shows is a match-predicate bug, not a styling weakness — check the identity types in the compare before restyling.** The principal reported "nothing shows which session is open." The selected-row CSS existed but was faint, so the obvious read was "make it pop." Root cause was deeper: `board.js` matched `s.session_id === sel.id`, but `sel.id` is the **8-char sid8** for a PTY `TermConn` (`term.js` sets `this.id = f.sid8`; server sends `session_id[:8]`) while a peek's `.id` is the **full UUID** — so `.selected` could never apply to cockpit-driven sessions (the common case). The cockpit's sid8-vs-full-session-id duality is a recurring footgun (it also shaped the `/rename` + focus plumbing); when a value flows through both connection kinds, normalize to sid8 (`id.slice(0,8)` works for both) at the boundary. Fix the predicate first, *then* style.

From [[S085]] (the receipt for [[S020]] + [[S015]]): **the six "architectural guarantees" were not enforced at brain root — proven by an `rm` that went through.** All six boundary hooks were wired ONLY in `gielinor/.claude/settings.json` via `${CLAUDE_PROJECT_DIR}`; a session opened at brain root (the *default* per CLAUDE.md, AND what the cockpit launches with `cwd=brain root`) loaded only `brain/.claude/settings.json`'s observability hooks. So the guarantees the docs call unbypassable were prompt discipline in the dominant operating mode. S020 said "architectural guarantees need a live failure test, not just code review"; S015 said "delete discipline isn't enforced for dev-brain infrastructure" — both were right and neither was acted on for ~65 sessions. **Discipline: enforcement lives at the intersection of (where the hook script sits) ∩ (which settings.json the session actually loads) ∩ (where the session launched) — verify a guard FIRES from the real launch dir, don't trust the wiring's intent. The cheapest test is to try the thing the guard forbids and watch it get blocked.** Fix: register the boundary hooks in the root settings with absolute paths so they fire repo-wide.

From [[S085]]: **triage an external/automated review against the LIVE code before acting — findings go stale, mis-attribute, and mis-severitize.** Of Codex's two batches: #6 (sel.id vs session_id) was already fixed the same afternoon (S084) — the snapshot predated the fix; #3 was rated High but the blast radius is Medium (gielinor-session-only, niche path); #1 needed *empirical* proof (the `rm` test), not just reading the settings, to separate "looks unenforced" from "is unenforced." An external reviewer is a strong prompt for *where to look*, not a verdict to apply. Recalibrate each finding's severity against your own context, and prove the scary ones with a test rather than a code-read.

From [[S086]]: **for a "documentation" / deliverable ask, settle the output *form* up front — don't default to the source format silently.** Asked to "build full technical documentation," I produced a `docs/` tree of markdown (a fine default — renders on GitHub, links work), scoped audience/home/depth via a 3-choice, and shipped. The principal's next message was "where is the HTML version?" — they'd assumed a browsable rendered artifact, not raw `.md`. The markdown wasn't wrong, but the *form* was an unsurfaced assumption. Discipline: when the ask is a documentation/report/export deliverable, treat the rendered form (raw MD vs single-file HTML vs static site vs PDF) as a first-class scoping question alongside content — the same multiple-choice-with-recommendation I already used for audience/home/depth. Cheap to ask, and "where's the X version" is the tell that a format expectation went unasked.

From [[S087]]: **"nothing's showing" — settle bug-vs-filter by inspecting the live data payload before touching render code.** The principal reported their live Jebrim session wasn't "popping up in the feed." The obvious read was a broken event pipeline. Instead I curled the running backend's `/api/feed` (port 8770) and found the session's events all present — 11 items, all `say`+`action`. A *working* session emits almost only those two kinds (213 of 300 in the live payload), and both are gated behind the FEED panel's `actions`/`prose` toggles (default on, but localStorage-persisted off) — so the symptom was a view filter, not a missing event. Discipline: when a surface "shows nothing," read what the server is actually serving (or what's in the source file/stream) *first* — one query separates "data absent" from "data present, hidden by a client filter/scroll/toggle" and tells you which half of the stack to fix. Application of the existing `instrument-don't-reguess` memory to a diagnostic (not a fix) question.

From [[S092]] (clean-text transcript panel): **to render claude's output as clean content, the source is the transcript `.jsonl` (/history), never the terminal grid — and the structured render for it often already exists for a sibling case.** The principal wanted the cockpit to "not look like a terminal" so output could be *copied cleanly* (xterm is a fixed-width grid: long lines hard-wrap at the column, TUI chrome bakes into cells → selection copies the mangled form). Two wrong instincts dodged: (1) scrape the xterm ANSI and reformat — brittle, it's a repainting TUI; (2) drive headless for a chat UI — that's the metered path ([[S060]]). The right source was the on-disk transcript `.jsonl`, which `backend.parse_transcript`/`/history` already turned into clean structured turns *for read-only peeks* — the driven PTV session simply wasn't wired to it. Build was ~1 new file + a toggle that keeps `<Term>` mounted (hidden) so the PTY/subscription never drops. **Discipline: for "show the agent's output as clean/structured content," reach for the transcript jsonl, not the rendered terminal; and before building a "new" view, check whether the structured render already exists for an adjacent code path (peek) and just isn't reachable from the case you need.** Reinforces [[S017]] (inventory what exists before prescribing DOM) — here the reuse target was a sibling *code path*, not a doc.

From [[S092]] (the "I can't select text" report): **a live/polling view must yield to an active user selection — re-rendering content out from under a drag-select reads as "selection doesn't work."** The transcript polled `/history` every 2s and called `setTurns` on change; the newest turn (the one you most want to copy) grows each poll, so any highlight there was wiped within ~2s. Before blaming CSS I checked the real candidates — `app.py`/styles.css for a global `user-select:none` (only `body.resizing` + scoped xterm), confirming no static block — which pointed at the re-render, not a style. Fix: skip the content swap while `window.getSelection()` has a non-collapsed range inside the panel (defensive `user-select:text` added too, for the chromeless WebView2 case). **Discipline: any auto-refreshing surface the user can select/interact with must pause the DOM swap while a selection is live inside it.** Application of `instrument-don't-reguess` to a UI bug: rule out the static cause (CSS/global block) by reading it before concluding it's the dynamic one (poll).

From [[S092]] (lost rename on close/reopen): **when the identity key can rotate, EVERY store keyed by it needs a carry at the rotation point — and a code comment asserting "it won't rotate" is itself the latent bug.** Renames are keyed by `sid8` in two stores (localStorage via names.js for terminal `/rename`; `state-names.json` on disk for board/VSCode rename). `sid8` is NOT stable: `claude --resume <uuid>` (what a cockpit reopen runs) mints a NEW id — unlike `claude --session-id <uuid>`, which *pins* it. The existing `_carry_name_across_clear` covered only the in-process `/clear` case, only the disk store, and its own comment baked in the false assumption *"a resume reuses the old UUID (same sid8 → label never lost)"* — which is exactly what broke. Fix carried the label across the rotation in BOTH stores: localStorage in term.js's re-announce handler, disk in new `ptybridge._carry_disk_name`. **Discipline: identity keyed by a rotatable value needs carry-on-rotate across all stores, applied where the rotation is detected; and treat an unverified assumption written into a comment as a bug waiting to fire ([[S039]] "comments noting we-chose-not-to-do-X become bugs"; [[S084]] the recurring sid8-vs-full-uuid footgun — same key-identity family).** Substrate fact worth keeping flat: **`--resume` does not pin the session id; `--session-id` does.** *(CORRECTED by [[S093]]: a live trace showed `--resume` KEPT the id — no rotation on resume. This assumption was wrong; see the S093 lesson below.)*

From [[S092]] (the two-fix selection patch): **when you can't isolate which of two plausible causes is real (no GUI to instrument), apply both individually-correct fixes but SAY SO and ask which mattered — don't pass a 2-fix bundle off as one confident fix.** "Can't select" had two live candidates (poll-wipe; chromeless-webview user-select). Both fixes are correct on their own merits regardless of which was the actual cause, so I shipped both — but flagged to the principal that the poll-yield is the likely cause and the CSS is defensive, with a relaunch check to confirm. Nuance on [[S083]]'s autonomous-verify lesson: the honest move under eyeball-blindness isn't to guess one and hope, nor to silently bundle — it's parallel correct fixes + transparent "here's which I think mattered, confirm on relaunch."

From [[S086]] (cockpit compose-bar — the parallel S086, not the docs one): **a second input path onto a stateful surface must reconcile that surface's existing state, not just append to it.** The cockpit terminal compose-bar (a fixed `<textarea>` that pipes text+Enter to the PTY so you can scroll the terminal while writing) blasted its text straight into claude's in-terminal input box — but that box is a *shared* surface. The terminal is focused by default, so the principal had half-typed `dssd` directly into it; Esc cancelled the turn but left `dssd` in the box, and the next composed send prepended to it → a merged message. Fix reused the `_linebuf` mirror term.js already keeps for `/rename`: backspace the leftover away on Esc and before every composed send. Discipline: when you bolt a new input channel onto a surface that already accepts input (PTY prompt + composer; two cursors on one doc), the channels share hidden state — clear/reconcile the surface before writing, don't assume it's empty. Caught by the principal on first live use, which is also the standing reminder that interactive-input bugs surface only in real use — an eyeball-blind build must hand off a concrete "type X then Y" regression repro, not just a feature checklist.

From [[S093]] (rename-on-restart — the SECOND attempt; instrument resolved it): **`claude --resume <uuid>` KEEPS the id, it does NOT rotate — correcting [[S092]]'s premise.** S092 "fixed" lost-rename-on-reopen on the belief that `--resume` mints a new id (so it carried the label prev→cur *on rotation*), and shipped it with the EYES-ONLY relaunch never done. It regressed — the principal reported names still dropping. Rather than guess patch #2, I instrumented the announce/rotation/carry path to a disk log (`switchboard/rename-diag.log`) and had the principal do one restart. The trace was decisive: both resumed sessions announced `resuming:true` with the SAME uuid and produced **zero `rotate` events**. So `--resume` pins the id; the name survives a restart via the stable sid8 + durable localStorage (the board reads `nameFor()` first, disk `state-names.json` as fallback). The earlier breakage was almost certainly the running cockpit window holding **stale code** (a relaunch loads the current `term.js`) and/or lost-name cases that had gone through a `/clear` rotation. I shipped a **resume-anchor carry** (copy the disk label from the resume-uuid's sid8 → the live id) as insurance for the `/clear`-then-restart path, then **stripped the always-on disk logger** once it had answered its question (kept a zero-cost gated `window.__RENAMEDIAG` client trace). **Discipline: (1) read the OVERRIDE flag to infer a default — `--fork-session` ("create a new session id *instead of reusing the original*") is the tell that plain `--resume` REUSES the id; (2) [[S083]]'s instrument-don't-reguess applies *doubly* after an unverified fix regresses — the prior fix's stated PREMISE is the first thing to instrument, not the last; (3) a fix shipped without its EYES-ONLY relaunch ever happening is a guess wearing a fix's clothes — S092 marked "verify pending" and the pending verify is exactly what failed. When the checklist says EYES-ONLY, the work isn't done until eyes are on it.**

From [[S094]] cockpit no-open (new): **diagnostic probes become confounds in the system under test — clean them up.** While diagnosing the cockpit hang as Jebrim I left two `backend.py` probes running, squatting `:8770` — the exact port `app.py`'s reuse-check keys on. They turned into part of the mess I was later debugging as Braindead. **Discipline:** when a debug step spawns a server/process (especially against a port-bound or single-instance app), kill it before moving on, or it pollutes the very thing you're investigating. Verified-fix-vs-isolated-mechanism honesty also applies: I proved the clean slate works, but did NOT separate profile-lock vs port-squat vs stacked-instances under a stack trace — say "fix verified, mechanism inferred," don't dress inference as diagnosis.

From [[S094]] cockpit no-open (new): **a persistent-profile GUI app with no single-instance guard self-DoSes on retry.** The cockpit's `webview.start()` hung with no window and no `msedgewebview2` child — the [[S066]] persistent `.webview` `storage_path` lock-contends when multiple instances stack, and the natural user response to a hang (relaunch via the icon) compounds it: each stuck instance keeps holding/waiting on the profile lock. Killing all `cockpit/.venv` pythons + freeing the port fixed it. **Follow-up (logged in respawn):** the cockpit needs a single-instance guard (if `:8770` is already a *cockpit*, focus the existing window, refuse a second) and/or stale-profile-lock recovery on launch — otherwise one transient hang escalates into a pile-up the user can't escape without Task Manager.

From [[S097]]: **When parked/planned work depends on something the principal is actively doing (a "revamp", a parallel effort), inspect the live session + its artifacts and wire the concrete interlink — don't abstract a live, inspectable dependency into a vague gate.** Anchor: I parked the RAG plan as "gated on the Obsidian revamp" while braindead-b53fca39 was live in a sibling session speccing the exact link-migration my Phase 1 consumes; the principal had to say "check what the obsidian session is doing and enhance with exactly how it interlinks." Sibling-detection at respawn already surfaces these sessions for collision-avoidance — extend the habit to dependency-wiring: when a plan names a dependency a live session owns, read their intent/comms/artifacts and name the concrete coupling (inputs, inherited semantics, ordering).

From [[S095]] (the "textbox stuck" #2 bug, root-caused from a disk trace): **a persisted instrument doesn't just break the reguess loop — it can DISPROVE the obvious hypothesis a bug has been "fixed" against twice.** The recurring prompt-below-fold/"textbox stuck" had an obvious suspect — over-fit — and had been fixed *as* over-fit in [[S083]] and [[S093]]. The honest move (per the `instrument-don't-reguess` memory) was to refuse a third over-fit tweak and instead leave a gated disk-logger (`term-fit-diag.log`) armed across relaunches. When it reproduced, the trace was decisive *against* the assumption: **every healthy sample had `overfit=-16px` (a row of SLACK, not over-fit)**; the only bad samples were `open … frameH=0` — the terminal was selected while the transcript view was up, so it mounted `display:none` and the multi-frame open-pin loop bailed on a 0-box; the single RO re-show pin then raced the layout. Fix targeted *that* (a `reshow()` multi-frame fit+pin on the view-flip), and I explicitly did NOT touch the over-fit guard — the trace proved it innocent. **Discipline: for a bug that keeps coming back after "fixes," the instrument's job is to test the PREMISE, not just locate the next tweak; be ready for it to exonerate the code you'd have changed and point somewhere you weren't looking (here: the hidden-mount path, not the fit math).** Also: keep such a logger ARMED through the verification relaunch (strip only once confirmed) — a one-shot trace you stripped too early can't catch an intermittent "popped up in one session" report.

From [[S095]] (the "I think we introduced a new issue — all sessions lost their name" report): **when blamed for a regression, instrument to CONFIRM-OR-REFUTE before either accepting it or dismissing it — the same investigation usually does both (clears the recent change AND finds the real cause).** The principal attributed the name-loss to my in-flight transcript/compose work. I neither defended nor assumed: grep-proved the rename code path (`names.js`, ptybridge announce/carry, the `term.js` label code) was untouched by my diff (so: not introduced here), AND read the re-enabled rename-diag trace, which showed `--resume` KEEPS the id (zero rotate) — so manual renames always survived — and thereby pinpointed the *actual* gap: the AUTO-label (a placed "Jebrim") wasn't persisted across resume (`resumeTerm` started blank, idle sessions have no hook attribution yet → "chat"). Fixed it with a uuid-keyed label store. **Discipline: a "you broke X" report is a pointer to investigate, not a verdict to accept or reflexively deny. Run the cheap check (diff/grep for "is my change even in this path" + the trace for "what actually happens") — it simultaneously exonerates the wrong suspect and surfaces the right bug, and "not my code" is only HALF the answer when the thing is genuinely broken.**
