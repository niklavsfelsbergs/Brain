# Read the routing manifest before proposing new docs

**Captured:** 2026-05-22 (S032)
**Status:** drafted; awaits alching review.
**Origin:** S032 bi-etl shipping-mart harvest, D1.

## The skill

When extending a structured doc system (any folder where multiple files cohabit and carry distinct purposes), read its routing manifest **before** proposing where new content lands. The manifest is usually called `_about.md`, `README.md`, or carries a routing-table section inline ("when to add new content, route it before adding").

Look specifically for:

- An **"if you're about to write" / "routing for new content"** section listing where each shape of content belongs.
- File-by-file audience and stability tags ("STABLE / LIVE", "audience: AI + analyst").
- Cross-references between files — they signal where the system expects content to flow.

## When this applies

- Adding documentation to an existing doc system (a multi-file reference layer, a docs site, a knowledge base, an agent's reference folder).
- Proposing a new file in a structured codebase before writing it.
- Extending any system where multiple files have differentiated roles you can't see at first glance.

## When it doesn't

- One-file projects. There's no routing to read.
- Fresh-canvas docs. If no convention exists yet, you're proposing one — different problem.

## What the failure looks like

S032 (verbatim trigger): I proposed a new `data-caveats.md` for the shipping-agent reference layer. Niklāvs approved. Mid-implementation, I read `reference/_about.md` and discovered it carried an explicit routing rule that split caveats across 4 existing files. The new file would have duplicated content and violated convention. Pivoting cost a turn and required re-validating the placement with Niklāvs.

The cost: a planning loop, mid-implementation surprise, and the user briefly questioning a decision they'd just approved.

## The fix shape

Before proposing a placement decision in a structured doc system:

1. **Glob for `_about.md`, `README.md`, `CONVENTIONS.md`** at the relevant level.
2. **Read it specifically for routing rules** — search for "routing," "where to add," "if you're about to write," "when to read," "convention."
3. **If a routing rule exists, route to it.** Don't propose new files until you've confirmed no existing file fits the role.
4. **If no routing rule exists, surface that** — "no convention found; here's where I'd propose putting it" — so the user knows the decision is fresh.

## Diagnostic

When tempted to propose a new file: ask "have I read the routing manifest?" If no, read first. If yes and no rule covers this, surface that explicitly. If yes and a rule exists, follow it.

## Related

- `inventory/shipping-agent-audit-resume.md` § Watch-outs — *"Resist new-file bias."*
- `gielinor/meta/layer-routing.md` — the brain's own routing rule, structurally identical pattern.
