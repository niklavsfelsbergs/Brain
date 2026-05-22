# 2026-05-21 — Observation harvest pump installed at close-session

## What changed

`gielinor/spellbook/rituals/close-session.md` gained a new step (step 6) that runs an observation harvest before commit. Four questions, agent-judged stability, cap 1–5 drafts, bias to less, empty-set valid. Drafts land in the appropriate per-layer `drafts/` or `proposals/` folder.

`gielinor/meta/write-rules.md` flipped the `bank/` layer from auto-write to drafts-gated. All bank-notes — harvest-derived or chat-initiated — now route through `bank/drafts/notes/` → alching promotes to `bank/notes/`. Uniform with identity-layer drafts pattern.

`gielinor/spellbook/rituals/alching.md` step 2 extended to triage `bank/drafts/notes/` before reviewing `bank/notes/` for staleness. A new step 6 added for skill graduation — walking confirmed identity layers + completed quest logs for patterns that have repeated and earned a name.

`gielinor/meta/modes.md` alching mode scope adds `spellbook/skills/` to the active player's write reach.

Per-player `bank/_about.md` files (Jebrim, Zezima) updated to describe the drafts gate. Per-player scaffolds added: `bank/drafts/notes/`, `bank/rejected/notes/`, `spellbook/skills/drafts/`.

## Why

The first Jebrim alching pass (2026-05-21) executed correctly and surfaced near-empty rooms across every layer except quest-log. The procedure was right; the procedure assumed a draft pile that didn't exist.

Diagnosis: three population pumps run the brain. Pump 1 (per-turn quest-log) works. Pump 3 (per-ritual integrative: alching + bankstanding) was structurally fine but assumed Pump 2 had populated draft folders. Pump 2 (per-close harvest) didn't exist — close-session reconciled, tightened, surfaced existing drafts, committed, but never *created* drafts from session observation. Without Pump 2, the alching/bankstanding rituals found empty rooms regardless of how often they ran.

Pump 2 is the keystone. Installing it lets the rituals downstream actually do work.

## What triggered it

Concrete moment: 2026-05-21, Jebrim alching pass. Step 1 (identity drafts) found 0 in each of three folders. Step 3 (quest-log compression) found `completed/` empty. Step 5 (rejected patterns) found `rejected/` empty. The pass terminated cleanly but produced nothing. Surfaced to Niklavs as "the procedure assumed a state that didn't exist."

Niklavs cued the deeper question: "How could we actually make sure that all repos are growing organically?" The discussion produced the three-pumps frame, identified Pump 2 as the gap, and resolved into [[D-012]] (dev brain).

## What was affected

- `gielinor/meta/write-rules.md` (bank row flip + principle softening + enforcement note)
- `gielinor/spellbook/rituals/close-session.md` (new step 6, renumbering 6→7, 7→8, 8→9, 9→10)
- `gielinor/spellbook/rituals/alching.md` (step 2 extension, new step 6 for skill graduation, old step 6 → step 7)
- `gielinor/meta/modes.md` (alching mode scope adds `spellbook/skills/`)
- Per-player `bank/_about.md` files (Jebrim, Zezima — drafts-gate description)
- Per-player scaffolds (`bank/drafts/notes/`, `bank/rejected/notes/`, `spellbook/skills/drafts/`)
- `developer-braindead/CLAUDE.md` (stale "does not modify gielinor" line corrected)

## Supersedes / superseded by

— (this is the lorebook's first entry of substance).

## Anchor

[[D-012]] in dev brain — full design rationale and alternatives considered. Decision packet: D1=A (in close-session), D2=B (player-scope first), D3=richer skim, Path 2 (one-tier bank gated), skill-graduation yes, cross-player drift deferred, cap 1–5 with bias to less.
