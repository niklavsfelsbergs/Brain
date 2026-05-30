#!/usr/bin/env python3
"""
comms_append.py — atomic, locked append to a comms/active.md log (S127 plan.md
section R.1).

WHY THIS EXISTS
---------------
The comms logs are "append-only," and both comms/_about.md files long claimed
that appends were safe because they use `open(path, "a")`. That premise was a
fiction: nothing in the brain actually appended that way. The agent posted
comms entries by READING the file and REWRITING it (the Edit tool rewriting
around the last entry, or the Write tool rewriting the whole file). Both are
read-modify-write:

  * two sessions read the same N lines, both write N+their-entry -> the second
    clobbers the first (lost update);
  * a Write truncates-then-writes -> an interrupted/raced rewrite leaves the
    file short or EMPTY (the "truncated to zero" that fired live in S127).

This tool is the safe path: an exclusive cross-process lock around a true
append. Concurrent callers serialize; no lost updates, no truncation. The
companion guard hook (gielinor/.claude/hooks/comms-append-guard.py) blocks raw
Edit/Write of comms/active.md so this becomes the only way in.

USAGE
-----
  py tools/comms_append.py --vault dev --entry "[ts] braindead-xxxx OPEN
    Targets: ..."
  printf '%s' "$ENTRY" | py tools/comms_append.py --vault gielinor
  py tools/comms_append.py --file path/to/comms/active.md --entry "..."

Vault auto-detects from CWD when --vault/--file are omitted. The entry is the
full multi-line block (header line + indented body); the tool handles blank-line
separation against whatever the file currently ends with.

EXIT CODES
----------
  0  appended OK
  1  usage / lock-timeout / write error (message on stderr)
"""
import argparse
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULTS = {"dev": "developer-braindead", "gielinor": "gielinor"}
LOCK_TIMEOUT = 10.0  # seconds to wait for the lock before giving up


class _FileLock:
    """Exclusive cross-process advisory lock on a sidecar lockfile.

    msvcrt on Windows, fcntl on POSIX. Blocking with a timeout; raises
    TimeoutError if the lock can't be taken in time (caller turns that into a
    clean exit 1 rather than a silent overwrite).
    """

    def __init__(self, target_path, timeout=LOCK_TIMEOUT):
        self.lockpath = target_path + ".lock"
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
                        f"could not acquire {self.lockpath} within {self.timeout}s"
                    )
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


def _resolve_path(args):
    if args.file:
        return os.path.abspath(args.file)
    vault = args.vault
    if not vault:
        # Auto-detect from CWD: which vault does the working dir sit inside?
        cwd = os.path.abspath(os.getcwd()).replace("\\", "/")
        if "/developer-braindead" in cwd or cwd.endswith("developer-braindead"):
            vault = "dev"
        elif "/gielinor" in cwd or cwd.endswith("gielinor"):
            vault = "gielinor"
    if vault not in VAULTS:
        return None
    return os.path.join(REPO, VAULTS[vault], "comms", "active.md")


def _leading_newlines(path):
    """How many newlines to put before the new entry so there is exactly one
    blank line between the prior entry and this one."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return ""
    with open(path, "rb") as f:
        f.seek(-2, os.SEEK_END) if os.path.getsize(path) >= 2 else f.seek(0)
        tail = f.read()
    if tail.endswith(b"\n\n"):
        return ""
    if tail.endswith(b"\n"):
        return "\n"
    return "\n\n"


def append_entry(path, entry):
    """Atomic locked append. Returns None on success, an error string on failure."""
    entry = entry.rstrip("\n") + "\n"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with _FileLock(path):
            lead = _leading_newlines(path)
            with open(path, "a", encoding="utf-8") as f:
                f.write(lead + entry)
                f.flush()
                os.fsync(f.fileno())
        return None
    except TimeoutError as e:
        return f"lock timeout: {e}"
    except Exception as e:
        return f"append failed: {e}"


def main():
    ap = argparse.ArgumentParser(description="Atomic locked append to comms/active.md")
    ap.add_argument("--vault", choices=list(VAULTS), help="dev | gielinor (auto-detect from CWD if omitted)")
    ap.add_argument("--file", help="explicit path to a comms/active.md (overrides --vault)")
    ap.add_argument("--entry", help="entry text (full block); read from stdin if omitted")
    args = ap.parse_args()

    path = _resolve_path(args)
    if not path:
        sys.stderr.write(
            "comms_append: could not resolve target. Pass --vault dev|gielinor "
            "or --file PATH (CWD is not inside a vault).\n"
        )
        sys.exit(1)

    entry = args.entry if args.entry is not None else sys.stdin.read()
    if not entry or not entry.strip():
        sys.stderr.write("comms_append: empty entry; nothing to append.\n")
        sys.exit(1)

    err = append_entry(path, entry)
    if err:
        sys.stderr.write(f"comms_append: {err}\n")
        sys.exit(1)
    sys.stderr.write(f"comms_append: appended to {path}\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
