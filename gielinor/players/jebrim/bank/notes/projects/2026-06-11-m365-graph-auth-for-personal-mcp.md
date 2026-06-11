# M365 corporate-tenant auth for a personal MCP server (Graph mail/calendar)

As of: 2026-05-23 (auth fundamentals; durable — Microsoft identity mechanics, not ecosystem snapshot)

- Right flow for an interactive personal assistant on a corp tenant: **authorization code + PKCE** (delegated, public client, no secret). Device-code flow works in principle but is **widely CA-blocked at corporate tenants** since the Feb–May 2025 Microsoft-managed policy rollout (STORM-2372 device-code phishing response) — don't build on it.
- Scopes for full mail+calendar: `Mail.ReadWrite`, `Mail.Send`, `Calendars.ReadWrite`, `Contacts.ReadWrite`, `offline_access`, `User.Read` — **none require admin consent by Graph's own flags**, but tenant consent *policy* can still force "Approval required" (MC1097272, mid-2025: Microsoft disabled default user consent at most tenants).
- Three 30-second tenant checks decide the whole path (visible to a non-admin in the Entra portal): (a) "Users can register applications" Yes/No; (b) user-consent policy (disabled / verified-low-impact / all-apps); (c) admin-consent workflow on/off. tcgroup.com's actual settings were never tested — that experiment is the open gate.
- If app registration is blocked: the single clean IT ask is "register a single-tenant public-client app with these delegated scopes + grant consent." Escape hatches: PnP `cli-microsoft365-mcp-server` (reuses existing `m365 login` app), or local-Outlook COM servers (no Graph, no Entra at all).
- Token lifetimes: access 60–90 min (auto-refresh), refresh until-revoked with 90-day inactivity cap; store via MSAL token cache (DPAPI on Windows), fall back to interactive on `invalid_grant` — don't loop a dead refresh token.

Source research: [[2026-05-23-m365-corp-tenant-auth-for-mcp]] — full scope table, recipe, and sources there.
