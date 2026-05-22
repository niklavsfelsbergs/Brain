# S045 — shipping-agent chart system fixes

**As of:** 2026-05-22
**Player:** Jebrim
**Session ID:** 91ee1383

## What this is

User surfaced a broken chart from the shipping agent — carrier cost-per-parcel Jan-Apr 2026 line chart with `,.0f` literal as every x-axis tick label and no visible legend. Started as an exploratory "what can we do about it" and graduated into a centralization + rule-teaching session against `shipping-agent/`.

Quest closed within the session — build shipped, rule taught, verified end-to-end via a re-render. Propose move to `completed/`.

## What happened

Started ungrounded. User addressed me as Jebrim at session open; I went straight to diagnosis and recommendations without loading my keepsake/persona/quest-log. Three turns in, user asked *"are you jebrim?"* and then *"why dont you know where shipping agent lives"* — both fair hits. Loaded keepsake and found the shipping-agent pin (relocated 2026-05-22 out of NFE; lives at `Documents/GitHub/shipping-agent/`). The cost of skipping the ritual was three turns of advice given without grounding.

Once grounded, walked the actual chart system:

- Read `shipping-agent/how_to.md` — found the chart hygiene rulebook (§7 Mode 2) was *already* opinionated about formatters, legend, labels. The architecture I had been about to propose (per the ultrathink turn) already exists. Plan revised: don't redesign, find the bug.
- Read `shipping-agent/harness/build_inline_chart.py` and `harness/_report_style.py`.
- Located the broken chart's source: `scratchpad/20260522-212413--tcg-carrier-mom-2026.html`, rendered from `scratchpad/20260523-tcg-carrier-mom-2026.csv` (5 carriers: ASENDIA USA, DHL, FEDEX, ONTRAC, UPS; monthly invoiced avg EUR).

### The two bugs

**Bug A — `,.0f` leaks onto datetime x-axis.** `infer_format("month")` falls back to `"int"` because the column name doesn't match `pct_*` / `eur_*` tokens. `plotly_tickformat("int")` returns `(",.0f", "", "")`. The line-chart branch parses the `month` column to actual datetime *after* `x_fmt` is computed (lines 196-199 of original `build_inline_chart.py`). `apply_style` then sets `tickformat=",.0f"` on the now-datetime axis. Plotly's d3-time-format doesn't recognize `,.0f` as a valid date directive → renders the literal string at every tick. Confirmed in HTML: `"tickformat":",.0f"` on xaxis.

**Bug B — multi-series legend silently disabled.** The line-chart multi-series branch (line 215 of original) correctly called `update_layout(showlegend=True, legend={...})`. The local `apply_style` ran *after* and unconditionally set `showlegend=False`. The earlier `True` was clobbered. Carrier names existed as trace names in the HTML but `showlegend:false` → no legend rendered. `apply_style` was a force-overwrite that didn't respect prior layout state.

### The fix (centralized, per principal call)

Three files in `shipping-agent/harness/`:

1. **`_report_style.py`** — added two helpers:
   - `style_axes(fig, *, x_label, y_label, x_fmt, y_fmt)` — single entry point for axis title + tickformat + prefix/suffix + metric-axis-only gridlines. Used by both build scripts.
   - `resolve_format_for_series(arg, col, series)` — `resolve_format` plus a datetime-dtype override that forces `"none"` (Plotly's date logic takes over), so the `,.0f` int fallback can't leak onto a date axis.

2. **`build_inline_chart.py`** — deleted the local `apply_style` (the one that hardcoded `showlegend=False`). Now uses `style_axes` + `apply_chart_style` like `build_report.py` does. Line-chart branch calls `resolve_format_for_series` after the datetime parse.

3. **`build_report.py`** — uses `style_axes` instead of inline `update_xaxes`/`update_yaxes`. Line-chart branch adds the same datetime-dtype override (one `if` after the parse).

### Verification

Re-rendered the broken chart from the existing CSV through the patched script. Parsed HTML JSON:

- `xaxis: tickformat=''`, `showgrid=False` — Plotly date defaults take over, `,.0f` leak gone.
- `yaxis: tickformat=',.0f'`, `tickprefix='€'`, `showgrid=True` — EUR on the metric, gridlines visible.
- `showlegend: True`, trace names `['ASENDIA USA', 'DHL', 'FEDEX', 'ONTRAC', 'UPS']` — legend now renders.

Output: `scratchpad/20260522-215229--tcg-carrier-mom-2026-fixed.html`. Smoke-tested a horizontal bar (shop quota CSV) — bar paths unchanged.

### --focus flag + how_to.md rule teach

After the user re-prompted the agent with a different ask (drift question), the agent produced a chart with one carrier (DPD UK) highlighted and labels missing on the line — bare line with markers, reader squints. User: *"teach the agent that when you filter a chart to 1 dimension, it should show labels."*

Two changes to honor this:

1. **`how_to.md` §7 Mode 2 chart hygiene** — extended the *Direct value labels* rule to cover line charts focused on a single series (either truly single-trace, or multi-trace with one highlighted via `--focus`).
2. **`build_inline_chart.py`** — added `--focus <value>` flag. When passed with `--color`, the matching trace gets `lines+markers+text` with formatted y-values at each point, thicker line, larger marker; other traces are present but `visible='legendonly'` (clickable in the legend). For true single-trace lines (no `--color`), labels auto-add by the same path.

Verified with `--focus FEDEX` on the existing CSV: 5 traces present, FEDEX visible with `['€27','€23','€21','€20']` baked in as text labels, others `visible='legendonly'`. X-axis date defaults preserved.

## Decisions

- **Centralize, don't surgically patch.** Principal call. The local `apply_style` in `build_inline_chart.py` had drifted away from `_report_style.py`'s `apply_chart_style`. Consolidating into one shared `style_axes` + reusing `apply_chart_style` kills this class of drift permanently.
- **Single-trace lines auto-label.** Don't make the agent pass a flag for the common case (one entity → labels). The flag is for the *focused-multi* pattern where the others should still appear in the legend as siblings.
- **Date format token deferred.** Considered adding `"date"` → `("%b %Y", "", "")` to `plotly_tickformat`. Plotly's auto-tick handling is good for monthly data; the empty tickformat works. Add the token if explicit control becomes needed.

## Pending external actions

None pending. Shipping-agent changes are on disk (uncommitted in that repo — see Open / next probe). Brain commit lands at close.

## Open / next probe

- **Shipping-agent commit.** 4 files modified in `shipping-agent/` (uncommitted there). Principal call on whether to commit and how to scope.
- **End-to-end verification through the agent.** User wants to re-prompt the agent with the drift question to see if it reaches for `--focus` when picking one carrier to highlight. If it doesn't, the rule update needs to be louder (move to §0, or add an example in the §7 Mode 2 hygiene block).
