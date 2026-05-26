# 2026-05-22 — When a project's findings doc is older than its sibling artifacts, treat the doc as stale

**Observation.** [[S030_2026-05-22_dashboard-gold-cutover|S030]] T10 (DB Schenker meeting prep). The principal asked me to summarize project 38's prior conclusion. The CLAUDE.md ended on a "Status update — 2026-05-11 (too early to call)" section. I summarized that and presented the question framing as if the open thread was the May-11 status check.

The principal corrected me: *"But there was already a conclusion in project 38 last time I looked at it I think, I want to check what happened since then."*

That cue forced me to re-look. The folder contained:
- `dbs_carrier_migration.py` (mtime 2026-05-15)
- `pull_dbs_since_may9.py` (mtime 2026-05-15)
- `data/dbs_carrier_migration_since_may9.xlsx` (mtime 2026-05-15)
- `CLAUDE.md` (last touched 2026-05-11)

Reading the xlsx recovered the actual conclusion — of 523 DBS shipments since May 9, only 13% migrated from UPS. **That's the answer the principal remembered, but it was never appended back to CLAUDE.md.** The doc was 4 days behind the data.

**Pattern.** A repo's findings doc (`CLAUDE.md`, `README.md`, summary markdown) is not authoritative when the same folder contains data/scripts with newer mtimes. The conclusion lives in the most-recent artifact, not the most-prominent one. Default-trusting the markdown leads to a stale read.

**How to apply.** When opening a project folder to recover prior conclusions:

1. List all files with mtimes.
2. Compare the doc's mtime against the newest sibling artifact (xlsx, parquet, csv, py).
3. If the doc is older and sibling artifacts exist post-doc-update — **the doc is incomplete.** Read the artifacts.
4. Surface the staleness in the response so the principal knows the doc wasn't the source of truth.

**Anchor.** [[S030_2026-05-22_dashboard-gold-cutover|S030]] T10, 2026-05-22. The Glob results in `38_ups_de_cost_investigation_apr_2026/` showed `data/dbs_carrier_migration_since_may9.xlsx` dated 2026-05-15-11:43; CLAUDE.md dated 2026-05-11-15:53. 4-day gap should have been the immediate signal.

**Caveat.** Single occurrence. Pattern firms up with the next time I open a stale doc and either catch it or miss it.
