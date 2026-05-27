# S065 — cockpit hang: AskUserQuestion/ExitPlanMode auto-dismissed in headless `claude -p`

**Session:** braindead-bfa95764 (one of two parallel cockpit-driven sessions the
principal launched; sibling braindead-f1df4fa5 hit the same wall).
**Mode:** dev-brain. **Surface:** `cockpit/backend.py`, `cockpit/_about.md`.

## The report

Principal, mid-respawn: *"i cant answer in the cockpit, its broken."* Both this
session and f1df4fa5 had just issued an `AskUserQuestion` ("which cockpit thread
to push on" / "what should this session focus on"). The principal could not
answer either — the cockpit console showed a question with no way to respond.

## Diagnosis (evidence, not theory)

- esm.sh reachable (HTTP 200), backend serving :8770 (200), all `web/*.js` pass
  `node --check` → **not** a blank-render / dead-server / CDN problem.
- `chat.ndjson` showed both braindead sessions emit `needs_you` (the
  status-sidecar's AskUserQuestion PreToolUse signal, [[S053_c082b489_switchboard_visual_ux_overhaul|S053]]) then sit at
  `waiting_for_user` — the wedge signature.
- **Probe** (`_probe_ask.py`, mimics `backend.chat_handler`): forced an
  `AskUserQuestion`, then sent a `tool_result` over stdin. The CLI had **already
  auto-injected its own** `tool_result` `{content:"Answer questions?",
  is_error:true}` — the exact dismissal string. **Headless `claude -p`
  auto-dismisses AskUserQuestion the instant it's called; no stream-json client
  can intercept or supply the answer.** ExitPlanMode is the same family (needs a
  TTY to approve). So the cockpit *fundamentally* cannot answer these tools.
- Second probe: launching with `--disallowedTools "AskUserQuestion ExitPlanMode"`
  → the model does **not** call the tool; it asks `"Do you prefer option A or
  option B?"` in plain prose, `is_error=false`. Prose is answerable in the
  composer.

## Fix (landed, on disk)

`cockpit/backend.py`:
- new `NO_TTY_TOOLS = "AskUserQuestion ExitPlanMode"` constant (commented with
  the why);
- `chat_handler` args gain `--disallowedTools NO_TTY_TOOLS`.
Driven sessions now ask in prose instead of reaching for a tool the harness will
auto-dismiss. `cockpit/_about.md` driver note updated. `py_compile` green.

## To take effect

The running cockpit (`app.py`, PID 39988) holds the **old** backend in memory and
builds the claude args per `/chat` connection, so the fix is inert until the
**cockpit process is relaunched** (close + reopen the window / Switchboard icon).
The two wedged sessions (this one + f1df4fa5) are this backend's headless
children — they die on relaunch; just re-place them. **Not self-restarted:**
killing the backend would terminate this very session mid-response.

## Open / next

- Principal: relaunch the cockpit, place a session, confirm a question now lands
  as a prose bubble answerable in the composer (mechanism proven by probe;
  end-to-end-in-window not yet eyeballed since this session can't outlive the
  relaunch).
- Commit not yet made (principal sign-off pending; the on-disk edit already
  suffices for the relaunch). Exclude throwaway `cockpit/_probe_ask.py` from any
  commit (or archive it).
- Offline-vendor Preact/htm (respawn Step 0 #2) remains separately deferred — the
  intended task this session before the breakage surfaced.
