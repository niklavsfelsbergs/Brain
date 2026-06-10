# S190 · jebrim-9a064d86 · EU Tender 2026 — red-team audit → report rebuild → annualization plan

**Player:** Jebrim · **sid8:** 9a064d86 · **Opened:** 2026-06-09 ~21:40 · **Closed:** 2026-06-10

## What this session was
A final adversarial (red-team) audit of EU Tender 2026 before management, which then turned into a correctness-fix + report-rebuild + a locked plan for the annualization (4th) report.

## Narrative / decisions

1. **80-agent red-team workflow** (`wf_91d323f7-a64`, resumed once after a laptop crash via the journal) — 11 carrier-engine finders + 8 cross-cutting, every material finding adversarially verified, + 1 live-mart provenance spot-check. → `research/2026-06-09-eu-tender-2026-red-team-audit.md` (committed `b25244d`). Verdict: directional decision holds; headline was a Q1 best-case, not a floor; tier-(a) cluster = saving leans on unvalidatable Hermes/Maersk-EU engines + the scorer has no per-parcel do-nothing floor (A5). Live mart surfaced A0 (MAERSKUK 32k > MAERSKFR 28k — baseline is a 3-carrier subset; scope to confirm).
2. **Oversize→freight leak** (dwarf): Maersk/Hermes were keeping ~3,448 freight-sized parcels at cheap oversize pricing. The parallel session fixed it (maersk-3.1.0/hermes-2.1.0, HEAD bi-analytics `6833671`) → headline €377,471/12.77% → €276,951/9.37% (the audit leak was real, cost ~€100k).
3. **Fuel/peak per-carrier review** with Niklavs — decisions: Hermes → **flat 7%** (was 0/0/7); Maersk peak → keep **€0.25** placeholder (noted); DPD confirmed **no peak** (correct, not a gap); DHL bulky **carrier-confirmed correct** round-2 (any-side>60 = Sperrgut; NOT the maersk/hermes girth class — see learning). Maersk-EU fuel 6.6% is above the carrier's stated 4–6% band + its derivation doc `FUEL_SUMMARY.md` is missing (flagged).
4. **Hermes flat-7% rebuild, done here** — edited `carriers/hermes/constants.py` (flat 7%, hermes-2.2.0), regenerated **both** cost matrices (Q1 + 2025 full-year) + all 3 Q1 reports + refreshed the stale hand cards. Headline → **€275,484 / 9.32%**. Committed bi-analytics `052d3c4` (pathspec-scoped, not pushed).
5. **Annualization plan locked + saved** → `research/2026-06-10-eu-tender-annualization-method-and-assumptions.md`. Key: flat-fuel makes fuel month-invariant → peak is the only seasonal cost → clean recipe (peak-free base × annual volume + peak × peak-window volume), the Q1→annual bridge, mix-adjust dropped (qualitative caveat only, principal call).

## Cross-repo (bi-analytics, separate repo — committed, NOT pushed)
- `6833671` (oversize fix, parallel session) → `052d3c4` (Hermes flat-7% + 3 reports rebuilt, this session). Tree clean bar pre-existing untracked `management_briefing/`.

## Main-brain changes (this repo)
- Committed: `b25244d` (audit report), `35dd91e` (annualization note v1). This-close commit adds: quest-log + inventory resume + 1 examine draft + the updated annualization note + comms CLOSING.

## No pending external actions.
All commits landed; nothing left `pending`.

## Open (carried forward)
- **Build the annualization report (the 4th report)** — full spec in the annualization note. This is the open dependency; resume → `inventory/eu-tender-annualization-resume__9a064d86.md`.
- Standing audit items A0 (Maersk scope) + the open carrier items (Maersk EU fuel schedule/band, Maersk peak schedule, UPS GRI 5%-vs-5.9%, DHL thin-flat Sperrgut waiver) — all in the note's ledger.
