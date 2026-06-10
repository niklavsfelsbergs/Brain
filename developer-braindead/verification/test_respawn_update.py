#!/usr/bin/env python
"""test_respawn_update.py — harness for tools/respawn_update.py (486d6682).

Exercises the real CLI as a subprocess on temp fixtures (no monkeypatching):
prepend+normalize+rotate transform, idempotence, prose-mention immunity,
single-line details, unterminated-details refusal, empty-stdin refusal, and a
real two-process concurrent prepend through the lock (the D-024 race).
"""

import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parents[2] / "tools" / "respawn_update.py"
PY = sys.executable

FIXTURE = """# respawn.md — dev brain entry point

> Read this first.
>
> **Discipline.** Keep it small.

**Last updated ([[S185_x|S185]] [old top; sid aaaaaaaa].)** 2026-06-09. Body of S185. Mentions `<details>` in prose to try to confuse the parser.

**Prior ([[S184_x|S184]] [older; sid bbbbbbbb].)** 2026-06-09. Body of S184.

<details><summary>Prior: [[S183_x|S183]] (det one)</summary>

**[[S183_x|S183]] body.** Stuff.

</details>

<details><summary>Prior: [[S182_x|S182]] (det two, single line)</summary>**[[S182_x|S182]] one-liner body.**</details>

<details><summary>Prior: [[S181_x|S181]] (det three)</summary>

**[[S181_x|S181]] body.** More stuff.

</details>

> **★ NEXT** tail blockquote stays.

**Recent sessions (full detail in `quest-log/`):** rollup paragraph stays in tail.

## Where we are

Tail prose stays byte-identical.
"""

NEW_BLOCK = "**Last updated ([[S186_x|S186]] [new top; sid cccccccc].)** 2026-06-10. Fresh close block."

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}  {detail}")


def run(args, stdin=None, cwd=None):
    return subprocess.run([PY, str(TOOL)] + args, input=stdin,
                          capture_output=True, text=True, cwd=cwd)


def make_files(tmp, text=FIXTURE):
    f = Path(tmp) / "respawn.md"
    a = Path(tmp) / "archive" / "respawn-history.md"
    f.write_text(text, encoding="utf-8", newline="")
    return f, a


def main():
    with tempfile.TemporaryDirectory() as tmp:
        f, a = make_files(tmp)
        r = run(["--prepend", "--file", str(f), "--archive", str(a)], stdin=NEW_BLOCK)
        out = f.read_text(encoding="utf-8")
        check("prepend exits 0", r.returncode == 0, r.stderr)
        check("new block is on top of the session region",
              out.find("S186") < out.find("S185") and "**Last updated ([[S186" in out)
        check("old Last updated relabeled to Prior", "**Prior ([[S185_x|S185]]" in out
              and out.count("**Last updated") == 1)
        check("old Prior wrapped into details",
              "<details><summary>Prior: [[S184_x|S184]]" in out)
        real_dets = sum(1 for ln in out.splitlines() if ln.strip().startswith("<details>"))
        check("rotation kept 2 details, evicted 2",
              real_dets == 2 and "S182" not in out and "S181" not in out,
              f"details={real_dets}")
        arch = a.read_text(encoding="utf-8")
        check("evicted blocks landed in archive verbatim",
              "S182_x|S182]] one-liner body" in arch and "[[S181_x|S181]] body." in arch)
        check("tail preserved", "★ NEXT" in out and "## Where we are" in out
              and "Tail prose stays byte-identical." in out
              and "rollup paragraph stays in tail" in out)
        check("header preserved", out.startswith("# respawn.md — dev brain entry point"))

        # idempotence: rotate-only on the result changes nothing
        before = out
        r2 = run(["--rotate", "--file", str(f), "--archive", str(a)])
        check("rotate-only on normalized file is a no-op",
              r2.returncode == 0 and f.read_text(encoding="utf-8") == before, r2.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        f, a = make_files(tmp, FIXTURE.replace("\n</details>\n\n> **★ NEXT**",
                                               "\n\n> **★ NEXT**", 1))
        # fixture now has an unterminated <details> (third det lost its closer)
        before = f.read_text(encoding="utf-8")
        r = run(["--rotate", "--file", str(f), "--archive", str(a)])
        check("unterminated details refused, exit 1", r.returncode == 1, r.stderr)
        check("file untouched on refusal", f.read_text(encoding="utf-8") == before)

    with tempfile.TemporaryDirectory() as tmp:
        f, a = make_files(tmp)
        r = run(["--prepend", "--file", str(f), "--archive", str(a)], stdin="")
        check("empty stdin refused", r.returncode == 1)
        r = run(["--prepend", "--file", str(f), "--archive", str(a)],
                stdin="not a Last updated block")
        check("non-'**Last updated' block refused, file untouched",
              r.returncode == 1 and f.read_text(encoding="utf-8") == FIXTURE)

    # stdin UTF-8: em-dashes/arrows piped through stdin must land verbatim
    # (Windows stdin defaults to cp1252 — the S186 first-firing mojibake bug)
    with tempfile.TemporaryDirectory() as tmp:
        f, a = make_files(tmp)
        utf8_block = "**Last updated ([[S187_x|S187]] [utf-8 — test; sid dddddddd].)** 2026-06-11. Em-dash — arrow → star ★ section §Z."
        r = subprocess.run([PY, str(TOOL), "--prepend", "--file", str(f),
                            "--archive", str(a)],
                           input=utf8_block.encode("utf-8"), capture_output=True)
        out = f.read_text(encoding="utf-8")
        check("utf-8 stdin lands verbatim (no mojibake)",
              r.returncode == 0 and "Em-dash — arrow → star ★ section §Z." in out
              and "â" not in out, r.stderr.decode("utf-8", "replace"))

    # concurrency: two real processes prepend at once; both blocks must survive
    with tempfile.TemporaryDirectory() as tmp:
        f, a = make_files(tmp)
        b1 = "**Last updated ([[S190_x|S190]] [racer one; sid 11111111].)** 2026-06-10. One."
        b2 = "**Last updated ([[S191_x|S191]] [racer two; sid 22222222].)** 2026-06-10. Two."
        p1 = subprocess.Popen([PY, str(TOOL), "--prepend", "--block", b1,
                               "--file", str(f), "--archive", str(a)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen([PY, str(TOOL), "--prepend", "--block", b2,
                               "--file", str(f), "--archive", str(a)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p1.wait(timeout=30)
        p2.wait(timeout=30)
        out = f.read_text(encoding="utf-8")
        check("concurrent prepends: both exit 0",
              p1.returncode == 0 and p2.returncode == 0,
              f"{p1.stderr.read()} {p2.stderr.read()}")
        check("concurrent prepends: NO lost update — both blocks present",
              "S190" in out and "S191" in out)
        check("concurrent prepends: exactly one Last updated, loser demoted",
              out.count("**Last updated") == 1)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
