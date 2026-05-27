# S040 — Outlook MCP research

**Session:** S040
**SID8:** 1cf1eb75
**Player:** Jebrim
**Date opened:** 2026-05-23

## Ask

Principal: *"we need to research outlook mcp, I cant keep up with my emails"*

Scope confirmed via clarifying Q's:
- **Primary job:** Full assistant — read, draft, send, search, calendar
- **Account:** Work (tcgroup.com / M365)

## Plan

Two penguins, parallel, background:

- **P1 — Outlook MCP landscape.** What MCP servers exist for Outlook / Microsoft 365 / Exchange. Capability matrix (read / send / search / calendar). Maturity, maintenance, license, install shape (npm / uvx / Docker). Compatibility with Claude Code's MCP client.
- **P2 — M365 corporate tenant auth.** Azure AD app registration shape, Microsoft Graph API scopes needed for full-assistant scope, admin-consent gotchas at corporate tenants. Practical path for a non-admin user at tcgroup.com (delegated vs application permissions, conditional access, common blockers).

Both clusters independent — P1 maps the tool space, P2 maps the auth substrate. Synthesis weaves them into a setup recommendation.

## Turns

- **T1 (2026-05-23).** Principal opened session. Clarified scope. Spawning P1 + P2 in background.
- **T2 (2026-05-23).** P1 returned. Three viable candidates: Softeria `ms-365-mcp-server` (200+ tools, active, MIT, device-code default), littlebearapps `outlook-assistant` (22 consolidated tools, Claude Code first-class), pnp/cli-m365 escape hatch (reuses existing `m365 login` — no new app registration). Anthropic's hosted M365 connector is read-only; Microsoft's official MCP is Entra-directory only (no mail). P1 recommends Softeria first, `--read-only` for the first session. P2 still running — its findings determine whether Softeria/littlebearapps survive TC Group's CA + app-registration policy.
- **T3 (2026-05-23).** P2 returned. Critical constraint: device-code flow is **blocked at most corporate tenants** by Microsoft-managed CA policy post-STORM-2372 (rolled out Feb–May 2025). Auth-code + PKCE on a public-client app with `http://localhost:<port>` redirect is the required path. Softeria's `ms-365-mcp-server` qualifies — BYO client ID via `MS365_MCP_CLIENT_ID` / `MS365_MCP_TENANT_ID`, `--http` mode for auth-code, `--org-mode` for work accounts. Scopes list nailed down: `offline_access`, `User.Read`, `Mail.ReadWrite`, `Mail.Send`, `MailboxSettings.ReadWrite`, `Calendars.ReadWrite`, `Contacts.ReadWrite` (all delegated, all "no admin consent required" per MS catalog but gated by tenant-level user-consent switch — Microsoft Message Center MC1097272 flipped default to "do not allow user consent" mid-2025).
- **T4 (2026-05-23).** Synthesis delivered to principal. Recommendation: **Softeria `ms-365-mcp-server`** with auth-code+PKCE, own Entra app reg, scopes above, `--read-only` first session. Three-branch path on tcgroup IT policy: self-serve (best), admin-consent ticket scoped to single principal (most likely), full IT-registers-app ticket (worst). Escape hatch if Entra reg blocked entirely: pnp/cli-m365 server reuses existing `m365 login` context.
- **T5 (2026-05-23).** Principal pointed at `Desktop/AI-codebase/AI-raw-invoice-analyzers/AI-ontrac-raw-invoice-analyzer` — there's a prior Microsoft connection there. Reading confirms: ETL analyst at tcgroup provisioned an Azure App Registration in October 2025 (CLIENT_ID, CLIENT_SECRET, TENANT_ID). **Critically**, that app is a confidential client with application permissions (Graph client_credentials flow) — wrong shape for an MCP assistant which needs public-client + delegated permissions + auth-code+PKCE. The OnTrac project's own troubleshooting log notes IMAP failed because of this mismatch; status stalled at "manual CSV workaround." Implication: same IT relationship exists, but existing app cannot be reused as-is. Cleanest move = go back to the same ETL analyst with a precise second ask for a *separate* assistant app reg (delegated, public client). Much smaller relationship cost than first-time provisioning.
- **T6 (2026-05-23).** Principal asked whether self-registration possible. Drafted three-step self-serve check at portal.azure.com → Entra → App registrations: (1) reach App registrations blade, (2) attempt + New registration as public-client/native with `http://localhost` redirect, (3) add delegated Graph scopes and observe whether grant-status flips green (user consent allowed) or stays "Not granted" (admin consent needed). Each failure mode maps to a specific next step.
- **T7 (2026-05-23).** Principal parked the decision — "can't do it now." Resume state written to `inventory/S040-outlook-mcp-resume__1cf1eb75.md`. Quest stays in-progress; pick up at the self-serve check.
- **T8 (2026-05-23, post-Slack-install).** Principal asked for recall (*"wait yeah, what do you know about outlook mcp?"*). Walked the synthesis: landscape, recommendation (Softeria + auth-code-PKCE + own Entra app + read-only first), TCG-specific blockers (existing Oct 2025 app wrong shape; device-code blocked; user-consent disabled by default since Aug 2025), scope list, 3-step self-serve check. Re-proposed Step 1 walkthrough.
- **T9 (2026-05-23).** Hit Step 1c blocker — principal asked *"why cant i log in if i am logged in on my desktop"*. Explained Windows session ≠ browser session: SSO requires Entra-joined device + Edge/Chrome-with-extension; TCG laptop likely not Entra-enrolled so portal.azure.com asks for fresh sign-in. Suggested signing in once (caches for hours), checking Windows Settings → Accounts → Access work or school for SSO substrate. Re-parked.

## Pending external actions

None pending. Self-serve check at portal.azure.com is principal-side (browser sign-in + portal navigation), not an agent action.
