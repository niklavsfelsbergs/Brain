# Complete-ready quests must graduate in-session, not "next session"

**Observation ([[B-007_2026-05-25_seventh-bankstanding|B-007]], 2026-05-25).** Jebrim's `quest-log/in-progress/` held 15 files at the start of this bankstanding; verification showed 11 were done-but-hanging (deliverable shipped + committed, nothing open). Bankstanding Phase 0 graduated them (15→5).

**This is the second identical occurrence.** [[B-004_2026-05-23_fourth-bankstanding|B-004]] (2026-05-23, S053) found the *same* folder at 15 files and cleared it to 3 — also dominated by complete-ready debris ([[S045_91ee1383_shipping-agent-chart-system-fixes|S045]]/[[S047_1cf1eb75_slack-mcp-install|S047]]/etc.). So in ~2 days of sessions ([[S054_50b00902_shipping-agent-audit-2|S054]]–[[S072_35eca9a3_shipping-agent-audit-3|S072]]) the folder re-accumulated 3→15 with the same composition.

**Root cause.** Sessions close a quest by writing *"deliverable shipped — reads complete-ready; propose move to `completed/` next session (principal approval)"* and then **never execute the move** — the next session has its own task and defers again. The graduation keeps getting kicked to a "future session" that doesn't come. Only a cleanup pass (S053) or a bankstanding Phase 0 ([[B-007_2026-05-25_seventh-bankstanding|B-007]]) actually moves them. The pattern is visible verbatim across nearly every Jebrim CLOSING in `comms/active.md` ("propose →completed/").

**Why it matters.** A 15-deep in-progress folder defeats the crash-recovery signal (`death-and-spawn.md`): if everything looks in-progress, a genuinely-interrupted quest can't be distinguished from 11 done ones. It also makes every respawn's "what's open" survey noisy and forces a periodic manual sweep.

**Decision.** A quest whose deliverable has shipped + been verified + committed is moved to `completed/` **in the session that finishes it**, not deferred. Deferral is the exception (genuine ambiguity about whether it's done), not the default. Bankstanding Phase 0 remains the backstop, not the primary mechanism.

**Ritual follow-up (user-only, pending).** `spellbook/rituals/close-session.md` should gain an explicit step: graduate complete-ready quests before wrap. That edit touches a user-only ritual file and is left for the principal's hand — this decision authorizes it; the edit itself is separate.

**Caveat — don't over-correct.** Some quests legitimately stay open with a shipped deliverable (e.g. [[S068_363fdec7_v1-freeze-mart-knowledge-reconciliation|S068]] pending the A5 ruling, [[S065_48847e45_shipping-agent-org-repo-migration|S065]] carrying un-acted harvest, [[S040_1cf1eb75_outlook-mcp-research|S040]] parked on a principal-side action). The rule is "graduate when nothing is genuinely open," not "graduate everything with a commit."

**Anchors.** [[B-004_2026-05-23_fourth-bankstanding|B-004]] S053 (15→3, comms 2026-05-23 08:57); [[B-007_2026-05-25_seventh-bankstanding|B-007]] Phase 0 (15→5, this round). Repeated "propose →completed/ next session" lines across Jebrim CLOSINGs in `comms/active.md`.
