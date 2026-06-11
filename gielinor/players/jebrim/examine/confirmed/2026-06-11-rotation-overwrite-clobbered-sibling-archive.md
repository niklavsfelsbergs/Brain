# A whole-file write to a shared dated path needs an existence check first

**Anchor (S196/5733cb1d close, 2026-06-11 ~14:14).** Rotating comms/active.md at close, I wrote
`archive/active-2026-06-11.md` with `Out-File` — overwriting the 52KB archive the [[S197_b93204b5_q04e-label-churn-deep-dive|S197]] sibling
had created and committed (975311c) two hours earlier for the SAME rotation date. The close-gate's
line-count check fired me into a rotation without checking whether today's rotation had already
happened. Caught because 79 lines from 315 with 1 archived entry didn't add up; recovered via
`git show 975311c:...` + append.

**Rule.** Before any whole-file write to a shared, convention-named path (dated archives,
rotation targets, inbox files): (1) check existence — if present, APPEND, never replace;
(2) treat a "do X at close" checklist item as "check whether X is already done" first — parallel
sessions run the same checklist (same family as fix-the-class-across-sibling-consumers and the
[[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] commit sweep, but on the write side). The earlier directory-pathspec sweep of the sibling's
q04e files this same session was the soft version of the same miss.
