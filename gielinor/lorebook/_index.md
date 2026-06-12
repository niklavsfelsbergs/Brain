# lorebook/_index.md — synthesized cue index over confirmed decisions

> **What this is.** The machine-read map of `lorebook/confirmed/` — one entry per
> decision, with a distilled load-bearing rule and (where a topic cue exists) the
> prompt patterns that should force it into view mid-session. The `[LOR]` arm of
> `domain-cue-reminder.py` parses this file on every prompt: a pattern match
> force-inlines the entry's `rule:` line once per session per decision (the §Z.C
> forcing-over-naming shape, entry-level — a distilled rule is 2–4 lines, so the
> rule itself is the payload, not a file pointer). Closes knowledge-miss
> regression case 10 (S145 set; built [[S192_384c1c27_db-schenker-reroute-package-dims|S192]]).
>
> **Entry shape the hook parses.** A `## D-NNN — title` header, then optional
> `- file:`, `- carried-by:`, `- patterns:` (comma-separated literal substrings,
> matched case-insensitively), `- rule:` (ONE line — the distilled, in-force
> rule). Entries without both `patterns:` and `rule:` are inert to the hook —
> they document where that decision's behavior already lives (`carried-by:`).
>
> **Honest accounting.** Most confirmed decisions do NOT need a cue: they are
> carried by an always-on file (`meta/communication-protocol.md`,
> `meta/layer-routing.md`), by a ritual file read at its moment (close-session,
> alching, bankstanding — the close-cue hook routes to the first), by a hook
> (grounding-cue IS [[D-028_grounding-precondition-needs-a-trigger|D-028]]), or they are historical records with no standing
> per-turn behavior. Cue rows exist only where a decision is genuinely missable
> in a player turn. A `carried-by:` label is a claim — if the named carrier
> stops existing, the entry needs a cue row or a new carrier.
>
> **Maintenance.** When a draft is promoted to `lorebook/confirmed/`, add its
> entry here in the same pass (drafts-triage / bankstanding both carry the
> step). Drift detector: `developer-braindead/verification/hygiene-check.py`
> flags confirmed decisions missing from this index and ghost entries whose
> decision file is gone.

---

## [[D-017_user-only-with-explicit-permission|D-017]] — "User-only" is default-no, not architectural-no
- file: lorebook/confirmed/D-017_user-only-with-explicit-permission.md
- carried-by: cue (this index)
- patterns: user-only, keepsake, pin this, pin that
- rule: "User-only" surfaces (keepsake/current.md, meta/*.md, spellbook/rituals/) are a default, not a prohibition — on explicit principal authorization for a specific write ("yes, write it"), make the write directly instead of forcing a copy-paste loop. Only the hook floor (confirmed/ writes, deletes) is non-overridable.

## [[D-018_close-session-ritual-adoption|D-018]] — Close-session ritual adoption
- file: lorebook/confirmed/D-018_close-session-ritual-adoption.md
- carried-by: ritual (spellbook/rituals/close-session.md; close-cue-reminder.py routes to it) — historical adoption record

## [[D-019_harvest-pump-installation|D-019]] — Observation harvest pump at close-session
- file: lorebook/confirmed/D-019_harvest-pump-installation.md
- carried-by: ritual (close-session.md step 6; alching.md step 2) — historical adoption record

## [[D-020_layer-routing-and-resume-via-inventory|D-020]] — Layer routing codified; resume state via inventory
- file: lorebook/confirmed/D-020_layer-routing-and-resume-via-inventory.md
- carried-by: always-on (meta/layer-routing.md, @imported every session)

## [[D-021_lorebook-folder-naming-correction|D-021]] — Lorebook folder naming corrected (decisions/ → confirmed/)
- file: lorebook/confirmed/D-021_lorebook-folder-naming-correction.md
- carried-by: historical (the docs it corrected are fixed; no standing behavior)

## [[D-022_lorebook-folder-naming-correction-expanded-scope|D-022]] — Lorebook folder naming, expanded scope
- file: lorebook/confirmed/D-022_lorebook-folder-naming-correction-expanded-scope.md
- carried-by: historical (same correction as [[D-021_lorebook-folder-naming-correction|D-021]], wider sweep)

## [[D-023_powershell-utf8-readall-not-getcontent|D-023]] — PowerShell round-trips: ReadAllText, never Get-Content -Raw
- file: lorebook/confirmed/D-023_powershell-utf8-readall-not-getcontent.md
- carried-by: cue (this index)
- patterns: powershell, get-content, set-content, bulk edit, find and replace, find-and-replace, mojibake
- rule: Any PowerShell snippet that read-modify-writes a text file must use [System.IO.File]::ReadAllText → modify → WriteAllText — never Get-Content -Raw → Set-Content. PS 5.1 decodes UTF-8 as Windows-1252 and silently mojibakes every multi-byte character in the file (— becomes â€”); the script reports success and the damage is invisible at authoring time. Applies to every find-and-replace / bulk-edit snippet.

## [[D-024_scope-git-commits-with-pathspecs-parallel-sessions|D-024]] — Scope git commits with explicit pathspecs (parallel sessions)
- file: lorebook/confirmed/D-024_scope-git-commits-with-pathspecs-parallel-sessions.md
- carried-by: cue (this index)
- patterns: commit, git add, push
- rule: Shared working tree + parallel sessions — always commit with explicit pathspecs (git commit -m ... -- <paths>), never a bare git commit: the git index is shared, so a bare commit sweeps a sibling session's staged files into yours (live sweeps [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]], [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]]). Before committing, inspect the UNFILTERED staged set (git diff --cached --name-only — a path-filtered check is what masked it). Never push without an explicit, separate principal ask.

## [[D-025_offer-multiple-choice-with-recommendation|D-025]] — Offer choices as multiple-choice with a recommendation
- file: lorebook/confirmed/D-025_offer-multiple-choice-with-recommendation.md
- carried-by: always-on (meta/communication-protocol.md §Offer choices as multiple-choice)

## [[D-026_graduate-complete-ready-quests-in-session|D-026]] — Complete-ready quests graduate in-session
- file: lorebook/confirmed/D-026_graduate-complete-ready-quests-in-session.md
- carried-by: ritual (close-session.md graduation step; refined by [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]])

## [[D-027_plain-text-deliverables-for-terminal-copy|D-027]] — Copyable deliverables as plain text, not code blocks
- file: lorebook/confirmed/D-027_plain-text-deliverables-for-terminal-copy.md
- carried-by: always-on (meta/communication-protocol.md §Copyable deliverables)

## [[D-028_grounding-precondition-needs-a-trigger|D-028]] — The grounding-precondition needs a trigger, not another note
- file: lorebook/confirmed/D-028_grounding-precondition-needs-a-trigger.md
- carried-by: hook (grounding-cue-reminder.py IS this decision's mechanism)

## [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] — Auto-graduate unambiguous complete-ready quests
- file: lorebook/confirmed/D-029_auto-graduate-unambiguous-complete-ready-quests.md
- carried-by: ritual (close-session.md step 4 — shipped+committed+no-open-dependency moves without a y/n, vetoable batch)

## [[D-030_alching-sweeps-orphan-subagent-traces|D-030]] — Alching sweeps orphan sub-agent traces
- file: lorebook/confirmed/D-030_alching-sweeps-orphan-subagent-traces.md
- carried-by: ritual (alching / bankstanding Phase 0 — read at ritual entry)

## [[D-031_partial-alch-by-draft-settledness|D-031]] — Partial-alch a mid-quest player by draft-settledness
- file: lorebook/confirmed/D-031_partial-alch-by-draft-settledness.md
- carried-by: ritual (bankstanding §0 flag-and-ask resolution)

## [[D-032_braindead_full_access|D-032]] — Braindead has unrestricted edit access
- file: lorebook/confirmed/D-032_braindead_full_access.md
- carried-by: hook (block-confirmed-writes.py / block-deletes.py carry the actor bypass) + developer-braindead/CLAUDE.md

## [[D-033_act-only-when-an-act-is-merited|D-033]] — Act only when an act is clearly merited
- file: lorebook/confirmed/D-033_act-only-when-an-act-is-merited.md
- carried-by: memory (feedback_act_only_when_asked_to) + examine/confirmed — no clean topic cue (its trigger is "the prompt is a question", which would fire on everything; a wallpaper cue is worse than the memory carrier). Honest residual: if the memory index rotates it out, this needs a new carrier.

## [[D-034_guthix_executes_on_explicit_authorization|D-034]] — Guthix executes on explicit principal authorization
- file: lorebook/confirmed/D-034_guthix_executes_on_explicit_authorization.md
- carried-by: cue (this index)
- patterns: why can't you, why cant you, carry it out, carry this out, carry that out, you should be able
- rule: Guthix's "proposes-only" rule governs UNILATERAL action; on explicit, specific principal authorization ("do it — this change, now") Guthix executes directly against the discipline-gated surfaces (globals, per-player layers, rulebook prose). The hook floor still binds him (no confirmed/ writes, no deletes — that routes through Braindead or the principal). Don't re-derive propose-only as a hard limit; that exact friction is why [[D-034_guthix_executes_on_explicit_authorization|D-034]] exists.
