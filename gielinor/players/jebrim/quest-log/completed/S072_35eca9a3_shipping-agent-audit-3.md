# S072 — Shipping-agent audit-3 (pre-demo, 2nd full pass after S054 audit-2)

**Opened:** 2026-05-25 ~21:28. Principal cue (after S071 drift test): "one last thing before the demo — let's do an audit: contradictions, files too long which need splitting, hygiene, etc. We did a similar audit once."
**Mode:** READ-ONLY. 4 background auditor dwarves over disjoint subtrees (DA how_to.md / DB reference / DC skills / DD cross-cutting+harness). Grounded on audit-2 findings (`shipping-agent/workbench/audits/2026-05-23-audit-2/findings.md`) → flagged only NEW + REGRESSED. NO shipping-agent edits (how_to.md frozen/held @a43c1779, pre-2026-05-26 demo).
**Demo:** 2026-05-26. Verdict: zero demo-blockers; accumulated hygiene debt, mostly post-demo.

## Ground-truth resolutions (mine, redshift)
- **fact_shipments = 65 columns** (information_schema, authoritative). Docs stating 65 are CORRECT; bank's open "65-vs-63-enumerated" (H3) was a miscount → **RESOLVED, 65 stands.** Only residual: confirm tables.md column-group list totals 65. (Other facts: cost_summary 32, invoice_lines 18, orderitems 14, fact_truck_charges 12.)
- cost_source live = invoice 12.26M / expected 4.80M / NULL ~935K (~5.2%) / avg ~79K — **4 values, no `invoice_estimate`** (confirms it's gone post-reload). NULL ≈5%, not 8%.

## Consolidated findings (deduped, ranked)

### Contradictions
- **C1 (HIGH, POST-DEMO)** — how_to §0 Mode-1 anchor example answers "how many packages in April" by silently defaulting "we"→all-lines (lines 24-28, incl. `If "we" is asked it's all production lines` + `~502,000`) — the exact move rule-12 (line 80) bans (unstated vertical → 1/2/3 selection + wait). Flagship example teaches the banned pattern. Also stale number: ~502K vs live **473,858** (+5.9%). [DA1+DA2; = drift-test D1, now confirmed structural]. Fix: rewrite the example with a vertical named (or carve-out) + refresh/strip the number.
- **C2 (MED, POST-DEMO)** — how_to rule 11 (line 79) "NULL cost_source ≈8% mart-wide" is stale; live ~5%, and mart-contract §3 already says 5.18%. Stale number leaked into the always-loaded file. [DB1]
- **C3 (MED, SAFE-NOW)** — query-patterns.md:179 still claims `invoice_estimate` 5th cost_source value "exists (~0.5%)"; mart-contract:101 says it's gone post-reload; live confirms 4 values. [DB2/DC1]
- No *hard* rule-vs-rule conflicts otherwise — DA5 checked the suspect pairs (r3 vs r4, r7 vs r12, r8 vs skill-triggers): all reconciled in-text. Residual: r1/r7/r7-investigation-exception give three "first line" instructions with no stated precedence order (LOW, optional). [DA5]

### Files too long / split
- **L1 (MED, trend-HIGH, POST-DEMO)** — how_to.md regrew **479→527 (+10%)** since audit-2; the BL1 trim is fully eaten. Four mega-rules (2/4/11/12) = ~24% of the text. Concrete split [DA6]: move §11 personal-folders (~129 lines) → `skills/personal-folders.md` (or fold into `workbench/_about.md`, which §11 already calls canonical); collapse rules 30-34 to name-only pointers (full text already in savings-investigation.md); push worked-precedent prose (rule 4 +17%, rule 12 Wolfen-drag, rule 30 €460K) into skills/reference. Target ~390 lines (below audit-2's 479 floor). [DA3/DA6]
- **L2 (MED, POST-DEMO)** — rules 35/36 carry "every-mode" scope but sit after the "investigation-only (30-34)" block, needing a defensive "numbered to avoid renumbering" clause each — comprehension trap (esp. r36 reload-gate, which r11 calls the first gate for every cost answer). Renumber up into the 1-16 block, or relabel EM-1/EM-2. [DA4]
- **Verdict: only how_to needs splitting.** reference (mart-contract 219, tables 200) + query-patterns (193) all judged cohesive — no split. [DB/DC]

### Hygiene
- **H1 (HIGH, SAFE-NOW)** — `harness/build_report.py:1029` `output_html.relative_to(BASE_DIR)` crashes when `--out` is outside the package — latent-OPEN from audit-2, still unfixed (REGRESSED). Half-builds the bundle then dies. Wrap/guard the relative path. [DD1]
- **H2 (HIGH-symptom, SAFE-NOW)** — 3 stray malformed dirs at repo root (`workbenchanalysis20260525-fuel-trend-tcg-by-regiondata|outputs|sql`) — a path-join bug stripped all separators. Junk is gitignored/harmless; the **bug could misplace user output**. Hunt the offending join (likely an agent-authored workbench script, not build_*.py). [DD2]
- **H3 (MED, SAFE-NOW)** — CLAUDE.md (5 lines) still routes via bare `@import` only; audit-2 gave AGENTS/GROK/GEMINI an explicit "read how_to.md first" imperative because the shim is unreliable. CLAUDE.md never got it; demo runs on Claude. Add parity line. [DD3]
- **H4 (MED, SAFE-NOW)** — README skills list (lines 29, 106-107) names only query-patterns; omits the two newer skills (reprompting, savings-investigation). [DD4]
- **H5 (LOW, SAFE-NOW)** — mart-contract.md internal residue: "12.03M invoice rows" (live ~12.26M) + "~34% non-invoiced" (its own §3 table → ~32%). [DB4]
- **H6 (LOW, SAFE-NOW)** — coverage-audit.md section heading dated 2026-05-22 over a post-reload (05-25) body; known-dq.md top stamp 05-21 below its own 05-25 per-entry updates. Cosmetic. [DB5/DB6]
- **H7 (LOW, POST-DEMO)** — reprompting.md missing from how_to §1 "where to find things" index (reachable via skill-trigger block; index-completeness only). [DD5]
- **H8 (LOW, POST-DEMO)** — savings-investigation.md cause-attribution self-gate predates how_to r4's "charge-bucket split FIRST" step; lockstep drift. [DC2]
- **H9 (LOW)** — empty root `data/` dir (SAFE-NOW); README bi-etl `enterprise_silver` path hedge (SAFE-NOW, low value); triple-stated ORWO/NULL facts across mart-contract/tables/sources → designate one owner (POST-DEMO consolidation). [DD6/DD7/DB7]

### Confirmed clean (no regression)
- audit-2 dedupes held: §8 canonical output-routing, rule-2 jargon-ban single home, rule-11 formulas in mart-contract. All 8 §1-index sibling files resolve; no dead §-pointers. Entry imperatives (AGENTS/GROK/GEMINI) intact. The `build_light_html_presentation.py`→`build_report.py` rename fully clean.
- pandas (not polars) in requirements.txt — standalone repo, NO action.

## Now-vs-demo cut
- **SAFE-NOW (no frozen-how_to touch):** C3, H1, H2, H3, H4, H5, H6, H9(data/, README hedge).
- **POST-DEMO (touches how_to / needs lockstep):** C1, C2, L1, L2, H7, H8, DA5, DB7-consolidation. Batch with drift-test D1/D2 + held S070 menu edits + held dimension-scan rule.

## Next concrete step
- Principal decision on now-vs-post-demo fix scope (asked via menu). NO edits until go.
- On approval of post-demo batch: one maintainer session does C1/C2 + the DA6 split + L2 renumber + H7/H8 + reconcile with the held S070/dimension-scan as ONE coherent "lean + don't-guess" pass.
- Offer to colocate a findings.md in `shipping-agent/workbench/audits/2026-05-25-audit-3/` (matches audit-2), if principal wants it in-repo (workbench is gitignored — not a rulebook touch).
- Harvest audit to bank note + comms CLOSING after the decision.

## Outcome — fixes shipped + re-test (2026-05-25, principal said "fix it all")

4 checkpoint commits on main (picanova-tracked), on top of e6be3da:
- `d9bb138` — safe-now hygiene: H1 build_report --out crash guard, C3 invoice_estimate drop, H5 mart-contract numbers, H6 stamps, H3 CLAUDE.md parity, H4 README skills list + stale ORWO Status.
- `9293965` — how_to content: C1 Mode-1 example → vertical-named (kills rule-12 contradiction + stale 502K), C2 NULL 8%→~5%, H7 §1 index, D2 which-cut clause in rule 4, H8 bucket-first + full which-cut gate in savings-investigation.
- `f02c6e0` — L1 split: §11 detail → new `skills/personal-folders.md` (behaviour rules 17-29 + §8 kept always-loaded); how_to **528→410** lines (below audit-2's 479 floor); L2 every-mode banner on rules 35/36 (no renumber).
- (H2 path-bug = now-deleted one-off script, no code fix; 3 empty gitignored root dirs for principal to rmdir.)

**Re-test: 6 embodied probes vs the EDITED rulebook, all PASS, every number ground-truthed, zero regressions.**
- RT1 (split/save) — saved a chart correctly WITHOUT loading the moved file (§7/§8 stayed always-loaded). **Split preserved save-behavior.**
- RT2 (volume scope) — still fires rule-12 menu on unstated "we" (276K/474K/197K reconciled). C1 didn't break scope.
- RT3 (NOVEL which-cut, FedEx/US, no scar) — sliced weight-bands, **reversed the premise** (UPS carries 1,045 US parcels vs FedEx 18,270, FedEx = heavy tail), recommended don't-switch. **D2 proven GENERATIVE — closes the S071 D2 reference-primed caveat.**
- RT4 (bucket-first) — bucket split first; discount-collapse story; per-source falsification. Intact.
- RT5 (savings gate) — reload-gate→bucket-first→dimension-gate (89% fit)→lane cut (narrowed to Germany ~€590K), led with moves, no unearned confidence. Intact + applies which-cut to its own lever.
- RT6 (scope/Mode-2) — scope menu + reload gate + May lag handled; bucket-split held as follow-up. Intact.

**Col count 65 CONFIRMED** (information_schema) → resolves the open H3 from the S071 note.
**Deferred post-demo (low-value/higher-churn):** full 35/36 renumber (banner suffices), aggressive 30-34→pointer collapse + rule 2/12 prose trims, DB7 triple-NULL-fact consolidation.

**PENDING:** push to picanova (origin 3 behind at e6be3da; my 3 commits local-only) — awaiting principal go (outward-facing; demo-source question). Then bank-note harvest + comms CLOSING + brain commit (principal-gated).
