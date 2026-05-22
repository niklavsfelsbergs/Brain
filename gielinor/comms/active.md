# active.md — gielinor coordination channel

> Append-only log. Each player or Guthix session reads at respawn, posts an `OPEN` declaration, dialogues as needed, posts a `CLOSING` entry at session-close.
>
> See `_about.md` for the protocol and entry kinds.

---

[2026-05-22 — channel opened] braindead-4a888d50 SCAFFOLD
  Channel created in S043 (dev-brain). First live OPEN entry will land at the next gielinor respawn under the new ritual. Mirrors dev-brain's `developer-braindead/comms/active.md` shape.

[2026-05-23 00:25] guthix-ebd90fea OPEN
  Bankstanding B-002. Globals only — drafts/proposals across examine/, niksis8/, lorebook/, keepsake/; inbox triage; cross-player synthesis read. Not touching per-player houses. Live siblings noted: jebrim-a110d573, braindead-b070e9be, braindead-f9da453a — none in conflict with global write surface.

[2026-05-23 00:32] guthix-ebd90fea CLOSING
  B-002 done — promoted D-022 (meta/ rot follow-up) + D-023 (PowerShell UTF-8 rule). 9 meta/ line-edits left for principal hand (user-only). Jebrim flagged for next-cycle alching; Zezima still pre-operational. Trace in deities/guthix/quest-log/completed/B-002_*.

[2026-05-23 00:35] jebrim-1cf1eb75 OPEN
  S040 — Outlook MCP research. Spawning 2 penguins (P1 landscape, P2 M365 corp-tenant auth). External research only; touching jebrim/research/ + jebrim/quest-log/. No conflict with live siblings.

[2026-05-23] jebrim-1cf1eb75 UPDATE
  Adding sibling scope: Slack MCP implementation. Likely new SNNN once choices settle. Will touch brain/.mcp.json (currently holds redshift + orps); no conflict with live siblings.

[2026-05-23 01:10] jebrim-1cf1eb75 CLOSING
  S040 research wrapped. Both penguins returned, full source-anchored writeups in jebrim/research/. Decision parked at "self-serve check vs IT ticket" — principal will run the portal.azure.com three-step check later. Resume state in jebrim/inventory/S040-outlook-mcp-resume__1cf1eb75.md. Quest stays in-progress.

[2026-05-23 01:17] jebrim-1cf1eb75 UPDATE
  Slack MCP live — korotovsky server, cookie-auth, authed as niklavs.felsbergs @ The Customization Group. Read tools surfaced (channels_list, conversations_history, search_messages, ...). Posting still disabled by config. Voice rule recorded: any outbound Slack post must read in Niklavs' voice (he posts under his own account). Memory: feedback-slack-posts-in-niklavs-voice, reference-slack-mcp-tcg.

[2026-05-23] jebrim-1cf1eb75 UPDATE
  Outlook MCP (S040) re-parked. Principal opened it briefly post-Slack-install; got to portal.azure.com sign-in confusion (Windows-vs-browser session). Resume nudge appended to inventory/S040-outlook-mcp-resume__1cf1eb75.md. Quest stays in-progress.

[2026-05-23] jebrim-1cf1eb75 CLOSING
  Completed: Slack MCP live (S047 — korotovsky cookie-auth, authed as niklavs.felsbergs @ The Customization Group; read tools surfaced; posting disabled by config; voice rule pinned to memory). Voice cues + install gotchas captured in bank/drafts/notes/workflow/slack-mcp-install.md. Outlook MCP (S040) re-engaged briefly for recall.
  Leaving open: S040 still in-progress at portal.azure.com self-serve check Step 1 (sign-in pending). S047 proposed to move to completed; follow-ups parked (rotate leaked tokens, enable posting, graduate install pattern to skill).
