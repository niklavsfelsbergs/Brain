# S089 — cockpit duplicate-row fix (session-id rotation re-announce)

**Session:** braindead-35b35dc5 · 2026-05-25 · dev-brain via "lets develop gielinor" (mid-conversation; OPEN posted).
**Status:** committed; **EYES-ONLY post-relaunch verify pending** → stays in-progress.

## The report

Principal: a cockpit-launched braindead session "suddenly turned into running on VScode, but it definitely isnt, i just triggered it from the cockpit" + "split into 2 switchboard sessions — one idle (the real one), and the one showing statuses says the original is in vscode … somehow got doubled." Later, with a board screenshot: *the bottom two rows are the same session — the "braindead" one is read-only like the VScode ones, the "chat" one is where I can actually drive it.*

## Diagnosis (read the live payload first — S087 lesson)

It was never a host-classification bug:

- Curled `/api/sessions` 5× over 5s — always the 4 real cockpit rows, **no vscode tag, no duplicate sid8**. The board the principal saw was holding a row the backend no longer returned.
- Every `host=vscode` status file on disk is a **genuine** VS Code session (`Code.exe` in `claude_pid_chain`), all ended ~30–50min earlier.
- A `CLAUDE_COCKPIT` session **cannot structurally** flip to vscode — `status-sidecar.py:1641` re-detects host every fire and `CLAUDE_COCKPIT` wins over the leaked `VSCODE_PID`; confirmed `CLAUDE_COCKPIT=1` live in this session's env.

**Real root cause — session-id rotation.** `ptybridge.py` announces the session id **once** at `/pty` connect (`claude --session-id <uuid>`). When the conversation in that one terminal rotates to a new id (a `/clear`, or one task ending and a new one starting in the same shell), the hooks track the new id but the cockpit's `TermConn` keeps the old announced sid8. Result on the board:

- **manifest row** (current session) → no live terminal matches its sid8 → `openPeek` = **read-only** ("acting like the VScode ones").
- **liveTerms row** (stale sid8) → the actual PTY → **drivable**, but mislabeled "chat" with the prior session's stale feed line.
- dedup at `main.js:342` (`!known.has(t.sid8)`) can't merge them — two different sid8s → two rows.

## The fix

- **`cockpit/ptybridge.py`** — new `_session_for_shell_pid()` reads `state-switchboard.json` and returns the freshest live session whose `claude_pid_chain` contains this PTY's shell pid. New per-terminal `watch_session()` task polls it every 2s; on a change vs the announced id, re-announces a `session` frame (`rotated: true`). Cancelled in the handler `finally`.
- **`cockpit/web/term.js`** — the `f.t === "session"` handler now handles re-announce: deletes the stale `bySid8` key, `removeOwned(prevSessionId)` + `addOwned(newSessionId)` (so a reopened cockpit resumes the *current* convo), re-registers under the new sid8. liveTerms then reports the current id → board dedups against the manifest row → **dupe collapses to one drivable row, no relaunch needed**.
- **`cockpit/web/board.js`** — build tag `b87.1` → `b88.1`.

## Verification

Headless (all green):
- `proc.pid` from `PtyProcess.spawn` **== the powershell pid** that lands in `claude_pid_chain` (the load-bearing unknown — live winpty spawn confirmed `7072 → powershell.exe`).
- `_session_for_shell_pid` against the real manifest: each terminal's powershell pid resolves to its own session; synthetic shared-pid case → freshest wins; malformed/missing manifest → `None`.
- `py_compile ptybridge.py`, `node --check` (term/board/main), `test_backend.py` **39/39**.

**Pending (eyes-only, needs a relaunch that ends this session):** board reads **b88.1**; drive a terminal then `/clear` (or finish one task, start another) → board shows **one drivable row**, not a stale ghost + a read-only row.

## Notes / caveats

- The **current** on-screen dupe only clears on relaunch (the running window holds old JS); that terminal will resume the **earlier** conversation (its owned-uuid predates this fix). Rotations self-heal from here on.
- Cross-link: @f731b4e8's **D-030** (git-worktree isolation) is the parallel-session collision-**gate** track; this S089 is the cockpit display-**attribution** track — same neighborhood, different layer.
- Strategic next step unchanged — the §C shipping-mart pilot (the outward build) per [[D-027_inward_outward_build_imbalance]].
