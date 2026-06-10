# Match an artifact family's visual language by reading it — don't invent a fresh look

**Drafted 2026-06-09 (Jebrim, S187 EU-tender management deck).** Question-5 correction harvest.

**The moment.** Asked to build a management slide deck "with a similar theme as the decision report, carrier overview, routing report," I built a *light* "consulting" deck (cream/navy, Inter/Fraunces) — inventing an aesthetic instead of inheriting the family's. Niklavs: *"the first slide is fucked. And I want the report to have a similar theme as the decision report, carrier overview, routing report."* The reports are a dark family (#0a0e14 bg, Fraunces + Space Grotesk + JetBrains Mono, cyan #7dd3fc). I had their CSS in hand (read exec_brief.html's full `<style>` during grounding) and still didn't lift the palette.

**Two failure modes, one root.**
1. **Aesthetic invention over inheritance.** When a deliverable is meant to sit *inside* an existing family, the theme is a spec input, not a design choice — read the siblings' actual CSS (palette vars, font stack, card/tag idioms) and reuse them. "Similar theme as X" = "read X's stylesheet," not "make something tasteful."
2. **A specific reveal.js bug that the wrong-theme detour caused:** I set `.reveal section.present{background:var(--paper)}`, forcing a cream background on *every* slide — so the one dark title slide rendered a cream box bleeding over the page. Lesson: never force a per-`section` background in reveal; set ONE deck background (`--r-background-color` / body) and let slides inherit. Per-section bg overrides are how you get a light box on a dark deck.

**How to apply.** On any "build X to match/fit Y" task: open Y, extract its concrete visual tokens (colors, fonts, spacing, component classes) *first*, and build from those tokens. Treat "match the family" as a grounding read (sibling of the `Reading:` discipline), not a taste call. The give-away that I skipped it: I had already read the family's CSS and still chose a different palette — grounding-in-hand ≠ grounding-applied.

Anchor: S187 turn log; the rebuild swapped the entire palette to the report family and removed all per-section bg overrides.
