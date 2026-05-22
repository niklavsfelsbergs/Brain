# S047 — Slack MCP install (TCG corp)

**Session:** S047 (born in same Claude Code session as S040, sid8 `1cf1eb75`)
**Player:** Jebrim
**Date opened:** 2026-05-23

## Ask

Principal (in middle of S040 Outlook MCP parking): *"Hey Jebrim, youre smart, help me implement the slack mcp"*. Then *"walk me through step by step"*.

Scope confirmed via 3-q batch:
- **Workspace:** TCG corporate (`thecustomizationgroup.slack.com`, team `T02MRFLS3`).
- **Server:** `korotovsky/slack-mcp-server` (Go, MIT, active; cookie auth supports full user reach incl. DMs and private channels; bot install not required at corp).
- **Scope:** read public channels, read DMs/private channels, post messages, search history. All require cookie auth (xoxc + xoxd), not bot token.

## Plan

Cookie-auth install (no bot install, no admin involvement). Drop server entry into `brain/.mcp.json` (gitignored, already holds `redshift`/`orps` with raw creds — consistent pattern). Posting disabled by config until explicitly flipped. Walk extraction + install + smoke test step-by-step.

## Turns

- **T1 (2026-05-23).** Pre-install scoping: read jebrim's keepsake + last-alched + comms; checked brain/.mcp.json gitignore status (root .mcp.json gitignored; gielinor/.mcp.json tracked but placeholder). Posted comms UPDATE on jebrim-1cf1eb75 noting Slack as sibling scope to S040. Batched 3 unblocking questions.
- **T2.** Wrote .mcp.json `slack` entry with placeholder tokens + `SLACK_MCP_ADD_MESSAGE_TOOL=""` (posting off). Verified install path against korotovsky README + auth-setup + config-usage docs via WebFetch — pulled real npx invocation + env-var names + extraction snippet rather than relying on recall.
- **T3.** Step 1 (Node ≥18 verified) → Step 2 (xoxc extraction). Principal hit wrong page: `/ssb/redirect` is the desktop-app launcher, not the workspace client; `localConfig_v2` only exists on `app.slack.com/client/T.../C...`. Redirected via the "use Slack in your browser" link visible on the redirect page. Also clarified: Edge doesn't need `allow pasting` ceremony (Chrome's quirk).
- **T4.** Step 3 xoxd extraction (cookie `d` from Application tab). Step 4 paste into .mcp.json. Principal pasted tokens directly in chat — flagged the leak (transcript persists; rotate after install verifies). Step 5 restart Claude Code: MCP connect timed out at 30s.
- **T5.** Diagnosed: first-run npx download exceeds Claude Code's 30s MCP timeout on Windows. Pre-warm path: run server manually in PowerShell to populate npx cache + surface real auth error. Got `invalid_auth` from `auth.test`.
- **T6.** Root cause: Edge cookie value showed URL-encoded form (`%2F`, `%2B`). Slack `d` cookie is base64-style session blob with literal `/` and `+`; server wants raw, not percent-encoded. Decoded xoxd and pasted decoded form in .mcp.json. Re-ran manual server: **authenticated as `niklavs.felsbergs` @ The Customization Group, 2439 users + 175 channels cached**. Ctrl+C, restart Claude Code, `/mcp` showed `slack: connected`.
- **T7.** Principal cued behavioral rule: *"whenever we send slack messages... LEts ack like me okay?"* Recognized as sticky cross-session rule, not one-off. Captured to memory (NOT to gielinor's lorebook — light-touch, no draft ceremony needed): `feedback-slack-posts-in-niklavs-voice` (voice cues from this session's transcript, draft-and-confirm-before-send discipline) + `reference-slack-mcp-tcg` (install state + gotchas inventory). MEMORY.md index updated.
- **T8.** Comms UPDATE on jebrim-1cf1eb75 announcing Slack live + voice rule.
- **T9.** Brief pivot back to Outlook MCP recall (S040 re-engagement; logged in S040 entry T8). User parked again on portal.azure.com sign-in confusion.
- **T10.** Principal cued wrap. Close ritual begins.

## Decisions

- **Server choice:** korotovsky over modelcontextprotocol/server-slack. Bot-token server is archived and can't see DMs/private channels; cookie-auth path is the only one that meets the read-DM + read-private scope on a corp tenant without admin install.
- **Tokens in root `.mcp.json`** (gitignored), not in `gielinor/.mcp.json` (tracked placeholder). Consistent with existing `redshift`/`orps` pattern.
- **Posting disabled by config** (`SLACK_MCP_ADD_MESSAGE_TOOL=""`) until explicitly flipped. Surfaced as a knob, not a default.
- **Voice rule pinned to memory, not lorebook.** Light-touch, behavioral, doesn't need principal draft-approval ceremony. If it generalizes (e.g., "draft any outbound message that posts as Niklavs in his voice") it can graduate.

## Pending external actions

None pending.

## Follow-ups (parked, principal call)

1. **Rotate the leaked tokens.** Sign out of Slack web → sign back in → re-extract (URL-decoded this time) → swap in `.mcp.json`. Cheap insurance.
2. **Enable posting.** One env-var edit + Claude Code restart. Recommended: start with a small whitelist (own DMs + 1-2 low-stakes channels) before flipping to `"true"`.
3. **Skill graduation candidate.** "MCP server install pattern" — pre-warm via manual run when first-load exceeds Claude Code's 30s timeout, URL-encoding gotcha for cookie-auth servers, real-config fetch via WebFetch over recall. Applied once here; held for second-occurrence before graduating to `spellbook/skills/`. (Per harvest rule, captured as workflow bank note this session; skill graduation is alching's job.)
