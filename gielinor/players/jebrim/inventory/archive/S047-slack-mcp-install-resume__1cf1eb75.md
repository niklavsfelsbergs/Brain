# S047 — Slack MCP install, resume

**Quest:** `quest-log/in-progress/S047_1cf1eb75_slack-mcp-install.md`
**Status:** done (proposed complete this close)

## Where we are

Slack MCP server is live via `korotovsky/slack-mcp-server`, cookie-auth, authed as `niklavs.felsbergs` @ The Customization Group. Read toolset surfaced; posting disabled by config. Voice rule pinned to memory.

## Next concrete step

None for the install itself. Three optional follow-ups (principal call, no urgency):

1. **Rotate the leaked tokens.** Sign out of Slack web → sign back in → re-extract (URL-decoded) → swap in `.mcp.json`.
2. **Enable posting.** Edit `SLACK_MCP_ADD_MESSAGE_TOOL` from `""` to a channel-ID whitelist (preferred) or `"true"`. Restart Claude Code.
3. **Skill graduation.** If the MCP-install pattern recurs on Outlook MCP (S040), promote `bank/drafts/notes/workflow/slack-mcp-install.md` content into `spellbook/drafts/skills/mcp-server-install-pattern.md`.

## Files / paths to read first

- `brain/.mcp.json` (the install — gitignored)
- `bank/drafts/notes/workflow/slack-mcp-install.md` (workflow capture)
- Memory: `feedback-slack-posts-in-niklavs-voice` + `reference-slack-mcp-tcg`

## Pending drafts

None — all writes landed this session.
