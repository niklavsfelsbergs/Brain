# Cockpit neuron overlay — v0 design sketch

> **Status.** Design parked, not built ([[S071_e11aff01_neuron-overlay-design|S071]], sid e11aff01, 2026-05-24). Build deferred until the live cockpit sessions land their work (zoom/layout rework + term.js paste fix) — see *Sequencing* below. Captured so resume can build straight from it.
>
> **Origin.** Principal asked "does the brain consist of thousands of wiki-links?" → discussion of what the *neurons* of this brain would be → chose to render it as a small live widget in the **top-right corner of the cockpit**, design **(b) a fixed overlay outside `.app-grid`**.

## One-liner

A small always-on canvas pinned to the cockpit's top-right corner that renders the brain as **functional regions that fire in real time** off the activity stream the cockpit already polls — and (v1) renders **draft→confirmed promotion as synapses hardening**. Not a file-graph hairball; a region-level "is the brain thinking, and where" monitor.

## Why the cockpit is the right host

The firing data is **already being polled**. `cockpit/web/main.js` runs, every 2s:

```js
const r = await fetch("/api/feed");        // items: { sid8, ts, kind, text }
// → feedState[sid8] = { kind, ts, text }  // kind = action | intent | needs_you | done | picked_up
```

That `/api/feed` stream is `switchboard/chat.ndjson` (written by `developer-braindead/.claude/hooks/emit-event.py`, served by `cockpit/backend.py`). The overlay reuses it — **no new hook, no new poll, no new backend for v0.**

## Placement decision — (b) fixed overlay, OUTSIDE `.app-grid`

The cockpit shell is a 3-column grid: `Board | console-col | FeedPanel` (`main.js` → `<div class="app-grid">`). The overlay does **not** join the grid. It is a `position:fixed; top; right` canvas that mounts its own DOM node.

Two reasons this beats docking it into the feed column:

1. **Dodges the `zoom:1.35` landmine.** The whole `.app-grid` renders under CSS `zoom:1.35`; [[S069_c3f2e3f3_terminal-scale-fix-and-brain-presentation|S069]] burned a session proving pixel-sensitive children break under it (xterm mouse-mapping drifted ~10 rows). A canvas mounted *outside* `.app-grid` gets honest 1:1 pixels for free — no counter-scale dance, and any future hover-a-neuron interaction Just Works. **If it ever moves inside the grid, it inherits the zoom bug** — keep it out.
2. **Lowest collision.** A new self-contained module barely touches shared files (see *Mount contract*), which matters because the cockpit is under active sibling edit right now.

## Data model the widget consumes

Per feed item (already emitted): `{ sid8, ts, kind, text }`, plus `/api/sessions` gives `{ sid8, actor, instance, state, building, intent, ... }` (the manifest, also already polled into `data.sessions`).

- **`actor`** → which hemisphere fires (`jebrim`, `zezima`, `guthix`, `braindead`, `unscoped/wisp`).
- **`kind`** → the firing *type* (table below).
- **`text`** → humanized action ("Editing active.md", "Reading chat.js", "Running git add cockpit/web/term.js"). Carries a (partial) path → region, best-effort. Region precision is an enhancement, not a v0 blocker.
- **`state`** (manifest) → tints the hemisphere (working / waiting / idle), matching the board chips.

## Region model (the "lobes")

Per **player** hemisphere (`jebrim`, `zezima`):

| Region | Layer | Brain analogue |
|---|---|---|
| hippocampus | `quest-log/` | episodic memory |
| semantic cortex | `bank/` | facts / knowledge |
| procedural | `spellbook/` | how-to / motor skill |
| working memory | `inventory/` | volatile scratch |
| self-model | `examine/`, `niksis8_character/` | self / other model |

Shared structures:

- **Identity core** (center, bright when consolidated) — any `confirmed/` path + `keepsake/current.md` + `lorebook/confirmed/`. The durable, hardened memory. Synapses migrate here on promotion (v1).
- **Guthix** — `deities/guthix/*`; a cross-region modulator that lights during consultation/bankstanding.
- **Braindead** — `developer-braindead/*` + `cockpit/` + `.claude/` (hooks/body); the external builder, drawn off to the side (he builds the brain, he isn't a region of it).

## Firing semantics — `kind` → visual

| `kind` | neural reading | render |
|---|---|---|
| `action` (Read) | inbound signal | dendrite glow on the region of the touched path |
| `action` (Edit/Write) | outbound signal | axon pulse out of the region |
| `action` (Bash/Grep) | diffuse activity | soft flicker on the actor's core / classified region |
| `intent` | a thought | glow at the actor's hemisphere core, radiating |
| `needs_you` | a spike that can't complete | **amber** synapse reaching *out of the brain* toward "you", pulsing until answered |
| `picked_up` | external stimulus | input flash entering from outside the network |
| `done` | settle | burst, then quiet |

Hemisphere tint follows manifest `state` (reuse board chip colors): working / waiting_for_user / idle / ended.

## Path → region classifier

The one bit of real logic. Two ways, start cheap:

- **v0 (zero shared-file edits): client-side best-effort.** `actor` already gives the hemisphere; regex the `text` for a layer keyword (`quest-log|bank|spellbook|inventory|examine|keepsake|lorebook|confirmed|drafts|deities/guthix`) to pick the region; fall back to "core flicker" when the path is ambiguous. Robust because **v0 is meaningful at hemisphere+kind granularity even when region is unknown** — "the Jebrim side is firing, working" already reads.
- **v0.5 (cleaner): stamp it at the source.** `emit-event.py` already has a path classifier (`path-map.json`); add a `region` field to the chat.ndjson record and pass it through `backend.py` `/api/feed`. Removes the fragile string-parse. Small hook edit — lower collision than cockpit/web files, but still defer behind the sibling work.

## Build phases

- **v0** — regions + live firing from `/api/feed`. "The corner brain pulses the hemisphere/region you're working in." Ambient, already useful. **No backend changes.**
- **v1** — consolidation: draft→confirmed renders a synapse *hardening* (dim dashed → solid bright, node migrates to identity core); archive → ghost-grey (never deleted, per `archive-discipline.md`); reject → snaps to a gutter. Needs a small **consolidation watcher**: poll the `confirmed/`/`drafts/`/`archive/` listings server-side (or parse `git mv drafts→confirmed` out of the action stream) and emit synapse events. This is the part no off-the-shelf brain-graph has — you'd *watch a memory consolidate during alching*.
- **v2** — both player hemispheres side by side + Guthix as a cross-region modulator that fires across the whole brain during bankstanding.

## Render approach

- Canvas 2D (or lightweight SVG). Regions as small clustered node groups; spikes as short-lived glow/edge animations keyed to incoming feed deltas; persistent synapses (v1) as edges whose weight = consolidation state.
- Reuse the cockpit OSRS palette (wood/parchment/gold) + the vendored `runescape-uf.woff`.
- Sizing: lives *outside* the `zoom:1.35`, so size in true px. Compact (~corner badge), click-to-expand to a larger panel later if wanted.
- Collapsible, like the feed (`lsBool`/`setLsBool` pattern already in `main.js` for `cockpit-feed`/`cockpit-sound`).

## Mount contract (minimal shared-file touch)

The whole point of (b): keep the footprint to near-nothing in contested files.

- **New file:** `cockpit/web/brain.js` — self-contained module: creates its own fixed-position container (appended to `document.body`, NOT into `#app`/`.app-grid`), starts its own poll of `/api/feed` (or accepts the parent's `feedState` via one prop), renders the canvas, cleans up on unmount.
- **Shared-file edits, ideally ≤2 lines total:** one `import` + one mount call. Cleanest is self-mount on import (`brain.js` calls its own init) so even `main.js` stays untouched. If a toggle button is wanted in the board header, that's the only `main.js`/`styles.css` line — defer it.
- **No `index.html` edit** beyond what the import map already allows (it's plain ESM; `main.js` can `import "./brain.js"`).

## Sequencing — why we wait

As of [[S071_e11aff01_neuron-overlay-design|S071]] the live manifest shows **two sibling sessions inside the cockpit**:

- `2f4981ed` (braindead·1) — just fixed the term.js paste-handler crash.
- `dbd41cc0` (braindead·2) — **actively reworking cockpit zoom/layout** ("scroll-to-zoom should resize the whole cockpit").

The zoom rework touches the exact layout the overlay sits over, and `main.js`/`styles.css` carry uncommitted sibling WIP. Even though (b) is the lowest-collision shape possible, building it into the shared tree now is a head-on [[D-024_parallel_player_coordination|D-024]] collision. **Hold until those land**, then build `brain.js` + coordinate the ≤2-line mount via `comms/active.md`.

## Open questions / deferred decisions

- Region precision via client-parse (v0) vs source-stamp (v0.5) — start client-side, promote to stamp if the parse is too lossy.
- Whether the overlay polls independently or shares the parent's `feedState` prop (sharing avoids a 2nd poll; independent keeps it fully self-contained). Lean self-contained for v0.
- Consolidation watcher mechanism (git-mv-parse vs dir-diff poll) — decide at v1.
- Does it belong to *one* cockpit window or should it reflect all sessions globally? `/api/feed` is global already → it shows the whole fleet's firing. Probably correct; confirm with principal.

## Related

- `cockpit-competitive-learnings.md` — the cockpit's product context (this is a "we lead on" differentiator: nobody renders consolidation).
- [[D-027_inward_outward_build_imbalance]] — the operability-vs-observability critique. This is observability; honest framing = a Sunday build, not ahead of the shipping-mart pilot (`gielinor`-side `plan.md` §C).
- [[D-028_switchboard_cockpit_rebuild]] — the cockpit spec this extends.
