# `comms/` — gielinor coordination channel

Where parallel player + deity sessions coordinate so they don't trample each other's work. Per [[D-024]] (dev brain).

The collision surface is the **disk-side** of running parallel sessions. The visualizer + per-session intent files ([[D-018]] dev brain) handle the screen-side; this layer handles the file-system side:

- `inventory/<topic>__<sid8>.md` collisions across two Jebrim sessions on the same topic.
- `quest-log/in-progress/SNNN_<sid8>_<slug>.md` SNNN-allocation races.
- Global identity-draft collisions (`examine/drafts/`, `niksis8/drafts/`, `lorebook/drafts/`, `players/inbox/`).
- The agent being unaware a sibling session exists at all — the content-based wrong-instance check in `meta/communication-protocol.md` doesn't catch *file-system* collisions, just principal-side mis-addressing.

Single file, all participants. Players (Jebrim, Zezima, future roster) and the deity (Guthix) post here. One file is deliberate: cross-player visibility is the point, and per-player files would fragment the wrong-instance check exactly when it pays off.

## Files

- **`active.md`** — append-only log. Every player or Guthix session reads at respawn and writes at least two entries: an `OPEN` declaration after sibling detection, and a `CLOSING` entry at session-close.

## Entry kinds

Each entry starts with a header line:

```
[YYYY-MM-DD HH:MM] <actor>-<sid8> <KIND>
```

Where `<actor>` is `jebrim`, `zezima`, `guthix`, or a future-roster player name, `<sid8>` is the first 8 chars of `CLAUDE_CODE_SESSION_ID`, and `<KIND>` is one of:

| Kind | When | Body shape |
|---|---|---|
| `OPEN` | Respawn, after sibling detection | `Targets:`, `Steering clear of:`, `Open to handoff:` lines |
| `→ @<target-id>` | Ad-hoc dialogue addressed to a specific sibling | Free-form; expect a reply or an action |
| `UPDATE` | Targets shifted materially mid-session | Same shape as `OPEN`, only the changed lines need to appear |
| `CLOSING` | Session-close, before commit | `Completed:`, `Leaving open:` lines |
| `ABANDONED` | (Synthesized at respawn by the next session) when a prior OPEN has no CLOSING and the [[D-020]] status sidecar shows the session as `ended` or stale (`last_event_ts > 5min`) | One-line: "synthesized — no closing entry, sidecar state <state> since <time>" |

Body is indented 2 spaces, free markdown, multi-line OK.

## Read cadence

1. **Mandatory at respawn.** Before any task selection — see `spellbook/rituals/respawn.md`. Sibling detection (sidecar manifest + comms log cross-reference) drives whether an OPEN is needed and what to steer clear of.
2. **Before any write to a shared global surface.** `gielinor/examine/drafts/`, `niksis8/drafts/`, `lorebook/drafts/`, `players/inbox/` are the cross-player collision spots. Cheap re-read; might surface a sibling who landed on the same surface since respawn.
3. **Before touching a quest-log or inventory file whose suffix doesn't match own sid8.** Per the inventory-recovery rule in `respawn.md`.
4. **When the principal asks something that reads as another player's domain.** Pair with the content-based wrong-instance check in `meta/communication-protocol.md`.

Polling every turn is overkill. These trigger points cover the actual risks.

## Liveness — sidecar-driven, not mtime-driven

Sibling detection reads `~/.claude/status/<sid8>.json` (the [[D-020]] dev-brain decision):

```
state ≠ ended AND last_event_ts < 5min AND actor in {jebrim, zezima, guthix, ...}
```

Cross-reference each live session id against the comms log: any id in the sidecar without a matching `CLOSING` entry is a confirmed-live sibling. Strictly stronger than intent-file mtime — the sidecar tracks `working` / `waiting_for_user` / `idle` / `ended` states explicitly.

## Write discipline

- **Append-only.** Never edit an existing entry — even your own. Mistakes get a follow-up entry, not a rewrite.
- **One blank line between entries.** Bounded sections are what makes the file scannable + safe under concurrent writes.
- **Plain markdown.** No code fences inside entries unless quoting code.
- **Use the entry kinds.** Free-form posts that don't slot into `OPEN`/`UPDATE`/`→ @...`/`CLOSING`/`ABANDONED` belong in the quest-log, not here.
- **Body cap: 2–3 lines, ≤120 chars each.** This is a chat channel, not a session journal. Detail belongs in the quest-log; the comms entry references the SNNN. Born S043 (2026-05-22) — the first live render of this layer hit the visualizer with multi-paragraph press-release bodies and the chat was unreadable.
- **Conversational, first-person, in voice.** "Working on EU tender pull, staying off the rollups subtree" — not "Targets:" + bullet list. The protocol *allows* the structured-body shape; the discipline says don't lean on it when one line will do. Each player speaks in-character.
- **`CLOSING` template:** one line for what shipped, optionally one for what's left open. SNNN reference is enough — the quest-log carries the rest.

## Concurrent-write safety

Append-only newline-separated entries with `open(path, 'a')` are atomic at the line level on Windows + POSIX for small writes. Two sessions posting OPENs within the same second may interleave entries in either order, but no data is lost. The protocol tolerates minor ordering noise — the file is a coordination signal, not a database.

If observable garbling shows up routinely, add a file lock around append. Defer until needed.

## Rotation

Manual for now. When the file gets unwieldy (call it ~500 entries), move the bulk to `comms/archive/active-YYYY-MM-DD.md` and leave the most recent 50 in `active.md`. Don't delete.

## What lives here vs. elsewhere

| Content | Where it goes |
|---|---|
| "I'm working on EU tender pull; staying off the report subtree" | `comms/active.md` (OPEN entry) |
| "Hey @jebrim-<sid8>, OK if I touch the rollups draft?" | `comms/active.md` (dialogue entry) |
| Detailed reasoning about a domain decision | `quest-log/in-progress/` (the active player's), not here |
| Cross-cutting decision about how the agent operates | `lorebook/drafts/` |
| Self-observations about a player | `examine/drafts/` (the active player's) |
| Idle banter unrelated to coordination | nowhere — this isn't a chat channel for its own sake |

The comms channel is **operational** — what's in flight, who's where. Voice carries personality (each player speaks in-character), but the content is always coordination. Anything reflective belongs elsewhere.

## Visualizer rendering

The visualizer's COMMS panel polls this file in live mode and renders entries as chat lines tagged by the posting actor. The speech bubble above each sprite continues to show the agent's current intent ("what I'm doing"); the COMMS panel shows the inter-session conversation ("what we're saying to each other"). The two channels are deliberately distinct.

## Related

- [[D-024]] (dev brain) — founding decision; full design including suffix rules, sidecar liveness, inventory recovery.
- [[D-017]] (dev brain) — parallel player instances (the parent scaffolding).
- [[D-019]] (dev brain) — dev-to-dev mirror; this is its player-side twin.
- [[D-020]] (dev brain) — status sidecar; the liveness source.
- `spellbook/rituals/respawn.md` — sibling-detection + comms-read + OPEN-entry + inventory-recovery rule.
- `spellbook/rituals/close-session.md` — CLOSING-entry step.
- `meta/communication-protocol.md` §"Wrong-instance check" — the content-based sibling check this layer complements.
- `developer-braindead/comms/` — dev-brain twin (single-actor channel).
