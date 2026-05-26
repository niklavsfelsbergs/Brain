# Obsidian fit + link-migration spec

> 2026-05-26, dev-brain session (braindead-b53fca39). Research + design. Captures the Obsidian-fit investigation and specs the one-time link migration that would make the *existing* brain resolve in Obsidian. **No execution — this is the thing to review before anything runs.**

## TL;DR

- The brain is already an Obsidian-shaped vault (markdown + folders + `[[wikilinks]]`). Adopting Obsidian is *pointing a lens at the files we already have*, not a migration of format.
- **Topology: per-brain vaults** (`gielinor/` and `developer-braindead/` as two separate vaults). This is the natural setup and the one that resolves cleanly. A single combined repo-root vault is the wrong model (it manufactures cross-brain `D-NNN` collisions that don't exist in practice).
- **Stock Obsidian resolves `[[links]]` by exact filename.** Our dominant link is the *ID-prefix* (`[[D-027]]`, `[[S060]]`), and the files are `D-027_<slug>.md` — so out of the box those show as **unresolved/phantom** links. Only the ~9% that are already exact-filename links (`[[guthix]]`, `[[archive-discipline]]`) resolve untouched.
- **Forward-convention alone does nothing for existing files** — they stay present and readable but unlinked in the graph. To light up history you need a **one-time migration**, which is a **link-TEXT rewrite (not file renames)** → the hooks/cockpit that parse `SNNN_sid8_slug.md` filenames are untouched. It's a deterministic script, volume-immune.

## The measured picture (per-brain vaults)

Modelled Obsidian's resolver against all 1,146 `[[link]]` occurrences, each brain as its own vault, prefix-aware (i.e. what resolution looks like *after* a migration maps `[[D-027]]`→its file):

| Bucket | Share | Disposition |
|---|---|---|
| In-vault unique (`[[D-027]]`→one file) | 71% | **Auto-rewrite** — deterministic |
| In-vault "ambiguous" | 7% | Almost all are **conventions**, not dupes (see below) |
| Code-file refs (`[[backend.py]]`) | 7% | **Leave** (or stop authoring) — not note links |
| Dangling (no file) | 7% | **Leave/flag** — forward-refs, planned notes, typos |
| Cross-brain (resolves only in other vault) | 4% | **Leave/flag** — mostly root `docs/` describing both brains |
| Placeholders (`[[D-NNN]]`, `[[ID]]`) | 4% | **Leave** — literal template syntax in the rulebook |

Stock-Obsidian (exact-match, pre-migration) resolution is ~9%; the 71% is the post-migration target.

### The "ambiguous" bucket is mostly deliberate structure — do not renumber

- **Sub-agent run-logs share the session ID by design**: `S034` → main entry + `S034_d1_maersk`, `S034_p1_*`, `S034_g2_alching`, etc. (dwarf `_dN`, penguin `_pN`, gnome `_gN`). A `[[S034]]` link means "session 34" and should resolve to the **main entry**.
- **Quest + `inventory/` resume pairs** (`S023` quest + `S023-...-resume.md`) — the [[D-024_parallel_player_coordination]] convention.
- **Genuinely careless duplicates** (after stripping conventions): dev-brain quests `S038`, `S060`, `S086` (parallel-session renumbering residue) + decisions `D-001/D-002/D-012` — and even those decision pairs look like a **separate legacy series** living in `bank/main-brain-construction/` and `bank/drafts/`, not the canonical `bank/decisions/`. Knowable today, bounded, won't grow if IDs stay unique going forward.

## The mechanism choice (the decision I need)

How a migrated `[[D-027]]` is made to resolve. Two viable mechanisms; one sub-knob.

### Option A — full-stem link rewrite  ← recommended
Rewrite `[[D-027]]` → `[[D-027_inward_outward_build_imbalance]]` (the bare ID becomes the actual filename stem).
- **Pro:** stock Obsidian, **zero plugin dependency**, resolves natively, works in *any* markdown tool. **Aligned with the brain's no-lock-in / plain-text-forever ethos** — the links survive even if Obsidian disappears.
- **Con:** raw links get longer; large one-time body churn in git. Mitigant: the verbose form *is* the descriptive filename the agent already reads, so it introduces no new vocabulary.

### Option B — frontmatter aliases + resolver plugin
Add `aliases: ["D-027"]` to each file; keep `[[D-027]]` links as-is.
- **Pro:** raw markdown stays terse (`[[D-027]]`) — kindest to the *primary* reader (the agent reads raw `.md` far more than anyone reads it in Obsidian).
- **Con:** Obsidian **core does not resolve bare links against aliases** (confirmed — aliases only feed autocomplete), so existing bare links need a **community plugin** to resolve. Plugin = a fragility (one such alias-resolution plugin was reported breaking across versions) and a dependency the no-lock-in ethos dislikes. Also requires adding frontmatter to ~every file (most have none today).

**Recommendation: Option A.** A system that prizes "readable as plain text even if the tool vanishes" should not put its core navigation behind a plugin. The verbosity cost is real but modest (it's the filename you already have); the dependency cost of B is structural and permanent.

**DECIDED (2026-05-26): Option A — full-stem rewrite, no plugin.** Principal chose the dependency-free / ethos-aligned path.

### Sub-knob: display alias
- `[[D-027_inward_outward_build_imbalance]]` — bare. Renders verbose *in prose* ("see D-027_inward_outward_build_imbalance for…").
- `[[D-027_inward_outward_build_imbalance|D-027]]` — keeps prose reading "[[D-027_inward_outward_build_imbalance|D-027]]", at the cost of the most verbose raw form.
- **Lean:** bare stems for standalone refs; the script *can* preserve a `|D-027` display where the link sits inline in prose, but that's a nicety, not load-bearing. Decide during dry-run review.

## The algorithm

1. **Index per vault.** Build two maps from the vault's `.md` files: exact-stem → file, and leading-ID-token (`^[A-Z]{1,2}-?\d+`) → files.
2. **Walk every `[[link]]`** (skip fenced code blocks so example syntax isn't rewritten). Strip `|display` and `#anchor` to get the target; classify:
   - **Exact-stem match** → already resolves, leave.
   - **1:1 ID-prefix** → rewrite to the full stem (Option A) / ensure alias exists (Option B).
   - **Convention group** (ID-prefix → many files) → resolve to the **main entry**:
     - *Quests:* the file whose stem matches `S\d+_(\d{4}-\d{2}-\d{2}|[0-9a-f]{8})_…` and is **not** a `_[dpgf]\d+` sub-entry and **not** `-resume`. If **>1 main** exists → real dupe → **flag for human** (this cleanly isolates [[S038_brain_underutilization_diagnosis|S038]]/[[S060_brain_self_audit_and_plan_reconciliation|S060]]/[[S086_e668ec7e_brain-technical-docs|S086]]).
     - *Decisions:* the file under canonical `bank/decisions/` wins; `main-brain-construction/` + `drafts/` copies → flag.
   - **Cross-brain / code-ref / placeholder / dangling** → leave; list in the report.
3. **Dry-run report first** — counts per bucket, a unified-diff preview of proposed link rewrites, and an explicit "needs human" list (the ~6 known-ambiguous items). **Nothing is written in dry-run.**
4. **Apply on a branch** after review. Edits are link text only; **no file renames, no deletes** (archive-discipline intact; fully reversible via git).

### What it never touches
Filenames (→ hooks/cockpit safe), code-file `[[ ]]` refs, placeholder tokens, and anything in the "needs human" list until a human rules.

## Pilot

Smallest proof that lights up a real vault:
1. **dev-brain `D-` decisions only**, Option A, dry-run → review the diff + the [[D-001_two_brain_split|D-001]]/002/012 legacy question.
2. Apply on a branch; open `developer-braindead/` as an Obsidian vault.
3. Confirm: the decision graph wires up, backlinks populate (`D-027`'s backlinks now list every file that referenced it), unresolved count drops to the known-flagged set.
4. Decide from there whether to extend to dev-brain quests, then to `gielinor/`.

Faithful to [[D-027_inward_outward_build_imbalance]]: this is bounded, reversible, and doesn't pull the team off the outward §C pilot — it's a dry-run + a branch, not a brain-wide sweep.

## Forward convention (worth doing regardless, Obsidian or not)
- IDs unique **within** each brain (the parallel-session SNNN slips are the only thing to prevent).
- Stop wiki-linking code files (`[[backend.py]]`).
- Sub-entry `SNNN_dN/_pN/_gN` sharing the session ID is **intentional** — documented here so a future reader (or the migration script) treats `[[SNNN]]`-resolving-to-many as by-design.

A `D-NNN` decision can formalize the chosen mechanism + this convention once the mechanism is picked.

## Status — 2026-05-26 ([[S098_b53fca39_obsidian_fit_and_dlink_migration]])

- **Mechanism DECIDED:** Option A (full-stem, no plugin). [[D-004_stable_ids]] **amended** to match (stable-ID core kept; "short-ID-alone is canonical" clause retired; original preserved).
- **Pilot DONE:** dev-brain `D-` decision links migrated — **341 `[[D-NNN]]`→full-stem across 97 files** (link-text only; no file renames → hook/cockpit filename parsing untouched). Auto for 27 1:1 IDs + [[D-012_close_session_harvest_pump|D-012]]; [[D-001_two_brain_split|D-001]]/[[D-002_folder_name|D-002]] split by the "main brain" qualifier (the `bank/main-brain-construction/` mirror overloads those IDs); code-fenced + convention-doc illustrative occurrences excluded/hand-edited (`bank/_about.md`, `spellbook/entry-formats.md`, [[D-004_stable_ids|D-004]]/[[D-006_dev_brain_restructure|D-006]] real-refs).
- **QUESTS DONE ([[S099_acf8fc80_obsidian_quest_link_migration]], 2026-05-26):** dev-brain quest (`S-`) links migrated — **357 rewrites across 87 files** (327 clean `[[SNNN]]`→main-entry + 30 per-occurrence dupe disambiguations). The `SNNN_dN/_pN/_gN` run-logs fold to the main entry; the 3 real dupes ([[S038_brain_underutilization_diagnosis|S038]]/[[S060_brain_self_audit_and_plan_reconciliation|S060]]/[[S086_e668ec7e_brain-technical-docs|S086]]) were resolved **per-occurrence by the authors' own context tags** (principal-signed-off), not renumbered — no file renames. [[S049_17e701eb_visualizer_state_aware_motion_and_action_line|S049]] was a 4th ambiguous group but moot (0 inbound links). Script saved + generalized over ID prefix (reusable for the gielinor pass): `bank/research/obsidian-link-migrate.py`.
- **VERIFIED IN OBSIDIAN ([[S099_acf8fc80_obsidian_quest_link_migration]], 2026-05-26):** opened `developer-braindead/` as a vault (per-brain topology, the decided model) — the decision + session graph wired into **one connected web** with hubs at the most-referenced files ([[D-027_inward_outward_build_imbalance|D-027]]/plan/respawn/build-lessons); only the expected orphans remain (code-refs, placeholders, no-link files). Closes the §O.2 + §O.3 verify gate.
- **NEXT:** (1) extend to **gielinor/** (§O.4 — its own vault, the larger surface; reuse the script, `--vault gielinor/`). Expect more dupes there (per-player `SNNN` numbering may collide across players) — dry-run will surface them. (2) two fuzzy [[D-001_two_brain_split|D-001]] calls (`plan.md:29`, `S003:13`) left as-set — both resolve. (3) cross-brain ~4% refs decision. Roadmap: [[plan]] §O.
- **Lesson:** the migration script must exclude the docs that *describe* the convention — it clobbered this spec's own illustrative examples on the first run (fixed). Link-text rewrite ≠ file rename.
