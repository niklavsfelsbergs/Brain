# D-034 — Guthix executes on explicit principal authorization; "proposes only" is scoped to unilateral action

**Decided.** 2026-06-09, principal-authorized in a Guthix consultation that pivoted to dev-brain ([[S165_e0f6de1a_nfe_reference_judgment_layer_to_brain|S165]]; Niklavs: *"I want you to be able to carry all this out, why can't you? You are the god. We already discussed once that you should be able to."*). Sibling of [[D-032_braindead_full_access|D-032]].

## Decision

Guthix's **"he proposes; the principal decides"** rule (`meta/guthix.md`, `meta/write-rules.md`, `deities/guthix/proposals/_about.md`) governs **unilateral** action only — Guthix acting on his *own* judgment during a consultation or bankstanding pass. It was never meant to block **authorized execution**.

When the principal gives **explicit, specific authorization** for a change inside a Guthix session, Guthix **executes it directly** — no godly-proposal detour — against the **discipline-gated** surfaces: globals (`examine/`, `niksis8/`, `keepsake/`, `lorebook/`), per-player layers, the user-only rulebook (`meta/*.md`, `spellbook/rituals/*.md`, `keepsake/current.md`, body files), and ritual prose. These surfaces are guarded by *discipline*, not hooks (`guthix.md`: "the hook does not enforce these surfaces specifically for Guthix"), so authorized execution touches nothing a hook would stop.

## The floor stays — the one hard limit

The **hook-enforced floor remains in force for Guthix even when authorized**: no `confirmed/` writes, no file deletes. That bypass is keyed to actor `braindead` alone ([[D-032_braindead_full_access|D-032]]); Guthix never resolves to `braindead`, so `block-confirmed-writes.py` / `block-deletes.py` still stop him. A change that genuinely needs a `confirmed/` identity write or a delete routes through **dev-brain (Braindead)** or the principal. Authorized-Guthix gets everything *except* the floor.

This is deliberate: it keeps the architectural guarantee intact and needs **no hook change**. Guthix gains discipline-level authority to execute on authorization; he does not gain a floor bypass.

## Why

The propose-then-land detour is overhead when the principal is sitting in the session authorizing the change live — the exact reasoning behind [[D-032_braindead_full_access|D-032]]'s Braindead grant. The recurring friction (*"why can't you, we already discussed this"*) came from the docs stating propose-only without the authorization carve-out, so the agent re-derived a false hard limit every session. Writing the carve-out down is the durable fix.

## Scope and guardrail

- **Authorization must be explicit and specific** — *this change, now*, not a standing blanket grant. Absent it, propose-only holds and Guthix defaults to `deities/guthix/proposals/` (bankstanding) or chat-only (consultation).
- **Safeguard** is the [[D-032_braindead_full_access|D-032]] one, not a gate: the principal is in the interactive session seeing the diffs, and every change is git-reversible.
- **Surface high-blast-radius changes first.** As with Braindead, an authorized edit to user-only rulebook / identity-adjacent surfaces should be surfaced (decision text shown) before it lands.

## Scope of impact

- `meta/guthix.md` — write-model gains an *Authorized execution* case; the "do not unilaterally widen" discipline line carves out explicit authorization.
- `meta/write-rules.md` — the ritual-reach table + "Guthix's godly proposals" para note the carve-out so the table isn't read as absolute.
- No hook change. No change to Braindead's reach. Other actors (players, wisp, sub-agents) unaffected — their boundaries were never authorization-gated.

## Related

- [[D-032_braindead_full_access|D-032]] — the precedent: Braindead's unrestricted reach, enacted by Guthix-on-authorization. D-034 generalizes the *authorization* half to Guthix without the *floor-bypass* half.
- `meta/guthix.md` — Guthix's persona, modes, write reach.
- `meta/write-rules.md` — the ritual write-reach table.
- `deities/guthix/proposals/_about.md` — the unilateral-proposal surface (still correct for the unauthorized case).
