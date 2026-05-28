# D-033 — 2026-05-28 — Positive enforcement gate: OPEN-on-entry

> **Status: decided and built (code).** First *positive* enforcement hook in the brain — it blocks a **must-do** step (post your OPEN) rather than a must-not-do one. Imported from the Khaan comparative audit (item 1 of the learnings catalogue). Principal chose the **hard-block** scope over warn-only. Hook written, tested at the boundary (12/12 synthetic payloads), registered in both settings files. Runtime-unverified pending a fresh session.

## Context — where this came from

Cloned and audited `JustsCE/Khaan` (another markdown-brain Claude-Code agent) this session — writeups at `bank/research/2026-05-28-khaan-comparative-audit.html` + `2026-05-28-khaan-learnings-implementation.html`. The audit's sharpest finding: **our hooks only say "no."** All six architectural guarantees are *negative* (block `confirmed/` writes, block deletes, block sub-spawn, the role write-boundaries). Every *positive* obligation — post an OPEN, ground before advising, write the per-turn quest-log — was prompt-discipline only, and our own audits keep catching it leak. Khaan gate-enforces its positive loop (recall→identity→decision per turn); we don't gate any positive step.

The highest-value, cleanest target is the **OPEN-on-entry discipline**. Respawn steps 6–8 require posting an OPEN to `comms/active.md` before substantive work — it is the **#1 historical discipline leak** (`S034/S037–S043/S046/S057/S060…`; ~70% skip pre-S110, "did not post an OPEN — entered mid-conversation"). [[D-031_task_list_discipline]] even named "the OPEN-skip leak" as the candidate for a future enforcement nudge. This is that nudge, hardened to a gate.

## Decision — hard-block, scoped, fail-open

A new `PreToolUse` hook `gielinor/.claude/hooks/require-open-on-entry.py` blocks `Edit|Write|MultiEdit|NotebookEdit` of brain content until this `sid8` has posted an OPEN carrying its id to its actor's `comms/active.md`.

Principal picked **hard-block** over the warn-only and "also harden grounding" alternatives:
- **Warn-only first** — rejected: we already have advisory mechanisms (`grounding-cue-reminder.py`); item 1's whole value is the *block*.
- **Also block grounding** — rejected: grounding was *deliberately* made advisory (over-trust risk, and "substantive output" isn't a tool event). Don't reverse a sound design choice. Grounding stays advisory.

**Decision table** (the load-bearing scoping — keeps the gate from over-firing):

| Condition | Result |
|---|---|
| non-brain target path | allow |
| actor not an OPEN-poster (`guthix`/`wisp`/unknown/`""`) | allow |
| sub-agent (`agent_type` set) | allow — dwarves/gnomes/penguins don't post OPENs |
| target is an escape path (the OPEN itself, marker, intent, narration) | allow |
| OPEN with this `sid8` already in the actor's comms | allow |
| otherwise | **BLOCK (exit 2)** |

**Escapes** exist so the entry sequence is never gated against itself: `comms/active.md` (post the OPEN), `.claude/active-mode.txt` (dev-brain marker), `.claude/intent/*` (intent sidecars), `.claude/narration.txt`. Actor is read from the per-session status sidecar (`~/.claude/status/<sid8>.json`) — same source `grounding-cue-reminder.py` uses. Braindead → dev comms; players → gielinor comms.

**Fail-open is absolute.** Any error — unparseable payload, missing/unreadable comms, unknown actor — exits 0 (allow). A bug in this hook can never brick a session. This matches every other brain hook and is the only safe posture for a blocker that fires across all parallel sessions.

## What landed

- `gielinor/.claude/hooks/require-open-on-entry.py` — the gate.
- `.claude/settings.json` (brain-root, authoritative for cockpit/brain-root launches) — registered on the `Edit|Write|MultiEdit|NotebookEdit` matcher with an absolute path ([[S052_98d4ec5e_switchboard-rebuild|S052]] convention) + a `_comment_open_gate` rationale.
- `gielinor/.claude/settings.json` — registered too (`${CLAUDE_PROJECT_DIR}`), defense-in-depth per the boundary-hook redundancy pattern; blocking hooks are idempotent so the redundancy is harmless.

## Verification

Boundary-tested on 12 synthetic stdin payloads (the "verify-enforcement-fires" lesson): braindead-no-OPEN → **block**, braindead-WITH-OPEN (real live sid) → allow, player-no-OPEN → **block** (routes to gielinor comms), all four escape paths → allow, guthix/unknown actor → allow, sub-agent → allow, non-brain path → allow, non-write tool → allow, malformed payload → exit 0. **12/12.** `py_compile` clean; both `settings.json` parse.

**RUNTIME-UNVERIFIED:** mid-session `settings.json` edits don't reload hooks, so this session is not gated by it. Needs a **fresh session** that attempts a brain-content write before posting an OPEN and is blocked (the [[S106_cf03bfe1_self-eating-audit-and-d8-enforcement-fix|S106]]/[[S110_144c0ca2_brain_full_audit|S110]] fresh-session-config-load pattern). Verify: open a fresh player/dev session, try an Edit before the OPEN → expect the block banner; post the OPEN → expect the write to succeed.

## Out of scope / open

- **The meta/lorebook propagation is NOT done here.** `meta/write-rules.md` should gain an "enforced by hook" line for this gate, and gielinor's `lorebook/` a confirmed decision — but `meta/` and `lorebook/confirmed/` are user-only, and a dev-brain `[[D-033]]` link won't resolve in the gielinor vault (the [[D-032_godly_proposal_flow_and_code_bearing_seam]] precedent). Route the gielinor-binding text through a **godly proposal at the next bankstanding**, or principal hand-edit. Proposed text surfaced in the build session.
- **Bash git-commit is not gated.** Only file-write tools. The OPEN should precede all writing anyway, so by commit time it exists; gating Bash risks bricking the universal escape hatch. Revisit only if a "commit without ever posting an OPEN" pattern shows up.
- **Other positive obligations** (per-turn quest-log write, grounding-as-block) are not gated. This is one gate for the one leak that most warranted it; resist gate-sprawl (Khaan's own logged frustration trigger is permission-prompt overload).

## Related

- [[D-031_task_list_discipline]] — named the OPEN-skip leak as the candidate for an enforcement nudge; this is it.
- [[D-032_godly_proposal_flow_and_code_bearing_seam]] — why the meta/lorebook propagation routes through bankstanding, not a dev-brain meta-edit.
- [[D-024_parallel_player_coordination]] — the comms/`active.md` + `sid8` machinery this gate reads.
- `bank/research/2026-05-28-khaan-learnings-implementation.html` — item 1 (HITL §1) and the full catalogue this is drawn from.
- `gielinor/.claude/hooks/grounding-cue-reminder.py` — the sibling advisory hook (grounding stays advisory by design).
