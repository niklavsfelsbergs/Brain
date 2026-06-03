# Resume — shipping-agent access split (S101, jebrim-612683db)

## Status
in-progress — core done; carried forward on named deps (principal push + smoke-test + a dev-brain build).

## Where we are
Dual-access setup designed + built. One agent, two tiers off `picanova/shipping-agent`: colleagues on `ship_mart_ro` (gold-only); Niklavs full-access via a gitignored `CLAUDE.local.md` overlay + `.env` user `tcg_nfe` (verified live: USAGE+SELECT on enterprise_silver/bronze/dw/sl_gold/gold). Gold lineage mapped (builds at bi-etl `dags/shipping_mart/`; silver dominant + bronze source-systems + dw/sl_gold dims; `poc_dw` NOT a gold input). `.env` set to tcg_nfe (ship_mart_ro kept as commented toggle). Working model agreed: brain-in-the-loop, work in NFE, shipping agent called as a scoped specialist; teaching loop = edit its rulebook together. Harvest + a "calling the shipping agent" skill drafted.

## Next concrete step (blocked on principal / dev-brain)
1. Niklavs smoke-tests `tcg_nfe` auth: `python harness/connect_redshift.py --query "SELECT 1"` from shipping-agent/, then an upstream-only query to confirm the scope widening took.
2. Niklavs pushes the 2 HELD shared edits (`.gitignore` + `how_to.md` rule-10 conditional) to picanova/main — `git commit -- <pathspec>` on just those two (untracked `demo/` stays out).
3. DEV-BRAIN task: build a dedicated `shipping-agent` subagent type (agent def + cockpit sprite/label + write-boundary call) so a call is visibly distinct from a dwarf. Skill step 2 already points at it; ad-hoc dwarf is the fallback until built. (Principal said he'll call dev to work on this.)

## Files to read first
- `gielinor/players/jebrim/quest-log/in-progress/S101_612683db_shipping-agent-access-split.md` (full finding, decisions, lineage table, held state)
- shipping-agent: `CLAUDE.local.md` (the overlay), `how_to.md` rule 10, `.gitignore`, `harness/db.py`
- `gielinor/players/jebrim/spellbook/drafts/skills/calling-the-shipping-agent.md`
- bi-etl `dags/shipping_mart/`

## Drafts pending (await alching/triage)
- bank: `bank/drafts/notes/projects/2026-05-27-shipping-mart-gold-lineage-and-access-tiering.md`
- skill: `spellbook/drafts/skills/calling-the-shipping-agent.md`
- examine: `examine/drafts/2026-05-27-dont-over-formalize-reachable-capability.md`
- niksis8_character: `niksis8_character/drafts/2026-05-27-collaboration-first-brain-as-intelligence-layer.md`
- keepsake proposal: `keepsake/proposals/2026-05-27-routing-pin-mart-path-and-access-update.md`
- (also: cross-conv memory `dont-over-formalize-reachable-capability` written)
