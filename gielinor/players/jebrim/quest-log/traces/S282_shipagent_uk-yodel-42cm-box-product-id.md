# Trace — shipping-agent: UK Yodel 42.1cm box product identity

- Player in scope: Jebrim
- Spawned: 2026-06-19 (S282-era), red-team follow-up to the 1,743-parcel Yodel Medium-tier-miss isolation
- Tier: gold-contract for product identity (packagetype + orderitems on the four gold facts); maintainer profile present but did NOT need upstream — gold carried it

## Ask
Identify the product/SKU/format/category behind population P (1,743 UK mainland Yodel parcels that miss Medium by ~1cm: d_long 64-70, d_mid>41, etc., shop_order_created 2026-Q1, invoice cost, Picturator+PicaAPI). Split the ~1,679 shallow box (66x42x8.5) from the ~64 deep box (66x42x20.5-27).

## Turn log
- Reproduced P exactly: 1,743 parcels (len 66.0-66.1, mid 42.0-42.1, short 8.5-27.0). Matches brief.
- fact_shipments product fields: only packagetype / packagetype_group (box descriptor, not product); no name/format/canvas-size column. orderitems: sku, articlenumber, quantity, product_key, format_key (format_key NULL across the board).
- packagetype split: shallow box (1,679) = "WICKELVERPACKUNG 60x40_Box in the Box"; deep box (64) = "WICKELVERPACKUNG 60x40 (2stk./3stk. strapped)" — multi-item strapped consolidation.
- Composition: NOT single-item. Shallow avg 5 items / 4 lines; deep avg 15 items / 14 lines. Multi-item consolidation boxes.
- Product family by SKU prefix: Canvas print (CVS) 73.3% of items, 5,991 shallow + 1,012 deep. MixPix/MixBlox 16.7%, Cushion 6.5%, rest <1%. Canvas is the only family in the deep box at scale.
- Box driver: every deep box (64/64) and 90% of shallow (1,506/1,679) contain >=1 canvas. 60x40 canvas item present in 555 shallow + 33 deep. 66x42 box = 60x40cm canvas format + packing margin. Box name literally carries "60x40".

## Headline
Both boxes are the standard **60x40cm canvas-print wrap-box** ("WICKELVERPACKUNG 60x40"). Product = **canvas prints**, dominantly the 60x40cm format. Shallow = 1-layer Box-in-the-Box; deep = 2-3 canvases strapped. Identity from packagetype (fact_shipments) + sku/articlenumber (orderitems). NOT single-product parcels — multi-item, canvas-dominated.

## Caveats
- Cost basis: invoiced-only (cost_source='invoice'), per brief scope. Product-id work is dimension/orderitem-based, not cost — basis not load-bearing here.
- Product family = SKU-prefix classification (CVS=canvas etc.), confirmed against self-describing articlenumbers (KLAS/QUAD/DIGI/PAN1 = canvas formats). dim_products (dw, off-contract) not needed — gold sku/articlenumber were self-describing.
- format_key NULL across all P orderitems — not a usable identifier in this mart state.
