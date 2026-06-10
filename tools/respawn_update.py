#!/usr/bin/env python
"""respawn_update.py — locked prepend + normalize + rotate for the dev-brain
respawn.md (supersedes respawn_rotate.py, same session 486d6682).

WHY THIS EXISTS
---------------
respawn.md is the dev brain's baton: read once at entry, rewritten once at
close. Under parallel sessions the close used to be a RAW read-modify-write
guarded only by prose (the D-024 "prepend, don't overwrite" note) — the same
lost-update class comms/active.md had before the S128 append lock. And the
size discipline ("current state + the newest one or two pointers") was
hand-enforced and drifted twice (49k tokens at the 2026-05-24 trim, 62k by
2026-06-10). This tool closes both: every close-time write goes through ONE
locked, atomic transform —

  1. PREPEND the new `**Last updated ...**` block (stdin) above the old ones;
  2. NORMALIZE — the previous `**Last updated` paragraph is relabeled
     `**Prior`; any older bold paragraphs are wrapped into collapsed
     `<details>` blocks;
  3. ROTATE — all but the newest KEEP_DETAILS collapsed blocks are evicted,
     verbatim, to quest-log/archive/respawn-history.md (append-only; the
     archive is written and fsynced BEFORE respawn.md is rewritten — nothing
     is ever deleted).

The lock is the proven S128 primitive from comms_append.py (msvcrt/fcntl on a
sidecar .lock file). Concurrent closes serialize; the loser of the race
prepends onto the winner's fresh state instead of clobbering it.

PARSING (line-anchored, prose-proof)
------------------------------------
The file is header -> session blocks -> tail. A session block is either a
bold paragraph whose first line matches `**Last updated (` / `**Prior (`, or
a `<details>` block that OPENS on a line starting `<details>` and CLOSES on a
line ending `</details>` (single-line blocks OK). Body prose that *mentions*
`<details>` mid-line (S142 does) cannot confuse it. `**Prior sessions ...`
rollup paragraphs do NOT match (no `(` after the label) — they belong to the
tail, which is preserved verbatim, as is the header.

USAGE
-----
  printf '%s' "$BLOCK" | py tools/respawn_update.py --prepend   # close step 3
  py tools/respawn_update.py --rotate                            # tidy only
  py tools/respawn_update.py --rotate --check                    # dry-run

EXIT CODES
----------
  0 OK · 1 usage/lock-timeout/bad-input (file untouched on every error)
"""

import argparse
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent
RESPAWN = BRAIN_ROOT / "developer-braindead" / "respawn.md"
ARCHIVE = BRAIN_ROOT / "developer-braindead" / "quest-log" / "archive" / "respawn-history.md"
KEEP_DETAILS = 2
LOCK_TIMEOUT = 10.0

BLOCK_HEAD_RE = re.compile(r"^\*\*(Last updated|Prior)\s*\(")

ARCHIVE_HEADER = """# respawn-history — blocks rotated out of respawn.md

> Append-only. `tools/respawn_update.py` moves the oldest collapsed
> `<details>` session blocks here at session close (discipline: current
> state + the most recent one or two pointers stay in respawn.md).
> Full session narratives live in the sibling `quest-log/SNNN_*.md` files;
> these are the respawn-era summary rollups, preserved verbatim.
"""


class _FileLock:
    """Exclusive cross-process lock on a sidecar lockfile (comms_append S128).
    msvcrt on Windows, fcntl on POSIX; blocking with timeout."""

    def __init__(self, target_path, timeout=LOCK_TIMEOUT):
        self.lockpath = str(target_path) + ".lock"
        self.timeout = timeout
        self.fh = None

    def __enter__(self):
        self.fh = open(self.lockpath, "a+")
        deadline = time.time() + self.timeout
        while True:
            try:
                self._acquire()
                return self
            except OSError:
                if time.time() >= deadline:
                    raise TimeoutError(
                        f"could not acquire {self.lockpath} within {self.timeout}s")
                time.sleep(0.05)

    def _acquire(self):
        self.fh.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(self.fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def __exit__(self, *exc):
        try:
            self.fh.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            self.fh.close()
        except Exception:
            pass


def parse(text):
    """Split into (header_lines, blocks, tail_lines).

    blocks: list of {"kind": "para"|"details", "lines": [...]} in file order.
    Raises ValueError on an unterminated <details> (caller leaves file alone).
    """
    lines = text.splitlines()
    first = None
    for i, ln in enumerate(lines):
        if BLOCK_HEAD_RE.match(ln):
            first = i
            break
    if first is None:
        return lines, [], []

    header = lines[:first]
    blocks = []
    i = first
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if s == "":
            i += 1
            continue
        if BLOCK_HEAD_RE.match(lines[i]):
            j = i
            while j < n and lines[j].strip() != "":
                j += 1
            blocks.append({"kind": "para", "lines": lines[i:j]})
            i = j
        elif s.startswith("<details>"):
            if s.endswith("</details>"):           # single-line block
                blocks.append({"kind": "details", "lines": [lines[i]]})
                i += 1
            else:
                j = i + 1
                while j < n and not lines[j].strip().endswith("</details>"):
                    j += 1
                if j >= n:
                    raise ValueError(
                        f"unterminated <details> opened at line {i + 1}")
                blocks.append({"kind": "details", "lines": lines[i:j + 1]})
                i = j + 1
        else:
            break  # tail starts here
    tail = lines[i:]
    return header, blocks, tail


def _relabel_to_prior(para_lines):
    out = list(para_lines)
    out[0] = "**Prior" + out[0][len("**Last updated"):] \
        if out[0].startswith("**Last updated") else out[0]
    return out


def _summary_for(para_lines):
    """Derive a <summary> label from a bold block's first line."""
    head = para_lines[0]
    m = re.match(r"^\*\*(?:Last updated|Prior)\s*\((.*?)\.?\)\*\*", head)
    if m:
        return "Prior: " + m.group(1).strip()
    return "Prior: " + head.lstrip("*").strip()[:110]


def _wrap_details(para_lines):
    return (["<details><summary>" + _summary_for(para_lines) + "</summary>", ""]
            + list(para_lines) + ["", "</details>"])


def normalize(blocks, new_block_lines=None):
    """Apply the prepend (optional) + positional discipline.

    Paragraph #1 stays `Last updated`, #2 becomes `Prior`, #3+ get wrapped
    into <details>. Details blocks pass through (rotation handles their count).
    """
    seq = ([{"kind": "para", "lines": new_block_lines}] if new_block_lines else []) + blocks
    out, para_seen = [], 0
    for b in seq:
        if b["kind"] == "para":
            para_seen += 1
            if para_seen == 1:
                out.append(b)
            elif para_seen == 2:
                out.append({"kind": "para", "lines": _relabel_to_prior(b["lines"])})
            else:
                out.append({"kind": "details", "lines": _wrap_details(b["lines"])})
        else:
            out.append(b)
    return out


def rotate(blocks, keep=KEEP_DETAILS):
    """Keep the first `keep` details blocks; return (kept_blocks, evicted_texts)."""
    kept, evicted, seen = [], [], 0
    for b in blocks:
        if b["kind"] == "details":
            seen += 1
            if seen > keep:
                evicted.append("\n".join(b["lines"]))
                continue
        kept.append(b)
    return kept, evicted


def assemble(header, blocks, tail):
    parts = []
    if header:
        parts.append("\n".join(header).rstrip("\n"))
    for b in blocks:
        parts.append("\n".join(b["lines"]))
    if tail:
        parts.append("\n".join(tail).rstrip("\n"))
    return "\n\n".join(parts) + "\n"


def _write_atomic(path: Path, data: str):
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(data, encoding="utf-8", newline="")
    try:
        with open(tmp, "r+b") as f:
            f.flush()
            os.fsync(f.fileno())
    except OSError:
        pass
    os.replace(tmp, path)


def _archive_evicted(archive: Path, evicted):
    stamp = f"\n---\n\n## Rotated {date.today().isoformat()} — {len(evicted)} block(s)\n\n"
    body = stamp + "\n\n".join(evicted) + "\n"
    if archive.exists():
        with archive.open("a", encoding="utf-8", newline="") as f:
            f.write(body)
            f.flush()
            os.fsync(f.fileno())
    else:
        archive.parent.mkdir(parents=True, exist_ok=True)
        with archive.open("w", encoding="utf-8", newline="") as f:
            f.write(ARCHIVE_HEADER + body)
            f.flush()
            os.fsync(f.fileno())


def update(respawn: Path, archive: Path, new_block: str | None,
           keep=KEEP_DETAILS, check=False) -> str:
    """The whole transform under one lock. Returns a human report string."""
    with _FileLock(respawn):
        text = respawn.read_text(encoding="utf-8")
        header, blocks, tail = parse(text)  # ValueError propagates: file untouched
        new_lines = None
        if new_block is not None:
            nb = new_block.strip("\n")
            if not nb.startswith("**Last updated"):
                raise ValueError("the prepend block must start with '**Last updated'")
            new_lines = nb.splitlines()
        blocks = normalize(blocks, new_lines)
        blocks, evicted = rotate(blocks, keep)
        new_text = assemble(header, blocks, tail)
        report = (f"respawn.md: {len(text.encode('utf-8')) / 1024:.0f} KB -> "
                  f"{len(new_text.encode('utf-8')) / 1024:.0f} KB; "
                  f"{'prepended 1 block; ' if new_lines else ''}"
                  f"evicted {len(evicted)} block(s)")
        if check:
            return report + " [--check, no writes]"
        if evicted:
            _archive_evicted(archive, evicted)  # archive lands BEFORE the rewrite
        if new_text != text:
            _write_atomic(respawn, new_text)
        return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Locked prepend/normalize/rotate for respawn.md")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepend", action="store_true",
                      help="read the new '**Last updated ...' block from stdin (or --block)")
    mode.add_argument("--rotate", action="store_true",
                      help="normalize + rotate only, no new block")
    ap.add_argument("--block", help="prepend block text (stdin if omitted)")
    ap.add_argument("--keep", type=int, default=KEEP_DETAILS,
                    help=f"collapsed blocks to keep (default {KEEP_DETAILS})")
    ap.add_argument("--check", action="store_true", help="dry-run, no writes")
    ap.add_argument("--file", help="override respawn.md path (tests)")
    ap.add_argument("--archive", help="override archive path (tests)")
    args = ap.parse_args()

    respawn = Path(args.file) if args.file else RESPAWN
    archive = Path(args.archive) if args.archive else ARCHIVE

    new_block = None
    if args.prepend:
        if args.block is None:
            # Windows stdin defaults to the console codepage (cp1252) — piped
            # UTF-8 mojibakes silently (caught live on this tool's FIRST real
            # firing, S186; same class as D-023). Force UTF-8.
            try:
                sys.stdin.reconfigure(encoding="utf-8")
            except Exception:
                pass
        new_block = args.block if args.block is not None else sys.stdin.read()
        if not new_block or not new_block.strip():
            sys.stderr.write("respawn_update: empty prepend block.\n")
            return 1

    try:
        report = update(respawn, archive, new_block, keep=args.keep, check=args.check)
    except TimeoutError as e:
        sys.stderr.write(f"respawn_update: lock timeout: {e}\n")
        return 1
    except ValueError as e:
        sys.stderr.write(f"respawn_update: {e} — file untouched.\n")
        return 1
    print(f"respawn_update: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
