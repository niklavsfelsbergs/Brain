#!/usr/bin/env python3
"""Harness for hygiene-check.py (S187) — synthetic trees, no live state read.

Run: python developer-braindead/verification/test_hygiene_check.py
"""
import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hygiene_check", HERE / "hygiene-check.py")
hc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hc)

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def _mk_player(root: Path, name: str, n_inprog=0, n_stale=0, n_inv=0,
               now=None) -> None:
    now = now or time.time()
    ip = root / name / "quest-log" / "in-progress"
    ip.mkdir(parents=True, exist_ok=True)
    for i in range(n_inprog):
        (ip / f"S{i:03d}_fresh_{i}.md").write_text("x", encoding="utf-8")
    for i in range(n_stale):
        p = ip / f"S9{i:02d}_stale_{i}.md"
        p.write_text("x", encoding="utf-8")
        old = now - (hc.STALE_DAYS + 5) * 86400
        os.utime(p, (old, old))
    inv = root / name / "inventory"
    inv.mkdir(parents=True, exist_ok=True)
    for i in range(n_inv):
        (inv / f"resume-{i}.md").write_text("x", encoding="utf-8")


with tempfile.TemporaryDirectory() as td:
    root = Path(td)

    # 1. clean player — no flags
    _mk_player(root, "alice", n_inprog=3, n_inv=2)
    check("1 clean player -> no flags", hc.check_active_state(root) == [])

    # 2. over the in-progress cap
    _mk_player(root, "bob", n_inprog=hc.INPROGRESS_CAP + 5)
    flags = hc.check_active_state(root)
    check("2 over-cap in-progress flagged",
          any("bob" in f and "in-progress quest files" in f for f in flags))

    # 3. stale files individually flagged with age
    _mk_player(root, "carol", n_inprog=1, n_stale=2)
    flags = hc.check_active_state(root)
    check("3 stale in-progress flagged per file",
          sum(1 for f in flags if "carol" in f and "stale" in f) == 2)

    # 4. dwarf traces counted in the over-cap message
    ip = root / "bob" / "quest-log" / "in-progress"
    (ip / "trace__dwarf.md").write_text("x", encoding="utf-8")
    flags = hc.check_active_state(root)
    check("4 dwarf-trace count appears in over-cap flag",
          any("bob" in f and "1 dwarf traces" in f for f in flags))

    # 5. inventory over cap
    _mk_player(root, "dave", n_inv=hc.INVENTORY_CAP + 1)
    flags = hc.check_active_state(root)
    check("5 inventory over cap flagged",
          any("dave" in f and "inventory" in f for f in flags))

with tempfile.TemporaryDirectory() as td:
    sb = Path(td)

    # 6. empty switchboard — clean
    check("6 empty telemetry dir -> clean",
          hc.check_telemetry(sb, is_synthetic=lambda s: False) == [])

    # 7. ndjson over cap*headroom flagged; under it not
    big = sb / "state.ndjson"
    big.write_text("x" * int(hc.NDJSON_CAPS["state.ndjson"] * 1.3), encoding="utf-8")
    flags = hc.check_telemetry(sb, is_synthetic=lambda s: False)
    check("7a oversized state.ndjson flagged",
          any("state.ndjson" in f and "not holding" in f for f in flags))
    big.write_text("x" * int(hc.NDJSON_CAPS["state.ndjson"] * 1.1), encoding="utf-8")
    flags = hc.check_telemetry(sb, is_synthetic=lambda s: False)
    check("7b within headroom -> not flagged",
          not any("not holding" in f for f in flags))

    # 8. root *.log + tmp litter flagged
    (sb / "term-fit-diag.log").write_text("d", encoding="utf-8")
    (sb / "state.ndjson.tmp.123").write_text("t", encoding="utf-8")
    flags = hc.check_telemetry(sb, is_synthetic=lambda s: False)
    check("8 root log + tmp litter flagged",
          any("un-archived log" in f for f in flags)
          and any("litter" in f for f in flags))

    # 9. synthetic sids in ritual-events flagged via the injected matcher
    ev = sb / "ritual-events.ndjson"
    rows = [{"sid8": "aaaa1111", "hook": "x", "decision": "y"},
            {"sid8": "0a1b2c3d", "hook": "x", "decision": "y"}]
    ev.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    flags = hc.check_telemetry(sb, is_synthetic=lambda s: s == "aaaa1111")
    check("9 synthetic sid reappearance flagged (real sid not)",
          any("aaaa1111" in f for f in flags)
          and not any("0a1b2c3d" in f for f in flags))

    # 10. the real adherence-rates denylist loads and classifies
    is_syn = hc._load_synthetic_matcher()
    check("10 shared denylist: aaaa1111+zv_x synthetic, 76f2e60f real",
          is_syn("aaaa1111") and is_syn("zv_carri") and not is_syn("76f2e60f"))

with tempfile.TemporaryDirectory() as td:
    lb = Path(td)
    conf = lb / "confirmed"
    conf.mkdir(parents=True)

    # 11. confirmed + indexed in sync -> clean
    (conf / "D-017_user-only.md").write_text("x", encoding="utf-8")
    (conf / "D-024_pathspecs.md").write_text("x", encoding="utf-8")
    (lb / "_index.md").write_text(
        "# index\n\n## D-017 — user-only\n- rule: r\n\n## D-024 — pathspecs\n"
        "- patterns: commit\n- rule: r\n", encoding="utf-8")
    check("11 lorebook in-sync -> clean", hc.check_lorebook_index(lb) == [])

    # 12. confirmed-but-unindexed flagged; ghost entry flagged
    (conf / "D-035_new-decision.md").write_text("x", encoding="utf-8")
    (lb / "_index.md").write_text(
        "# index\n\n## D-017 — user-only\n- rule: r\n\n## D-024 — pathspecs\n"
        "- rule: r\n\n## D-099 — ghost\n- rule: r\n", encoding="utf-8")
    flags = hc.check_lorebook_index(lb)
    check("12a unindexed confirmed decision flagged",
          any("D-035" in f and "NOT in _index" in f for f in flags))
    check("12b ghost index entry flagged",
          any("D-099" in f and "ghost" in f for f in flags))

    # 13. missing index file -> single blind-arm flag
    (lb / "_index.md").unlink()
    flags = hc.check_lorebook_index(lb)
    check("13 missing index -> blind-arm flag",
          len(flags) == 1 and "blind" in flags[0])

# 14. the LIVE index covers the LIVE confirmed set (the real drift check)
check("14 live lorebook index in sync", hc.check_lorebook_index() == [])

fails = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(fails)}/{len(results)} passed"
      + (f"  FAILURES: {fails}" if fails else ""))
sys.exit(1 if fails else 0)
