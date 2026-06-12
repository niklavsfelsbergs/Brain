#!/usr/bin/env python3
"""hygiene-check.py — S187, the §Z.D detector pattern on the two drift axes
the S186 audit flagged. The audit's recurring failure class is *hand-enforced
caps drift while hooks hold*: nothing breaks loudly, files and folders just
regrow between cleanups (respawn.md 49k→62k tok in 17 days; Jebrim in-progress
27→30; state.ndjson 7 MB with no sweep). Hooks can't gate "too many files" —
but a detector can make the drift visible BEFORE the next audit trips over it,
exactly like domain-coverage.py does for stale digests.

Two axes:

  A — ACTIVE-STATE hygiene, per player (gielinor/players/*):
      quest-log/in-progress/ count vs cap + stale files (mtime > threshold);
      inventory/ resume-file count vs cap. The S158 cleanup (46→2) regrew to
      30 by S187 — this is the regrowth alarm.

  B — TELEMETRY boundedness (switchboard/ + the known sidecar streams):
      ndjson streams over their sweep caps ×1.25 (a sweep exists but isn't
      holding), un-archived *.log files in switchboard/ root (dead diag
      loggers), synthetic test-fixture sids in ritual-events.ndjson (the
      suites redirect via RITUAL_EVENTS_PATH since S187 — any reappearance
      means a new emitter bypassed it), and *.tmp.* litter from failed
      atomic replaces.

  C — LOREBOOK-INDEX coverage (S192, the [LOR] cue arm's drift guard):
      gielinor/lorebook/_index.md is the synthesized cue index the
      domain-cue hook parses; a decision promoted to confirmed/ without an
      index entry is invisible to the arm (the index regrows stale exactly
      like every other hand-maintained map). Flags confirmed D-NNN files
      missing from the index and ghost index entries with no confirmed file.

Read-only. Exit 0 always (a detector surfaces, it doesn't gate — the R3
honesty: rituals/sessions choose to act). Run any time:

    python developer-braindead/verification/hygiene-check.py
"""

import importlib.util
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]            # brain/
PLAYERS_DIR = ROOT / "gielinor" / "players"
SWITCHBOARD = ROOT / "switchboard"
LOREBOOK = ROOT / "gielinor" / "lorebook"

# ── Axis A thresholds (hand-enforced caps, made visible) ────────────────────
INPROGRESS_CAP = 10        # files in quest-log/in-progress/ before flagging
STALE_DAYS = 14            # an in-progress file untouched this long is stale
INVENTORY_CAP = 8          # resume files in inventory/ before flagging

# ── Axis B caps — mirror the writers' sweep constants ×1.25 headroom ────────
# (over cap×1.25 means the sweep ISN'T HOLDING, not merely "due a sweep")
NDJSON_CAPS = {
    "state.ndjson": 3_000_000,        # emit-event/status-sidecar sweep (S187)
    "chat.ndjson": 1_000_000,         # emit-event/status-sidecar sweep (S052)
    "ritual-events.ndjson": 2_000_000,  # ritual_log sweep
}
CAP_HEADROOM = 1.25


def _load_synthetic_matcher():
    """Reuse adherence-rates.py's synthetic-sid denylist (single source)."""
    spec = importlib.util.spec_from_file_location(
        "adherence_rates", Path(__file__).resolve().parent / "adherence-rates.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.is_synthetic_sid


# ── Axis A ───────────────────────────────────────────────────────────────────
def check_active_state(players_dir: Path = PLAYERS_DIR,
                       now: float | None = None) -> list[str]:
    """Per-player in-progress/inventory drift. Returns FLAG lines ([] = clean)."""
    now = now if now is not None else time.time()
    flags: list[str] = []
    if not players_dir.is_dir():
        return [f"FLAG players dir missing: {players_dir}"]
    for player in sorted(p for p in players_dir.iterdir() if p.is_dir()):
        if player.name.startswith("_"):
            continue
        inprog = player / "quest-log" / "in-progress"
        files = sorted(inprog.glob("*.md")) if inprog.is_dir() else []
        stale = [f for f in files
                 if (now - f.stat().st_mtime) > STALE_DAYS * 86400]
        if len(files) > INPROGRESS_CAP:
            dwarf = sum(1 for f in files if "dwarf" in f.name.lower())
            flags.append(
                f"FLAG {player.name}: {len(files)} in-progress quest files "
                f"(cap {INPROGRESS_CAP}; {dwarf} dwarf traces) — graduate or archive")
        for f in stale:
            age = int((now - f.stat().st_mtime) / 86400)
            flags.append(f"FLAG {player.name}: stale in-progress "
                         f"{f.name} ({age}d untouched)")
        inv = player / "inventory"
        resumes = [f for f in inv.glob("*.md")
                   if not f.name.startswith("_")] if inv.is_dir() else []
        if len(resumes) > INVENTORY_CAP:
            flags.append(f"FLAG {player.name}: {len(resumes)} inventory files "
                         f"(cap {INVENTORY_CAP}) — stale resumes to archive?")
    return flags


# ── Axis B ───────────────────────────────────────────────────────────────────
def check_telemetry(sb: Path = SWITCHBOARD,
                    is_synthetic=None) -> list[str]:
    """Switchboard telemetry boundedness. Returns FLAG lines ([] = clean)."""
    flags: list[str] = []
    if not sb.is_dir():
        return [f"FLAG switchboard dir missing: {sb}"]
    for name, cap in NDJSON_CAPS.items():
        p = sb / name
        if p.exists() and p.stat().st_size > cap * CAP_HEADROOM:
            flags.append(f"FLAG {name}: {p.stat().st_size:,} B > "
                         f"{int(cap * CAP_HEADROOM):,} B — its sweep is not holding")
    for log in sorted(sb.glob("*.log")):
        flags.append(f"FLAG un-archived log in switchboard root: {log.name} "
                     f"({log.stat().st_size:,} B) — dead diag logger? move to archive/")
    for tmp in sorted(sb.glob("*.tmp.*")):
        flags.append(f"FLAG atomic-replace litter: {tmp.name}")
    ev = sb / "ritual-events.ndjson"
    if ev.exists():
        if is_synthetic is None:
            is_synthetic = _load_synthetic_matcher()
        import json
        syn_sids = set()
        for line in ev.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                sid = json.loads(line).get("sid8") or ""
            except Exception:
                continue
            if is_synthetic(sid):
                syn_sids.add(sid)
        if syn_sids:
            flags.append(
                f"FLAG synthetic sids back in ritual-events.ndjson: "
                f"{sorted(syn_sids)} — an emitter is bypassing RITUAL_EVENTS_PATH")
    return flags


# ── Axis C ───────────────────────────────────────────────────────────────────
def check_lorebook_index(lorebook: Path = LOREBOOK) -> list[str]:
    """Confirmed-decision vs cue-index coverage. Returns FLAG lines ([] = clean)."""
    import re
    flags: list[str] = []
    confirmed_dir = lorebook / "confirmed"
    index = lorebook / "_index.md"
    if not confirmed_dir.is_dir():
        return [f"FLAG lorebook confirmed/ missing: {confirmed_dir}"]
    if not index.exists():
        return [f"FLAG lorebook/_index.md missing — the [LOR] cue arm is blind"]
    confirmed = {m.group(1) for f in confirmed_dir.glob("D-*.md")
                 if (m := re.match(r"(D-\d{3})", f.name))}
    # Headers may carry born-link wikilink wraps: `## [[D-NNN_stem|D-NNN]] — …`.
    indexed = set(re.findall(
        r"^##\s+(?:\[\[[^\]|]+\|)?(D-\d{3})(?:\]\])?\s",
        index.read_text(encoding="utf-8"), re.MULTILINE))
    for d in sorted(confirmed - indexed):
        flags.append(f"FLAG lorebook {d} confirmed but NOT in _index.md — "
                     f"invisible to the [LOR] cue arm; add its entry")
    for d in sorted(indexed - confirmed):
        flags.append(f"FLAG lorebook _index.md has ghost entry {d} "
                     f"(no confirmed file) — remove or fix")
    return flags


def main() -> int:
    print("=" * 72)
    print("S187 HYGIENE DETECTOR — active-state drift + telemetry boundedness")
    print("=" * 72)
    a = check_active_state()
    b = check_telemetry()
    c = check_lorebook_index()
    print(f"\nAxis A — active-state (players under {PLAYERS_DIR.name}/):")
    print("\n".join(f"  {f}" for f in a) if a else "  clean")
    print(f"\nAxis B — telemetry ({SWITCHBOARD.name}/):")
    print("\n".join(f"  {f}" for f in b) if b else "  clean")
    print(f"\nAxis C — lorebook cue-index coverage:")
    print("\n".join(f"  {f}" for f in c) if c else "  clean")
    print(f"\nsummary: {len(a) + len(b) + len(c)} flag(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
