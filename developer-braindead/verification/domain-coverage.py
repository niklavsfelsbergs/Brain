#!/usr/bin/env python3
"""domain-coverage.py -- the §Z.D domain-coverage detector.

Read-only audit of the per-player `bank/domains/` layer (the §Z domain-knowledge
digests). It surfaces three things, per player, that the alching digest-synthesis
step (gielinor/spellbook/rituals/alching.md, step 2b) acts on:

  1. STALE digests -- a `corpus[]` note whose mtime is newer than the digest's
     `synthesized:` date => the digest should be re-synthesized.
  2. UNCOVERED note-clusters -- `bank/notes/**` notes that appear in NO digest's
     corpus, grouped by folder => candidate new domains (the bootstrap worklist).
  3. NO-LAYER players -- a player with bank notes but no `bank/domains/` digests
     at all => the whole player needs a bootstrap pass (e.g. Zezima).

Plus MISSING-corpus (a digest cites a note that no longer exists) as a hygiene flag.

It NEVER writes -- it's a detector. The lifecycle "born" (uncovered -> synthesize)
and "tended" (stale -> re-synthesize) decisions are alching's, principal-gated.

Run:
  python developer-braindead/verification/domain-coverage.py            # all players
  python developer-braindead/verification/domain-coverage.py --player jebrim
  python developer-braindead/verification/domain-coverage.py --stale-exit   # exit 1 if any stale
"""
import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parents[2]
PLAYERS_DIR = BRAIN_ROOT / "gielinor" / "players"


def parse_frontmatter(path: Path) -> dict:
    """Minimal stdlib reader for the digest frontmatter (matches the parser in
    domain-cue-reminder.py): flat `key: scalar` / `key:`-then-`  - item`. A
    malformed file returns {}."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data, cur_key = {}, None
    for raw in parts[1].splitlines():
        if not raw.strip():
            continue
        item = re.match(r"^\s+-\s+(.*)$", raw)
        if item and cur_key:
            if isinstance(data.get(cur_key), list):
                data[cur_key].append(item.group(1).strip())
            continue
        kv = re.match(r"^([\w-]+):\s*(.*)$", raw)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            cur_key = key
            data[key] = val if val else []
    return data


def _parse_date(s: str):
    """A 'YYYY-MM-DD' (optionally with trailing text) -> date, else None."""
    if not isinstance(s, str):
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s.strip())
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _mtime_date(p: Path):
    try:
        return datetime.fromtimestamp(p.stat().st_mtime).date()
    except OSError:
        return None


def _player_dirs(only: str = ""):
    if not PLAYERS_DIR.is_dir():
        return []
    out = []
    for d in sorted(PLAYERS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_") or d.name == "inbox":
            continue
        if only and d.name != only:
            continue
        out.append(d)
    return out


def audit_player(player_root: Path) -> dict:
    """Returns {player, has_layer, digests, stale[], uncovered{dir:[notes]},
    missing[], note_count}."""
    name = player_root.name
    domains_dir = player_root / "bank" / "domains"
    notes_dir = player_root / "bank" / "notes"

    all_notes = []
    if notes_dir.is_dir():
        all_notes = sorted(
            p.relative_to(player_root).as_posix()
            for p in notes_dir.rglob("*.md")
            if p.is_file() and not p.name.startswith("_")
        )

    digests = []
    if domains_dir.is_dir():
        digests = sorted(
            p for p in domains_dir.glob("*.md") if not p.name.startswith("_")
        )

    res = {
        "player": name,
        "has_layer": bool(digests),
        "digest_count": len(digests),
        "note_count": len(all_notes),
        "stale": [],
        "missing": [],
        "uncovered": {},
    }

    covered = set()
    for dg in digests:
        fm = parse_frontmatter(dg)
        corpus = fm.get("corpus") or []
        synth = _parse_date(fm.get("synthesized") or "")
        for rel in corpus:
            if not isinstance(rel, str) or not rel:
                continue
            covered.add(rel)
            note_path = player_root / rel
            if not note_path.is_file():
                res["missing"].append((dg.name, rel))
                continue
            md = _mtime_date(note_path)
            if synth and md and md > synth:
                res["stale"].append((dg.name, rel, md.isoformat(), synth.isoformat()))

    # Uncovered = notes in no digest corpus, grouped by parent folder.
    for rel in all_notes:
        if rel in covered:
            continue
        folder = rel.rsplit("/", 1)[0] if "/" in rel else "."
        res["uncovered"].setdefault(folder, []).append(rel)
    return res


def print_report(results: list) -> int:
    stale_total = 0
    print("=" * 72)
    print("§Z.D DOMAIN-COVERAGE DETECTOR -- per-player bank/domains/ audit")
    print("=" * 72)
    for r in results:
        head = (f"\nPLAYER {r['player']} -- {r['digest_count']} digest(s), "
                f"{r['note_count']} bank note(s)")
        if not r["has_layer"]:
            if r["note_count"]:
                print(head + "  ** NO DOMAINS LAYER -> whole-player bootstrap candidate **")
            else:
                print(head + "  (no notes, no layer -- nothing to cover)")
            continue
        print(head)

        if r["stale"]:
            stale_total += len(r["stale"])
            print("  STALE (corpus note newer than the digest's synthesized date -> re-synthesize):")
            for dg, rel, md, synth in r["stale"]:
                print(f"    - {dg}: {rel} edited {md} > synthesized {synth}")
        else:
            print("  STALE: none")

        if r["missing"]:
            print("  MISSING corpus (digest cites a note that no longer exists -> fix the corpus list):")
            for dg, rel in r["missing"]:
                print(f"    - {dg}: {rel}")

        if r["uncovered"]:
            tot = sum(len(v) for v in r["uncovered"].values())
            print(f"  UNCOVERED note-clusters ({tot} note(s) in no digest corpus -> candidate domains):")
            for folder, notes in sorted(r["uncovered"].items(), key=lambda kv: -len(kv[1])):
                print(f"    {folder}/  ({len(notes)})")
                for n in notes:
                    print(f"      - {n.rsplit('/', 1)[-1]}")
        else:
            print("  UNCOVERED: none -- every bank note is cited by some digest")
    print("\n" + "-" * 72)
    print(f"summary: {stale_total} stale digest-corpus link(s) across "
          f"{len(results)} player(s)")
    return stale_total


def main() -> int:
    ap = argparse.ArgumentParser(description="§Z.D domain-coverage detector (read-only)")
    ap.add_argument("--player", default="", help="audit one player only")
    ap.add_argument("--stale-exit", action="store_true",
                    help="exit 1 if any stale digest-corpus link is found")
    args = ap.parse_args()

    results = [audit_player(p) for p in _player_dirs(args.player)]
    if not results:
        print("no players found", file=sys.stderr)
        return 0
    stale_total = print_report(results)
    return 1 if (args.stale_exit and stale_total) else 0


if __name__ == "__main__":
    sys.exit(main())
