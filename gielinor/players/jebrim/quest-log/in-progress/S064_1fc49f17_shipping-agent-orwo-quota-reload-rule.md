# S064 — Shipping-agent ORWO cost-quota transcript → reload-detection rule

**Born:** 2026-05-25 (sid 1fc49f17). Jebrim, activated first-message via "Hey Jebrim". Posted OPEN to comms. One live sibling all session: braindead-f3239bdc (dev-brain cockpit work, out of namespace).

## What this was

Principal handed over a 2nd shipping-agent board-prep transcript (the 1st was S063's board-numbers deck). Prompt to the agent: *"how has the cost quota developed since October for ORWO."* Asked: what can we teach the shipping agent from this. Became: critique → instrument the live mart → discover the real root → harvest → implement a rulebook rule → re-test → (commit pending).

## What happened

- **Critiqued the transcript.** The agent computed an invoice-line *proxy* quota for ORWO (cost field blank), titled the chart "ORWO shipping cost quota," and buried the proxy basis in a trailing caveat. Mapped it to the known root ("full rigor present, doesn't self-trigger on the fast path") — a 4th location after cause-attribution / scope-denominator / set-coherence. Initial framing: metric-unavailable + proxy-labeling.
- **Principal added a domain fact:** `fact_shipments` cost includes truck costs that are absent from `invoice_lines` → the proxy structurally understates. Sharpened the critique.
- **Instrumented the live mart before writing any DQ claim** (verify-before-write, the I3 scar). Found cost columns (`real`/`expected`/`avg`/`final` + `cost_source`) **100% NULL across ALL 5 sources** — 18.4M rows, revenue 99%+ populated, 56M invoice lines (€66.6M) present. **Principal: this is a DATA RELOAD IN PROGRESS, transient — exactly what the agent should catch.** Nearly wrote a wrong "ORWO cost null by design" DQ entry; instrumenting caught the mart-wide reload instead. **DQ pass dropped per principal — he runs it when data's back.**
- **Reframed the teaching** around the real root: transient-state / systemic-NULL detection. Harvested into the Jebrim bank note (2026-05-25 ORWO section). Implemented as **how_to.md rule 36** (every-mode; cost-null mart-wide + revenue/lines present → say "reloading," don't proxy, don't blame one source) + rule-11 first-gate pointer + §0 rule-count 35→36.
- **Re-tested** by spawning a naive general-purpose agent to embody the shipping agent on the exact ORWO prompt, blind to the changes. **The reload finished mid-test** — by the time the embodied agent queried, ORWO cost was populated, so it computed the *real* canonical quota (Oct 27.1% → Dec 30.1% peak → ~19–22% settled → May 26.9%), no proxy, basis stated, % invoiced per month, endpoints flagged as billing-completeness artifacts. Rule 36 was read + applied *as a gate* (agent: "had revenue been empty I would have stopped"). The reload-*block* branch could NOT be exercised (no reload left to catch) — honestly flagged, not claimed validated.
- **Bonus finding (for principal's post-reload DQ pass):** the embodied agent caught `coverage-audit.md` (stamped 2026-05-22) says ORWO revenue = 0.0% but live shows it fully populated — stamp stale after the reload landed. Not edited (his pass).

## Decisions

- DQ pass (known-dq.md + mart-contract.md §4 ORWO cost entry) **deliberately dropped** — transient reload, not a durable DQ fact; principal owns it post-reload.
- Rule 36 numbered after 35 (no renumber — preserves cross-references), explicit every-mode scope line, same pattern as S063's rule 35.
- Re-test honesty: gate-application validated; reload-block branch untestable until the next real reload window. Did not overclaim.

## Pending external actions

Commits NOT yet made (awaiting principal go, per global ask-before-commit):
- shipping-agent: `how_to.md` (rule 36 + rule-11 pointer + count) — local, will need push.
- brain: bank note 2026-05-25 section + comms OPEN/CLOSING + this quest-log + inventory resume.
