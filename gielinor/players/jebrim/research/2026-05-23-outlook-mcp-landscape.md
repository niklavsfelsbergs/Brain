# Outlook / Microsoft 365 / Exchange MCP server landscape

## Question

What MCP servers exist for accessing Outlook / Microsoft 365 / Exchange (mail, calendar, contacts) from Claude (Code / Desktop) and the broader MCP ecosystem as of late May 2026? Which is the right one to try first for a "full assistant" use case — read mail, search, draft, send, calendar — on a corporate M365 tenant?

## Date of research

2026-05-23.

## Confidence

**Medium-high** on the landscape map (the four "tiers" of options are clear, with primary sources for each). **Medium** on specific maturity numbers (star counts and last-release dates are accurate snapshots but churn weekly; a server that's "active today" may be unmaintained in three months). **Low** on the corporate-tenant operational reality — admin consent, conditional-access policy interaction, MFA loops are P2's territory and were not deep-dived here.

## Sources

- [Microsoft MCP Server for Enterprise — Microsoft Graph overview](https://learn.microsoft.com/en-us/graph/mcp-server/overview) — official Microsoft, currently in **public preview**, last updated 2025-12-03. Load-bearing because it defines what "official Microsoft" actually means right now (and how narrow it is).
- [Microsoft 365 connector security guide — Claude Help Center](https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide) — Anthropic's hosted M365 connector. Load-bearing because it's the first-party answer for Claude.ai but constrains scope (read-only, no Claude Code .mcp.json integration described).
- [Set up the Microsoft 365 connector — Claude Help Center](https://support.claude.com/en/articles/12542951-enabling-and-using-the-microsoft-365-connector) — setup-side companion to the security guide.
- [Tony Redmond on the Anthropic M365 connector (2026-04-08)](https://office365itpros.com/2026/04/08/microsoft-365-connector-for-claude/) — independent confirmation that the connector is **read-only** ("cannot create new documents, chats, emails, or messages") and runs against the dual Entra apps `M365 MCP Server for Claude` + `M365 MCP Client for Claude` via OBO. This single line is what kicks the Anthropic connector out of contention for the full-assistant brief.
- [softeria/ms-365-mcp-server (GitHub)](https://github.com/softeria/ms-365-mcp-server) — 729 stars, 290 forks, v0.112.2 released 2026-05-22 (yesterday). MIT. 200+ Graph tools, multi-account, read-only flag, stdio/HTTP/SSE. Load-bearing as the most actively maintained broad community option.
- [littlebearapps/outlook-mcp (GitHub)](https://github.com/littlebearapps/outlook-mcp) — published as `@littlebearapps/outlook-assistant`. 16 stars but recent (v3.7.4 2026-05-05), MIT, 22 consolidated tools, **first-class Claude Code support documented**, device-code default. Load-bearing as the Outlook-focused alternative to Softeria's breadth.
- [ryaker/outlook-mcp (GitHub)](https://github.com/ryaker/outlook-mcp) — 379 stars, 134 forks, JavaScript/Node. Mail + calendar + OneDrive + Power Automate. Older, larger community, but Claude Code support not explicitly documented (Claude Desktop only).
- [XenoXilus/outlook-mcp (GitHub)](https://github.com/XenoXilus/outlook-mcp) — 24 stars, last commit Jan 2026 (v1.0.1), MIT, PKCE OAuth. Explicit multi-client support (Claude, ChatGPT, generic MCP).
- [pnp/cli-microsoft365-mcp-server (GitHub)](https://github.com/pnp/cli-microsoft365-mcp-server) — 107 stars, PnP community project (Microsoft-adjacent semi-official tooling). Wraps the established CLI for M365 — leverages existing `m365 login`. Broad surface, full read+write, "best with Claude Sonnet 4 or 3.7."
- [Aanerud/outlook-desktop-mcp (GitHub)](https://github.com/Aanerud/outlook-desktop-mcp) — 27 stars, AGPL-3.0, Python. Uses local Outlook Desktop via COM (Windows, 29 tools) / AppleScript (macOS, 22 tools). No Graph, no Entra registration, inherits the desktop client's auth.
- [marlonluo2018/outlook-mcp-server (GitHub)](https://github.com/marlonluo2018/outlook-mcp-server) — 12 stars, MIT, Python. Win32 COM, Windows-only. Smaller and narrower than Aanerud.
- [hvkshetry/office-365-mcp-server (GitHub)](https://github.com/hvkshetry/office-365-mcp-server) — 14 stars, MIT, 24 tools across mail/calendar/Teams/planner. **Authors explicitly state "not yet production-ready."** Listed for completeness.

## Findings

### Q1 — What MCP servers exist?

Four tiers, each answering a different question.

**Tier 1 — first-party but narrow.** Two "official" options exist, and neither solves the full-assistant brief on its own.

- **Microsoft MCP Server for Enterprise** at `https://mcp.svc.cloud.microsoft/enterprise` is currently in **public preview** and is **scoped to read-only Microsoft Entra identity/directory data** — users, groups, applications, devices, admin reporting. It does **not** expose Outlook mail or calendar. ([MS Learn](https://learn.microsoft.com/en-us/graph/mcp-server/overview))
- **Anthropic Microsoft 365 connector** — Anthropic-hosted, available on all Claude plans, OBO flow against `M365 MCP Server for Claude` + `M365 MCP Client for Claude` Entra apps. Covers Outlook mail search, calendar search, OneDrive, Teams chat search, SharePoint. **Read-only — "cannot create new documents, chats, emails, or messages."** Requires Microsoft Entra Global Admin one-time consent at the tenant. Documentation is silent on whether it surfaces inside Claude Code (the .mcp.json path); the architecture is "Anthropic-hosted connector" not "local MCP server," which suggests it lives in Claude.ai/Desktop and not in Claude Code's local MCP runtime. ([Claude Help Center](https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide), [Tony Redmond](https://office365itpros.com/2026/04/08/microsoft-365-connector-for-claude/))

**Tier 2 — community-official broad servers.** These cover most of the Graph surface with read+write, and run as local stdio MCP servers compatible with Claude Code.

- **softeria/ms-365-mcp-server** — 200+ tools, 729 stars, very active (v0.112.2 released 2026-05-22), MIT, device-code default with HTTP/OAuth/BYOT options, multi-account, read-only flag, npm/Docker. The most active broad option. ([GitHub](https://github.com/softeria/ms-365-mcp-server))
- **pnp/cli-microsoft365-mcp-server** — 107 stars, MIT, wraps the PnP community's mature `cli-microsoft365` (10+ year-old project) as MCP. **Re-uses your existing `m365 login` context** — no separate Azure app registration needed if you already use the CLI. Full read+write across Outlook/SharePoint/Teams/Entra/Planner. Authors recommend Claude Sonnet 4 / 3.7. ([GitHub](https://github.com/pnp/cli-microsoft365-mcp-server))

**Tier 3 — Outlook-focused Graph MCPs.** Narrower scope (mail + calendar, sometimes contacts/SharePoint), often easier to reason about than the 200-tool wall.

- **littlebearapps/outlook-assistant** — `@littlebearapps/outlook-assistant`, 22 tools, MIT, v3.7.4 from 2026-05-05. Explicit Claude Code + Claude Desktop documentation. Device-code default, fallback browser-redirect flow. Includes forensic-headers and delta-sync features not in the broader options. ([GitHub](https://github.com/littlebearapps/outlook-mcp))
- **ryaker/outlook-mcp** — 379 stars (popular but older), mail + calendar + OneDrive + Power Automate. Claude Desktop documented; Claude Code not explicitly documented but the stdio shape suggests it'll work. Footgun called out: "Client secret must use VALUE field, not Secret ID" — common Azure app reg gotcha. ([GitHub](https://github.com/ryaker/outlook-mcp))
- **XenoXilus/outlook-mcp** — 24 stars, v1.0.1 from Jan 2026, MIT, PKCE OAuth (no client secret). Mail (read/search/send/reply/draft/attachments), calendar, SharePoint via link/ID. Generic MCP-client support. ([GitHub](https://github.com/XenoXilus/outlook-mcp))
- **hvkshetry/office-365-mcp-server** — 24 consolidated tools, mail + calendar + Teams + planner + notifications. Authors flag "**not yet production-ready**." Listed for completeness; not a first-choice candidate. ([GitHub](https://github.com/hvkshetry/office-365-mcp-server))

**Tier 4 — local-Outlook MCPs (no Graph, no Entra registration).** Sidesteps the corporate-IT auth problem entirely; Outlook Desktop is the auth, the MCP is just a tool wrapper. The catch: needs the desktop client running, doesn't work in headless / VPS / cloud scenarios.

- **Aanerud/outlook-desktop-mcp** — Win COM (29 tools) + Mac AppleScript (22 tools), AGPL-3.0, Python, read+write, install via `pip install outlook-desktop-mcp` then `claude mcp add outlook-desktop`. ([GitHub](https://github.com/Aanerud/outlook-desktop-mcp))
- **marlonluo2018/outlook-mcp-server** — Win-only COM, 12 stars, MIT, smaller scope. ([GitHub](https://github.com/marlonluo2018/outlook-mcp-server))

### Q2 — Capability / maturity / license / transport / install / auth (summary table)

| Server | Scope | Mail R/W | Cal R/W | Maturity | License | Transport | Install | Auth |
|---|---|---|---|---|---|---|---|---|
| MS Graph Enterprise MCP | Entra/identity only | — | — | **Preview**, MS-hosted | MS APIs ToU | HTTP (hosted endpoint) | Hosted, no install | Delegated Graph scopes |
| Anthropic M365 connector | mail/cal/files/Teams/SP | R only | R only | GA on Claude plans | Anthropic-hosted | Anthropic-hosted | Claude.ai/Desktop config | OBO + Entra global admin consent |
| softeria/ms-365-mcp-server | 200+ Graph tools | R+W | R+W | v0.112.2 2026-05-22, **very active** | MIT | stdio / HTTP / SSE | `npx @softeria/ms-365-mcp-server` / Docker | Device code (default), OAuth 2.1, BYOT |
| pnp/cli-microsoft365-mcp-server | full M365 admin+user | R+W | R+W | 107 stars, active | MIT | stdio | `npm i -g @pnp/cli-microsoft365` + `npx @pnp/cli-microsoft365-mcp-server` | Re-uses existing `m365 login` |
| littlebearapps/outlook-assistant | Outlook+contacts+rules | R+W | R+W | v3.7.4 2026-05-05, active | MIT | stdio | `npx @littlebearapps/outlook-assistant` | Device code (default), OAuth fallback |
| ryaker/outlook-mcp | Outlook + OneDrive + Flow | R+W | R+W | 379 stars, mature | (not displayed) | stdio | `git clone` + `npm install` + auth server on :3333 | OAuth 2.0 client-secret |
| XenoXilus/outlook-mcp | Outlook + SharePoint | R+W | R+W | v1.0.1 2026-01-18 | MIT | stdio | DXT extension or CLI | OAuth 2.0 PKCE (no client secret) |
| hvkshetry/office-365-mcp-server | Outlook + Teams + Planner | R+W | R+W | 14 stars, **not prod-ready** | MIT | stdio / HTTP-SSE | clone + npm + .env | OAuth 2.0 |
| Aanerud/outlook-desktop-mcp | Local Outlook desktop | R+W | R+W | 27 stars | AGPL-3.0 | stdio | `pip install outlook-desktop-mcp` | **None — inherits Outlook client** |
| marlonluo2018/outlook-mcp-server | Local Outlook (Win COM) | R+W | R+W | 12 stars | MIT | stdio | `uvx` / `pip` | **None — inherits Outlook client** |

### Q3 — Claude Code compatibility + known footguns

All Tier 2–4 servers above are stdio MCP servers and slot into Claude Code's `.mcp.json` cleanly — `command` + `args` + optional `env`. Explicit Claude Code documentation appears in **softeria/ms-365-mcp-server**, **littlebearapps/outlook-assistant**, **pnp/cli-microsoft365-mcp-server**, and **Aanerud/outlook-desktop-mcp**. The others (ryaker, XenoXilus, marlonluo2018, hvkshetry) document Claude Desktop primarily but use the same stdio shape and should work in Claude Code with equivalent config.

The **Anthropic M365 connector** is the outlier: it's an Anthropic-hosted integration, not a local MCP server, and the documentation doesn't describe a `.mcp.json` path. *(Inferred from the architecture description — "Anthropic-hosted," dual Entra apps, OBO — and the absence of any setup-from-Claude-Code mention in the security guide or setup article.)*

**Footguns surfaced in the sources:**

- **ryaker/outlook-mcp**: client-secret VALUE-vs-ID confusion (Azure portal gotcha); port-3333 conflict on the auth server.
- **softeria/ms-365-mcp-server**: TOON output format flagged experimental; nothing else load-bearing.
- **littlebearapps/outlook-assistant**: pre-v3.7.2 had a token-refresh bug that broke device-code auth after ~60 min — fixed but worth pinning to ≥v3.7.2; rate-limiting and recipient-allowlist safety features are **off by default**; personal-account `$search` limitations on Outlook.
- **hvkshetry/office-365-mcp-server**: authors say not production-ready — take at face value.
- **Aanerud / marlonluo2018**: Outlook Desktop must be running constantly; no headless/cloud path.
- **Anthropic connector**: read-only is the load-bearing limitation — *cannot draft, cannot send*. Also requires Entra Global Admin consent at the tenant, which is the same conditional-access hurdle as any third-party Entra app and *not* a free pass. RCD (Restricted Content Discovery) and sensitivity-labeled files are blocked even on the read side.

### Q4 — Recommendation for "full assistant" (read + draft + send + search + calendar)

The Anthropic M365 connector is the obvious *non*-answer because it's read-only. If the brief said "search my mail and summarize," it'd be the right call (zero friction, Anthropic-hosted, no Azure app reg). It doesn't, so it's out.

The Microsoft Enterprise MCP is out too — wrong scope entirely (Entra identity, not Outlook mail).

Among the remaining options, two stand out for **first-to-try** depending on operator preference:

**Primary recommendation: `softeria/ms-365-mcp-server`.** Reasons:

1. Active to the day (v0.112.2 released 2026-05-22).
2. Broadest tool surface (200+) — covers everything in the brief and then some.
3. Device-code auth as the default — simpler than client-secret OAuth at corporate tenants where you can't always register your own Entra app (P2 territory).
4. Multi-account out of the box — useful if Jebrim's flow ever spans tenants.
5. Read-only flag for safety dry-runs before turning on send/draft.
6. Documented Claude Code support.

**Alternative if 200 tools feels like too much surface: `@littlebearapps/outlook-assistant`.** 22 consolidated tools, Outlook-focused, explicit Claude Code support, device-code default, recent. Smaller bus-factor (16 stars) but actively maintained and architecturally cleaner. Worth a fallback slot.

**If the corporate tenant blocks new Entra app registrations** (which P2 will tell us), the escape hatch is `pnp/cli-microsoft365-mcp-server` — it re-uses an existing `m365 login` context, so the Entra-app problem is amortized into the existing PnP CLI app rather than requiring a fresh registration. PnP CLI is widely used in M365 admin shops and is generally pre-approved.

**If Niklavs's Outlook Desktop is the daily driver and he wants to avoid Azure entirely**: `Aanerud/outlook-desktop-mcp` is the no-Graph escape — read+write via the desktop client, no app reg, no OAuth, just whichever account is signed into Outlook. The constraint is "Outlook must be running" and "won't work from a VPS." For local interactive use that's fine.

## Gaps & open questions

- **Anthropic M365 connector in Claude Code.** Documentation is silent on whether the connector appears in Claude Code or is Claude.ai/Desktop-only. The architecture (Anthropic-hosted, dual Entra apps) reads as Claude.ai-side. Confirming this needs either a Claude Code test against an enabled tenant or an explicit statement from Anthropic — neither was findable in the public docs. *(Inferred, low-medium confidence.)*
- **TC Group's tenant policy.** Whether new Entra app registrations are allowed (and under which scopes) is the binary that decides between Softeria/littlebearapps (need fresh registration) vs PnP CLI (re-uses existing CLI app) vs Aanerud (no Graph at all). This is P2's domain.
- **MFA / conditional-access loops.** Device-code auth handles MFA but some tenants block device-code flows entirely via CA policy. Not surfaced for the candidate servers in this pass.
- **Last-commit dates vs star counts.** Several servers are listed as "active" based on recent releases, but I didn't sweep open-issues backlog or PR responsiveness — a 1-week-old release with 40 open issues is different from a 1-week-old release with 2. Real-use dogfooding will catch this faster than docs review.
- **The Microsoft Graph Enterprise MCP roadmap.** Currently scoped to Entra identity read-only; whether Microsoft plans to expand to Outlook mail/calendar (which would replace much of Tier 2/3) is not stated in the preview docs. Worth re-checking in 2–3 months.
- **License conflict at Aanerud.** AGPL-3.0 on the local-Outlook desktop MCP could matter if any of this gets bundled into something redistributed; for personal-assistant use it's fine.
