# S281 - ORWO tender: carrier_engines refactor + GLS/Maersk carrier-switch

**sid8:** 926f247a - 2026-06-19 - continues the ORWO arc, phase of the umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] (after [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]]). Cue: "continue orwo tender". Executed the locked S281-cont plan.

## Ask (Niklavs)
Continue the ORWO tender. Then mid-session: commit everything, update docs, wrap up, hand over; explain why the GLS offer wins.

## Done this session
- **Engine refactor (decided last session, option 1):** flat `repricing_base/engine/` → `repricing_base/carrier_engines/{ups,dhl_paket}/`, mirroring the EU-tender `carrier_engines/` layout. `_dhl` filename suffix dropped (folder disambiguates); raw vendor cards stayed in `offers/<carrier>/`; offer code moved into `<carrier>/offer/`. `git mv` preserved history (parquets gitignored → plain `mv`). Path surgery: `NFE_ROOT`/`CONTRACTS` `parents[3]→[4]`; `calculate.py` reads `rate_tables/`; offer scripts re-anchored to raw cards + carrier-root baseline.
- **Re-gated both (verify-the-thing):** re-ran build + gate live. **UPS base 0.971 / total 0.942; DHL freight 0.9992 / surcharge 0.9995 / sperrgut €307k excluded — reproduced to the cent.** Both incumbent offer compares unchanged (UPS H1 €16,973; DHL flat −€317, GB intl €50.6k lever intact).
- **GLS carrier-switch built** (`carrier_engines/gls/`, no own-baseline — applied card to existing UPS+DHL parcels). **GLS beats the current book ≈ −€509k/yr full-cost** (−€413k non-GB + −€96k GB on confirmed IC18). Dominant driver = DHL DE domestic 548k parcels −€238k/yr. US (1,855) + >40kg not servable.
- **Maersk carrier-switch built** (`carrier_engines/maersk/`, broker card, Home-Delivery method, cheapest local carrier per country/band). Splits by lane: LOSES DE domestic (+€206k H1, pricier than own DHL) but WINS GB (−€96k H1) + most cross-border (AT/FR/ES/IT −20-45%). All-Maersk +€160k/yr worse overall.
- **Synthesis `carrier_engines/COMPARISON.md`:** all-GLS −€634k/yr freight-only (−€509k full-cost); all-Maersk +€160k; per-lane best −€741k/yr ceiling. **Verdict: GLS = primary carrier; Maersk = GB/cross-border specialist; pragmatic = GLS primary + Maersk for GB.** Both incumbent UPS/DHL offers reprice flat (GRI-avoided only).
- **Doc path-sync:** roadmap/_scope/contracts_review/coverage/findings + relocated offer_summary refs `engine/` → `carrier_engines/`.

## Decisions (Niklavs)
- GB customs clearance = **IC 18** (VAT pre-paid, ~€3/parcel) → GLS wins GB ≈−€96k/yr; combined GLS ≈−€509k/yr.
- Commit everything (NFE work repo + brain), wrap up, hand over.

## Corrections / failure modes this session
- **Entry-OPEN gate fired** (require-open-on-entry hook) — entered via "continue orwo tender" and skipped the respawn comms OPEN; posted it late when the gate blocked a brain write. The recurring continuation-entry OPEN-skip; the gate backstopped it.
- **GLS freight-only would have overstated** — caught it before headlining: leveled DHL's €143k surcharge in + GLS €0.38 toll → honest full-cost −€413k non-GB (freight-only was −€634k). Reported the conservative number.

## Verification
- UPS + DHL gates re-run live post-move, reproduced to the cent (the load-bearing proof the refactor was clean). GLS/Maersk are MODELED (no own invoices to trust-gate) — card parses spot-checked to the cent; comparison freight-level (GLS full-cost leveled). Caveats documented in each README + COMPARISON.md.

## Cascade
- ORWO offer set now COMPLETE at 4 carriers (UPS✓ DHL✓ GLS✓ Maersk✓). The orwo-tender digest (still undigested per `bank/domains/_index.md`) should fold in the GLS-wins verdict at next alching; ORWO rate cards → carrier-contracts digest.

## Main-brain changes
- None to gielinor rules/rituals. Brain writes = this quest entry + resume__abfcf511 update + comms OPEN/CLOSING only.

## Open / next
- See `inventory/orwo-tender-resume__abfcf511.md`. Tender modeling done; remaining = deferred refinements (US/ROW-zone modeling, Maersk surcharge-sheet leveling for full-cost, seasonal annualization, confirm Maersk GB clearance) + present the GLS-primary recommendation to ORWO stakeholders. Parent [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] stays in-progress (umbrella).
