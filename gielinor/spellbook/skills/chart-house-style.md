# Chart house style — skill

Niklavs' taste for analytical charts: dark-mode, pastel, distribution-honest. The *judgment* (palette, type hierarchy, which chart type tells the truth, why the legend sits where it does) is here, transferable to any plotting surface. The repo-specific `lib.style` / `workbench`-template wiring stays in the repo.

> Migrated from `bi-analytics-main/NFE/.claude/reference/house-style.md` (2026-06-09, [[D-034_guthix_executes_on_explicit_authorization|D-034]]). The NFE doc keeps the `apply_style`/`wrap_chart`/`workbench` wiring and points here for the taste.

## When this fires

Building or styling any chart — Plotly especially, but the palette/type/honesty calls generalize.

## Palette — pastel on dark

```
#93C5FD  blue       #FDE68A  yellow
#86EFAC  green       #C4B5FD  purple
#FCA5A5  red         #FDBA74  orange
#A5F3FC  cyan        #F9A8D4  pink
```

- **Default two-series pair: blue + yellow** (`#93C5FD` + `#FDE68A`) — maximum hue distance, both readable on dark, colorblind-safe. The go-to whenever comparing two groups.
- Pick sequentially for more series.

## Type hierarchy (dark mode)

| Element | Size | Color |
|---|---|---|
| Title | 24 | white |
| Subplot titles | 18 | light, bold |
| Base / axis | 15–16 | muted / light |
| Bar labels | 12 | light |
| Hover | 14 | white |

## Truth-telling defaults

- **Violin over box plot** — violins show the full distribution shape; a box hides multimodality and where the mass actually sits.
- **Don't mix metric variants** in one view — one chart, one definition.

## Layout reasoning (not just values)

- **Legend grows upward, not into the plot.** Horizontal, centered above the plot, anchored at its *bottom* edge (`yanchor="bottom"`) so it expands into the top margin instead of overlapping the chart. The default top-anchor for `y>0.5` is the trap — it overlaps. Single chart `y≈1.02`; subplots `y≈1.08` (subplot titles occupy `~1.0–1.05`).
- **Margins buy room for bigger type.** Single chart `t≈100`; with a legend `t≈130`; subplots with a main + subplot titles `t≈140` so the main title clears the subplot titles. Omit `l`/`r` to let the engine auto-fit axis labels.
- **Subplot titles styled, not hand-placed** — pass via the subplot-titles param, then bold + size them; don't position annotations manually.

## What stays in the repo

The `workbench` Plotly template registration, `apply_style(fig, …)`, `wrap_chart(…)`, the `lib.style` exports, `st.plotly_chart(theme=None)` integration. Repo wiring. See the repo's `reference/house-style.md` (now a pointer).

## Related

- [[report-design-language]] — reports define their *own* tokens (don't use this template); this style is for notebooks/dashboards.
