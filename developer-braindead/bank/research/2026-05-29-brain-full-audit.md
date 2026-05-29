# Full brain-system audit — 2026-05-29 ([[S125]])

> **Verdict: 🟡 yellow — structurally healthy bones, two things hold it back.** A ~9-day-old system (born 2026-05-20). Re-run of the [[S110_144c0ca2_brain_full_audit|S110]] full audit (2026-05-27), two days on, with the corpus grown ([[S111_a268b008_shipping-agent-subagent-type|S111]]–S124). Run as an Opus-4.8 `Workflow` (6 read-only recon crews + synthesis) plus a main-session live-fire enforcement test (the part a workflow can't do — its subagents aren't `agent_type`-gated).

## Method

- **6 read-only recon crews** (deterministic `Workflow` fan-out, run `wf_42553347-907`), one per dimension: structure/routing, discipline (measured), inbox/cadence, verification debt, session-load/bloat, plan-vs-reality. Read-only → the lowest-risk first real use of the workflow engine; §Q.2 (do our write-boundary hooks fire inside a workflow?) stays **unverified** since nothing wrote.
- **Live-fire enforcement** (main session, 4 typed sub-agents): dwarf/gnome/penguin/shipping-agent each attempted an off-surface write + a `confirmed/` write. **8/8 blocked**, well-formed verbatim messages, no files created. Re-proves guarantees #3/#4/#5 + the shipping-agent boundary (never live-tested before) hold after the [[S121_03861733_ritual-analytics-item-11|S121]] logging additions (which were only synthetic-tested). Each tighter typed boundary short-circuited ahead of the generic `block-confirmed-writes` layer — correct precedence.

## Dimension health

| Dimension | Health | One-line |
|---|---|---|
| Structural integrity & routing | 🟢 green | Bones sound; only minor layer-hygiene (undocumented `zezima/docs/`, legacy stubs, 1 stale quest, 1 born-link exception). |
| Discipline (measured) | 🟡 yellow | Drafts gate + hook-blocks healthy and verified firing — but require-open fails open silently and the "leak closed" claim is false for gielinor (≥3 post-S110). |
| Inbox health & ritual cadence | 🟢 green | 8 pending HITL files actively drained, B-010 today, daily bankstanding; only soft spot is unmeasured Guthix consultation. |
| Verification debt | 🟡 yellow | Bounded to dev-brain cockpit behind one deferred relaunch, but grew since [[S110_144c0ca2_brain_full_audit|S110]] ([[S111_a268b008_shipping-agent-subagent-type|S111]]/[[S112_c7986694_cockpit-terminal-scroll-up-lock|S112]] added, none cleared) + 3 live probes. |
| Session-load / bloat | 🟡 yellow | respawn.md, both comms files, and the A4 trim all back over their own caps within 2 days; discipline caps not self-holding. |
| Plan vs reality & inward/outward | 🟡 yellow | Inward/outward gap substantially CLOSED (outward now dominant); real defect was stale plan.md/respawn.md mislabeling a deployed §C-adjacent producer as unbuilt. |

## Ranked findings

### 1 — 🔴 require-open gate fails open *silently*; "leak closed since [[S110_144c0ca2_brain_full_audit|S110]]" is false for gielinor
Two crews converged independently. [[S124]] (sid8 `61d62e21`, actor=jebrim) wrote three brain files, posted no OPEN, and emitted **zero** require-open events — neither block nor allow. The gate built to catch exactly this never fired. Mechanism: the hook's actor lookup returned `''` at write-time (status file lagged before settling to `jebrim`) → `_comms_for('')` is `None` → the hook returned 0 (allow) **with no telemetry**. The "OPEN-leak ~100% closed since [[S110_144c0ca2_brain_full_audit|S110]]" claim holds **only for the dev brain** (0 leaks, 42 OPEN ≥ 40 sessions); gielinor has **3 post-S110 leaks** (2026-05-27 + two on 2026-05-29) and a 32-OPEN-vs-38-session deficit. This is the first audit where an enforcement gate is shown **verified-broken** rather than merely unverified — the exact failure mode the brain's own `verify-enforcement-fires` memory warns against. [[S114_277d9053_khaan-audit-and-open-gate|S114]] only ever exercised the actor-*present* path.

**FIXED this session ([[S125]]).** `gielinor/.claude/hooks/require-open-on-entry.py`: (1) added `_actor_from_intent(sid8)` — recover the actor from the per-session intent file `.claude/intent/<actor>-<sid8>.txt` (the documented on-disk session anchor) before failing open; (2) `actor = _actor_for(sid8) or _actor_from_intent(sid8)`; (3) on the still-unresolved fail-open branch, emit a `skip-noactor` telemetry event so silent non-fires become **visible**. Verified 5/5 synthetic harness against the real `main()` (monkeypatched temp tree): **A** unresolved→allow+`skip-noactor` logged; **B** intent-fallback resolves jebrim→**BLOCK** (the S124 shape, now closed); **C/D** normal allow intact; **E** sub-agent still skips. `py_compile` clean. Header decision-table updated. **Remaining (doc tail):** scope the "leak closed" claim in `gielinor/CLAUDE.md` + `AGENTS.md` + brain-root `CLAUDE.md` to *dev-brain only* — pending principal sign-off (rulebook-prose edit).

### 2 — 🟡 Always-loaded discipline caps are not self-holding (and the cross-cutting insight)
`respawn.md` was ~13.9k tokens behind a deceptively-low 80-line count (14 stacked Prior blocks, each ~3k chars). **Both** `comms/active.md` files were back over the ~300-line/~30k-token rotation trigger they were *reset to on 2026-05-27* — regrown in two days. The A4 respawn-trim was a verbatim "NOT trimmed (A4 WATCH)" no-op for **10+ consecutive sessions**, each rationalized as "small focused session."

**The cross-cutting pattern no single crew named, and the most useful output of this audit:** **hook-blocking enforcement holds cleanly** — every block fired today (no-delete, confirmed-write, the 4 sub-agent boundaries, sub-spawn) — while **discipline-nudge / manual-deferred enforcement drifts** (OPEN-on-entry leaked, A4 trim a 10-session no-op, comms rotation regrew, cockpit relaunch perpetually deferred). *Enforcement that blocks works; enforcement that nudges or relies on a session remembering to act, drifts.* The generalizing fix: convert any must-hold cap from WATCH to a threshold-gated automatic step.

**DONE this session ([[S125]]):** A4 trim (respawn 80→56 lines, 55.8KB→22KB, ~8.4k tokens/dev-spawn recovered — 14 Prior blocks → two curated rollups + the existing ones); both comms rotated (dev 543→250 lines / moved 52; gielinor 448→253 lines / moved 27; nothing deleted, entry counts reconcile). **Pending (design choice surfaced to principal):** the *automation* — hook vs close-session step vs improved-WATCH — to stop the regrowth.

### 3 — 🟡 plan.md + respawn.md stale; §C-urgency + a landed proposal mislabeled
Both planning surfaces had frozen while later work landed. The load-bearing consequence: plan.md §C still read "manual-invocation-only / outward producer unbuilt" as the load-bearing gap. **The good news this exposes: the [[S110_144c0ca2_brain_full_audit|S110]] inward/outward gap has substantially closed** — the last ~2 days are outward-dominated (the FIF UPS-ORWO daily DAG deployed + live-validated (gielinor commit 609bcb4), the carrier OTD SLA baseline on ~734k Q1 shipments, the designed weekly Shipping Agent Report, gielinor commit 1be1db1), all as hands-on Jebrim player work — exactly the 2026-05-27 steer in practice. **Caveat (don't over-claim):** none of those *is* the §C pilot; §C's specific deliverable (six `shipping_mart` freshness checks on a trigger) is still unbuilt. Separately, the "write-rules.md enforced-by-hook godly proposal" carried as "pending next bankstanding" across §P/§O.10/respawn had **already landed at [[B-010]]** (proposal in `proposals/archive/`, write-rules.md:86 carries the note, zero open proposals).

**DONE this session ([[S125]]):** plan.md §C reconciled (urgency retired, the over-claim caveated); §O.10 godly-proposal carry marked LANDED; respawn.md prose refreshed (§O closed, inward/outward updated, the stale ★NEXT Khaan block replaced with the audit-current state); respawn pointer updated.

### 4 — 🟢/🟡 Verification debt grew but stays bounded; ritual telemetry has no history
Verification debt is **100% dev-brain cockpit/enforcement** (0 UNVERIFIED items in gielinor). One deferred "verification-only cockpit relaunch" gates ~10 sessions of RUNTIME-UNVERIFIED UI changes ([[S073_d82c4fbc_terminal-scroll-root-fix|S073]]/79/84/85/86/[[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]]/[[S108_98592157_cockpit-place-session-name-and-prewrite|S108]]/[[S112_c7986694_cockpit-terminal-scroll-up-lock|S112]]) **plus** the never-live-verified [[S111_a268b008_shipping-agent-subagent-type|S111]] shipping-agent type (a real `Agent(subagent_type:'shipping-agent')` spawn + the cyan "S" chip on relaunch). Backlog grew since [[S110_144c0ca2_brain_full_audit|S110]] ([[S111_a268b008_shipping-agent-subagent-type|S111]]/[[S112_c7986694_cockpit-terminal-scroll-up-lock|S112]] added, none cleared). 3 debug-log probes flagged "strip once verified" since [[S093_f3239bdc_transcript-readability-and-term-fit|S093]]/[[S094_cockpit_noopen_stale_process_cleanup|S094]]/[[S112_c7986694_cockpit-terminal-scroll-up-lock|S112]] are still live and writing daily (`term-fit-diag.log` ~988KB). Separately, `ritual-stats.py` Band A has **no usable history** — all 36 events are from one 3.5h window today, so `--days 30` == all-time (the telemetry is gitignored, born recently). Expected mid-cockpit-build for a 9-day-old system; the only risk is the relaunch deferring indefinitely (same pattern as #1/#2). **Top remaining principal action.** Recommended: one relaunch pass clears the checklists ([[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]]/[[S108_98592157_cockpit-place-session-name-and-prewrite|S108]]/[[S111_a268b008_shipping-agent-subagent-type|S111]]/[[S112_c7986694_cockpit-terminal-scroll-up-lock|S112]]), live-spawn the shipping-agent, strip the 3 probes + gitignore the logs; add a "Band A window: <first>→<last>" caveat line to `ritual-stats.py`.

### 5 — 🟢 Minor layer-hygiene — benign, none urgent (→ next bankstanding)
`zezima/docs/` holds a source PDF outside the spec'd `research/` home (wants a one-line `_about.md` carve-out, no relocation); two legacy empty `spellbook/skills/drafts/` stubs from the superseded [[S018_jebrim_layer_utilization_audit|S018]] routing; zezima's [[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]] in-progress quest stale since 05-26 but reads as a deliberately-held human-values call; one graph-isolated hub note (`eu_tender_2026.md`, 0 wikilinks) that is a legitimate born-link exception (no IDs to wrap); Guthix consultation still leaves **zero G-NNN traces** (the [[S038_brain_underutilization_diagnosis|S038]] ~1.9% problem shows no on-disk improvement — but it's chat-only-by-design, so "unmeasured" ≠ "unused"; recommend a lightweight consultation-invocation counter); Jebrim's 3 identity drafts pending principal `/drafts` approval (generated today, not accumulating).

## Measured signals (the healthy half)

- **Drafts→confirmed gate is discriminating, not rubber-stamping:** 88% promote (43/49), 6 genuine rejections across 3 layers (examine 3 / niksis8_character 2 / spellbook 1), 5 pins. Brisk flow (43 promotions in 9 days), no clog.
- **Bankstanding cadence excellent:** B-001..B-010 in 8 days, B-010 ran today, each with a Phase-0 alching loop.
- **Inbox small + drained:** 8 pending HITL files total (7 Jebrim, 1 Guthix, 0 globals, 0 Zezima); `players/inbox/` empty.
- **Structural:** 31 `_about.md` (0 missing at any spec'd layer root); 0 true deletes since birth (6 git-D entries all reconciled as moves/merges/renames); born-link pre-commit hook installed + firing.

## Deltas since [[S110_144c0ca2_brain_full_audit|S110]] (2026-05-27)

**Improved:** (1) the inward/outward gap substantially closed — outward production now dominant; the 2026-05-27 reprioritization is honored in practice. (2) Born-link enforcement shipped (pre-commit hook, May 28) — the graph-rot risk is now machine-guarded. (3) The drafts gate is proven discriminating. (4) require-open's actor-present path + all sub-agent boundaries observed firing from the real entry point.

**Regressed / newly exposed:** (1) **the headline "OPEN-leak ~100% closed" claim is false for gielinor** — and require-open fails open *silently* on the empty-actor race (verified-broken, not just unverified). The single most important delta. *(Fixed this session.)* (2) Verification-debt backlog grew ([[S111_a268b008_shipping-agent-subagent-type|S111]]/[[S112_c7986694_cockpit-terminal-scroll-up-lock|S112]] added; the deferred relaunch [[S110_144c0ca2_brain_full_audit|S110]] flagged still hasn't run). (3) Discipline caps stopped holding — respawn.md, both comms files, the A4 trim all drifted past documented triggers within 2 days of the 05-27 reset. *(Trim + rotation done this session; automation pending.)*

## Follow-ups

**Done this session ([[S125]]):**
- require-open fail-open fix + `skip-noactor` telemetry (verified 5/5 synthetic harness).
- plan.md §C reconcile + the landed-at-B-010 godly-proposal correction.
- respawn.md A4 trim (80→56 lines, ~8.4k tok/spawn) + prose refresh + pointer.
- both comms/active.md rotated (dev 543→250, gielinor 448→253; nothing deleted).
- **Discipline-cap automation = the close-gate (principal pick):** added a `session-load hygiene` check to `close_check.py` for BOTH rituals — dev checks dev-comms lines + respawn stacked-`Prior` count; player checks gielinor-comms lines; threshold 300 lines / 2 Prior blocks; a real FAIL with precise remediation. Verified: PASSES on the just-rotated state, FAILs when over cap. This converts the drift-prone WATCH into a close-precondition that holds (the #2 cross-cutting fix, realized via the gate that already holds rather than a risky SessionEnd auto-write).
- **Claim correction (principal pick) — with a record-check caveat:** the "OPEN-leak ~100% closed" claims in `CLAUDE.md`/`AGENTS.md`/`respawn-ritual.md` were found **already dev-brain-scoped + accurate** (the audit synthesis overstated them as false). No wrong claim to rewrite; instead added a **scope note** to the two router files (`CLAUDE.md` + `AGENTS.md`) recording that the ~100% is dev-brain-specific and the gielinor *player* side leaked until this session's gate fix.
- this report.

**Remaining (principal's GUI action / later):**
- **Verification-debt clearing** — the deferred cockpit relaunch (board reads `b91.0`) + shipping-agent live-spawn + strip the 3 diag probes. One principal session clears most of it.
- §Q.2 (do our write-boundary hooks fire inside a workflow?) — verify before any workflow *writes* brain content (this audit's workflow was read-only).
- finding-#5 hygiene sweep → next bankstanding (Guthix).
