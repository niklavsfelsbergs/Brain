import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "h", HERE / ".claude" / "hooks" / "emit-event.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cases = [
    ("Read",  {"file_path": "C:/x/y/respawn.md"}),
    ("Edit",  {"file_path": "/repo/index.html"}),
    ("Write", {"file_path": "foo.txt"}),
    ("Glob",  {"pattern": "**/*.py"}),
    ("Grep",  {"pattern": "instanceKey"}),
    ("Bash",  {"command": "git status"}),
    ("Bash",  {"command": "git diff HEAD~1"}),
    ("Bash",  {"command": "git add -p"}),
    ("Bash",  {"command": "git commit -m 'x'"}),
    ("Bash",  {"command": "git push origin main"}),
    ("Bash",  {"command": "git pull"}),
    ("Bash",  {"command": "ls -la"}),
    ("Bash",  {"command": "cat foo.txt"}),
    ("Bash",  {"command": "python -m pytest"}),
    ("Bash",  {"command": "gh pr list"}),
    ("Bash",  {"command": "echo hello > .claude/active-mode.txt"}),
    ("Bash",  {"command": "rsync foo bar"}),
    ("Task",  {"description": "audit subtree X", "subagent_type": "Explore"}),
    ("WebFetch", {"url": "https://docs.python.org/3/library/re.html"}),
    ("WebSearch",{"query": "claude code hooks"}),
    ("Unknown",  {}),
]
for t, args in cases:
    arg = args.get("command") or args.get("pattern") or args.get("file_path") or args.get("url") or args.get("query") or args.get("description") or ""
    print(f"{t:9} {arg[:42]:42} -> {mod.subtask_for(t, args)!r}")
