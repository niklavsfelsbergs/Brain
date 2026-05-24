# 08 — Enforcement & hooks

The brain's rules are split into two kinds: lines the agent *cannot* cross (hard gates) and
lines it is *disciplined* to hold (prompt rules). This page documents the gates and the
observability machinery beneath them. The hook source is authoritative; this is the map.

## Two hook families

| Family | Location | Behaviour | Job |
|---|---|---|---|
| **Enforcement** | [`gielinor/.claude/hooks/`](../gielinor/.claude/hooks/) | Exit 2 to **block** the tool call | The six architectural guarantees |
| **Observability** | [`developer-braindead/.claude/hooks/`](../developer-braindead/.claude/hooks/) | Always exit 0, swallow errors — **never** block | Emit events + state files for the cockpit |

All ten hooks are Python, read the hook payload as JSON from stdin, and derive their root
from their own file location (`__file__` walked up), **not** from `CLAUDE_PROJECT_DIR`.

## The enforcement hooks (the six guarantees)

| # | Hook | Blocks | Event | Gated on |
|---|---|---|---|---|
| 1 | [`block-confirmed-writes.py`](../gielinor/.claude/hooks/block-confirmed-writes.py) | Any write whose path contains a `confirmed/` segment | `PreToolUse` | Edit/Write/NotebookEdit/MultiEdit, path inside brain |
| 2 | [`block-deletes.py`](../gielinor/.claude/hooks/block-deletes.py) | Shell delete commands (`rm`, `remove-item`, `del`, `unlink`, `rmtree`, …) | `PreToolUse` | Bash/PowerShell command-string regex (path-agnostic) |
| 3 | [`dwarf-write-boundary.py`](../gielinor/.claude/hooks/dwarf-write-boundary.py) | Dwarf writes outside `bank/notes/`, `quest-log/`, `inventory/` | `PreToolUse` | `agent_type == "dwarf"` |
| 4 | [`gnome-write-boundary.py`](../gielinor/.claude/hooks/gnome-write-boundary.py) | Gnome writes outside the housekeeping surface | `PreToolUse` | `agent_type == "gnome"` |
| 5 | [`penguin-write-boundary.py`](../gielinor/.claude/hooks/penguin-write-boundary.py) | Penguin writes outside `research/`, `quest-log/`, `inventory/` | `PreToolUse` | `agent_type == "penguin"` |
| 6 | [`block-sub-spawn.py`](../gielinor/.claude/hooks/block-sub-spawn.py) | Any sub-agent spawning a sub-agent | `PreToolUse` | `agent_type in (dwarf, gnome, penguin)`, tool Agent/Task |

The gnome and penguin hooks check a **blocklist first** (it wins even over an allow-list
hit) — e.g. the penguin's `/bank/` block is what forces research output through `research/`
rather than letting a penguin author bank notes directly.

### Two facts that change how you read these

1. **Role hooks are inert for a principal.** They gate on the `agent_type` payload field,
   which is *absent* on a principal's tool calls — so hooks 3–6 exit 0 immediately in a
   principal session. **A principal is constrained only by #1 and #2.** (Env-var gating
   was the original S019 design but was confirmed inert — env vars don't propagate into
   sub-agent payloads — and was switched to payload-field gating in S020.)

2. **The guarantees became real gates only at [S085].** The enforcement hooks were
   originally wired *only* in `gielinor/.claude/settings.json` via `${CLAUDE_PROJECT_DIR}`.
   But the default session — and the cockpit's PTY sessions — launch at the **brain root**,
   where that path resolved empty and the hooks silently no-op'd. So the "guarantees" were
   prompt discipline, not gates: an `rm` at brain root was proven *not* blocked. S085 wired
   the enforcement hooks into the **brain-root** `.claude/settings.json` with absolute paths
   so they fire repo-wide. The lesson — *a documented guarantee isn't real until you've
   watched it fire from the actual entry point* — is recorded as feedback.

## The observability hooks

All write under [`switchboard/`](../switchboard/) (the `VIZ_DIR`, promoted there from the
old `experiments/visualizer/` location in S052). Atomic writes use `.tmp.<pid>` +
`os.replace`; `state.ndjson` / `chat.ndjson` are append-only and interleave-tolerant.

### [`emit-event.py`](../developer-braindead/.claude/hooks/emit-event.py) — the event emitter

Classifies each touched path into a map "building" + actor and appends move / action /
intent / spawn / despawn / log events to the event stream. Every event is stamped with
`sessionId` so parallel sessions sharing one stream can be disambiguated.

- **Fires:** `PreToolUse`/`PostToolUse` on Task/Agent (spawn/despawn);
  `PostToolUse` on Edit/Write/Read/Glob/Grep/Bash (move/action/chat); `SessionEnd` (despawn
  + GC).
- **Writes** (under `switchboard/`): `state.ndjson` (the event stream); `state-actors.json`
  (actor→building map); `state-instances.json` (parallel-session instance numbering);
  `state-{dwarves,gnomes,penguins}.json` (sub-agent spawn registries); `chat.ndjson` (the
  human-language feed).

### [`status-sidecar.py`](../developer-braindead/.claude/hooks/status-sidecar.py) — fleet status

Writes the per-session status record the cockpit board reads, deriving state on a two-axis
model ([D-029]): a base state plus flavour `tags`.

- **State mapping:** `UserPromptSubmit`/`PreToolUse`/`PostToolUse` → `busy`; `Stop` →
  `your_move`; `SessionEnd` → `ended`. A tight matcher (registered only for
  `AskUserQuestion|ExitPlanMode|Task|Agent`) keeps fire-rate low: wait-tools Pre →
  `needs_you`; foreground sub-agent spawn → stays `busy` + `crew` tag. Reads the `.mode`
  marker (`alching` tag / `wrapped_up` → base `done`).
- **Canonical store:** `~/.claude/status/<sid8>.json` — user-global (not per-repo) so one
  board sees every session on the machine. Shape: `{sid8, session_id, actor, instance,
  state, last_event_ts, started_at, first_prompt, intent, tags[], project_dir, cwd, host,
  claude_pid, claude_pid_chain[], claude_hwnd, …}`.
- **Browser mirror:** `switchboard/state-switchboard.json` — the live manifest the cockpit
  polls; re-derives actor/instance/building/subtitle per row, excludes `ended`, applies
  liveness gates (process-dead via PID chain + staleness).
- Also writes `state-names.json` (board renames), `chat.ndjson` (intent/say/lifecycle), and
  `state-comms-{gielinor,braindead}.md` (comms mirrors for the COMMS panel); GCs dead actor
  keys and stale intent/tmp files.

### [`rename-intercept.py`](../developer-braindead/.claude/hooks/rename-intercept.py) — `/rename`

Catches a `/rename <name>` prompt on `UserPromptSubmit`, writes the label to
`state-names.json`, and **blocks the prompt (exit 2)** so no model turn runs. Any
parse/IO failure exits 0 and lets the prompt through.

### [`emit-commit-event.py`](../developer-braindead/.claude/hooks/emit-commit-event.py) — commit banner

Appends one `commit` event on every git commit. **Not wired in `settings.json`** — it is
invoked by `.git/hooks/post-commit`.

> ⚠ **Known discrepancy.** This is the one hook that still writes to the *legacy*
> `developer-braindead/experiments/visualizer/state.ndjson`, while every other hook writes
> to `switchboard/state.ndjson` (the S052-promoted location). Commit events therefore land
> in the stale stream and don't show in the current cockpit. A documented bug, not by
> design.

## settings.json wiring

Two settings files register hooks. Authoritative:
[`.claude/settings.json`](../.claude/settings.json) (brain root) and
[`gielinor/.claude/settings.json`](../gielinor/.claude/settings.json).

- **`brain/.claude/settings.json`** (the load-bearing one — loaded for any session at brain
  root or below, which is the default and the cockpit's behaviour). Uses **absolute paths**
  to hook commands (the S052 fix for empty `${CLAUDE_PROJECT_DIR}`). Wires **both**
  families: observability (`emit-event`, `status-sidecar`, `rename-intercept`) on the broad
  tool/event matchers, **and** the enforcement hooks (the S085 fix) on
  Edit/Write/MultiEdit/NotebookEdit (the four `confirmed`/boundary hooks), Bash/PowerShell
  (deletes), and Agent/Task (sub-spawn).
- **`gielinor/.claude/settings.json`** (loaded when a session opens inside `gielinor/`).
  Uses `${CLAUDE_PROJECT_DIR}` (correct there) and registers **only** the enforcement hooks
  — defence-in-depth. The redundancy is intentional and harmless: blocking hooks are
  idempotent.

`defaultMode` is `bypassPermissions` with a small allow-list; the permission allow-lists
also live in the corresponding `settings.local.json` files.

## Summary — what's a gate vs. discipline

- **Hard gates (cannot bypass):** no `confirmed/` writes; no deletes; the three sub-agent
  write boundaries; no sub-spawn.
- **Discipline (the agent must hold):** the draft-then-approve flow, the `bank/` and
  `skills/` draft gates, treating `meta/` and rituals as user-controlled, the routing rules.
  See [04 — Write discipline](04-write-discipline.md).

---

Next: **[09 — The cockpit](09-cockpit.md)** — how you drive the fleet.
