# S040_p1 — Outlook / M365 MCP landscape research

**Role:** Penguin (p1) — research operative for Jebrim
**Date opened:** 2026-05-23
**Brief:** Survey Outlook / Microsoft 365 / Exchange MCP servers available for Claude / MCP clients. Identify candidates, capabilities, maturity, auth model. Recommend first-to-try.
**Deliverable:** `players/jebrim/research/2026-05-23-outlook-mcp-landscape.md`

## Turn log

- Opening: read research skill, drafted source map. Plan to broad-scout for official Microsoft MCP, then Anthropic mcp-servers repo, then community.
- Broad scout (3 parallel WebSearches): turned up (a) Anthropic's official Claude M365 connector — first-party, OBO flow; (b) Microsoft's official Graph MCP server (learn.microsoft.com); (c) ~10 community MCPs incl. Softeria ms-365-mcp-server, ryaker/outlook-mcp, XenoXilus/outlook-mcp, marlonluo2018/outlook-mcp-server (COM-based local), pnp/cli-microsoft365-mcp-server, hvkshetry/office-365-mcp-server. Source map shaping up clearly.
- Narrow reads: fetched MS Learn (Enterprise Graph MCP — preview, read-only Entra/identity only), Softeria README (200+ tools, 729 stars, device-code auth, Claude Code supported), Anthropic M365 connector security guide (OBO, **read-only**, admin consent required, no .mcp.json), ryaker/outlook-mcp (379 stars, OAuth full mail+calendar+OneDrive+Power Automate), XenoXilus (24 stars, PKCE, recent), marlonluo2018 (Windows-only COM, 12 stars), hvkshetry (14 stars, not production-ready), pnp/cli-microsoft365-mcp-server (107 stars, full read+write across most of M365 via existing m365 login), Aanerud outlook-desktop-mcp (Win+Mac COM/AppleScript, 27 stars, no Graph required), littlebearapps/outlook-assistant (16 stars, 22 tools, device-code, explicit Claude Code support, forensic features).
- Synthesis: writing deliverable. Recommendation cluster: Softeria (broadest, most active) or littlebearapps (cleaner Outlook focus + Claude Code first-class) for full-assistant use. Anthropic connector covers read-only but cannot send/draft — fails the brief.
- Delivered: `research/2026-05-23-outlook-mcp-landscape.md`. Tier'd 4 ways (first-party narrow, community-broad, Outlook-focused Graph, local-desktop COM). Primary recommendation Softeria; fallback littlebearapps; escape hatches pnp/cli-m365 (no fresh Entra app needed) and Aanerud (no Graph at all). Open: Claude Code compat of the Anthropic connector, tenant Entra-app policy (P2's call).
