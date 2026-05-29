# B2B vs B2C — strict definition (shipping mart)

**Claim.** The mart has **no B2B/B2C column** — it is always derived, and two signals that both look like "B2B" disagree. The canonical definition (set 2026-05-29) is **"is the paying customer a business":**

```sql
B2B  = source_system = 'PicaAPI'                  -- MerchOne: merchant/brand fulfilment
       OR shop ILIKE 'b2b-shop-%.picanova.com'    -- Picanova's own business storefronts
B2C  = source_system = 'Picturator' AND shop NOT ILIKE 'b2b-shop-%'
OTHER= PCS / ORWO / Rewallution                   -- production/channel sources, report separately
```

**The trap it resolves.** `b2b-shop-eu.picanova.com` and `b2b-shop-us.picanova.com` (~291K shipments lifetime) sit on `source_system = 'Picturator'` — the *B2C platform* by the platform axis, but B2B by buyer. The `ILIKE` is evaluated first, so they land in B2B. Conflating the storefront (`shop`) with the platform (`source_system`) produced contradictory "B2B" numbers in a WICKEL 60×40 routing analysis (storefront → ~96% UPS vs canonical B2B/MerchOne → mostly Maersk).

**Scale (2026 YTD):** B2B ≈ 328K shipments / €2.0M (MerchOne 306K + storefronts 22K); B2C ≈ 1.15M / €7.4M; OTHER ≈ 1.03M / €1.2M. B2B ≈ 22% of TCG.

**Caveat.** The only Picturator business-buyer signal is the `b2b-shop-*` shop name; a wholesale/corporate order through an ordinary consumer storefront is invisible (counted B2C). Flag if a question hinges on total business-buyer volume.

**Cross-ref.** Mirrored into the agent contract at `shipping-agent/reference/sources.md` (§ "B2B vs B2C — strict definition"). Builds on [[S075_b3bb305b_shipping-agent-production-site-origin-awareness|S075]] (platform-level TCG = Picturator + MerchOne).

## Anchor [[S123_4a7041b5_b2b-b2c-strict-definition|S123]]
