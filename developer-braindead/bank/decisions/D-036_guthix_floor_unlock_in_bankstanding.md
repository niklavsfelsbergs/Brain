# D-036 — Guthix floor-unlock for `confirmed/` writes in bankstanding (build record)

**Built.** 2026-06-19, [[S277_d371d189_guthix-floor-unlock|S277]] (dev-brain pivot from a live Guthix bankstanding [[B-021_2026-06-19_bankstanding|B-021]], same sid d371d189). The canonical decision is gielinor `lorebook/confirmed/D-036_guthix-floor-unlock-in-bankstanding.md`; this is the construction record.

## The ask

Principal, mid-bankstanding: *"why can't guthix act with my permission? He should be able to, i want to close everything during bankstanding."* The friction: examine→`confirmed/` promotions and per-player domain/quest closes always routed to his own `git mv` because the `confirmed/` floor (`block-confirmed-writes.py`) is `braindead`-only (gielinor [[D-034_guthix_executes_on_explicit_authorization|D-034]] kept it so).

## Root cause (why it was blocked)

The floor is a **PreToolUse hook** — a binary actor check (`resolve_actor(sid8) == "braindead"`). It has no payload field for "the principal authorized this specific write," so [[D-034_guthix_executes_on_explicit_authorization|D-034]] could only give authorized-Guthix the *discipline-gated* (hook-free) surfaces and had to leave the floor a hard actor line. Not a trust limit — a mechanism limit.

## What was built

A **second bypass** in `block-confirmed-writes.py`, gated on three independent ANDs: `actor==guthix` × `.mode ∈ {bankstanding,alching}` × a non-empty `.claude/intent/<sid8>.floor-unlock` marker (the machine-readable authorization signal [[D-034_close_ritual_enforcement|D-034]] said a hook couldn't read). Logged `bypass-guthix-authorized`. Two helpers added: `read_mode` (freshest `.mode` across both intent dirs, mirroring `_actor.py`) + `floor_unlocked`. **`confirmed/` writes only — `block-deletes.py` untouched** (bankstanding archives, never deletes; the principal chose confirmed-only scope).

- Hook: `gielinor/.claude/hooks/block-confirmed-writes.py`
- Test: `developer-braindead/verification/test_block_confirmed_unlock.py` — 9 cases, **verified live from the real stdin entry point** (every gate-drop blocks; a player can't enter with a marker; draft path always allowed). Auto-discovered by `run_tests.py` → full suite **21/21**.
- Ritual: `gielinor/spellbook/rituals/bankstanding.md` — floor-unlock lifecycle (write-on-explicit-grant, clear-at-close, the gnome-recommends/Guthix-executes note).
- Docs: `gielinor/meta/write-rules.md` + `gielinor/meta/guthix.md` floor statements carved out; gielinor `lorebook/confirmed/D-036` + `_index.md` cue row; [[D-034_close_ritual_enforcement|D-034]] amendment pointer.

## Design choices (the fork the principal picked)

- **Per-session unlock grant** over mode-keyed-always or status-quo: keeps the default floor ON, makes "with my permission" a deliberate auditable artifact, not a blanket-on-during-bankstanding.
- **confirmed/ writes only**, deletes stay `braindead`-only: never-destroy stays fully hard.
- Safeguard model is [[D-032_braindead_full_access|D-032]]'s (interactive principal + git-reversible) **plus** the audit log — not a gate, since the marker is agent-written (same trust posture as every other sidecar; the agent can already reach full floor via the Braindead actor anyway).

## Watch / open

- First **live** use of the unlock by a real Guthix bankstanding (this session pivoted to Braindead, so the unlock path is test-verified but not yet exercised by an actual guthix-actor session).
- `bankstanding.md` says clear the marker at close — no auto-clear hook; relies on ritual discipline (acceptable: stale marker is sid-scoped).

## Related

- gielinor [[D-034_guthix_executes_on_explicit_authorization|D-034]] (the precedent; D-036 supplies the floor-bypass half it withheld), [[D-032_braindead_full_access|D-032]] (the parallel bypass + safeguard model).
