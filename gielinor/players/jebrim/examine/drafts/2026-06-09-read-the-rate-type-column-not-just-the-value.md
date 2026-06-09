# A rate-card value means what its type/label column says — read it, don't assume the number is the rate

**Observed:** [[S171_c4e56024_ups-fuel-basis-and-gri-sensitivity|S171]] (c4e56024), 2026-06-09 — UPS fuel basis.

**What happened.** The UPS engine encoded `FUEL_PCT = 0.35` as a flat 35% fuel surcharge on base, with a
code comment that *guessed* at the gap to reality ("real effective ~18-21%… it's a weekly floating
index, 35% is the v1 snapshot"). That guess was a plausible-but-wrong mechanism and it stood for two
sessions (S163 → S168). The actual answer was on the rate card the whole time: the fuel row reads
**"35, Percent Off — per Shipment, Net Rate NA"** — the *type* column says "Percent Off", i.e. the 35 is
a **discount off UPS's floating published index**, not the rate itself. Effective = index × (1−0.35) ≈
20%, which is exactly what our invoices show. The fix came only when Niklavs asked "how is the fuel rate
*listed*?" and I read the type column literally instead of treating the number as the surcharge.

**The lesson.** When a value comes from a structured source (a rate card, a tariff sheet, a config), its
meaning is carried by the *type/label/unit column next to it*, not the number alone. A "35" under a
"Percent Off" header is a discount; the same 35 under a "Rate" header is a surcharge — opposite signs in
the cost model. Read the qualifying column before encoding. And a **code comment that explains away a
discrepancy is a hypothesis, not ground truth** — when the model overshoots reality ~2× and the comment
hand-waves "it's an index, this is a snapshot," that's the cue to go back to the source's own semantics,
not to trust the narration.

**How to apply.** Before encoding a parameter pulled from a card/sheet: confirm what its rate-type /
unit / label column declares (discount vs rate, per-shipment vs per-kg, off-index vs flat). If a tuned
constant runs persistently hot/cold vs actuals, suspect a semantics misread before a "floating/snapshot"
story. Sibling of [[2026-06-05-code-comment-isnt-ground-truth]] (code comment describing data isn't
authoritative) and the read-domain-knowledge-before-proposing reflex.
