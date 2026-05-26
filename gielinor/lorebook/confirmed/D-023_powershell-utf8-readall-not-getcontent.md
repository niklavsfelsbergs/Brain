# 2026-05-22 — PowerShell snippets that round-trip file content must use `[System.IO.File]::ReadAllText`, never `Get-Content -Raw`

## What changed

A behavioral rule for the agent when authoring PowerShell snippets that read-modify-write text files on Windows:

- **Forbidden:** `Get-Content -Raw` → modify → `Set-Content` / `[System.IO.File]::WriteAllText`. PowerShell 5.1's `Get-Content` defaults to the system locale encoding (Windows-1252 on en-US Windows). UTF-8 multi-byte characters (em-dashes, smart quotes, arrows, non-ASCII letters) are decoded as 1252 garbage on read, mojibake'd in memory, and re-encoded as UTF-8 on write — producing visible damage like `—` → `â€"`.
- **Required:** `[System.IO.File]::ReadAllText($path)` → modify → `[System.IO.File]::WriteAllText($path, $content)`. The .NET methods autodetect BOM and default to UTF-8 (no BOM) on both sides. Round-trip is encoding-safe.

This applies to *any* find-and-replace, content rewriting, or bulk-edit snippet the agent gives the principal to paste into PowerShell — not only `meta/` patches, not only bankstanding work.

## Why

The footgun is invisible at snippet-authoring time. PowerShell shows no warning. The script reports success. The damage is only visible by inspecting bytes (e.g., `od -c`) or by displaying the file in a UTF-8-aware viewer. A round-trip that touches one ASCII line corrupts every other line in the file silently.

The agent reaches for `Get-Content -Raw` because it's the documented PowerShell idiom for whole-file reads. The PowerShell 5.1 default-encoding behavior is a known wart but is not the first thing surfaced in PowerShell tutorials, examples, or AI-training corpora. Without the explicit rule, the agent will hit this footgun again.

## What triggered it

Concrete moment: bankstanding [[B-001_2026-05-22_first-bankstanding|B-001]], 2026-05-22, the `meta/` lorebook-folder-naming-correction patch.

The agent gave the principal this one-liner:

```powershell
Get-ChildItem gielinor/meta/*.md -File | ForEach-Object {
  $c=Get-Content $_.FullName -Raw
  $n=$c -replace 'lorebook/decisions/','lorebook/confirmed/'
  if($c -ne $n){ [System.IO.File]::WriteAllText($_.FullName, $n) }
}
```

It ran on all 6 meta files. The `lorebook/decisions/` → `lorebook/confirmed/` replacement landed correctly. Every em-dash in every patched file was destroyed (`—` → `â€"`), every smart quote mangled, every arrow broken. The principal didn't notice; the agent only caught it when the next system-reminder showed the file contents with mojibake throughout.

Recovery: `git checkout HEAD -- <files>` to restore the originals, then re-run the patch with `[System.IO.File]::ReadAllText` instead of `Get-Content -Raw`. Round-trip clean.

## What was affected

In this incident:
- `gielinor/meta/_about.md`, `gielinor/meta/death-and-spawn.md`, `gielinor/meta/drafts-mechanics.md`, `gielinor/meta/layer-routing.md`, `gielinor/meta/modes.md`, `gielinor/meta/write-rules.md` — all six damaged then recovered.

Going forward, the rule shapes the agent's PowerShell snippet output. Any shell-snippet skill or spellbook entry that involves text-file mutation should cite this rule.

## Supersedes / superseded by

— (first entry on PowerShell snippet authoring).

## Anchor

Bankstanding [[B-001_2026-05-22_first-bankstanding|B-001]] chat transcript, 2026-05-22. Specific message: the one-liner pasted into PowerShell that produced the encoding damage. Byte-level evidence: `od -c` on `gielinor/meta/layer-routing.md` before recovery showed `303 242 342 202 254 342 200 235` where the header em-dash should have been a single `342 200 224` (UTF-8 `—`).
