# "Make a v2 of the report" → the variant he means is the most-recently-active one

**Rule.** A bare singular reference ("the report / the X") to a multi-variant artifact family anchors to the **most-recently-active variant in the working thread**, not the structurally-primary / base-named one. The base-named variant (`final_report/`, the "main" report) is a **magnet for wrong-anchor** when a later variant is the live focus. When the reference is ambiguous and the action non-trivial (a build, or quoting a canonical figure), **name the variant in the Plan line** so a wrong pick costs one line, not a full build or a wrong number to the principal. Twice in one day (S219 build, S234 grounding) → pattern, not one-off.

**Source:** [[S219_e0eb59c8_eu-tender-final-report-content-pass|S219]] (e0eb59c8), 2026-06-12.

## The moment
Niklavs said "implement all the changes but as a v2 report" (singular). I read "the report" as the **main** final
report — defensible, since it carries 10 of the 11 review changes — built `final_report_v2/`, and flagged the
no-Hermes report as separate. His next message: *"bro, i wanted the no hermes version. make that as well."*

## The lesson
When the principal references "the report / the X" about an **artifact family** with several variants, the one he
means is usually the **most-recently-active variant in the working thread**, not the structurally-primary one. The
no-Hermes report was the live focus across the immediately prior sessions ([[S212_177f00f1_eu-tender-no-hermes-report|S212]] built it, [[S218_932b8e5c_eu-tender-no-hermes-deck|S218]] turned it into a deck);
"the report" anchored to *that*, not the main report I treated as canonical.

This is the [[anchor-referent-before-analyzing]] discipline applied to *which* artifact, not *whether* it's new: a
bare "the report" inherits the thread's recent subject. When a singular reference is ambiguous across variants and the
build is non-trivial, **name the variant in the Plan line ("building v2 of the *main* report — say if you meant the
no-Hermes one")** so a wrong pick is corrected at one line, not after a full build.

Not a costly miss here (the main v2 was wanted too), but the cheaper path was one clarifying half-sentence up front.
Related: [[feedback_build_the_named_ingredient_not_the_old_plan]], [[feedback_match_artifact_family_by_reading_it]].

## Recurrence — [[S234_976b6908_eu-tender-presented-canonical-report-pin|S234]] (976b6908), 2026-06-12 (costlier: grounding, not just building)
Niklavs: "the eu tender just got presented." I grounded off `final_report/` (the structurally-primary, base-named
folder) and quoted its **stale** €420k/€577k base+module split as the headline. He corrected: *"how do you not know
the final saving was 976k? just the firm one"* — the canonical/presented artifact is `final_report_no_hermes_v2/`
(firm headline €976,024). Same failure mode as the moment above, **applied to which artifact I read for the canonical
figure**, and worse: I stated a wrong number to the principal the day he presented it, instead of naming the variant.
The corpus already *contained* the right pointer — the no-Hermes v2 was the live focus across the entire prior
session run ([[S212_177f00f1_eu-tender-no-hermes-report|S212]]/[[S219_e0eb59c8_eu-tender-final-report-content-pass|S219]]/[[S221_eec4ee99_eu-tender-report-review-qa|S221]]/[[S222_3309c3da_eu-tender-no-hermes-v2-headline-reconciliation|S222]]/[[S226_da65054b_eu-tender-routing-report-no-hermes|S226]]) — I just defaulted to the folder name that reads "final". **Fix landed this
session:** pinned a `CANONICAL PRESENTED REPORT = final_report_no_hermes_v2/` line into the force-loaded
`bank/domains/eu-tender.md` so the next session can't re-anchor to the superseded folder. Second occurrence in one day
→ this is a real pattern, not a one-off; the base-named/structurally-primary variant is a **magnet for wrong-anchor**
when a later variant is the live one. Promote on next alch.
