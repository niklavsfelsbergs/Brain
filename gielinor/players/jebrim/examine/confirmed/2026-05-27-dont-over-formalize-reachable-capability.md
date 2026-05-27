# Don't over-formalize a capability that's already reachable

**Observation ([[S101_612683db_shipping-agent-access-split|S101]], 2026-05-27).** Designing how Jebrim would "call the shipping agent," I proposed standing up a subagent definition + a spellbook skill + a lorebook entry — formalization — for something already doable with the tools in hand (spawn a dwarf, point it at `how_to.md` + the Redshift MCP). Niklavs pushed back twice toward simplicity: *"do you really think its so complicated that we need to have a real session?"* I conceded I'd overbuilt.

**Rule.** When a capability is already reachable with current tools, default to *using* it; reserve formalization (agent definitions, skills, lorebook entries, dedicated build sessions) for after the ad-hoc form has actually proven clunky through use. Capture-after-stabilize, not scaffold-first — the brain's anti-ceremony culture applied to capability design, same bias as the bank/skill harvest discipline.

**Nuance that survived:** a skill (how/when to call) WAS warranted — but as a tight procedure to load, not as build ceremony. And a dedicated agent type for cockpit clarity is a real, principal-driven improvement — correctly routed to dev-brain, not built reflexively from a work session.
