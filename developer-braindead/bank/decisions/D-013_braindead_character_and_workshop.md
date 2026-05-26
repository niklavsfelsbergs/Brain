# D-013 — 2026-05-21 — Braindead the construction crew + the Workshop building

**Context.** [[S011_visualizer_intent_narration]] gave gielinor actors speech bubbles for intent. The remaining honesty gap: dev-brain sessions writing to `gielinor/` paths showed up as the wisp — same sprite as gielinor's own unscoped self-tending sessions. Two structurally distinct situations rendered identical. Niklavs asked for the dev brain to have its own sprite in the visualizer, walking around gielinor when it modifies the main brain.

**Decision.** Give the dev brain a named character — **Braindead** — with his own sprite, his own building (**the Workshop** in the top-left of the map), and his own session-mode marker that tells the hook when to spawn him.

Three knobs (settled in chat with Niklavs):

- **Sprite flavor.** Quirky tinkerer — head wrap with dangling end, goggles pushed to forehead, hammer in right hand, rolled blueprint in left, slate-blue robe over a wood-dark belt with a bandage pouch. Reads as "construction crew," matches the cheeky name, visually distinct from both player avatars (Jebrim's wizard hat / Zezima's hooded silhouette) and the wisp's floating orb.
- **Building.** New isoBuilding entry at `(140, 140)` (top-left corner, well above Inbox Square), labeled "The Workshop." Small footprint (w=38, d=22, h=38, r=14) — a shack, not a hall. Scaffolding poles on the SE side rising above the roof line with crossbeams; a propped plank from scaffold to ridge; sawhorse with a half-cut plank on the SW; toolbox at the SE ground; blueprint pinned to the SW wall; a single lit window. Slate-blue/wood-dark roof palette matching the sprite robe so the building "belongs to" Braindead visually.
- **Mode marker.** Sidecar file `brain/.claude/active-mode.txt`. Agent writes `dev-brain` on dev-brain entry (per `developer-braindead/spellbook/respawn-ritual.md` step 5) and `unscoped` (or empty) on session close (step 6 of `session-close.md`). Hook detects the write, reads the file, and on transitions emits `spawn-braindead` (entering dev-brain mode) or `despawn-braindead` (leaving). Soft enforcement — visualizer concern, not architectural.

**Alternatives considered.**

- **Robed master architect with scroll.** Quieter, more dignified, more aligned with the player avatars. Rejected because the name "Braindead" pulls in the opposite direction — the silhouette should agree with the name, not fight it. Architect would be a fine v2 if the name ever softens.
- **No new building; Braindead parks at last gielinor building visited or despawns when work crosses out of gielinor/.** Cheaper, no pixel art. Rejected because Niklavs wanted the dev brain to have a home visible on the map — option 2c in the earlier discussion. The workshop also makes "dev-brain mode is happening" legible at a glance.
- **Bottom-left or top-right corner.** Symmetric to inbox-square; either fine. Niklavs picked top-left (Braindead lives north of Inbox Square, near where Jebrim awakens). No deep reason.
- **Mode-marker as a single JSON `{mode, player}` rather than plaintext.** Considered. Plaintext is simpler to write, easier to grep, easier to debug. Single line, lowercased, stripped. The hook reads only the first line.
- **Auto-detect dev-brain mode from path patterns (e.g., the agent touches files under `developer-braindead/` so therefore dev-brain).** Rejected: gielinor sessions occasionally read dev-brain files (cross-reference allowance per brain-root CLAUDE.md), and a passive misclassification would create spurious Braindead spawns. The explicit marker is honest about session intent.
- **A hook that emits Braindead at the start of every Claude Code session at brain/ root.** Rejected: brain-root sessions can be either gielinor or dev-brain. The marker is what disambiguates.

**Consequences.**

- New CSS color tokens: `--braindead-robe`, `--braindead-robe-dk`, `--braindead-bandage`, `--braindead-goggle`, `--braindead-hammer`.
- New `<g id="braindead">` sprite in defs (pixel-art SVG, billboard convention shared with jebrim/zezima/wisp).
- BUILDINGS / STAND / LABEL_Y_OFFSET each gain a `braindead-workshop` entry. New `buildBuildings()` block draws the workshop via isoBuilding with custom details (scaffolding, sawhorse, toolbox, blueprint, lit window).
- Engine state: `braindeadActive`, `braindeadNode`. `spawnBraindead(ev)` / `despawnBraindead()` mirror the wisp lifecycle. `applyEvent` cases for `spawn-braindead` / `despawn-braindead`. `deriveSpeaker` returns 'braindead' when active.
- `path-map.json` reorders rules: `/developer-braindead/experiments/` keeps routing to spellbook-tower (visualizer work belongs in the spell-tower per S008/S009 framing); everything else under `/developer-braindead/` routes to braindead-workshop. Individual dev-brain root-file rules (CLAUDE.md, _about.md, respawn.md) are removed — they now fall through to the workshop, which is more correct. New actorRule `/developer-braindead/` → braindead. The default actor stays `wisp`; the hook applies the mode-marker on top — when active-mode is `dev-brain` and no actorRule matched, the actor flips to `braindead`.
- Hook (`emit-event.py`) grows two functions: `read_active_mode()` (reads the first line of `active-mode.txt`, lowercased+stripped) and `handle_active_mode_write()` (detects writes to the marker, reads contents, compares to `state-actors.json["_mode"]`, emits spawn/despawn events on transition and persists the new mode). `handle_write_or_read` checks the marker write first, then intent, then path-classify; after classification, the mode-marker overrides default actor.
- Protocol additions: `developer-braindead/CLAUDE.md` gains a "The visualizer marker" section naming Braindead and stating the marker convention. `spellbook/respawn-ritual.md` gains step 5 (write marker on entry); `spellbook/session-close.md` gains step 6 (clear marker on close).
- Gitignore: `.claude/active-mode.txt` added alongside the existing intent-file rule (both transient, both visualizer-only).
- The "construction crew" framing also corrects a stale claim in the old dev-brain CLAUDE.md scope section ("does not modify gielinor/ from this brain") — main brain changes routinely happen from dev-brain sessions, and the brain-root CLAUDE.md already permits this. The scope section now reflects reality.

**Open follow-ups (deferred).**

- **Workshop interior reveal.** If Braindead lingers in the workshop, hover-zoom or a separate panel could surface what he's working on (recent dev-brain writes, pending decisions). Decide once we've watched a few live sessions.
- **Multi-architect future.** If another build-assistant character ever joins (e.g., a dedicated "Linter" or "Reviewer"), the workshop scales: same building, more sprites. Don't design for it now.
- **Bootstrap stale-mode handling.** If `active-mode.txt` is stale from a crashed session (still says `dev-brain` but the new session is gielinor), bootstrap-from-tail will show Braindead in the workshop until the new session writes the marker. Tolerable for v0; revisit if it confuses.
- **Gielinor side writing the marker.** Currently only dev-brain writes the marker (and only on entry / close). Gielinor sessions don't touch it. If we later want gielinor sessions to update it (e.g., to `jebrim` / `zezima` / `unscoped` for richer hook context), that's a small addition to `gielinor/spellbook/rituals/respawn.md`. Defer until there's a use case.

**Session ref.** [[S012_braindead_character_and_workshop]] (in progress).
