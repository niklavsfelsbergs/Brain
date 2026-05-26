# S030 — 2026-05-22 — Penguins: research-operative sub-agent + research/ folder

The brain gained a third sub-agent role. Where dwarves dig in the repo and gnomes tend the brain, **penguins** go beyond Gielinor's gates — external research via `WebSearch` / `WebFetch`, outputs anchored in a new per-player `research/` layer that is distinct from the bank. The trichotomy closes a hole in the model: there was no shape for outward-facing work, and no place for source material that doesn't belong in `bank/notes/` directly. See [[D-021_penguins_research_subagent]] for the full design.

## How it came up

Principal cue mid-session: *"We need a researcher player."* First-pass instinct was to scaffold a third player alongside Jebrim and Zezima. The `players/_about.md` discipline rule pushed back — don't pre-create speculative players; volume hasn't materialized. The principal agreed: *"Lets make a research skill which the player can use. If I research work related stuff I go to Jebrim etc."*

Skill shipped first — `gielinor/spellbook/skills/research.md` with the four-section spec (when-fires / tool surface / pragmatic source discipline / decomposition / parallelism / output / anti-patterns / related). Three calls landed before drafting: tool surface = `WebSearch` + `WebFetch`, source strictness = pragmatic, drafts-gate = direct (Braindead's construction-crew path).

Then a second cue: *"oh but wait, then lets make the researcher also a subagent like dwarves and gnomes."* That escalated the work from a single skill file to the full third-role bundle.

Naming arc: *researcher* → *wizard* (proposed for RS-lore fit) → *Reldo* (Varrock library archivist NPC) → *penguin*. The principal pivoted to penguins after a brief intermission, and the lineage clicked into place — penguins are an RS race (parallel to dwarves and gnomes), and the KGP lore (penguin intelligence service from the Cold War quest series) maps the role exactly. Researchers as spies.

## What shipped — bundled end-to-end in one session

Five chunks, all landed before commit:

**Chunk A — role definition (docs).** `meta/modes.md` extended with the Penguin role subsection (write surface, inheritance, tool surface, hook enforcement reference). `CLAUDE.md` renamed "five" → "six architectural guarantees," added penguin write boundary as #5, extended sub-spawn block to include penguins. `meta/write-rules.md` extended (new `research/` row in per-layer table, penguin row in hooks-enforce list). `players/_about.md` extended with `research/` in per-player template and new section explaining the layer. `CLAUDE.md` layer index updated. `meta/death-and-spawn.md` extended (research/ preserved across reset).

**Chunk B — research/ folder + skill amendment.** `gielinor/spellbook/skills/research.md` retargeted output from `bank/drafts/notes/` to `research/` and added a "Two modes — principal-self vs penguin-spawn" section. `players/jebrim/research/_about.md` and `players/zezima/research/_about.md` created (parallel content; can diverge per character later). `meta/layer-routing.md` extended with the research row and a new *Research vs bank* paragraph in *Operational consequences* — the *"2,000-word writeup vs four-sentence pick"* framing.

**Chunk C — hook enforcement.** `gielinor/.claude/hooks/penguin-write-boundary.py` shipped, structurally parallel to `gnome-write-boundary.py`. Allowed prefixes: research/, quest-log/, inventory/. Blocked substrings: confirmed/, bank/, all other drafts/, proposals/, rejected/, keepsake/, lorebook/, examine/, niksis8_character/, niksis8/, meta/, spellbook/rituals/, body files, `.claude/*`. Gates on `agent_type == "penguin"` per the S020 payload-field gating pattern. `block-sub-spawn.py` refactored from binary check to `ROLE_PLURALS` mapping (penguin added cleanly). `gielinor/.claude/settings.json` PreToolUse wired the new hook alongside dwarf/gnome boundary checks.

**Chunk D — agent config + spawning-penguins skill.** `gielinor/.claude/agents/penguin.md` shipped (frontmatter: `name: penguin`, `tools: Read, Edit, Write, Glob, Grep, WebSearch, WebFetch`; system prompt covers read-first list, write boundary, tool surface, operating discipline, reporting format, what-not-to-do). `gielinor/spellbook/skills/spawning-penguins.md` shipped, parallel to spawning-dwarves and spawning-gnomes. Heuristic: external work required AND (>5 fetches OR ≥2 independent clusters OR wall-time pressure). Briefing template, channel discipline (background by default), status-on-ping (tail-since-last), anti-patterns.

**Chunk E — visualizer + hook.** Biggest mechanical surface area. `developer-braindead/.claude/hooks/emit-event.py` added `PENGUINS_PATH`, added ROLE_CONFIG entry for penguin, and **generalized** `spawn_kind_from_tool_input` and `attribute_to_subagent` from gnome-or-else binaries to `in ROLE_CONFIG` lookups — the comment block at line 65 prophesied this exact move ("currently a binary gnome/else split — generalize to a mapping if a third kind lands") and it cashed in cleanly. `developer-braindead/experiments/visualizer/index.html` extended across many surfaces: CSS palette + COMMS tint family for penguins; tab dot, filter, speaker bullet, COMMS tab declaration; new building **iceberg** at (1480, 220) — NE corner, mirroring Braindead's workshop in the NW — with terrain-style render (glacier mound, three peaks, ice cracks, snow caps, KGP flag banner, intel scroll + fish at base); `spawnPenguin` / `despawnPenguin` (tuxedoed silhouette, scarf in spawn color); penguin nodes/counts + reset hooks; `isPenguinActor` + `isSubAgentActor` extension; `ensureActorExists` P\d+ filter; `actorAccentColor`, `actorDisplayName`, `speakerFor`, `deriveSpeaker` extended; `applyEvent` dispatch.

## Why this shipped now

The skill came up organically — the principal needs research support for work-flavored tasks (EU Tender 2026 has been chewing on this surface for weeks). The role escalation came once the skill existed and was clearly cross-player. The naming arc (researcher → wizard → Reldo → penguin) stabilized once the RS-race lineage clicked.

The principal said *"do it all at once"* after the five-chunk sequencing question, which was an explicit license to bundle. The S029 carry-over observation (*"bundle big structural decisions; resist piecemeal landing"*) cashed in here — visualizer touched in the same pass as the role definition and the hooks.

## Observations to carry

- **Discipline rules pay off when consulted.** The `players/_about.md` rule (*"don't pre-create speculative players"*) stopped a wrong first move. The principal had a real need; the rule routed it to the right shape (skill + sub-agent role, not new player). Worth noting: surface this rule early when "new player" or "new role" cues land — it's cheap to read and the principal benefits from being asked.

- **Predictive comments in code pay off.** `emit-event.py` line 65 said *"generalize to a mapping if a third kind lands"* — written when gnomes shipped in S019. Two sessions later, penguins land, and the comment becomes a checklist. Worth doing more of this kind of forward-thinking documentation: when a structure could obviously grow, name the growth pattern in-place.

- **Naming arcs are cheap if surfaced.** Reldo → penguin took 30 seconds of principal time and reshaped the metaphor cleanly. Don't lock naming early; let the principal iterate while the architectural work is still in design.

- **Research vs bank — the source/picking split.** The principal's correction (*"research needs its own place to live"*) was structural, not cosmetic. Treating research as source material and bank notes as picked claims gives both layers a clean purpose: research has size, bank has browsability. The picking-during-alching flow operationalizes the split. Carry this principle to other "size-vs-browsability" tensions if they surface.

- **Five-chunk bundle held together.** No mid-pass discoveries forced re-sequencing. The pre-flight survey (read modes.md, write-rules.md, layer-routing.md, players/_about.md, the existing hooks, the existing agent config, the spawning-dwarves and spawning-gnomes skills) gave a complete map of touch points before the first edit. Worth keeping the pattern: for large bundles, read the cascade before writing.

- **The visualizer's ROLE_CONFIG generalization is the kind of payoff that "structure-first, content earns its way in" predicts.** S019's gnome-or-else binary was the right shape *at the time* (two roles). When penguins arrived, the binary became wrong and was generalized in two-line edits. The comment kept the upgrade path visible the whole time.

## Cascade

`gielinor/`:

- `meta/modes.md` — penguin role added; principal/dwarf/gnome/penguin axis everywhere; Principle line rewritten.
- `meta/write-rules.md` — research row in per-layer table; penguin row in hooks-enforce list.
- `meta/layer-routing.md` — research row + Research vs bank paragraph.
- `meta/death-and-spawn.md` — research preserved across reset.
- `CLAUDE.md` — six architectural guarantees (was five); per-player layer index includes research/.
- `players/_about.md` — research/ in per-player template; new section explaining the layer.
- `players/jebrim/research/_about.md` (new).
- `players/zezima/research/_about.md` (new).
- `spellbook/skills/research.md` — amended.
- `spellbook/skills/spawning-penguins.md` (new).
- `.claude/agents/penguin.md` (new).
- `.claude/hooks/penguin-write-boundary.py` (new).
- `.claude/hooks/block-sub-spawn.py` (ROLE_PLURALS refactor).
- `.claude/settings.json` — PreToolUse extended.

`developer-braindead/`:

- `bank/decisions/D-021_penguins_research_subagent.md` (new).
- `quest-log/S030_penguins_subagent_and_research_folder.md` (this file).
- `.claude/hooks/emit-event.py` — ROLE_CONFIG entry; spawn-kind + attribute generalization; predictive-comment refresh.
- `experiments/visualizer/index.html` — extensive (iceberg, penguin sprite, full wiring; see Chunk E in [[D-021_penguins_research_subagent]] for the surface list).
- `respawn.md` — next concrete step + carry-over rewritten.

## Next session

Live test the new role. The whole shipped surface (hook routing, write-boundary enforcement, visualizer spawn/despawn, sprite rendering at Iceberg, research file landing in player's research/, COMMS tab attribution) is untested under live conditions. Spawn a penguin from a Jebrim session with a small research brief and watch.

If live test passes, Step 2 of the existing respawn carry-over (scale up the map) needs revisiting — the iceberg pushes the map farther east; the viewport may need adjustment. Step 3 (Guthix live test) and Step 1 (parallel Braindead live test) remain pending.
