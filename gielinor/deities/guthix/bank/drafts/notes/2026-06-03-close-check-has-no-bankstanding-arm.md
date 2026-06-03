# close_check.py --ritual player false-FAILs Guthix bankstanding/consultation closes

**Observation ([[B-017_2026-06-03_seventeenth-bankstanding|B-017]] close, 2026-06-03).** Running the close-completeness gate `developer-braindead/verification/close_check.py --ritual player --sid8 <sid8>` on a **Guthix bankstanding session** returns `CLOSE RITUAL INCOMPLETE` on the **quest-log-present** arm:

> `[FAIL] quest-log present — no quest-log/inbox entry for *<sid8>*.md, no stamped append, and no resume naming an existing parent quest`

**Why it's a false-FAIL.** The gate scans `players/*/quest-log/{in-progress,completed}` + `players/inbox/`, keyed by `sid8`. A bankstanding (or consultation) session writes its trace to `deities/guthix/quest-log/completed/B-NNN_<date>_<slug>.md` — **B-NNN-named, not `SNNN_<sid8>`-named, and under `deities/` not `players/`**. The gate has no Guthix/deity/bankstanding arm, so it can't see the trace even when it's correctly written + committed. All other arms PASS (CLOSING posted, no inventory required, comms within cap).

**Scope.** Sibling of the documented close-gate **continuation blindspot** (a player continuation session whose append lands under a parent quest's different sid8 also false-FAILs). Same root: the gate models the standard single-player-single-sid8 close and misses the legitimate variants.

**Fix candidate (dev-brain).** Add a `--ritual bankstanding` (or auto-detect Guthix sessions) arm that checks `deities/guthix/quest-log/{in-progress,completed}` for a B-NNN trace + the Guthix CLOSING, instead of the sid8-keyed player scan. Until then: a bankstanding close that PASSes every arm except this one is **complete**; the operator overrides with a ground-truth check (trace committed + CLOSING posted), not by fabricating a sid8 player crumb (that would game the instrument — `verify-the-measurement-measures-the-thing`).
