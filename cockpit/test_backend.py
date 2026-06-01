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
    """S139: a quiet `your_move` keeps its main status (YOUR MOVE) and gains an
    `idle` sub-bubble — it does NOT relabel to a main IDLE chip (that was the
    short-lived S134 behaviour). It greys, drops out of the attention tally, and
    sinks in the sort; live ball-in-court states stay hot and on top."""
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
    check("idle your_move is NOT attention", by["c0000000"]["attention"] is False)
    check("stale flag set on the 2.5h-quiet row", by["c0000000"]["stale"] is True)
    check("live busy is NOT stale", by["a0000000"]["stale"] is False)
    # S139: a quiet your_move keeps main YOUR MOVE + gains an `idle` sub-bubble
    # (was, briefly in S134, a relabel to a main IDLE state).
    check("2.5h-quiet your_move keeps main your_move", by["c0000000"]["main"] == "your_move")
    check("2.5h-quiet your_move gains an idle sub-bubble", "idle" in by["c0000000"]["subs"])
    check("live needs_you main = needs_you (ACTION NEEDED)", by["d0000000"]["main"] == "needs_you")

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
    handled cockpit-side via the Esc keystroke, not here. A quiet busy session
    never greys or flips to idle; it keeps main BUSY, and only once its heartbeat
    freezes past the generous STALL_AFTER_SEC (15 min) does it gain a `stalled`
    sub-bubble (S139 — a sub-bubble, not a relabel of the main chip)."""
    tmp = _sandbox()
    now = time.time()
    backend.MANIFEST.write_text(json.dumps({"sessions": [
        {"sid8": "f0000000", "session_id": "f0000000-0000-0000-0000-000000000000",
         "actor": "jebrim", "state": "busy", "last_event_ts": now - 5},     # fresh
        {"sid8": "f1000000", "session_id": "f1000000-0000-0000-0000-000000000000",
         "actor": "jebrim", "state": "busy", "last_event_ts": now - 200},   # 200s silent (long query/think)
        {"sid8": "f2000000", "session_id": "f2000000-0000-0000-0000-000000000000",
         "actor": "jebrim", "state": "busy", "last_event_ts": now - 9000},  # 2.5h quiet
        # S141: a bg-task wait (hook flipped your_move->busy + `monitoring` tag) is
        # intentionally quiet — it must NOT escalate to stalled even past 15 min.
        {"sid8": "f3000000", "session_id": "f3000000-0000-0000-0000-000000000000",
         "actor": "braindead", "state": "busy", "tags": ["monitoring"], "last_event_ts": now - 9000},
    ]}), encoding="utf-8")
    m = backend.build_session_model()
    by = {s["sid8"]: s for s in m["sessions"]}

    check("fresh busy stays busy", by["f0000000"]["main"] == "busy")
    check("200s-silent busy STILL busy (no false idle — the Jebrim regression)", by["f1000000"]["main"] == "busy")
    check("200s-silent busy not yet stalled (<15min)", "stalled" not in by["f1000000"]["subs"])
    check("200s-silent busy never greyed", by["f1000000"]["stale"] is False)
    # S139: a busy row whose heartbeat froze past STALL_AFTER_SEC keeps main BUSY
    # and gains a `stalled` sub-bubble — never greyed, never relabelled.
    check("2.5h-quiet busy keeps main BUSY", by["f2000000"]["main"] == "busy")
    check("2.5h-quiet busy gains a stalled sub-bubble", "stalled" in by["f2000000"]["subs"])
    check("2.5h-quiet busy is NOT greyed (active)", by["f2000000"]["stale"] is False)
    # S141: a monitoring (bg-wait) row stays BUSY and never gains the stalled sub
    check("monitoring bg-wait stays main BUSY", by["f3000000"]["main"] == "busy")
    check("monitoring bg-wait NOT stalled despite 2.5h quiet", "stalled" not in by["f3000000"]["subs"])


def test_your_move_with_crew_is_busy():
    """S139: a session parked on a Stop (your_move) while a FOREGROUND subagent is
    still out is waiting on its crew, not the principal — the board must read it
    main BUSY, never YOUR MOVE. The crew shows via the kind-letter row
    (`subagents`), not a sub-bubble. (The hook stamps your_move when a Stop fires
    mid-spawn; the backend re-derives from the live pending list.)"""
    tmp = _sandbox()
    now = time.time()
    # a0: your_move with a dwarf still out -> must be busy; b0: plain your_move
    backend.MANIFEST.write_text(json.dumps({"sessions": [
        {"sid8": "a0000000", "session_id": "S-crew", "actor": "jebrim",
         "state": "your_move", "last_event_ts": now - 5},
        {"sid8": "b0000000", "session_id": "S-bare", "actor": "zezima",
         "state": "your_move", "last_event_ts": now - 5},
    ]}), encoding="utf-8")
    (tmp / "state-dwarves.json").write_text(
        json.dumps({"bySession": {"S-crew": {"byToolUseId": {"tu1": {"id": "D1"}}}}}),
        encoding="utf-8")
    m = backend.build_session_model()
    by = {s["sid8"]: s for s in m["sessions"]}

    check("your_move + pending crew -> main busy", by["a0000000"]["main"] == "busy")
    check("your_move + pending crew -> crew chip present", len(by["a0000000"]["subagents"]) == 1)
    check("your_move + pending crew is NOT ball-in-court attention", by["a0000000"]["attention"] is False)
    check("bare your_move (no crew) stays main your_move", by["b0000000"]["main"] == "your_move")
    check("bare your_move has no crew chip", len(by["b0000000"]["subagents"]) == 0)


def test_main_status_taxonomy():
    """S139: rituals (alching/bankstanding) promote to a MAIN chip; but a ball-state
    (ACTION NEEDED / YOUR MOVE) wins the chip and demotes the ritual to a sub-bubble.
    consultation/drafts are always sub-bubbles."""
    tmp = _sandbox()
    now = time.time()
    backend.MANIFEST.write_text(json.dumps({"sessions": [
        # busy + alching marker -> main ALCHING
        {"sid8": "a0000000", "session_id": "S-a", "actor": "jebrim",
         "state": "busy", "tags": ["alching"], "last_event_ts": now - 5},
        # busy + bankstanding -> main BANKSTANDING
        {"sid8": "b0000000", "session_id": "S-b", "actor": "guthix",
         "state": "busy", "tags": ["bankstanding"], "last_event_ts": now - 5},
        # parked alching -> ball-state wins: main YOUR MOVE, alching demoted to sub
        {"sid8": "c0000000", "session_id": "S-c", "actor": "jebrim",
         "state": "your_move", "tags": ["alching"], "last_event_ts": now - 5},
        # question during bankstanding -> main ACTION NEEDED, bankstanding sub
        {"sid8": "d0000000", "session_id": "S-d", "actor": "guthix",
         "state": "needs_you", "tags": ["bankstanding"], "last_event_ts": now - 5},
        # consultation is always a sub on a busy chip
        {"sid8": "e0000000", "session_id": "S-e", "actor": "guthix",
         "state": "busy", "tags": ["consultation"], "last_event_ts": now - 5},
        # S141 two-phase close. mid-wrap (closing tag) -> main WRAPPING UP
        {"sid8": "10000000", "session_id": "S-w1", "actor": "braindead",
         "state": "busy", "tags": ["closing"], "last_event_ts": now - 5},
        # close pauses for a commit nod -> ball-state wins, closing demoted to sub
        {"sid8": "11000000", "session_id": "S-w2", "actor": "braindead",
         "state": "your_move", "tags": ["closing"], "last_event_ts": now - 5},
        # finished (wrapped_up sets base state done) -> main WRAPPED UP
        {"sid8": "12000000", "session_id": "S-w3", "actor": "braindead",
         "state": "done", "tags": ["wrapped"], "last_event_ts": now - 5},
    ]}), encoding="utf-8")
    m = backend.build_session_model()
    by = {s["sid8"]: s for s in m["sessions"]}

    check("busy + alching -> main ALCHING", by["a0000000"]["main"] == "alching")
    check("busy + alching -> no demoted ritual sub", "alching" not in by["a0000000"]["subs"])
    check("busy + bankstanding -> main BANKSTANDING", by["b0000000"]["main"] == "bankstanding")
    check("parked alching -> ball-state wins (main YOUR MOVE)", by["c0000000"]["main"] == "your_move")
    check("parked alching -> ritual demoted to sub", "alching" in by["c0000000"]["subs"])
    check("question in bankstanding -> main ACTION NEEDED", by["d0000000"]["main"] == "needs_you")
    check("question in bankstanding -> ritual demoted to sub", "bankstanding" in by["d0000000"]["subs"])
    check("consultation is a sub on busy", by["e0000000"]["main"] == "busy" and "consultation" in by["e0000000"]["subs"])
    # S141 two-phase close: WRAPPING UP (mid-wrap) -> WRAPPED UP (done)
    check("mid-wrap (closing tag) -> main WRAPPING UP", by["10000000"]["main"] == "closing")
    check("closing-while-busy is NOT demoted to sub", "closing" not in by["10000000"]["subs"])
    check("close pauses on your_move -> ball-state wins", by["11000000"]["main"] == "your_move")
    check("paused close keeps wrap context as a sub", "closing" in by["11000000"]["subs"])
    check("wrapped_up -> main WRAPPED UP (done)", by["12000000"]["main"] == "done")


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
    test_your_move_with_crew_is_busy()
    test_main_status_taxonomy()
    test_robust_to_missing_and_malformed()
    test_pty_auth()
    test_result_cap()
    print(f"\n{_PASS} passed, {_FAIL} failed")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
