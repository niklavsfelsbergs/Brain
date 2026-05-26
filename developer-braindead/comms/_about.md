# `comms/` — dev-to-dev channel

Where parallel Braindead instances coordinate so they don't trample each other's work. Per [[D-019_parallel_braindead_and_comms_channel]].

The collision surface that motivates this layer is `gielinor/` writes — two Braindeads editing the same main-brain file in the same window produces merge pain that no visualizer tint prevents. Dev-brain files are mostly safe (per-session quest-log, naturally namespaced), but main-brain shared files (`meta/`, `spellbook/rituals/`, `CLAUDE.md`) are not.

## Files

- **`active.md`** — append-only log. The channel itself. Every Braindead session reads at respawn and writes at least two entries: an `OPEN` declaration after sibling detection, and a `CLOSING` entry at session-close.

## Entry kinds

Each entry starts with a header line:

```
[YYYY-MM-DD HH:MM] <braindead-id> <KIND>
```

Where `<braindead-id>` is `braindead-<sid8>` (first 8 chars of `CLAUDE_CODE_SESSION_ID`), and `<KIND>` is one of:

| Kind | When | Body shape |
|---|---|---|
| `OPEN` | Respawn, after sibling detection + principal directs target | `Targets:`, `Steering clear of:`, `Open to handoff:` lines |
| `→ @<target-id>` | Ad-hoc dialogue addressed to a specific sibling | Free-form; expect a reply or an action |
| `UPDATE` | Targets shifted materially mid-session | Same shape as `OPEN`, only the changed lines need to appear |
| `CLOSING` | Session-close, before commit | `Completed:`, `Leaving open:` lines |
| `ABANDONED` | (Synthesized at respawn by the next Braindead) when a prior OPEN has no CLOSING and intent-file mtime > 5min — the prior session died ungracefully | One-line: "synthesized — no closing entry, intent file stale since <time>" |

Body is indented 2 spaces, free markdown, multi-line OK.

## Read cadence

1. **Mandatory at respawn.** Before any task selection. See `spellbook/respawn-ritual.md`.
2. **Before any `gielinor/` edit.** The collision surface. Cheap re-read; might surface a sibling who picked it up since respawn.
3. **When stuck.** A sibling may have relevant in-flight reasoning worth pinging.

Polling every turn is overkill. These three trigger points cover the actual risks.

## Write discipline

- **Append-only.** Never edit an existing entry — even your own. Mistakes get a follow-up entry, not a rewrite.
- **One blank line between entries.** Bounded sections are what makes the file scannable + safe under concurrent writes.
- **Plain markdown.** No code fences inside entries unless quoting code blocks.
- **Use the entry kinds.** A free-form post that doesn't slot into `OPEN`/`UPDATE`/`→ @...`/`CLOSING`/`ABANDONED` belongs in the quest-log, not here.
- **Body cap: 2–3 lines, ≤120 chars each.** This is a coordination channel surfaced in the visualizer's chat panel, not a session journal. Detail belongs in the quest-log; the comms entry references the SNNN. Born S043 (2026-05-22) — the gielinor twin shipped under this rule from day one after the dev-brain shape produced multi-paragraph press-release bodies that were unreadable in the chat panel.
- **Conversational, in voice.** "Wrapping up S042 — shipped 4 of 6 audit fixes, #2 handed to @braindead-f9da453a" — not a structured `Completed:` / `Leaving open:` block with sub-points. The protocol *allows* the structured shape; the discipline says don't lean on it when one line will do.
- **Lead with a human gist; bury the machine detail.** Line 1 is a plain-language sentence a *human* watching the board can follow — what you're doing or asking, in prose. **No file paths, line numbers, or code identifiers on line 1.** The exact refs a sibling needs to act (`styles.css ~L301`, `STATE_RANK`, `.sb-row[data-state=…]`) go on line 2+, where the board dims them as monospace. The dev channel is read by *two* audiences — the sibling Claude (needs precision) and the principal watching the board (needs to follow along); line 1 serves the human, the tail serves the agent. **Bad:** *"S059 needs ADDITIVE hunks — styles.css: two `.sb-row[data-state="alching"]` blocks ~L301 + STATE_RANK keys, renumber idle/ended down."* **Good:** *"Heads up — I need you to add styling for two new switchboard states."* …then the file/line refs on the next line. Born S056 (2026-05-23): a dev handoff rendered as unfollowable jargon on the human board.
- **`CLOSING` template:** one line for what shipped, optionally one for what's left open. SNNN reference is enough — the quest-log carries the rest.

## Concurrent-write safety

Append-only newline-separated entries with `open(path, 'a')` are atomic at the line level on Windows + POSIX for small writes. Two Braindeads posting OPENs within the same second may interleave entries in either order, but no data is lost. The protocol tolerates minor ordering noise — the file is a coordination signal, not a database.

If observable garbling shows up routinely, add a file lock around append. Defer until needed.

## Rotation

Manual for now. When the file gets unwieldy (call it ~500 entries), move the bulk to `comms/archive/active-YYYY-MM-DD.md` and leave the most recent 50 in `active.md`. Don't delete.

## What lives here vs. elsewhere

| Content | Where it goes |
|---|---|
| "I'm working on X; staying off Y" | `comms/active.md` (OPEN entry) |
| "Hey @braindead-X, OK if I touch Y?" | `comms/active.md` (dialogue entry) |
| Detailed reasoning about a design choice | quest-log, not here |
| Cross-cutting decision about how dev brain works | `bank/decisions/D-NNN_*.md` |
| Self-observations about Braindead-the-actor | `examine/` |

The comms channel is **operational** — what's in flight, who's where. Anything reflective belongs elsewhere.

## Related

- [[D-019_parallel_braindead_and_comms_channel]] — founding decision; full design including hook + visualizer changes.
- [[D-017_parallel_player_instances]] — parallel player instances (the parent scaffolding).
- `spellbook/respawn-ritual.md` — sibling-detection + comms-read steps.
- `spellbook/session-close.md` — CLOSING-entry step.
