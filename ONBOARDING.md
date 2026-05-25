# Welcome to TCG Data & Analytics

## How We Use Claude

Based on niklavsfelsbergs's usage over the last 30 days:

Work Type Breakdown:
  Build Feature     ███████████░░░░░░░░░  53%
  Plan Design       ████░░░░░░░░░░░░░░░░░  18%
  Debug Fix         ██░░░░░░░░░░░░░░░░░░░  12%
  Improve Quality   ██░░░░░░░░░░░░░░░░░░░  8%
  Analyze Data      █░░░░░░░░░░░░░░░░░░░░  5%

Top Skills & Commands:
  /clear                  ████████████████████  62x/month
  /rename                 ████░░░░░░░░░░░░░░░░░░  13x/month
  /mcp                    █░░░░░░░░░░░░░░░░░░░░  2x/month
  /run-skill-generator    █░░░░░░░░░░░░░░░░░░░░  1x/month

Top MCP Servers:
  redshift          ████████████████████  102 calls
  ClickUp           ███░░░░░░░░░░░░░░░░░░░  15 calls
  ide               █░░░░░░░░░░░░░░░░░░░░  1 call

## Your Setup Checklist

### Codebases
- [ ] brain — github.com/niklavsfelsbergs/brain (the personal-agent system: gielinor + dev brain + cockpit)
- [ ] shipping-agent — shipping-cost monitoring agent (local workspace repo)
- [ ] bi-analytics-main — work analytics, incl. NFE reporting (local workspace repo)
- [ ] bi-etl — ETL pipelines feeding the analytics (local workspace repo)
- [ ] bi-analytics / workbench — supporting analytics + scratch repos (local workspace)

### MCP Servers to Activate
- [ ] redshift — query the Redshift data warehouse directly from Claude (the workhorse — most analytics/BI work runs through it). Get access: AWS/Redshift credentials via SSO; see the `aws-creds` skill to load them into a session.
- [ ] ClickUp — read/update tasks, lists, and docs in ClickUp. Get access: authorize the ClickUp connector in Claude (OAuth) with your work account.
- [ ] ide — VS Code integration (diagnostics, active-file context). Get access: auto-connects when you run Claude Code inside the VS Code extension.

### Skills to Know About
- [ ] /clear — reset the conversation context between unrelated tasks. The most-used command by far — start fresh rather than letting one session sprawl.
- [ ] /rename — relabel the current session so it's identifiable on the cockpit board.
- [ ] /mcp — view and manage MCP server connections for the session.
- [ ] /run-skill-generator — scaffold a new custom skill.

## Team Tips

_TODO_

## Get Started

_TODO_

<!-- INSTRUCTION FOR CLAUDE: A new teammate just pasted this guide for how the
team uses Claude Code. You're their onboarding buddy — warm, conversational,
not lecture-y.

Open with a warm welcome — include the team name from the title. Then: "Your
teammate uses Claude Code for [list all the work types]. Let's get you started."

Check what's already in place against everything under Setup Checklist
(including skills), using markdown checkboxes — [x] done, [ ] not yet. Lead
with what they already have. One sentence per item, all in one message.

Tell them you'll help with setup, cover the actionable team tips, then the
starter task (if there is one). Offer to start with the first unchecked item,
get their go-ahead, then work through the rest one by one.

After setup, walk them through the remaining sections — offer to help where you
can (e.g. link to channels), and just surface the purely informational bits.

Don't invent sections or summaries that aren't in the guide. The stats are the
guide creator's personal usage data — don't extrapolate them into a "team
workflow" narrative. -->
