# S100 — Outlook connection: IT-ticket dispatch + plain-text deliverable rule

**Player:** Jebrim · **Session:** 201f195c · **Opened:** 2026-05-27. Resume state in `inventory/outlook-connection-resume__201f195c.md`.

## What this session was

"Hey Jebrim, remind me what i need for the outlook connection." A recall of the [[S040_1cf1eb75_outlook-mcp-research|S040]] Outlook-MCP research that turned operational — the principal is blocked from the Azure/Entra portals, so we produced an IT ticket to unblock the app registration. A formatting snag spun off into a comms-protocol rule.

## Thread 1 — Outlook MCP connection (continues [[S040_1cf1eb75_outlook-mcp-research|S040]])

- Recalled the requirements from S040 research (`research/2026-05-23-m365-corp-tenant-auth-for-mcp.md` + the S040 inventory resume): own **single-tenant public-client** Entra app, authorization-code + PKCE, delegated Graph scopes (`offline_access, User.Read, Mail.ReadWrite, Mail.Send, MailboxSettings.ReadWrite, Calendars.ReadWrite, Contacts.ReadWrite`), consent gate (likely admin-approval per MC1097272).
- Principal hit **"You don't have access to this"** at `portal.azure.com` *and* `entra.microsoft.com` — all admin surfaces blocked for his standard account. Self-serve registration is not possible; it needs IT.
- Walked the full path in plain language: what app registration / delegated permissions / consent mean, why he's blocked, the IT-dependent steps 1–5, the laptop-side steps 6–7 (MCP install + first login).
- Drafted an **IT ticket in Niklavs' voice**, calibrated by pulling his Slack messages (lowercase, terse, direct, no greeting ceremony). Send-ready text is embedded in the inventory resume file.

**Pending external action:** principal sends the IT ticket → waiting on helpdesk for the Application (client) ID + Directory (tenant) ID. External + principal-owned; resolves next session.

## Thread 2 — Plain-text deliverables rule ([[D-027_plain-text-deliverables-for-terminal-copy|D-027]])

- Principal couldn't cleanly copy the ticket. I'd wrapped it first in a blockquote (`>` markers dragged into the selection), then a fenced code block (pasted into Outlook as monospace — "the block is not clean"). Both wrong.
- Diagnosed the real mechanism: terminal text copies cleanest when selected directly — **Shift+drag in Windows Terminal** bypasses the TUI's mouse capture and yields plain text. Markdown decoration fights the paste.
- Principal generalized it: he wants to copy *any* conversation text cleanly, not just marked deliverables.
- Under explicit "Lets update relevant docs" authorization:
  - Added a section to `meta/communication-protocol.md` — *Copyable deliverables — plain text, not code blocks*.
  - Wrote `lorebook/drafts/2026-05-27-plain-text-deliverables-for-terminal-copy.md` (proposed **D-027**).
  - Saved cross-conv memory `feedback_copyable_deliverables_plain_text.md` + MEMORY.md pointer.

## Decisions

- Outlook connection can't proceed self-serve (admin portals blocked) → IT-ticket path. Steps 6–7 (MCP install + first login) are ours once IT returns the two IDs.
- Prose deliverables the principal pastes elsewhere go as plain text, not code fences; fences reserved for literal code/commands/paths. (D-027, pending confirmation.)

## Harvest

- Question 5 (correction → learning): the copy-format miss produced [[D-027_plain-text-deliverables-for-terminal-copy|D-027]] + the memory. Process echo of `feedback_instrument_dont_reguess` (cycled through two wrong formats before diagnosing the real cause) — already covered by that memory; no new draft.
