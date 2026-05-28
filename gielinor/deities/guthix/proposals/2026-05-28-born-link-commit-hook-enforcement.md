# Proposal — note the born-link commit-hook enforcement in `meta/write-rules.md`

> **Provenance note (irregular).** Drafted by **Braindead** (dev-brain construction, 2026-05-28), not by Guthix at a bankstanding pass, at the principal's explicit request after the hook was built. Queued here for Guthix to **adopt + land at the next bankstanding** (or for the principal to land directly — `meta/` is user-only). Flagged because the normal discipline is Guthix-authored-during-bankstanding; redirect if you'd rather Guthix re-author it fresh.

## Observation

`meta/write-rules.md` → *Link & anchor conventions* (added in the §O.9 born-linked pass) tells authors to use full-stem `[[stem|ID]]` links and to wrap source anchors as links. It is **authoring discipline only** — no enforcement. The 2026-05-28 dev session measured the result on the live gielinor vault: **42% of nodes isolated, 27 phantom/ghost link targets**, and **3 new isolated nodes born during the session itself**. Documentation alone does not hold; the graph re-rots as new entries land.

A commit-time enforcement hook was built + installed to close exactly this gap. The convention doc should *say so*, so future authors/agents know the rule is enforced (and where).

## Proposed change

In `gielinor/meta/write-rules.md`, append one line to the *Link & anchor conventions (Obsidian-resolvable)* section:

> **Enforced at commit (2026-05-28).** A git pre-commit hook (`developer-braindead/bank/research/born-link-lint.py`, installed to `.git/hooks/pre-commit`) checks staged gielinor `.md`: it **auto-wraps** resolvable bare `[[ID]]` and unwrapped prose/anchor IDs to full-stem links (and re-stages them), and **blocks the commit** on a malformed `[[…md]]` / `[[../path]]` wikilink with a fix-list. This is the enforcement layer behind the conventions above — they are no longer discipline-only.

No other file changes. (The hook + linter already exist; this is documentation catching up to enforcement.)

## Reasoning

The brain's stated philosophy is gates for the load-bearing invariants, discipline for the rest — but born-linking proved to be load-bearing for the whole Obsidian/RAG retrieval substrate (§N depends on a non-rotting graph) and discipline was visibly failing. Recording the enforcement in `write-rules.md` keeps the doc honest (the "this is guidance not a hook" framing elsewhere in the file is now false for this convention) and tells the next author the wrap is automatic.

## Scope of impact

One sentence added to one `meta/` file. Affects every actor that authors gielinor notes (informational — the hook already acts on them). No migration; no backfill.

## Alternatives considered

- **Leave the doc as-is** — rejected: the file elsewhere distinguishes hook-enforced from discipline-only lines, so silence here is misleading now.
- **Braindead edits `meta/` directly** — rejected: `meta/` is user-only; the dev-brain decision that would justify it ([[D-032_godly_proposal_flow_and_code_bearing_seam|D-032]], dev brain) won't resolve in this vault. Routed through this proposal instead, per that decision.

## Risk if landed wrong

Negligible — it's a descriptive sentence. The only failure mode is the path/filename drifting if the hook is later moved or renamed; keep the reference current (or make it path-agnostic: "a git pre-commit hook").
