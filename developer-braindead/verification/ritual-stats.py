#!/usr/bin/env python3
"""ritual-stats.py — Khaan item 11 reporter (read-only).

Quantifies how the brain's rituals actually behave, two ways:

  Band A — hook decisions. Reads switchboard/ritual-events.ndjson (emitted by
    the enforcement/advisory hooks via switchboard/ritual_log.py): how often
    each gate blocked, each boundary caught an off-surface write, each advisory
    nudge fired, plus the require-open gate's allow-after-OPEN baseline. Ground
    truth from code — not agent self-report.

  Band B — ritual outcomes. Derived from git history (no new emission, no
    discipline dependency): drafts promoted to confirmed/ vs rejected/, keepsake
    proposals pinned. These are file-moves the principal makes during alching /
    drafts-triage / bankstanding; git -M rename detection recovers them.

Band C (hand-emitted ritual markers) is deliberately NOT built — it would depend
on the very discipline the gates exist to backstop.

Usage:
    python developer-braindead/verification/ritual-stats.py [--days N] [--events PATH]

Read-only: never writes, never mutates state. Safe to run any time.
"""

import argparse
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # brain/
EVENTS_DEFAULT = ROOT / "switchboard" / "ritual-events.ndjson"


# ── Band A ────────────────────────────────────────────────────────────────
def band_a(events_path: Path, days: float | None) -> list[str]:
    out = ["Band A — hook decisions (switchboard/ritual-events.ndjson)"]
    if not events_path.exists():
        out.append("  (no ritual-events.ndjson yet — no hook decisions recorded)")
        return out

    cutoff = (time.time() - days * 86400) if days else None
    by_hook_decision: Counter = Counter()
    blocks_by_class: Counter = Counter()
    blocks_by_actor: Counter = Counter()
    nudges: Counter = Counter()
    total = 0
    skipped = 0

    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            skipped += 1
            continue
        if cutoff is not None and float(ev.get("ts") or 0) < cutoff:
            continue
        total += 1
        hook = ev.get("hook") or "?"
        decision = ev.get("decision") or "?"
        by_hook_decision[(hook, decision)] += 1
        if decision == "block":
            blocks_by_class[ev.get("path_class") or "(none)"] += 1
            blocks_by_actor[ev.get("actor") or "(main)"] += 1
        elif decision == "nudge":
            nudges[hook] += 1

    window = f"last {days:g} days" if days else "all time"
    out.append(f"  window: {window}   events: {total}" + (f"   (skipped {skipped} malformed)" if skipped else ""))
    if not total:
        out.append("  (no events in window)")
        return out

    out.append("  by hook / decision:")
    for (hook, decision), n in sorted(by_hook_decision.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"    {hook:<24} {decision:<7} {n}")
    if blocks_by_class:
        out.append("  blocks by path-class: " + ", ".join(f"{k}={v}" for k, v in blocks_by_class.most_common()))
    if blocks_by_actor:
        out.append("  blocks by actor: " + ", ".join(f"{k}={v}" for k, v in blocks_by_actor.most_common()))
    if nudges:
        out.append("  advisory nudges: " + ", ".join(f"{k}={v}" for k, v in nudges.most_common()))
    return out


# ── Band B ────────────────────────────────────────────────────────────────
def _git_renames() -> list[tuple[str, str]]:
    """Every rename in history as (old, new). git -M infers renames from
    add/delete pairs too, so a 'drafts/X -> confirmed/X' promotion is caught
    even when content changed on promotion. Returns [] on any git failure."""
    try:
        res = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-M", "--diff-filter=R",
             "--name-status", "--pretty=format:"],
            capture_output=True, text=True, timeout=60,
        )
    except Exception:
        return []
    if res.returncode != 0:
        return []
    pairs = []
    for line in res.stdout.splitlines():
        if not line.startswith("R"):
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            pairs.append((parts[1].replace("\\", "/"), parts[2].replace("\\", "/")))
    return pairs


def _layer_of(path: str) -> str:
    for tag in ("examine", "niksis8_character", "niksis8", "lorebook",
                "keepsake", "bank", "spellbook"):
        if f"/{tag}/" in path or path.startswith(f"{tag}/"):
            return tag
    return "other"


def band_b() -> list[str]:
    out = ["Band B — ritual outcomes (git history)"]
    pairs = _git_renames()
    if not pairs:
        out.append("  (git rename history unavailable)")
        return out

    promoted = Counter()
    rejected = Counter()
    pinned = 0
    for old, new in pairs:
        o, n = old.lower(), new.lower()
        if "/drafts/" in o and "/confirmed/" in n:
            promoted[_layer_of(new)] += 1
        elif ("/drafts/" in o or "/proposals/" in o) and "/rejected/" in n:
            rejected[_layer_of(new)] += 1
        elif "/keepsake/proposals/" in o and "/archive/" in n:
            pinned += 1

    tot_p, tot_r = sum(promoted.values()), sum(rejected.values())
    out.append(f"  drafts promoted to confirmed/: {tot_p}"
               + (("   (" + ", ".join(f"{k}={v}" for k, v in promoted.most_common()) + ")") if promoted else ""))
    out.append(f"  drafts/proposals rejected:     {tot_r}"
               + (("   (" + ", ".join(f"{k}={v}" for k, v in rejected.most_common()) + ")") if rejected else ""))
    out.append(f"  keepsake proposals pinned:     {pinned}")
    if tot_p + tot_r:
        rate = 100.0 * tot_p / (tot_p + tot_r)
        out.append(f"  promote rate: {rate:.0f}%  ({tot_p}/{tot_p + tot_r})")
    out.append("  (best-effort: promotions are git -M renames drafts/ -> confirmed/; "
               "content-rewritten moves below the rename-similarity threshold are missed.)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Ritual analytics (Khaan item 11).")
    ap.add_argument("--days", type=float, default=None,
                    help="window Band A to the last N days (default: all time)")
    ap.add_argument("--events", type=Path, default=EVENTS_DEFAULT,
                    help="path to ritual-events.ndjson")
    args = ap.parse_args()

    print("=== Ritual analytics (Khaan item 11) ===\n")
    print("\n".join(band_a(args.events, args.days)))
    print()
    print("\n".join(band_b()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
