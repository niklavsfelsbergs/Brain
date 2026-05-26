# [[S033_2026-05-22_shipping-agent-audit|S033]] D1 — shims-and-import

**Role:** Jebrim dwarf, spawned by Jebrim-principal in [[S033_2026-05-22_shipping-agent-audit|S033]] shipping-agent audit (apply-fixes phase).
**Task:** Replace the 4 entry-shim files in `shipping-agent/` with short shims that `@`-import `how_to.md`.
**Status:** completed at [[S033_2026-05-22_shipping-agent-audit|S033]] close. No pending external actions.

## Pre-edit state (all 4 files read)

All four shims (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `GROK.md`) are 11 lines each, near-verbatim copies of one another. Only line 1 (the header parenthetical) and line 3 (the identity sentence) differ between them. Lines 5–11 are byte-identical across all four: a restatement of §0, §10, §7/§8/§11, and a conflict-tiebreaker pointing at `how_to.md`.

Crucially, the link to `how_to.md` is a **markdown link** (`[\`how_to.md\`](./how_to.md)`) — not a Claude Code `@./how_to.md` import. So Claude Code's auto-loader does not pull `how_to.md` into context at session start; the rulebook only lands if the agent voluntarily reads it. This is the hallucination root-cause hypothesis.

## Plan

For each of the 4 files, replace whole content with a 5-line shim:
- `# AI Assistant — Shipping Agent (<Name>)`
- blank
- `You're <Name>, working on the Shipping Data Mart agent. The rulebook below is authoritative — read it in full every session.`
- blank
- `@./how_to.md`

Identity line per file:
- `CLAUDE.md` → "You're Claude"
- `AGENTS.md` → "You're an AI assistant working on the Shipping Data Mart agent (this file is the entry point for Codex and any agent without its own named file)"
- `GEMINI.md` → "You're Gemini"
- `GROK.md` → "You're Grok"

## Action log

- [completed] Write `C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent\CLAUDE.md` — replaced 11-line shim with 5-line `@./how_to.md`-importing shim.
- [completed] Write `C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent\AGENTS.md` — same shape, Codex/generic identity line preserved verbatim from spec.
- [completed] Write `C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent\GEMINI.md` — same shape, Gemini identity.
- [completed] Write `C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent\GROK.md` — same shape, Grok identity.

## Anomalies

None. All four pre-edit files were exactly the structure the audit predicted (11 lines, identical body, markdown link instead of `@`-import). No surprises.

## Post-edit shape (all 4 files)

5 lines: `# AI Assistant — Shipping Agent (<Name>)` / blank / identity sentence ending with "read it in full every session." / blank / `@./how_to.md` on its own line at the bottom (no trailing prose). Claude Code's auto-loader keys on that exact syntax, so `how_to.md` will now land at session start without the agent having to voluntarily read it.

## Hand-off

Other dwarves working in parallel on different shipping-agent files (per principal's [[S033_2026-05-22_shipping-agent-audit|S033]] brief). I did not touch anything outside the 4 named files. Principal commits after synthesis.

