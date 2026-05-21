# S015 — 2026-05-21 — TTYD review and dry-run

**Principal:** Niklavs
**Player:** Jebrim
**Born:** 2026-05-21 (continuation of S014, opened immediately after S014's close in S019)
**No pending external actions.**

## The ask

S014 shipped the Shipping Data Mart TTYD artifact at `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/` (commit `48e0b44`). This quest is the **review pass**: discuss what landed, dogfood-test whether it works as intended, decide what needs revision before it's actually relied on.

Open shape — the principal will steer the angle:

- **Coherence re-read** — does §1–§9 + the existing §5/§6/§7/§8 (Stream A) land as a single document? Cross-section conflicts? Tone consistency?
- **Dogfood run** — act as a fresh AI agent that just landed in the repo and was told "read `how_to.md`, then answer a real Shipping Data Mart question." Where does the artifact help, where does it have gaps?
- **Critique pass** — what's overconfident, underspecified, or premature in what we wrote?
- **Use-case mapping** — how does this artifact actually get used in practice (which agents will read it, in which workflows, with what handoff to Niklavs)?

## Relationship to S014

S014 is closed in `quest-log/completed/`. This quest does **not** inherit S014's open task list (there is none — all 11 tasks landed). It inherits the *artifact* — `how_to.md`, the four AI entry points, the connection harness, the viz-studio retarget, the reference set. Anything we surface here that requires a fix lands as a new commit to `bi-analytics-main`, not as a reopening of S014.

## Where we are

T1: Quest opened. Awaiting principal direction on which review angle to take first.

## Turn log

- T1 (2026-05-21): S014 closed (S019 brain commit `18f8184`, bi-analytics commit `48e0b44`). Principal cued opening of continuation quest S015 for review/dogfood. Quest file created with open-shape ask; awaiting principal's choice of first angle.
- T2 (2026-05-21): Session resumed mid-quest after `/clear`. Respawn completed — no pending external actions, no reconciliation needed. Surfaced the four review angles to the principal.
- T3 (2026-05-21): Principal chose dogfood angle (test the artifact as a fresh AI agent). Pre-spawn discussion surfaced a meta-question — should we build a specialized agent for shipping-data-mart questions? Recommended deferring that until after the dogfood (else we lose the diagnostic on whether the artifact is self-sufficient). Principal accepted.
- T4 (2026-05-21): Principal raised the "what points the dwarf to TTYD?" question — investigated the discoverability chain. Found a real gap: `bi-analytics-main/CLAUDE.md` has no mention of shipping mart; `NFE/CLAUDE.md` points only at `.claude/reference/shipping-data-mart/overview.md`, never at TTYD. The four AI entry points in the TTYD folder route inward but nothing outside points in.
- T5 (2026-05-21): Principal created `TTYD-template/NFE/` for brain outputs, then reverted — outputs go to TTYD's intended conventional locations (`visualization-studio/content/generated/<ai>/<timestamp-slug>/` per how_to.md §7–§8). Proposed 4-item plan (keepsake / bank / skill / NFE patch); principal greenlit items 1 (keepsake) + 4 (NFE patch).
- T6 (2026-05-21): Wrote `keepsake/proposals/2026-05-21_shipping-data-mart-routing.md` (supersedes the stale S014-progress proposal). Patched `NFE/CLAUDE.md` Shipping Data Mart section — new top callout points at TTYD `how_to.md` as the canonical guide for *doing* mart work; existing reference-doc callouts kept as the navigation map. Sibling commits pending: brain commit for the keepsake proposal + NFE commit for the CLAUDE.md patch.
- T7 (2026-05-21): Principal approved pinning the new keepsake. Pinned the routing card into `keepsake/current.md`. Archived both proposal files into `keepsake/archive/proposals/` per `archive-discipline.md` — the new routing proposal (now pinned) and the superseded S014-progress proposal. Jebrim's keepsake is no longer empty — first standing pin landed.
- T8 (2026-05-21): Principal cued session close with handover "continue with the dogfood." Ran close-session ritual: wrote `inventory/S015-ttyd-resume.md` (step 3); harvested two drafts (step 6) — `spellbook/drafts/skills/investigate-before-specialize.md` (methodology earned from the chain-investigation pattern) and `niksis8_character/drafts/2026-05-21-prefers-evidence-over-premature-infrastructure.md` (working knowledge of how Niklavs accepts evidence-driven deferrals); quest stays in-progress (dogfood not yet run).
- T9 (2026-05-21): SNNN check — quest-log glob max is S015 but commit history shows S019 was last (the glob misses sessions that didn't birth a new quest file). Next session ID is **S020**. Surfacing as a soft ritual gap; not blocking. Commit scoped to Jebrim namespace; meta/ + CLAUDE.md changes (principal's parallel work introducing the gnome role) left for a separate commit. NFE/CLAUDE.md patch (other repo) flagged as open — not committed by brain close.

## Close summary

**Session S020** closed at 2026-05-21. Active player: Jebrim. Quest S015 remains in-progress.

**Landings (S020):**
- First standing pin in Jebrim's keepsake — shipping data mart routing card.
- Discoverability gap closed at NFE root via `NFE/CLAUDE.md` callout (uncommitted in the bi-analytics-main repo — flagged for principal).
- Two harvest drafts surfaced for next-alching review.

**Resume:** see `players/jebrim/inventory/S015-ttyd-resume.md`. Next concrete step: run the dogfood test.

---

## S022 turns (2026-05-21, session opened after S021 alching)

Principal context shift: tomorrow (2026-05-22) is a stakeholder demo of the Shipping Data Mart with TTYD as the showcase. Logistics manager in audience. The dogfood test is no longer abstract — it's a dry-run of the actual demo path (cold AI agent in TTYD answering a real business question). Self-sufficiency of `how_to.md` is now load-bearing.

### T1 — outward-reference scan of TTYD

Scanned TTYD `.md` files for outward refs. AI-config files (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `GROK.md`) clean. `how_to.md` had 4 outward refs: L59 (`NFE/.claude/reference/.../sources.md`), L83 (per-carrier SQL in bi-etl), L196 (`NFE/.claude/reference/.../tables.md` + bi-etl READMEs), L394 (`../../../.env` walk-up for credentials). Also surfaced: a `TTYD-template/` subfolder mirroring the active project with a generic-template `how_to.md` (revenues / labour costs — not shipping-specific) — risk of a cold agent reading the wrong file.

### T2 — structure decision

Principal chose folder-standalone (option b): `how_to.md` as entry, sibling `reference/tables.md` + `reference/sources.md` for deeper drill-downs. Env code change deferred ("works on my laptop, good enough"); a local `.env` was added for the demo. `TTYD-template/` to be removed. Carrier SQL outward ref to be cut, not folded. `how_to.md` to be re-oriented as TTYD-specific, not generic-template-flavored.

### T3 — credentials and template removal

Principal supplied a new read-only Redshift user for the data mart: `ship_mart_ro`. Per discipline: `.gitignore` updated to include `.env` first (it was not previously ignored — only `creds.env` was), then `.env` written at TTYD root with `REDSHIFT_USER` + `REDSHIFT_PASSWORD`. `git check-ignore` confirmed protection. `TTYD-template/` moved via `git mv` to `NFE/projects/_TTYD-template/` (sibling, preserving history); untracked `visualization-studio - template/` came with it. `semantic-layer-draft.json` lived inside the template, so it moved with the template (out of active TTYD path) — semantic layer is deferred per principal until things stabilize.

### T4 — reference files + how_to.md surgical edits

Wrote `reference/tables.md` (folded from NFE-side tables.md, stripped of bi-etl paths and Canonical-README footers) and `reference/sources.md` (folded from NFE-side sources.md, stripped of bi-etl SQL path references). Both files self-contained within TTYD.

Edited `how_to.md`:
- Header reframed from generic "AI How-To" to "Talk-To-Your-Data how-to" with explicit folder-self-contained framing. Dropped "TBD pending principal-Jebrim authoring (Stream B)" jargon.
- L59 → `reference/sources.md`.
- L83 → "per-carrier source tables and ingestion notes in `reference/sources.md`" — bi-etl path dropped.
- L196 → `reference/tables.md` — both NFE-side and bi-etl per-table README links dropped.
- §6 Connecting to Redshift — rewrote credentials section: local `.env` (next to `how_to.md`), `find_dotenv()` finds it first via walk-up, gitignored. Mentions `ship_mart_ro` as the demo user.

Verified: `grep` for outward paths across all `.md` files in TTYD returns no matches.

### T5 — known residual

Python docstrings in `db.py` and `connect_redshift.py` still reference `NFE/.env` ("credentials are read from `NFE/.env`", "located by walking up", `../../../.env` fallback). Behavior is correct (`find_dotenv()` walks up from the script's dir, so local `.env` wins), but the docstrings mislead. Principal said env-code cleanup is "later" — leaving for now, flagged for next pass.

### Where we are after S022 turns

- TTYD folder is `.md`-self-contained. Cold agent reading anything in this folder will not hit an outward path link.
- Local `.env` in place; demo user is `ship_mart_ro` (read-only).
- `TTYD-template/` out of the active project tree (moved to `NFE/projects/_TTYD-template/`).
- Python docstring cleanup is the one known residual.
- **Next concrete step** unchanged from S020 close: run the dogfood test. Question TBD with principal.
