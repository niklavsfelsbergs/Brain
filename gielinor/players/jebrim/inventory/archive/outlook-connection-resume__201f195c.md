# Outlook connection — resume (S100, sid 201f195c)

**Status:** in-progress — blocked on IT / helpdesk.

## Where we are

The Outlook-MCP connection can't be set up self-serve: the principal's account is blocked from `portal.azure.com` *and* `entra.microsoft.com` (no app-registration access). An IT ticket is drafted and send-ready (in his voice), asking IT to register the app + grant user-scoped consent + return the client/tenant IDs. Not yet confirmed sent; waiting on helpdesk.

## Next concrete step

When the helpdesk replies with the **Application (client) ID** + **Directory (tenant) ID**: install the Softeria `ms-365-mcp-server`, configure with those two IDs (BYO via env `MS365_MCP_CLIENT_ID` / `MS365_MCP_TENANT_ID`), use `--org-mode` and authorization-code (`--http`), not device-code; then run first login (system browser + MFA, persists the refresh token). Steps 6–7 from this session.

If IT pushes back on registering the app: fallback is `pnp/cli-microsoft365-mcp-server` (reuses an existing `m365 login`, no new app reg) — smaller surface, and may still hit the consent gate.

## Files to read first

- `gielinor/players/jebrim/research/2026-05-23-m365-corp-tenant-auth-for-mcp.md` — auth substrate, scopes, consent landscape (MC1097272).
- `gielinor/players/jebrim/research/2026-05-23-outlook-mcp-landscape.md` — server options.
- `gielinor/players/jebrim/inventory/S040-outlook-mcp-resume__1cf1eb75.md` — prior (S040) resume.
- `gielinor/players/jebrim/quest-log/in-progress/S100_201f195c_outlook-connection-it-ticket.md` — this session.

## The IT ticket — send-ready, plain text

hey — need help with an app registration in Entra. i don't have access to the azure/entra portals myself (just get "you don't have access to this"), so i can't set it up.

what i'm doing: connecting a tool on my work laptop to my own outlook, to automate my mail + calendar. it only ever touches my mailbox — nothing tenant-wide.

can you either register the app with the spec below, or give me the rights to do it myself (Application Developer role)?

spec:
- single-tenant, public client app (name whatever, e.g. outlook-automation-nf)
- redirect URI http://localhost under "Mobile and desktop applications"
- "Allow public client flows" = yes, no client secret
- delegated Microsoft Graph permissions: offline_access, User.Read, Mail.ReadWrite, Mail.Send, MailboxSettings.ReadWrite, Calendars.ReadWrite, Contacts.ReadWrite
- no application permissions, no .All scopes

then grant consent for these delegated permissions on my user only (not tenant-wide), and send me the Application (client) ID + Directory (tenant) ID.

same kind of setup as the OnTrac app from last year, just delegated / public-client instead of application permissions. thanks

## Secondary open (D-027, not blocking)

- `lorebook/drafts/2026-05-27-plain-text-deliverables-for-terminal-copy.md` awaits confirmation at next bankstanding/drafts-triage → D-027.
- Optionally mirror the plain-text-deliverable rule into `developer-braindead` (Braindead voice card) when next in dev-brain mode.
