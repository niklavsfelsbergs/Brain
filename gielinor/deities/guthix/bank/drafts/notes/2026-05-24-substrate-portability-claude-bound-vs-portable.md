# Substrate portability — what's Claude-Code-bound vs. portable

**As-of:** 2026-05-24 (B-006). Anchor: consultation this session — *"would my setup work with Codex or have I made it Claude-specific?"* Read across `.claude/settings.json`, `.claude/hooks/`, the cockpit launcher (`cockpit/web/term.js`), and the meta/ ruleset.

Cross-cutting knowledge about the brain itself: the split between what would survive a move to a different agent runtime (Codex, Gemini CLI, etc.) and what is wired to Claude Code specifically. Seed material for the unwritten `spellbook/rituals/ascension.md` (death-as-migration; see `meta/death-and-spawn.md`).

## The core distinction

The constraint is **the harness, not the model.** Any frontier model can *run* this brain — reading instructions, holding a persona, walking rituals, writing files in the right shapes is plain instruction-following. What varies between runtimes is the program wrapping the model, which decides whether the brain's **enforcement** and **observability** exist at all.

## Portable (substrate-neutral — moves nearly free)

- The entire cognitive architecture: the `gielinor/` + `developer-braindead/` split, the layer model (`bank/`, `quest-log/`, `examine/`, `keepsake/`, `lorebook/`, `inventory/`, `research/`), the RuneScape metaphor.
- The players/personas, the rituals (respawn, alching, bankstanding, close-session), the routing rules in `meta/`.
- All of it is markdown + discipline. The *mind* travels.

## Claude-Code-bound (would need re-implementation per runtime)

1. **Instruction loading** — `CLAUDE.md` + the `@import` directory-walk syntax. Codex reads `AGENTS.md`, no `@import`; rename and flatten the import chain.
2. **The hooks = the architectural guarantees** (the load-bearing dependency). Seven Python hooks (`block-confirmed-writes`, `block-deletes`, `dwarf`/`gnome`/`penguin-write-boundary`, `block-sub-spawn`, plus instrumentation) wired through Claude Code's `PreToolUse`/`PostToolUse`/`Stop`/`SessionEnd` events, reading its JSON payload (`agent_type`, tool name). Codex's extension surface is thinner — the "you cannot bypass them" guarantees would not carry over intact; some (sub-spawn block, per-agent-type write boundaries) may not be expressible at all.
3. **Sub-agents** — dwarves/gnomes/penguins are Claude Code's Task/Agent system with typed configs. No equivalent typed-subagent spawning elsewhere; the whole role axis rebuilds or drops.
4. **Slash commands & skills** — `.claude/commands/` (`/drafts`, `/rename`) and the Skill tool are Claude-format.
5. **Intent/visualizer sidecars** — keyed off `CLAUDE_CODE_SESSION_ID` for the `<sid8>` filenames; the COMMS feed is fed by hook-emitted events to `state.ndjson`. Different session identifier and no event stream elsewhere — the cockpit's live view goes dark until rewired.
6. **The cockpit** — `cockpit/web/term.js` launches `claude` / `claude --resume` in a PTY (the on-subscription pivot). It's a Claude launcher, not agent-neutral.

## The implication for migration

We built to **Claude Code's ceiling** — veto-hooks + typed subagents + an event stream — currently the highest extension surface in the field. The bitter irony: the part that *feels* most bespoke (the cognitive architecture) is the most portable; the boring plumbing (hooks) is the least. A migration loses the floor, not the soul.

An eventual `ascension.md` should treat migration as: brain content moves nearly free → rewrite the hook-enforcement layer against the target harness (with likely reduced guarantees) → drop or rebuild the sub-agent roles → rename `CLAUDE.md`→`AGENTS.md` and flatten imports → re-wire the cockpit launcher + event taxonomy. Budget the hook rewrite as the long pole.

## Related

- `meta/death-and-spawn.md` — death-as-migration is Phase 3; this note is its seed.
- `meta/modes.md` / `meta/write-rules.md` — the role boundaries and write discipline the hooks enforce.
- `.claude/settings.json` — the hook wiring this note describes.
