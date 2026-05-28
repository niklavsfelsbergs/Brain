#!/usr/bin/env python3
"""Born-link enforcement — commit-time fixer + linter for the gielinor vault.

Reuses obsidian-link-migrate.py's resolver/apply engine (imported by path).
Driven by the git pre-commit hook over the STAGED gielinor .md files:

  AUTO-FIX (in place): bare `[[ID]]` -> full-stem (resolvable + unambiguous) and
    unwrapped prose IDs -> `[[stem|ID]]`. Self-healing: the author writes `S117`
    and it becomes a link with zero effort. (This is the dominant rot — §O.9's
    anchor-not-wrapped case — turned automatic.)
  BLOCK (exit 1): malformed wikilinks -- `[[...md]]` (extension) or `[[../x]]` /
    `[[a/b]]` (path-style). Obsidian resolves by stem, so these never resolve;
    they bit us repeatedly (the gertrudes notes). They need a decision (which
    file did the author mean?), so they FAIL the commit with a list rather than
    being silently mangled.
  WARN (exit 0): other non-resolving `[[slug]]` -- a cross-brain dev ref (left
    dangling per §O.5) or an external memory-system slug. Informational only;
    high-precision blocking means we don't false-fail on legitimate dangles.

Scope = the same knowledge+quest surface prose-mode writes: excludes
inventory/archive/rejected/comms/experiments/last-alched and the user-only
meta/ + spellbook/rituals/ + convention docs.

This script is git-agnostic (takes an explicit --files list) so it is unit-
testable; the pre-commit shim computes the staged set and re-stages the wraps.

Usage:
  born-link-lint.py --vault <gielinor> --files a.md,b.md        # fix + lint
  born-link-lint.py --vault <gielinor> --files a.md --check     # lint only
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIGRATE = HERE / "obsidian-link-migrate.py"


def load_migrate():
    spec = importlib.util.spec_from_file_location("obsidian_link_migrate", MIGRATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = load_migrate()


def excluded(rel: str) -> bool:
    """Same skip set as prose-mode: volatile/operational + user-only/convention."""
    return bool(
        M.SKIP_SRC_RE.search("/" + rel)
        or M.BODY_RULEBOOK_RE.search(rel)
        or rel in M.PROSE_CONVENTION_DOCS
    )


def malformed_in(vault: Path, rel: str):
    """Yield (lineno, link_text, target) for BLOCK-worthy malformed wikilinks:
    a `.md` extension or any `/` (path-style, incl. `../`) in the link target."""
    p = vault / rel
    if not p.exists():
        return
    fenced = False
    for lineno, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if M.FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        code = M.inline_code_spans(line)
        for m in M.LINK_RE.finditer(line):
            if M.in_span(m.start(), code):
                continue
            target = m.group(1).split("|", 1)[0].split("#", 1)[0].strip()
            if not target:
                continue
            if target.lower().endswith(".md") or "/" in target:
                yield (lineno, m.group(0), target)


def run_migrate(vault: Path, mode: str, csv: str):
    """Invoke the migration engine for one mode, scoped to the staged files."""
    cmd = [sys.executable, str(MIGRATE), "--vault", str(vault),
           "--mode", mode, "--apply", "--files", csv]
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--files", required=True, help="comma-separated vault-relative .md paths")
    ap.add_argument("--check", action="store_true", help="lint only; do NOT auto-fix")
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    targets = [f.strip() for f in args.files.split(",") if f.strip().endswith(".md")]
    targets = [f for f in targets if not excluded(f)]
    if not targets:
        return 0  # nothing in scope -> let the commit through

    csv = ",".join(targets)

    if not args.check:
        before = {f: (vault / f).read_text(encoding="utf-8", errors="replace")
                  if (vault / f).exists() else None for f in targets}
        for mode in ("links", "prose"):
            r = run_migrate(vault, mode, csv)
            if r.returncode != 0:
                sys.stderr.write(f"[born-link] migrate {mode} failed:\n{r.stderr}\n")
                return 1
        fixed = [f for f in targets
                 if (vault / f).exists()
                 and (vault / f).read_text(encoding="utf-8", errors="replace") != before[f]]
        for f in fixed:
            print(f"FIX\t{f}")          # stdout: machine-readable for the shim to re-stage
        if fixed:
            sys.stderr.write(f"[born-link] auto-wrapped {len(fixed)} file(s):\n  "
                             + "\n  ".join(fixed) + "\n")

    # Lint AFTER the fix: malformed links the auto-wrap can't resolve.
    blocks = []
    for f in targets:
        for lineno, link, target in malformed_in(vault, f):
            blocks.append((f, lineno, link, target))

    if blocks:
        sys.stderr.write(
            "\n[born-link] COMMIT BLOCKED — malformed wikilink(s) that Obsidian "
            "cannot resolve (fix the target stem, then re-commit):\n")
        for f, ln, link, target in blocks:
            sys.stderr.write(f"  {f}:{ln}  {link}\n")
        sys.stderr.write(
            "  -> a wikilink resolves by FILENAME STEM: drop any '.md' extension "
            "and any '../path/' prefix; point it at the bare stem.\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
