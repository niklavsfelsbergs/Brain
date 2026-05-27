# Hermes fuel surcharge — Destatis diesel-fuel index, Q1 2026 replay

**Project:** EU Tender 2026 (Picanova shipping-carrier tender)
**Question:** What are the Destatis diesel-fuel producer-price-index values (base 2021=100) for Jan/Feb/Mar 2026, what fuel surcharge % does each map to on the Hermes ladder, and which of Hermes's two ladders (offer vs reply) is the correct one for a Q1 2026 replay?
**Date of research:** 2026-05-27 (firm-up pass appended 2026-05-27, P1b)
**Penguin:** P1 / P1b (Jebrim-scoped), sibling run-log `quest-log/in-progress/S099_p1_hermes-destatis-fuel.md`
**Confidence:** HIGH on Jan, Feb, AND Mar 2026 index values (firm-up pass closed the Feb/Mar gap — see §0b) and on the two-ladder reconciliation.

---

## 0b. FIRM-UP PASS (P1b, 2026-05-27) — Feb & Mar now HIGH confidence

The first pass derived Feb/Mar by chaining the press-release **motor-fuel (petrol+diesel combined)** MoM off the confirmed Jan anchor — MEDIUM, and the Mar figure (~151) turned out to be an **underestimate** because combined motor-fuel understated diesel's specific March spike. The firm-up pass found a cleaner, primary method.

**The method: the index IS the price relative to the 2021 annual average.** The Destatis *Dieselkraftstoff Abgabe an Großverbraucher* index, base 2021=100, is just `price ÷ (2021 annual-average price) × 100`. Two facts close it:

- **2021 annual-average Großverbraucher price = €108.66 / 100L** (Destatis, via LasiPortal + BGL). This is the index denominator.
- **Confirmed monthly Großverbraucher prices** (LasiPortal, 15th-of-month survey): Jan €133.08, Feb €133.36, Mar €172.25 / 100L.

Apply the formula — and it **self-validates on the Jan anchor**: 133.08 / 108.66 × 100 = **122.47 ≈ 122.5**, exactly the Destatis-confirmed Jan index. So the same formula on Feb/Mar is trustworthy:

| Month | Price €/100L (Großverbr., excl. VAT) | Index = price/108.66×100 | Rounded | vs prior pass |
|---|---|---|---|---|
| **Jan 2026** | 133.08 | 122.47 | **122.5** ✓ (matches confirmed) | was 122.5 — unchanged |
| **Feb 2026** | 133.36 | 122.73 | **122.7** | was ≈123.6 — **revised down** |
| **Mar 2026** | 172.25 | 158.52 | **158.5** | was ≈151 — **revised UP ~7.5 pts** |

**Independent corroboration of the Mar = 158.5:** the BGL "Dieselpreis-Information (Großverbraucher)" series reports the March index at **158,5** (search-surfaced from the BGL PDF metadata; the PDF itself is image-only and couldn't be machine-read, so this is one corroborating hit rather than a fully-opened cell). The price→index formula and the BGL figure agree to the decimal.

**Net surcharge change from the firm-up:**

- **Feb 2026 — index 122.7.** This sits **right on the 0% / 0.5% boundary** (0% band ≤ 122.7). At exactly 122.7 it is **0.00%** (≤ is inclusive); a hair higher and it flips to 0.50%. Feb is effectively the threshold itself — see the cliff note in §3. *(Prior pass had Feb at 123.6 → 0.50%; the firmer price-based index puts it right on the edge at 0%.)*
- **Mar 2026 — index 158.5 → ~7.0%** (range 6.5–7.0%) on the clean linear-band rule (§3). Note: the first pass quoted ~11% for March, which was wrong on two counts — the index was too low (~151) *and* the step arithmetic was inconsistent. The firmed index is **higher** (158.5) but the corrected ladder math gives a **lower** surcharge (~7.0%). Do not price March off the old ~11%.

The series question is also resolved: **Großverbraucher** (large-consumer) is the correct one — it's the series Hermes's Jan=122.3 anchor matches, and the only one all the carrier-republication feeds (BGL, LasiPortal, ZUFALL, trans.info) track. *Großhandel* (wholesale) and the consumer *Verbraucherpreisindex* are different series and are NOT what the ladder uses. See §1.

---

## 0. TL;DR / verdict

- **The correct series for a Q1 2026 replay is the current Destatis "Dieselkraftstoff (Abgabe an Großverbraucher)" producer-price index, base 2021 = 100.** That is the basis Hermes's **reply** uses (Jan 2026 = 122.3 ≈ Destatis 122.5).
- **Hermes's OFFER ladder (0% up to 155.3; "March 2026 index = 154.9 → 0%") is built on the OLD base 2015 = 100 diesel series**, which Destatis retired with the January-2024 reporting month. Using it for a 2026 replay would silently mismatch the published index by the rebasing factor (~1.27×). **Do not replay on the offer ladder.**
- **Resulting Hermes fuel surcharge, Q1 2026 (on the correct 2021=100 reply ladder) — FIRMED in P1b:**
  - **Jan 2026** — index 122.5 → **0.00%** (band ≤122.7). HIGH.
  - **Feb 2026** — index **122.7** → **0.00%** — sits *exactly on* the 0% threshold (≤122.7 inclusive). HIGH. *(Revised from the first pass's 123.6→0.50%; the price-based index lands on the edge.)*
  - **Mar 2026** — index **158.5** → **~7.0%** (range 6.5–7.0%, band ~156.4–158.9). HIGH on the index; the % is by linear-band rule off Hermes's two published endpoints (§3). *(First pass said ~11% — wrong on both index AND ladder arithmetic; corrected here.)*

The single most important finding: **the offer and reply ladders are the SAME ladder shape on DIFFERENT base years.** Pick the 2021=100 reply ladder and feed it the published 2021=100 diesel index.

---

## 1. The Destatis source — what it is, exact IDs

- **Statistic / EVAS:** **61241** — *Indizes der Erzeugerpreise gewerblicher Produkte (Inlandsabsatz)* / Producer Price Indices for commercial products (domestic sales).
  Landing: <https://www.destatis.de/EN/Themes/Economy/Prices/Producer-Price-Index-For-Industrial-Products/_node.html> (EN), <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/_inhalt.html> (DE).
- **Base year:** **2021 = 100.** Destatis rebased the whole 61241 family from **2015=100 → 2021=100 with the January-2024 reporting month**; all values from January 2021 were recalculated. Basis-changeover note: <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Methoden/Erlaeuterungen/basisumstellung.html>
- **The diesel sub-index Hermes prices off:** *Dieselkraftstoff bei **Abgabe an Großverbraucher*** (diesel fuel, delivery to large consumers — Destatis defines the delivery as 50–70 hl free delivery point). There is also a parallel *Abgabe an Großhandel* (delivery to wholesale) series; the carrier-relevant one is **Großverbraucher**. Both are part of EVAS 61241.
- **Where the diesel cell actually lives (two routes):**
  1. **GENESIS-Online** (free), database 61241, the goods-detail tables (61241-0006 / -0004 family). Portal: <https://www-genesis.destatis.de/genesis/online> — *note: JS-driven; the cell can't be read by a plain fetch, you have to query it in the portal or pull the CSV export.*
  2. **Dedicated monthly report** — *"Statistischer Bericht – Preise für ausgewählte Mineralölerzeugnisse"* (selected mineral-oil products), which carries the Dieselkraftstoff Großverbraucher index (base 2021=100) plus the average €/100L price. Data is in the **Excel download**, not the HTML page:
     - Jan 2026 report (publ. 2026-02-13): <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Publikationen/Downloads-Erzeugerpreise/statistischer-bericht-ausgewaehlte-mineraloelerzeugnisse-2170200262015.html>
     - Feb 2026 report (publ. 2026-03-13): <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Publikationen/Downloads-Erzeugerpreise/statistischer-bericht-ausgewaehlte-mineraloelerzeugnisse-2170200262025.html>
     - Mar 2026 report: <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Publikationen/Downloads-Erzeugerpreise/statistischer-bericht-ausgewaehlte-mineraloelerzeugnisse-2170200262035.html>

---

## 2. Monthly diesel index, Oct 2025 – Apr 2026 (base 2021=100, Großverbraucher)

| Month | Diesel index (2021=100) | Avg price €/100L (excl. VAT, incl. duties) | Source / status |
|---|---|---|---|
| Oct 2025 | not directly confirmed | ~120.82 €/hl (carrier republication) | €/hl figure from ZUFALL <https://www.zufall.de/dieselpreis/> — *price, not index* |
| Nov 2025 | not directly confirmed | ~123.41 €/hl (ZUFALL) | same |
| Dec 2025 | not directly confirmed (~111–112, *inferred from Jan −9.8%*) | **€121.31/100L** | price confirmed via trans.info quoting Destatis <https://trans.info/de/dieselpreise-explodieren-im-januar-2026-458080> |
| **Jan 2026** | **122.5** *(Hermes reply: 122.3)* | **€133.08/100L** | **CONFIRMED.** trans.info quotes Destatis verbatim: *"Das entspricht einem Indexstand von 122,5 (Basisjahr 2021 = 100)"* — <https://trans.info/de/dieselpreise-explodieren-im-januar-2026-458080>. MoM +9.8% vs Dec. Cross-check: official PE26_057 motor-fuels +7.5% MoM <https://www.destatis.de/EN/Press/2026/02/PE26_057_61241.html> |
| **Feb 2026** | **122.7** *(price-based, P1b)* | **€133.36/100L** | FIRMED (HIGH): 133.36 / 108.66 × 100 = 122.73. Price €133.36/100L from LasiPortal <https://www.lasiportal.de/service/dieselpreisindex/entwicklung-der-dieselpreise/>. *(First pass had ≈123.6 by chaining motor-fuel MoM — revised down.)* |
| **Mar 2026** | **158.5** *(price-based, P1b)* | **€172.25/100L** | FIRMED (HIGH): 172.25 / 108.66 × 100 = 158.52; BGL Großverbraucher series independently reports **158,5**. Price €172.25/100L from LasiPortal (same URL). *(First pass had ≈151 by chaining combined motor-fuel +22.3% — that aggregate understated diesel's specific spike; revised UP ~7.5 pts.)* |
| Apr 2026 | not confirmed (rising further) | ~167 €/hl "kalkulatorisch" (ZUFALL) | PE26_169 reports producer prices +1.7% YoY, motor fuels +34.0% YoY <https://www.destatis.de/EN/Press/2026/05/PE26_169_61241.html> |

**Reading the table — three traps to avoid:**

1. **Index ≠ €/100L price.** The €/100L prices (121.31, 133.08, 133.36, 172.25) happen to sit numerically near the index in early 2026, but they are *gross producer prices incl. energy tax / CO2 levy*, not the base-2021 index. The carrier-republication pages (ZUFALL, LasiPortal, BGL, spedition-mueller, kompetenz-bus) almost all publish the **price**, and several mislabel it "Preisindex." Only the trans.info quote and the Destatis Excel give the *index*.
2. **Survey-date offset.** LasiPortal labels by the **15th-of-month** survey; ZUFALL labels by **billing/reporting month** — so their tables are offset by one month against each other. Don't line them up naively.
3. **"Motor fuels" ≈ diesel, not = diesel — and this bit the first pass.** The press-release MoM figures the first pass chained on are *Kraftstoffe* (petrol + diesel combined). The combined aggregate **understated diesel's specific March spike** (combined +22.3% → implied index ~151; diesel-specific price moved +29.2% → actual index 158.5). **The firm-up pass (§0b) discards the MoM-chaining method** in favour of the direct price-based index (`price / 108.66 × 100`), which self-validates on the confirmed Jan anchor. Use the price-based numbers; the MoM-derived Feb/Mar in this row's history are superseded.
4. **The index denominator is fixed: 2021 annual-average Großverbraucher price = €108.66/100L** (= index 100.0). Every monthly index in this file is that month's Großverbraucher price ÷ 108.66 × 100. Source: Destatis 2021 annual average, via LasiPortal/BGL.

---

## 3. The Hermes fuel ladder (from the reply) and the per-month surcharge

**Ladder (as stated in Hermes's reply, base 2021=100):** 0.00% for index ≤ 122.7; then +0.50% per ~2.5-index-point band:

| Index band (2021=100) | Surcharge |
|---|---|
| ≤ 122.7 | 0.00% |
| 122.8 – 125.3 | 0.50% |
| 125.4 – 127.9 | 1.00% |
| 128.0 – 130.4 | 1.50% |
| 130.5 – 133.0 | 2.00% |
| … (+0.5% per ~2.5-pt band) … | … |
| 192.4 – 194.8 | 14.00% |

**The band-width math, done cleanly (P1b).** Two hard anchors from Hermes's ladder: 0% band tops out at **122.7**, and the **14% band is 192.4–194.8**. From 0% to 14% in 0.5% steps is **28 steps**. The first paid band starts at 122.8. So:

- Span 122.8 → 192.4 (lower edge of the 14% band) across 27 step-starts ⇒ width = 69.6 / 27 = **2.578 pts/step**.
- Cross-check on the published low bands: 122.8 / 125.4 / 128.0 / 130.5 — successive lower edges step ~2.55–2.6 pts. ✓ Consistent.

So the surcharge for an index `I` (for `I > 122.7`) is **`% ≈ ceil((I − 122.7) / 2.578) × 0.5%`** — round *up* to the band the index falls in.

- **Feb, I = 122.7:** at/below the 0% threshold ⇒ **0.00%**.
- **Mar, I = 158.5:** (158.5 − 122.7) / 2.578 = 35.8 / 2.578 = **13.9 steps** → 14th band ⇒ **14 × 0.5% = 7.0%**. Band edges ≈ 156.4–158.9, so 158.5 sits in the **7.0%** band (one step below it, 153.8–156.3, would be 6.5%). **Mar 2026 ≈ 7.0% (range 6.5–7.0% depending on the exact printed band edge around 158.5).**

> **Correction to the first pass.** The first pass quoted Mar ≈ **11–11.5%**, which was wrong on *two* counts: the index was too low (~151 vs the firmed 158.5) *and* the step arithmetic was inconsistent (it conflated "step number" with "percentage"). The clean linear rule on the firmed index 158.5 gives **~7.0%**. This is the single most material change in the firm-up pass — do not price March off the old ~11% figure.

*Caveat unchanged:* I have Hermes's ladder only as the two endpoints (≤122.7 = 0%; 192.4–194.8 = 14%) plus the first five bands. The ~7.0% for March rests on the linear rule being uniform across all 28 bands. **Confirm against Hermes's full printed ladder for the exact band edge around index 158.5** before pricing — a non-uniform band near the top could shift March by ±0.5%.

**Per-month surcharge result (Q1 2026) — FIRMED:**

| Month | Diesel index (2021=100) | Hermes band | **Fuel surcharge** | Confidence |
|---|---|---|---|---|
| **Jan 2026** | 122.5 | ≤122.7 | **0.00%** | HIGH |
| **Feb 2026** | 122.7 | ≤122.7 (on the edge) | **0.00%** | HIGH (index); knife-edge — see cliff note |
| **Mar 2026** | 158.5 | ~156.4–158.9 | **≈7.0%** (range 6.5–7.0%) | HIGH (index); % by linear rule, confirm band edge |

Note the cliff: Jan (122.5) and Feb (122.7) **both sit at or just under the 122.7 threshold**, so both are 0% — but Feb is *exactly on* the edge. If Hermes's Feb figure (offered to send) reads even 122.8, Feb flips to 0.50%. **This is the one number to get in writing from the carrier.** Mar is the outlier — the late-Feb/March oil spike (Destatis attributes part of it to the Iran/Middle-East conflict from 2026-02-28 and the January CO2-allowance step) lifts the index to 158.5, a ~7% surcharge.

---

## 4. The two-ladder reconciliation — RESOLVED

**The discrepancy:**
- **Offer (slide 8):** 0% band runs up to index **155.3**; offer text "March 2026 index = 154.9 → 0%".
- **Reply:** 0% band ends at **122.7**; "Jan 2026 = 122.3 → 0%".

**Resolution — they are the same ladder shape on two different base years:**

- The **reply** ladder (0% ≤ 122.7; Jan 2026 = 122.3) is internally consistent with the **actual current Destatis diesel index, base 2021 = 100**, which is **122.5 in Jan 2026** (confirmed, §2). ✅ This is the live, published series.
- The **offer** ladder (0% ≤ 155.3; "March 2026 = 154.9") is consistent with the **retired base 2015 = 100** diesel series. Destatis rebased 2015=100 → 2021=100 with the **January-2024 reporting month** (basisumstellung, §1). A diesel index that reads ~155 in early 2026 on a ~122 actual (2021=100) implies an old/new ratio of **154.9 / 122.5 ≈ 1.26**, i.e. the 2021 base year sat at roughly **126** on the old 2015=100 scale. That ~1.26 factor is exactly the kind of rebasing shift Destatis documents for the energy segment. *(Inferred from the rebasing note + the two anchor values; the precise 2015-basis diesel value for the 2021 average was not pulled from a raw cell.)*

**Which to use for a Q1 2026 replay:** **the reply ladder (base 2021 = 100).** Reasons:
1. It matches the index series Destatis actually publishes today; the 2015=100 diesel series is discontinued, so the offer ladder has no live feed to price against in 2026.
2. The "March 2026 = 154.9" figure in the offer is **not** a current-Destatis number — on the live 2021=100 series March 2026 is **158.5** (firmed, §0b), and that is a ~7% surcharge band, not a 0% point. Read on the offer ladder's own (old) scale, ~154.9 ≈ a 0% band; read on the live scale, 158.5 is a ~7.0% band. **The offer therefore drastically understates the March surcharge** if anyone naively fed a 2021=100 index into the offer ladder, or — worse — if Hermes intended the offer ladder to apply but quotes a stale 2015-basis value as "current." *(Coincidence to flag: the offer's stale "154.9" and the live 158.5 are numerically close — only ~4 pts apart — which makes the base-year mismatch easy to miss. They are different scales; do not treat the proximity as agreement.)*

**Action for the tender team:** confirm with Hermes in writing that the binding fuel clause uses the **base 2021=100 Großverbraucher diesel index** and the **reply ladder** (0% ≤ 122.7). If the contract text still references the offer ladder / a ~155 threshold, that is a base-year mismatch that must be corrected before signing — otherwise the surcharge formula and the index feed disagree by ~1.26×.

---

## 5. Hermes's €/Litre conversion — sanity check

Hermes reply: *"base year 2021 = €1.165/Litre"* and *"Jan 2026 = 122.3 = €1.424/Litre."*
- €1.424 / €1.165 = **1.222** → index **122.2**. ✅ Internally consistent with index 122.3 (Hermes is just applying the index to its own 2021 base price of €1.165/L).
- Note this €1.165/L base differs from the Destatis Großverbraucher 2021 average implied by the €/100L series (Destatis Jan-2026 avg €133.08/100L = €1.3308/L *incl. mineral-oil tax + CO2*). Hermes's €1.165/L base looks like a **net/ex-duty diesel price** specific to its own cost base, scaled by the Destatis *index movement*. That's a legitimate construction — Hermes uses the Destatis index as the *escalator*, not as an absolute price — but it means **the €/L figures are Hermes-internal; only the index (122.3 / 2021=100) is the Destatis-anchored, auditable number.** Replay should track the index, not Hermes's €/L.

---

## 6. Gaps & open questions

- **Feb & Mar 2026 — FIRMED in P1b, but via the price-based formula, not a raw GENESIS cell.** Feb 122.7 and Mar 158.5 are computed as `price / 108.66 × 100` off the confirmed Großverbraucher prices (133.36, 172.25) and self-validate on the Jan anchor (133.08→122.5). The Mar 158.5 is independently corroborated by the BGL Großverbraucher series. The one residual: the raw Destatis Excel cell / GENESIS 61241 diesel row for Feb and Mar was still not machine-openable (Excel-only, JS portal, image-PDF). Confidence is HIGH on the strength of the self-validating formula + the BGL agreement; pulling the raw cell would only move it from "HIGH-derived" to "HIGH-primary." **Hermes offered to send the Feb figure — accept it; it settles the 122.7 knife-edge directly.**
- **Wholesale vs large-consumer series — RESOLVED.** The carrier-relevant series is **Dieselkraftstoff Abgabe an Großverbraucher** (large consumer), confirmed: it's the series Hermes's Jan=122.3 matches and the one BGL/LasiPortal/ZUFALL/trans.info all track. *Abgabe an Großhandel* (wholesale) and the consumer *Verbraucherpreisindex für Kraftstoffe* are distinct series and are NOT what the ladder prices off. Do not substitute them.
- **Hermes full ladder line-by-line.** I have the first five bands + the two endpoints (≤122.7 = 0%; 192.4–194.8 = 14%) and computed the ~7.0% March band by the uniform linear rule (width 2.578 pts/0.5% step, §3). The March surcharge depends on that rule holding across all 28 bands; verify against Hermes's printed ladder for the exact band edge around index 158.5 (could shift March ±0.5%).
- **Oct/Nov 2025 and Apr 2026 index** values not confirmed as base-2021 index numbers (only €/hl prices via carrier republications). Not load-bearing for the Q1 replay but listed for context.
- **Offer's "154.9" provenance.** I inferred it's a 2015=100 reading from the rebasing math; I did not find the exact 2015-basis diesel value for early 2026 in a raw Destatis cell to nail the conversion factor to a decimal. The conclusion (offer = old base) is robust on the structure; the exact 1.26× factor is approximate.

---

## Sources

- Destatis EVAS 61241 landing (EN): <https://www.destatis.de/EN/Themes/Economy/Prices/Producer-Price-Index-For-Industrial-Products/_node.html> — the producer-price-index statistic, base 2021=100. Load-bearing: defines the statistic and base year.
- Destatis base-changeover note (2015→2021): <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Methoden/Erlaeuterungen/basisumstellung.html> — load-bearing for the two-ladder reconciliation (rebasing with Jan-2024 reporting month).
- trans.info, "Dieselpreise explodieren im Januar 2026": <https://trans.info/de/dieselpreise-explodieren-im-januar-2026-458080> — quotes Destatis verbatim: Jan 2026 diesel index = **122,5 (Basisjahr 2021=100)**, avg €133.08/100L, +9.8% MoM. The confirming source for the Jan anchor.
- Destatis PE26_057 (Jan 2026 producer prices, EN): <https://www.destatis.de/EN/Press/2026/02/PE26_057_61241.html> — motor fuels +7.5% MoM / +0.3% YoY; mineral oil +2.8% MoM.
- Destatis PE26_095 (Feb 2026): <https://www.destatis.de/EN/Press/2026/03/PE26_095_61241.html> — motor fuels **+0.9% MoM** / +1.6% YoY (basis for Feb index derivation).
- Destatis PE26_140 correction (Mar 2026): <https://www.destatis.de/EN/Press/2026/04/PE26_140_61241.html> — motor fuels **+22.3% MoM** / +29.5% YoY (basis for Mar index derivation); largest monthly producer-price gain since Aug 2022.
- Destatis PE26_169 (Apr 2026): <https://www.destatis.de/EN/Press/2026/05/PE26_169_61241.html> — context, motor fuels +34.0% YoY.
- "Ausgewählte Indizes" table (energy aggregate): <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Tabellen/Erzeugerpreise-GewProdukte-Ausgewaehlte-Indizes.html> — energy aggregate Jan 135.9 / Feb 133.4 / Mar 143.4 (NOT diesel; used only to sanity-check direction).
- "Statistischer Bericht – Preise für ausgewählte Mineralölerzeugnisse" Jan/Feb/Mar 2026 (Excel reports, carry the diesel Großverbraucher index): Jan <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Publikationen/Downloads-Erzeugerpreise/statistischer-bericht-ausgewaehlte-mineraloelerzeugnisse-2170200262015.html> · Feb <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Publikationen/Downloads-Erzeugerpreise/statistischer-bericht-ausgewaehlte-mineraloelerzeugnisse-2170200262025.html> · Mar <https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Erzeugerpreisindex-gewerbliche-Produkte/Publikationen/Downloads-Erzeugerpreise/statistischer-bericht-ausgewaehlte-mineraloelerzeugnisse-2170200262035.html> — the authoritative place to pull exact Feb/Mar cells.
- LasiPortal Dieselpreisindex Großverbraucher: <https://www.lasiportal.de/service/dieselpreisindex/entwicklung-der-dieselpreise/> — €/100L prices Jan 133.08 / Feb 133.36 / Mar 172.25 (15th-of-month survey). Price cross-check, not index.
- ZUFALL Dieselpreisentwicklung: <https://www.zufall.de/dieselpreis/> — €/hl series Oct 2025–Apr 2026 (billing-month labelling); price cross-check.
- GENESIS-Online portal (database 61241): <https://www-genesis.destatis.de/genesis/online> — the free raw database; JS-driven, query the 61241 goods table or CSV-export for the diesel cell.

### Sources added in the firm-up pass (P1b, 2026-05-27)

- **2021 base-price anchor (load-bearing for the price→index formula):** Destatis 2021 annual-average Großverbraucher diesel price = **€108.66/100L** (= index 100.0), surfaced via LasiPortal/BGL republication of the Destatis series. This is the denominator: every monthly index in this file = month price ÷ 108.66 × 100. Self-validates on the Jan anchor (133.08/108.66×100 = 122.47 ≈ confirmed 122.5).
- **BGL "Dieselpreis-Information (Großverbraucher)" PDF:** <https://www.bgl-ev.de/wp-content/uploads/simple-file-list/Dieselpreisinformationen/dieselpreisinfo-grossverbraucher.pdf> — the BGL monthly Großverbraucher index series, base 2021=100, published the 20th of the following month. Surfaced **March index = 158,5** (corroborates the price-based computation). PDF is image-only — couldn't be machine-read, so this is a search-metadata hit, not a fully-opened cell. BGL index landing: <https://www.bgl-ev.de/dieselpreisinformationen/>
- **LasiPortal March-2026 article** ("Preisindex im März 2026 wieder stark erhöht"): same URL as above — confirms the Feb→Mar price jump (133.36 → 172.25, +29.3%) that drives the Mar index to 158.5.
- **ADAC press release, "Diesel im März 2026 im Durchschnitt so teuer wie noch nie":** <https://presse.adac.de/meldungen/adac-ev/verkehr/diesel-im-maerz-2026-im-durchschnitt-so-teuer-wie-noch-nie.html> — March 2026 pump diesel avg €2.164/L, a record (vs €2.140 in Mar 2022). Independent confirmation of the magnitude of the March spike (direction + size), not the Großverbraucher index itself.
- **Method note on the carrier-republication feeds:** LasiPortal/BGL/ZUFALL/spedition-mueller/kompetenz-bus all publish the **price**, not the index, and ZUFALL is offset one month (billing-month labelling) vs LasiPortal (survey-month). Confirmed the offset directly: ZUFALL's "March 2026 = 133.08" is the *January* Destatis figure. The price→index formula (÷108.66×100) is what converts any of these price feeds to the base-2021 index.
