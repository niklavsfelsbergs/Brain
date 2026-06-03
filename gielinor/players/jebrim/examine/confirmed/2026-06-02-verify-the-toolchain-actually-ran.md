# Verify the toolchain actually RAN before trusting a green exit

**Observation ([[S146_f20d7744_scm-serving-memory-review|S146]], 2026-06-02).** I ran `npm run build 2>&1 | tail -60; echo "=== build done ==="` and the harness reported **exit 0** — I declared "build passed, type-check clean." It hadn't: the trailing `echo` masked the real exit, and `next` wasn't even on PATH (the `npm ci` had silently FAILED on duckdb's native node-pre-gyp build under node-25). The "green" was the echo's exit, not the build's. I caught it only by re-reading the captured output and seeing `'next' is not recognized`.

**Rule.** A zero exit means nothing if the command never ran, or if a trailing `echo`/pipe swallowed the real status. Before trusting a "passed":
- Don't end a verification command with `; echo done` — the echo's exit overrides. Capture the real exit (`cmd; echo "EXIT=$?"`) or read the actual tool output for the success marker.
- Confirm the tool was even invoked (binary resolves, install completed) — a failed/partial `npm ci` leaves `node_modules` without `.bin`, so every script "succeeds" by not-running.
- This is the shell-verification instance of [[2026-06-01-verify-diffs-both-ways|verify-diffs-both-ways]] and the "verify the measurement measures the thing" family: prove the instrument ran and measured the thing, then trust the number.

Caught and corrected in-session (re-ran with `node_modules/.bin/tsc` directly → genuine exit 0; `next build` → genuine "Compiled successfully" + the real duckdb-native failure isolated as an env artifact). No false "done" shipped.
