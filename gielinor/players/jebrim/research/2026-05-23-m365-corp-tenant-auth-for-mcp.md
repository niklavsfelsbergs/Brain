# M365 corporate-tenant auth for an Outlook MCP server

## Question

For a personal-use MCP server pulling full mail + calendar (read, send, search) from a corporate Microsoft 365 tenant (tcgroup.com), what's the right auth substrate? Specifically:

1. Which Microsoft Graph OAuth flow does an interactive personal-assistant use (not a daemon)?
2. What Azure AD app registration shape is required — tenancy, redirect URI, exact delegated scopes?
3. Which of those scopes require tenant admin consent at a typical corporate M365 tenant?
4. What Conditional Access / MFA / token-lifetime behaviour bites a personal assistant running against a corporate tenant?
5. Practical recipe to stand up an app registration suitable for an MCP server.

## Date of research

2026-05-23.

## Confidence

High on the auth-flow choice, scope inventory, and admin-consent flags (all anchored to Microsoft Learn primary docs published 2024-2026 and to Microsoft's own published rollout MC1097272). Medium on tcgroup.com-specific outcomes — those depend on tenant-admin choices that can only be confirmed by attempting the app registration and the consent flow. The structural shape ("what you'll see" / "what you'll need IT for") is high-confidence; the specific tcgroup configuration is one experiment away.

## Sources

- **Microsoft Learn — Authentication and authorization basics (Microsoft Graph)** — <https://learn.microsoft.com/en-us/graph/auth/auth-concepts> — The canonical Graph auth-concept page. Load-bearing for the delegated-vs-application-permission split and for "public clients don't need a client secret."
- **Microsoft Learn — Authentication flow support in MSAL** — <https://learn.microsoft.com/en-us/entra/identity-platform/msal-authentication-flows> — The matrix of which OAuth flow is recommended for which app type. Load-bearing for "authorization code with PKCE for desktop" and the warnings on ROPC / implicit.
- **Microsoft Learn — Microsoft Graph permissions reference** — <https://learn.microsoft.com/en-us/graph/permissions-reference> — Per-scope admin-consent flags. Load-bearing for the scope-by-scope table below.
- **graphpermissions.merill.net — Mail.Send permission detail** — <https://graphpermissions.merill.net/permission/Mail.Send> — Confirms the delegated Mail.Send "AdminConsentRequired = No" field from Microsoft's permission metadata. Used as the corroborator to Microsoft Learn.
- **Microsoft Learn — Overview of user and admin consent** — <https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/user-admin-consent-overview> — Explains the three built-in user-consent policies (disabled / verified-publishers-only / all-apps) and the admin-consent workflow path.
- **AppGov Score blog — MC1097272 explainer** — <https://www.appgovscore.com/blog/microsoft-disables-user-consent-by-default-are-you-ready-for-mc1097272> — Microsoft Message Center notice 1097272 (rolled out mid-July through August 2025). The reason "user consent" probably no longer works at most tenants by default.
- **Microsoft Learn — Configurable token lifetimes** — <https://learn.microsoft.com/en-us/entra/identity-platform/configurable-token-lifetimes> — Source for access-token (60-90 min, up to 24-28h with CAE) and refresh-token (90-day inactivity, otherwise "until-revoked") lifetimes.
- **Microsoft Learn — Block authentication flows with Conditional Access** — <https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-authentication-flows> — Confirms that device-code flow can be (and increasingly *is*) blocked by tenant CA policy.
- **Microsoft Threat Intelligence — STORM-2372 device-code phishing campaign / Microsoft-managed CA rollout (Feb-May 2025)** — surfaced via the Conditional Access docs above. Load-bearing for "device code flow is now widely blocked at corporate tenants by default."
- **Microsoft Learn — Register an application with the Microsoft identity platform** — <https://learn.microsoft.com/en-us/graph/auth-register-app-v2> — Step-by-step shape of the app registration (account types, redirect URIs, when a secret is and isn't needed).
- **Microsoft Learn — Default user permissions (Entra ID)** — <https://learn.microsoft.com/en-us/entra/fundamentals/users-default-permissions> — Confirms "Users can register applications" defaults to **Yes** at tenant level, but admins can flip it off; tcgroup.com's actual setting is unknown until attempted.
- **softeria/ms-365-mcp-server (GitHub)** — <https://github.com/softeria/ms-365-mcp-server> — A real Outlook-targeting MCP server. Useful as the reference for "what does an MCP server in this space actually request": default device code flow, ships a default client ID, supports BYO client ID via env var, supports `--org-mode` for work accounts.

## Findings

### 1. Auth-flow taxonomy and the right pick

Microsoft Graph supports four broad auth shapes (per Microsoft Learn auth-concepts and MSAL flow matrix):

| Flow | Acts as | Designed for | Fit for personal Outlook MCP |
|---|---|---|---|
| **Authorization code + PKCE** | signed-in user (delegated) | desktop, mobile, SPA, web | **Yes — the recommended default** |
| **Device code** | signed-in user (delegated) | input-constrained devices, CLIs | Works, but **increasingly blocked by corporate CA**; see §4 |
| **Client credentials** | the app itself (application permissions) | daemons / server-to-server | No — wrong shape for personal assistant; full mailbox-tenant scope; requires admin |
| **On-behalf-of (OBO)** | upstream web API → downstream API | middle-tier web APIs | No — wrong topology; OBO is for a service that itself was called by a user-authenticated client |
| **ROPC / implicit** | — | — | No. MS docs: *"Do not use this flow"* / *"It's no longer recommended"* |

Microsoft Learn explicitly lists authorization-code-with-PKCE as the supported shape for **Desktop / Mobile / SPA / Web** apps, and the MSAL flow doc says PKCE is *required* for SPAs and *supported* for native apps (<https://learn.microsoft.com/en-us/entra/identity-platform/msal-authentication-flows>). Device-code is documented as *"available only for public client applications"* and *"input-constrained devices like smart TVs, IoT devices, and printers."*

Why this matters: an MCP server running on a laptop *is* a public-client desktop app from Entra's perspective. The signed-in user (Niklavs) opens a browser, authenticates against tcgroup's IdP including MFA and any Conditional Access prompts, the local listener catches the redirect with the auth code, MSAL exchanges it for tokens. The MCP server stores the **refresh token** locally and uses it to mint new access tokens silently until it's revoked or expires per §4.

**Pick: authorization code with PKCE on a `http://localhost` loopback redirect.** Device-code flow is the historical answer for headless CLIs and is what tools like `mgc` (Microsoft Graph CLI) default to, but at a corporate tenant in 2026 it's likely to be blocked at the CA layer — see §4.

### 2. Azure AD app-registration shape

**Single-tenant vs multi-tenant.**

- For a personal assistant against *only* tcgroup.com → **single-tenant** ("Accounts in this organizational directory only"). Per the app-registration doc (<https://learn.microsoft.com/en-us/graph/auth-register-app-v2>): *"Select this option if you're building an application for use only by users (or guests) in your tenant. Often called a line-of-business (LOB) application."* This is the right shape.
- Multi-tenant only matters if the same app registration would also serve other tenants (e.g., a personal Outlook.com account in parallel). Out of scope per brief.

**Platform / redirect URI.**

- Under app registration → **Authentication** → **Add a platform** → **Mobile and desktop applications**.
- Recommended redirect URIs (verbatim from MS Learn):
  - *"For desktop applications using embedded browser, we recommend `https://login.microsoftonline.com/common/oauth2/nativeclient`"*
  - *"For desktop applications using system browser, we recommend `http://localhost`"*
- MCP-server-shaped tools that pop the user's real browser want `http://localhost` (often `http://localhost:<port>` with a port the MCP server binds for the redirect listener). The Microsoft Q&A confirms public-client redirect URIs must be under "Mobile and desktop applications" — putting them under "Web" makes the platform expect a client_secret and breaks public-client auth (Q&A: AADSTS700025 returned when a public client sends a secret).
- **No client secret.** Per <https://learn.microsoft.com/en-us/graph/auth/auth-concepts>: *"This property is only required for confidential client applications; it isn't required for public clients like native, mobile, and single page applications."*

**API permissions — delegated, not application.**

| Scope | Type | Admin consent required (Microsoft default) | What it grants |
|---|---|---|---|
| `User.Read` | Delegated | No | Sign-in + read user profile. Implicit baseline. |
| `offline_access` | Delegated | No | Issue a **refresh token**. Without this, you'll re-auth every ~75 min. **Essential.** |
| `Mail.Read` | Delegated | No | Read user mail. |
| `Mail.ReadWrite` | Delegated | No | Full mailbox read + write (folders, flags, drafts, delete). Superset of `Mail.Read`. |
| `Mail.Send` | Delegated | **No** | Send mail as the signed-in user. ([Microsoft Learn](https://learn.microsoft.com/en-us/graph/permissions-reference), confirmed at [graphpermissions.merill.net](https://graphpermissions.merill.net/permission/Mail.Send): *"AdminConsentRequired = No"*.) |
| `MailboxSettings.Read` | Delegated | No | Automatic-replies, time zone, working hours. Often needed by an assistant. |
| `MailboxSettings.ReadWrite` | Delegated | No | Same + write (e.g., set auto-reply). |
| `Calendars.Read` | Delegated | No | Read user calendars. |
| `Calendars.ReadWrite` | Delegated | No | Full calendar — read + create + accept/decline. |
| `Contacts.Read` | Delegated | No | Read user contacts (helpful for resolving recipients). |
| `Contacts.ReadWrite` | Delegated | No | Read + write contacts. |
| *(Optional)* `Mail.Read.Shared`, `Mail.Send.Shared` | Delegated | No | Access shared / delegate mailboxes (only if a shared mailbox is in play; otherwise omit). |

**All scopes above are delegated and Microsoft-flagged "no admin consent required"** in their default catalog state — meaning *Microsoft's* baseline is "user may consent." The actual gate is the tenant's user-consent setting, which is the next section.

What you do **not** want: any `.All` variants (`Mail.Read.All`, `Calendars.ReadWrite.All`) or **application** permissions. Those grant the app access to *every* mailbox in the tenant, are admin-consent-only, and a corporate admin will (correctly) refuse them for a personal-use app.

### 3. Admin-consent landscape — the load-bearing constraint

This is the section where the architecture meets the politics.

**Microsoft's per-permission flag says all the chosen scopes are "no admin consent required."** That historically meant: user goes to sign-in page, sees the consent prompt listing the scopes, clicks "Accept," and the app gets a token. No admin involvement.

**That's no longer the default at most tenants as of late 2025.** Per Microsoft Message Center notice **MC1097272** (covered at <https://www.appgovscore.com/blog/microsoft-disables-user-consent-by-default-are-you-ready-for-mc1097272>), Microsoft started flipping tenants from "Allow user consent for apps" to **"Do not allow user consent"** for third-party applications beginning **mid-July 2025**, completing the rollout by August 2025. Quote: *"Non-privileged user accounts can no longer be used to grant consent to third party applications."* Exception: *"Organizations who have applied custom user consent settings through custom application consent policies will not be affected by this change."*

In effect, the per-permission admin-consent flag is now overridden by a tenant-level switch for any unverified third-party app. Three configured states are possible at any given tenant (Microsoft Learn — user-admin-consent-overview):

1. **User consent disabled** — only admins can grant consent. **This is now the Microsoft default.**
2. **User consent allowed only for verified publishers + low-impact permissions** (admin picks which scopes count as "low impact" via permission classifications).
3. **User consent allowed for all apps** (the pre-MC1097272 historical default — increasingly rare at enterprise tenants).

**Realistic path for a non-admin user at a corporate tenant like tcgroup.com.** Four scenarios, sorted best→worst:

| Scenario | What you do | Outcome |
|---|---|---|
| **A. User-consent for all apps is still enabled** | Register your own single-tenant app, configure scopes, sign in. Consent prompt appears, you accept. | Works end-to-end alone. Increasingly unlikely post-MC1097272. |
| **B. User-consent restricted to verified publishers + low-impact perms** | If your scopes (Mail.ReadWrite, Mail.Send, Calendars.ReadWrite) are classified by IT as "low-impact" you can self-consent. If they're not classified or are classed as anything else, you get blocked. | Maybe works. Mail.Send is rarely classed as low-impact. Likely partial / probable block. |
| **C. User-consent disabled but admin-consent workflow enabled** | You hit the sign-in, get an *"Approval required"* page (Microsoft Learn — user-admin-consent-overview), type a justification, IT receives a ticket and approves or denies the *specific* app+scopes for *you*. | Works after one IT ticket. The cleanest realistic path at most enterprises. |
| **D. User-consent disabled, admin-consent workflow disabled** | Direct ask to IT to grant tenant-wide admin consent (or single-user consent via Graph PowerShell `Grant-MgUserOauth2PermissionGrant`-shaped flow). | Requires IT cooperation outside the in-product flow. Slowest but doable. |

**Worth knowing.** Microsoft Learn's user-admin-consent-overview lists a less-known third option for sympathetic admins: *"Instead of granting consent for an entire organization, an admin can also use the Microsoft Graph API to grant consent to delegated permissions on behalf of a single user."* — i.e., IT can consent the app on Niklavs' behalf only, scoped to just his mailbox, without exposing the app to the rest of tcgroup. This is the smallest-blast-radius ask. If you have to go to IT (scenarios C/D), this is the framing — *"grant consent for delegated permissions on my user only, not tenant-wide."*

**A separate but parallel gate: "Users can register applications."** Default is **Yes** (Microsoft Learn — default user permissions: *"By default in Microsoft Entra ID, all users can register applications and manage all aspects of applications they create"*) but admins can flip this to **No** — at which point even creating the app registration requires the **Application Developer** role or higher. Don't know the tcgroup setting until you try; test by going to <https://entra.microsoft.com> → App registrations → New registration. If the button is disabled, the consent path doesn't matter yet — you need IT to either flip the setting or grant you Application Developer.

### 4. Conditional Access, MFA, and token-lifetime gotchas

**Token lifetimes (defaults, since refresh-token lifetimes became non-configurable on 2021-01-30 per Microsoft Learn):**

| Token | Default | Notes |
|---|---|---|
| Access token | **60–90 minutes** (75 min average), variable per client/resource/CA-policy | *"When both the client and the resource support Continuous Access Evaluation (CAE), the token lifetime may be automatically extended to 24-28 hours."* (Microsoft Learn — configurable-token-lifetimes) |
| Refresh token | **Until-revoked**, with a **90-day inactivity** ceiling | Inactivity counter resets on each successful use. *"Refresh and session token lifetimes are no longer configurable through token lifetime policies."* (Microsoft Learn — configurable-token-lifetimes) |
| MFA session | Tenant CA-defined "Sign-in frequency" (commonly 1 hour to 90 days) | When sign-in frequency is set, **refresh tokens get re-prompted for MFA at that cadence** even if technically valid (Microsoft Learn — concept-session-lifetime). |

**Practical implication.** Once the MCP server has its first refresh token and CA "sign-in frequency" isn't set aggressively, it can mint new access tokens silently for months. The first auth is the painful one; steady state is silent until tcgroup's IT changes a CA policy, you change your password, or 90 days of agent-idle pass. **The MCP server should persist the refresh token to disk** (encrypted at rest) and use MSAL's silent-acquire pattern before falling back to interactive.

**Conditional Access traps that commonly bite a personal-assistant app on a corporate tenant:**

1. **Device-code flow is now widely blocked by default.** Per <https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-authentication-flows>: as of Feb-May 2025 Microsoft began rolling out a *Microsoft-managed* Conditional Access policy that blocks device-code flow for tenants that aren't actively using it. Triggered by the STORM-2372 device-code-phishing campaign (Microsoft Threat Intelligence, Feb 2025). Quote: *"Device code flow is rarely used by customers, but is frequently used by attackers."* → **Don't design the MCP around device code; use authorization code + PKCE.**

2. **MFA on every fresh device.** First auth from the MCP server's machine will trigger the tenant's MFA flow (Authenticator app, FIDO key, etc.) — fine, this is just the normal sign-in.

3. **Sign-in frequency / "session token lifetime"** policies. If tcgroup sets sign-in frequency to e.g. 12 hours, the MCP will need to re-prompt the user every 12h regardless of refresh token validity. Symptom: the assistant works fine until lunch, then asks Niklavs to re-auth. Knowable only by attempting.

4. **Compliant-device / Hybrid-Entra-Joined device requirement.** Common at corporates. If CA requires "device must be marked compliant" and the laptop running the MCP isn't Intune-managed or domain-joined, the auth fails at the CA layer with an error that does *not* look like a consent error. Symptom: AADSTS53000-ish errors after the user has already consented. Mitigation: run the MCP on the corporate-managed laptop, not a personal device.

5. **Location-based / IP-based blocks.** Less common for the user's own work mailbox, but if Niklavs runs the MCP from a personal cloud VPS, that IP may fail CA. → Run the MCP locally on the corporate-issued machine.

6. **Continuous Access Evaluation (CAE) revocation.** Quote (Microsoft Learn): *"These long-lived tokens will be revoked in near real time in response to critical events such as account disablement and password changes."* — i.e., changing your tcgroup password kills all refresh tokens and forces re-auth. Expected behaviour; not a defect.

### 5. Practical recipe

Assuming "Users can register applications" is still on at tcgroup (the structural default; verify in 30 seconds at <https://entra.microsoft.com>) and you intend to write your own app registration:

1. **Register the app.** Microsoft Entra admin center → **Identity** → **Applications** → **App registrations** → **New registration**.
   - Name: e.g., `jebrim-outlook-mcp`.
   - Supported account types: **"Accounts in this organizational directory only"** (single-tenant, tcgroup).
   - Redirect URI: leave blank for now, configure under Authentication.
   - Click **Register**. Copy the **Application (client) ID** and **Directory (tenant) ID** off the Overview pane.

2. **Configure the platform.** Manage → **Authentication** → **Add a platform** → **Mobile and desktop applications**.
   - Add custom redirect URI: `http://localhost:<port>` (pick a fixed port the MCP server will bind, e.g., `http://localhost:53682`). Optionally also add `https://login.microsoftonline.com/common/oauth2/nativeclient` as a fallback for embedded-browser flows.
   - Under *Advanced settings*, ensure **"Allow public client flows"** is set to **Yes** (this enables authorization-code-with-PKCE on a public client).
   - Save.

3. **Add the API permissions.** Manage → **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**. Tick:
   - `offline_access` (critical — without it, no refresh token)
   - `User.Read`
   - `Mail.ReadWrite`
   - `Mail.Send`
   - `MailboxSettings.ReadWrite`
   - `Calendars.ReadWrite`
   - `Contacts.ReadWrite`
   - *(optional)* `Mail.Read.Shared` / `Mail.Send.Shared` only if a shared mailbox is actually in scope
   - Click **Add permissions**.
   - Do **not** add Application permissions. Do **not** click "Grant admin consent for {tenant}" — you don't have that role and won't.

4. **Trigger consent.** Run the MCP server's `login` (or equivalent) command. It opens the system browser to `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize?...`, completes MFA, then either:
   - Shows the consent screen → click Accept → token lands, you're done.
   - Shows **"Approval required"** → submit justification → wait for IT → on approval, re-run the login command.
   - Shows a CA block → contact IT with the specific error code.

5. **Persist tokens.** The MCP server should store the refresh token encrypted (DPAPI on Windows, Keychain on macOS, libsecret on Linux). MSAL has built-in token-cache serialization for this; don't roll your own.

6. **Failure modes to wire up.** When the access token returns 401/403, refresh silently. When the refresh token returns `invalid_grant` (revoked, expired, password changed, CAE event), fall back to full interactive sign-in. Don't loop on a dead refresh token.

**If "Users can register applications" is off at tcgroup**, the recipe doesn't change — only the prerequisite does. Open an IT ticket asking for either (a) the **Application Developer** role on Niklavs' account, or (b) IT to register the app on his behalf with the scopes above and the public-client redirect URI. The cleanest single ask is *"register a single-tenant public-client app for me with delegated Graph scopes (list), and either grant my user consent or enable user consent for this app via the admin-consent workflow."*

**Reference MCP server worth borrowing from.** `softeria/ms-365-mcp-server` (Node, MIT) — ships a default client ID, supports BYO client ID via `MS365_MCP_CLIENT_ID` and `MS365_MCP_TENANT_ID` env vars, has `--org-mode` flag specifically for work/school accounts (without it, only personal-account features are exposed). Default flow is device-code; switch to its `--http` mode (authorization-code) for the corporate-tenant path. The README explicitly notes BYO Azure registration is *"recommended for production."* See <https://github.com/softeria/ms-365-mcp-server>.

## Gaps & open questions

1. **tcgroup-specific tenant settings.** The structural shape of the answer is known; the specific configuration at tcgroup is not. Three settings determine which scenario above applies: (a) "Users can register applications" Yes/No; (b) "User consent" policy (disabled / verified+low-impact / all-apps); (c) admin-consent workflow enabled/disabled. All three are 30-second checks once Niklavs is logged into the Entra admin center even as a non-admin (the registration page either lets you click "New registration" or doesn't; the consent prompt either appears or shows "Approval required").
2. **Conditional Access policies in force.** Sign-in frequency, device compliance, location, and risk-based policies at tcgroup are not visible to non-admins. The MCP works or doesn't on first attempt; CA failures need IT to surface.
3. **Whether tcgroup blocks the entire pattern.** Some highly regulated tenants block all non-vendor-vetted apps via app-management policy regardless of user/admin consent. Probability is low for a typical professional-services or tech firm; not zero. If MC1097272-class restrictions go further and tcgroup has explicitly whitelisted only specific app IDs, this path is blocked entirely and the answer becomes "use a vendor-published, verified-publisher MCP server that IT has already approved." *(Inferred — not directly anchored to a tcgroup-specific source.)*
4. **MFA + sign-in frequency cadence.** Until the first interactive sign-in is attempted, the practical "how often will Niklavs be re-prompted?" is unknown. Sources document the mechanism, not tcgroup's number.
5. **Whether tcgroup has already deployed the Microsoft-managed device-code-block CA policy.** Probably yes given the Feb-May 2025 rollout, but unconfirmed. Authorization code with PKCE sidesteps the question entirely — which is why that's the recommended pick.
