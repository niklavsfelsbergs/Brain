# brain-health-check — the in-depth health audit + rating

**Invoked.** On demand, when Niklavs (or a Braindead/Guthix session) wants a deep read on how the gielinor brain is operating, ending in a rating. Successor to the ad-hoc audits S060 / S110 / S142 / S145 — this is their reusable, scored form.

**Produces.** A scorecard across seven dimensions, a per-dimension narrative with citations, a ranked top-3 issue list + the single highest-leverage fix, a weighted **Health Index /100 + grade**, a written judgment verdict, and a snapshot appended to `switchboard/brain-health-snapshots.ndjson` so successive runs read as a *trend*, not a one-off.

**Where to run it.** Prefer **Guthix consultation** — system-scope cross-read, no side effects, exactly his tending. Dev-brain can run it too. It is **fan-out-shaped**: one dwarf per dimension (each returns `{score, evidence[], findings[]}`), then synthesize. The one part that stays with the principal/main-agent is **live-firing the guarantees** (sub-agents can't spawn, and live-fire needs the real entry point).

## Governing discipline (do not skip)

- **Verify firing, not wiring.** A guarantee is not healthy because it is *registered*. Exercise it from its real entry point and watch it fire/block. (`examine/confirmed/.../verify-the-thing-dont-trust-the-wiring`; memory `verify_enforcement_fires`.)
- **Evidence before judgment; do not mechanize the verdict.** The rubric *ranks attention*; the "is the brain healthy" call stays a written judgment. (memory `dont_mechanize_judgment_in_analytical_reports`.) A dimension can score "2" yet not be the thing to fix first — say so.
- **Every "empty / absent / N entries" is a hypothesis** to check against the live file (`ls` / `git ls-files` / open it), never a fact echoed forward.
- **Each score must cite its evidence.** An uncited score is invalid.

## Instruments (use these — don't reinvent)

All under `developer-braindead/verification/` unless noted:

- `brain-weight.py` — always-on `@import` token load (last known ~11,886 tok; was ~23k pre-S145 trim).
- `hook-manifest-check.py` — confirms hooks are *wired* (the precondition, not the proof).
- `adherence-rates.py` — session-grouped compliance rates (OPEN-on-entry, boundary/floor catch-counts, forced-read coverage).
- `ritual-stats.py` — raw event counts.
- `close_check.py` — ritual-completeness gate (`--ritual {dev,player}`).
- `check.py` — structural checks.
- `knowledge-miss-regression-set.md` — retrieval scorecard (baseline 5 caught / 2 partial / 3 miss).
- `switchboard/ritual-events.ndjson` — event ground truth (filter synthetic sid8s: `livefire`/`lf*`).
- Prior baselines: `quest-log/S060_*`, `S110_*`, `S142_*`, `S145_*`.

## The seven dimensions + rubric (score 0–5, weighted)

1. **Structural integrity** (weight 10) — every layer has its `_about.md`; content routed correctly (no narrative-as-bank-note, no resume-state stranded in quest-log); archive discipline held (no deletes; superseded → `archive/`); no dangling wiki-links. *Evidence:* `check.py`, tree scan, `git log` for deletes. *5 = clean; 2 = systemic misrouting or dead links.*

2. **Enforcement & the six guarantees** (weight 20 — heaviest) — `hook-manifest-check.py` for wiring, then **live-fire each from its real entry point** and confirm in `ritual-events.ndjson`: a `confirmed/` write (blocked?), a delete (blocked?), a dwarf sub-spawn (blocked?), a main-agent `bank/notes/` write (redirected to drafts?), a `wrapped_up` close with a gap (blocked?), SessionStart (keepsake inlined?). *5 = all six observed firing in-anger; 3 = wired but unexercised; 0 = a guarantee fails open silently.*

3. **Rule adherence & operational discipline** (weight 18) — OPEN-posting rate (target ~100%, the historic #1 leak), OPEN/CLOSING balance, close-ritual completeness over the last ~15 sessions, commit-by-pathspec compliance (no sibling-sweep incidents). *Evidence:* `adherence-rates.py`, `close_check.py`, comms scan. *5 = ≥95% OPEN + clean closes; 2 = recurring leak.*

4. **Knowledge hygiene & alching cadence** (weight 15) — drafts backlog by age across `bank/drafts/`, `spellbook/drafts/`, `examine/drafts/`; research picked into bank; `keepsake/current.md` current and not stale; `examine/confirmed/current.md` reflects recent learning. *Evidence:* draft counts + oldest-draft age per player; keepsake/examine mtime vs recent quests. *5 = drafts triaged within a session-or-two; 2 = months-old pile.*

5. **Knowledge retrieval effectiveness** (weight 15) — re-score `knowledge-miss-regression-set` vs baseline (5/2/3); domain-cue obedience by cross-referencing fired cues against the `Reading:` line in transcripts; confirm forced-read inlines real content. *5 = ≥ baseline + obedience observed; 2 = cues fire but knowledge doesn't land.*

6. **Context economy** (weight 12) — `brain-weight.py` now vs S145/S147 baselines; trend (monotonic growth is the rot driver); the open ~6.6k CORE-thinning debt. *5 = flat/shrinking with rules intact; 2 = re-growing unmanaged.*

7. **Active-state hygiene & drift** (weight 10) — per-player in-progress quest + inventory resume counts (Y.3 cleaned Jebrim 23→3 / 46→4 — regrown?); stale OPENs with no CLOSING; lorebook/examine internal contradictions; pins that no longer pay rent. *5 = lean + coherent; 2 = bloated/contradictory.*

## Rating method

1. Score each dimension 0–5 **with cited evidence**.
2. Weighted sum → **Health Index /100**, mapped: **A** ≥90 · **B** 75–89 · **C** 60–74 · **D** 45–59 · **F** <45.
3. **Judgment overlay (required):** 3–5 sentences — is the brain *actually* healthy, the **top 3 issues ranked by blast radius**, and the single highest-leverage fix. The index ranks attention; this is the call.
4. **Snapshot** the scorecard to `switchboard/brain-health-snapshots.ndjson` (one JSON line: date, sid8, per-dimension scores, index, grade) so the next run is a trend.

## Output shape

Scorecard table (dimension · score · weight · one-line evidence) → per-dimension narrative with file/log citations → ranked top-3 issues + highest-leverage fix → Health Index + grade → judgment verdict.

## The runnable prompt

Hand this to a Guthix-consultation or dev-brain session:

```
Run an in-depth health check of the gielinor brain and give it a rating, per
developer-braindead/spellbook/brain-health-check.md.

Score seven dimensions 0–5, each from CITED evidence (no impression-only scores).
Verify firing, not wiring — exercise the guarantees from their real entry points and
watch ritual-events.ndjson; treat any "empty/absent" as a hypothesis to check.

Dimensions + weights:
 1. Structural integrity (10)         — check.py; routing; archive discipline; dead links
 2. Enforcement & six guarantees (20) — hook-manifest-check.py + LIVE-FIRE all six + ritual-events.ndjson
 3. Rule adherence & discipline (18)  — adherence-rates.py; close_check.py over ~15 sessions; OPEN/CLOSING balance
 4. Knowledge hygiene & alching (15)  — drafts backlog by age; keepsake/examine currency; research picked
 5. Knowledge retrieval (15)          — re-score knowledge-miss-regression-set; domain-cue obedience vs Reading: line
 6. Context economy (12)              — brain-weight.py now vs S145/S147; the ~6.6k CORE-thinning debt
 7. Active-state hygiene & drift (10) — per-player in-progress/inventory counts; stale OPENs; lorebook/examine contradictions

This is fan-out-shaped — consider a Workflow or parallel dwarves (one per dimension,
each returning {score, evidence[], findings[]}), then synthesize. Live-fire of guarantees
stays with the principal/main-agent (sub-agents can't spawn).

Output: scorecard table → per-dimension narrative with citations → top-3 issues ranked
by blast radius + the single highest-leverage fix → weighted Health Index /100 + grade
(A≥90/B75/C60/D45/F<45) → 3–5 sentence judgment verdict → snapshot to
switchboard/brain-health-snapshots.ndjson. Do NOT mechanize the verdict.
```

## Related

- `verification/` — the instruments listed above.
- `quest-log/S145_*` — the knowledge-loading & rule-adherence audit this generalizes.
- `gielinor/spellbook/rituals/bankstanding.md` — Guthix's brain-tending ritual; a health check is a deeper, scored cousin run on demand.
