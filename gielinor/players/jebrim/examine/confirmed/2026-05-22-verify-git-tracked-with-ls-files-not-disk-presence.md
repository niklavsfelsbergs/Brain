# Verify "git-tracked" with `git ls-files`, not disk presence

**Date:** 2026-05-22
**Player:** Jebrim
**Anchor:** [[S033_2026-05-22_shipping-agent-audit|S033]] audit finding H1 + D4 dwarf report. Pass 1 flagged `workbench/investigations/ups-de-zv-130cm-diversion/` as "committed despite gitignore rule" — the folder was on disk, `.gitignore` had a `workbench/` rule, so I assumed git was tracking it and proposed `git rm --cached -r` as the fix. D4 ran the command during apply; it failed with `pathspec did not match`. The folder was already untracked. The disk presence was independent of git state.

## The observation

**Disk presence ≠ git tracking.** A file or folder can exist on disk for many reasons:

- It's in `.gitignore` and was never tracked (untracked + ignored — the [[S033_2026-05-22_shipping-agent-audit|S033]] case).
- It was tracked, got `git rm --cached`'d, and is now ignored (untracked but on disk).
- It's tracked and clean (`git ls-files` lists it).
- It's tracked and modified.
- It was tracked, was deleted, the deletion was committed, and someone restored it on disk locally (untracked, would-be-added).

Reading just `.gitignore` + `ls` tells you which combinations are possible; it does NOT tell you which one is actually in force. The authoritative check is `git ls-files <path>` — output non-empty means tracked, empty means not tracked. For "tracked despite .gitignore rule" specifically: `git ls-files <path>` returning a result confirms the gitignore rule is dormant for already-tracked paths (the documented git behavior).

## The lesson

For any audit-time claim of the form "X is tracked in git" or "X is committed":

1. **Run `git ls-files <path>` first.** Don't infer from disk presence + ignore rules.
2. **If the claim is about a folder, run `git ls-files <path>/`** (with trailing slash) to enumerate what's tracked underneath. A folder being "tracked" is shorthand for "some file inside is tracked."
3. **For the inverse claim ("X is untracked despite being on disk"),** `git ls-files <path>` empty + the file existing confirms it. `git check-ignore <path>` tells you whether `.gitignore` is the reason.

## Why this is examine-worthy

The H1 finding was wrong because I treated `.gitignore` + disk presence as sufficient signal. Same trap applies to any future audit where the agent claims something about git state from disk reads alone. The fix is procedural — `git ls-files` is a one-line check that converts inference into observation. Skipping it produces audit findings that fail at apply time, which is exactly when failure is most expensive (mid-dwarf-wave).

## Generalization

Whenever the audit claim form is "X has property Y" where Y is a system-state property (git tracking, file permissions, process running, port listening, env var set), reach for the authoritative command first, not the proxy signal. The pattern: name the property → name the command that observes it → run the command → cite the output. Don't compose properties from proxies.
