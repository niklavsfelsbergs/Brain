# Report & document design language — skill

Niklavs' house taste for **static, shareable, self-contained HTML** — reports, doc pages, dashboards-frozen-to-a-file. The *judgment* (which tool for which audience, how a report reads, what makes it feel made-not-generated) lives here so it applies to every surface — analysis repos, the cockpit, the brain visualizer — not just the repo it was born in. The repo *wiring* (the `lib.` loaders, build paths) stays in that repo.

> Migrated from `bi-analytics-main/NFE/.claude/reference/report-patterns.md` + `notebook-patterns.md` taste + `lib/templates/{documentation,report}.html` (2026-06-09, [[D-034_guthix_executes_on_explicit_authorization|D-034]]). The NFE docs keep the wiring and point here for the language.

## When this fires

Building anything a stakeholder *reads* rather than *operates*: an HTML report, a documentation page, an exported summary, a static deliverable emailed or linked. Also the presentation-taste layer of any notebook/dashboard.

## Audience → tool

| Audience | Tool | Why |
|---|---|---|
| Analyst, self-serve | Marimo notebook | reactive cells, fast iteration |
| Stakeholder, interactive | Streamlit | sidebar filters, KPI sparklines, app feel |
| Stakeholder, static | **Self-contained HTML report** | no server, email-friendly, fully bespoke |

When it's a *send-it* artifact with a known narrative → static HTML. No server, no filters, no framework runtime.

## How a report reads

- **Lead with a bold key observation.** First line of any commentary block is the finding, emphasized — not setup. The reader gets the answer before the evidence.
- **Each report owns its design.** No shared renderer for reports — every report defines its own design tokens (colors, fonts, Plotly layout dict) inline. Notebooks/dashboards share `lib.style`; reports do not. This is deliberate: a report is a one-off artifact with its own voice.
- **Distinctive fonts, never the defaults.** Avoid Inter / Roboto / Arial. Each report gets its own pairing via Google Fonts CDN (e.g. Darker Grotesque + IBM Plex Mono). The font choice is half the personality.
- **Self-contained.** Fonts via CDN `<link>`, Plotly via CDN `<script>`, everything else inlined in one `<style>`. One file, opens anywhere.

## Layout taste

- **Center the content** — `max-width` + `margin: 0 auto`. Never full-bleed text.
- **Unified grids, not floating cards** — KPI strips use CSS Grid with a `1px` gap so cells read as one surface, not scattered boxes.
- **Stagger the entrance** — fade sections in with incremental `animation-delay`.
- **Responsive** — stack grids below ~700px.

## Presentation taste (carries into notebooks/dashboards too)

- **Format decimals to 2 places** by default.
- **Bullets over tables** inside callouts/accordions — a table in a small callout reads worse than tight bullets.
- **Sections first, filters second** — each analytical question gets its own dedicated chart visible by default; don't bury topics in tabs. The one global filter that earns a sidebar is a date-range that re-scopes everything.

## The templates

The two reference templates — a dark-themed **documentation page** (sidebar nav, scroll-spy, utility CSS classes: `.card`, `.flow-steps`, `.kpi-row`, `.tag`, `.arch-diagram`) and a **report** shell — are the canonical starting design. They live with their loader (`lib/docs.py`, `lib/report.py`) in the analysis repo; treat *this skill* as the language they express. When building HTML anywhere else, reach for the same language, not the repo's loader.

## What stays in the repo

The `lib.docs` / `lib.report` Python loaders, `analysis_config.json` wiring, the reference-implementation paths, `fig.to_html` embedding mechanics. Those are how *that* repo renders — not transferable taste. See the repo's own `reference/report-patterns.md` (now a pointer) for them.

## Related

- [[chart-house-style]] — the Plotly chart styling that sits inside these reports.
- [[commentary-methodology]] — how the narrative text in a refreshed report/dashboard gets generated traceably.
