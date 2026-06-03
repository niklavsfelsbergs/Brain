# Resume — S061 shipping-agent security review

**Quest:** `quest-log/in-progress/S061_64d03d53_shipping-agent-security-review.md`
**Status:** documented only. No code read, no fixes, nothing committed.

## Where we are

External 5-finding security review of out-of-tree `Documents/GitHub/shipping-agent/` captured, with my assessment + reprioritization. Key reframes: deployment is single-operator-local (not company-facing) so several severities deflate; permissions (#4) upstream of SQL guards (#1); HTML-escape is the real High; review missed `.env` secrets, PII-in-artifacts, audit trail.

**Deployment thread (same session):** principal wants company use. Chose **per-seat desktop** (B) over API web product (A). Cockpit-dodge corrected (per-operator, doesn't fan out). Delivery vehicle decided = **Claude Code desktop app, per seat, on a Claude Team/Enterprise plan**. B's real work = per-user DB creds (IT, gates all) + repeatable setup + the seats. Team-pitch framing drafted (pitch capability not tool; 3 prereqs; S060 credibility line). A SUBSET of S061 stays a deployment dependency even per-seat (secrets, `python:*`, PII-in-artifacts). Full detail in the quest entry's "Deployment direction" section.

## Next concrete step

Two open tracks:
1. **Security verify** (≈10 min, no edits): `python:*`↔`db.py` bypass; `.env` secrets handling (gitignored? leaks?). Then scoped fix plan per the quest's priority order.
2. **Deployment** — awaiting principal answer on: how many analysts + terminal-comfortable or business users (decides setup effort). Then: per-user-cred ask for IT + setup checklist.

Principal sign-off before any edit; repo denies push.

## Files to read first

- `quest-log/in-progress/S061_64d03d53_shipping-agent-security-review.md` (the full record)
- Then in the repo: `.claude/settings.json`, `harness/db.py`, `connect_redshift.py`, `build_inline_chart.py`, `build_report.py`, `query_to_csv.py`, `query_to_xlsx.py`, `requirements.txt`, `.gitignore`

## Boundary

Uncommitted S060 edits already in the shipping-agent repo — keep clear of them.
