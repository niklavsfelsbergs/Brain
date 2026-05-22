# Bash echo + quoted Windows path = literal filename, not a write

**Anchor (S027, 2026-05-22).** Twice this session I tried to write the Jebrim intent sidecar using:

```bash
echo "Drafting shipping cost vocab" > "C:\Users\niklavs.felsbergs\Documents\GitHub\brain\.claude\intent\jebrim.txt"
```

Bash on Windows (git-bash / cygwin layer) did not resolve the quoted Windows-style path to a Win32 filesystem path. Instead, the colon got encoded as Unicode U+F03A (private-use area), backslashes were preserved, and the whole string became a single literal filename at the **current working directory** — landing as `CUsersniklavs.felsbergsDocumentsGitHubbrain.claudeintentjebrim.txt` at the brain root rather than as `.claude/intent/jebrim.txt`.

The intended visualizer sidecar was never written; the bubble didn't update. The stray file then sat at brain root and the delete attempt was correctly blocked by `block-deletes.py` (architectural guarantee). Principal had to clean it up outside Claude.

## The rule

When writing intent sidecars (or any small file at a Windows path) from this brain's working directory, **do not use Bash `echo > "C:\..."`**. Use one of:

- **Write tool** with the absolute path as `file_path`. Cleanest — the harness handles the path correctly.
- **PowerShell** `Set-Content -LiteralPath "C:\..." -Value "..."` or `"text" | Out-File -LiteralPath "C:\..." -Encoding utf8`.

The pattern that *does* work in Bash on this machine is forward-slash + lowercase drive: `echo "x" > "/c/Users/.../intent/jebrim.txt"`. But it's quietly different from PowerShell semantics and easy to get wrong; the Write tool is the safer default.

## Why this drafted as examine vs reference

It's a self-observation about how I operate (tool selection, not knowledge about a thing). The CLAUDE.md preamble already says "Shell: PowerShell — Bash is also available via the Bash tool for POSIX scripts." The lesson is that "available" ≠ "preferred for Windows paths" — Bash should be reserved for genuinely POSIX-shape work, and file writes to Windows paths should go through Write or PowerShell.

Promote on next examine review.
