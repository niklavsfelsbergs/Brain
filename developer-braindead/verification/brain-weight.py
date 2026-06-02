#!/usr/bin/env python3
"""brain-weight.py — Phase-0 ground-truth instrument (read-only).

Measures the brain's ALWAYS-ON CONTEXT WEIGHT: the tokens that load every
single session before any task work. The anti-deterioration thesis (S145) is
that the brain gets dumber as it gets richer — because the always-on load grows
monotonically and a heavier load degrades adherence to every rule (constraint-
count collapse, lost-in-the-middle, context rot). This script turns that thesis
into a number you can watch.

Two things it reports:

  WEIGHT NOW — the eager-load footprint at HEAD, broken down:
    * @import chain: the CLAUDE.md files + every `@path` they pull in,
      recursively. Claude Code expands these INLINE at launch — they are in
      context verbatim, every session, unconditionally. This is the hard tax.
    * ritual-read identity layers: the files the respawn ritual reads on entry
      (examine/confirmed, keepsake/current, niksis8/confirmed, persona, player
      CLAUDE.md). Eager via ritual rather than @import, but still every session.

  GROWTH CURVE — the @import-chain total over git history, one sample per day,
    from birth to HEAD. This is the deterioration curve: if it climbs, the
    always-on tax is rising and every session pays more.

Token estimate: len(text) / 4.0 (no tiktoken on this host). It is an ESTIMATE,
labelled as such; the trend matters more than the absolute. chars are exact.

Usage:
    python developer-braindead/verification/brain-weight.py            # full report
    python developer-braindead/verification/brain-weight.py --root gielinor/CLAUDE.md
    python developer-braindead/verification/brain-weight.py --no-curve # skip git history

Read-only: never writes, never mutates. Safe any time.
"""
import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[2]  # brain/
CHARS_PER_TOKEN = 4.0
IMPORT_RE = re.compile(r"^@(\S+)\s*$")

# Roots that load eagerly. Brain-root CLAUDE.md @imports gielinor/CLAUDE.md,
# which @imports the meta rulebook — so starting at the brain root captures the
# whole chain a default (brain-root) session pulls in.
DEFAULT_ROOTS = ["CLAUDE.md", "gielinor/CLAUDE.md"]

# Ritual-read identity layers (globs, relative to brain root). The respawn ritual
# reads these on entry for the active player + globals. Player globs use jebrim as
# the representative active player (one player loads at a time).
RITUAL_GLOBS = [
    "gielinor/keepsake/current.md",
    "gielinor/examine/confirmed/*.md",
    "gielinor/niksis8/confirmed/*.md",
    "gielinor/players/jebrim/keepsake/current.md",
    "gielinor/players/jebrim/examine/confirmed/*.md",
    "gielinor/players/jebrim/niksis8_character/confirmed/*.md",
    "gielinor/players/jebrim/persona.md",
    "gielinor/players/jebrim/CLAUDE.md",
    "gielinor/players/jebrim/_about.md",
]


def est_tokens(text: str) -> int:
    return round(len(text) / CHARS_PER_TOKEN)


def resolve_imports(root_rel: str, brain: Path = BRAIN, _seen=None, _depth=0):
    """Return ordered list of (relpath, text) for a CLAUDE.md and everything it
    @imports, recursively (depth cap 4 = Claude Code's limit). Missing/cyclic
    imports are skipped silently (they contribute 0, as they would at runtime)."""
    if _seen is None:
        _seen = set()
    out = []
    rel = root_rel.replace("\\", "/")
    if rel in _seen or _depth > 4:
        return out
    _seen.add(rel)
    fp = (brain / rel)
    try:
        text = fp.read_text(encoding="utf-8")
    except OSError:
        return out
    out.append((rel, text))
    base = fp.parent
    for line in text.splitlines():
        m = IMPORT_RE.match(line.strip())
        if not m:
            continue
        imp = (base / m.group(1)).resolve()
        try:
            imp_rel = imp.relative_to(brain).as_posix()
        except ValueError:
            continue
        out.extend(resolve_imports(imp_rel, brain, _seen, _depth + 1))
    return out


def weight_now(roots) -> None:
    print("=" * 68)
    print("ALWAYS-ON CONTEXT WEIGHT @ HEAD   (token est = chars / 4)")
    print("=" * 68)

    seen = set()
    chain = []
    for r in roots:
        chain.extend(resolve_imports(r, _seen=seen))
    print("\n@IMPORT CHAIN (expanded inline every session, unconditional):")
    ctot_c = ctot_t = 0
    for rel, text in chain:
        c, t = len(text), est_tokens(text)
        ctot_c += c
        ctot_t += t
        print(f"  {t:>6} tok  {c:>7} ch  {rel}")
    print(f"  {'-'*46}")
    print(f"  {ctot_t:>6} tok  {ctot_c:>7} ch  == @import-chain subtotal ({len(chain)} files)")

    print("\nRITUAL-READ IDENTITY LAYERS (respawn reads on entry; jebrim as active):")
    rtot_c = rtot_t = 0
    rfiles = 0
    for g in RITUAL_GLOBS:
        for fp in sorted(BRAIN.glob(g)):
            try:
                text = fp.read_text(encoding="utf-8")
            except OSError:
                continue
            c, t = len(text), est_tokens(text)
            rtot_c += c
            rtot_t += t
            rfiles += 1
            print(f"  {t:>6} tok  {c:>7} ch  {fp.relative_to(BRAIN).as_posix()}")
    print(f"  {'-'*46}")
    print(f"  {rtot_t:>6} tok  {rtot_c:>7} ch  == ritual-read subtotal ({rfiles} files)")

    print(f"\nTOTAL ALWAYS-ON: {ctot_t + rtot_t} tok est  ({ctot_c + rtot_c} ch)")
    print(f"  of which @import chain (the hard tax): {ctot_t} tok "
          f"({100*ctot_t//max(1,ctot_t+rtot_t)}%)")
    return [rel for rel, _ in chain]


def growth_curve(chain_paths) -> None:
    print("\n" + "=" * 68)
    print("GROWTH CURVE — @import-chain total over time (one sample/day)")
    print("  (chain membership resolved at HEAD; a path missing in an older")
    print("   commit counts 0 — so this tracks today's chain growing into being)")
    print("=" * 68)
    try:
        log = subprocess.run(
            ["git", "log", "--reverse", "--date=short", "--format=%H|%ad"],
            cwd=BRAIN, capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"  (git unavailable: {e})")
        return

    # last commit per day
    per_day = {}
    for line in log:
        h, d = line.split("|", 1)
        per_day[d] = h  # later overwrites -> last commit that day

    prev = None
    for day, h in per_day.items():
        total_c = 0
        for rel in chain_paths:
            try:
                blob = subprocess.run(
                    ["git", "show", f"{h}:{rel}"],
                    cwd=BRAIN, capture_output=True, text=True,
                )
                if blob.returncode == 0:
                    total_c += len(blob.stdout)
            except OSError:
                pass
        t = est_tokens_int(total_c)
        delta = "" if prev is None else f"  ({'+' if t-prev>=0 else ''}{t-prev})"
        bar = "#" * (t // 200)
        print(f"  {day}  {t:>6} tok{delta:<10} {bar}")
        prev = t


def est_tokens_int(chars: int) -> int:
    return round(chars / CHARS_PER_TOKEN)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", action="append", help="CLAUDE.md root(s) to resolve; repeatable")
    ap.add_argument("--no-curve", action="store_true", help="skip the git growth curve")
    args = ap.parse_args()
    roots = args.root or DEFAULT_ROOTS
    chain_paths = weight_now(roots)
    if not args.no_curve:
        growth_curve(chain_paths)
    return 0


if __name__ == "__main__":
    sys.exit(main())
