# S023 — Shipping Data Mart coverage audit

**Opened:** 2026-05-21
**Player:** Jebrim
**Trigger:** Principal flagged that another agent (a TTYD instance) raised something concerning during a uk.photo.gifts investigation — specifically that ~27% of shipments lack cost data, that Wolfen's carrier-cost wiring is "still being wired up" (€0 cost on Wolfen→DHL/UPS parcels), and that external print partners (Allcop, LaserTryk) ship at >95% cost-to-revenue. Principal wants an independent coverage check across the whole mart, sliced by source × carrier × country, before accepting the framing.

## Scope

- Mart-wide coverage audit, not shop-scoped.
- Costs: `enterprise_silver.fact_shipment_cost_summary.total_eur` (per §7 of how_to.md — `fact_shipments.final_shipping_cost_eur` is V0-NULL outside the Phase 5 backfill cycle).
- Revenues: `fact_shipments.net_revenue_eur` (rollup from `fact_shipment_orderitems`).
- Default window: `order_created_date >= '2025-01-01'` (covers full PicaAPI history + ORWO wiring period). Adjust as findings dictate.
- Output mode: chat. Lift to HTML only if the size of the breakdown demands it.

## Other-agent claims to verify

1. **Cost data coverage: ~27% NULL across the mart** (other agent's claim, uk.photo.gifts scope).
2. **UPS especially: 86% of UPS shipments missing carrier invoices** (other agent's claim, uk.photo.gifts scope).
3. **Wolfen→DHL and Wolfen→UPS show €0 because bulk-bill allocation "still being wired up"** — how_to.md §2 says `dhl_orwo.sql` / `ups_orwo.sql` carry distributive allocation and are wired. The two stories conflict; probe will settle it.
4. **External print partners (Allcop ~109%, LaserTryk ~95%) shipping at high cost ratio** — verifying this is downstream of cost-coverage; if cost is missing on those, the ratio is unreliable.

## Turn log

### T1 — respawn + framing (2026-05-21)

- Respawned cleanly. Three in-flight quests on disk (S001 paused, S002 multi-thread, S015 dogfood pending). Principal chose fresh investigation, not resume.
- Loaded shipping-agent `how_to.md` to refresh schema. Key constraint surfaced: cost reads must use `fact_shipment_cost_summary.total_eur`, not `fact_shipments.final_shipping_cost_eur` (V0 says fact-side cost cols are NULL outside Phase 5 cycle).
- Quest log opened, tasks created.

### T2 — coverage by source_system (2026-05-21)

Window: `order_created_date >= '2025-01-01'`. Cost = `fact_shipment_cost_summary.total_eur IS NOT NULL`.

| Source | Shipments | Cost % | Revenue % |
|---|---:|---:|---:|
| Picturator | 5,005,768 | 86.7% | 99.3% |
| ORWO | 2,506,429 | 68.7% | 0.0% |
| PicaAPI | 1,192,685 | 93.9% | 99.6% |
| PCS | 15,919 | 68.7% | 0.0% |
| Rewallution | 957 | 97.9% | 100.0% |

Mart-wide cost coverage ~85% (not ~73% as the other agent's framing implied). ORWO revenue 0% known per how_to §4 (in progress). PCS revenue 0% by design.

### T3 — source × carrier × country drill (2026-05-21)

Per source × carrier (rows ≥1K):

- **ORWO POST = 0.4% coverage on 567,930 shipments.** The biggest concentrated hole.
- **ORWO DHL = 91.7% on 1.77M.** Wired and healthy in aggregate.
- **ORWO UPS = 58.8% on 155K.** Partial — see T4.
- **Picturator (unresolved carrier_group) = 44.4% on 334K.** Decomposed in T3a.
- **Picturator MAERSK = 68.9% on 98K**, with Sweden the weakest sub-slice (17.4% on 3.5K).
- **Picturator ASENDIA = 0% on 5.8K** (separate from ASENDIA USA, which is 97.1% on 70K).
- **Picturator DHL/UPS** = 87.6% / 87.4%. The other agent's "86% of UPS missing carrier invoices" does **not** hold mart-wide.

ORWO `destination_country` is **100% blank** on every row in this window — confirming the S002 thread "destination_country wiring problem". Country slice on ORWO is impossible until that lands.

### T3a — Picturator (unresolved) extkey decomposition

| extkey | shipments | cost % | reading |
|---|---:|---:|---|
| `POST_DVF` | 169,764 | 0.0% | Deutsche Post variant — no invoice source. The Germany hole. |
| `USPS` | 151,235 | 98.1% | Dim didn't catalog it, but cost flows. Cosmetic dim gap. |
| (NULL extkey) | 12,669 | 0.0% | Spine carries no provider key. |

How_to §9's "bare-DHL / bare-UPS / UPSWWE / DHLWPINT" story does **not** appear in 2025+ data. Either §9 is stale or the 2026-05-21 `dim_shipping_providers` refactor (`356a565b6`) caught those variants. Worth flagging.

### T4 — ORWO bulk-bill claim verification (2026-05-21)

By-month coverage of ORWO DHL / UPS / POST (window 2025-10-01+):

| Month | DHL | UPS | POST |
|---|---:|---:|---:|
| 2025-10 | 68.0% | 60.6% | 0.9% |
| 2025-11 | 98.1% | **4.4%** | 0.7% |
| 2025-12 | 97.4% | **11.6%** | 0.3% |
| 2026-01 | 99.1% | 91.0% | 0.2% |
| 2026-02 | 98.9% | 98.0% | 0.3% |
| 2026-03 | 98.9% | 99.5% | 0.4% |
| 2026-04 | 98.6% | 98.5% | 0.5% |
| 2026-05 | 27.5% | 21.5% | 0.2% (invoice lag) |

Verdict on the other agent's claim:

- **"Wolfen DHL = €0" is false** in aggregate and false in every month except the in-flight current month (invoice-lag artifact). 97-99% Nov 2025 → Apr 2026.
- **"Wolfen UPS = €0" is partially true historically** — Nov–Dec 2025 were 4–12% (real wiring issue). Recovered Jan 2026; now 98%+.
- **"Wolfen bulk-bill allocation still being wired up" is wrong as stated.** It IS wired (per §2 of how_to: `dhl_orwo.sql`, `ups_orwo.sql` use distributive allocation). The Nov-Dec 2025 UPS gap was a real defect that's since been fixed.
- **The real ORWO coverage hole the other agent missed: ORWO POST = 0.2–0.9% every month** (568K parcels for 2025+ window). No bulk-bill source for ORWO POST.

## Summary findings (mart-wide, 2025-01-01+ window)

**Cost coverage:**

- Mart-wide: ~85% of shipments have a `fact_shipment_cost_summary.total_eur`.
- Healthy carriers (>95% covered): Picturator YODEL/FEDEX/ONTRAC/GLS/DPD UK/ASENDIA USA/COLIS PRIVE/APG, PicaAPI DHL/FEDEX/GLS/COLIS PRIVE/YODEL/DPD UK, ORWO DHL (Nov 25 onward), Rewallution all.
- **Real coverage holes** (concentrated, fixable):
  1. **ORWO POST — 568K shipments, 0.4% covered.** No bulk-bill source. The single biggest hole in the mart.
  2. **Picturator POST_DVF — 170K shipments, 0% covered.** Deutsche Post variant, no invoice source. Concentrated on Germany.
  3. **Picturator MAERSK — 98K shipments, 68.9% covered.** Sweden the weakest (17.4%). Pattern-of-allocation issue worth probing.
  4. **Picturator ASENDIA (not "USA") — 5.8K at 0%.** Likely a deferred-carrier label that shouldn't be live on the spine.
- **Recurrent invoice-lag** on the current month (~21–28% on big carriers) — normal cadence, not a defect.

**Revenue coverage:**

- Picturator 99.3%, PicaAPI 99.6%, Rewallution 100%.
- ORWO 0% (in progress, intended-populated per §4).
- PCS 0% by design (cost-only source).

**Country dimension:**

- Available on Picturator + PicaAPI (Germany / UK / US / France / Sweden / etc. resolve cleanly).
- **Unavailable on ORWO** — `destination_country` is 100% blank. S002 thread is still open on this; until it lands, no country slice on ORWO is possible.

## Bank-note candidates (drafts post-quest)

- `coverage-audit-mart-wide-2025-windowed.md` — the matrix above as a durable reference.
- `orwo-post-no-bulk-bill.md` — note the structural gap; suggest follow-up with Grzegorz/ETL on whether an ORWO POST allocation source exists or is in the roadmap.
- `picturator-post-dvf-no-invoice-source.md` — flag a single-carrier hole.
- Possible `how_to.md` §9 patch — the dim-coverage gap description doesn't match current data; needs a regenerated audit or a softer wording.

### T5 — implementation pass (2026-05-21)

Principal asked "how will we implement this in short" — agreed plan:

1. Add `§0` rule 7 to `how_to.md` (coverage questions need time + source axis).
2. Add `§2` source-maturity subsection.
3. Patch `§9` with last-verified stamp + corrected unresolved set; point to `reference/coverage-audit.md`.
4. Drop matrix into new `shipping-agent/reference/coverage-audit.md`.
5. Drop Jebrim skill draft: methodology rule survives outside the shipping-agent folder.
6. Drop Jebrim bank-drafts breadcrumb linking to the external audit file.

`§9` rewrite is "tight" per principal — only the dim-coverage subsection gets rewritten; the carrier-ts NULL extkey table is a different phenomenon and stays.

### T6 — close-session (2026-05-21)

Principal cued *"lets commit the shipping agent. Then lets close the session with a handover which will continue iterating on the shipping agent."*

External commits landed (both in `bi-analytics-main`, separate from brain):

- `4952b65` — *S023: shipping-agent restructure + coverage knowledge layer*. Destination side of the S022 restructure (TTYD → `shipping-agent/` + `_TTYD-template/` split), plus `reference/coverage-audit.md` (new) + the three `how_to.md` patches (§0 rule 7, §2 maturity, §9 dim-coverage rewrite).
- `0b4ea40` — *S023: remove old 3_shipping_data_mart_TTYD/ path*. Source-side deletions; two commits because pathspec on the first commit only picked up the destination tree.

Close-session harvest (Pump 2):

- Skill draft already on disk (`coverage-questions-time-and-source-axis.md`) — written T5.
- Bank-note breadcrumb already on disk (`shipping_mart_coverage_audit_2026-05-21.md`) — written T5.
- New examine self-observation: `examine/drafts/2026-05-21-cross-project-read-context-as-advantage.md`. Anchored to the principal's *"what made you so much smarter"* question — Jebrim's wider read context is the structural advantage over folder-scoped agents, not raw intelligence.
- New niksis8_character observation: `niksis8_character/drafts/2026-05-21-niklavs-verifies-agent-claims-by-cross-checking.md`. Anchored to the opening turn — Niklavs treats agent outputs as hypotheses to verify, not facts to act on.

No keepsake proposal earned this session. Existing pin (`Shipping Data Mart — routing`) already covers the routing surface; the coverage-audit doesn't earn an independent pin while it's downstream of that.

Inventory resume tightened to `inventory/S023-shipping-mart-coverage-audit-resume.md` — frames the umbrella iteration thread with six options for next session.

S023 quest **stays in-progress** as the umbrella thread for continued shipping-agent iteration. Audit phase shipped; backlog of four cost-coverage holes + how_to follow-ups + S015 dogfood + reference build-out remains.

## Pending external actions

`completed` 2026-05-21:

- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/coverage-audit.md` — created.
- `how_to.md` §0 rule 7 — added.
- `how_to.md` §2 "Source maturity (V1 status)" subsection — added.
- `how_to.md` §9 — stamp + pointer + rewritten dim-coverage subsection.
- `players/jebrim/spellbook/drafts/skills/coverage-questions-time-and-source-axis.md` — created.
- `players/jebrim/bank/drafts/notes/projects/shipping_mart_coverage_audit_2026-05-21.md` — created.
- `players/jebrim/examine/drafts/2026-05-21-cross-project-read-context-as-advantage.md` — created (T6 harvest).
- `players/jebrim/niksis8_character/drafts/2026-05-21-niklavs-verifies-agent-claims-by-cross-checking.md` — created (T6 harvest).
- `bi-analytics-main` commits `4952b65` + `0b4ea40` — landed.

No pending external actions.
