#!/usr/bin/env python3
"""recall-scoring.py — scored retrieval over the brain's markdown memory.

The brain retrieves by grep + [[link]]-following, with the model ranking
relevance in its head. That works, but it has no *attention* signal: it can't
cheaply tell which note matters most, so an important-but-quiet note (well
referenced, but unpinned and not touched lately) silently never surfaces.

This adds that signal — a heuristic score, NO embeddings, NO manual tagging.
Every input is already on disk:

  centrality  backlink degree in the [[link]] graph  (a note many others
              reference is important)  -- the Obsidian densification (24%->74%
              connected) is what makes this signal real.
  recency     filesystem mtime, exponential decay     (recent = fresh)
  staleness   1 - recency                              (old = due for a revisit)
  pinned      stem appears as a [[link]] in any keepsake/current.md
  relevance   query-term hit density                   (--query mode only)

Two modes, because recency pulls opposite ways depending on the job:

  --surface          PROACTIVE. "What important thing have I not looked at
                     lately?" Ranks DURABLE knowledge by  centrality x staleness,
                     skipping already-pinned notes (they surface anyway) and the
                     volatile floor (archive/inventory/drafts/rejected/quest-log).
                     This is the gap the model can't fill in-session: it can't
                     survey 435 files every respawn.

  --query "terms"    RECALL. Ranks notes MATCHING the query by
                     relevance x centrality x recency. A pre-ranker for the
                     Guthix "what do I have on X" path.

Read-only. Self-contained (stdlib only) so a gielinor ritual can call it without
reaching into the dev brain (the read-asymmetry rule). The link parser is copied
from developer-braindead/bank/research/obsidian-graph-report.py on purpose —
duplication beats a cross-brain runtime import.

Usage:
  python recall-scoring.py --surface [--top 15]
  python recall-scoring.py --query "shipping cost mart" [--top 15]
  python recall-scoring.py --surface --vault /path/to/gielinor
"""
from __future__ import annotations

import argparse
import math
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

# ---- tunable weights (the --validate step calibrates these) ----------------
W_SURFACE = {"central": 0.6, "stale": 0.4}      # proactive resurfacing
W_QUERY = {"relevance": 0.5, "central": 0.25, "recency": 0.2, "pinned": 0.05}
HALFLIFE_DAYS = 30.0                              # recency/staleness decay

# Durable knowledge worth resurfacing. Surface-mode candidates must match one of
# these path fragments; everything else (volatile/episodic/by-design floor) is out.
DURABLE = (
    "/bank/notes/",
    "/examine/confirmed/",
    "/niksis8/confirmed/",
    "/niksis8_character/confirmed/",
    "/lorebook/confirmed/",
    "/spellbook/skills/",
)
# Never a candidate / never scored as durable, even if nested oddly.
EXCLUDE = ("/archive/", "/rejected/", "/drafts/", "/inventory/",
           "/quest-log/", "/proposals/", "/comms/")

LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


# ---- link parsing (copied from obsidian-graph-report.py) --------------------
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


def link_targets(text: str):
    """Yield each link's bare target stem (alias/heading stripped), skipping
    fenced + inline code."""
    fenced = False
    for line in text.splitlines():
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


# ---- helpers ---------------------------------------------------------------
def norm(d: dict) -> dict:
    """Min-max normalize a {key: value} map to 0..1 (flat -> all 0)."""
    if not d:
        return {}
    lo, hi = min(d.values()), max(d.values())
    if hi == lo:
        return {k: 0.0 for k in d}
    return {k: (v - lo) / (hi - lo) for k, v in d.items()}


def git_commit_times(vault: Path, rels) -> dict:
    """rel -> last-commit epoch, via ONE git-log walk (committer time of the most
    recent commit that touched each file). Filesystem mtime is unreliable here:
    a checkout/commit stamps whole clusters with one time, collapsing the
    'quiet' signal. Falls back to fs mtime for untracked/new files, and for all
    files if git is unavailable."""
    fs = {rel: (vault / rel).stat().st_mtime for rel in rels}
    try:
        root = subprocess.run(
            ["git", "-C", str(vault), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip()
        prefix = vault.resolve().relative_to(Path(root).resolve()).as_posix()
        out = subprocess.run(
            ["git", "-C", str(vault), "log", "--format=C%ct", "--name-only"],
            capture_output=True, text=True, check=True).stdout
    except Exception:
        return fs
    pre = (prefix + "/") if prefix and prefix != "." else ""
    times, cur = {}, None
    for line in out.splitlines():
        if line.startswith("C") and line[1:].isdigit():
            cur = int(line[1:])
        elif line and cur is not None:
            rel = line[len(pre):] if pre and line.startswith(pre) else (
                line if not pre else None)
            if rel and rel not in times:   # first occurrence = most recent
                times[rel] = cur
    return {rel: times.get(rel, fs[rel]) for rel in rels}


def excluded(rel: str) -> bool:
    p = "/" + rel
    return any(frag in p for frag in EXCLUDE)


def is_durable(rel: str) -> bool:
    return (not excluded(rel)) and any(frag in ("/" + rel) for frag in DURABLE)


# ---- main ------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--surface", action="store_true",
                   help="proactive: rank durable notes by centrality x staleness")
    g.add_argument("--query", metavar="TERMS",
                   help="recall: rank notes matching TERMS by relevance x centrality x recency")
    ap.add_argument("--top", type=int, default=15, help="results to show (default 15)")
    default_vault = Path(__file__).resolve().parents[2]  # gielinor/
    ap.add_argument("--vault", type=Path, default=default_vault,
                    help=f"vault root (default: {default_vault})")
    args = ap.parse_args()

    vault = args.vault.resolve()
    files = [p for p in vault.rglob("*.md") if "/.git/" not in p.as_posix()]
    rel_of = {p: p.relative_to(vault).as_posix() for p in files}
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in files}

    # --- backlink graph (undirected degree = centrality) ---
    stem_to_rel = {p.stem: rel_of[p] for p in files}
    rel_to_path = {rel_of[p]: p for p in files}
    degree = defaultdict(int)
    seen_pairs = set()
    for p in files:
        rel = rel_of[p]
        for tgt in link_targets(texts[p]):
            dest = stem_to_rel.get(tgt)
            if dest is None or dest == rel:
                continue
            pair = tuple(sorted((rel, dest)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            degree[rel] += 1
            degree[dest] += 1

    # --- pins: any stem linked from a keepsake/current.md ---
    pinned_stems = set()
    for p in files:
        if rel_of[p].endswith("keepsake/current.md"):
            pinned_stems.update(link_targets(texts[p]))

    # --- recency from git last-commit-time (fs mtime is checkout-contaminated) ---
    now = time.time()
    ctime = git_commit_times(vault, [rel_of[p] for p in files])
    age_days = {p: max(0.0, (now - ctime[rel_of[p]]) / 86400.0) for p in files}
    recency = {p: math.exp(-age_days[p] / HALFLIFE_DAYS) for p in files}

    if args.surface:
        cands = [p for p in files if is_durable(rel_of[p])
                 and p.stem not in pinned_stems]
        cen = norm({p: degree[rel_of[p]] for p in cands})
        rows = []
        for p in cands:
            central = cen.get(p, 0.0)
            stale = 1.0 - recency[p]
            score = W_SURFACE["central"] * central + W_SURFACE["stale"] * stale
            rows.append((score, p, {"central": central, "stale": stale,
                                    "deg": degree[rel_of[p]],
                                    "age": age_days[p]}))
        title = (f"PROACTIVE SURFACING - {len(cands)} durable, unpinned notes "
                 f"(centrality x staleness)")
    else:
        terms = [t.lower() for t in re.findall(r"\w+", args.query) if len(t) > 1]
        hits = {}
        for p in files:
            if excluded(rel_of[p]):
                continue
            low = texts[p].lower()
            c = sum(low.count(t) for t in terms)
            if c:
                hits[p] = c
        if not hits:
            print(f"# no matches for: {args.query}")
            return
        cands = list(hits)
        rel_n = norm(hits)
        cen = norm({p: degree[rel_of[p]] for p in cands})
        rows = []
        for p in cands:
            relev = rel_n.get(p, 0.0)
            central = cen.get(p, 0.0)
            rec = recency[p]
            pin = 1.0 if p.stem in pinned_stems else 0.0
            score = (W_QUERY["relevance"] * relev + W_QUERY["central"] * central
                     + W_QUERY["recency"] * rec + W_QUERY["pinned"] * pin)
            rows.append((score, p, {"rel": relev, "central": central,
                                    "rec": rec, "hits": hits[p],
                                    "deg": degree[rel_of[p]]}))
        title = f"RECALL - {len(hits)} notes matching '{args.query}'"

    rows.sort(key=lambda r: -r[0])
    print(f"# {title}")
    print(f"# vault: {vault}  |  showing top {min(args.top, len(rows))} of {len(rows)}\n")
    for score, p, sig in rows[:args.top]:
        sigstr = "  ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}"
                           for k, v in sig.items())
        print(f"  {score:5.3f}  {rel_of[p]}")
        print(f"         {sigstr}")


if __name__ == "__main__":
    main()
