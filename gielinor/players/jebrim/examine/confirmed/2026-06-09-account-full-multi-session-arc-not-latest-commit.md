# Account the full multi-session arc, not the latest commit

**Observation (S195, sid8 1a966d4a).** Asked to estimate how much work got done "today," I scoped it to the final session's commit subjects + the latest in-progress files and undercounted the EU-tender output by roughly half. Niklavs caught it: *"seems youre not taking into account all the EU tender work today but just the final session."* The tender work actually ran across ~8 sessions ([[S177_eac2ab42_dpd-poland-clc-de-reconciliation|S177]]–S187); I'd flattened a multi-session arc into the two or three discrete commit headers I happened to read.

**The failure.** Anchoring on discrete commit *subjects* as if each were "a thing," instead of tracing the work *behind* them across the day's sessions. Commit headers compress; reading them as the unit of work systematically undercounts parallel/multi-session effort. This is the same grain mistake I'd flag in a data pull (mistaking the row count for the work).

**Rule.** When estimating or summarizing work done across a *period* (a day, a sprint, "since X"), enumerate the full session/commit arc first — `git log --since` across all sessions, the quest-logs, the promoted drafts — before sizing it. Don't let the few commit subjects in immediate view stand in for the whole body of work. The latest session is a slice, not the total.
