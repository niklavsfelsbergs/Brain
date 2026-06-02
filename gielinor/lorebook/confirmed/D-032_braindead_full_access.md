# D-032 — Braindead has unrestricted edit access to the whole brain

**Decided.** 2026-06-02, principal-authorized in dev session [[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]] (Guthix executed the grant on `Hey Guthix`; Braindead canonicalized it).

## Decision

The dev-brain construction crew (actor `braindead`) has **unrestricted edit reach over the entire brain** — every layer, with no draft gate, no godly-proposal detour, and **no hook-enforced floor**. This includes:

- the user-only rulebook: `meta/*.md`, `spellbook/rituals/*.md`, `CLAUDE.md`, hook files, `keepsake/current.md`;
- `confirmed/` paths (identity layers);
- file deletes (not just archive-moves).

The two floor hooks — `block-confirmed-writes.py` and `block-deletes.py` — carry an `actor == "braindead"` bypass, resolved via the hardened `_actor.resolve_actor` (status → intent-file anti-race), and **log a `bypass-braindead` event** so every override is auditable.

## Scope — the floor stays for everyone else

The bypass is keyed to the resolved actor `braindead` *only*. For players, Guthix, the wisp, and all sub-agents (dwarf/gnome/penguin/shipping-agent — `agent_type`-gated, never resolving to `braindead`), the floor is **fully in force**: no `confirmed/` writes, no deletes. Verified empirically at grant time: a `braindead` sid passes both hooks (exit 0); an unknown/other actor is still blocked (exit 2).

## Why

Building and maintaining the brain *is* the construction crew's role (`developer-braindead/CLAUDE.md`: "Modifying `gielinor/` is fine from this brain. That's what the construction crew does."). The propose-then-land detour — Braindead → Guthix godly proposal → principal lands — is overhead when the principal is sitting in the interactive dev session watching the diffs. This grant gives Braindead strictly *more* reach than Guthix (who only *proposes* to user-only surfaces during bankstanding; Braindead *edits* them).

## The safeguard that replaces the gate

The never-destroy / identity-gate guarantees existed so the principal could authorize aggressive reorganization *because* nothing was destroyed without sign-off. With the floor lifted for Braindead, the safeguard is no longer a hook but the **context**: dev-brain sessions are interactive principal sessions (Niklavs sees every diff in-session), and every change is **git-reversible**. The never-destroy property still holds for the brain at large — it is simply no longer enforced against the one actor whose job is to maintain it.

## Related

- `meta/write-rules.md` → *The Braindead exception* (the canonical permission statement).
- `gielinor/.claude/hooks/block-confirmed-writes.py`, `block-deletes.py` (the bypass).
- `developer-braindead/CLAUDE.md` (the construction-crew scope).
- Founding context: the anti-deterioration plan ([[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]], `developer-braindead/bank/plan.md` §X) — this grant lets Braindead execute Phase 1 (the `@import`-chain trim, which edits user-only `meta/`) directly instead of through a godly proposal.
