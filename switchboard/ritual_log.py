#!/usr/bin/env python
"""Ritual-event log — Khaan item 11, Band A (machine-readable hook analytics).

WHY
  Rituals leave a quest-log *narrative* but no machine-readable trace. We can't
  currently answer "how often does the OPEN gate block?", "which write-boundary
  fires most?", "how often does block-deletes catch something?" without grepping
  prose. This module records what the enforcement/advisory hooks actually *did*
  — ground truth from code, not agent self-report (Band C, the hand-emitted
  path, is deliberately NOT built; it depends on the discipline the gates exist
  to backstop). Agent-decision outcomes (alching reject-vs-promote, drafts
  approve-vs-reject) are derived separately from git history by ritual-stats.py
  (Band B) — they are not emitted here.

WHAT
  One append-only NDJSON stream at switchboard/ritual-events.ndjson, one record
  per gate-relevant decision: {ts, hook, decision, actor, sid8, path_class,
  detail?}. Queried by developer-braindead/verification/ritual-stats.py.

HOW HOOKS USE IT (one import block, copy-paste; never breaks a hook on failure)
    import sys
    from pathlib import Path
    _SB = Path(__file__).resolve().parents[3] / "switchboard"
    if str(_SB) not in sys.path:
        sys.path.insert(0, str(_SB))
    try:
        from ritual_log import log_event, classify_path
    except Exception:
        def log_event(*a, **k): pass
        def classify_path(p): return ""

  Then at the decision points that matter (block branch, meaningful-allow
  branch), call log_event(...). Do NOT log every early `return 0` — those are
  not-applicable cases (wrong tool, outside brain), not ritual decisions.

INVARIANT
  NEVER raises, NEVER blocks. A logging fault must not fail or delay a tool
  call. Every path is wrapped; all errors swallowed to stderr. Mirrors
  emit-event.py's atomic-append + fail-silent posture (the B8/B9 lessons).
"""

import json
import os
import sys
import time
from pathlib import Path

EVENTS_PATH = Path(__file__).resolve().parent / "ritual-events.ndjson"

# Bounded growth — same shape as chat.ndjson's sweep. Cheap stat-gated check;
# truncates to the tail on an atomic rewrite. Append-only otherwise.
_SIZE_MAX = 2_000_000      # bytes
_TAIL_KEEP = 4000          # lines retained on truncate


def _events_path() -> Path:
    """Resolve the event-log path per call. RITUAL_EVENTS_PATH overrides the
    default — set by the verification test harnesses so synthetic boundary-test
    events land in a temp file instead of polluting the LIVE analytics stream
    (S187 finding: ~173 test-fixture events had accumulated in the real log,
    skewing draft-redirect counts 4→18). Resolved per call, not at import, so
    a harness can set the env var before or after importing a hook module."""
    override = os.environ.get("RITUAL_EVENTS_PATH")
    return Path(override) if override else EVENTS_PATH


def classify_path(rel: str) -> str:
    """Coarse class of a brain-relative path, for analytics grouping. Returns
    a short tag ('confirmed', 'drafts', 'meta', 'quest-log', ...) or '' when
    nothing matches. Order matters — most-specific first."""
    if not rel:
        return ""
    s = str(rel).replace("\\", "/").lower()
    table = [
        ("confirmed/", "confirmed"),
        ("/drafts/", "drafts"),
        ("drafts/", "drafts"),
        ("/rejected/", "rejected"),
        ("keepsake/", "keepsake"),
        ("lorebook/", "lorebook"),
        ("/meta/", "meta"),
        ("spellbook/rituals/", "rituals"),
        ("spellbook/", "spellbook"),
        ("quest-log/", "quest-log"),
        ("inventory/", "inventory"),
        ("/bank/", "bank"),
        ("research/", "research"),
        ("examine/", "examine"),
        ("niksis8", "niksis8"),
    ]
    for needle, tag in table:
        if needle in s:
            return tag
    return ""


def _sweep() -> None:
    try:
        path = _events_path()
        if not path.exists():
            return
        if path.stat().st_size <= _SIZE_MAX:
            return
        lines = path.read_text(encoding="utf-8").splitlines()
        tail = lines[-_TAIL_KEEP:]
        tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
        tmp.write_text("\n".join(tail) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    except Exception as e:
        print(f"ritual_log: sweep failed: {e}", file=sys.stderr)


def log_event(hook: str, decision: str, *, actor: str = "", sid8: str = "",
              path_class: str = "", detail: str = "") -> None:
    """Append one ritual-event record. hook = the hook's short name
    ('require-open', 'gnome-boundary', 'block-deletes', ...). decision =
    'allow' | 'block' | 'nudge' | 'silent'. All other fields optional context.
    Never raises."""
    try:
        rec = {
            "ts": round(time.time(), 3),
            "hook": hook or "",
            "decision": decision or "",
            "actor": (actor or "").lower(),
            "sid8": (sid8 or "")[:8].lower(),
            "path_class": path_class or "",
        }
        if detail:
            rec["detail"] = str(detail)[:200]
        path = _events_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
        _sweep()
    except Exception as e:
        print(f"ritual_log: log_event failed: {e}", file=sys.stderr)
