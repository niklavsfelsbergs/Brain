# S040 — Outlook MCP research, resume

**Quest:** `quest-log/in-progress/S040_1cf1eb75_outlook-mcp-research.md`
**Status:** Research done, decision parked.

## Where we are

Research complete. Two writeups:
- `research/2026-05-23-outlook-mcp-landscape.md` (P1 — server options)
- `research/2026-05-23-m365-corp-tenant-auth-for-mcp.md` (P2 — auth substrate)

**Recommended target:** Softeria `ms-365-mcp-server` with auth-code+PKCE, own Entra app reg, `--read-only` first session.

**Critical context discovered late:** existing Azure app at tcgroup (Oct 2025, ETL analyst, for OnTrac at `Desktop/AI-codebase/AI-raw-invoice-analyzers/AI-ontrac-raw-invoice-analyzer`) is **confidential client + application permissions** — wrong shape for MCP. Need a *separate* second app reg, public client + delegated permissions.

## Next concrete step

Self-serve test at https://portal.azure.com → Microsoft Entra ID → App registrations. Three-step check (see T6 in quest-log or end of last chat turn) tells us whether self-registration is allowed or IT ticket needed.

If blocked: send the ready-to-use ask to the same ETL analyst who did the OnTrac app — text drafted in last response.

## Required delegated Graph scopes (verbatim)

`offline_access`, `User.Read`, `Mail.ReadWrite`, `Mail.Send`, `MailboxSettings.ReadWrite`, `Calendars.ReadWrite`, `Contacts.ReadWrite`

## Escape hatch if Entra reg blocked entirely

`pnp/cli-microsoft365-mcp-server` — reuses existing `m365 login` CLI context, no new app reg needed. Smaller capability surface.

## Decisions parked

- Whether to draft `.mcp.json` config now or wait for client_id — principal said wait.

## Resume nudge (2026-05-23, end of session)

Re-engaged briefly after Slack MCP install finished. Principal asked for recall of Outlook research → walked the headline → proposed the 3-step self-serve check at `portal.azure.com`. Got blocked at "why do I have to sign in if I'm logged into desktop" (Windows session ≠ browser session — TCG device likely not Entra-joined, so no SSO to Edge). Parked again.

**Next time:** start at Step 1c — sign into `portal.azure.com` with TCG creds, find App registrations, check whether **+ New registration** button is clickable, greyed out, or page blocked. Three branches from there per the resume above.
