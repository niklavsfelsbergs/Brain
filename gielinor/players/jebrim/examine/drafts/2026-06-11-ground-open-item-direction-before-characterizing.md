# Ground an open item's direction before characterizing it

**Anchor ([[S200_104770bd_eu-tender-no-hermes-portfolio-check|S200]], `104770bd`, 2026-06-11, turns 2–3).** Listing the EU-tender open items, I characterized the DHL thin-flat waiver from the [[eu-tender]] digest's one-line mention as a both-ways number-mover: "Maersk EU fuel and the DHL thin-flat waiver — both erode or pad the €420k base." Niklavs challenged ("sperrgut 20 eur? that wont disappear"). Grounding in `carrier_overview_v2/sections/dhl_paket.md` + the phase-1 verification showed the engine prices the full €20 Sperrgut today and the waiver is **upside-only** — it cannot erode anything. The directional claim was wrong; the grounded answer corrected it.

**The pattern.** A digest/index one-liner names an open item but not its *asymmetry*. Stating which way an open item can move a headline (erode / pad / both) is a substantive claim about the model's current assumptions — it requires knowing whether the engine prices the item as landed or as not-landed. I asserted direction from the name alone.

**The rule.** Before stating an open item's directional effect on a reported number, check how the model currently treats it (assumption baked in vs priced at today's state). Upside-only / downside-only / both-ways is a property of the *modeling baseline*, not of the item. One grep into the engine docs settles it — same cost as the wrong claim, without the correction round.

Sibling of the global read-domain-knowledge-before-proposing reflex; this is the *direction-of-effect* special case.
