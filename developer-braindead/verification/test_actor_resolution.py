#!/usr/bin/env python3
"""test_actor_resolution.py -- guards the S181 _actor.py fix.

The bug: a "Hey Jebrim" session with no intent bubble yet got its status
mis-stamped `braindead` by the sidecar's instance-map tiebreaker (highest
instance number), and the shared resolve_actor trusted that status over the
agent's own intent declaration -> the require-open gate blocked writes against
the wrong (dev) comms. Fix: resolve_actor is intent-first, actor_from_intent
reads BOTH intent dirs and the freshest bubble wins.

Run: python developer-braindead/verification/test_actor_resolution.py
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[2] / "gielinor" / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS))
import _actor  # noqa: E402

PASS = 0
FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}: got {got!r}, want {want!r}")


def _mk_intent(root, subdir, actor, sid8, mtime=None):
    d = root / subdir / ".claude" / "intent"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{actor}-{sid8}.txt"
    f.write_text(f"{actor} intent bubble", encoding="utf-8")
    if mtime is not None:
        os.utime(f, (mtime, mtime))
    return f


def _mk_status(status_dir, sid8, actor):
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / f"{sid8}.json").write_text(
        json.dumps({"sid8": sid8, "actor": actor}), encoding="utf-8")


def main():
    sid = "a0b39f49"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        status_dir = root / "status"
        # Point actor_from_status at our temp status dir.
        _actor.STATUS_DIR = status_dir

        # 1. Intent-first: status says braindead, a jebrim bubble exists -> jebrim.
        _mk_status(status_dir, sid, "braindead")
        _mk_intent(root, "gielinor", "jebrim", sid)
        check("intent-first beats a wrong status", _actor.resolve_actor(sid, root), "jebrim")

        # 2. Scatter: the bubble lives in gielinor/.claude/intent (not brain root)
        #    and is still found (the half-dead-fallback bug).
        check("finds bubble in gielinor/.claude/intent", _actor.actor_from_intent(sid, root), "jebrim")

        # 3. Mid-session pivot: jebrim bubble (old) + braindead bubble (new, other
        #    dir) -> newest by mtime wins = braindead (the current actor).
        now = time.time()
        _mk_intent(root, "gielinor", "jebrim", sid, mtime=now - 100)
        _mk_intent(root, ".", "braindead", sid, mtime=now)  # brain-root intent dir
        check("freshest bubble wins across both dirs", _actor.resolve_actor(sid, root), "braindead")

        # 4. Status fallback: no intent bubble anywhere -> status value.
        sid2 = "deadbeef"
        _mk_status(status_dir, sid2, "zezima")
        check("status fallback when no bubble", _actor.resolve_actor(sid2, root), "zezima")

        # 5. Genuinely unresolved: no bubble, no status -> "".
        check("unresolved -> empty", _actor.resolve_actor("ffffffff", root), "")

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
