# The reconciliation gap against actuals is the completeness check on a re-rate model

**Observation (S179, 2026-06-09).** Comparing the DB Schenker 2026 vs 2025 offers, my first-pass re-rate priced each shipment as `base × (1+MAUT) × (1+BAF)` and reported **net −0.73% (2026 favourable)**. That was wrong. The real DB Schenker calculator is **additive**, and the lane is entirely HOME service — so the all-in carried CAF + a Mobility Package + a €10 HOME-delivery fee + a NEW €1 Sustainability fee my model omitted. Adding the full stack flipped the net to **+1.09% (2026 dearer)** — opposite sign.

**What caught it:** the reconciliation against actual invoiced. The first-pass model came in **−39% below actual**. That gap was the tell that the model was missing cost components — I didn't trust the delta until I'd driven the gap down (to a stable −15.8%, the irreducible cheapest-zone-fallback residual) and the model reconciled.

**Why it matters / how to apply:**
- When re-rating against a population that has a **ground-truth cost** (actuals), reconcile model-vs-actual *first*. A large gap means the model is incomplete — **do not report a net delta off an unreconciled model.** The gap is the completeness signal, free and authoritative.
- Two offsetting structural levers (here: +1.18% base rise vs a favourable conversion-factor cut) can leave a delta near zero — at which point a **single new flat fee flips the sign**. A "roughly +1.2% base" headline hid both a €28k concession and a new €33k fee. Decompose; don't trust the headline number.
- Sibling of [[2026-05-31-rerating-mirage-guard-capability-and-noise]] and the validate-through-the-pipeline lesson: a re-rate that passes its own internal arithmetic is still a hypothesis until it reconciles against the thing it claims to model.
