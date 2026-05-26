# S040 — 2026-05-22 — ideas/ folder at brain root

**Status.** Done. New folder + spec landed at brain root; capture/listing triggers wired into both brains' CLAUDE.mds and into `gielinor/meta/layer-routing.md`. Live-test pending (no idea captured yet via the trigger).

## What happened

- **Principal asked for a low-friction "ideas" sidecar.** Verbatim: *"We need an ideas folder in the root. They will be indexed by which player or whatever else thought of them. But I just want to be able to say note this idea and then move on. Then sometimes I can jus task what ideas i have had."* Pre-everything thoughts that don't fit the existing routing table — not drafts (no anchor), not quest-log narrative (not work), not keepsake (not load-bearing), not decisions (not settled). Just seeds.

- **Three load-bearing choices via `AskUserQuestion`.** (1) Location: `brain/ideas/` at the brain root, neutral between `gielinor/` and `developer-braindead/`. Rejected: gielinor-only (forces cross-write for Braindead) and split per-brain (most pure, worst friction for listing). (2) Shape: one file per idea, `YYYY-MM-DD-<actor>-<slug>.md`. Rejected: single per-actor append-only file (kills per-idea promotion) and one shared chronological log (simplest, worst for promotion). (3) Interface: phrase-trigger only — `note this idea: <text>` captures; conversational patterns (*"what ideas have I had"*) list. Rejected slash commands — discoverable but adds files for a feature meant to live in flow.

- **Spec written at `brain/ideas/_about.md`.** Canonical: file shape, capture trigger (colon required, anywhere in message), listing trigger (default grouping by actor newest-first, filters honored on ask), who-can-write (principals only — dwarves/gnomes/penguins don't capture, the agent does not preemptively label observations as ideas), what ideas are NOT (drafts/quest-log/keepsake/decisions), manual promotion path (graduated ideas move to `ideas/archive/promoted/` with destination stub; rejected to `ideas/archive/rejected/`; per [[archive-discipline]] never destroyed).

- **Wired into both CLAUDE.mds.** New "Capturing ideas" section in `gielinor/CLAUDE.md` between "How to tend the brain" and "The rulebook (imported)"; parallel section in `developer-braindead/CLAUDE.md` before "Cross-reference allowance". Each names the trigger, the listing patterns, and points to the canonical spec. Reaffirms principal-only.

- **Routing table updated.** New row at the tail of `gielinor/meta/layer-routing.md` for the "pre-everything idea" content shape pointing to `brain/ideas/`. Keeps the routing reference single-source — the agent consulting layer-routing during a session now sees ideas alongside drafts/quest-log/keepsake/decisions.

## Decisions explicitly not made

- **No D-NNN decision file.** Structurally small (one new folder, one spec, three short doc edits), reversible, and the user's framing was low-friction. A D-NNN entry would have been heavier than the change itself. If `brain/ideas/` grows enough to need a triage ritual or promotion automation, that future work earns its own D-NNN. Pattern: D-NNN tracks decisions worth re-reading; this one isn't.
- **No hooks.** `brain/ideas/` is not under any gated path. Discipline-only enforcement. If the agent starts pre-emptively labeling observations as ideas (the failure mode), tighten via a hook or a meta-rule then.
- **No `/idea` slash command.** Phrase trigger only, per principal choice. The slash command can be added later as a non-disruptive alternative if the phrase trigger misfires.

## Observations to carry

- **Trigger pattern asymmetry: capture is permissive (anywhere in message, colon required), address routing is strict (start of message only).** The asymmetry is justified by risk budget. A misfired address switches actor identity mid-session — high cost. A misfired idea capture writes a file you didn't want — low cost, never destroyed. Match strictness to consequence. Worth keeping in mind whenever a new conversational trigger gets specified: ask "what does a misfire cost?" before defaulting to strict.

- **"Don't pre-build for hypothetical scale" promoted from [[S030_penguins_subagent_and_research_folder|S030]] carry into a new spec.** The `_about.md` explicitly says *"If the folder grows to the point that browsing becomes painful, a triage ritual can be added then — not now."* Same posture [[S030_penguins_subagent_and_research_folder|S030]] used for the research/ folder ("no draft gate inside the folder"). When a new folder lands, name what won't be built — saves a future audit pass over speculative scaffolding.

- **Cross-brain sidecars get documented in both subfolder CLAUDE.mds, not only at the brain-root router.** `comms/`, `.claude/`, and now `brain/ideas/` follow the same shape. Reason: sessions opening inside `gielinor/` or `developer-braindead/` walk only that subfolder's CLAUDE.md per Claude Code's directory walk; brain-root CLAUDE.md doesn't load for those sessions. If a behavior must be reachable from inside both brains, document it inside both. Worth a short brain-design note next bankstanding — the pattern is consistent across at least three folders now.

## Files touched

- `brain/ideas/_about.md` — **new**, the canonical spec (~80 lines).
- `brain/gielinor/CLAUDE.md` — new "Capturing ideas" section.
- `brain/developer-braindead/CLAUDE.md` — parallel "Capturing ideas" section.
- `brain/gielinor/meta/layer-routing.md` — new row in routing table for pre-everything ideas.

## Open items / deferred

- **Live test the capture trigger.** Next session that has an idea, watch (1) whether the agent recognizes `note this idea:` mid-message vs. only at start, (2) whether actor attribution picks the right name across mode transitions (capture during a player→Guthix flip, capture by Braindead from inside gielinor edits, capture from unscoped). If trigger misfires, tighten in `_about.md`.

- **Promotion ritual.** Currently manual ("promote `<idea>` to <destination>"). If folder reaches >20 entries without much promotion, lift into a `/drafts`-like ritual at brain-root scope. No evidence yet; deferred.

- **`brain/ideas/archive/` directory not pre-created.** Created on first promotion or rejection. The `_about.md` describes the structure; the directories materialize when needed. Standard never-delete shape.

**Cascade.** `brain/ideas/_about.md` (new), `brain/gielinor/CLAUDE.md` (edit), `brain/developer-braindead/CLAUDE.md` (edit), `brain/gielinor/meta/layer-routing.md` (edit), `developer-braindead/quest-log/S040_ideas_folder_at_brain_root.md` (this entry), `developer-braindead/respawn.md` (refresh).

**Main-brain changes.** Three edits crossed into `gielinor/` — the CLAUDE.md "Capturing ideas" section and the layer-routing row. Discipline-level only; no identity surface touched, no canonical entry added. The shared sidecar at `brain/ideas/` lives outside both brain folders.
