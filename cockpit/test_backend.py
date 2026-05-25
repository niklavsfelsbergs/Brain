"""Cockpit backend regression gate — the session-model contract.

Standalone, no pytest: `python cockpit/test_backend.py` (exit 0 = green). Add it
to the cheap pre-commit gates alongside `node --check` + `py_compile`.

Why this file exists: the cockpit's status pipeline has regressed repeatedly
across sessions — the board blanked (S080), the idle tally lied (S074), CLOSING
was a dead chip (S074), a malformed role file could 500 /api/sessions (S083). The
GUI can only be eyeballed on a relaunch; this pins the *logic* so a future edit
can't silently break the contract. It sandboxes backend.py's module-level file
constants into a tempdir, writes synthetic state, and asserts the shaped model.

Covers: stale-greying (S080) keeps last-known state + drops from the attention
tally; D-029 legacy-token aliasing; the action heartbeat; rank ordering; and the
S083 _pending_subagents crash-guard against malformed role files.
"""
from __future__ import annotations

import asyncio
import datetime
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backend  # noqa: E402

_PASS = 0
_FAIL = 0


def check(name, cond):
    global _PASS, _FAIL
    print(("PASS " if cond else "FAIL ") + name)
    if cond:
        _PASS += 1
    else:
        _FAIL += 1


def _sandbox():
    """Point backend's file constants at a fresh tempdir so tests never touch the
    live switchboard/ state. Returns the tmp Path."""
    tmp = Path(tempfile.mkdtemp(prefix="cockpit-test-"))
    backend.MANIFEST = tmp / "state-switchboard.json"
    backend.NAMES = tmp / "state-names.json"
    backend.STATE_NDJSON = tmp / "state.ndjson"
    backend.ROLE_FILES = {
        "dwarf": tmp / "state-dwarves.json",
        "gnome": tmp / "state-gnomes.json",
        "penguin": tmp / "state-penguins.json",
    }
    (tmp / "state-names.json").write_text("{}", encoding="utf-8")
    (tmp / "state.ndjson").write_text("", encoding="utf-8")
    return tmp


def _utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def test_pending_subagents_crashguard():
    """S083: a corrupt/truncated role file must never 500 /api/sessions."""
    tmp = _sandbox()
    # top-level list, non-dict bySession, non-dict byToolUseId — all malformed
    (tmp / "state-dwarves.json").write_text('["not a dict"]', encoding="utf-8")
    (tmp / "state-gnomes.json").write_text('{"bySession": "nope"}', encoding="utf-8")
    (tmp / "state-penguins.json").write_text(
        '{"bySession": {"S1": {"byToolUseId": "garbage"}}}', encoding="utf-8")
    try:
        out = backend._pending_subagents("S1")
        check("malformed role files -> no crash, empty list", out == [])
    except Exception as e:  # noqa: BLE001
        check(f"malformed role files -> no crash (raised {e!r})", False)

    # valid shape still resolves
    (tmp / "state-dwarves.json").write_text(
        json.dumps({"bySession": {"S1": {"byToolUseId": {"tu1": {"id": "D1"}}}}}),
        encoding="utf-8")
    out = backend._pending_subagents("S1")
    check("valid role file -> [dwarf D1]", out == [{"kind": "dwarf", "id": "D1"}])

    # missing/empty session id is a no-op
    check("no session id -> empty", backend._pending_subagents("") == [])


def test_stale_greying_and_attention():
    """S080: a quiet session keeps its real state (greyed), not flattened; it
    drops out of the attention tally; live ball-in-court states stay hot."""
    tmp = _sandbox()
    now = time.time()
    manifest = {"sessions": [
        {"sid8": "a0000000", "session_id": "S-a", "actor": "jebrim",
         "state": "busy", "last_event_ts": now - 5},
        {"sid8": "b0000000", "session_id": "S-b", "actor": "zezima",
         "state": "your_move", "last_event_ts": now - 10},
        {"sid8": "c0000000", "session_id": "S-c", "actor": "guthix",
         "state": "your_move", "last_event_ts": now - 9000},   # 2.5h quiet -> stale
        {"sid8": "d0000000", "session_id": "S-d", "actor": "braindead",
         "state": "needs_you", "last_event_ts": now - 3},
    ]}
    backend.MANIFEST.write_text(json.dumps(manifest), encoding="utf-8")
    m = backend.build_session_model()
    by = {s["sid8"]: s for s in m["sessions"]}

    check("live your_move is attention", by["b0000000"]["attention"] is True)
    check("live needs_you is attention", by["d0000000"]["attention"] is True)
    check("stale your_move is NOT attention", by["c0000000"]["attention"] is False)
    check("stale flag set on the 2.5h-quiet row", by["c0000000"]["stale"] is True)
    check("live busy is NOT stale", by["a0000000"]["stale"] is False)
    check("stale row keeps real state (your_move, not flattened)",
          by["c0000000"]["state"] == "your_move")

    att = sum(1 for s in m["sessions"] if s["attention"])
    check("attention tally = 2 (live needs_you + live your_move; stale excluded)",
          att == 2)

    order = [s["sid8"] for s in m["sessions"]]
    check("needs_you sorts to the top", order[0] == "d0000000")
    check("live your_move ranks above live busy",
          order.index("b0000000") < order.index("a0000000"))
    check("stale row sinks below live busy",
          order.index("c0000000") > order.index("a0000000"))


def test_legacy_token_aliasing():
    """D-029: a session still carrying a pre-vocabulary token renders through the
    transition via LEGACY_STATE."""
    tmp = _sandbox()
    now = time.time()
    cases = {
        "working": "busy", "waiting_for_user": "your_move",
        "waiting_for_answers": "needs_you", "waiting_for_subagents": "busy",
        "alching": "busy", "wrapped_up": "done", "closing": "done",
    }
    sessions = [{"sid8": f"{i:08x}", "session_id": f"S{i}", "actor": "x",
                 "state": old, "last_event_ts": now - 2}
                for i, old in enumerate(cases)]
    backend.MANIFEST.write_text(json.dumps({"sessions": sessions}), encoding="utf-8")
    m = backend.build_session_model()
    got = {s["session_id"]: s["state"] for s in m["sessions"]}
    for i, (old, new) in enumerate(cases.items()):
        check(f"legacy '{old}' -> '{new}'", got[f"S{i}"] == new)


def test_action_heartbeat():
    """D-029: a busy session with a fresh action in state.ndjson reads low quiet
    even when its last hook fire is older — the heartbeat keeps it alive."""
    tmp = _sandbox()
    now = time.time()
    # sid8 MUST equal session_id[:8] — that's the join key between the manifest row
    # and the action stream (backend keys the heartbeat map on sessionId[:8]).
    sid_full = "a0000000-0000-0000-0000-000000000000"
    backend.MANIFEST.write_text(json.dumps({"sessions": [
        {"sid8": "a0000000", "session_id": sid_full, "actor": "jebrim",
         "state": "busy", "last_event_ts": now - 200},   # last hook fire 200s ago
    ]}), encoding="utf-8")
    # NOTE: compact separators, matching emit-event.py (json.dumps(..., separators=
    # (",", ":"))). backend._last_action_ts_map fast-path-filters on the literal
    # substring '"type":"action"' (no space) — so the heartbeat SILENTLY breaks if
    # emit-event ever pretty-prints. This line pins the real on-disk format.
    backend.STATE_NDJSON.write_text(json.dumps({
        "type": "action", "sessionId": sid_full, "wallTime": _utc_now_iso(),
    }, separators=(",", ":")) + "\n", encoding="utf-8")
    m = backend.build_session_model()
    a = m["sessions"][0]
    check("fresh action heartbeat -> quiet_sec < 60", a["quiet_sec"] < 60)
    check("busy + fresh heartbeat is NOT stale", a["stale"] is False)


def test_robust_to_missing_and_malformed():
    """build_session_model must degrade gracefully, never raise."""
    tmp = _sandbox()
    # no manifest file at all
    if backend.MANIFEST.exists():
        backend.MANIFEST.unlink()
    try:
        m = backend.build_session_model()
        check("missing manifest -> empty model", m["sessions"] == [])
    except Exception as e:  # noqa: BLE001
        check(f"missing manifest -> no crash (raised {e!r})", False)

    # garbage manifest
    backend.MANIFEST.write_text("{ not json", encoding="utf-8")
    try:
        m = backend.build_session_model()
        check("garbage manifest -> empty model", m["sessions"] == [])
    except Exception as e:  # noqa: BLE001
        check(f"garbage manifest -> no crash (raised {e!r})", False)

    # a session row missing most fields
    backend.MANIFEST.write_text(json.dumps({"sessions": [{"sid8": "a0000000"}]}),
                                encoding="utf-8")
    try:
        m = backend.build_session_model()
        s = m["sessions"][0]
        check("sparse row -> defaults applied (actor unknown)", s["actor"] == "unknown")
        check("sparse row -> tags default []", s["tags"] == [])
    except Exception as e:  # noqa: BLE001
        check(f"sparse row -> no crash (raised {e!r})", False)


def test_busy_stays_busy_when_quiet():
    """S083 REGRESSION GUARD (the Jebrim bug): a genuinely-working session that
    goes hook/action-silent — long thinking, a long single tool/MCP query, writing
    a long response — must STAY busy, never flip to idle. An earlier timeout-decay
    (BUSY_IDLE_AFTER_SEC=90) false-tripped real work and was REMOVED: there's no
    server-side way to tell 'cancelled' from 'quietly working'. The cancel case is
    handled cockpit-side via the Esc keystroke, not here. A quiet busy session only
    greys (keeps the BUSY chip) past IDLE_AFTER_SEC — never relabels to idle."""
    tmp = _sandbox()
    now = time.time()
    backend.MANIFEST.write_text(json.dumps({"sessions": [
        {"sid8": "f0000000", "session_id": "f0000000-0000-0000-0000-000000000000",
         "actor": "jebrim", "state": "busy", "last_event_ts": now - 5},     # fresh
        {"sid8": "f1000000", "session_id": "f1000000-0000-0000-0000-000000000000",
         "actor": "jebrim", "state": "busy", "last_event_ts": now - 200},   # 200s silent (long query/think)
        {"sid8": "f2000000", "session_id": "f2000000-0000-0000-0000-000000000000",
         "actor": "jebrim", "state": "busy", "last_event_ts": now - 9000},  # 2.5h quiet
    ]}), encoding="utf-8")
    m = backend.build_session_model()
    by = {s["sid8"]: s for s in m["sessions"]}

    check("fresh busy stays busy", by["f0000000"]["state"] == "busy")
    check("200s-silent busy STILL busy (no false idle — the Jebrim regression)", by["f1000000"]["state"] == "busy")
    check("200s-silent busy not yet greyed (<300s)", by["f1000000"]["stale"] is False)
    check("2.5h-quiet busy still BUSY (greyed, not relabelled)", by["f2000000"]["state"] == "busy")
    check("2.5h-quiet busy is greyed (stale)", by["f2000000"]["stale"] is True)


async def _pty_auth_checks():
    """S085: /pty must be unforgeable from a cross-origin page. The token is the
    primary gate (fail-closed); the Origin check is defense-in-depth. None of the
    rejection paths reach the winpty import or spawn a PTY (they return before the
    WS upgrade), so this is safe to run headless."""
    from aiohttp.test_utils import TestClient, TestServer

    app = backend.make_app()
    token = app["cockpit_token"]
    check("make_app mints a non-empty token", isinstance(token, str) and len(token) >= 16)

    async with TestClient(TestServer(app)) as client:
        r = await client.get("/")
        body = await r.text()
        check("index.html injects window.__CT", "window.__CT" in body)
        check("injected HTML carries the make_app token", token in body)

        r = await client.get("/pty?launch=claude&cols=80&rows=24")
        check("/pty without a token -> 403 (fail-closed)", r.status == 403)

        r = await client.get("/pty?launch=evil-payload&token=" + token)
        # even WITH a token, an unknown launch must not be an arbitrary command —
        # the handler only honors launch=claude / resume=<uuid>. (Can't assert the
        # PTY contents here; the code path simply has no raw-passthrough branch.)
        check("/pty with valid token -> not 403 (auth passed)", r.status != 403)

        r = await client.get("/pty?launch=claude&token=" + token,
                             headers={"Origin": "https://evil.example"})
        check("/pty with a foreign Origin -> 403", r.status == 403)

        r = await client.get("/pty?launch=claude&token=wrong")
        check("/pty with a wrong token -> 403", r.status == 403)

        # Ctrl+C copy bridge (S087). Empty text hits the no-clobber guard before
        # _write_clipboard_text, so this asserts the route is wired without ever
        # touching the real clipboard during the test run.
        r = await client.post("/api/clipboard", json={"text": ""})
        check("POST /api/clipboard registered; empty text -> ok:False (no clobber)",
              r.status == 200 and (await r.json()).get("ok") is False)


def test_pty_auth():
    asyncio.run(_pty_auth_checks())


def test_result_cap():
    """The clean-text transcript panel passes &full=1 for untruncated tool output
    (a truncated copy is a broken copy). _result_text honours an explicit cap; the
    default stays the tight bound; FULL is generous enough to carry a real result
    whole. Guards the S091 copy-fidelity path."""
    big = "x" * 50_000
    default = backend._result_text(big)
    check("default cap truncates (<= HISTORY_RESULT_CAP + marker)",
          default.endswith("…(truncated)") and len(default) < backend.HISTORY_RESULT_CAP + 40)
    full = backend._result_text(big, backend.HISTORY_RESULT_CAP_FULL)
    check("full cap returns the result whole (no truncation)",
          full == big and "…(truncated)" not in full)
    check("FULL cap is materially larger than the default",
          backend.HISTORY_RESULT_CAP_FULL > backend.HISTORY_RESULT_CAP)
    # parse_transcript threads the cap down to the tool_result fill.
    small = backend._result_text(big, 100)
    check("explicit small cap shears at the requested length",
          small.startswith("x" * 100) and small.endswith("…(truncated)"))


def test_name_carry():
    """ptybridge._carry_disk_name moves a board label old sid8 → new sid8 across a
    session-id rotation (the "lost rename on reopen" fix): carries when the old has
    a label and the new doesn't; never clobbers an existing new label; no-ops on a
    missing source. Guards the disk half of the carry."""
    import ptybridge
    tmp = Path(tempfile.mkdtemp(prefix="cockpit-names-"))
    ptybridge.NAMES_PATH = tmp / "state-names.json"
    ptybridge.NAMES_PATH.write_text(json.dumps({"aaaaaaaa": "My Session"}), encoding="utf-8")
    ptybridge._carry_disk_name("aaaaaaaa", "bbbbbbbb")
    after = json.loads(ptybridge.NAMES_PATH.read_text(encoding="utf-8"))
    check("rename carried old sid8 -> new sid8 across rotation", after.get("bbbbbbbb") == "My Session")
    check("original label left intact (never destroy)", after.get("aaaaaaaa") == "My Session")
    # Never clobber a label already on the new sid8.
    ptybridge.NAMES_PATH.write_text(json.dumps({"aaaaaaaa": "Old", "cccccccc": "Fresh"}), encoding="utf-8")
    ptybridge._carry_disk_name("aaaaaaaa", "cccccccc")
    after2 = json.loads(ptybridge.NAMES_PATH.read_text(encoding="utf-8"))
    check("existing new-sid8 label not clobbered by carry", after2.get("cccccccc") == "Fresh")
    # No source label → no-op, no crash.
    ptybridge.NAMES_PATH.write_text(json.dumps({}), encoding="utf-8")
    ptybridge._carry_disk_name("dddddddd", "eeeeeeee")
    after3 = json.loads(ptybridge.NAMES_PATH.read_text(encoding="utf-8"))
    check("no source label -> no carry, no crash", "eeeeeeee" not in after3)


def main():
    test_name_carry()
    test_pending_subagents_crashguard()
    test_stale_greying_and_attention()
    test_legacy_token_aliasing()
    test_action_heartbeat()
    test_busy_stays_busy_when_quiet()
    test_robust_to_missing_and_malformed()
    test_pty_auth()
    test_result_cap()
    print(f"\n{_PASS} passed, {_FAIL} failed")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
