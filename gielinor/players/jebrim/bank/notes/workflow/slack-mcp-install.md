# Slack MCP install — korotovsky cookie-auth path

**Drafted:** 2026-05-23 ([[S047_1cf1eb75_slack-mcp-install|S047]]). **Anchor:** the install walkthrough in `quest-log/in-progress/S047_1cf1eb75_slack-mcp-install.md`.

## What this is

End-to-end install of `korotovsky/slack-mcp-server` against a corporate Slack workspace using browser-cookie auth (`xoxc` + `xoxd`). The path used when bot installation isn't approved or when full user reach (DMs, private channels, post-as-self) is needed.

## The install in 6 steps

1. **Verify pre-reqs.** `node --version` ≥ 18; `npx --version` works.
2. **Extract `xoxc` from the workspace client.** Open `https://app.slack.com/client/<TEAM_ID>/<CHANNEL_ID>` in a browser (not the desktop app, not the `/ssb/redirect` launcher page). F12 → Console → run:
   ```js
   JSON.parse(localStorage.localConfig_v2).teams[document.location.pathname.match(/^\/client\/([A-Z0-9]+)/)[1]].token
   ```
   Returns `"xoxc-..."`. Strip the surrounding quotes when copying.
3. **Extract `xoxd` from cookies.** Same DevTools window → Application tab → Cookies → `https://app.slack.com` → cookie named `d` (just the letter). Double-click Value → Ctrl+C.
4. **Add server to `.mcp.json`** (root, gitignored):
   ```json
   "slack": {
     "command": "npx",
     "args": ["-y", "slack-mcp-server@latest", "--transport", "stdio"],
     "env": {
       "SLACK_MCP_XOXC_TOKEN": "xoxc-...",
       "SLACK_MCP_XOXD_TOKEN": "xoxd-...",
       "SLACK_MCP_ADD_MESSAGE_TOOL": "",
       "SLACK_MCP_LOG_LEVEL": "info"
     }
   }
   ```
   `SLACK_MCP_ADD_MESSAGE_TOOL=""` keeps posting disabled. Set to `"true"`, a channel-ID whitelist, or `"!Cxxx"` blacklist to enable.
5. **Pre-warm the npx cache** (see gotcha #2 below) before relying on Claude Code's auto-start.
6. **Restart Claude Code** in the same dir. `/mcp` should show `slack: connected` within a few seconds (post-warm).

## Gotchas — each one cost a turn during [[S047_1cf1eb75_slack-mcp-install|S047]]

1. **URL-encoded `xoxd`.** Edge displayed the `d` cookie value with `%2F` (slash) and `%2B` (plus) percent-encoded. The server wants the raw cookie (literal `/` and `+`). Symptom: `auth.test` returns `invalid_auth` immediately even though tokens look correct. Fix: decode the percent-escapes before pasting.
2. **30s MCP-connect timeout vs first-run npx download.** `npx -y slack-mcp-server@latest` downloads the npm wrapper + Go binary on first run — easily exceeds Claude Code's MCP-connect timeout. Symptom: `Failed to reconnect to slack: MCP server "slack" connection timed out after 30000ms`. Fix: pre-warm by running the server manually in a separate PowerShell with the same env vars; Ctrl+C once it logs *"Slack MCP Server is fully ready"*. Subsequent Claude Code starts hit the warm cache and connect in <5s.
3. **Wrong page for `xoxc` extraction.** `thecustomizationgroup.slack.com/ssb/redirect` (the desktop-app launcher) does NOT have `localConfig_v2` in localStorage. Snippet fails with `Cannot read properties of null`. Must be on `app.slack.com/client/T.../C...` (inside a channel of the workspace client). The redirect page offers a *"use Slack in your browser"* link to get there.
4. **`allow pasting` is Chrome-only.** Edge doesn't require it; typing the phrase in Edge's console produces a SyntaxError. Just paste the snippet directly in Edge.

## Sanity-check manual run (PowerShell)

```powershell
$env:SLACK_MCP_XOXC_TOKEN = "xoxc-..."
$env:SLACK_MCP_XOXD_TOKEN = "xoxd-..."   # URL-decoded
$env:SLACK_MCP_LOG_LEVEL = "debug"
npx -y slack-mcp-server@latest --transport stdio
```

Expected success log: `Authenticated to Slack` → `Caching users collection...` → `Loaded users from cache (count: N)` → `Loaded channels from cache (count: N)` → `Slack MCP Server is fully ready` → `Starting STDIO server`. Ctrl+C once it's idle waiting for stdin.

## Cache + persistence

Server caches users + channels per-team in `%LocalAppData%\slack-mcp-server\T<TEAM_ID>_users_cache.json` and `..._channels_cache_v2.json`. Default TTL 24h; stale data served while background refresh runs. Cache survives Claude Code restarts.

## Token lifetime + rotation

`xoxc` + `xoxd` are tied to the browser session: signing out of Slack web invalidates the `d` cookie immediately, and most other session events (password reset, SSO re-auth) revoke it too. When the MCP starts erroring with `invalid_auth`, re-extract.

## Source

Full step-by-step including failure modes: `quest-log/in-progress/S047_1cf1eb75_slack-mcp-install.md`. Server docs: `https://github.com/korotovsky/slack-mcp-server`.
