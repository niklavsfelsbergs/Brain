# S218 · EU Tender 2026 — no-Hermes final report → management slide deck

**Player:** Jebrim · **sid8:** 932b8e5c · **opened:** 2026-06-11

## Ask

Build an HTML slide deck of the EU-tender **no-Hermes** final report — a management-meeting
presentation of the project results, paced to flow and read logically.

## What happened

- **Misread the target first (see Cascade / harvest).** "in the final report no hermes folder"
  → I dropped the `no hermes` qualifier. The follow-up "srry its for eu tender" read (wrongly) as
  "use the main `final_report/`", so I built the deck off `final_report/` + `final_stats.json` first.
  Principal corrected: *"but this is not the final_report_no_hermes"*. Rebuilt against the right source.
- **Delivered:** `final_report_no_hermes/deck_no_hermes.py` → `deck_no_hermes.html` — 13-slide
  self-contained dark-theme deck (same palette as `report_no_hermes.html`), generated from
  `stats_no_hermes.json` (no hand-typed numbers, same discipline as `report_no_hermes.py`).
  Keyboard/click nav (arrows, space, edge-click, dot-jump, F=fullscreen), progress bar, per-slide `#n` deep-links.
- **Story (no-Hermes scenario):** single committed number **€976,024/yr (6.5%)**, five carriers, no
  oversize module. Flow: title → bottom line (confirmed €683k + offer-based €293k) → scope (Hermes OFF) →
  recommendation (5 carriers, 3 moves) → yardstick bridge → saving by confidence (2 tiers, no conditional) →
  by mechanism (reprice vs reroute) → who carries what → **optional upside** (the €696,082/yr DB Schenker
  reroute, gated + NOT banked: template dims + oversize-on-UPS) → how built → risks → decisions → close.
- **Headline figures verified** against `stats_no_hermes.json`: €976,024/yr committed, €696,082/yr optional
  upside — both tie in the rendered HTML.
- **Cleanup:** the first (wrong-scenario) `final_deck.py`/`.html` were moved to `final_report/_superseded/`
  (the brain's `block-deletes.py` hook blocks deletes repo-wide — archived, not removed).

## Pending external actions

None pending in the brain. The bi-analytics artifacts are **uncommitted** (separate repo) awaiting
principal review of the rendered deck + a commit go (never push).

## Cascade.

None — self-contained deliverable. The deck reads `stats_no_hermes.json`; if the no-Hermes stats are
rebuilt (e.g. the AU relabel / service-mix mirror decisions on [[S212_177f00f1_eu-tender-no-hermes-report|S212]]), rerun `python
final_report_no_hermes/deck_no_hermes.py` to pick up the new numbers.

## Main-brain changes.

None to `gielinor/` substance — brain footprint is this quest-log entry + its resume + 1 examine draft
+ the comms CLOSING. All deliverable code lives in bi-analytics (separate repo).
