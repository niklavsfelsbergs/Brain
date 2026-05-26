# respawn-ritual — session-start procedure

**Invoked.** At the start of every dev session, before substantive work begins — **including a mid-conversation pivot into dev-brain via "lets develop gielinor".** That cue is not a lighter-weight entry; it runs this same ritual, sibling-detection and `OPEN` (steps 6–8) included.

**Produces.** Shared context between user and Claude on where we are and what's next.

## Steps

1. **Confirm brain.** Ask which brain we're working on (`developer-braindead/` vs `vault/`) unless the user has already stated it. Per [[D-005_session_start_protocol]].
2. **Read `respawn.md`.** It's the entry point — current state, what's open, next concrete step.
3. **Read the latest quest-log entry** (`quest-log/SNNN_*.md`, highest NNN). This is the most recent narrative; tells you *how* we got here, not just *where* we are.
4. **Read referenced files only as cited.** Don't pre-load `bank/` — it's reference material, fetched on demand.
5. **Write the visualizer marker.** Set `brain/.claude/active-mode.txt` to `dev-brain` so the hook spawns Braindead in the visualizer. Skip silently if the file already says `dev-brain`. (Visualizer concern only — not architecturally enforced.)
6. **Detect live Braindead siblings.** Per [[D-019_parallel_braindead_and_comms_channel]] — parallel dev sessions need to know about each other before picking work.
   - List intent files matching `brain/.claude/intent/braindead-*.txt` whose mtime is within the last 5 minutes. Exclude your own (`braindead-<sid8>.txt` where `<sid8>` is the first 8 chars of `CLAUDE_CODE_SESSION_ID`).
   - Read `comms/active.md`. Scan the last ~20 entries for any sibling id from the previous step lacking a `CLOSING` entry — that's a confirmed-live sibling.
   - Also flag any `OPEN` entry whose author's intent file is stale (mtime > 5min) and has no `CLOSING`. Surface these as candidates for `ABANDONED` synthesis.
   - If there are no live siblings and no stale OPENs, proceed silently. If there is anything to surface, state it in plain language before step 7: *"Detected one live sibling — braindead-9c1f2a4b, currently on gielinor/meta/communication-protocol.md. They've left Step 4 demos open."*
7. **State the plan for this session** back to the user in 1–3 sentences. Get a nod (or a redirect) before acting. If a live sibling was detected in step 6, the plan must explicitly account for them — pick non-overlapping targets, or explain why overlap is fine.
8. **Post the `OPEN` entry to `comms/active.md`.** After the user nods on the plan. Format per `comms/_about.md`:

   ```
   [YYYY-MM-DD HH:MM] braindead-<sid8> OPEN
     Targets: <files/areas this session will touch>
     Steering clear of: <areas a sibling is on, or areas this session won't touch>
     Open to handoff: <work surfaced in respawn.md that this session won't pick up>
   ```

   Append-only — never edit an existing entry.

## Notes

- The "ask which brain" step is the one most worth not skipping. Implicit defaults rot.
- If `respawn.md` is stale (last updated > 2 sessions ago, or references files that no longer exist), flag it before relying on its claims.
- **Sibling detection produces noise, not certainty.** A fresh intent file doesn't prove the sibling session is actually alive (crashed sessions leave their last intent behind for 5 minutes). Surface the detection; the principal decides whether to assume the sibling is live, ping them, or treat as `ABANDONED`. Don't pre-empt that judgment.
- **`OPEN` entries are commitments.** Don't post one until the principal has nodded on the plan. A rejected target shouldn't appear in `active.md` — that file is the operational record of what's actually in flight.
- **The `OPEN` is the half that prevents collisions — do not skip it on mid-conversation entry.** The recurring *"did not post an OPEN — dev-brain entered mid-conversation"* note across `comms/active.md` (S034, S037–S043, S046, S057, S060, …) is the system's most common discipline leak: `CLOSING` gets posted faithfully, `OPEN` only ~30% of the time. `CLOSING` is the autopsy; `OPEN` + sibling-detection is the seatbelt. Fire steps 6–8 on every entry regardless of how dev-brain was reached. A talk-only or test-only session still posts an `OPEN` (its target can be "discussion only, no file targets") — that's how a sibling knows you're live.
