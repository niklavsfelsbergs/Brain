# Outlook MCP — project state + server landscape (STALE-PRONE snapshot)

As of: 2026-05-23 — **flagged perishable**: the research itself rates its maturity numbers "churn weekly" and says re-check in 2–3 months; that window has passed. Re-research the landscape before acting. The project was parked — no Outlook MCP was ever installed (no outlook server in `.mcp.json` as of 2026-06-11).

- Durable taxonomy (four tiers): (1) first-party but narrow — Microsoft's Enterprise MCP is Entra-directory-only (no mail), Anthropic's M365 connector is **read-only** (no send/draft → fails the full-assistant brief); (2) community-broad Graph servers (softeria 200+ tools, PnP CLI wrapper); (3) Outlook-focused (littlebearapps, ryaker); (4) local-Outlook COM, no Graph (Aanerud).
- The 2026-05-23 first-pick was `softeria/ms-365-mcp-server` (most active, device-code default + HTTP/OAuth, read-only safety flag, documented Claude Code support). Treat as a hypothesis to re-verify, not a current recommendation.
- The binary that decides the install path is the tcgroup tenant policy (app registration + consent) — see [[2026-06-11-m365-graph-auth-for-personal-mcp]]; that gate was never tested.
- Open question that may obsolete the whole tier-2/3 layer: whether Microsoft expands its Enterprise MCP from Entra-identity to mail/calendar.

Source research: [[2026-05-23-outlook-mcp-landscape]] — full server-by-server comparison and sources there.
