#!/usr/bin/env python3
"""confirmed-scan.py -- contradiction / rot scan over the GATED layers.

The brain's value rests on the gated layers being trustworthy ground truth:
the per-player and global examine/confirmed/, niksis8/confirmed/,
lorebook/confirmed/, and the promoted bank/notes/. Those are the layers that
get force-injected and reasoned FROM every session. If they accumulate a
wrong-but-confident claim, it doesn't crash -- it compounds silently.

This is the cheap audit that turns "read everything" into "read the few things
that look wrong." Read-only; it flags and nominates, it never edits.

Two tiers, because honesty about precision matters:

  HARD FLAGS -- near-zero false positives; treat as a worklist.
    1. DANGLING  -- a [[wikilink]] points at no existing file AND is a genuine
                    break: a bare ID (`[[D-012]]`, `[[S018]]`) or a single-word
                    placeholder (`[[keepsake]]`, `[[wikilink]]`). Resolution is
                    PREFIX-AWARE -- it strips the brain's filename conventions
                    (SNNN_/sid8_/date_, the `feedback_`/`reference_` memory type
                    prefixes, and the `D-NNN_`/`S018` lorebook/quest IDs) off
                    BOTH the link target and the corpus stems before matching,
                    because the brain links lessons by concept-slug while the
                    files carry those prefixes. A multi-word concept-slug that
                    still doesn't resolve is demoted to LOOSE (below), not hard-
                    flagged -- it points at a real lesson under a differing
                    stem, so crying "broken" trains the operator to ignore it.
    2. UNDATED   -- a note makes a load-bearing claim (money / percent /
                    "current"/"now") with NO as-of date anywhere (frontmatter,
                    body, or filename). The brain's own rule: every money
                    figure states its period.
    3. STALE     -- a load-bearing note whose newest as-of date is older than
                    --stale-days. Not an error; a re-verification worklist.

  CANDIDATES -- heuristic; deterministic code CANNOT judge these, it nominates
                them for an in-session Claude pass (see --emit-candidates).
    4. COLLISION -- two gated notes with near-identical titles (possible
                    redundant or conflicting canon -- human-facing).
    5. RELATED   -- topically-overlapping note PAIRS within one namespace,
                    emitted to JSON as the worklist for the semantic pass: a
                    Claude read of each pair judges whether their claims
                    actually contradict. Code clusters cheaply; the model judges.

Deterministic figure-pairing was tried and CUT: regex can't see a figure's unit
or magnitude, so it pairs a per-parcel rate against an aggregate total and floods
false positives -- and a scan that cries wolf trains the operator to ignore it,
the exact failure this tool exists to prevent. Contradiction judgment is the
semantic pass's job, over the RELATED pairs.

Known limitation (considered, deferred 2026-06-19): RELATED clusters on TITLE
tokens only, so a contradiction between two notes with dissimilar titles slips
through. Body-similarity widening was deferred -- the demonstrated need in real
use was HARD-flag (DANGLING) PRECISION, not RELATED recall, and widening the net
adds noise to the one tier that's clean. Revisit if a missed cross-title
contradiction actually surfaces.

The candidate tiers are deliberately NOT exit-code-failing on their own -- they
are review fodder, not errors.

Run:
  python developer-braindead/verification/confirmed-scan.py
  python developer-braindead/verification/confirmed-scan.py --stale-days 30
  python developer-braindead/verification/confirmed-scan.py --emit-candidates /tmp/cand.json
  python developer-braindead/verification/confirmed-scan.py --root <dir> --today 2026-06-18  # test/override
  python developer-braindead/verification/confirmed-scan.py --strict   # exit 1 on any HARD flag
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parents[2]

# The gated layers: canonical, force-injected, reasoned-from. These are what
# the operator auto-writes and (per the founding conversation) does not read.
GATED_GLOBS = (
    "**/confirmed/**/*.md",
    "**/bank/notes/**/*.md",
)
# Never scan history or the un-gated staging areas.
EXCLUDE_PARTS = ("archive", "drafts", "rejected", "__pycache__")

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
ASOF_RE = re.compile(r"as[\s_-]?of:?\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
FRONT_DATE_RE = re.compile(
    r"^\s*(?:freshness|synthesized|date|as_of|updated):\s*.*?(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE | re.MULTILINE,
)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
# load-bearing = quantitative or present-tense factual
MONEY_RE = re.compile(r"(?:€|EUR)\s?\d|\d[\d.,]*\s*(?:€|EUR)")
PCT_RE = re.compile(r"\d+(?:\.\d+)?\s?%")

# The brain's filename-prefix conventions. Stripped off BOTH the link target and
# the corpus stems so a concept-slug link resolves to its differently-named file:
#   - SNNN_ / sid8_ / date_      -- renamed quest files
#   - feedback_/reference_/...   -- harness auto-memory type prefixes
#   - D-NNN_ / S018_ / I-003_    -- lorebook decision / quest / idea IDs
_PREFIX_PATTERNS = (
    re.compile(r"^s\d+[-_]", re.IGNORECASE),                              # SNNN_ quest
    re.compile(r"^[0-9a-f]{8}[-_]", re.IGNORECASE),                       # sid8_
    re.compile(r"^\d{4}-\d{2}-\d{2}[-_]"),                                # date-
    re.compile(r"^(?:feedback|reference|project|user)[-_]", re.IGNORECASE),  # memory type prefix
    re.compile(r"^[dsiaqrbg]-?\d+[-_]", re.IGNORECASE),                   # D-033_/S018_/I-003_/B-020_ IDs
)
# a bare ID with no descriptive suffix: `D-012`, `S018`, `I-003` -- a genuine
# convention break (the brain authors links by full stem, per D-004), kept HARD.
_BARE_ID_RE = re.compile(r"[a-z]-?\d+", re.IGNORECASE)
_STOP = {
    "the", "a", "an", "to", "of", "is", "isnt", "not", "vs", "and", "for", "on",
    "in", "be", "it", "its", "with", "by", "as", "at", "or", "from", "2026",
    "current", "new", "old", "notes", "note", "report", "data",
}


def _collapse(s: str) -> str:
    """Lowercase, collapse - _ and whitespace to one separator (cross hyphen/underscore)."""
    return re.sub(r"[-_\s]+", "_", s.lower()).strip("_")


def _norm_stem(stem: str) -> str:
    """Strip the brain's filename-prefix conventions (iteratively, since none
    stack in practice but the order shouldn't matter) so a concept-slug resolves
    to its prefixed file."""
    s = stem.lower()
    changed = True
    while changed:
        changed = False
        for pat in _PREFIX_PATTERNS:
            new = pat.sub("", s)
            if new != s:
                s, changed = new, True
    return s


def _match_keys(stem: str) -> set:
    """The forms a stem can be linked by: full + prefix-stripped, separator-collapsed."""
    return {_collapse(stem), _collapse(_norm_stem(stem))}


def _sig_tokens(text: str) -> set:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in toks if t not in _STOP and len(t) > 2}


def _namespace(rel: str) -> str:
    """Coarse namespace so RELATED pairs stay within one canon (per-player / global)."""
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "players":
        return f"players/{parts[1]}"
    return parts[0]


def _default_memory_dir() -> Path:
    """The harness auto-memory dir for this project (link targets live here too)."""
    return (Path.home() / ".claude" / "projects"
            / "C--Users-niklavs-felsbergs-Documents-GitHub-brain" / "memory")


def _gated_files(root: Path) -> list:
    seen = {}
    for glob in GATED_GLOBS:
        for p in root.glob(glob):
            if any(part in EXCLUDE_PARTS for part in p.parts):
                continue
            if p.name.startswith("_about"):
                continue
            seen[p.resolve()] = p
    return sorted(seen.values())


def _link_corpus(roots: list) -> set:
    """Every .md basename stem across the given roots, in all match-key forms.

    Targets resolve across BOTH brains and the harness auto-memory dir -- a
    gated note routinely links a dev-brain decision (D-NNN) or a memory topic
    file (feedback_*/reference_*), so a gielinor-only corpus mis-flags those.
    """
    corpus = set()
    for root in roots:
        if not root or not root.exists():
            continue
        for p in root.rglob("*.md"):
            if "__pycache__" in p.parts:
                continue
            corpus |= _match_keys(p.stem)
    return corpus


def _resolve_link(target: str, corpus: set) -> str:
    """Return 'ok' | 'loose' | 'dangling' for a wikilink target.

    'ok'        resolves (prefix-aware) to a real file, or is a templated/anchor link.
    'loose'     points nowhere navigable but isn't a genuine break: a prose
                description (spaces/apostrophe) OR a multi-word concept-slug that
                names a real lesson under a differing stem -- fix opportunistically.
    'dangling'  a genuine break worth a HARD flag: a bare ID (`D-012`, `S018`) or
                a single-word placeholder (`keepsake`, `wikilink`).
    """
    t = target.split("|")[0].split("#")[0].strip()
    if not t:
        return "ok"          # pure-anchor link, nothing to resolve
    if "*" in t:
        return "ok"          # templated placeholder, not a real target
    if _match_keys(t) & corpus:
        return "ok"
    # link-by-description (prose / apostrophe) -> soft, not a hard flag
    if " " in t or "'" in t or "’" in t:
        return "loose"
    # a bare ID with a descriptive suffix would have resolved above; a BARE id is
    # a genuine convention break -> HARD. A multi-word concept-slug names a real
    # lesson under a differing filename -> soft (LOOSE). Single bare words
    # (placeholders, layer names) stay HARD.
    if _BARE_ID_RE.fullmatch(t):
        return "dangling"
    word_parts = [w for w in re.split(r"[-_]", _norm_stem(t)) if w]
    if len(word_parts) >= 3:
        return "loose"
    return "dangling"


def audit(root: Path, today: date, stale_days: int, corpus_roots: list = None) -> dict:
    files = _gated_files(root)
    corpus = _link_corpus(corpus_roots if corpus_roots else [root])

    dangling = []     # (relpath, target)
    loose = []        # (relpath, target) -- link-by-description, soft
    undated = []      # relpath
    stale = []        # (relpath, asof, age_days)
    titles = []       # (relpath, sig_topic_tokens, namespace)

    for p in files:
        rel = p.relative_to(root).as_posix()
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # CHECK 1 -- dangling links (+ soft loose bucket)
        for raw in WIKILINK_RE.findall(text):
            verdict = _resolve_link(raw, corpus)
            if verdict == "dangling":
                dangling.append((rel, raw.strip()))
            elif verdict == "loose":
                loose.append((rel, raw.strip()))

        # dates: body as-of, frontmatter, filename
        dates = set(ASOF_RE.findall(text)) | set(FRONT_DATE_RE.findall(text))
        dates |= set(DATE_RE.findall(p.name))
        # load-bearing = carries an actual quantitative claim (the "every money
        # figure states its period" rule). Present-tense prose alone is too noisy.
        load_bearing = bool(MONEY_RE.search(text) or PCT_RE.search(text))

        # CHECK 2 -- undated load-bearing claim
        if load_bearing and not dates:
            undated.append(rel)

        # CHECK 3 -- stale load-bearing note
        if load_bearing and dates:
            newest = max(dates)
            try:
                d = date.fromisoformat(newest)
                age = (today - d).days
                if age > stale_days:
                    stale.append((rel, newest, age))
            except ValueError:
                pass

        # CHECK 4/5 inputs -- topic tokens (title carries the topic densely)
        topic = _sig_tokens(_norm_stem(p.stem))
        titles.append((rel, topic, _namespace(rel)))

    collisions, related = _find_pairs(titles)

    return {
        "n_files": len(files),
        "dangling": dangling,
        "loose": loose,
        "undated": sorted(undated),
        "stale": sorted(stale, key=lambda x: -x[2]),
        "collisions": collisions,
        "related": related,
        "stale_days": stale_days,
    }


# COLLISION threshold (near-duplicate, human-facing) and RELATED threshold
# (topically-overlapping, fed to the semantic pass). Same-namespace only.
COLLISION_JACCARD = 0.6
RELATED_JACCARD = 0.34
RELATED_MIN_SHARED = 2


def _find_pairs(titles: list) -> tuple:
    """One pairwise pass -> (collisions, related). Same namespace, shared topic."""
    collisions, related = [], []
    n = len(titles)
    for i in range(n):
        rel_i, t_i, ns_i = titles[i]
        if len(t_i) < 2:
            continue
        for j in range(i + 1, n):
            rel_j, t_j, ns_j = titles[j]
            if ns_i != ns_j or len(t_j) < 2:
                continue
            inter = t_i & t_j
            if len(inter) < RELATED_MIN_SHARED:
                continue
            jac = len(inter) / len(t_i | t_j)
            rec = {"a": rel_i, "b": rel_j, "shared": sorted(inter), "jaccard": round(jac, 2)}
            if jac >= COLLISION_JACCARD:
                collisions.append(rec)
            elif jac >= RELATED_JACCARD:
                related.append(rec)
    collisions.sort(key=lambda d: -d["jaccard"])
    related.sort(key=lambda d: -d["jaccard"])
    return collisions[:25], related[:80]


def print_report(r: dict) -> int:
    hard = 0
    print("=" * 72)
    print(f"confirmed-scan: {r['n_files']} gated note(s) audited (read-only)")
    print("=" * 72)

    print("\n-- HARD FLAGS (worklist; near-zero false positives) --")

    if r["dangling"]:
        hard += 1
        print(f"\n  DANGLING: {len(r['dangling'])} wikilink(s) -> no such file "
              f"(the cited anchor vanished):")
        for rel, tgt in r["dangling"][:30]:
            print(f"    - {rel}")
            print(f"        [[{tgt}]]")
        if len(r["dangling"]) > 30:
            print(f"    ... and {len(r['dangling']) - 30} more")
    else:
        print("\n  DANGLING: ok (every wikilink resolves)")

    if r["loose"]:
        print(f"\n  LOOSE: {len(r['loose'])} link-by-description (prose target, "
              f"navigates nowhere -- soft, fix opportunistically):")
        for rel, tgt in r["loose"][:10]:
            print(f"    - {rel}  ->  [[{tgt}]]")
        if len(r["loose"]) > 10:
            print(f"    ... and {len(r['loose']) - 10} more")

    if r["undated"]:
        hard += 1
        print(f"\n  UNDATED: {len(r['undated'])} load-bearing note(s) with NO as-of date "
              f"(every figure states its period):")
        for rel in r["undated"][:30]:
            print(f"    - {rel}")
        if len(r["undated"]) > 30:
            print(f"    ... and {len(r['undated']) - 30} more")
    else:
        print("\n  UNDATED: ok (every load-bearing note carries a date)")

    if r["stale"]:
        print(f"\n  STALE: {len(r['stale'])} load-bearing note(s) older than "
              f"{r['stale_days']}d (re-verify worklist, not an error):")
        for rel, asof, age in r["stale"][:20]:
            print(f"    - [{age:>4}d  as-of {asof}]  {rel}")
        if len(r["stale"]) > 20:
            print(f"    ... and {len(r['stale']) - 20} more")
    else:
        print(f"\n  STALE: ok (no load-bearing note older than {r['stale_days']}d)")

    print("\n-- CANDIDATES (review fodder; the semantic pass judges these) --")

    if r["collisions"]:
        print(f"\n  COLLISION: {len(r['collisions'])} near-duplicate title pair(s) "
              f"(possible redundant/conflicting canon):")
        for c in r["collisions"][:15]:
            print(f"    - [{c['jaccard']}] {c['a']}")
            print(f"             {c['b']}")
    else:
        print("\n  COLLISION: none nominated")

    print(f"\n  RELATED: {len(r['related'])} topically-overlapping pair(s) "
          f"queued for the semantic contradiction pass.")
    print("  (run --emit-candidates <path>, then a Claude read of each pair)")

    print("\n" + "-" * 72)
    print(f"summary: {hard} HARD flag-class(es). RELATED/COLLISION need an in-session "
          f"Claude read -- run with --emit-candidates.")
    return hard


def main() -> int:
    ap = argparse.ArgumentParser(description="contradiction/rot scan over gated layers (read-only)")
    ap.add_argument("--root", default="", help="audit-scope root override (testing)")
    ap.add_argument("--today", default="", help="YYYY-MM-DD override for staleness (testing)")
    ap.add_argument("--stale-days", type=int, default=45, help="staleness threshold in days")
    ap.add_argument("--memory-dir", default="", help="harness auto-memory dir for link resolution")
    ap.add_argument("--no-default-corpus", action="store_true",
                    help="resolve links against --root only (testing isolation)")
    ap.add_argument("--emit-candidates", default="", help="write DIVERGENCE/COLLISION candidates as JSON")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any HARD flag-class is raised")
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else (BRAIN_ROOT / "gielinor")
    today = date.fromisoformat(args.today) if args.today else date.today()

    if args.no_default_corpus:
        corpus_roots = [root]
    else:
        # links resolve across both brains + the harness auto-memory dir
        mem = Path(args.memory_dir) if args.memory_dir else _default_memory_dir()
        corpus_roots = [BRAIN_ROOT, mem]

    r = audit(root, today, args.stale_days, corpus_roots)
    hard = print_report(r)

    if args.emit_candidates:
        payload = {
            "instructions": (
                "Each pair is two gated notes that share a topic. For each, read "
                "both files and decide: do their factual claims CONTRADICT (same "
                "quantity/definition/decision, incompatible values), accounting for "
                "stated as-of dates and acknowledged supersession? Report only real "
                "contradictions with file:line evidence; ignore mere overlap."
            ),
            "collisions": r["collisions"],
            "related": r["related"],
        }
        Path(args.emit_candidates).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\ncandidates written -> {args.emit_candidates}")

    return 1 if (args.strict and hard) else 0


if __name__ == "__main__":
    sys.exit(main())
