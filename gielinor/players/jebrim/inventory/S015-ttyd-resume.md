# S015 resume — TTYD review and dry-run

**Status:** in-progress
**Quest file:** `players/jebrim/quest-log/in-progress/S015_2026-05-21_ttyd-review-and-dry-run.md`
**Demo:** 2026-05-22 — Shipping Data Mart with the shipping-agent as the TTYD showcase.

## Where we are

The "TTYD review" reframed mid-session into a **full revamp of the shipping-agent's setup**, driven by tomorrow's demo (a logistics manager will use the agent live). Two dogfood runs happened this session; the first failed (paranoid 5-question gating, jargon leaks, 2 min runtime); the second succeeded (Mode 1 direct answer with translated plain English). The §0 rewrite + restructure + safety perimeter all landed.

**What's in place for the demo:**

- **Restructure:** `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/` → `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/`. Generic TTYD-template moved to `NFE/projects/_TTYD-template/` (out of the way).
- **§0 Answering Questions** — three-mode structure (Direct / Decompose / Clarify) + seven cross-cutting rules + translation table + chat-default output mode. Replaced the original defensive seven-behavior draft after the first dogfood failed. Rule 7 (Coverage questions get a time slice and a source axis) added by principal mid-session.
- **§10 Scope and Safety** — agent operates inside `shipping-agent/` only; no walk-up, no external reads/writes/bash.
- **Single-perimeter credentials** — local `.env` in `shipping-agent/` with working creds. Python harness (`db.py`, `connect_redshift.py`) had its NFE/.env walk-up fallback ripped out — credentials only come from the local `.env`, no fallback.
- **`.claude/settings.json`** (checked-in) — allow rules for Read/Edit/Write/Glob/Grep/Bash/PowerShell inside the folder; deny rules for relative path traversal, sensitive locations (`~/.ssh`, `~/.aws`, `/etc`), and dangerous bash/PowerShell commands (cd outside, env enumeration, curl, ssh, git push/config). The over-broad `Read(/**)` / `Read(C:/**)` denies were attempted then rolled back — they blocked legitimate in-folder reads because Claude Code resolves paths to absolute before pattern-matching.
- **Four AI-config files** (CLAUDE.md / AGENTS.md / GEMINI.md / GROK.md) — slimmed to ~10 lines each, point at §0 + §10 explicitly.
- **`reference/tables.md` and `reference/sources.md`** — folded from NFE-side reference docs, TTYD-folder-self-contained.
- **Brain keepsake card** (Jebrim) — re-pathed to new shipping-agent location; mentions the credential setup.
- **NFE/CLAUDE.md** callout — updated to point at the new path.

**Demo readiness:** The harness needs one smoke test from inside the folder (`python connect_redshift.py`) to confirm the local `.env` loads cleanly. The second dogfood produced the right answer (~502K April packages, translated to plain English, sub-second response). Permission prompts on `dir` and `Get-Location; Get-ChildItem` surfaced and were patched into the allow list.

## Next concrete step

**Tomorrow (2026-05-22) — present the demo.** Two follow-ups owe attention before then:

1. **One smoke test of the harness** from inside `shipping-agent/`. Run `python connect_redshift.py` to confirm the seven-table row-count default returns. If it errors, the local `.env` copy or the credential name expectations didn't survive cleanly.
2. **`reference/coverage-audit.md` is referenced in §0 rule 7 but doesn't exist** — either write the file before demo (a quick coverage matrix of current cost/revenue % by source × month), or remove the reference from rule 7.

After the demo: run more of the proposed test questions (the 10+10 list in the S022 turn block of the quest log) to stress-test Mode 2 decompose, Mode 3 clarify, sanity-check, and facts-vs-guesses behaviors which haven't been live-tested yet.

## Files to read first

1. `gielinor/players/jebrim/quest-log/in-progress/S015_2026-05-21_ttyd-review-and-dry-run.md` — full turn log including S022 narrative.
2. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — §0 + §10 are the load-bearing sections.
3. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/.claude/settings.json` — the perimeter backstop.
4. Jebrim's keepsake routing card (auto-loads at respawn).

## Open meta-questions

- Whether bi-analytics-main needs a commit before tomorrow (the brain close commits only touch gielinor). Many uncommitted files in shipping-agent/ — `how_to.md`, `reference/`, `.claude/settings.json`, `db.py`, `connect_redshift.py`, `.gitignore`, AI-config files. Some are renames from the restructure; some are content changes.
- Whether `ship_mart_ro` (the broken read-only user) should be granted proper access post-demo so a future demo can use the original "scoped demo user" story.
- Whether `_TTYD-template/` should be archived further or kept as a sibling for future TTYD-style projects.

## Pending drafts

One examine draft surfaced at close (defensive-rules-create-paranoid-agents — see surface block in the S022 close summary).
