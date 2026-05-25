# S065 — shipping-agent org-repo migration

**Session:** 48847e45 · **Player:** Jebrim · **Opened:** 2026-05-25

Principal: "The shipping agent has migrated to the official repo (github.com/picanova/shipping-agent). What do we need to change?"

## What I found

The migration was a **seed, not a transfer** — both repos exist independently, old URL does not redirect:
- Local working copy + `niklavsfelsbergs/shipping-agent`: HEAD `854128ac` (S064, rule 36 reload-detection).
- `picanova/shipping-agent`: HEAD `7562825c` (S062 state) — **behind by the S064 commit.**
- Local `origin` still pointed at `niklavsfelsbergs`. Working tree clean.

Sibling check: jebrim-1fc49f17 (S064) ended ~11 min prior; only live sibling braindead-f3239bdc (dev-brain, no overlap). Posted OPEN.

## Actions

- **[completed]** Repoint local `origin`: `niklavsfelsbergs` → `picanova/shipping-agent.git`.
- **[completed]** Push `7562825..854128a main -> main` to picanova (clean FF, verified `git merge-base --is-ancestor` first). picanova now current with rule 36. In sync 0/0. **Push succeeded with no auth block** — consistent with the S062 correction that the repo IS pushable.
- **[completed]** Updated onboarding-message bank draft (`bank/drafts/notes/projects/shipping-agent-onboarding-message.md`): clone URL → picanova; access note rewritten for org-membership model (was: personal-private + "make public").
- **[pending — principal action]** Archive `niklavsfelsbergs/shipping-agent` on GitHub now that picanova is confirmed current. Flagged safe. Optional `gh repo archive niklavsfelsbergs/shipping-agent`.

## Left as history (not rewritten, per archive-discipline)

Completed quest-logs and `inventory/archive/shipping-agent-audit-resume.md` (which predicted this move) keep the old URL. One stale-active inventory file `shipping-agent-audit-2-resume__91ee1383.md` carries the old URL — optional cleanup, low value.

## Not affected

Keepsake pin (local path only, no URL). `ONBOARDING.md` shipping-agent line has no URL — its *brain* line references `niklavsfelsbergs/brain`, a separate repo / separate question.

## Demo prep for 2026-05-26 showcase (same session)

Principal: examples-first, setup-last; catalogue of 3-5 (multiple easy / 1 medium / 1 bigger). Chose **board-deck** as the bigger project (over savings). Will self-test the questions.

**Verified live (redshift MCP, did not trust prior notes):** cost RELOAD IS DONE — `final_shipping_cost_eur` 95% populated, cost_source mix back to normal (invoice 66 / expected 27 / null 5 / avg 1.4 / invoice_estimate 0.4). Data through 2026-05-25. Cost questions SAFE.

**Calibrated numbers (April 2026, received_by_carrier basis; April = all current volume since ORWO/PCS/Rewallution had ~0 April rows):**
- Volume 249,375 parcels; total cost €1.76M; avg cost/parcel €7.06; net rev €8.07M; shipping 21.8% of rev; return flag 0.5% (incomplete).
- Carriers: DHL 90K@€3.32, UPS 45K@€10.24, MAERSK 29K@€4.91, ONTRAC 23.5K@€9.31, DPD-PL 21.5K@€4.64, USPS 18K@€6.51, FedEx 9K@€19.80, DPD-UK 6.8K@€8.95.
- On-time (232.8K delivered): 82.9%@3BD / 95.6%@5BD / 98.2%@7BD. No SLA set.
- Typical order cost €7.25 avg (~1.03 parcels/order); median lower (PERCENTILE_CONT/MEDIAN both rejected by the MCP validator — agent computes live).
- Cost/parcel trend Nov→May: 6.17 / 5.67 / 6.85 / 6.43 / 6.88 / 7.06 / 6.33(May partial). NOT a clean down-trend; April is the high. Dec dip = holiday volume mix.

**Rulebook wiring confirmed in how_to.md (so behaviors will fire):** rule 12 scope selector (TCG/both/ORWO), rule 4 self-gate + rate-vs-mix decomp + anti-median-dodge, rule 35 set pre-flight (scope-once/period-align/cross-reconcile/lead-with-status), rule 36 reload detection, rule-16 on-time no-SLA threshold fork.

**Caveat flagged to principal:** ORWO (Wolfen lab) empty in mart now → scope selector still fires but TCG-only ≈ both; judgment demo is the decomposition + integrity blocks, not a scope sign-flip.

**Open:** offered to save finalized catalogue as a bank draft (reusable demo reference).

## Rule 15 UPS surcharge band fix (same session)

Principal correction to UPS oversize sub-type inference bands in how_to.md rule 15:
- OML: €500+ → **€400+**
- LPS: €100–500 → **€50–400**
- AHS/small handling: under €100 → **under €50**

Edited how_to.md (only location — grep confirmed bands appear nowhere else; bucket name `oversize_overweight_eur` and savings examples are unrelated). **Uncommitted in shipping-agent working tree** — awaiting principal go on commit+push to picanova. Offered a reclassification-impact check (parcels in €400–500 flip OML→LPS; €50–100 flip AHS→LPS).

**[completed]** Rule 15 fix committed `81cb309` + pushed to picanova (854128a..81cb309). Live.

## Harvest: UPS YoY transcript vs the rule-15 change we just shipped (same session)

Principal handed over a shipping-agent transcript (TCG board Q → YoY +17% → why → bucket decomp → UPS oversize tier shift). Critiqued + verified against live mart (redshift MCP).

**Headline catch:** transcript classified UPS oversize parcels into LPS/OML "per rule 15" using the OLD bands (AHS<100 / LPS 100-500 / OML 500+). We changed rule 15 THIS session (AHS<50 / LPS 50-400 / OML 400+). Verified the reclassification (UPS, TCG, order-placement basis):
- **2026 (481 parcels):** flip-zones €50-100 and €400-500 both EMPTY → tier counts UNCHANGED (32 AHS / 404 LPS / 45 OML hold). My "already stale" was wrong here.
- **2025 (222 parcels):** 172 parcels sit in €50-100 → under new bands they flip AHS→LPS. Old tally 221 AHS / 1 LPS → new tally 49 AHS / **173 LPS**. The transcript's "2025 was almost all small AHS" narrative is an ARTIFACT of the old €100 cut.

**Corrected story:** Large Package was already the 2025 norm (172 parcels, €16K) → grew to 404 (€41K) in 2026. What's genuinely NEW is Over Max Limits: 0 → 45 parcels, €0 → **€48K** (66% of the +€73K oversize increase). The actionable (probe the OML parcels) survives and sharpens; the "shift into LP" framing was the binning artifact.

**Reconciliation flag:** transcript said "45 OML ≈ €27K of €100K"; live SUM is €48K of €90K. Likely coverage firming since the transcript ran (87%→higher invoiced) + a loose estimate — but the agent didn't reconcile its own sub-figure against the bucket total (rule 35).

**Proposed harvest (NOT yet done — awaiting principal go):** rule-15 hedge clause (tier counts carrying euros/actions keep the raw-amount distribution + "depends on current bands" caveat; band revision = re-query not re-investigation); rule-9 extension (cross-period maturity asymmetry — quantify sensitivity, don't just caveat); bank-note section in shipping-agent-quality-assessment.
