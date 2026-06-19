# D-036 — Guthix may write `confirmed/` during bankstanding/alching under a per-session floor-unlock grant

**Decided.** 2026-06-19, principal-authorized in a Guthix bankstanding ([[B-021_2026-06-19_bankstanding|B-021]]) that pivoted to dev-brain ([[S277_d371d189_guthix-floor-unlock|S277]]; Niklavs: *"why can't guthix act with my permission? He should be able to, i want to close everything during bankstanding."*). Extends [[D-034_guthix_executes_on_explicit_authorization|D-034]] — the one carve-out [[D-034_guthix_executes_on_explicit_authorization|D-034]] deliberately withheld.

## Decision

The `confirmed/`-write floor (`block-confirmed-writes.py`) gains a **second bypass** beside `braindead`: **Guthix, during bankstanding or its Phase-0 alching, under an explicit per-session principal grant.** With it, bankstanding becomes a one-stop "close everything" — Guthix promotes drafts to `confirmed/` (global identity drafts *and* the per-player examine drafts a Phase-0 gnome can only recommend) in-pass, instead of every promotion routing to the principal's own `git mv`.

## Mechanism — three independent AND-gates

A `confirmed/` write is honored for Guthix iff **all** hold (drop any one → the floor holds exactly as before):

1. `resolve_actor(sid8) == "guthix"` — players, wisp, sub-agents never qualify.
2. the `.mode` marker reads `bankstanding` or `alching` — consultation never qualifies.
3. a non-empty `.claude/intent/<sid8>.floor-unlock` marker exists — **the principal's explicit, session-scoped grant.**

Every honored write logs `bypass-guthix-authorized`. Test: `developer-braindead/verification/test_block_confirmed_unlock.py` (9 cases, in `run_tests.py`).

## Scope — `confirmed/` writes only

**Deletes are not covered.** `block-deletes.py` stays `braindead`-only. Bankstanding/alching archive, never delete, so Guthix never needs a delete — the never-destroy guarantee stays fully hard for him.

## Why

[[D-034_guthix_executes_on_explicit_authorization|D-034]] gave authorized-Guthix every *discipline-gated* surface but kept the *hook-gated* floor `braindead`-only — for a mechanical reason, not a trust one: **a PreToolUse hook can't read "the principal authorized this write."** It sees a tool, a path, a sid. So the floor stayed a binary actor check. The floor-unlock marker is that missing authorization signal made machine-readable: an explicit, deliberate, auditable, session-scoped artifact the hook *can* read. Bankstanding is already an interactive, principal-supervised, propose-then-approve ritual — the same safeguard ([[D-032_braindead_full_access|D-032]]'s) that justifies Braindead's floor bypass (principal sees the diffs, every change is git-reversible) holds here, now with an audit-logged grant on top.

## Guardrail — the marker *is* the permission record

- **Write the marker only on explicit, specific authorization** (*this pass, now*), never pre-emptively. Writing it unprompted is a discipline violation — the hook trusts it as Guthix's attestation that the principal said go.
- **Default holds without it:** propose, and let the principal `git mv`. No standing/blanket grant.
- **Clear at close** — empty/remove the marker alongside the `.mode` marker (a stale marker only affects its own `<sid8>`, but don't let the grant outlive the pass).

## Scope of impact

- `.claude/hooks/block-confirmed-writes.py` — the second bypass + `read_mode`/`floor_unlocked` helpers.
- `gielinor/spellbook/rituals/bankstanding.md` — the floor-unlock lifecycle (write-on-grant, clear-at-close, gnome note).
- `gielinor/meta/write-rules.md` + `gielinor/meta/guthix.md` — the carve-out in the floor statements.
- No change to Braindead's reach, to deletes, or to any other actor's boundary.

## Related

- [[D-034_guthix_executes_on_explicit_authorization|D-034]] — the precedent; D-036 supplies the *floor-bypass half* it withheld, scoped to bankstanding/alching + `confirmed/` writes.
- [[D-032_braindead_full_access|D-032]] — the `braindead` floor bypass this parallels (and the safeguard model).
