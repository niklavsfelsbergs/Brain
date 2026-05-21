# S023 resume — shipping-agent iteration thread

**Status:** in-progress (S023's audit phase shipped; iteration on the shipping-agent continues under this quest slug).
**Quest file:** `players/jebrim/quest-log/in-progress/S023_2026-05-21_shipping-mart-coverage-audit.md`

## Where we are

Audit phase **shipped** in S023:

- Two commits in `bi-analytics-main`: `4952b65` (restructure destinations + coverage layer) and `0b4ea40` (restructure source deletions). Together they land the shipping-agent at `NFE/projects/3_shipping_data_mart/shipping-agent/`, with a new `reference/coverage-audit.md`, a §0 rule 7 on coverage discipline, a §2 source-maturity table, and a re-verified §9 dim-coverage subsection.
- Brain-side drafts pending: skill (`spellbook/drafts/skills/coverage-questions-time-and-source-axis.md`), bank breadcrumb (`bank/drafts/notes/projects/shipping_mart_coverage_audit_2026-05-21.md`), examine self-observation (`examine/drafts/2026-05-21-cross-project-read-context-as-advantage.md`), niksis8_character observation (`niksis8_character/drafts/2026-05-21-niklavs-verifies-agent-claims-by-cross-checking.md`).
- No pending external actions.

Four concentrated cost-coverage holes the audit surfaced (none yet raised with ETL):

1. **ORWO POST** — 568K shipments, 0% covered. No bulk-bill source. Largest hole in the mart.
2. **Picturator `POST_DVF`** — 170K shipments, 0% covered. Deutsche Post variant, no invoice source. Concentrated Germany.
3. **Picturator MAERSK** — 98K shipments, 68.9%. Weakest in Sweden (17.4%), France (67.6%), UK (72.6%). Pattern suggests per-country allocation gap.
4. **Picturator ASENDIA** (not "ASENDIA USA") — 5.8K at 0%. Likely stale carrier label.

Plus the still-open S002 thread: **ORWO `destination_country` is 100% blank**. Country slicing on ORWO is impossible until the wiring lands.

## Next concrete step

Principal chooses from the iteration backlog. Options (loosely ordered by leverage):

1. **Raise the four holes with Grzegorz / ETL.** Specifically: is ORWO POST allocation on the roadmap; is `POST_DVF` supposed to map to a `bronze.csv_dhl_invoicedata`-style source; what's the MAERSK per-country pattern; is `ASENDIA` retired? **Most direct path to closing the actual coverage gaps.**
2. **Finish ORWO `destination_country` wiring** (S002 thread). Probe `enterprise_bronze.orwo_shipping_data_mart` for a country column per the S002 inventory plan. Unblocks the country axis on the largest source.
3. **Probe MAERSK per-country pattern** — why Sweden at 17%, France at 68%, UK at 73%. Could be a single `maersk.sql` allocation rule.
4. **Run the deferred S015 TTYD dogfood** against the new restructured shipping-agent. The dogfood now has a richer chain to grade (coverage-audit.md + source-maturity table + tighter §9). Could close S015.
5. **Audit how_to.md for other stale sections** — §9 was stale, what else? A scan for "last verified" markers (now that §9 has one) and a re-check pass.
6. **Build out `reference/` further** — common-question recipes, per-shop quick-reads, a `methodology.md` capturing the time-and-source rule with worked examples. Lower-leverage; the shipping-agent's how_to is the load-bearing artifact.

If `/drafts` is run at next respawn, expect to triage the four brain-side drafts (skill / bank breadcrumb / examine / niksis8_character).

## Files / paths to read first

1. This file + the S023 quest-log file for full T1-T6 history.
2. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/coverage-audit.md` — the durable matrix + the three regenerate-on-demand probes. **Verify "last verified" stamp before quoting.**
3. `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — §0 rule 7, §2 source-maturity, §9 dim-coverage subsection are the new surface.
4. `bank/drafts/notes/projects/shipping_mart_coverage_audit_2026-05-21.md` — Jebrim-side breadcrumb with the headline.
5. `spellbook/drafts/skills/coverage-questions-time-and-source-axis.md` — methodology rule (promote during alching).
6. **For option 2** (ORWO destination_country): also read `inventory/S002-shipping-data-mart-v1-resume.md` — the S002 thread carries the probe plan.
7. **For option 4** (S015 dogfood): also read `inventory/S015-ttyd-resume.md` — three candidate questions are pre-staged there.

## Constraints (in-force)

- `bi-analytics-main` is a separate repo from the brain. Brain commits don't reach NFE; commit the two repos separately when shipping new work.
- The shipping-agent operates inside its folder only (§10 of how_to.md). When asking the shipping-agent to re-run the matrix, expect it to use its in-folder harness (`python connect_redshift.py …`), not external paths.
- The skill draft and bank breadcrumb are observation-backed (per drafts-mechanics); promote them during alching only after a second occasion reproduces the pattern.
- Don't re-quote the audit numbers from memory after >1 month — regenerate via the probes in `reference/coverage-audit.md`.

## Open meta-questions for next session

- Is the shipping-agent currently configured to re-run `coverage-audit.md`'s probes on cue, or does that take a manual ask? (Affects how the "last verified" stamp gets maintained.)
- Should the four concentrated holes get individual quest entries (one per hole) when raised with ETL, or one umbrella entry? Likely one umbrella ("coverage-hole follow-ups") with sub-tasks.
- The skill draft says *"adjacent skill (future): `decompose-questions-by-etl-atom-not-business-unit.md`"* — that's still a future draft, not a written one. Surface in alching if it earns its way.
