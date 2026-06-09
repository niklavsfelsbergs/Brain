# A populated dim column ≠ an independent measurement — and "full coverage" needs a coverage %

**Observed:** S173 (2026-06-09), package-dimension accuracy work.

**What happened.** Two related slips this session, both caught by pushing the analysis one step further:

1. The S167 coverage map (which I'd relayed) listed Maersk under "real measured dimensions" because its invoice carries L/W/H. The discriminator showed Maersk **reprints our declared dims 100% verbatim** — a passthrough with zero audit value. Same for DB Schenker / Direct Link (volume scalars). A column being *populated* says nothing about whether it's an *independent* measurement.
2. In the discriminator pass I told Niklavs Yodel was a "REAL, full-coverage" measurer. The Yodel deep-dive found its measured `actual_*` field is **only 6.9% populated** and bursty. I'd relayed a sub-agent's "full coverage on the dim-populated subset" without checking what fraction *was* dim-populated.

**The lesson.** When reporting that a source "has X" / "measures X" / "full coverage":
- **Independence:** verify the field is an independent measurement, not a round-trip of our own input. The cheap test is exact-equality vs our value (passthrough ⇒ ~100% exact). Watch the dual-field trap (a passthrough field AND a measured field coexist).
- **Coverage:** "full coverage" is a number, not an adjective — state the populated %. A field can be real and 6.9%-populated.

**Why it matters.** Both are instances of the standing reflex *verify the thing, don't trust the wiring* — applied to data provenance. A populated column and a sub-agent's summary phrasing are both "wiring"; the measurement's independence and its coverage % are "the thing." Sits next to [[don't generalize from a single verified case]] and [[verify the measurement measures the thing]].
