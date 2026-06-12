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
      transcript (`Reading:` lines + actual Read/Grep/Agent calls), NOT in this
      event stream. The default report shows fire-density + a clearly-LABELED
      co-occurrence proxy. **--obedience (S192) closes the axis**: it joins each
      real nudge event to its session transcript (~/.claude/projects/), locates
      the prompt turn the cue fired on, and scores the turn on (a) a `Reading:`
      preamble line and (b) an actual tool call touching the cued knowledge home
      (per-hook token map from cue_registry / the §Z digest paths). That turns
      "fired 295x, obedience unmeasured" into a measured rate — honest caveats:
      only nudge-decisions are scored (inline = guaranteed load, no obedience
      question), and sessions whose transcript is gone score as unscored, never
      as disobedient.

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
    python developer-braindead/verification/adherence-rates.py --obedience [--days N]

Read-only by default; --snapshot appends one line to the snapshot file (never
mutates the event log). Safe to run any time.
"""

import argparse
import json
import re
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

# Synthetic sid8s the boundary/live-fire test suites append to the LIVE event
# log (S187 finding: ~173 polluted events across 5 test days — 78% of the raw
# draft-redirect count was test fixtures). Several are hex-shaped (aaaa1111,
# deadbe99), so real-vs-synthetic cannot be inferred from sid shape alone; this
# is an explicit denylist of the known fixture conventions. Filtered by default;
# --include-synthetic restores the raw stream. The root fix (tests targeting a
# temp events file) is tracked separately — until then this keeps the rates
# honest. NOTE: rates may differ slightly from pre-S187 snapshots, which were
# computed on the raw stream.
_SYNTHETIC_SID_RE = re.compile(
    r"^(lf[0-9a-z]*|livefire|test1234|sess[a-z0-9]*|scm(?:one|two)00"
    r"|aaaa\d+|bbbb\d+|cccc\d+|dddd\d+|7777aaaa|9999cccc|zzzz9999"
    r"|zv_.*|deadbe99)$"
)


def is_synthetic_sid(sid8: str | None) -> bool:
    return bool(sid8) and bool(_SYNTHETIC_SID_RE.match(sid8))


def _load(events_path: Path, days: float | None,
          include_synthetic: bool = False) -> list[dict]:
    """Parse the event stream, windowed to the last `days` (None = all time).
    Malformed lines are skipped, mirroring ritual-stats.py's tolerance.
    Synthetic test-fixture sessions are dropped unless include_synthetic."""
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
        if not include_synthetic and is_synthetic_sid(ev.get("sid8")):
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


# ── Tier-3 obedience (S192): transcript-grounded cue-obedience ────────────
# A nudge event says "the cue fired"; the transcript says what happened next.
# For each REAL nudge we locate the prompt turn it fired on (nearest real user
# prompt to the event ts) and score that turn on two independent signals:
#   reading_line — the assistant's text carries a `Reading:` preamble line
#                  (the R3 visible-grounding-plan discipline);
#   cued_read    — a tool call in the turn actually touches the CUED knowledge
#                  home (Read/Grep/Bash/Agent input contains a home token).
# `either` is the headline obedience rate. Sessions with no transcript on disk
# (rotated away) are UNSCORED, never counted as disobedient.

TRANSCRIPT_ROOT = Path.home() / ".claude" / "projects"

# Both the plain "Reading: x" and the bold preamble form "**Reading:** x".
_READING_LINE_RE = re.compile(r"\bReading:(?:\*\*)?\s")
_PROMPT_MATCH_WINDOW_S = 300        # event-ts -> prompt-row max distance

# Static home-token map for hooks whose homes aren't in cue_registry.
_STATIC_HOME_TOKENS = {
    "grounding-cue": ["bank/", "research/", "quest-log/", "memory/"],
}


def _iso_epoch(ts: str) -> float:
    from datetime import datetime
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def _cue_home_tokens(hook: str) -> list[str]:
    """Lowercase substrings that count as 'touched the cued home' for a hook."""
    for prefix, toks in _STATIC_HOME_TOKENS.items():
        if hook.startswith(prefix):
            return toks
    if hook.startswith("domain-cue:domain-"):
        # §Z.C per-player digest nudge -> the digest file (post-inline name-nudges)
        slug = hook.split("domain-cue:domain-", 1)[1]
        return [f"bank/domains/{slug}", "bank/domains/"]
    if hook.startswith("lorebook-cue"):
        return ["lorebook/"]
    if hook.startswith(("domain-cue:", "shipping-cue")):
        name = hook.split(":", 1)[1] if ":" in hook else "shipping"
        try:
            hooks_dir = ROOT / "gielinor" / ".claude" / "hooks"
            if str(hooks_dir) not in sys.path:
                sys.path.insert(0, str(hooks_dir))
            from cue_registry import DOMAINS  # type: ignore
        except Exception:
            return [name]
        for d in DOMAINS:
            if d.get("name") == name:
                toks = [name]
                for f in d.get("canonical_files", []):
                    base = f.replace(":", "/").split("/")[-1].strip()
                    if base:
                        toks.append(base.lower())
                if d.get("specialist"):
                    toks.append("shipping-agent")
                return toks
        return [name]
    return []


def _find_transcript(sid8: str, root: Path = None) -> Path | None:
    root = root or TRANSCRIPT_ROOT
    if not sid8 or not root.is_dir():
        return None
    for proj in root.iterdir():
        if not proj.is_dir():
            continue
        hits = sorted(proj.glob(f"{sid8}*.jsonl"))
        if hits:
            return hits[0]
    return None


def _parse_transcript(path: Path) -> list[dict]:
    """Reduce a transcript to scoring rows: ts, is_prompt (a REAL user prompt —
    not a tool_result carrier, not isMeta, not a sub-agent sidechain), the
    assistant text, and the tool-call inputs."""
    rows = []
    try:
        fh = path.open(encoding="utf-8")
    except OSError:
        return rows
    with fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            t = r.get("type")
            if t not in ("user", "assistant") or r.get("isSidechain"):
                continue
            try:
                ep = _iso_epoch(r.get("timestamp") or "")
            except Exception:
                continue
            content = (r.get("message") or {}).get("content")
            texts, tools, has_tool_result = [], [], False
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    bt = b.get("type")
                    if bt == "text":
                        texts.append(b.get("text") or "")
                    elif bt == "tool_use":
                        try:
                            tools.append(json.dumps(b.get("input") or {}).lower())
                        except Exception:
                            pass
                    elif bt == "tool_result":
                        has_tool_result = True
            is_prompt = (t == "user" and not has_tool_result
                         and not r.get("isMeta") and bool("".join(texts).strip()))
            rows.append({"type": t, "ts": ep, "texts": texts, "tools": tools,
                         "is_prompt": is_prompt})
    return rows


def _score_turn(rows: list[dict], event_ts: float, home_tokens: list[str]) -> dict | None:
    """Find the prompt turn the cue fired on; score it. None = prompt not located."""
    prompts = [(i, abs(r["ts"] - event_ts)) for i, r in enumerate(rows)
               if r["is_prompt"] and abs(r["ts"] - event_ts) <= _PROMPT_MATCH_WINDOW_S]
    if not prompts:
        return None
    start = min(prompts, key=lambda p: p[1])[0]
    end = next((i for i in range(start + 1, len(rows)) if rows[i]["is_prompt"]),
               len(rows))
    reading_line = False
    cued_read = False
    toks = [t.lower() for t in home_tokens]
    for r in rows[start + 1:end]:
        if r["type"] != "assistant":
            continue
        if not reading_line and any(_READING_LINE_RE.search(x) for x in r["texts"]):
            reading_line = True
        if not cued_read and toks:
            for tool_input in r["tools"]:
                if any(t in tool_input for t in toks):
                    cued_read = True
                    break
        if reading_line and cued_read:
            break
    return {"reading_line": reading_line, "cued_read": cued_read,
            "either": reading_line or cued_read}


def compute_obedience(events: list[dict], transcript_root: Path = None) -> dict:
    """Join nudge events to transcripts; per-hook + total obedience. Pure given
    the events list + a transcript root (harness-drivable)."""
    transcript_root = transcript_root or TRANSCRIPT_ROOT
    per_hook: dict[str, Counter] = defaultdict(Counter)
    cache: dict[str, list[dict] | None] = {}
    for ev in events:
        hook = ev.get("hook") or ""
        if ev.get("decision") != "nudge":
            continue
        if not any(hook.startswith(p) for p in
                   _ADVISORY_CUE_PREFIXES + ("lorebook-cue",)):
            continue
        c = per_hook[hook]
        c["fired"] += 1
        sid8 = ev.get("sid8") or ""
        if sid8 not in cache:
            tp = _find_transcript(sid8, transcript_root)
            cache[sid8] = _parse_transcript(tp) if tp else None
        rows = cache[sid8]
        if not rows:
            c["no_transcript"] += 1
            continue
        score = _score_turn(rows, float(ev.get("ts") or 0), _cue_home_tokens(hook))
        if score is None:
            c["unlocated"] += 1
            continue
        c["scored"] += 1
        c["reading_line"] += int(score["reading_line"])
        c["cued_read"] += int(score["cued_read"])
        c["either"] += int(score["either"])
    total = Counter()
    for c in per_hook.values():
        total.update(c)
    return {"per_hook": {k: dict(v) for k, v in per_hook.items()},
            "total": dict(total)}


def report_obedience(m: dict, window: str) -> list[str]:
    out = [f"=== Tier-3 cue OBEDIENCE — transcript-grounded (S192) — window: {window} ===",
           "(scored = nudge joined to its prompt turn; unscored = transcript gone or",
           " prompt not located — never counted as disobedient. inline events are",
           " guaranteed-load and excluded by construction.)\n",
           f"  {'hook':<34} {'fired':>5} {'scored':>6} {'Reading:':>9} "
           f"{'cued-read':>9} {'either':>7}"]

    def line(name, c):
        s = c.get("scored", 0)
        def cell(k):
            v = c.get(k, 0)
            return f"{v} ({v / s * 100:.0f}%)" if s else "-"
        return (f"  {name:<34} {c.get('fired', 0):>5} {s:>6} "
                f"{cell('reading_line'):>9} {cell('cued_read'):>9} {cell('either'):>7}")

    for name, c in sorted(m["per_hook"].items(),
                          key=lambda kv: -kv[1].get("fired", 0)):
        out.append(line(name, c))
    out.append(line("TOTAL", m["total"]))
    t = m["total"]
    unscored = t.get("no_transcript", 0) + t.get("unlocated", 0)
    if unscored:
        out.append(f"\n  unscored: {unscored} "
                   f"({t.get('no_transcript', 0)} transcript gone, "
                   f"{t.get('unlocated', 0)} prompt not located)")
    out.append("\n  caveat: for inline-bearing hooks (deploy-schema, the per-player")
    out.append("  domain-* digests) a 'nudge' is the post-inline tail — the contents")
    out.append("  were force-injected EARLIER in that session, so a low rate there is")
    out.append("  NOT disobedience. The honest obedience reads are the never-inlined")
    out.append("  advisory hooks: domain-cue:shipping and grounding-cue.")
    return out


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
    out.append("  Obedience — did the agent load the CUED knowledge? — lives in the")
    out.append("  transcript, not this stream: run with --obedience for the")
    out.append("  transcript-grounded measure (S192). High-fire cues below are the")
    out.append("  forced-read CONVERSION CANDIDATES (advisory → guaranteed-load):")
    for k, v in sorted(m["cue_fires"].items(), key=lambda kv: -kv[1])[:5]:
        out.append(f"    - {k}: {v} fires")
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
            r = json.loads(line)
        except Exception:
            continue
        if r.get("kind") == "obedience":
            continue  # obedience snapshots have their own shape; not in this table
        rows.append(r)
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
    ap.add_argument("--include-synthetic", action="store_true",
                    help="keep test-fixture sessions (raw stream; default drops them)")
    ap.add_argument("--obedience", action="store_true",
                    help="transcript-grounded tier-3 cue-obedience report (S192)")
    args = ap.parse_args()

    if args.trend:
        print("\n".join(trend(args.snapshots)))
        return 0

    events = _load(args.events, args.days, args.include_synthetic)
    window = f"last {args.days:g} days" if args.days else "all time"

    if args.obedience:
        ob = compute_obedience(events)
        print("\n".join(report_obedience(ob, window)))
        if args.snapshot:
            t = ob["total"]
            s = t.get("scored", 0)
            rec = {"kind": "obedience", "ts": round(time.time(), 3),
                   "window_days": args.days, "fired": t.get("fired", 0),
                   "scored": s,
                   "reading_line_rate": (t.get("reading_line", 0) / s) if s else None,
                   "cued_read_rate": (t.get("cued_read", 0) / s) if s else None,
                   "either_rate": (t.get("either", 0) / s) if s else None}
            args.snapshots.parent.mkdir(parents=True, exist_ok=True)
            with args.snapshots.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, separators=(",", ":")) + "\n")
            print(f"\n[obedience snapshot appended to "
                  f"{args.snapshots.relative_to(ROOT).as_posix()}]")
        return 0

    m = compute(events)
    print("\n".join(report(m, window)))

    if args.snapshot:
        write_snapshot(m, args.days, args.snapshots)
        print(f"\n[snapshot appended to {args.snapshots.relative_to(ROOT).as_posix()}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
