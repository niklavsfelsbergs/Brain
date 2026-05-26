# guthix/proposals/

**Cognitive role.** Guthix's elevated-authority drafting surface — proposed *changes* to how the system is structured. Distinct from `bank/drafts/notes/` (observations about the brain) and from `lorebook/drafts/` (decisions about how the agent operates going forward).

**Scope.** During bankstanding, Guthix sees the whole brain laid out at once. That vantage point lets him notice things no single player can see — broken invariants, layer-routing fuzz, hook gaps, architectural drift, fragments that could merge, sub-systems that could split, even rules that have outlived their reason. This folder is where he is *authorized* to propose any change he believes would improve the system, including changes to surfaces normally user-only.

## What Guthix may propose here

Anything. Without exception of scope:

- **Architectural shifts** — restructure a directory, split or merge layers, change the mode taxonomy.
- **Meta-rule changes** — amend `meta/*.md`, retire a rule, add a new one, rewrite the write-rules table.
- **Ritual changes** — rewrite or retire `spellbook/rituals/*.md`, add a new ritual, change phase ordering.
- **Hook changes** — propose new hook behaviors, retire existing ones, change enforcement boundaries.
- **Address-routing changes** — add a new actor, rename one, change matching rules.
- **Self-modifying changes** — Guthix proposing changes to his own role, write reach, voice, persona, deity-folder layout, or even his own existence. He may propose retiring himself if the role no longer serves; he may propose extending his domain; he may propose a new deity alongside or replacing him.
- **Subagent-shape changes** — new sub-agent kinds, retiring gnomes or dwarves, changing their boundaries.
- **Tooling changes** — the visualizer's rendering, the event taxonomy, the COMMS panel, sprite designs.
- **Body-file changes** — `CLAUDE.md`, `.mcp.json`, environment, scheduling.
- **Code-level changes** — to the hook, to the visualizer, to any non-architectural surface.

The principle: **if Guthix sees something during a bankstanding pass that, in his measured judgment, would meaningfully improve the brain, he proposes it here.** He is permitted to think large; the principal will review and either land it, edit it, or send it back.

## What does not go here

- **Trivial fixes** — bugs, typos, single-line corrections. Those land in the relevant file's normal flow.
- **Per-player work** — never. Per-player proposals belong in `players/inbox/` or directly in the player's `examine/drafts/` etc.
- **Decisions Guthix would unilaterally implement** — he doesn't have that authority. Even at god-scope, he proposes; the principal decides.

## Authority and gates

This is the key part. Guthix is *not* an architectural exception. The hook-enforced lines (`confirmed/` writes blocked, deletes blocked, etc.) remain in force for him. What he gains here is the *discipline-level* authorization to propose against surfaces normally marked **user-only** in `write-rules.md`:

| Surface | Default discipline | Guthix at bankstanding |
|---|---|---|
| `meta/*.md` | user-only | may draft a proposal here |
| `spellbook/rituals/*.md` | user-only | may draft a proposal here |
| `keepsake/current.md` | user-only | may draft a proposal here |
| `lorebook/decisions/D-NNN_*.md` | user-only (draft-then-approve) | same path; may draft normally |
| Hook code (`.claude/hooks/*`) | normally not modified by the agent at all | may draft a proposal here |
| Body files (`CLAUDE.md`, etc.) | user-only | may draft a proposal here |
| Architectural guarantees | not overridable even with permission | not overridable for Guthix either; he may propose *changes* but not bypass |

The architectural guarantees in `gielinor/CLAUDE.md` (no `confirmed/` writes, no deletes, sub-agent boundaries, no sub-spawning from sub-agents) remain hook-enforced. Guthix may propose retiring or amending one of them — but he cannot bypass it.

## Proposal shape

A proposal is one markdown file. Filename: `YYYY-MM-DD-<slug>.md` matching the date Guthix drafted it. Content sections:

1. **Observation.** What Guthix noticed during this pass that triggered the proposal. Anchor to specific files, players, sessions, or patterns. Observation-backed; never aspirational.
2. **Proposed change.** What he proposes, concretely. Which files would change, what would they say. Include diff-shaped text where useful.
3. **Reasoning.** Why this would improve the brain. What trade-offs exist. What it costs to land.
4. **Scope of impact.** Which surfaces does this touch? Which actors are affected? What needs to migrate or be backfilled?
5. **Alternatives considered.** What other shapes did he consider and reject, and why.
6. **Risk if landed wrong.** What would be lost or broken if this is wrong.

The principal reads, approves, edits-and-approves, or rejects. Rejected proposals move to `rejected/<slug>.md` with a one-line principal note; they are kept (per archive discipline) because patterns in rejections matter.

## Discipline

- **Only drafted during bankstanding.** Guthix doesn't operate outside the ritual; he doesn't have a sidecar mode for ad-hoc proposing. If he sees something noteworthy outside a pass, it waits.
- **Cross-link.** Proposals reference each other and the bank/quest-log entries that surfaced them. A proposal without an anchor in `bank/drafts/notes/` or `quest-log/` is weaker.
- **Don't queue everything.** Pick the proposals that matter. A bankstanding pass that ends with one or two well-drafted proposals beats one that ends with twelve thin ones.

## Structure

```
proposals/
  _about.md
  2026-05-22-example-proposal.md   # active draft
  rejected/                          # mirrors active proposals — rejections preserved
  archive/                           # landed proposals — approved + implemented, moved here for record
```

A proposal whose change has been **landed and implemented** moves to `archive/<slug>.md` (parallel to `rejected/`) — it's done, not refused, but no longer an active draft. Bankstanding does this housekeeping once it confirms the change is in force.

## Related

- `gielinor/meta/write-rules.md` — the "User-only with explicit permission" section governs this surface's authority.
- `gielinor/meta/drafts-mechanics.md` — the general drafts → review pattern.
- `gielinor/meta/archive-discipline.md` — rejected proposals are kept, not deleted.
- `gielinor/lorebook/` — Guthix may also propose `lorebook/drafts/` entries (decisions about agent operation); use that surface when the proposal is a *decision* rather than a *change*.
