# S111 — shipping-agent sub-agent type

**Session:** braindead-a268b008 · **Opened:** 2026-05-27 (dev-brain via "lets develop gielinor", mid-conversation; OPEN posted)
**Closes:** [[S101_612683db_shipping-agent-access-split|S101]] open item 6 (the DEV-BRAIN handoff).

## Ask

Make the shipping agent a **first-class named sub-agent type** so Jebrim can call it as a distinct, cockpit-visible specialist instead of an ad-hoc dwarf briefed to behave like it. Three pieces: agent definition, cockpit rendering, write-boundary decision.

## Decision (this session)

- **Write boundary: dedicated hook** (principal picked over documented-globals, AskUserQuestion). A new `agent_type` inherits only the global guards (`block-confirmed-writes`, `block-deletes`); it does **not** inherit the dwarf/gnome/penguin fine-grained limits, and the agent carries Write/Edit/Bash for charts — so without a hook it could write anywhere in the brain except `confirmed/`. The hook keeps the type consistent with the other three and makes the boundary actually fire.
- **Brain-internal write surface = quest-log + inventory only** (penguin-style, no `bank/`). Mart findings reach `bank/` via *alching*, not by the agent's own write. Its real deliverables (charts/CSVs/SQL) live **outside the brain** (shipping-agent `workbench/` or the NFE folder), which no brain hook governs.
- **It's a "named specialist"** — a dwarf-like functional sub-agent hardened to one external system, with its own identity + tool surface + boundary. First of a generalizable pattern.

## Built

1. **Agent def** — `.claude/agents/shipping-agent.md`. Emulation brief: read `shipping-agent/how_to.md` (+ `reference/`/`skills/` on cue), query the live gold `shipping_mart` via the Redshift MCP (read-only), gold-contract default with the `CLAUDE.local.md`/upstream exception, deliverables outside the brain, quest-log trace inside, verify numbers, no sub-spawn, never headless. Tools: `Read, Glob, Grep, Edit, Write, Bash` + `mcp__redshift__{execute_sql,list_schemas,list_objects,get_object_details,explain_query}`.
2. **Cockpit rendering** — wired the kind end-to-end:
   - producer `developer-braindead/.claude/hooks/emit-event.py` — `ROLE_CONFIG["shipping-agent"]` (id_prefix `S`, `state-shipping-agents.json`, spawn/despawn events, speaker) + `SHIPPING_AGENTS_PATH`; refreshed the stale "adding a new kind" comment (the old switchboard `index.html` sprite path is archived — the live consumer is the cockpit board chip + backend/sidecar role-file lists).
   - `status-sidecar.py` — `SUBAGENT_STATE_PATHS += state-shipping-agents.json` (awaiting-crew state + manifest crew override).
   - `cockpit/backend.py` — `ROLE_FILES += shipping-agent` (so `_pending_subagents` surfaces it as a crew chip).
   - `cockpit/web/board.js` — per-kind class on the crew chip (`sub sub-<kind>`); the chip letter is `kind[0]` → **"S"**.
   - `cockpit/web/styles.css` — `--ship: #46c8d8` (cyan) + `.sub-shipping-agent` chip color/ring, distinct from the blue dwarf/gnome/penguin crew.
3. **Write boundary** — new `gielinor/.claude/hooks/shipping-agent-write-boundary.py` (gated on `agent_type == "shipping-agent"`, allows `quest-log/{in-progress,completed}` + `inventory/`, blocks the rest inside the brain, allows outside-brain paths). Registered in both `.claude/settings.json` (brain-root) and `gielinor/.claude/settings.json` (S085 redundancy pattern). `block-sub-spawn.py` `ROLE_PLURALS += shipping-agent` (defense-in-depth; unreachable backstop — the agent has no Task/Agent tool).
4. **Docs** — `gielinor/meta/modes.md` (new *Shipping-agent role* subsection + four-roles/inheritance/principle/Related updates). Updated the Jebrim skill draft `players/jebrim/spellbook/drafts/skills/calling-the-shipping-agent.md` step 2 ("until built → fall back to dwarf" was stale) — **flag for Jebrim's alching review**.

## Verified

- `py_compile` (emit-event, status-sidecar, backend, both new/edited hooks) + `node --check board.js` + both `settings.json` valid JSON.
- `cockpit/test_backend.py` 9/9.
- **Enforcement fires (synthetic payloads):** the boundary hook BLOCKS (rc=2) `bank/notes` + `examine/drafts` for `agent_type==shipping-agent`; ALLOWS (rc=0) `quest-log/in-progress`, `inventory`, and an NFE path outside the brain; is NOT gated for a dwarf payload; and a shipping-agent payload is NOT caught by the dwarf hook (each hook governs only its own type).
- **Routing:** `spawn_kind_from_tool_input` maps `subagent_type` "shipping-agent"/"Shipping-Agent" → `shipping-agent`, unknown → `dwarf`; `ROLE_CONFIG` carries id_prefix `S`, speaker `shipping-agent`.

## RUNTIME-UNVERIFIED (relaunch checklist)

- **Live Agent spawn** — a real `Agent(subagent_type: "shipping-agent")` populating `agent_type == "shipping-agent"` needs a **fresh session** to load the new `.claude/agents/` config (per the [[S106_cf03bfe1_self-eating-audit-and-d8-enforcement-fix|S106]] config-registration fact); this session predates the file. From a fresh session: spawn it, watch the boundary hook block a `bank/` write + allow a `quest-log/` write (the [[S110_144c0ca2_brain_full_audit|S110]] live-test pattern, now for the 4th type).
- **Cockpit chip** — relaunch the cockpit; a live shipping-agent spawn should render a cyan **"S"** crew chip on the spawning session's board row (title "shipping-agent"), distinct from a dwarf "D".

## Design note — dwarf → shipping-agent nesting (considered, declined)

Principal asked: *what if we allowed dwarves to spawn shipping-agents?* — i.e. relax guarantee #6 ("only the principal spawns") for this one leaf. **Decision: keep #6 as-is** (AskUserQuestion, 2026-05-27).

Reasoning on record so it isn't re-litigated:
- **Gating fact is technical first.** #6 holds via two layers — typed agents carry no `Agent`/`Task` tool (the real control) *and* `block-sub-spawn.py`. Whether Claude Code even *permits* sub-agent nesting at the platform level (if the tool were added) is **unverified** — would need an empirical check before any design.
- **Win is narrow.** Only helps a dwarf that discovers a mart-pull need *mid-task*; the principal usually knows upfront (parallel-sibling spawn) or eats a one-turn bounce-back. A dwarf hitting the Redshift MCP raw loses the shipping-agent's *methodology* — which argues for the principal spawning the specialist, not the dwarf.
- **Cost/depth fears don't bite** (shipping-agent is a leaf → depth bounded at 2; Task sub-agents are in-session/subscription, not the metered headless path) — so the case against is the **clean-guarantee** argument, not safety: carving #6 turns one line into a growing allow-matrix and fragments the spawn tree away from the principal.
- **Revisit trigger:** if real use shows dwarves frequently needing mart pulls mid-task and the bounce is costly, reconsider — a selective carve-out (dwarf→shipping-agent only) is feasible, pending the nesting verification. Per *don't-over-formalize-a-reachable-capability*: not now.

The shipped build already encodes this — `shipping-agent` is in `block-sub-spawn`'s `ROLE_PLURALS` and carries no `Agent`/`Task` tool, so it can neither spawn nor be spawned by a dwarf.

## Files

NEW: `.claude/agents/shipping-agent.md`, `gielinor/.claude/hooks/shipping-agent-write-boundary.py`, this quest-log.
M: `.claude/settings.json`, `gielinor/.claude/settings.json`, `gielinor/.claude/hooks/block-sub-spawn.py`, `developer-braindead/.claude/hooks/{emit-event.py,status-sidecar.py}`, `cockpit/backend.py`, `cockpit/web/{board.js,styles.css}`, `gielinor/meta/modes.md`, `gielinor/players/jebrim/spellbook/drafts/skills/calling-the-shipping-agent.md`, `developer-braindead/comms/active.md`.
