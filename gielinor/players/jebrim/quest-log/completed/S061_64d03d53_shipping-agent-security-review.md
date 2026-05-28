# S061 — Shipping-agent security review (documented, not acted on)

**Date:** 2026-05-24
**Session:** jebrim-64d03d53
**Status:** in-progress — **documentation only**. No code read, no fixes, nothing committed. Parked for a later verify-then-fix pass on principal cue.

## What this is

Principal pasted an external security/quality review of the out-of-tree `Documents/GitHub/shipping-agent/` repo (5 findings) and asked what I'd raise. We agreed to capture the review + my assessment as a quest now, act later.

**Threat-model caveat that reframes every severity:** the review grades for *"company-facing tooling"* (untrusted inputs, browser-opened artifacts, multi-user). The live deployment is a **single operator running locally against a read-only, gold-only DB user (`ship_mart_ro`), opening his own artifacts.** That deflates several severities. They re-inflate if it goes multi-user / hosted / shares reports externally. The review should state its assumed deployment model.

## The review (as received — preserve verbatim)

- **High — SQL perimeter is mostly policy, not code.** Docs say `shipping_mart.*` only, but the harness executes arbitrary SQL in `connect_redshift.py:118`, `db.py:94`, and the CSV/XLSX exporters. Read-only DB user helps, but company-facing tooling should enforce SELECT/WITH only, single statement, `shipping_mart` table refs only, row limits, and statement timeout *in code*.
- **High — generated HTML is injection-prone.** Chart/report titles, descriptions, markdown-ish content inserted into HTML without escaping in `build_inline_chart.py:224` and `build_report.py:196`. Artifacts may be LLM/user-authored and opened in a browser → sanitize/escape by default.
- **Medium-high — output path controls too soft.** Tools only block writing to repo root, but allow arbitrary resolved paths elsewhere — `query_to_csv.py:38`, `build_report.py:917`. Enforce outputs under `workbench/`, `scratchpad/`, or `memory/`, with explicit maintainer override.
- **Medium — Claude permissions stricter than they look.** `.claude/settings.json:10` denies many fs/network ops but broadly allows `python:*`, `pip install:*`. Raw Python is an escape hatch around file-read/network intent. Split setup vs runtime permissions; allow named harness commands, not arbitrary Python.
- **Low-medium — XLSX export missing a dependency.** `query_to_xlsx.py:63` needs `openpyxl`, but `requirements.txt:1` doesn't include it.

## My assessment

**Ordering is wrong: #4 (permissions) is upstream of #1 (SQL).** `python:*` makes the in-code SQL allowlist decorative against a *misbehaving agent* — it can `import redshift_connector` and bypass `db.py` entirely, same as it routes around any file/network deny. In-code SQL guards only protect the sanctioned path. Fix the permission model first (named harness entrypoints, not raw `python`/`pip`) or the rest is theater for anything but accidental bad SQL. Reviewer rated this Medium; it's load-bearing.

Per finding:

- **#1 SQL — split it.** "Mostly policy" undersells `ship_mart_ro`: the read-only gold-only grant *is* DB-level enforcement (denies writes + anything outside `shipping_mart.*`). Security half largely covered. The uncovered, higher-likelihood risk is **operational**: `statement_timeout` + default `LIMIT`. A cross-join on the 65-col `fact_shipments` is a real Redshift cost / cluster-contention incident. Reframe #1 around cost/availability, not injection.
- **#2 HTML injection — agree High; they missed the real vector.** Not just LLM-authored titles — the **data**: carrier names, shipment notes, any string column rendered into a label/cell. Report HTML is the *shared deliverable* → only realistic path to harm. `html.escape` at both render boundaries; allowlist intentional markdown.
- **#3 output paths — Medium, not Medium-high, at current scope.** For a local single operator the harm is overwriting your own files, not traversal. Stronger reason to confine paths is **PII egress** (below). Cheap guard; do it.
- **#5 openpyxl — Low, just a bug.** One-line `requirements.txt` fix. Confirm not pulled transitively first.

**What the review missed (more concrete than #2/#3 given our history):**

1. **Secrets handling.** Board has a *parked follow-up to rotate leaked tokens* — creds-in-wrong-place already happened here once. Review silent on: is `.env` gitignored, does the connection string leak into error messages / logs / artifacts, does the `--query "SELECT 1"` smoke path echo anything.
2. **PII in artifacts.** `fact_shipment_invoice_lines` + customer dims → CSV/HTML exports can carry addresses + customer names. Where do they land, who reads them, gitignored? The real reason to confine output paths.
3. **Query audit trail.** For company use, want a log of what SQL the agent ran. Probably quest-log covers it — confirm, don't assume.

## My priority order (when we act)

1. Permission model — `python:*` → named harness commands. Gates everything.
2. `html.escape` at the two render boundaries (`build_inline_chart.py`, `build_report.py`).
3. `statement_timeout` + default `LIMIT` in `db.py`.
4. `.env`/secrets + PII-egress audit.
5. Confine output paths to allowed roots.
6. `openpyxl` in `requirements.txt`.

## Next concrete step

Verify the two load-bearing claims against the actual files before any fix plan (≈10-min read, no edits):
- the `python:*` ↔ `db.py` bypass (does the permission allowance actually defeat in-code SQL guards as I claim),
- `.env` secrets handling (gitignored? leak into logs/artifacts/errors?).

Then turn the priority list into a scoped fix plan for principal sign-off.

## Deployment direction (added 2026-05-24, same session)

Principal asked how to host the agent for company use online. Resolved:

- **Cockpit-dodge misconception corrected.** The cockpit keeps an *interactive single-operator* session on subscription via PTY (project_headless_billing_constraint). That's per-operator — it does NOT fan one subscription out to a company web app, and multiplexing a subscription across many users via puppeted interactive sessions is exactly what the 2026-06-15 headless-metering change targets. Wrong tool for "company online."
- **Two clean shapes:** (A) API-backed web product (Agent SDK) — metered token pricing, but the only legitimately scalable shape for many users; (B) per-seat desktop tooling — each analyst on their own Claude Code subscription, no central hosting, no API meter.
- **Principal chose B (per-seat desktop).**

**What B actually requires (LLM side is done; plumbing is the work):**
1. **Per-user DB credentials** — the real prerequisite. Don't copy the shared `ship_mart_ro` `.env` to N laptops (multiplies S061 secrets risk × N, kills DB audit, makes rotation a fire drill). Each analyst gets own read-only gold-only DB user or SSO-federated Redshift. **IT / data-platform task, gates everything.**
2. **Repeatable setup** — clone + Python env + `requirements.txt` (+ `openpyxl` S061 fix) + own `.env`. Worth a setup script.
3. **Launcher / delivery vehicle** — decided: **Claude Code desktop app, per seat**, on a **Claude Team/Enterprise plan** (company-managed seats + billing, not personal subs). Legitimate — own interactive seat, no multiplex, no metering trap. The app opens the shipping-agent project; CLAUDE.md/how_to.md make it behave as the agent. Cockpit-style custom wrapper deferred (entangled with the brain; only if the app UX proves insufficient).

**Team-pitch framing (added this session):** pitch the *capability* (plain-English shipping-cost Q&A → verified numbers/charts/reports, no SQL), not the tool. Three honest prereqs the pitch must carry: (a) N Team-plan seats = budget ask; (b) IT provisions per-user read-only gold-only DB access = the real gate (app is useless until this exists); (c) ~30 min one-time per-machine setup. Credibility line: [[S060_7cd31d19_shipping-agent-training-campaign|S060]] — 10-Q battery, ground-truth-verified, zero hallucination, read-only by design. Offered to draft the concrete IT credential ask (user/role/schema/grants) next.

**S061 under B — partial deflation, NOT full.** Still live per-seat: secrets handling (N laptops), `python:*` escape hatch (per-machine), PII-in-artifacts (if reports shared). Deflated: multi-user SQL perimeter, HTML injection from untrusted shared artifacts. **So a subset of S061 hardening is a deployment dependency, not optional.**

**Cost note:** per-seat = fixed cost per head regardless of usage; wins on heavy/regular users, loses to metered API for light/occasional users. B's implicit bet = these are heavy users.

**Open discriminators (asked, awaiting principal):** how many analysts, and are they terminal-comfortable (analysts → repo+README+creds; business users → build/maintain an internal installer = ongoing work).

## Boundary notes

- Out-of-tree repo `Documents/GitHub/shipping-agent/` (push denied by design).
- **Uncommitted [[S060_7cd31d19_shipping-agent-training-campaign|S060]] edits already sit in that repo** awaiting principal go — keep any S061 work clear of them.
- Nothing in this session touched the repo. Documentation only.
