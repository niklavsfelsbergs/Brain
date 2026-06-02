# Skill — read for the governing signal, not the salient surface

**Class of work.** Any task where I read a body of content and report what it *means* — recapping a meeting/transcript/thread, explaining what code does, extracting requirements from a doc or spec, interpreting a request.

**Failure this guards against.** Treating a *salient surface feature* as the answer — locking onto whatever is loudest, most-repeated, best-named, or first-stated, and reporting it as the substance. Salience is not authority. The thing that governs is often quiet, late, or contradicts the loud signal.

Salience wears different clothes by content type:

- **Transcript / discussion:** the most-repeated phrase. (Often the framing the group argued *about* and then decided *against*.)
- **Code:** a function/variable name or a comment — vs the line that actually executes.
- **Doc / spec:** a heading or framing sentence — vs the operative/binding clause.
- **Request:** a loud keyword — vs the actual intent behind the ask.

## The core rule (the discriminator)

**Every claim I report must point to the specific thing that makes it true — the governing evidence, quoted or cited.** If I can't point to it, I'm reporting salience, not substance, and the claim doesn't ship.

- Transcript → the verbatim line that *settled* the point (speaker + words).
- Code → the line/branch that actually runs.
- Doc → the operative clause, not the heading.

A claim with no locatable backing is the red flag: it usually means I paraphrased the loudest signal instead of finding what governs.

## Procedure

1. **Read the whole thing before concluding.** One full pass first — don't summarize forward as I read. The governing fact often arrives late and contradicts the framing.
2. **Decompose by the unit that matters**, not by surface order: decision points (transcript), execution paths (code), binding requirements (doc). List them before answering.
3. **For each unit, track the trajectory: open → contested → close.** What got narrowed, dropped, or overturned. The conclusion is usually a *delta* from the opening, not a restatement of it.
4. **Take the last/binding word, not the first/loudest** — and attach its backing verbatim.
5. **Separate established from discussed.** Conclusions = backed claims only. Framing, debate, dead ends, plausible-but-unexecuted code go in a distinct "open / discussed" section, never folded into "what's true."
6. **Red-flag self-check before sending.** Re-read any claim that (a) has no locatable backing, or (b) just echoes the most salient phrase/name. Both are signals I read the surface, not the substance.

## Why it works

It's verifiable, not aspirational. The recurring bug is unbacked paraphrase of the loud signal; the fix forces every claim to point at the thing that governs. Same principle the brain already enforces elsewhere — drafts must be observation-backed, anchors must be real links — generalized to reading: a reported claim must be backed by its governing evidence.

## Anchor

Source: 2026-06-02 transit-time/SLA meeting recap slip (Jebrim) — reported "product category × country" as agreed when the meeting had collapsed product to a binary standard/oversized flag ("two KPIs per country") and explicitly decided *against* a product split. The most-repeated phrase was exactly the thing voted down. Generalized from transcripts to all read-and-report work in the same session at Niklavs' direction. Extends the S124 transit-time baseline work.
