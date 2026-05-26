# D-021 — 2026-05-22 — Penguins: research-operative sub-agent + per-player research/ folder

**Context.** Until now the brain had three sub-agent roles — **principal** (introspective), **dwarves** (repo-bound functional), **gnomes** (system-namespace structural housekeepers). External research — *"what's the current state of EU CBAM"*, *"what changed in polars 0.20"*, *"what does this vendor's pricing look like"* — fell to the principal by default, with no shape, no dedicated tool surface, and no place to land the source material that's distinct from the player's distilled `bank/notes/`.

The principal cued a researcher role mid-session. Initial framing was *"a researcher player"*, but the `players/_about.md` discipline rule (*"don't pre-create speculative players; add when content genuinely doesn't fit existing ones AND volume justifies overhead"*) routed the design to a **skill + sub-agent role**, not a new player. Research work belongs to whichever player is principal (Jebrim for work, Zezima for personal); the *act* of researching is what gets its own machinery.

A second decision branched mid-design: where does research output land? Initial draft pointed at `bank/drafts/notes/`. The principal's pushback — *"research needs its own place to live; what's picked out from the research goes into the players bank"* — split the surface: **full research writeups** live in a new per-player `research/` folder; **picked claims** still flow into `bank/drafts/notes/` during alching with cross-link back to the source. Research is the source material; bank is the picking.

**Decision.** Ship penguins as the third functional sub-agent role + the research skill + the per-player research/ folder, end-to-end in one session.

## The role

**Penguin** — research-operative sub-agent, functional like a dwarf, with its own tool kit and write surface. Named after the RuneScape penguin race — KGP (*Komitet Gosudarstvennoy Pingvinnosti*) intelligence operatives. They go past Gielinor's gates, gather intel, return with anchored findings.

Three orthogonal lineages now stand in parallel:

- **Dwarves** — internal-source work (repo, bank, existing knowledge). Race-named per RS.
- **Gnomes** — structural housekeeping (drafts triage, session-close, alching). Race-named per RS.
- **Penguins** — external-source work (web, vendor docs, regulations, news). Race-named per RS.

The principle from `meta/modes.md`:

> Principals are introspective. Dwarves are functional within the repo. Penguins are functional beyond the gates. Gnomes are structural housekeepers.

### Player inheritance

Penguins inherit the principal's player by default (like dwarves), with explicit cross-player override available (*"have a penguin look into X for Jebrim"*).

### Write surface

**Allowed:**

- Active player's `research/` (any subpath) — penguin's playground, no draft gate.
- Active player's `quest-log/in-progress/`, `quest-log/completed/`, `quest-log/archive/` — sibling run-log entry.
- Active player's `inventory/` — working state during research.

**Blocked** (hook-enforced by `penguin-write-boundary.py`):

- All `confirmed/` (architectural guarantee #1).
- All `bank/` — research stays in `research/`; bank notes are *picked* during alching, not authored by penguins.
- All other `drafts/` paths — penguins are field operatives, not introspectors.
- `keepsake/`, `lorebook/`, `examine/`, `niksis8_character/` — introspective layers.
- `meta/`, `spellbook/rituals/` — rulebook + user-only rituals.
- Body files (`CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `ticks.md`, `.claude/settings*`, `.claude/agents/`, `.claude/hooks/`).
- Cannot spawn sub-agents (`block-sub-spawn.py` now includes penguin agent_type).

### Tool surface

`Read`, `Glob`, `Grep`, `Edit`, `Write`, `WebSearch`, `WebFetch`. No `Bash` — research operations don't need shell access; if a brief implies it, the principal spawns a dwarf in parallel instead of widening the penguin's surface.

## The research/ folder

New per-player layer. Sits alongside `bank/`, `quest-log/`, etc. Shape:

```
players/<name>/
  research/
    _about.md
    <YYYY-MM-DD>-<topic-slug>.md
    archive/
```

`_about.md` codifies: who writes (penguins + principals running the research skill), what goes here (full writeups per the research-skill body shape — question, date, confidence, sources, findings with citations, gaps), filename convention, what doesn't go here (distilled claims belong in `bank/drafts/notes/`), promotion (none — research stays; bank notes are pickings), archive on supersede.

Death-and-spawn: preserved across reset (parallel to `bank/`).

## The picking flow

The pivot is `meta/layer-routing.md`:

> A 2,000-word writeup of *"what's the state of CBAM as of 2026-05"* with twelve sources is a **research** file. The four sentences that come out of it — *"CBAM applies to X, effective Y, fee formula Z; risk for our clients: ..."* — is a **bank note**. The research stays as the anchor; the bank note carries the picking.

The picking happens during alching, not at research time. The alching ritual walks recent `research/` files, proposes `bank/drafts/notes/` entries that capture the load-bearing claims with a cross-link back to the source research file. Principal approves; promotions land in `bank/notes/`. When the research is superseded later (regs change, vendor moves), it goes to `research/archive/` and the dependent bank notes follow the same archive flow.

This decouples source size from bank size — the bank stays browsable, the research stays anchored.

## What shipped

### Chunk A — role definition (docs)

- `meta/modes.md` — penguin role definition (write surface, inheritance, can't sub-spawn), updated principal/dwarf/gnome/penguin axis throughout, updated *Principle* section.
- `CLAUDE.md` — renamed "five" → "six architectural guarantees"; added penguin write boundary as #5; extended sub-spawn block (#6) to penguins.
- `meta/write-rules.md` — added penguin row to ritual write-reach hooks-enforce list; added `research/` row to per-layer table.
- `players/_about.md` — added `research/` to per-player template + new section explaining the layer.
- `CLAUDE.md` per-player layer index — added `research/`.
- `meta/death-and-spawn.md` — added `research/` row (preserved across reset).

### Chunk B — research folder + skill amendment

- `gielinor/spellbook/skills/research.md` — amended: shipped earlier this session targeting `bank/drafts/notes/`; retargeted to `research/`; added "Two modes — principal-self vs penguin-spawn" section; rewired related-skill references from spawning-dwarves to spawning-penguins.
- `players/jebrim/research/_about.md` — new.
- `players/zezima/research/_about.md` — new.
- `meta/layer-routing.md` — new row for full research writeups; new "Research vs bank" paragraph in *Operational consequences* describing the picking flow.

### Chunk C — hook enforcement

- `gielinor/.claude/hooks/penguin-write-boundary.py` — new, parallel to dwarf/gnome variants. Gates on `agent_type == "penguin"`. Allowed prefixes: research/, quest-log/, inventory/. Blocked substrings: confirmed/, bank/, all other drafts/, proposals/, rejected/, keepsake/, lorebook/, examine/, niksis8_character/, niksis8/, meta/, spellbook/rituals/, body files, `.claude/*`.
- `gielinor/.claude/hooks/block-sub-spawn.py` — refactored from binary ("dwarf"/"gnome") to `ROLE_PLURALS` mapping; penguin added.
- `gielinor/.claude/settings.json` — wired `penguin-write-boundary.py` into PreToolUse alongside dwarf/gnome boundary hooks.

### Chunk D — agent config + spawning skill

- `gielinor/.claude/agents/penguin.md` — new, parallel to `gnome.md`. Frontmatter: `name: penguin`, `tools: Read, Edit, Write, Glob, Grep, WebSearch, WebFetch`. System prompt covers read-first checklist, write boundary, tool surface, operating discipline, reporting format, what-not-to-do.
- `gielinor/spellbook/skills/spawning-penguins.md` — new, parallel to `spawning-dwarves.md` / `spawning-gnomes.md`. Spawn heuristic (>5 fetches OR ≥2 independent clusters AND external work required), pre-flight check, briefing template, channel discipline (background by default), status-on-ping (tail-since-last), completion-weave, anti-patterns.

### Chunk E — visualizer + hook

- `developer-braindead/.claude/hooks/emit-event.py` — added `PENGUINS_PATH`; added ROLE_CONFIG entry for `"penguin"` (id_prefix "P", color_prefix "penguin", color_count 3, spawn/despawn events `spawn-penguin`/`despawn-penguin`, speaker `penguins`). Generalized `spawn_kind_from_tool_input` and `attribute_to_subagent` from "gnome-or-else" binaries to `in ROLE_CONFIG` lookups (the comment block prediction landed exactly).
- `developer-braindead/experiments/visualizer/index.html`:
  - CSS palette (`--penguin-body`, `--penguin-body-dk`, `--penguin-belly`, `--penguin-beak`, `--penguin-feet`, scarf colors `--penguin-1/2/3`, COMMS tint family `--penguins-text/-dot/-swatch`).
  - Tab dot, filter rule, speaker bullet for `penguins`.
  - COMMS tab declaration: `PENGUINS` between GNOMES and WISP.
  - New building `iceberg` in `BUILDINGS` + `STAND` + `LABEL_Y_OFFSET` + `BUILDING_DESC`. Map position (1480, 220) — NE corner, mirroring Braindead's workshop in the NW. Custom building render (terrain-style, not isoBuilding) — glacier mound with three peaks, ice cracks, snow caps, KGP banner on flagpole, intel scroll + fish at base.
  - `spawnPenguin(ev)` / `despawnPenguin(id)` — tuxedoed silhouette (dark back, cream belly, orange beak, dark flippers), scarf in spawn color (the only varying element). Smaller and rounder than dwarf/gnome — reads as a different species at a glance.
  - `penguinNodes` / `penguinCount` globals. `resetWorld` clears them. `updateTicker` includes penguin count when > 0.
  - `isPenguinActor` + `isSubAgentActor` updated. `ensureActorExists` filters `P\d+` (penguins spawn via spawn-penguin only).
  - `actorAccentColor`, `actorDisplayName`, `speakerFor`, `deriveSpeaker` extended for `P\d+`.
  - `applyEvent` dispatch: `spawn-penguin` / `despawn-penguin` cases.

## Open questions / deferred

- **Parallel penguins.** First cut treats each penguin as singular like dwarves/gnomes; parallel-instance routing (D-017 / D-019 style) deferred until use shows it matters. Penguins are sub-agents (always unique IDs P1, P2, …), so the parallel-instance concept doesn't apply the same way — but a single principal could spawn 3 penguins simultaneously for cluster-research. The gather-slot scaffolding at the iceberg STAND handles 3+ co-located penguins.
- **Picking flow ritualization.** Alching's research → bank picking step is described in `_about.md` and `layer-routing.md` but not yet codified in the alching ritual file itself. Defer until first real picking pass.
- **Live test.** Penguin spawn end-to-end (Task tool with `subagent_type: "penguin"` → hook routes through ROLE_CONFIG → sprite appears at Iceberg → research file lands in player's `research/` → despawn fades sprite) untested under live conditions. Joins respawn Step 1 (parallel Braindead live test) and Step 3 (Guthix live test) in the pending verification queue.
- **Iceberg visual polish.** First cut is intentionally simple — geometric terrain rather than architectural detail. Refinement (animated penguins waddling at base, snow particle drift, aurora glow) deferred until the shape proves itself in use.
- **Cross-player penguin delegation visualization.** When *"have a penguin look into X for Zezima"* fires from a Jebrim session, the penguin writes to Zezima's `research/` but the visualizer attribution may render it under the spawning session. Same edge as cross-player dwarves; revisit if it surfaces as confusion.

## Cascade

`gielinor/` files landed:

- `meta/modes.md`, `meta/write-rules.md`, `meta/layer-routing.md`, `meta/death-and-spawn.md`
- `CLAUDE.md`
- `players/_about.md`
- `players/jebrim/research/_about.md` (new)
- `players/zezima/research/_about.md` (new)
- `spellbook/skills/research.md` (amended; shipped earlier in this session)
- `spellbook/skills/spawning-penguins.md` (new)
- `.claude/hooks/penguin-write-boundary.py` (new)
- `.claude/hooks/block-sub-spawn.py` (refactored to ROLE_PLURALS)
- `.claude/settings.json` (PreToolUse extended)
- `.claude/agents/penguin.md` (new)

`developer-braindead/` files landed:

- `bank/decisions/D-021_penguins_research_subagent.md` (this file)
- `quest-log/S030_penguins_subagent_and_research_folder.md`
- `.claude/hooks/emit-event.py` (ROLE_CONFIG + spawn-kind generalization)
- `experiments/visualizer/index.html` (extensive: iceberg building, penguin sprite, full wiring)
- `respawn.md` (next concrete step + carry-over rewritten)

## Related

- [[D-016_gnomes_subagent]] — gnomes as the second sub-agent role; the founding move that made "third sub-agent role" thinkable.
- [[D-017_parallel_player_instances]] — parallel player instances; established the actor-class extension pattern that ROLE_CONFIG generalization rode on.
- [[D-018_parallel_session_substrate_isolation]] — per-session intent files; the substrate that lets multi-penguin sessions disambiguate cleanly.
- [[D-019_parallel_braindead_and_comms_channel]] — parallel Braindead + comms channel; established the "extend ROLE_CONFIG when a new actor class lands" muscle memory.
- `gielinor/spellbook/skills/research.md` — the methodology penguins (and principals) follow.
- `gielinor/spellbook/skills/spawning-penguins.md` — the spawn heuristic.
- `gielinor/.claude/agents/penguin.md` — the agent config.
- `gielinor/meta/modes.md` — the role taxonomy.
