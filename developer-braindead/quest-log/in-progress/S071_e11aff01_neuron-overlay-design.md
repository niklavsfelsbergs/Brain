# S071 — cockpit neuron-overlay design sketch

**Session:** e11aff01 · 2026-05-24 · dev-brain (entered via "lets develop gielinor")
**Status:** OPEN — design parked, build deferred until live cockpit sessions land.

## Arc

Started as a question, not a task: principal asked *"does the brain consist of thousands of wiki-links or how does it work?"* — corrected the framing (layered markdown filesystem + gated write-discipline + hook guarantees + players/modes/rituals; wiki-links are glue, not substance). That led to *"what would the neurons be"* if the brain were rendered as a live neural net. Mapped it four ways:

1. files=nodes, `[[links]]`=edges — pretty but hollow (mostly chronological scaffolding).
2. layers=functional regions (hippocampus=quest-log, semantic=bank, procedural=spellbook, working=inventory, self=examine).
3. the live hook event stream (`chat.ndjson` / cockpit feed) — **already firing**; each tool call is a spike.
4. drafts→confirmed promotion = synaptic consolidation (Hebbian/LTP); alching/bankstanding = sleep consolidation. **The deep one.**

Principal chose to build it into the cockpit, **top-right corner**, design **(b) fixed overlay outside `.app-grid`**.

## What I did (design only — zero cockpit edits)

- Wrote the v0 spec → `developer-braindead/bank/research/cockpit-neuron-overlay-design.md`. Covers: why the cockpit (firing data already polled via `/api/feed` every 2s in `main.js`); placement (b) + the two reasons (dodges `zoom:1.35`, lowest collision); data model; region model; firing semantics (`kind`→visual); path→region classifier (client-parse v0 vs source-stamp v0.5); build phases v0/v1/v2; render approach; **mount contract** (new `cockpit/web/brain.js`, self-mounts fixed overlay, ≤2-line shared-file touch); the zoom landmine note; sequencing; open questions.
- Posted comms OPEN + a heads-up to @dbd41cc0 (the live zoom/layout sibling).

## Why parked

Live manifest at session time: `dbd41cc0` (braindead·2) is WORKING on cockpit zoom/layout ("scroll-to-zoom resizes the whole cockpit") — the exact surface the overlay sits over; `main.js`/`styles.css` carry uncommitted sibling WIP. Building into the shared tree now = head-on D-024 collision. Hold until it lands.

## Resume — next concrete step

1. Check the cockpit is settled (dbd41cc0 CLOSING'd; zoom/layout committed).
2. Build v0 from the spec: new `cockpit/web/brain.js` — fixed overlay outside `.app-grid`, polls `/api/feed`, renders actor-hemisphere + region firing on a canvas, OSRS palette. Keep shared-file touch ≤2 lines (ideally self-mount on import).
3. Coordinate the mount line via `comms/active.md` before editing `main.js`.
4. v1 (consolidation: synapses hardening on draft→confirmed) is a later pass — needs the consolidation watcher.

Not the load-bearing next step for the brain overall — that's still the parked shipping-mart pilot (gielinor `plan.md` §C, per [[D-027_inward_outward_build_imbalance]]). This is the Sunday build.

## Not committed

Nothing committed (principal hasn't cued commit). The spec is a clean new file ready to `git add` on cue; comms + this quest-log likewise.
