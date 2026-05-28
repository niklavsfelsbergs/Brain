#!/usr/bin/env python3
"""Obsidian graph-shape report — read-only enumeration of a vault's hanging points.

Mirrors stock Obsidian's resolver (a `[[target]]` / `[[target|alias]]` /
`[[target#heading]]` link resolves iff a file named `target.md` exists somewhere
in the vault, matched by exact stem). Builds the UNDIRECTED note graph and reports
the two kinds of "hanging point" you see in Obsidian's graph view:

  1. ISOLATED nodes   — real .md files with degree 0 (no resolved inbound or
                        outbound link to another note). They float at the rim.
  2. UNRESOLVED links — `[[target]]` where no `target.md` exists. Obsidian draws
                        these as ghost/placeholder nodes hanging off their referrer.

Grouped by top-level folder so the by-design floor (archive/inventory/rejected,
research, rulebook) is separable from real content misses.

Read-only: walks the vault, writes nothing. Default vault = gielinor/.
Self-links don't count toward degree. Code fences + inline code are skipped.

Usage:
  python obsidian-graph-report.py --vault <path-to-vault> [--list-isolated]
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def inline_code_spans(line: str):
    spans, i, n = [], 0, len(line)
    while i < n:
        if line[i] == "`":
            j = line.find("`", i + 1)
            if j == -1:
                break
            spans.append((i, j))
            i = j + 1
        else:
            i += 1
    return spans


def in_span(pos, spans):
    return any(a <= pos <= b for a, b in spans)


def link_targets(path: Path):
    """Yield each link's bare target stem (alias/heading stripped), skipping
    fenced + inline code. Empty / heading-only (`[[#sec]]`) links are skipped."""
    fenced = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        code = inline_code_spans(line)
        for m in LINK_RE.finditer(line):
            if in_span(m.start(), code):
                continue
            inner = m.group(1)
            target = inner.split("|", 1)[0].split("#", 1)[0].strip()
            if target:
                yield target


def top_folder(rel: str) -> str:
    parts = rel.split("/")
    return parts[0] if len(parts) > 1 else "(root)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True, help="vault root to analyze")
    ap.add_argument("--list-isolated", action="store_true",
                    help="list every isolated node (not just per-folder counts)")
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    files = [p for p in vault.rglob("*.md") if "/.git/" not in p.as_posix()]

    # stem -> rel (for exact-filename resolution). Last-writer-wins on dup stems
    # is fine: Obsidian also collapses, and we only need existence + a rel for grouping.
    stem_to_rel = {p.stem: p.relative_to(vault).as_posix() for p in files}
    rels = {p.relative_to(vault).as_posix() for p in files}

    # Build undirected adjacency + collect unresolved targets.
    adj = defaultdict(set)            # rel -> set(rel) of resolved neighbors
    unresolved = defaultdict(set)     # missing-target-stem -> set(referrer rel)
    for p in files:
        rel = p.relative_to(vault).as_posix()
        for tgt in link_targets(p):
            dest_rel = stem_to_rel.get(tgt)
            if dest_rel is None:
                unresolved[tgt].add(rel)
            elif dest_rel != rel:           # ignore self-links
                adj[rel].add(dest_rel)
                adj[dest_rel].add(rel)

    isolated = sorted(r for r in rels if not adj[r])
    connected = len(rels) - len(isolated)

    print(f"# Obsidian graph report — vault: {vault}")
    print(f"# {len(rels)} note nodes\n")

    print("## SUMMARY")
    pct = 100 * connected / len(rels) if rels else 0
    print(f"  connected nodes   : {connected}/{len(rels)} ({pct:.0f}%)")
    print(f"  ISOLATED nodes    : {len(isolated)} ({100-pct:.0f}%)")
    print(f"  unresolved targets: {len(unresolved)} distinct ghost nodes "
          f"({sum(len(v) for v in unresolved.values())} link occurrences)\n")

    # Isolated nodes grouped by top-level folder.
    iso_by_folder = defaultdict(list)
    for r in isolated:
        iso_by_folder[top_folder(r)].append(r)
    print("## ISOLATED nodes by top-level folder")
    for folder in sorted(iso_by_folder, key=lambda f: -len(iso_by_folder[f])):
        print(f"  {len(iso_by_folder[folder]):>4}  {folder}/")
    print()

    if args.list_isolated:
        print("## ISOLATED nodes — full list")
        for folder in sorted(iso_by_folder):
            print(f"\n  [{folder}/]")
            for r in iso_by_folder[folder]:
                print(f"    {r}")
        print()

    # Unresolved/phantom targets — the ghost nodes. Group by ID prefix vs other.
    if unresolved:
        print("## UNRESOLVED link targets (ghost nodes) — by referrer count")
        for tgt in sorted(unresolved, key=lambda t: (-len(unresolved[t]), t)):
            refs = sorted(unresolved[tgt])
            shown = ", ".join(refs[:3]) + (" ..." if len(refs) > 3 else "")
            print(f"  {len(refs):>3}x  [[{tgt}]]   <- {shown}")
        print()


if __name__ == "__main__":
    main()
