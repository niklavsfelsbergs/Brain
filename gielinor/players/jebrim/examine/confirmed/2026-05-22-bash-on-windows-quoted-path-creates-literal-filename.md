# Bash on Windows: quoted Windows path = literal filename

## Before / after

**Before (S027):** tried to write an intent sidecar with

    echo "..." > "C:\Users\.../intent/jebrim.txt"

Bash didn't resolve the quoted Windows path. The colon got encoded as Unicode U+F03A, backslashes were preserved, and the whole string became a single literal filename at the current working directory — landing as `CUsersniklavs.felsbergs...intentjebrim.txt` at brain root instead of `.claude/intent/jebrim.txt`. The intent file never updated; principal had to clean up outside Claude.

**After:** for any file write to a Windows path, use **Write** (clean — harness handles the path) or **PowerShell** (`Set-Content -LiteralPath "C:\..." -Value "..."`). Bash stays for genuinely POSIX work.

## The rule

Don't use `echo > "C:\..."` in Bash. Available ≠ preferred — the CLAUDE.md says "Shell: PowerShell; Bash also available," and the Bash path has a Windows-specific failure mode.

## Anchor

S027, twice this session before the lesson stuck.
