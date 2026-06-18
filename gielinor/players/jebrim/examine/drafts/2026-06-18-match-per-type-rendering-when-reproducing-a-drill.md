---
date: 2026-06-18
session: 5cbb1d00
quest: S269_scm-cost-drivers-panel-filters
---

# When reproducing a drill-in as a new component, preserve its per-type rendering

**Observation ([[S269_5cbb1d00_scm-cost-drivers-panel-filters|S269]]).** I replaced the Cost-Drivers driver-click behavior (which drilled into one of four inner tabs) with a single inline chart, and rendered one `CostTrend` for *every* driver type. Niklavs caught it: "it always opens the rate changes view — some drivers are from other tabs." The four inner tabs don't render the same chart — rate uses `CostTrend`, the three shift tabs use `CarrierShareChart`. I'd collapsed four chart behaviors into one and only noticed the happy path (rate).

**The lesson.** When you re-home an interaction (a drill-in, an expand, a navigation) into a new surface, the thing you're replacing usually has **type/branch-specific rendering**, not one uniform output. Before unifying, enumerate what the original does for *each* case (here: read each of the 4 tables' expand-chart block) and reproduce the branch, not just the first/most-common case. A "unified" reimplementation that erases legitimate per-type variation is a regression dressed as simplification — the over-collapse sibling of gold-plating.

**How to apply.** Reproducing existing behavior in a new place → list the input variants the original handles and check each renders correctly, before declaring it done. Don't generalize from the one variant you happened to test first.

Relates to the [[scm]] domain and [[2026-06-18-push-is-branch-granular-on-shared-tree]] (both from this session).
