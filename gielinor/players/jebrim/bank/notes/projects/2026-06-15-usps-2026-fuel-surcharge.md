# USPS first-ever fuel surcharge (2026)

**Confirmed** 2026-06-15 ([[S244_bb5d1f1a_na-quota-torsten-revenue-correction|S244]]/bb5d1f1a), penguin-verified against USPS Newsroom 2026-03-25 + corroborating logistics press. Full source-anchored writeup: `research/2026-06-15-usps-2026-fuel-surcharge.md`.

- **What:** USPS's **first-ever fuel surcharge** — a **flat 8% on base postage**, NOT a dynamic/indexed monthly surcharge (unlike UPS/FedEx fuel). Constant for the whole window.
- **Window:** effective **April 26, 2026 → January 17, 2027** ("time-limited"; USPS frames a permanent dynamic mechanism as future intent, undecided as of 2026-06).
- **Affected services:** Priority Mail Express, Priority Mail, **USPS Ground Advantage**, Parcel Select. (We ship 100% Ground Advantage in NA → fully exposed.)
- **Commercial rates ARE subject** — high-volume/negotiated shippers are not exempt; 8% on the negotiated base.
- **2026 base GRIs (separate from the surcharge):** Jan 18 (Ground Advantage avg +7.8%) and Jul 12. **No April base GRI** — April's only USPS price event is this surcharge.

**Why it matters for our data / mart:** the 8% surcharge **folds into the base-rate bucket** in `shipping_mart` — USPS bills all-in and our feed carries no separate USPS fuel line (USPS fuel bucket ≈ €0 every month). So it shows up only as a USPS per-parcel rate step (NA €6.14 Jan–Mar → €6.52 partial Apr → €7.19 full May), and a fuel-bucket query will NOT see it. Cost impact NA May ≈ €18.7k (≈ +0.87 quota pp); ~€9–11k/month run-rate at current USPS volume through Jan 2027. This is the mechanism behind the "USPS rate increase" Torsten flagged — and answers his fuel question (it IS a fuel surcharge, just invisible in the fuel bucket).

Cross-link: [[carrier-contracts]] digest (fuel/GRI), the NA-quota work [[S244_bb5d1f1a_na-quota-torsten-revenue-correction|S244]].
