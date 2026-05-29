# S121 — Khaan item 11: structured ritual analytics (Bands A+B)

**Session:** braindead-03861733 · 2026-05-29 · dev-brain via "lets develop gielinor" (mid-conversation).
**Arc:** Khaan learnings benchmark ([[S114_277d9053_khaan-audit-and-open-gate|S114]] →). The dev-buildable *recommended sequence* closed at [[S120_885d6702_khaan-item-4-five-lens-doctrine|S120]]; this picks up an item that slipped that sequence's tracker.

## What was asked

Principal: *"Anything left we should tackle from Khaan?"* — a completeness check. Then, on the finding, *"yeah lets scope it"* → scope + build item 11.

## The finding (why item 11 was still open)

`bank/plan.md` §P tracks only the *recommended sequence* (items 1, 2, 4, 5, 6, 12 + G held + H n/a). Re-checking against the **full 12-item HITL catalogue** (`bank/research/2026-05-28-khaan-learnings-implementation.html`) surfaced gaps the §P summary never triaged — notably the two genuinely-cheap ones:

- **item 9** — skill scaffolder + doc rules (Med / **Low**)
- **item 11** — structured invocation logs (Low / **Low**)

(items 3/7/8 = lean §N/later-phase; item 10 = Low priority.) Recommended item 11 first — it gives the brain its first machine-readable data on whether rituals actually fire, feeding every "is enforcement real?" question. Principal chose **Bands A+B** (full Low-effort version, no cockpit panel).

## The design constraint that shaped it

Gielinor rituals are **markdown procedures the agent follows, not code** — so most "invocation events" aren't observable by any code path. Three bands; only two worth building:

- **Band A (built) — hook-fires.** The enforcement/advisory hooks already run; they're *code*, so logging what they did is ground truth, not discipline-dependent self-report.
- **Band B (built) — ritual outcomes, derived from git.** alching/drafts promote-vs-reject = `drafts/ → confirmed/` vs `→ rejected/` file-moves, already in history.
- **Band C (deliberately NOT built) — hand-emitted ritual markers.** Would depend on the very discipline the gates exist to backstop (the OPEN-skip leak is the canonical failure). Skipping it is the point.

## Built

1. **`switchboard/ritual_log.py`** — shared helper. `log_event(hook, decision, *, actor, sid8, path_class, detail)` appends one NDJSON line to `switchboard/ritual-events.ndjson`; `classify_path(rel)` for coarse layer tags. Atomic-append, bounded sweep, **never raises** (mirrors `emit-event.py`'s B8/B9 posture).
2. **9 hooks wired** (one import block + `log_event` at the decision points only — not every early `return 0`):
   - `require-open-on-entry` — block **and** allow-after-OPEN (gate effectiveness baseline).
   - `block-confirmed-writes`, `block-deletes`, `block-sub-spawn` — block only (allow = every write/command, already in the emit-event stream; don't duplicate).
   - `dwarf/gnome/penguin/shipping-agent-write-boundary` — block only (gnome+penguin have 2 block branches each).
   - `grounding-cue-reminder`, `close-cue-reminder` — log `nudge` when they actually inject.
   - Import block is `try/except`-guarded: a missing/broken helper degrades to a no-op `log_event`, so a logging fault can never break or block a hook.
3. **`developer-braindead/verification/ritual-stats.py`** — read-only reporter. Band A aggregates the ndjson (per-hook/decision, blocks by path-class + actor, nudges; `--days N` window). Band B parses `git log -M --diff-filter=R` renames → promotions/rejections/pins by layer + promote-rate.
4. **`.gitignore`** — `ritual-events.ndjson` (+ `.tmp.*`) ignored, consistent with `state.ndjson`/`chat.ndjson` (runtime telemetry, not committed; avoids parallel-session churn). The two `.py` files **are** tracked (code).

## Verified BOTH ways

- **py_compile** clean on the helper + all 9 wired hooks + the reporter.
- **Synthetic-payload harness** (13 cases, temp driver outside the brain): every block → exit 2 **and** one log line; every allow → exit 0 **and no** line; nudges → exit 0 + `nudge` line; silent prompt → no line. **Enforcement exit codes unchanged** from pre-instrumentation (no regression) — 13/13 PASS.
- **Live confirmation:** `ritual-events.ndjson` captured this session's own `require-open allow` rows (actor `braindead`, sid8 `03861733`) — the gate's allow-path logging fires in production, not just synthetic.
- **Reporter run:** Band A rendered the 14 test+live events; Band B derived real history — **40 promotions, 6 rejections, 87% promote rate, 5 keepsake pins** (by layer: examine=23, lorebook=10, niksis8_character=6, niksis8=1).

## Notes / open

- Local `ritual-events.ndjson` carries the synthetic `deadbeef` verification rows + my own session's allows. It's gitignored (never commits); a real Band A read uses `--days`/sid8 filtering. Didn't clear it — the require-open hook re-appends an allow on every one of my writes, so clearing races the hook; not worth fighting for a gitignored telemetry file.
- **`active-mode.txt` anomaly:** got reset to `unscoped` mid-session by something external (flagged intentional by the harness). Left it per the instruction; Braindead may not render on the cockpit. Visualizer-only, non-load-bearing. Flagged to principal.
- Band B is best-effort: content-rewritten promotions below git's rename-similarity threshold are missed (documented in the reporter output).

## Sequence status

Khaan dev-buildable now: recommended sequence ([[S114_277d9053_khaan-audit-and-open-gate|S114]]–[[S120_885d6702_khaan-item-4-five-lens-doctrine|S120]]) + item 11 (this) DONE. Still open: **item 9** (skill scaffolder, the other cheap carry); the `meta/write-rules.md` "enforced by hook" line (godly proposal, next bankstanding — a Guthix job); items 3/7/8/10 later-phase/§N; §Q workflows gated on §Q.2 (do hooks fire inside a workflow). Optional: a gielinor `lorebook/drafts/` D-NNN to anchor the five-lens doctrine.

**Cascade.** New `developer-braindead/verification/ritual-stats.py`; `bank/plan.md` §P.9 `[x]`; `bank/build-lessons.md` (the tracker-vs-catalogue lesson); this quest-log entry; `respawn.md` prepend; `comms/active.md` OPEN/UPDATE/CLOSING. Brain-root: new `switchboard/ritual_log.py`; `.gitignore` += `switchboard/ritual-events.ndjson`.

**Main-brain changes.** 9 hooks instrumented in `gielinor/.claude/hooks/` (`require-open-on-entry`, `block-confirmed-writes`, `block-deletes`, `block-sub-spawn`, `dwarf/gnome/penguin/shipping-agent-write-boundary`, `grounding-cue-reminder`, `close-cue-reminder`) — one `try/except`-guarded `log_event` each, at decision points only; no enforcement-logic change (exit codes verified unchanged). No writes to any player namespace, `confirmed/`, `meta/`, or `spellbook/rituals/`.
