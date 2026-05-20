#!/usr/bin/env python3
# Architectural guarantee #2: nothing is destroyed; move to archive/ instead.
# Fires PreToolUse on Bash/PowerShell. Scans the command for delete patterns.
# Blocks broadly — running Claude Code inside gielinor/ means delete intent
# is wrong. Use moves to archive/ instead. See meta/archive-discipline.md.

import json
import re
import sys

DELETE_PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9_-])rm(?:\s+-[A-Za-z]+)*\s", re.IGNORECASE),
    re.compile(r"\bremove-item\b", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_-])del\s", re.IGNORECASE),
    re.compile(r"\berase\s", re.IGNORECASE),
    re.compile(r"\bunlink\s", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_-])ri\s+-", re.IGNORECASE),  # PS alias
    re.compile(r"\brmdir\s", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_-])rd\s+-", re.IGNORECASE),
    re.compile(r"\.unlink\(", re.IGNORECASE),
    re.compile(r"shutil\.rmtree\(", re.IGNORECASE),
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"block-deletes: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Bash", "PowerShell"):
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    for pat in DELETE_PATTERNS:
        if pat.search(command):
            print(
                f"BLOCKED: delete operations are disallowed inside the brain.\n"
                f"  Matched pattern: {pat.pattern!r}\n"
                f"  Command: {command[:200]}\n"
                f"  Use a move into the corresponding archive/ instead.\n"
                f"  See meta/archive-discipline.md.",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
