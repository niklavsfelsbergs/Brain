#!/usr/bin/env python3
"""sync_agents_md.py — generate the AGENTS.md mirror from the CLAUDE.md chain.

Why this exists (dev-brain §Y.1, the Codex external-audit triage):
    Claude Code reads CLAUDE.md and resolves its `@path` import directives, so a
    Claude session at brain root gets the full rulebook (root -> gielinor -> the
    meta/* chain). A non-Claude agent (Codex) reads AGENTS.md and composes
    instructions by directory-walk layering ONLY — it does NOT resolve `@import`
    (open feature request codex#17401). So an AGENTS.md that merely `@import`s, or
    points at, CLAUDE.md is dead text for Codex: it gets none of the rulebook and
    runs degraded. The fix is to make AGENTS.md carry the *flattened* content
    physically, and to keep it mechanically synced to the CLAUDE.md source so the
    two never diverge into hand-maintained copies.

What it does:
    For each CLAUDE.md in SOURCES, recursively inline every `@path` import
    (resolved relative to the importing file's directory) and write the flattened
    result to the sibling AGENTS.md, with a GENERATED banner. CLAUDE.md is the
    single source of truth; AGENTS.md is a build artifact. Deterministic and
    idempotent: same input -> byte-identical output. Stdlib-only.

Usage:
    py tools/sync_agents_md.py            # regenerate all AGENTS.md
    py tools/sync_agents_md.py --check    # exit 1 if any AGENTS.md is stale (writes nothing)

The pre-commit hook runs this and re-stages any changed AGENTS.md, so a commit
that touches a CLAUDE.md or meta/* file carries the regenerated mirror with it.
Pathspec note: a `git commit -- <pathspec>` only commits the named paths, so when
you commit a CLAUDE.md/meta change by pathspec, include the regenerated AGENTS.md
path(s) in the same pathspec.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Repo root = parent of this tools/ directory.
ROOT = Path(__file__).resolve().parent.parent

# Each entry: the CLAUDE.md source whose flattened content becomes the sibling
# AGENTS.md (same directory). Order is cosmetic.
SOURCES = [
    ROOT / "CLAUDE.md",
    ROOT / "gielinor" / "CLAUDE.md",
    ROOT / "developer-braindead" / "CLAUDE.md",
]

# A Claude Code import directive: a line that is exactly `@<path>` (no spaces in
# the path). This deliberately does NOT match `@mentions` or email-like text
# embedded in prose — only standalone import lines, which is how the chain is
# authored (CLAUDE.md:12, gielinor/CLAUDE.md:99-101).
IMPORT_RE = re.compile(r"^@(\S+)\s*$")


def flatten(path: Path, stack: tuple[Path, ...] = ()) -> str:
    """Return the text of `path` with every `@import` line replaced inline.

    Imports resolve relative to the importing file's own directory. `stack`
    guards against an import cycle.
    """
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(p.name for p in stack + (path,))
        raise ValueError(f"import cycle: {chain}")
    text = path.read_text(encoding="utf-8")
    out: list[str] = []
    for line in text.splitlines():
        m = IMPORT_RE.match(line)
        if not m:
            out.append(line)
            continue
        target = (path.parent / m.group(1)).resolve()
        rel = target.relative_to(ROOT).as_posix()
        if not target.exists():
            # Faithful-degradation: keep the directive visible rather than
            # silently dropping it, and flag it loudly so a broken chain surfaces.
            out.append(f"<!-- MISSING IMPORT: {rel} (source said `{line.strip()}`) -->")
            continue
        out.append(f"<!-- begin inlined import: {rel} -->")
        out.append(flatten(target, stack + (path,)))
        out.append(f"<!-- end inlined import: {rel} -->")
    return "\n".join(out)


def banner(source: Path) -> str:
    rel = source.relative_to(ROOT).as_posix()
    return (
        f"<!-- GENERATED from {rel} by tools/sync_agents_md.py — DO NOT EDIT.\n"
        f"     AGENTS.md is the non-Claude-agent (e.g. Codex) mirror of the CLAUDE.md\n"
        f"     rulebook. Codex composes by directory-walk layering and does NOT resolve\n"
        f"     @import, so the rulebook must be inlined physically here. Edit {rel}\n"
        f"     (or the files it imports) and re-run the sync — the pre-commit hook does\n"
        f"     this automatically. -->\n"
    )


def render(source: Path) -> str:
    return banner(source) + "\n" + flatten(source) + "\n"


def main(argv: list[str]) -> int:
    check = "--check" in argv[1:]
    stale: list[str] = []
    for source in SOURCES:
        if not source.exists():
            print(f"sync_agents_md: source missing: {source}", file=sys.stderr)
            return 2
        target = source.with_name("AGENTS.md")
        new = render(source)
        old = target.read_text(encoding="utf-8") if target.exists() else None
        rel = target.relative_to(ROOT).as_posix()
        if old == new:
            continue
        stale.append(rel)
        if not check:
            target.write_text(new, encoding="utf-8")
            print(f"sync_agents_md: wrote {rel}")
    if check and stale:
        print("sync_agents_md: STALE (re-run without --check): " + ", ".join(stale),
              file=sys.stderr)
        return 1
    if not check and not stale:
        print("sync_agents_md: all AGENTS.md already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
