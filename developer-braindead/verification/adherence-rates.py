#!/usr/bin/env python3
"""adherence-rates.py — plan §X.7, the compliance-RATE lens over ritual-events.

WHY (the gap this closes)
  ritual-stats.py (Khaan item 11) reports raw event COUNTS — "require-open
  allowed 602×, grounding-cue nudged 38×". A count of fires is not a measure of
  OBEDIENCE: "the cue fired 14×" says nothing about whether the right knowledge
  actually loaded those 14 times. As the brain grew a fleet of advisory + gate
  hooks (require-open, the 4 sub-agent boundaries, block-confirmed/deletes,
  draft-gate, forced-read, domain-/grounding-cue), the question that matters for
  anti-deterioration shifted from "did the hook fire?" to "what FRACTION of the
  time did discipline hold?" — the rate that makes drift visible BEFORE it leaks
  into a real miss. This analyzer groups the same event stream BY SESSION and
  computes those rates.

THE HONESTY TIERS (why some signals are rates and some are only counts)
  A rate needs BOTH a pass signal and a fail signal in the log. Only some hooks
  log both, so this report is deliberately tiered — it never fabricates a % it
  cannot ground (the brain's "verify the measurement measures the thing" rule):

    Tier 1 — GATE-GROUNDED compliance. require-open logs allow (OPEN posted) AND
      block (OPEN missing) → a true compliance RATE. The other gates log only the
      catch (block / redirect), with no allow-baseline, so they are honest
      catch-COUNTS — drift signals, not rates.

    Tier 2 — GUARANTEED-LOAD coverage. forced-read INLINES the keepsake contents,
      so fire == load by construction (the §X.4 design). Its injection coverage
      IS a "knowledge actually loaded" rate for that knowledge.

    Tier 3 — ADVISORY-CUE obedience — NOT gate-grounded. domain-/grounding-cue
      only NUDGE; whether the agent then loaded the named knowledge lives in the
      transcript `Reading:` line (R3-tier, optional, omitted on trivial turns),
      NOT in this event stream. We report fire-density + a clearly-LABELED
      co-occurrence proxy and name the high-fire cues as forced-read CONVERSION
      CANDIDATES. We do NOT invent an obedience %. Naming the unclosed axis IS
      the deliverable.

PERSISTENCE (--snapshot / --trend)
  Raw events already persist in switchboard/ritual-events.ndjson, but that file
  is swept to its tail at 2 MB, so long-horizon history is lost. "Drift visible
  pre-leak" needs a TREND, so --snapshot appends one rate record per run to
  switchboard/adherence-snapshots.ndjson (the new durable artifact, survives the
  sweep); --trend reads them back and shows the flagship rate over time.

Usage:
    python developer-braindead/verification/adherence-rates.py [--days N]
    python developer-braindead/verification/adherence-rates.py --snapshot [--days N]
    python developer-braindead/verification/adherence-rates.py --trend

Read-only by default; --snapshot appends one line to the snapshot file (never
mutates the event log). Safe to run any time.
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# Windows consoles default to cp1252, which can't encode the § / → glyphs this
# report uses. Reconfigure to UTF-8 (Windows Terminal handles it); guarded so a
# pinned/legacy stream can't crash the run.
try:
    sys.stdout.reconfigure(encoding="utf-8")            # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]                 # brain/
EVENTS_DEFAULT = ROOT / "switchboard" / "ritual-events.ndjson"
SNAPSHOTS_DEFAULT = ROOT / "switchboard" / "adherence-snapshots.ndjson"

# Hook-name groupings. ":suffix" variants (domain-cue:shipping) are matched by
# prefix so a newly-registered domain row needs no code change here.
_ENFORCEMENT_BLOCK_HOOKS = {        # decision == "block" => a real violation caught
    "block-confirmed", "block-deletes", "git-index-guard",
    "comms-append-guard", "block-sub-spawn",
}
_BOUNDARY_HOOKS = {                  # sub-agent off-surface write caught (block-only)
    "dwarf-boundary", "gnome-boundary", "penguin-boundary",
    "shipping-agent-boundary",
}
_ADVISORY_CUE_PREFIXES = ("domain-cue", "grounding-cue", "shipping-cue")


def _load(events_path: Path, days: float | None) -> list[dict]:
    """Parse the event stream, windowed to the last `days` (None = all time).
    Malformed lines are skipped, mirroring ritual-stats.py's tolerance."""
    if not events_path.exists():
        return []
    cutoff = (time.time() - days * 86400) if days else None
    out = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if cutoff is not None and float(ev.get("ts") or 0) < cutoff:
            continue
        out.append(ev)
    return out


def _by_session(events: list[dict]) -> dict[str, list[dict]]:
    """Group events by sid8 (preserving ts order within each session)."""
    sessions: dict[str, list[dict]] = defaultdict(list)
    for ev in events:
        sessions[ev.get("sid8") or "(nosid)"].append(ev)
    for evs in sessions.values():
        evs.sort(key=lambda e: float(e.get("ts") or 0))
    return sessions


def compute(events: list[dict]) -> dict:
    """The whole rate computation, pure (no I/O) so the harness can drive it on
    synthetic streams. Returns a dict of the metrics the report + snapshot use."""
    sessions = _by_session(events)
    m: dict = {"sessions_total": len(sessions)}

    # ── Tier 1: OPEN-on-entry compliance (the flagship rate) ──────────────
    # require-open logs `allow` (an OPEN for this sid8 existed before the gated
    # write) or `block` (it didn't — the gate caught a missing OPEN). Per
    # session, the FIRST allow/block decides compliance: was the OPEN already
    # posted when the first gated content write landed? skip-noactor is an
    # unresolved-actor fail-open (instrumented, not a pass/fail) — excluded.
    first_allow = first_block = 0
    open_catches = 0          # every block event (a session can be caught >once)
    never_recovered = 0       # blocked and never reached an allow
    noactor_sessions = 0
    for evs in sessions.values():
        ro = [e for e in evs if e.get("hook") == "require-open"]
        decisions = [e.get("decision") for e in ro]
        open_catches += decisions.count("block")
        if "skip-noactor" in decisions and not any(
            d in ("allow", "block") for d in decisions
        ):
            noactor_sessions += 1
        first = next((d for d in decisions if d in ("allow", "block")), None)
        if first == "allow":
            first_allow += 1
        elif first == "block":
            first_block += 1
            if "allow" not in decisions:
                never_recovered += 1
    open_total = first_allow + first_block
    m["open_compliant_sessions"] = first_allow
    m["open_caught_sessions"] = first_block
    m["open_total_sessions"] = open_total
    m["open_catches"] = open_catches
    m["open_never_recovered"] = never_recovered
    m["open_noactor_sessions"] = noactor_sessions
    m["open_compliance_rate"] = (first_allow / open_total) if open_total else None

    # ── Tier 1: catch-counts (block-only gates — no allow-baseline = no rate) ─
    floor = Counter()
    boundary = Counter()
    draft_redirects = 0
    draft_bypass = 0
    for ev in events:
        hook = ev.get("hook") or ""
        dec = ev.get("decision") or ""
        if hook in _ENFORCEMENT_BLOCK_HOOKS and dec == "block":
            floor[hook] += 1
        elif hook in _BOUNDARY_HOOKS and dec == "block":
            boundary[hook] += 1
        elif hook == "draft-gate":
            if dec == "redirect":
                draft_redirects += 1
            elif dec.startswith("bypass"):
                draft_bypass += 1
    m["floor_catches"] = dict(floor)
    m["floor_catches_total"] = sum(floor.values())
    m["boundary_catches"] = dict(boundary)
    m["boundary_catches_total"] = sum(boundary.values())
    m["draft_redirects"] = draft_redirects
    m["draft_bypasses"] = draft_bypass

    # ── Tier 2: forced-read guaranteed-load coverage (fire == load) ───────
    fr_session_start = set()
    fr_player_inject = set()
    for ev in events:
        if ev.get("hook") != "forced-read":
            continue
        sid = ev.get("sid8") or "(nosid)"
        if ev.get("decision") == "session-start":
            fr_session_start.add(sid)
        elif ev.get("decision") == "player-inject":
            fr_player_inject.add(sid)
    # Player sessions inferred from a player actor on any require-open event
    # (braindead/guthix/wisp excluded — they bear no player keepsake to inject).
    _NON_PLAYER = {"braindead", "guthix", "wisp", ""}
    player_sessions = set()
    for sid, evs in sessions.items():
        for e in evs:
            if e.get("hook") == "require-open":
                a = (e.get("actor") or "").lower()
                if a and a not in _NON_PLAYER:
                    player_sessions.add(sid)
                    break
    m["forced_read_session_start"] = len(fr_session_start)
    m["forced_read_player_inject"] = len(fr_player_inject)
    m["player_sessions_seen"] = len(player_sessions)
    covered = len(player_sessions & fr_player_inject)
    m["player_inject_coverage_rate"] = (
        covered / len(player_sessions) if player_sessions else None
    )

    # ── Tier 3: advisory-cue fires + the honest "not gate-grounded" view ──
    cue_fires = Counter()
    cue_sessions = set()
    for ev in events:
        hook = ev.get("hook") or ""
        if ev.get("decision") == "nudge" and any(
            hook.startswith(p) for p in _ADVISORY_CUE_PREFIXES
        ):
            cue_fires[hook] += 1
            cue_sessions.add(ev.get("sid8") or "(nosid)")
    # Co-occurrence PROXY (NOT obedience): cue-firing sessions that also saw a
    # forced-read inject — i.e. *some* knowledge entered context that session.
    # It does not prove the agent read the cued file; it is a weak floor only.
    fr_any = fr_session_start | fr_player_inject
    proxy_hits = len(cue_sessions & fr_any)
    m["cue_fires"] = dict(cue_fires)
    m["cue_fires_total"] = sum(cue_fires.values())
    m["cue_sessions"] = len(cue_sessions)
    m["cue_load_proxy_hits"] = proxy_hits
    m["cue_load_proxy_rate"] = (
        proxy_hits / len(cue_sessions) if cue_sessions else None
    )
    return m


# ── reporting ─────────────────────────────────────────────────────────────
def _pct(x: float | None) -> str:
    return f"{x * 100:.0f}%" if x is not None else "n/a"


def report(m: dict, window: str) -> list[str]:
    out = [f"=== Adherence rates (plan §X.7) — window: {window} ==="]
    out.append(f"sessions in window: {m['sessions_total']}\n")

    out.append("Tier 1 — GATE-GROUNDED compliance (ground truth from the gate)")
    ot = m["open_total_sessions"]
    out.append(
        f"  OPEN-on-entry compliance: {_pct(m['open_compliance_rate'])}"
        f"  ({m['open_compliant_sessions']}/{ot} sessions posted the OPEN before"
        f" their first gated write)"
    )
    out.append(
        f"    gate-catches: {m['open_catches']} missing-OPEN writes blocked"
        f"   |   {m['open_caught_sessions']} sessions caught"
        f"   |   {m['open_never_recovered']} never posted an OPEN"
        f"   |   {m['open_noactor_sessions']} unresolved-actor (fail-open, unscored)"
    )
    out.append(
        f"  floor catches (confirmed/deletes/index/comms/sub-spawn): "
        f"{m['floor_catches_total']}"
        + (("  [" + ", ".join(f"{k}={v}" for k, v in
            sorted(m['floor_catches'].items(), key=lambda kv: -kv[1])) + "]")
           if m["floor_catches"] else "")
    )
    out.append(
        f"  sub-agent boundary catches: {m['boundary_catches_total']}"
        + (("  [" + ", ".join(f"{k}={v}" for k, v in
            sorted(m['boundary_catches'].items(), key=lambda kv: -kv[1])) + "]")
           if m["boundary_catches"] else "")
    )
    out.append(
        f"  draft-gate redirects: {m['draft_redirects']}  "
        f"(main-agent writes auto-routed back to drafts/ — guided gate would have"
        f" been missed; {m['draft_bypasses']} authorized bypasses)"
    )
    out.append("  (block-only gates carry no allow-baseline, so these are honest")
    out.append("   catch-COUNTS — a rising count is the drift signal, not a rate.)\n")

    out.append("Tier 2 — GUARANTEED-LOAD coverage (forced-read: fire == load, §X.4)")
    out.append(
        f"  session-start keepsake injects: {m['forced_read_session_start']} sessions"
    )
    out.append(
        f"  player keepsake hard-inline coverage: "
        f"{_pct(m['player_inject_coverage_rate'])}"
        f"  ({m['forced_read_player_inject']} injected / "
        f"{m['player_sessions_seen']} player sessions seen)"
    )
    out.append("  (the inject IS the load — this is a real 'knowledge loaded' rate")
    out.append("   for keepsake content. Small N until the §X.4 hook ages in.)\n")

    out.append("Tier 3 — ADVISORY-CUE obedience — NOT gate-grounded (the honest gap)")
    out.append(
        f"  cue fires: {m['cue_fires_total']} across {m['cue_sessions']} sessions"
        + (("  [" + ", ".join(f"{k}={v}" for k, v in
            sorted(m['cue_fires'].items(), key=lambda kv: -kv[1])) + "]")
           if m["cue_fires"] else "")
    )
    out.append(
        f"  co-occurrence proxy (NOT obedience): {_pct(m['cue_load_proxy_rate'])}"
        f"  ({m['cue_load_proxy_hits']}/{m['cue_sessions']} cue-firing sessions"
        f" also got a forced-read inject)"
    )
    out.append("  Obedience — did the agent load the CUED knowledge? — is not in")
    out.append("  this stream; it lives in the transcript `Reading:` line (R3,")
    out.append("  optional). Not fabricated here. The high-fire cues below are the")
    out.append("  forced-read CONVERSION CANDIDATES (advisory → guaranteed-load):")
    for k, v in sorted(m["cue_fires"].items(), key=lambda kv: -kv[1])[:5]:
        out.append(f"    - {k}: {v} fires, obedience unmeasured")
    return out


def _snapshot_record(m: dict, window_days: float | None) -> dict:
    """The flat, persisted slice — only the scalars worth trending."""
    return {
        "ts": round(time.time(), 3),
        "window_days": window_days,
        "sessions_total": m["sessions_total"],
        "open_compliance_rate": m["open_compliance_rate"],
        "open_total_sessions": m["open_total_sessions"],
        "open_catches": m["open_catches"],
        "floor_catches_total": m["floor_catches_total"],
        "boundary_catches_total": m["boundary_catches_total"],
        "draft_redirects": m["draft_redirects"],
        "player_inject_coverage_rate": m["player_inject_coverage_rate"],
        "forced_read_session_start": m["forced_read_session_start"],
        "cue_fires_total": m["cue_fires_total"],
        "cue_load_proxy_rate": m["cue_load_proxy_rate"],
    }


def write_snapshot(m: dict, window_days: float | None, path: Path) -> None:
    rec = _snapshot_record(m, window_days)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")


def trend(path: Path) -> list[str]:
    out = ["=== Adherence-rate trend (switchboard/adherence-snapshots.ndjson) ==="]
    if not path.exists():
        out.append("  (no snapshots yet — run with --snapshot to record one)")
        return out
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    if not rows:
        out.append("  (no valid snapshots)")
        return out
    out.append(f"  {'when':<20} {'win':>5} {'OPEN%':>6} {'sess':>5} "
               f"{'floor':>6} {'bound':>6} {'redir':>6} {'cue':>5}  Δ OPEN%")
    prev = None
    for r in rows:
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(r.get("ts", 0)))
        win = r.get("window_days")
        wins = f"{win:g}d" if win else "all"
        rate = r.get("open_compliance_rate")
        delta = ""
        if prev is not None and rate is not None and prev is not None:
            delta = f"{(rate - prev) * 100:+.0f}pt"
        if rate is not None:
            prev = rate
        out.append(
            f"  {when:<20} {wins:>5} {_pct(rate):>6} "
            f"{r.get('sessions_total', 0):>5} {r.get('floor_catches_total', 0):>6} "
            f"{r.get('boundary_catches_total', 0):>6} {r.get('draft_redirects', 0):>6} "
            f"{r.get('cue_fires_total', 0):>5}  {delta}"
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Adherence compliance rates (plan §X.7).")
    ap.add_argument("--days", type=float, default=None,
                    help="window to the last N days (default: all time)")
    ap.add_argument("--events", type=Path, default=EVENTS_DEFAULT,
                    help="path to ritual-events.ndjson")
    ap.add_argument("--snapshot", action="store_true",
                    help="append the current rates to the snapshot time-series")
    ap.add_argument("--snapshots", type=Path, default=SNAPSHOTS_DEFAULT,
                    help="path to adherence-snapshots.ndjson")
    ap.add_argument("--trend", action="store_true",
                    help="print the snapshot time-series and exit")
    args = ap.parse_args()

    if args.trend:
        print("\n".join(trend(args.snapshots)))
        return 0

    events = _load(args.events, args.days)
    m = compute(events)
    window = f"last {args.days:g} days" if args.days else "all time"
    print("\n".join(report(m, window)))

    if args.snapshot:
        write_snapshot(m, args.days, args.snapshots)
        print(f"\n[snapshot appended to {args.snapshots.relative_to(ROOT).as_posix()}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
