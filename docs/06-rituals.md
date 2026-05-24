# 06 — Rituals

Rituals are the brain's control flow — the fixed procedures that drive a session from
start to close. They live in [`gielinor/spellbook/rituals/`](../gielinor/spellbook/rituals/)
and are **user-edited** (user-only write discipline). This page summarises each; the ritual
file is authoritative for the exact steps.

A ritual's *write-reach* (which layers it may touch at all) is set by the
[ritual write-reach matrix](04-write-discipline.md#ritual-write-reach); its *voice* is set
by the active mode ([05 — Actors & modes](05-actors-and-modes.md)).

<a id="respawn"></a>
## Respawn — session start

Source: [`respawn.md`](../gielinor/spellbook/rituals/respawn.md).

- **Trigger.** Automatically at every session start; also as a **mini-respawn** on a
  mid-session actor switch.
- **Reads.** Body/CLAUDE.md imports; global `keepsake/current.md`, all `examine/confirmed/`
  and `niksis8/confirmed/`; if a player is active, that player's persona, confirmed
  identity, `quest-log/in-progress/`, and inventory resume files. Sibling-detection reads
  `~/.claude/status/*.json` and `comms/active.md`. Cued layers (`bank/`, skills, lorebook)
  are **not** preloaded — they're fetched on demand.
- **Writes.** Reads-only in principle, except: posts an `OPEN` to `comms/active.md`, and
  maintains per-turn quest-log discipline once live. The mini-respawn also writes a hand-off
  note to the outgoing player and archives the outgoing intent file.
- **Produces.** Agent loaded with durable identity, active player in foreground, in-flight
  quests surfaced via a **reconciliation prompt** (surface what was in flight; offer
  Resume / Abandon / Reconcile — never auto-resume), an alching recommendation if
  thresholds are breached, and an `OPEN` posted.

> Load order is canonical — **do not improvise it.** Read the ritual file.

<a id="close-session"></a>
## Close-session — session wrap

Source: [`close-session.md`](../gielinor/spellbook/rituals/close-session.md).

- **Trigger.** Principal cue at session end ("let's close the session" / "wrap up" —
  loose matching). Covers **all** players with non-empty `quest-log/in-progress/`, not just
  the active one.
- **Writes.** Reconciles every `pending` action; compacts and moves quest-logs to
  `completed/`; writes resume state to `inventory/<slug>-resume__<sid8>.md`; harvests
  drafts; posts a `CLOSING` to comms; commits; writes a `wrapped_up` `.mode` marker.
  **No promotions to `confirmed/`, no `keepsake/current.md` pins.**
- **Procedure gist.** Spawn-decision (gnome vs. self) → reconcile pending → persist
  chat-only drafts → resume state + compact log → continue-vs-complete the quest →
  inventory hygiene → **observation harvest** (corrections/reverts harvest is mandatory) →
  surface drafts → `CLOSING` → commit (scoped; never pushes; this step overrides the global
  "always ask before committing") → state the close.

> The harvest step is where lessons get captured. Per a 2026-05-24 directive, **both**
> session-close rituals (main and dev) require harvesting correction/regression learnings
> at every wrap.

<a id="alching"></a>
## Alching — per-player tending

Source: [`alching.md`](../gielinor/spellbook/rituals/alching.md). Mode:
[alching](05-actors-and-modes.md#session-modes).

- **Trigger.** Explicit cue in a player session (`let's alch` / `/alch`); recommended at
  respawn on threshold breach; or as Phase 0 of bankstanding. Never auto-runs.
- **Reach.** Reads and writes **only the active player's** layers. Does not read globals or
  other players.
- **Procedure gist.** Review identity drafts → promote bank drafts + sweep `bank/notes/`
  for staleness → graduate **completed** quest episodes into bank drafts → self-observation
  sweep → enforce `keepsake/current.md` budgets → review `rejected/` patterns → skill
  graduation → stamp `last-alched.md`.
- **Marker.** When principal-run, writes an `alching` `.mode` marker so the cockpit shows
  the `ALCHING` chip.

<a id="bankstanding"></a>
## Bankstanding — system-level tending

Source: [`bankstanding.md`](../gielinor/spellbook/rituals/bankstanding.md). Mode:
[bankstanding](05-actors-and-modes.md#session-modes), voiced as Guthix.

- **Trigger.** Principal cue only (`Hey Guthix, bankstand` / `let's bankstand`). No
  auto-triggers (Phase 1).
- **Reach.** Reads **everything**; proposes only to **global** layers (`examine/`,
  `niksis8/`, `keepsake/`, `lorebook/`, `players/inbox/`) plus godly proposals. **Cannot
  write per-player layers** — it can only flag a player overdue for alching.
- **Procedure gist.** **Phase 0** — alch each changed player first (the one sanctioned
  mid-ritual mode transition: per-player writes allowed during Phase 0, then back to
  globals-only) → triage `players/inbox/` → review global identity drafts → cross-player
  synthesis (promote recurring patterns to globals) → enforce global budgets → review
  `rejected/` patterns → log behavioural changes to `lorebook/drafts/`.

**Godly proposals.** During bankstanding only, Guthix may *propose* changes to surfaces
normally user-only (`meta/`, rituals, hooks, even the architecture). Proposals land in
[`deities/guthix/proposals/`](../gielinor/deities/guthix/proposals/); the principal reviews.
The hook-enforced lines remain non-overridable even for him.

<a id="drafts-triage"></a>
## Drafts-triage — the lightweight promotion gate

Source: [`drafts-triage.md`](../gielinor/spellbook/rituals/drafts-triage.md). The `/drafts`
command.

A thin cut of alching's step 1 — promotion only. Surveys pending drafts in scope (active
player + global identity drafts; narrows to globals-only in dev-brain/consultation/unscoped
modes), surfaces each with claim + anchor + a y/n/edit recommendation, takes batch verdicts,
and executes via `git mv` (Bash bypasses the `confirmed/`-write hook for player-owned
moves). It does **not** update `last-alched.md`, sweep bank staleness, or graduate skills.

## Death & spawn — what survives

Source: [`gielinor/meta/death-and-spawn.md`](../gielinor/meta/death-and-spawn.md).

**Death-as-crash.** The runtime context is gone; recovery depends on disk. Discipline: the
quest-log appends **every turn** (not at session end); every external action is logged
`pending` before execution and updated after. A fresh session that finds an in-progress
entry with an unresolved `pending` runs the reconciliation prompt.

**Death-as-reset.** A deliberate fresh start. What persists:

| Persists | Lost |
|---|---|
| `bank/`, `research/`, `spellbook/`, all `confirmed/`, `keepsake/`, `lorebook/`, `meta/`, `quest-log/completed/` | `inventory/`, all `drafts/` |

`quest-log/in-progress/` and body files are the principal's choice. The asymmetry is
deliberate: **confirmed knowledge and history survive; working state and unapproved
proposals don't.** Identity is durable; mid-thought is not. (Reset is rare; there is no
`/reset` command yet.)

**Death-as-migration (ascension).** Moving to a new host. Phase-3 work; the
`ascension.md` ritual does not exist yet — when built, the whole brain travels and only the
body (config, scheduling) changes.

---

Next: **[07 — Communication & coordination](07-communication-and-coordination.md)** — the
response protocol and how parallel sessions coexist.
