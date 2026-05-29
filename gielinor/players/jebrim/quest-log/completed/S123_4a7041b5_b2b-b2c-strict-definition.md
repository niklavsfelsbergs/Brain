# S123 — B2B/B2C strict definition

**Session:** 4a7041b5 · **Player:** Jebrim · **Opened:** 2026-05-29

## What was asked

Post-mortem on a prior WICKELVERPACKUNG 60×40 carrier-routing analysis where a "B2B → UPS" claim collided with the principal's "81.5% of B2B is Maersk." Root cause traced, then: "we just need to more strictly define what is b2b/b2c."

## What happened

- Diagnosed the failure as **two errors**: (1) the one the prior agent caught — confident causal attribution ("deliberate routing rule") from pattern-only data; (2) the one it missed — an **equivocation on "B2B"**: it used the `b2b-shop-eu.picanova.com` *storefront* as "B2B" while the canonical contract calls MerchOne (`PicaAPI`) "B2B". The "99.9% B2B→UPS, 100% MerchOne→Maersk" line contradicted itself in one breath.
- Ground-truthed against the live mart (`shipping_mart.fact_shipments`):
  - **No B2B/B2C column exists** — always derived. Only signals: `source_system` (5) and `shop` (~1,380).
  - `b2b-shop-eu.picanova.com` (258,608) and `b2b-shop-us.picanova.com` (32,587) both sit on **`source_system = 'Picturator'`** — the platform the contract labels B2C. That is the entire collision.
- Offered 4 strict definitions (multiple-choice + recommendation). Principal chose **"customer-is-a-business"**:
  - `B2B = source_system='PicaAPI' OR shop ILIKE 'b2b-shop-%.picanova.com'`
  - `B2C = source_system='Picturator' AND NOT b2b-shop`
  - `OTHER = PCS / ORWO / Rewallution` (report separately)
- Validated (2026 YTD): B2B 327,803 / €2.0M (MerchOne 306,121 + storefronts 21,682), B2C 1,154,888 / €7.4M, OTHER 1,032,131 / €1.2M. B2B ≈ 22% of TCG.

## Persisted

- **Contract:** new "B2B vs B2C — strict definition" section in `shipping-agent/reference/sources.md`, plus the always-loaded `how_to.md` translation-table fix (Picturator→B2C now carries the b2b-shop exception; shop row points to the canonical rule) + `mart-contract.md` cross-ref. **Committed** to picanova/shipping-agent `main` @ `26f629b` (also swept in a pre-existing maintainer local-profile change — rule 10 + .gitignore CLAUDE.local.md, principal-authorized "commit everything"). **Not pushed** — ahead of origin/main by 1.
- **Bank draft:** `bank/drafts/notes/projects/2026-05-29-b2b-b2c-strict-definition.md` (→ alching to promote).
- Builds on [[S075_b3bb305b_shipping-agent-production-site-origin-awareness|S075]] (the prior fix that established TCG = Picturator B2C + MerchOne B2B at the platform level; this session adds the b2b-shop-on-Picturator nuance).

## Status

**Complete.** `26f629b` **pushed** to picanova/shipping-agent `main` (11996a8..26f629b, in sync 0/0) — the agent's deployed behavior now carries the strict B2B/B2C definition on the always-loaded path. Brain trace committed this close.

## Follow-ups (separate, not blocking this quest)

- The €21K Maersk-swap lever sizing should be re-run under this definition — the prior "exclude B2B" reasoning was built on the conflated label. New quest when picked up.
- Buyer-axis blind spot: a corporate order through an ordinary consumer storefront is invisible (counted B2C). Flag if a question hinges on *total* business-buyer volume.
