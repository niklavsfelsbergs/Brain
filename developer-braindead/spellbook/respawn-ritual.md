# respawn-ritual — session-start procedure

**Invoked.** At the start of every dev session, before substantive work begins.

**Produces.** Shared context between user and Claude on where we are and what's next.

## Steps

1. **Confirm brain.** Ask which brain we're working on (`developer-braindead/` vs `vault/`) unless the user has already stated it. Per [[D-005]].
2. **Read `respawn.md`.** It's the entry point — current state, what's open, next concrete step.
3. **Read the latest quest-log entry** (`quest-log/SNNN_*.md`, highest NNN). This is the most recent narrative; tells you *how* we got here, not just *where* we are.
4. **Read referenced files only as cited.** Don't pre-load `bank/` — it's reference material, fetched on demand.
5. **State the plan for this session** back to the user in 1–3 sentences. Get a nod (or a redirect) before acting.

## Notes

- The "ask which brain" step is the one most worth not skipping. Implicit defaults rot.
- If `respawn.md` is stale (last updated > 2 sessions ago, or references files that no longer exist), flag it before relying on its claims.
