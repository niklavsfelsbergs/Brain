# S024 — Shipping-agent rulebook revamp

**Opened:** 2026-05-21 (retroactively — see Discipline note below)
**Player:** Jebrim
**Trigger:** Principal flagged a real overkill in the shipping-agent: a simple "show me a chart" request had produced a full Next.js bundle (request folder + `index.html` + `bundle.json` + `spec.json` + viewer link) where an inline chart in chat would have sufficed. Asked Jebrim to rework how the HTML/Next.js paths get proposed — inline by default, bundles as confirmed escalations.

## Scope

Mutate the shipping-agent's `how_to.md` to:

1. Replace the three-mode visualization model (chat / HTML bundle / Next.js) with a four-mode model where **Mode 2 = inline HTML** is the new visual default and bundles are confirm-before-build escalations.
2. Add a minimal Python builder for the inline-mode artifact.
3. Tighten §10 scope enforcement after a couple of real overreach incidents (`ls` permission prompts; attempted read into `NFE/.claude/reference/`).
4. Add cross-cutting rules that came out of real friction: acknowledge briefly, don't over-research canonical questions, default visual breakdowns are an offer not a default.
5. Translation table: Picturator → "B2C", PicaAPI → "MerchOne" (per Niklavs' definition mid-session).

All edits land in `Documents/GitHub/bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/`.

## Turn log

### T1 — framing + design proposal (2026-05-21)

Principal showed the overkill screenshot. Diagnosed: §0 lines 80–84 and §7 wire the HTML-bundle path as the lightest visual escalation; no inline-chart tier exists between chat and bundle. Proposed three concrete changes — §0 rewording, §7 reshape to four modes, §8 carve-out for inline mode. Asked PNG-in-folder vs side-panel HTML.

### T2 — design clarified

Principal chose: single bare `.html` file (title + description + one chart), small enough to write quickly, opens in Claude Code side panel. Revised proposal accordingly — `visualization-studio/content/charts/claude/YYYYMMDD-HHMMSS--<slug>.html`, single-file, no spec/bundle/sql sidecars.

### T3 — implementation

Wrote `build_inline_chart.py` (~140 lines): pandas + plotly, CLI args (`--data --title --description --chart-type bar|line --x --y` + optional `--orientation --color --slug`), CDN-loaded Plotly JS so the output is one self-contained file. Auto-picks horizontal vs vertical bar by category count.

Edited `how_to.md`:
- §0 "Output mode" subsection rewritten: Mode 2 inline HTML is the new default visual; Modes 3/4 are escalations requiring confirmation.
- §7 reshaped from three modes to four. Mode 2 carries no confirmation requirement; Modes 3 and 4 each carry "confirm before building" lines.
- §8 carve-out: "one folder per request" applies to bundle modes only; Mode 2 is flat-file.
- Script reference and app-structure tree updated.

### T4 — scope-discipline incident (ls permission prompt)

Principal screenshotted a permission prompt for `ls C:\Users\...\shipping-agent\`. Root cause: §10 said "Don't run `ls`, etc. against paths *outside this folder*" — the qualifier was the loophole, and the agent reached for `ls` inside the folder. Tightened §10:
- Banned `cat / ls / find / grep / cd` regardless of path; named `Glob/Read/Grep` tools as the right substitutes.
- Added Windows-specific note: no trailing backslash on paths in bash invocations (parses as escaped quote).
- Added `build_inline_chart.py` to the harness allowlist callouts.

### T5 — narration discipline (the "spewing useless stuff" incident)

Principal showed the shipping-agent narrating "I'll check the table reference for date columns and what source_system values represent TCG shops, then run the query." — multi-sentence pre-action plan narration. Added cross-cutting rule #7: "Acknowledge briefly; don't narrate the plan." One acknowledgment line ("On it.", "Pulling that now."), then silent execution.

### T6 — latency discussion

Principal asked about 2-min response time on a chart request. Root causes diagnosed: (a) over-research at the front — reading reference/ for canonical questions whose answer is already in how_to; (b) re-pulling same-day artifacts that already exist with matching scoping. Added:
- Cross-cutting rule #8: "Don't over-research canonical questions" — how_to is enough for top-N / monthly trends / cost breakdowns; reference/ is for edge cases.
- §7 Mode 2 step 1: check `visualization-studio/content/charts/claude/` for a same-day reusable artifact with matching scoping before re-querying.

### T7 — acknowledgment refinement

Principal pointed out that "On it." is *too* sparse — followed by silent tool calls, it reads as a freeze. Refined rule #7: opening line must restate the scoping plus the action verb. "Top 10 countries by volume, TCG shops, 2025 — pulling now." Compresses Understanding/Plan into one line. Generic "On it." is now sub-target.

### T8 — out-of-perimeter read attempt

Principal showed a permission prompt for `NFE/.claude/reference/shipping-data-mart/overview.md` — agent reaching for a "reference" folder *outside* the shipping-agent. Diagnosed: existing settings.json deny rules use `../**` (relative) patterns which don't match absolute paths; Claude Code's working-dir boundary caught it, but the *behavioral* rule in §10 didn't stop the reach. Tightened §10 with two new lines:
- "Any path that starts with `C:\`, `/c/`, or `..\` is outside this folder by definition."
- "'Reference' means the in-folder `reference/`" — explicit list of the three reference files, ban on reaching for `.claude/reference/`, `NFE/.claude/reference/`, `bi-etl/reference/`, etc.

### T9 — real-world test pass

Principal shared a shipping-agent session transcript: "how much to ship a 20×30 canvas to Germany?" → clean one-line scoping ack ("Pulling avg shipping cost for 20×30 canvas to Germany — TCG production lines, last 12 months."), then silent tool calls, then €2–3 median answer with assumptions in parens. Follow-up: "show cost trends by canvas count" → built `20260521-205041--canvas-20x30-bundle-cost.html` (flat folder, single file, Mode 2 working as designed). Answer included the business insight: marginal shipping cost of a second canvas is 2 cents, strongly supporting a "buy 2" promo. Audit verdict: rules landed cleanly. Two minor nits — Picturator/PicaAPI internal names exposed in parens; turn 1 slightly long due to auto-breakout by sub-platform.

### T10 — naming swap + nit fixes

Principal defined Picturator = B2C, PicaApi = MerchOne. Asked Jebrim to swap and apply the called-out nits. Edits:
- §0 translation table: Picturator → "B2C", PicaAPI → "MerchOne".
- §2 source-systems table rows updated to match.
- `reference/sources.md` section headers updated.
- Rule #3 tightened: "Breakdowns are an offer, not a default" — "how much" questions get one number + assumptions, sub-platform splits surface as a follow-up offer.
- Stale "Six cross-cutting rules" lead-in now reads "Nine cross-cutting rules" after the two adds.

### T11 — quest-log discipline gap surfaced

Principal asked about open quests. Surfaced seven in-progress entries; called out that this session itself had no quest-log entry — substantive work happened in shipping-agent (additional working dir), nothing wrote to gielinor, the lapse was invisible to disk. Principal cued session close with retroactive log + handover note that shipping-agent iterations are still ongoing.

### T12 — post-close follow-up: local-first reach + recovery rule (2026-05-22)

After the S024 close commit (`188707b`), principal surfaced a third scope-discipline incident from a separate shipping-agent transcript: the agent had reached into the NFE folder for a database module instead of using the local `db.py`. The agent's own confession was diagnostic — *"I didn't check what was already in the folder. I saw the shared/database module fail (wrong working directory) and reached for the next thing I knew instead of stopping to look at what was already here."*

Two failure modes compound:

1. **No local inventory before reach.** Agent grabbed for a known-from-training pattern ("shared database module") instead of globbing the shipping-agent folder. `db.py` was sitting next to `how_to.md`.
2. **Recovery moved outward.** When the first invocation failed (wrong cwd → import path miss), the agent's recovery move was "find this helper elsewhere" rather than "the cwd is wrong; fix the invocation." Reaching out is *never* the right recovery; the previous §10 tightenings hadn't covered this specific shape.

Added two rules to §10:

- **"Local-first reach"** — before importing, calling, or invoking any helper not in Python's standard library or `pip install`-able, glob the shipping-agent folder first. Names the existing local helpers and the danger words (`shared/`, `lib/`, `helpers/`, `bi_etl/`, parent project).
- **"Recovery move is closer, not further"** — on script failure, diagnose by asking *what's local I haven't tried*, not *where else could this be*. Reaching outside the folder to find a helper is never the correct recovery.

Together these target the specific gap that the two earlier §10 tightenings (T4: ban shell exploration regardless of path; T8: reference-folder reach) didn't cover. The earlier rules covered *file reads* and *shell exploration*; this one covers *Python imports / script invocations* via cwd-and-PATH side effects.

### T13 — README addition (S025, 2026-05-22)

Principal asked whether the shipping-agent has a README. Confirmed it didn't — only agent-facing entry shims (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `GROK.md`) and `how_to.md`. Wrote a thin human-onboarding `README.md` pointing at `how_to.md` + `reference/` + `visualization-studio/`. Committed `0532678` and pushed.

### T14 — how_to.md split (S025, 2026-05-22)

Principal: *"how_to is a bit too large, brain has patterns we could borrow."* First proposal was mechanical — split by content shape (rules / knowledge / skills). Principal pushed back: *"we're on a good path. But can we do better?"* Forced a deeper read.

The deeper insight: **the brain's structure holds because of mechanisms, not shape.** Routing rule + size budgets + live-vs-stable + harvest discipline + stamps are what prevent reaccretion. Without them, any split rots to monolith in 3 months because new gotchas default to the path-of-least-resistance file.

Principal vetted six proposed points; four survived:

- **Live vs stable** — separate dated observations (coverage, DQ, source-maturity) from contract knowledge (pipeline, columns).
- **Always-loaded vs on-cue** — the actual splitting axis. `how_to.md` is the keepsake-equivalent; `reference/` + `skills/` are bank/spellbook-equivalents.
- **Audience tags** — each file declares AI / AI + analyst / human.
- **Stamps on live entries** — `last-verified: YYYY-MM-DD` + re-verify probe pointer (cheap, kept).

Dropped: **routing rule + size budgets** (agent doesn't self-modify, so the discipline lives in maintainer sessions, not in the agent's docs). **Harvest mechanism** reframed as Jebrim's responsibility, not the agent's.

Split landed:

- `how_to.md` 793 → 313 lines (−60%). Kept §0 + §7 + §8 + §10 + new §1 "Where to find things" index.
- `reference/mart-contract.md` (new) — §1 pipeline + §3 structure + §4 silver reference. STABLE.
- `reference/known-dq.md` (new) — §9. LIVE, per-entry stamps.
- `reference/sources.md` — extended with source-maturity table (LIVE) at top.
- `reference/_about.md` (new) — orientation.
- `skills/query-patterns.md` (new) — §5 join rule + example. STABLE.
- `skills/_about.md` (new) — orientation.
- `README.md` extended with §6 connection setup.

Committed `e15777a`, pushed.

### T15 — harness/ restructure (S025, 2026-05-22)

Principal: *"small restructure needed — python scripts mainly."* Moved the five `.py` files + `sample_queries.sql` into a new `harness/` folder. Updated `BASE_DIR = Path(__file__).resolve().parent.parent` in each script so folder-root anchoring still works (`.env` lookup at root, `visualization-studio/content/...` output paths). Updated doc references in `how_to.md`, `README.md`, and `visualization-studio/STANDARDS.md`. `.claude/settings.json` unchanged — its `./` / `../` patterns still match the new layout.

Smoke test: `python harness/connect_redshift.py --query "SELECT 1 AS smoke;"` returned a row from the new location. `from db import …` resolves via Python's script-local `sys.path[0]` (the `harness/` directory) — no `__init__.py` or `PYTHONPATH` needed.

Committed `d0d8386`, pushed.

### T16 — cost vocabulary + % invoiced reporting rule ([[S026_2026-05-22_shipping-costs-nextjs-architecture-read|S026]], 2026-05-22)

Principal flagged friction: the shipping-agent doesn't distinguish `real_shipping_cost_eur` (invoiced, trusted) from `expected_shipping_cost_eur` (pre-invoice approximation) from `final_shipping_cost_eur` (the coalesce). Wants a doc addition that teaches the agent (a) when to use which column, (b) to report what % of any cost figure is invoiced.

Column model confirmed from prior Jebrim work (`S001` L87, `S014_d1` L36/L50, `S023`):

- `real_shipping_cost_eur` — carrier-invoiced; high trust.
- `expected_shipping_cost_eur` — rate-card / negotiated-rate estimate; medium trust; available pre-invoice.
- `avg_shipping_cost_eur` — historical-average fallback; low trust.
- `final_shipping_cost_eur = COALESCE(real, expected, avg)`; `cost_source` flags which one populated it.

State update (principal, T16): the prior "fact_shipments cost cols 100% NULL outside Phase 5" finding from [[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]] D1 / [[S023_2026-05-21_shipping-mart-coverage-audit|S023]] is **stale** — the cost cols are now wired and populated. The caveat has been stripped from the bank draft.

Constraint: `bi-analytics-main` repo is **not present on this machine** (`Test-Path` = False). Cannot edit `shipping-agent/` docs directly. Drafted the column-vocabulary and the doc-edit proposal text into Jebrim's bank/drafts so the next bi-analytics session can apply it without re-thinking.

% invoiced weighting decided by principal: **euro-weighted** — `SUM(real)/SUM(final)` over the same filter as the headline. Surface the `real + estimated` breakdown when % invoiced < 95%. Low % invoiced on current-week/month-to-date windows is expected, not a defect (invoice lag).

Output: `gielinor/players/jebrim/bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md` — contains both Jebrim's durable column model and the exact proposal text for `reference/mart-contract.md` (new "Cost columns" subsection) + `how_to.md` §0 (new rule on % invoiced reporting).

**Addendum (T16b):** Principal added — cost-bucket grain rule. Buckets (11 `bkt_*` cols on `fact_shipment_cost_summary`) exist only on invoiced rows; expected/avg are single shipment-level totals with no breakdown. Therefore `final_shipping_cost_eur` carries bucket detail only when `cost_source = 'real'`, and an order's final cost is shipment-level only — no order-level column, no sub-shipment grain unless every shipment in scope is invoiced. Added as a separate section in the bank draft and folded into the §0 rule wording ("If the answer includes a bucket breakdown, state that the breakdown reflects only the invoiced subset").

### T17 — local-files channel (discussed + parked, 2026-05-22)

Principal raised the multi-consumer problem: shipping-agent ships via GitHub, BI team pulls updates, but each user also needs a place for personal rules / preferences / scratch that survives reclones and doesn't get clobbered by pulls.

Discussed shape (recommendation, not decided):

- `.local.md` **sidecar pattern** next to each shipped `.md` — `CLAUDE.local.md`, `how_to.local.md`, `notes.local.md`, etc. Claude Code's directory walk auto-loads `CLAUDE.local.md` after canonical; the rest are reference-on-demand. Wins over a `local/` folder for shipping-agent's small surface (~6 shipped docs).
- `.gitignore` covers `*.local.md`, `local/`, `.env`.
- Two open decisions for next time: (1) ship a `CLAUDE.local.md.example` template vs minimal README-only documentation; (2) personal-rule override status — silent override, agent-flagged override, or append-only.

Working recommendation: scaffolded (1b) + silent override (2a) — lightest thing that works.

Status: **parked**. Picks up when shipping-agent has enough users feeling friction from the lack of a local channel. No code/doc changes made. Pointer added to S024 inventory under "Parked ideas."

## Decisions

- **Inline HTML as the new visual default** — confirmed with principal in T2. Bundle modes shift to "ask before building."
- **Translation table replaces long phrases with single business names** — `B2C` / `MerchOne` instead of "our main EU shop platform" / "our newer customer-facing platform." Shorter, more aligned with how Niklavs actually refers to them.
- **Behavioral fix > settings.json deny tightening** for out-of-perimeter reads — settings.json deny rules use relative-path patterns and can't catch absolute paths without also denying the working dir. The behavioral rule in §10 is the load-bearing fix; deny patterns are backstop only.
- **Did not backfill old generated artifacts** (`visualization-studio/content/generated/claude/20260521-120000--tcg-2025-shipments-by-country/`) that still carry the pre-swap "main EU shop platform" phrasing. Those are historical bundles; not worth touching.
- **`harness/` over `bin/` or `scripts/`** (T15) — docs already call them "the harness"; naming alignment is cheap.
- **Stamps + audience tags adopted as doc-quality discipline** (T14). LIVE files carry per-entry `last-verified` stamps + re-verify probes; STABLE files don't need them. Every file declares its audience at the top.
- **Mechanism > shape** (T14, load-bearing). When proposing a structural restructure, the visible split is the easy part; the underlying mechanisms determine whether it holds. First-pass instinct was to optimize for shape; principal push forced the mechanism-first reading. Recorded as a skill draft below.

## Discipline note — quest-log open lapse

The whole session ran without an in-brain quest-log entry. Per `gielinor/meta/death-and-spawn.md`, every turn should append to `quest-log/in-progress/` of the active player. The lapse:

- Session opened with `hey jebrim` at message start (T0). Jebrim activated cleanly per the address rule.
- All substantive work landed in the **additional working directory** (`shipping-agent`), not in `gielinor/`. No edits to gielinor → no on-disk evidence that a Jebrim session was active.
- The lapse was invisible until T11 when principal asked.

This entry is the retroactive open. The turn log above is reconstructed from in-context recall (no transcript), so it captures shape and decisions but not every micro-action. The harvest below records the lesson.

### T18 — cost-basis disclosure + denominator-matches-numerator (2026-05-22, S028)

Principal flagged a real shipping-agent transcript that exposed two gaps in the T16 cost-vocab rule:

**Failure 1 — reactive disclosure.** Agent answered "€5.24 per parcel for TCG in April 2026 — €1.45M total spend across ~276K parcels" without naming the cost basis. Principal had to ask: "is this based on real or also expected cost?" Agent then disclosed "Real cost only." Correct, but reactive. The T16 rule didn't make basis-upfront unmissable.

**Failure 2 — wrong-denominator average framed as a "floor."** Agent's query was `SUM(c.total_eur) / NULLIF(COUNT(DISTINCT f.shipment_id), 0)` with `LEFT JOIN fact_shipment_cost_summary` — numerator restricts to invoiced rows (because `total_eur` is NULL for non-invoiced), denominator counts all parcels. Produced €5.24 and called it "a floor, not a final number." When asked to restrict to invoiced parcels: €6.29.

The "floor" framing is the load-bearing bug. €5.24 is not a floor — it's `real_per_shipment × (% shipments invoiced)`, a single number with two distortions baked in. Leading with it anchors the principal on a value below any plausible truth. The right answer leads with €6.29 (invoiced-only) and optionally surfaces a population-weighted final-cost average alongside.

**Sharpening landed in `bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md`.** Two new sections inserted before "The reporting rule — % invoiced":

- **"Cost basis disclosure — state upfront, not on follow-up."** Three bases named (invoiced-only / final / estimated-only), why upfront matters (basis frames trust), 2026-05-22 anchor, wording template.
- **"Average denominators — must match numerator scope."** Valid-pairings table (real → invoiced; final → costed); invalid-pairing table (real → all); the "floor framing is wrong" reasoning; 2026-05-22 anchor; operational shape (default invoiced-only, surface population-weighted final when <95% invoiced, lead with final on recent windows where lag is expected).

**§B doc-edit proposal expanded** from ~110 words to ~180 — now reads as five sub-rules under one numbered §0 entry: (1) open with basis, (2) match denominators, (3) default to invoiced-only headline, (4) report % invoiced, (5) flag bucket breakdowns as invoiced-only. Added a worked-example block showing the wrong shape vs the two right shapes using the April 2026 numbers, suggested as a `reference/mart-contract.md` or `skills/query-patterns.md` reference.

**Status:** still blocked on next session in `bi-analytics-main/` working dir for the doc-edit apply. Inventory updated.

**Pattern worth flagging.** The T16 rule existed and the agent still produced the wrong shape. Two reads:

1. Rules buried inside §0 don't fire reliably when the agent is mid-query. The new wording leads with the most behavioral sub-rules (basis upfront, denominator matching) before the calculation-detail sub-rule (% invoiced formula).
2. A worked example is load-bearing for arithmetic rules in a way prose isn't. Added the wrong/right shapes as a concrete reference. Without it, the agent has to re-derive the right denominator each time.

Both worth carrying into how skills/rules get written generally — possible spellbook/drafts/skills/ entry: "arithmetic-rules-need-worked-examples-not-prose." Not drafting yet; waits for a second occurrence of the same shape.

### T19 — standalone cutover proposal (2026-05-22, S028)

Principal surfaced two coupled changes plus an explicit posture goal:

1. **Gold layer landed as `shipping_mart` schema.** Replaces `enterprise_silver.*` for the four canonical facts: `fact_shipments`, `fact_shipment_cost_summary`, `fact_shipment_orderitems`, `fact_shipment_invoice_lines`.
2. **`ship_mart_ro` read-only user restored** (was deprovisioned mid-S022 per old keepsake). New creds.
3. **Posture goal: agent can be moved anywhere.** Standalone = relocatable. The shipping-agent folder should run with only its own `.env` and `harness/` — no walk-ups to parent `.env`, no reaches to NFE-side reference content.

**Local-repo verification (T19).** All three repos present locally (`bi-analytics-main`, `bi-analytics`, `bi-etl`). Concrete state:

- 16 shipping-agent files reference `enterprise_silver.{fact_shipments|fact_shipment_cost_summary|fact_shipment_orderitems|fact_shipment_invoice_lines}` — the cutover change surface. Includes one historical generated query (`visualization-studio/content/generated/claude/20260522-082530--uk-2026-tcg-shipping-export/query.sql`) — historical artifact, leave it; the other 15 flip.
- No `.env` or `.env.example` in `shipping-agent/` — credential decoupling needs to create both.
- bi-etl `dags/` has only `enterprise_silver/` and `enterprise_bronze/` — **no `enterprise_gold/` or `shipping_mart/` folder**. The gold-layer ground truth is not in bi-etl. Open question: Glue / dbt / separate repo / different folder name?

**Proposed change surface (presented to principal):**

- **A. Credentials / config** — create `shipping-agent/.env` + `.env.example`; verify `.gitignore`; tighten `harness/db.py` to explicit single-file load (no walk-up).
- **B. Schema flips** — 15 files (excl. historical generated query): `mart-contract.md`, `tables.md`, `sources.md`, `coverage-audit.md`, `known-dq.md`, `query-patterns.md`, `README.md`, `harness/connect_redshift.py`, `harness/db.py`, `harness/sample_queries.sql`, `visualization-studio/STANDARDS.md`, `visualization-studio/lib/standards.js`, `visualization-studio/app/page.js`, `visualization-studio/content/light-presentation-template.json.example`, `visualization-studio/content/generated/claude/20260521-120000--tcg-2025-shipments-by-country/{spec.json,query.sql,index.html}`. Carefulness rule: only the four named facts flip; `map_shipment_key`, `dim_*` stay where they are.
- **C. Standalone severance** — `how_to.md` §10 caveat (drop credential exemption), older NFE-side reference pointer (drop entirely; relocatable goal forbids), `README.md` § Connecting (rewrite setup).
- **D. Behavioral rule** — new §0 cross-cutting on schema discipline (qualify as `shipping_mart.<table>`, never assume `search_path`).
- **E. Brain-side** — keepsake proposal, cost-vocab cutover-tag, this quest-log entry, S024 inventory update.

**Principal cued:** start brain-side (E), then bi-analytics-main session for A–D in one tranche, fold T16/T18 cost-vocab apply into the same commit.

**Brain-side outputs (this session):**

- `players/jebrim/keepsake/proposals/2026-05-22_shipping-data-mart-routing-post-cutover.md` — supersedes the 2026-05-21 routing pin. Captures new schema, local-env connection, standalone posture, ground-truth-TBD placeholder, plus the four open items for the apply session (`ship_mart_ro` grants on silver dims, whether old `enterprise_silver.fact_*` linger as deprecated views, bucket-grain survival, bi-etl gold path).
- Cost-vocab draft (`bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md`) — added schema-cutover note at the top. Unqualified `fact_*` references stay unqualified in the draft (schema-agnostic); the apply qualifies them as `shipping_mart.<table>` in `reference/mart-contract.md`.
- This T19 entry.
- S024 inventory updated with cutover-apply tranche.

**Open items deferred to apply session (verify during the cutover):**

1. `ship_mart_ro` grant scope — does the user have SELECT on `enterprise_silver.map_shipment_key`, `enterprise_silver.dim_*`? If not, every join breaks; need either grants on silver or confirmation that gold brought dims along.
2. Old `enterprise_silver.fact_*` for the four tables — gone, or kept as deprecated views/aliases? Affects whether the schema-discipline rule has lower stakes during transition.
3. Bucket grain + `cost_source` flag survived cutover unchanged? T16/T18 cost-vocab assumes yes.
4. bi-etl ground-truth path for the gold layer — not in `dags/`. Surface during the apply.

**Pattern noted (not drafted yet).** Two changes landed near-simultaneously that should have been independent: schema cutover (technical) and standalone posture (architectural). They're being treated as one tranche because the credential decoupling has to happen for the agent to actually use the new schema (with the restored user). Worth flagging if this couples again later: standalone posture is a one-time event, but schema cutovers will recur — keep the second one mechanically separable from the first if possible. Not a draft yet; waits for a second occurrence.

### T20 — gold verification + scope narrowing (2026-05-22, S028)

Principal answered the apply-session open questions from T19. Two coupled outcomes: empirical verification against gold + scope narrowing from 7+24 tables to **4 facts only**.

**Gold schema verified via `ship_mart_ro` against `information_schema.columns`** (128 columns across 4 tables). Key findings:

- **`map_shipment_key` fully denormalized into `shipping_mart.fact_shipments`.** All 9 spine columns present on the fact (`shipment_id`, `trackingnumber`, `shop_ordernumber`, `source_system`, `source_order_id`, `shop_order_created_date` [renamed from `order_created_date`], `shippingprovider_extkey`, `updated_at`, `dw_timestamp`). No spine join needed.
- **`dim_shipping_providers` mostly denormalized.** Present on fact: `shipping_provider_id`, `shippingprovider_extkey`, `shipping_provider_group` (silver: `shippingprovider_group`, gold normalized name). Missing from gold fact: `service_type`, `truck_provider`, `has_truck_cost`. Principal: drop the three missing fields from agent scope (no user-facing query uses them).
- **`fact_truck_charges` not in gold.** Principal confirmed drop — internal plumbing only.
- **Carrier name mapping.** `shipping_provider_group` (high-level, e.g. "DHL", "FedEx") is the field for user-facing carrier breakdowns; `shippingprovider_extkey` is service-level (raw external key). Sample silver query referenced `dim_shipping_providers.shippingprovider_name` which doesn't exist in either silver tables.md or gold — phantom column. Use `shipping_provider_group`.

**Cost-vocab assumption corrections from live verification:**

- **`cost_source` values:** assumed `'real'` / `'expected'` / `'avg'`. Actual: `'invoice'` (65.15%), `'expected'` (24.37%), NULL (8.04%), `'avg'` (1.99%), `'invoice_estimate'` (0.45%). The `'real'` → `'invoice'` rename is a value-level rename, not a column rename — `real_shipping_cost_eur` is still the column name. Naming asymmetry to flag.
- **`'invoice_estimate'`** is a transient remnant being renamed upstream to `'invoice'`. Principal: ignore in docs. Don't add as a fifth category.
- **NULL `cost_source` at 8%** is larger than original T16/T18 draft assumed when writing the edge-cases section. Worth surfacing in the rule.
- **Buckets do NOT have `bkt_` prefix.** Gold (and silver — original T16 draft was wrong on this) has 13 bucket columns named directly: `base_rate_eur`, `truck_charges_eur`, `fuel_surcharge_eur`, `remote_area_charges_eur`, `peak_demand_charges_eur`, `oversize_overweight_eur`, `residential_eur`, `discounts_eur`, `credit_note_eur`, `other_eur`, `unclassified_eur`, `tax_eur`, `customs_duties_eur`. Each in `_eur` + `_local` pairs.
- **Bucket invariant** verified across 200K-row sample: `SUM(11 included buckets in EUR) == total_eur` with max diff 0.00. `tax_eur` and `customs_duties_eur` are **excluded** from `total_eur` (consistent with silver contract).
- **Cross-row invariant** verified across all 12.03M `cost_source = 'invoice'` rows: `fact_shipment_cost_summary.total_eur == fact_shipments.real_shipping_cost_eur == fact_shipments.final_shipping_cost_eur`.

**Principal scope decisions:**

1. **Agent scope = 4 gold facts only.** No `enterprise_silver.*` references in agent docs at all. Source-side lineage (~24 carrier invoice tables previously documented in `reference/sources.md` etc.) gets stripped — defer to bi-etl docs if lineage understanding is needed. Possible future extension: agent gains access to raw invoices, but not now.
2. **Drop spine + dim references.** `map_shipment_key`, `dim_shipping_providers`, `fact_truck_charges` — gone from agent docs. Data lives on `fact_shipments` directly.
3. **Drop missing dim fields.** `service_type`, `truck_provider`, `has_truck_cost` — not in gold, not used.
4. **Ground-truth path stays** at `bi-etl/dags/enterprise_silver/shipping_data_mart/` transitionally — bi-etl dags being repointed to gold; path will move with them.

**Brain-side outputs landed in T20:**

- `bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md` — full rewrite (not just qualification). Reflects actual gold values, 11-bucket invariant with correct column names, `'invoice'` value rename, NULL-at-8% edge case, defensive SQL, naming-asymmetry flag, gold-verified `cost_source` distribution table.
- `players/jebrim/keepsake/proposals/2026-05-22_shipping-data-mart-routing-post-cutover.md` — tightened with 4-table scope, denormalization confirmation, gold-verified `cost_source` values, schema-perimeter rule.
- This T20 entry.
- S024 inventory updated with the full concrete apply plan (next entry below in S024 quest-log timeline).

**Pattern noted (worth holding for skill-draft consideration).** The T20 verification exposed three layers of "stuff we assumed without checking":

1. `cost_source` values (`'real'` vs `'invoice'` — wrong from [[S001_2026-05-20_repo-orientation|S001]] forward).
2. Bucket column shape (`bkt_*` prefix — wrong from the original cost-vocab sketch).
3. Phantom column `dim_shipping_providers.shippingprovider_name` referenced in sample_queries.sql but never existed in documented schema.

All three would have shipped to the agent unchanged if Niklavs hadn't asked for verification. **Skill candidate:** "verify mart contracts against `information_schema` before promoting any rule that depends on a column name or enum value." Not drafting yet — waits for a second occurrence of "assumed-vs-actual" gap.

**Apply session is now fully concrete** — see updated S024 inventory for the single-commit tranche. Still blocked only on §10 perimeter (next session opened in `bi-analytics-main/`).

### T21 — apply executed + commits (2026-05-22, S028)

Principal cued "lets tackle the actual agent" — proceeded with the apply from this session despite the §10 wd-switch convention (Jebrim doing maintainer work on the shipping-agent is principal-level, not the agent operating; brain context was loaded; cost of switching > cost of single-session edit).

**Apply executed in 6 phases:**

- **A — Credentials.** Wrote `shipping-agent/.env` with `ship_mart_ro` creds; created `.env.example` template. Stripped unused Oracle/ANTHROPIC/TCGPT env vars from `.env` (no shipping-agent code references them). `db.py` `_locate_env()` already does single-file load — no code change needed. Smoke-test: connected as `ship_mart_ro` ✓.
- **B + C — Schema flips + 4-table doc stripping.** 16 files touched. All `enterprise_silver.fact_*` references for the 4 facts → `shipping_mart.fact_*`. `map_shipment_key` / `dim_shipping_providers` / `fact_truck_charges` / ~24 carrier invoice tables stripped per principal scope. `reference/sources.md`, `reference/tables.md`, `reference/mart-contract.md` rewritten; `skills/query-patterns.md` rewritten (no more fact→spine→dim walk); `harness/sample_queries.sql` + `connect_redshift.py` DEFAULT_QUERY rewritten; `README.md` rewritten with new setup flow; visualization-studio files (STANDARDS.md, lib/standards.js, app/page.js, light-presentation-template.json.example) flipped.
- **D — Standalone severance.** Older NFE-side reference pointer was in README's Related section (rewritten); how_to.md §10 already had no credential-walk-up caveat to drop.
- **E — Schema-perimeter rule (§0 rule 10).** Added: `shipping_mart` only, never assume `search_path`, reaching for other schemas is a scope violation. Bumped §0 lead-in from "Nine cross-cutting rules" → "Eleven."
- **F — Cost-vocab insertions.** §A landed as `reference/mart-contract.md` § Cost columns (full vocabulary + verified `cost_source` distribution + 11 bucket names + invariants + worked example). §B landed as how_to.md §0 rule 11 (basis upfront, denominator matching, % invoiced reporting).

**Three pre-apply assumptions caught by live verification (T20 → T21 carry):**

1. `cost_source` values: assumed `'real'`. Actual: `'invoice'` (65%) / `'expected'` (24%) / NULL (8%) / `'avg'` (2%) / `'invoice_estimate'` (0.5%, transient remnant). Renamed throughout cost-vocab + how_to §0 rule.
2. Bucket columns: assumed `bkt_*` prefix. Actual: no prefix; 11 columns named directly + 2 excluded (tax, customs). Corrected.
3. `dim_shipping_providers.shippingprovider_name`: phantom column (never existed in silver schema either; only in sample_queries.sql usage). Replaced with `shipping_provider_group` per principal guidance (high-level "DHL"/"FedEx"; `shippingprovider_extkey` is service-level).

**Smoke tests (all green):**
- `SELECT 1` as `ship_mart_ro` ✓
- `shipping_mart` schema sanity — 4 tables, 128 cols total (fact_shipments 65, cost_summary 32, invoice_lines 17, orderitems 14)
- April 2026 TCG row count → 276,490 (transcript said 276,483; +7 = data growth)
- Invoiced-only avg cost reproduces: **€6.95 / 209,874 parcels** (vs silver-era €6.29 / 231K — ~21K fewer invoiced parcels in gold for same slice, likely tighter matching post-cutover)
- Schema perimeter probe: `SELECT 1 FROM enterprise_silver.fact_shipments` → permission denied ✓

**Commits + push:**

- `bi-analytics-main` `7e74670` — "shipping-agent: cutover to shipping_mart gold + standalone" (16 files, +591 / −746 lines net). Pushed to origin/main.
- `brain` `cbf1766` — "S024 T19-T20: shipping-agent gold cutover — brain-side" (4 files: cost-vocab draft rewrite, keepsake proposal, S024 quest log T19+T20, S024 inventory). Pushed alongside pre-existing S027-close commit (`7c3aff0`).

**One residual flag deferred:** the €6.29 → €6.95 invoiced-avg shift between silver and gold for the same April-TCG slice. Documented in commit message; not blocking. Possible explanation: gold's invoice-matching logic is stricter (fewer borderline shipment_id matches accepted), so the invoiced denominator shrunk by ~21K while preserving the per-shipment cost structure. If this matters for any downstream consumer, investigation is its own task.

**Watch points carried to inventory:**
- Real shipping-agent sessions against the new structure (does the agent route new gotchas correctly post-rewrite? does `shipping_provider_group` granularity match user expectations?)
- gold-dag ground-truth path when bi-etl repoint lands
- §0 rule firing reliability (per-T18-onward watch)

## Pending drafts
