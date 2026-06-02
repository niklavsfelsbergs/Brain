# S144 — domain-knowledge grounding cue, generalized into a registry

**sid** 9b67aceb · 2026-06-02 · dev-brain via "lets develop gielinor", mid-conversation. OPEN→UPDATE(discussion→build)→CLOSING via `comms_append`. No live Braindead siblings ([[S142_a31a2bc0_brain_health_audit_and_gitignore_hygiene|S142]]/a31a2bc0 closed 23:11 prior night).

## The ask

Niklavs pasted two Jebrim sessions (the automated shipping-report work) — *"the brain is acting dumb… we need to think how to make it smarter."* Failures across the two: misread a meeting transcript (recapped the framing, not the decision); built a template-filler report (verified tables *render*, buried the conclusion); **mislabeled UPS OML surcharges as "billing errors"** for want of carrier-contract context; didn't know the mart schema (whether dims exist) when `shipping-agent/reference/tables.md` answers it in one line.

## Diagnosis (the sharp part)

The unifying read: **the brain is library-rich, reflex-poor.** The single strongest signal isn't in the transcripts — it's that the *exact lesson was already in memory* (S124 confirmed note: *"read domain knowledge before proposing — when a domain has a canonical reference, read it"*) and the failure recurred anyway. **A passive note about a failure didn't prevent the failure** → the fix is a *trigger*, not another note. (Same shape as the OPEN-posting leak: ~30% on discipline, ~100% once a gate fired.)

Failures collapsed to three roots — (1) knowledge exists but isn't loaded on-topic [acute]; (2) domain work ran on the principal path, not the specialist whose config bakes the knowledge in; (3) the report is a template-filler not an analyst [posture/harness]. Plus a capture gap (LPS/OML bands not yet in the brain) and a transcript-read skill miss.

Niklavs steered (multiple-choice): **generalize the grounding reflex** — and flagged *"something about the mart was already written by another session, align with that."*

## Key finding — S124 already built the shipping case (uncommitted)

The same shipping session built the whole shipping reflex and left it uncommitted: `shipping-cue-reminder.py` (a standalone copy of `grounding-cue-reminder.py`) + its brain-root `settings.json` registration + a *"Shipping / mart work — load the knowledge first"* section in `players/jebrim/CLAUDE.md` + the `calling-the-shipping-agent` skill + a `summarizing-discussions` draft skill (the convo-1 lesson). So this was **not** a rebuild — align, don't reinvent.

## Built — the registry (Niklavs picked: registry-driven single hook)

- **`gielinor/.claude/hooks/cue_registry.py`** — the `DOMAINS` table `{name, patterns, message, skip_actors}`. Shipping = **entry #1, ported VERBATIM from S124** (parity-proven). A commented EU-tender stub shows the worked example. **The Nth domain (EU tender / FIF / SCM — all have canonical homes in `bank/notes/projects/`) is ONE ROW** — no new hook file, no new settings line.
- **`gielinor/.claude/hooks/domain-cue-reminder.py`** — the generalized hook. Reads the registry, per-entry actor-skip, **one combined nudge** when several domains match (anti-wallpaper), defensive (any parse/IO/bad-pattern failure → exit 0; bad registry → no domains fire, hook still lives).
- **`settings.json`** — repointed `shipping-cue-reminder.py` → `domain-cue-reminder.py`; `_comment_shipping_cue` → `_comment_domain_cue`.
- **`jebrim/CLAUDE.md`** — updated the hook-name reference.
- Standalone `shipping-cue-reminder.py` → `hooks/archive/` (never-destroy; one cue hook in the live dir).
- **Left `grounding-cue-reminder.py` untouched** — distinct reflex: *identity* (continuation → own past work, [[D-028_grounding-precondition-needs-a-trigger|D-028]]) vs *domain* (topic → external knowledge home). Don't regress a committed, blessed mechanism.

## Verified

8/8 synthetic boundary + **parity** (new registry body byte-identical to S124's standalone for shipping payloads) + combine-path exercised directly (single=bare message, multi=one combined block) + `py_compile` + `settings.json` JSON-valid. **Live-fire from a real Jebrim entry is the verify hand-off** — the hook skips braindead by design, so it cannot fire in this dev session (verify-what-you-can); next Jebrim shipping prompt triggers it and `ritual-events.ndjson` records it.

## Open

- **Live-fire hand-off:** confirm the nudge injects on the next Jebrim shipping prompt (check the `domain-cue:shipping nudge` row in `switchboard/ritual-events.ndjson`).
- **First-prompt actor race** (noted, not fixed): on a session's *entry* prompt the status sidecar may not yet carry the actor, so the braindead-skip can miss on turn 1 — observed this session (grounding-cue fired on my own entry prompt despite the skip). Cuts the safe way for domain-cue (fires when unsure). Low priority.
- **Roots 3 & 4 from the diagnosis are NOT done** — the report-as-analyst redesign (delta/exception-driven, bottom-line-first, builder=evidence / shipping-agent=judge-against-contract) and capturing the LPS/OML band/refund knowledge into `shipping-agent/reference/`. Both are Jebrim-session work, surfaced for Niklavs.
- S124's Jebrim analysis files (report skill, `summarizing-discussions` draft, S124/[[S034_guthix_consultation_mode|S034]] quest-logs) left uncommitted for a Jebrim session / alching per Niklavs' "mechanism only" scope.

**Cascade.** Dev-brain side: this quest-log (S144), `bank/plan.md` §W, `bank/build-lessons.md` (+1 line), `comms/active.md` (OPEN→UPDATE→CLOSING). Commit `7f7606c` (mechanism) + the close commit.

**Main-brain changes.** Yes — the grounding mechanism crossed into gielinor: new `gielinor/.claude/hooks/cue_registry.py` + `domain-cue-reminder.py`, `gielinor/.claude/hooks/archive/shipping-cue-reminder.py` (archived standalone), `gielinor/players/jebrim/CLAUDE.md` (hook ref), brain-root `.claude/settings.json` (registration repoint + comment). S124's Jebrim analysis files (report skill, `summarizing-discussions` draft, S124/[[S034_guthix_consultation_mode|S034]] quest-logs) deliberately NOT landed — left for a Jebrim session per the "mechanism only" scope.
