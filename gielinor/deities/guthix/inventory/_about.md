# guthix/inventory/

**Cognitive role.** Working memory for the in-progress bankstanding pass. Where-we-are state that needs to survive between turns and (occasionally) between sessions when a pass spans more than one.

**Volatility.** More durable than a player's inventory (which is volatile by design and resets on death-as-reset) because a bankstanding pass *should* be resumable across crashes. Less durable than `bank/` — once the pass closes, contents either clear or migrate into the matching quest-log entry.

## What goes here

- **Phase tracker.** "Phase 0 done for Jebrim; Zezima next." "Drafts triage covered examine/ and niksis8/; lorebook/ still pending."
- **Carry-forward findings mid-pass.** Observations Guthix wants to act on later in *this same pass* but isn't ready to draft yet.
- **Resume-from-here pointer.** A single canonical "what next step" so a fresh session reading this folder knows immediately where the in-flight pass left off.

## What does not go here

- **Across-pass knowledge.** That graduates to `bank/drafts/notes/` and survives the pass close.
- **Decisions worth recording for the principal.** Those go to global `lorebook/drafts/`.
- **Per-player findings.** Even mid-pass — write straight to the per-player drafts (`players/<name>/inbox/`) if it concerns one player; keep inventory cross-cutting.

## Naming convention

When a pass is active, one file per resume topic. Default: `B-NNN-resume.md` matching the in-progress quest-log entry. Additional files only if the pass has parallel topics worth separating (uncommon).

## Lifecycle

- **Pass opens.** Guthix descends; creates `B-NNN-resume.md` with initial state.
- **Pass runs.** Files updated turn-by-turn as state shifts.
- **Pass closes cleanly.** Contents folded into the `quest-log/completed/B-NNN_*.md` entry; inventory cleared.
- **Pass abandoned mid-flight.** Inventory contents preserved with the `quest-log/archive/in-progress/B-NNN_*.md` entry — no information loss.

## Related

- `gielinor/meta/layer-routing.md` — what goes in inventory vs quest-log vs bank.
- `gielinor/players/<name>/inventory/_about.md` — the per-player analog (more volatile).
