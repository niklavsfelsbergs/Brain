#!/usr/bin/env python3
"""Export the brain as a force-graph JSON for the cockpit neuron overlay.

Reuses the EXACT Obsidian resolver from
developer-braindead/bank/research/obsidian-graph-report.py (a `[[target]]`
resolves iff `target.md` exists by stem). Walks the whole brain (both brains +
root), builds the undirected note graph, and emits cockpit/web/graph.json:

  { "generated_at": <epoch>,
    "nodes": [ { "id": <rel>, "label": <stem>, "group": <color-group>,
                 "deg": <int> }, ... ],
    "links": [ { "s": <node-index>, "t": <node-index> }, ... ] }

Links carry node *indices* (not paths) to keep the file small. Read-only on the
brain; writes only cockpit/web/graph.json. Run it again to refresh the graph.

  python cockpit/graph-export.py [--root <brain-root>] [--out <path>]
"""
from __future__ import annotations

import argparse
import json
import re
import time
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
            target = m.group(1).split("|", 1)[0].split("#", 1)[0].strip()
            if target:
                yield target


def group_for(rel: str) -> str:
    """Color group from the path — which brain / which cognitive region."""
    p = rel.split("/")
    if p[0] == "gielinor":
        if len(p) > 3 and p[1] == "players" and p[2] in ("jebrim", "zezima"):
            return p[2]                       # a real player's namespace
        if p[1] == "deities":
            return "guthix"
        if p[1] in ("examine", "niksis8", "keepsake", "lorebook"):
            return "identity"
        if p[1] in ("meta", "spellbook"):
            return "gielinor-core"
        return "gielinor"
    if p[0] == "developer-braindead":
        return "dev"
    return "infra"                            # cockpit / .claude / switchboard / docs / root


def cluster_for(rel: str) -> str:
    """The cognitive AREA a note belongs to — the bubble it lives in. Finer than
    group_for: player × layer, so a glowing bubble reads as 'Jebrim's quest-log'."""
    p = rel.split("/")
    if p[0] == "gielinor":
        if len(p) > 3 and p[1] == "players" and p[2] in ("jebrim", "zezima"):
            return f"{p[2]}·{p[3]}"        # jebrim·bank, zezima·quest-log, …
        if p[1] == "players":
            return "players·misc"
        if p[1] == "deities":
            return "guthix"
        if p[1] in ("examine", "niksis8", "keepsake", "lorebook"):
            return "identity"
        if p[1] == "meta":
            return "meta"
        if p[1] == "spellbook":
            return "spellbook"
        return f"gielinor·{p[1]}"
    if p[0] == "developer-braindead":
        return f"dev·{p[1]}" if len(p) > 1 else "dev"
    if p[0] == "cockpit":
        return "cockpit"
    return "infra"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent),
                    help="brain root to walk (default: repo root)")
    ap.add_argument("--out", default=None, help="output json (default: cockpit/web/graph.json)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out) if args.out else (root / "cockpit" / "web" / "graph.json")

    files = sorted(p for p in root.rglob("*.md")
                   if "/.git/" not in p.as_posix() and "/node_modules/" not in p.as_posix())
    rels = [p.relative_to(root).as_posix() for p in files]
    idx = {rel: i for i, rel in enumerate(rels)}

    # stem -> rel (exact-filename resolution; last-writer-wins on dup stems, as
    # Obsidian collapses). Global across both brains so cross-brain links that
    # DO resolve become edges; the §O.5 by-design cross-brain ghosts stay unlinked.
    stem_to_rel = {p.stem: p.relative_to(root).as_posix() for p in files}

    adj = defaultdict(set)
    for p, rel in zip(files, rels):
        for tgt in link_targets(p):
            dest = stem_to_rel.get(tgt)
            if dest is not None and dest != rel:
                a, b = idx[rel], idx[dest]
                adj[a].add(b)
                adj[b].add(a)

    links = [{"s": a, "t": b} for a in adj for b in adj[a] if a < b]
    nodes = [{"id": rel, "label": Path(rel).stem, "group": group_for(rel),
              "cluster": cluster_for(rel), "deg": len(adj[i])} for i, rel in enumerate(rels)]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"generated_at": time.time(), "nodes": nodes, "links": links}),
                   encoding="utf-8")

    connected = sum(1 for n in nodes if n["deg"] > 0)
    by_cluster = defaultdict(int)
    for n in nodes:
        by_cluster[n["cluster"]] += 1
    print(f"wrote {out}")
    print(f"  {len(nodes)} nodes · {len(links)} edges · {connected} connected "
          f"({100*connected//max(1,len(nodes))}%) · {len(by_cluster)} clusters")
    for g in sorted(by_cluster, key=lambda x: -by_cluster[x]):
        print(f"    {by_cluster[g]:>4}  {g}")


if __name__ == "__main__":
    main()
