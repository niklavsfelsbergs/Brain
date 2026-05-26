# Is the system eating itself? — a critical audit

> **Session:** S104 (braindead-cf03bfe1), 2026-05-26. Dev-brain, doc-only.
> **Prompt origin:** an external review prompt written by someone who had **only read the documentation**, asking whether the brain is over-engineered across 8 dimensions, with the standing instruction to "look at this with a critical eye" — including criticizing the prompt's own premises.
> **Method:** measurement over impression. 3 read-only evidence sub-agents (file census, inward/outward classification, discipline-leak rates) + direct empirical hook testing. Evidence cited inline.

---

## TL;DR — the verdict

**No, the system is not eating itself in the way the prompt assumes.** The prompt hunts for the failure mode of a *mature, bloated* system — ceremony accumulating without use, drafts piling up undecayed, dead rituals lingering. The measurements refute that picture: drafts folders are **near-empty** (aggressive triage keeps pace), 8 bankstandings + same-day alching in 6 days, and nearly every layer is exercised. This is a **6-day-old, high-velocity, self-pruning** system, not a silting one.

But the audit, by looking for the wrong disease, **walked past the two real ones**:

1. **🔴 Four of the six "architectural guarantees" do not fire from the real entry point.** The dwarf/gnome/penguin write-boundaries and the no-sub-spawn hook gate on `payload.agent_type ∈ {dwarf,gnome,penguin}` — a condition that is *unreachable* from brain root (where the cockpit launches everything). This is the S085 enforcement-gap repeating itself, **uncaught**, in the half of the hooks S085 didn't empirically re-test. This is the actual bug.
2. **🟠 The inward/outward imbalance (D-027) is real and live** — ~65% of all effort points inward (the agent observing/building itself), and the single most expensive artifact in the whole system (the cockpit/visualizer/switchboard line, ~S032–S095) exists *to watch the agent work*. The prompt's cut-instinct points at the cheap stuff (empty draft folders, theming words); the expensive inward thing goes unquestioned.

The honest reframe of "fewer moving parts working harder": the cheap markdown parts mostly pay rent and cutting them saves ~nothing. The leverage is in **enforcing the structure that already exists** (#1) and **building the outward half** (#2) — not in deleting layers.

---

## The framing error that infects the whole prompt

**The system is 6 days old.** Born 2026-05-20; this audit is 2026-05-26. 253 commits in that window.

The prompt repeatedly assumes a long timeline: *"last 90 days,"* *"60 days,"* *"if alching hasn't run for player X in N weeks,"* *"pull 5 random sessions per player."* None of those windows exist. There is no 90-day ratio. "Alching hasn't run in weeks" is impossible — the system has existed for days. "5 random sessions per player" over-samples Zezima (who has **3 sessions total**).

This isn't pedantry. It changes the diagnosis:

- **"Stale draft" logic is inapplicable.** A draft sitting 2 days in a 6-day-old system is not stale signal; it's fresh.
- **"Unused = cut it" logic is dangerous here.** A capability untouched in 6 days hasn't failed to pay rent — it hasn't been *load-tested* yet. Cutting it is cutting scaffolding before the building is occupied.
- **Velocity is the dominant fact, not bloat.** 253 commits / 6 days ≈ 42/day. The risk profile of a system being built this fast is *under-enforcement and wrong-direction*, not *accretion*.

A documentation-only reviewer cannot see the dates. The single most important correction to the prompt is: **size every judgment to a 6-day-old system.**

---

## Dimension-by-dimension

### D1 — Ceremony per component  →  *mostly used; a few genuinely cold spots*

Census (read-only sub-agent): Jebrim's full stack is the workhorse (88 completed quests, 26 examine/confirmed, 19 bank notes, 13 skills). Dev brain: 97 sessions, 30 decisions. Bankstanding: 8 passes. The drafts→confirmed→rejected pipeline **demonstrably cycles end-to-end** (3 rejected in Jebrim's examine/, 2 landed godly proposals) — it's not a happy-path-only theatre.

**Genuinely cold (0 uses in 6 days):**
- `players/inbox/` — unscoped-capture triage, never received a capture.
- `brain/ideas/` — the `note this idea:` mechanism, never fired.
- `deities/guthix/proposals/rejected/` — no godly proposal ever rejected.
- **Guthix consultation mode — 0 runs ever** (no `G-NNN` file exists; only 6 Guthix OPENs, all bankstanding). This is the standout: a whole *mode* with documented routing, voice, write-reach, and a dedicated heuristic in `communication-protocol.md` (the "Hey Guthix" suggestion rule, born S038 to fix exactly this) — and it has never once been used.
- **Zezima — 3 sessions vs Jebrim's 44.** 0 skills, no `spellbook/drafts/skills/` dir at all, 4 bank notes. The personal-life player is near-dormant.

**Verdict:** *Not* systemic ceremony-without-use. A short list of cold mechanisms. At 6 days, the right move for most is **watchlist, not cut** — except where the cold spot reveals a *design* problem (Guthix consultation; see below).

### D2 — Inward/outward ratio  →  🟠 *the real imbalance, already self-diagnosed*

~147 distinct sessions: ~88 Braindead (inward by definition) + 8 Guthix bankstandings (inward-meta) + 48 Jebrim (outward) + 3 Zezima (outward). **≈65% inward / 35% outward**, and a large slice of the "outward" Jebrim work is building his *own* shipping-agent tooling rather than delivering analyst artifacts. Git corroborates: ~23% of 249 commit subjects carry outward keywords. The system's own S060 audit measured ~52% observability-scaffold / ~28% player-work — consistent.

Two honest nuances:
- **The outward channel is alive, not dead.** Shipped/deployed/executed deliverables land as recently as the audit date (S097 prod OOM fix, S098 SCM alert split deployed, S078 EU-tender dispatch). ~15 concrete outward deliverables in 6 days. The imbalance is *proportion and reflex*, not absence of hands.
- **The expensive thing is inward.** The largest continuous build in the entire history is the cockpit/switchboard/visualizer line (~S032–S095) — a fleet-management UI so the operator can watch the agent work. **This is the one component whose cost most exceeds its outward value, and the audit prompt never points at it** because it's looking for cheap ceremony (markdown layers) not expensive infrastructure (code).

**Verdict:** D-027 is borne out and live. The cure is not "less structure" — it's the unbuilt operational half (`plan.md` §C pilot / scheduled triggers). Cutting layers does nothing for this.

### D3 — Discipline leak rate  →  *one rule leaks; the leak has a structural cause and a known fix*

| Discipline | Hit rate | Reading |
|---|---|---|
| OPEN-posting (dev-brain) | ~15% early → ~85% recent (~44% lifetime) | S082 doc-fix substantially worked; residual leak is mid-conversation entry bypassing the respawn checkpoint |
| OPEN-posting (gielinor) | ~90% | leaks only on immediate-task entry |
| CLOSING-posting | ~85–90% both channels | faithfully followed |
| Drafts observation-backed (not aspirational) | **~100% anchored, 0 aspirational** | best discipline measured; followed *without* a hook |
| Per-turn quest-log + `pending` action markers | append: spirit-met; `pending` markers: **~0%** | the literal mechanism was superseded |

**The cross-cutting pattern is the finding:** disciplines with a **reliable trigger point** (close-session cue, alching review) are followed faithfully; the one discipline whose trigger gets **bypassed** (OPEN at respawn, skipped on mid-conversation entry) is the one that leaks. This argues the fix is a **trigger/hook**, not more documentation — and S082 itself already scoped (and deferred) a `SessionStart`/`UserPromptSubmit` hook that refuses to proceed without an OPEN.

One doc-vs-reality drift worth fixing: `death-and-spawn.md`'s `pending`-before-execution action-marker rule is ~0% followed because a **better** mechanism emerged organically — commit-SHA + "HELD for principal go / COMMITTED+PUSHED" state tracked in comms + `inventory/*-resume__<sid8>.md`. Update the doc to describe what actually works; don't flag the gap as a behavioral failure.

**Verdict:** Mostly healthy. OPEN-leak → wants the deferred hook. `pending`-marker → wants a doc update, not enforcement.

### D4 — Draft / archive growth without decay  →  *refuted; decay outpaces accumulation*

The prompt's hypothesis ("accumulation outpaces promotion + rejection → review cadence is the bottleneck → propose compaction") is **false here.** Brain-wide there are **3 pending drafts total.** Every per-player drafts folder is currently **empty** — because B-008 just promoted/rejected their contents. The only zero-promotion item is one Guthix bank draft (substrate-portability, 2026-05-24) carried across B-005→B-008 — a single low-severity item.

If anything the bias runs the *other* way: drafts get triaged so fast (in-session alching) that the "draft when in doubt" early-bias may be *under*-firing. **Do not propose a compaction strategy — there is nothing to compact.** This dimension is a clean bill of health.

### D5 — Persona behavioral delta  →  *both earn keep; the under-used player is the more justified one*

- **Jebrim:** delta is real but ~70% lives in the *loaded layers* (bank/examine/keepsake encode pathspec-hygiene, ground-truthing-every-number, hold-for-sign-off reflex) and ~30% in voice. Strip the costume and "analyst-Claude + these notes" approximates him — the biggest loss being the encoded git/verification discipline, which isn't really persona, it's accumulated `examine/confirmed/`.
- **Zezima:** **larger, more genuine delta.** His persona produces a *decision-making posture* a generic helpful-assistant default actively fights — declining to over-recommend, holding ambivalence, honoring a "gut-fit veto" (S066: named the pattern across two flats, explicitly *did not relitigate* the user's gut call). The default assistant instinct is to resolve and recommend; Zezima's persona suppresses it. That's the persona doing load-bearing work.

**The irony worth surfacing:** the player the prompt's logic would flag for cutting (Zezima, 3 sessions) is the one whose persona is *most* behaviorally justified. Usage frequency ≠ behavioral value. **Verdict:** neither persona is overhead; if anything Zezima is under-used relative to his distinctiveness.

### D6 — Two-brain duplication cost  →  *the split pays rent; the coordination machinery is the tax*

Maintained in parallel between `gielinor/` and `developer-braindead/`:

| Parallel item | Duplication? | Half-surface equivalent? |
|---|---|---|
| `comms/active.md` + protocol | Same mechanism, 2 files, 2 copies of OPEN/CLOSING/UPDATE rules | Defensible — different actor populations |
| Respawn ritual / entry sequence | Two rituals, same shape | Defensible — different load orders |
| `quest-log/` SNNN format | Same format | — |
| **Shared SNNN counter** | Braindead + players draw from one number line | **Real tax** — comms is full of "SNNN bumped X→Y (collision with sibling)" |
| Decision log | `lorebook/confirmed/D-NNN` (main) **and** `bank/decisions/D-NNN` (dev) — two D-NNN namespaces | **Real tax** — D-NNN means two different things depending on brain |

**Verdict:** The two-brain split itself is one of the *better* design calls — the dev brain is a genuinely different mode (construction log, no players, no alching/bankstanding, Braindead voice, different lifecycle). A labeled subtree would *not* be functionally equivalent; it would blur a real boundary. But two specific pieces of shared machinery are pure overhead: the **shared SNNN counter** (collision races) and the **dual D-NNN namespace** (same ID, two meanings). Those are worth separating or disambiguating; the brains themselves are not worth merging.

### D7 — RuneScape theming tax  →  *real only at routing-ambiguity points; mostly valued flavor*

**Critical caveat first:** the principal has *documented* that the theming is deliberate signal, not noise (`CLAUDE.md` → Communication discipline: "playfulness is signal... Flat-affect responses are misaligned"). A blanket "strip the theming" recommendation would contradict a standing principal preference. The tax is real **only where a metaphor causes routing ambiguity or operational error**, not where it's flavor.

Highest translation cost (the ones that actually cause mistakes), worst first:

1. **`alching` vs `bankstanding`** — the two core maintenance rituals. Both mean "tend the brain"; neither name encodes its *scope* (per-player vs global) or *function* (consolidate vs promote-cross-cutting). They are mutually confusable and opaque to any outsider. **Highest tax.**
2. **`dwarf` / `gnome` / `penguin`** — three sub-agent roles named by arbitrary creatures with no mnemonic link to function (in-repo task / housekeeping / research). You must memorize a 3-way mapping, and "which do I spawn for X?" is a live routing question. (Also the roles with the broken enforcement — see D8.)
3. **`examine` / `lorebook` / `keepsake`** — three identity-ish layers that sound similar and don't map obviously to self-model / decision-log / pins.

**Recommendation — dual-naming, not replacement** (respects the preference *and* cuts the tax): keep the flavor name, add a functional subtitle everywhere the term is first used in routing-critical docs. e.g. *"alching (per-player consolidation)"*, *"bankstanding (global review + promotion)"*, *"penguin (research operative)"*. Leave pure-flavor terms (`gielinor`, `wisp`, `respawn`, `Guthix`, `quest-log`) untouched — they cost nothing operationally.

### D8 — Hooks-in-name-only  →  🔴 *the real bug: 4 of 6 guarantees inert from the default entry point*

Re-ran the S085 logic empirically from this brain-root session. Results:

| # | Guarantee | Wired at brain root? | **Fires from brain root?** | Evidence |
|---|---|---|---|---|
| 1 | No writes to `confirmed/` | ✅ | ✅ **PROVEN** | A real `Write` to `gielinor/examine/confirmed/__probe.md` was **BLOCKED** (exit 2) live this session |
| 2 | No deletes | ✅ | ✅ **PROVEN** | A real `rm` was **BLOCKED** live this session |
| 3 | Dwarf write-boundary | ✅ (wired) | ❌ **inert** | gates on `agent_type=="dwarf"`; see below |
| 4 | Gnome write-boundary | ✅ (wired) | ❌ **inert** | gates on `agent_type=="gnome"` |
| 5 | Penguin write-boundary | ✅ (wired) | ❌ **inert** | gates on `agent_type=="penguin"` |
| 6 | No sub-spawn from sub-agent | ✅ (wired) | ❌ **inert** | gates on `agent_type ∈ {dwarf,gnome,penguin}` |

**Why #3–#6 are inert from the default entry point** (chain of proof):

- The four role hooks block **iff** `payload.agent_type` is exactly `"dwarf"/"gnome"/"penguin"`. Direct-invocation harness (11 cases, all pass): they correctly block on those strings and correctly **exit 0 (allow) when `agent_type` is `"general-purpose"` or absent.**
- For that trigger to fire, you must spawn a sub-agent of `subagent_type` dwarf/gnome/penguin. But: **(a)** no `dwarf` agent config exists *anywhere* (only `gnome.md` + `penguin.md`); **(b)** those two live in `gielinor/.claude/agents/`, which is **not loaded at brain root** — proven directly: *this* brain-root session's available agent types are `claude, Explore, general-purpose, Plan, …` with **no gnome/penguin**; **(c)** the cockpit (the system's real driver) spawns `claude` with `cwd = brain root` (per the S085 settings.json comment).
- Therefore every sub-agent the system actually spawns is `general-purpose`/`Explore`/`claude`, whose payload `agent_type` is never one of the three magic strings → the boundary hooks exit 0 → **no enforcement.** Even the per-role *tool restrictions* in `penguin.md`/`gnome.md` don't apply, because those configs aren't loaded either.
- Corroboration from inside the codebase: `emit-event.py:1689` explicitly codes a fallback for `agent_type` being *"absent or unknown (older Claude Code versions)"* and defaults to `"dwarf"`. The brain's *own* instrumentation hook knows `agent_type` is unreliable; the *boundary* hooks (which have no fallback) assume it's always present and correct.

This is precisely the S085 failure mode — "the guarantees were prompt discipline, not gates" — except S085 only fixed and re-tested the two *path-based* hooks (confirmed-writes, deletes). The four *role-based* hooks were re-wired into brain-root settings.json in the same pass but **never empirically confirmed to fire**, because doing so requires actually spawning a typed sub-agent, which isn't possible from the entry point they were wired for. The brain believes guarantees #3–#6 are closed. They are not.

**This does not mean the system is unsafe today** — sub-agent behavior is still constrained by prompt discipline and by what tools the spawn grants. But the *architectural* claim ("hook-enforced, cannot bypass, do not try" — `CLAUDE.md`) is false for 4 of the 6. Per the brain's own memory note (`verify-enforcement-fires`): *a documented guarantee isn't real until you've watched it fire from the actual entry point.* These four have never been watched firing, and cannot fire as currently wired.

**Definitive empirical resolution (run this session, S104).** A passive payload-capture probe was temporarily registered (`settings.local.json`, PostToolUse, exit-0-always, reverted after) and a real `general-purpose` sub-agent was spawned through it. Captured payloads:

- **Principal tool call:** `agent_type: <ABSENT>`, `agent_id: <ABSENT>`.
- **Sub-agent tool calls (Bash + Write):** `agent_type: "general-purpose"`, `agent_id: "a3f29aead298e808c"`.

**Conclusion: Claude Code reliably stamps `payload.agent_type`, and its value is exactly the `subagent_type` string used at spawn.** So the boundary hooks' mechanism is *sound* — they would fire correctly if a sub-agent were spawned with `subagent_type ∈ {dwarf,gnome,penguin}`. The *only* defect is that those subagent_types are not registered/loadable at brain root, so real spawns are `general-purpose` (→ `agent_type="general-purpose"` → not in the magic set → exit 0). The hooks are correct; the **agent configs are missing/mislocated.**

**This decides the fix → option 1, and it's small:**
1. ✅ **Register `dwarf.md` + `gnome.md` + `penguin.md` at brain-root `.claude/agents/`** (copy the two existing from `gielinor/.claude/agents/`; author a `dwarf.md` — none exists). Then a spawn of `subagent_type="gnome"` stamps `agent_type="gnome"` and the already-wired, already-correct hooks enforce as designed. **No hook code changes; no `agent_id` rewrite needed.** Option 2 (gate on `agent_id`) is unnecessary — `agent_type` is reliable.
2. The deeper implication: because typed dwarf/gnome/penguin spawns were never possible from brain root, the system has **almost certainly never spawned a real typed sub-agent** — all "gnome/penguin/dwarf" work ran as `general-purpose` agents described as such in the prompt. That means the per-config **tool restrictions** (e.g. penguin = no `Bash`) also never applied. Defense-in-depth was doubly absent: neither the boundary hook nor the tool grant.
3. Residual discipline gap after the fix: the agent must actually *choose* `subagent_type="gnome"` (not `general-purpose`) when spawning a gnome. The fix makes enforcement *possible and automatic when the typed agent is used*; it doesn't force the agent to pick the type. The spawning skills (`spawning-gnomes.md` etc.) should be checked — if they instructed using a typed agent that was never loadable, they've been silently no-op'ing the type the whole time.

---

### D8 fix — implemented this session (S106), verification deferred

Registered the three agent configs at **brain-root `.claude/agents/`** (the launch dir for cockpit/default sessions): `gnome.md` + `penguin.md` (copied verbatim from `gielinor/.claude/agents/`) and a newly-authored `dwarf.md` (none existed). Brain-root `.claude/agents/` is outside the live §O.6 sibling's gielinor+dev-brain `.md` rewrite scope, so no Edit-race; committed separately from that session.

**In-session verification was impossible — and the failure is itself the proof.** Spawning `subagent_type="gnome"` from this (brain-root) session returned: `Agent type 'gnome' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, Plan, statusline-setup`. Two things follow: (1) it directly demonstrates the live gap — a gnome cannot be spawned from brain root, so the gnome-boundary hook could never have fired here; (2) **agent configs do not hot-reload** — the config I just wrote isn't visible to this already-running session. The fix therefore takes effect for the **next** brain-root session, not this one.

**Hand-off verification (run in a fresh cockpit/brain-root session):** spawning `subagent_type="gnome"`/`penguin`/`dwarf` should now succeed, and a gnome told to Write to a `confirmed/` (or `meta/`) path should be **BLOCKED** by `gnome-write-boundary.py`. Until that's observed, treat #3–#6 as discipline.

**Two follow-ups left for the principal (both in the §O.6 sibling's gielinor/ surface — not touched this session):**
- `spellbook/skills/spawning-gnomes.md:11` (and the sibling spawning-penguins/dwarves skills) name `gielinor/.claude/agents/gnome.md` as "the one agent config" — a location unreachable from brain root. Update to the brain-root location (or note both) so the doc matches where spawns actually resolve.
- `CLAUDE.md` calls #3–#6 hook-enforced "architectural guarantees you cannot bypass." Until the hand-off verification passes, that claim is false from the default entry point; reword or qualify.

## What to actually cut / simplify / fix (ranked by leverage)

1. **Fix the 4 inert guarantees (D8) — confirmed cheap.** Highest leverage and now known to be a small fix: register `dwarf.md`/`gnome.md`/`penguin.md` at brain-root `.claude/agents/` (the empirical test proved `agent_type` passes the subagent_type string through, so the existing hooks then enforce as designed — no code changes). Until done, stop calling #3–#6 "architectural guarantees" in `CLAUDE.md`; they're discipline.
2. **Build the outward half (D2 / D-027 §C).** Not a cut — the actual missing organ. Every layer of inward structure is in place; the agent still has no autonomous hands.
3. **Land the deferred OPEN hook (D3).** The one discipline that leaks, with a known structural fix already scoped in S082.
4. **Disambiguate the two cheap two-brain taxes (D6):** split the SNNN counter per-brain (or per-actor); disambiguate the dual D-NNN namespace.
5. **Dual-name the 3 routing-ambiguous metaphors (D7):** `alching`/`bankstanding`/the sub-agent roles get functional subtitles. Keep the flavor.
6. **Decide Guthix consultation's fate (D1).** A whole mode with 0 uses ever. Either actively route to it (the S038 heuristic was meant to; it hasn't taken) or fold it into bankstanding. This is the one cold spot that reflects a *design* question, not just youth.

## What NOT to cut (defending against the audit's cut-bias)

- **The drafts/archive/rejected machinery.** It cycles, it's near-empty, decay outpaces accumulation. Cutting it removes the thing that *prevents* the bloat the audit fears.
- **The markdown layer taxonomy.** Cheap, mostly used. Cutting saves ~nothing and loses routing clarity.
- **Zezima.** Lowest usage, *highest* persona-justification. Usage ≠ value.
- **The two-brain split.** A real boundary, not redundancy. Merge the *counters*, not the *brains*.
- **The empty scaffolds (`inbox/`, `ideas/`), at 6 days old.** Watchlist them. They haven't failed to pay rent; they haven't been load-tested. Re-evaluate at ~30 days.

## Method note / threats to validity

- 6-day window: structural findings (D6/D7/D8) are age-independent; usage findings (D1/D5) are age-*sensitive* and flagged as such.
- D8's "inert from brain root" is proven for the default/cockpit entry point. A manually-launched `cd gielinor && claude` session *might* load the gnome/penguin configs and fire the hooks — untested, and not how the system actually runs. Worth a follow-up empirical check if anyone relies on those guarantees from gielinor-cwd sessions.
- `agent_type` propagation **was** directly observed this session (passive probe, see D8 resolution): Claude Code stamps it with the `subagent_type` string. The inference no longer rests on config-loadability alone — it's confirmed. The one thing still unobserved: a sub-agent spawned with `subagent_type` literally `"gnome"` (couldn't, not loadable) — but since the value is verified to pass through verbatim, registering the config is sufficient.

## Related
- [[D-027_inward_outward_build_imbalance]] — the inward/outward imbalance (D2).
- [[S085_5f93bb32_cockpit-pty-auth-and-md-xss]] — the brain-root enforcement gap this audit found *still half-open* for role hooks (D8).
- [[S082_open_on_entry_discipline]] — the OPEN-leak fix and the deferred hook (D3).
- [[S060_brain_self_audit_and_plan_reconciliation]] — the prior self-audit whose ratios this corroborates.
