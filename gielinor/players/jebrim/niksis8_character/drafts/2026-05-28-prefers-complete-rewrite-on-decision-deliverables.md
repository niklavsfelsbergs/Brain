---
name: prefers-complete-rewrite-on-decision-deliverables
description: On a decision-facing deliverable, Niklavs picks the thorough complete rewrite over a minimal scoped fix
metadata:
  type: niksis8_character
---

**Observation (S119, 2026-05-28).** Hardening the EU-tender `decision_report.html`, I flagged that Section 04's per-carrier narratives held stale pre-rebuild numbers and offered three scopes: fix only the directly-contradicting figures (my recommendation), full Section-04 rewrite, or a "predates rebuild" banner. Niklavs chose the **full rewrite** — re-derive every carrier's numbers from current data.

**Read:** on a deliverable that feeds a real decision (a report stakeholders will act on), Niklavs leans toward complete internal consistency over a minimal scoped patch, even at higher effort. The minimal-fix instinct (don't expand scope) is the right default for *code* he didn't ask to change, but a *decision document* he treats as one artifact that must be coherent end-to-end. When scoping a decision-facing deliverable, bias toward the thorough option or at least surface it as the recommendation, not the fallback.

Anchor: [[S118_f41737e5_eu-tender-decision-scorer-report-regen|S118]] continuation (session 4c2210ee).
