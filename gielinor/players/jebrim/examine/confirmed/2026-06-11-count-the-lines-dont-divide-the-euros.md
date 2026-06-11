# Count the lines, don't divide the euros

**Observation ([[S206_01871b26_ups-2.0.0-engine-build|S206]], 2026-06-11).** I reported UPS residential incidence as "~64%" by dividing the residential bucket total (€37,228) by the assumed €0.40 unit charge. Niklavs' own report said ~38% — and his number was right. The actual count (residential lines > 0) was 46.3%; the average per *charged* shipment was €0.551, not €0.40, because surge-fee and WorldEase variants land in the same bucket. My derivation smuggled in a unit-price assumption that the data didn't hold.

**The pattern.** When a count is directly queryable, deriving it from an aggregate ÷ an assumed unit value is a hypothesis dressed as a measurement — any stacking, variant rates, or reversals in the aggregate silently corrupt it. The count was one `COUNT(*) WHERE bucket_lines > 0` away the whole time.

**Rule.** Derive counts by counting. Use aggregate-÷-unit-price only when the count is genuinely unreachable, and then label it as an estimate with the unit-price assumption stated. Sibling of [[2026-05-29-reconcile-definition-before-numbers]] (definitional equivocation) — this is the *derivation-method* variant.
