# A qualifier in a reference names a specific variant — anchor to it, don't drop it

**Observed:** [[S218_932b8e5c_eu-tender-no-hermes-deck|S218]] (2026-06-11). The ask was *"in the final report no hermes folder create a slide
deck."* I dropped the `no hermes` qualifier and went to the main `final_report/`. When the principal
added *"srry its for eu tender,"* I read it as "use the main report" — but both the main and the
no-Hermes folders live under the EU-tender project, so that clarification was **compatible with my wrong
reading** and I took it as confirmation. Built the whole deck off `final_stats.json`. Principal had to
correct a second time: *"but this is not the final_report_no_hermes."* Then I rebuilt it correctly.

**The pattern.** When a reference carries a qualifier that names a *specific sibling variant*
(`... no hermes folder`, `the staging config`, `the v2 export`), the qualifier is the load-bearing part —
it's there precisely to pick one of several near-identical things. Dropping it and matching the generic
noun lands on the wrong sibling. And a later clarification that is *also true of the wrong reading* is not
confirmation — it only rules out readings it actually contradicts.

**Why it cost a turn.** I built a full 13-slide deck against the wrong source before the second
correction. The five-lens *Contrarian* check ("what if the obvious read is wrong?") existed to catch
exactly this and I skipped it because the first clarification felt like it had resolved the ambiguity —
it hadn't.

**How to apply.**
- Treat a qualifier ("no hermes", "the X one", "staging") as the **primary key**, not a modifier on a
  generic match. If two folders/files differ only by that qualifier, the qualifier *is* the target.
- A clarification only confirms a reading if it would be **false** under the alternatives. "It's for EU
  tender" didn't exclude the no-Hermes folder — so it confirmed nothing about which folder.
- On a high-blast-radius build (a whole deliverable), spend the one Contrarian read before committing:
  *is there a sibling this qualifier is pointing at that I'm about to skip?*

Sibling of [[feedback_anchor_referent_before_analyzing]] (continuation cues) and the *Wrong-instance
check* — both are "map the exact referent before acting." This one is specifically about a discriminating
qualifier being silently dropped.
