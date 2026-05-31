# S135 — 2026-05-31 — brain map improvements + cockpit dev/preview backend

**Opened:** 2026-05-31
**Actor:** Braindead (dev-brain)
**Cue:** "Lets develop gielinor. [screenshot of the cockpit BRAIN map] so this doesnt look so great. Give me options for how we could improve it"

## Intent

Principal showed the cockpit BRAIN map (the 3D force-directed graph in `cockpit/web/brain.js`) and finds it ugly. Wants a menu of options to improve it. Read-only diagnosis this turn → ranked options → multiple-choice with a recommendation. No build without sign-off.

## Diagnosis (from brain.js + screenshot)

The current map: 690 nodes / 1742 links, 3D orbit camera, per-cluster gravity anchors, constant slow auto-spin. Why it reads bad:

1. **Off-center clump.** The mass sits in the left third, not centered. `fitView()` recenters scale but the green blob's visual centroid is off because `dev` (≈half the nodes) dominates — its anchor blob pulls the perceived center left. Possibly compounded by a stale `view.tx/ty` pan.
2. **Hairball density.** REP=720 / SPR=0.05 / L0=34 over 690 nodes packs the big clusters into an indistinct mush; structure is invisible.
3. **Colour domination.** `dev` green (#6fae6a) blended 78% over parchment → most of the screen is one green region because dev wins by raw count. The "distinct coloured regions" goal fails visually.
4. **Dust nodes.** Low-degree / isolated notes spray out as faint scattered dots on the right (repulsion with no link to pull them home), reading as noise.
5. **3D tradeoff.** A rotating ball is cool briefly but inherently fights legibility — you can't reliably find/read a node. Obsidian's own graph is 2D for this reason. (Principal explicitly asked for 3D in [[S129_e291b8fc_cockpit_polish_3d_brain|S129]], so this is a tension to name, not silently undo.)

## Turns

### T1 — entry + diagnosis + options menu
- Entry clean: sid 304c77fd (distinct from sibling 04ef0adc fun-features). OPEN posted, active-mode=dev-brain, intent set, this quest opened.
- Read brain.js fully. Diagnosed above.
- Offered ranked options (tune-in-place / 2D-Obsidian / structured-layout / filtering-LOD) as multiple-choice; Niklavs asked to clarify first.
- **Feedback memory updated** (`feedback_address_principal_as_you`): never call him "the principal" — "you" in chat, "Niklavs" where third-person is needed.

### T2 — Niklavs likes it; three concrete upgrades → BUILT
- Reframe: the map looks cool, he wants it *better*. Three asks: (a) make the sphere boundary visible, (b) zoom to cursor not centre, (c) de-blob dense regions.
- Built all three in `cockpit/web/brain.js` (node --check clean, RUNTIME-UNVERIFIED till relaunch):
  - **Sphere shell** — `drawSphere()`: faint gold lat/long wireframe at `sphereR` (90th-pctile node distance, computed in `fitView`, so outliers don't balloon it); same camera transform; per-segment depth alpha (back dim / front bright); drawn behind the cloud.
  - **Zoom-to-cursor** — `onWheel` shifts `tx/ty` so the point under the mouse stays fixed (`tx'=(mx-cx)(1-k)+tx*k`).
  - **De-blob** — per-section gravity + seed sizing in `loadGraph`: count each cluster, then big sections held looser (`grav *= clamp(9/√n, 0.4, 1)`) + seeded wider (`seedR *= clamp(√n/3.5, 1, 4.5)`); plus `REP 720→1000`, `L0 34→44`, `AR 2.1R→2.3R`, settle ticks `110→170`.
- My take on the blob (recorded): pure spacing inflates the whole cloud but keeps the dense region proportionally dense; the real lever is letting big sections breathe in proportion to size. Spacing bumps are additive on top.
- Next: relaunch eyeball; tunables if off = the per-section `grav`/`seedR` clamps, `REP`/`L0`, `sphereR` percentile + wireframe alpha (`0.03 + 0.13*depth`), `RINGS`/`SEG`.

### T3 — cockpit test/preview environment → BUILT + verified
- Niklavs: can I make a test env so I keep talking to agents in the live cockpit while seeing the result of my changes? (He said "switchboard"; means the cockpit.)
- Grounded the architecture before proposing: `run(port=…)` already parameterized; the UI + terminal transport over HTTP/WS relative to `location.host` (browser-compatible, token baked into the page); `backend.py` *reads* fleet state (hooks write it) so a second backend shows the same fleet without ghosts; no `/chat` route anymore (driving = `/pty` only); single-instance guard not built (wouldn't block a 2nd port anyway). Confirmed a backend is live on 8770 (HTTP 200).
- Offered 3 options (browser-tab-zero-build / dedicated dev backend / + hot-reload) multiple-choice w/ recommendation. **Niklavs picked the dedicated dev backend.**
- **Built:** `backend.py` — `--port`/`--dev` argparse + `make_app(dev)`/`run(port,dev)` + a `_dev_guard` aiohttp middleware that 403s `/pty` and `POST /api/rename` when `dev_mode`. New `cockpit/run-dev.bat` (launches `:8771 --dev`, opens browser). `_about.md` documented (How-to-run + Files).
- **Verified end-to-end** (started `:8771 --dev`, probed, killed): `/` 200, `/api/sessions` 200, `/api/feed` 200, `POST /api/rename` **403**, `/pty` **403**. Probe process stopped; 8771 confirmed down (no lingering confound). Live 8770 untouched (not probed for `/pty` — would spawn a real session).
- **Usage:** `cockpit\run-dev.bat` → browser on :8771 (read-only, mirrors live fleet); F5 for web/ edits, Ctrl+C+re-run for backend.py edits. Live cockpit on 8770 keeps driving agents.
- Not committed (ask-before-commit). Files touched: `cockpit/backend.py`, `cockpit/run-dev.bat` (new), `cockpit/_about.md`, plus the brain.js T2 work.

### T4 — two more map tweaks (eyeball-driven)
- **Invert Y-axis rotation** — `onMove` rotate branch: `view.yaw += dx` → `-= dx` (horizontal drag orbits the other way). Read "rotation on the y axis" as yaw (rotation about the vertical axis); flagged the alt reading (invert pitch / vertical look) as a one-char flip if I misread.
- **`center` button** — new `mkBtn("center", …)` in the BRAIN header resets pan (`tx=ty=0`) + `fitView()` (zoom-to-fit), so the graph snaps back to centered + framed. Leaves rotation alone.
- Both `node --check` clean, RUNTIME-UNVERIFIED till F5 on the dev backend. `cockpit/web/brain.js` only.

## Close

**What shipped:** (1) brain-map upgrades in `cockpit/web/brain.js` — sphere wireframe shell, de-blobbed layout (big sections held looser + seeded wider, plus more baseline spacing), zoom-to-cursor, inverted Y-axis rotation, a `center` button. (2) An isolated cockpit **dev/preview backend** — `backend.py --port/--dev` + a `_dev_guard` middleware (403s `/pty` + `POST /api/rename`), a `run-dev.bat` launcher, `_about.md` docs. Verified end-to-end (reads 200, drive/write 403; probe killed, port freed).

**Feedback captured:** Niklavs corrected "the principal" → call him **Niklavs**/"you" (memory `feedback_address_principal_as_you` updated; also a build-lesson on the commit hazard below).

**Commit-scope hazard (flagged to Niklavs):** `cockpit/web/brain.js` was `M` *before* this session began — a coherent but **uncommitted feature layer** (lightning bolts `drawBolt`/`BOLTS`, the click-to-open node popup `brain-pop`/`openNode`, breathing last-touched glow) sat on top of HEAD([[S129_e291b8fc_cockpit_polish_3d_brain|S129]]) with no live sibling owning it. A file can't be partially committed and my verified work is entangled with it, so this session's commit **folds that orphaned layer in** under S135 with this note, rather than leave my work uncommitted. Fully recoverable via git if attribution should differ.

**Open / next:** relaunch (or dev-backend F5) to eyeball all five map changes + the invert/center; tunables = per-section `grav`/`seedR` clamps, `REP`/`L0`, `sphereR` percentile, wireframe alpha, `RINGS`/`SEG`. Alt reading of "invert Y" (pitch/vertical-look) is a one-char flip if I misread. Standing dev backlog unchanged.

**Cascade.** `cockpit/web/brain.js` (5 map upgrades + folded-in orphaned bolts/popup/breathing layer), `cockpit/backend.py` (`--port`/`--dev` + `_dev_guard`), `cockpit/run-dev.bat` (new), `cockpit/_about.md` (dev-backend docs), `developer-braindead/quest-log/S135_*.md` (this), `developer-braindead/comms/active.md` (OPEN/UPDATE×2/CLOSING), `developer-braindead/bank/build-lessons.md` (commit-base lesson), `respawn.md` (prepend).

**Main-brain changes.** none. (No `gielinor/` writes this session. The dirty `gielinor/meta/communication-protocol.md` etc. belong to parallel Guthix/Jebrim sessions — steered clear, excluded from the commit. The `feedback_address_principal_as_you` memory lives outside the repo.)
