// brain.js — the brain graph, Obsidian-style. The real vault as one clean
// force-directed node graph (cockpit/web/graph.json, exported by
// cockpit/graph-export.py with the same resolver as obsidian-graph-report.py).
//
//   nodes = every .md note in both brains (~690)   edges = resolved [[wikilinks]]
//   Calm + muted at rest (faint regional tint, thin edges) — like Obsidian's
//   graph view, NOT a rainbow. Hover a node to FOCUS it: it + its neighbours +
//   their links light up, the rest dims. Live: a note fires → its node flares
//   and signal pulses snap down its synapses. Drag to pan, wheel to zoom.
//
// Docked as a square at the top of the feed column (feed.js mounts it via
// mountBrain). Sizes its canvas off its real rendered box each frame → agnostic
// to the .app-grid zoom:1.35. No deps, no build, no backend/hook change.

import { mdToHtml } from "./md.js";

const cssVar = (n, f) => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || f;
const escHtml = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const PAL = {
  bg:   cssVar("--bg", "#17120b"),
  panel:cssVar("--panel", "#2a2114"),
  line: cssVar("--line", "#6e5a2c"),
  ink:  cssVar("--ink", "#f1e7c4"),
  dim:  cssVar("--ink-dim", "#cdb985"),
  faint:cssVar("--ink-faint", "#9d8a5c"),
  gold: cssVar("--gold", "#e3b73c"),
};
// regional hue per group — each region a distinct, saturated colour so the map
// reads as coloured regions instead of one parchment mass. dev (the biggest
// region) gets its own green rather than the old tan that washed into yellow.
const GROUP_HUE = {
  jebrim: cssVar("--crew", "#5a9fe0"), zezima: cssVar("--answers", "#ff5d8f"),
  guthix: cssVar("--alching", "#b07ad8"), identity: cssVar("--gold", "#e3b73c"),
  "gielinor-core": cssVar("--wrapped", "#34c0ad"), gielinor: cssVar("--ship", "#46c8d8"),
  dev: "#6fae6a", infra: "#8f8aa0",
};
function rgba(hex, a) {
  const h = hex.replace("#", "");
  return `rgba(${parseInt(h.slice(0,2),16)},${parseInt(h.slice(2,4),16)},${parseInt(h.slice(4,6),16)},${a})`;
}
function blendHex(a, b, t) {       // t = weight of a
  const p = (h) => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)];
  const A = p(a), B = p(b), m = (i) => Math.round(A[i] * t + B[i] * (1 - t)).toString(16).padStart(2, "0");
  return "#" + m(0) + m(1) + m(2);
}
// node colour: hue-DOMINANT (78% regional hue + 22% parchment for warmth/cohesion)
// so regions read as their own colour instead of a uniform yellow blob.
const nodeColorCache = {};
const nodeColor = (g) => (nodeColorCache[g] ||= blendHex(GROUP_HUE[g] || PAL.faint, PAL.dim, 0.78));
function fireColor(kind, text) {
  if (kind === "needs_you") return cssVar("--answers", "#ff5d8f");
  if (kind === "done") return cssVar("--wrapped", "#34c0ad");
  if (kind === "intent" || kind === "comms") return cssVar("--alching", "#b07ad8");
  if (/^Reading\b/i.test(text)) return cssVar("--crew", "#5a9fe0");
  if (/^(Editing|Writing|Creating)\b/i.test(text)) return PAL.gold;
  return PAL.dim;
}

// ── graph state ──
let NODES = [], LINKS = [], ADJ = [];
let CLUSTERS = [];           // {name, ax, ay, az, n} — one spatial anchor per section
let baseByName = new Map();
let charge = new Map();      // gi -> {v,color,fresh}
let PULSES = [];
let BOLTS = [];              // lightning arcs drawn when the touched file moves to another node
let lastTouched = -1, lastColor = null;   // most-recent touched node — stays glowing + breathing
let seenMaxTs = 0, firstPoll = true, alpha = 0;
const TRAIL_OFF = true;      // clean hard-clear each frame (Obsidian look, no smear)
const PULSE_SPEED = 0.05, PULSE_CAP = 500, PULSE_PER_FIRE = 8;
const BOLT_SPEED = 0.045, BOLT_CAP = 24, BREATHE_SPEED = 0.05;

// 3D camera: yaw/pitch orbit + a constant very-slow auto-spin. The cloud is
// centred at the origin (gravity holds it there), so there's no pan — drag
// rotates, wheel zooms. Projection is weak-perspective (nearer nodes a touch
// bigger + brighter); per-node screen coords are cached on the node each frame
// by projectAll() so the renderer + hover hit-test read a.sx/a.sy.
const view = { w: 320, h: 320, scale: 1, yaw: 0, pitch: 0.32, tx: 0, ty: 0, drag: false, dragMode: null, mx: 0, my: 0, hover: -1 };
const AUTO_SPIN = 0.0001;     // rad/frame — one revolution ≈ 17min at 60fps, extremely slow
let cloudR = 200, FOCAL = 520; // sphere radius + perspective focal length (set in fitView)
let sphereR = 200;            // radius of the drawn wireframe shell (a node-distance percentile, so outliers don't balloon it)

function projectAll() {
  const cy = Math.cos(view.yaw), sy = Math.sin(view.yaw);
  const cp = Math.cos(view.pitch), sp = Math.sin(view.pitch);
  const cx = view.w / 2, cyc = view.h / 2, s = view.scale;
  for (let i = 0; i < NODES.length; i++) {
    const a = NODES[i];
    const x1 = a.x * cy + a.z * sy;        // yaw about the vertical (Y) axis
    const z1 = -a.x * sy + a.z * cy;
    const y2 = a.y * cp - z1 * sp;          // pitch about the horizontal (X) axis
    const z2 = a.y * sp + z1 * cp;
    const proj = FOCAL / (FOCAL - z2);      // weak perspective; +z = toward viewer
    a.srz = z2; a.sps = proj;
    a.sx = cx + view.tx + x1 * s * proj;
    a.sy = cyc + view.ty + y2 * s * proj;
  }
}

// ── 3D force sim: repulsion + link springs + per-cluster gravity, cooling ──
// Each node is pulled toward its SECTION's anchor (CLUSTER_GRAV) instead of a
// single origin, so bank / examine / quest-log / … each settle into their own
// region of the cloud. A weak origin pull (GRAV) keeps the whole thing centred.
const REP = 1000, SPR = 0.05, L0 = 44, GRAV = 0.004, CLUSTER_GRAV = 0.14;
function tick() {
  if (alpha < 0.02) { alpha = 0; return; }
  const n = NODES.length;
  for (let i = 0; i < n; i++) {
    const a = NODES[i];
    for (let j = i + 1; j < n; j++) {
      const b = NODES[j];
      const dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z;
      const d2 = dx * dx + dy * dy + dz * dz || 0.01, d = Math.sqrt(d2);
      const f = (REP * alpha) / d2, ux = dx / d, uy = dy / d, uz = dz / d;
      a.vx -= ux * f; a.vy -= uy * f; a.vz -= uz * f;
      b.vx += ux * f; b.vy += uy * f; b.vz += uz * f;
    }
  }
  for (const e of LINKS) {
    const a = NODES[e.s], b = NODES[e.t];
    const dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z, d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 0.01;
    const f = SPR * alpha * (d - L0), ux = dx / d, uy = dy / d, uz = dz / d;
    a.vx += ux * f; a.vy += uy * f; a.vz += uz * f; b.vx -= ux * f; b.vy -= uy * f; b.vz -= uz * f;
  }
  for (const a of NODES) {
    const c = CLUSTERS[a.cl];               // pull toward this node's section anchor (looser for big sections — see loadGraph)
    if (c) { const cg = c.grav * alpha; a.vx += (c.ax - a.x) * cg; a.vy += (c.ay - a.y) * cg; a.vz += (c.az - a.z) * cg; }
    a.vx += -a.x * GRAV * alpha; a.vy += -a.y * GRAV * alpha; a.vz += -a.z * GRAV * alpha;
    a.vx *= 0.82; a.vy *= 0.82; a.vz *= 0.82;
    a.x += Math.max(-30, Math.min(30, a.vx)); a.y += Math.max(-30, Math.min(30, a.vy)); a.z += Math.max(-30, Math.min(30, a.vz));
  }
  alpha *= 0.985;
}
function fitView() {
  if (!NODES.length) return;
  let R = 1;
  const dists = [];
  for (const a of NODES) { const d = Math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z); dists.push(d); if (d > R) R = d; }
  cloudR = R; FOCAL = R * 2.6;
  // sphere shell radius = ~90th-percentile node distance, so a few far outliers
  // don't balloon the drawn sphere past the bulk of the cloud.
  dists.sort((x, y) => x - y);
  sphereR = dists[Math.floor(dists.length * 0.9)] || R;
  const pad = 34, half = Math.min(view.w, view.h) / 2 - pad;
  const maxProj = FOCAL / (FOCAL - R);     // the nearest possible node, biggest projection
  view.scale = Math.max(0.05, half / (R * maxProj));
}

// ── live firing ──
function extractMd(text) { const out = [], rx = /([\w.\-]+\.md)/g; let m; while ((m = rx.exec(text))) out.push(m[1].toLowerCase()); return out; }
function ingest(it) {
  const kind = it.kind || "action", text = it.text || "", col = fireColor(kind, text);
  let primary = -1;                                   // the file this action is touching
  for (const name of extractMd(text)) {
    const hits = baseByName.get(name);
    if (hits) for (const gi of hits) { charge.set(gi, { v: 1, color: col, fresh: true }); if (primary < 0) primary = gi; }
  }
  if (primary >= 0) {
    // moved to a different file → arc a lightning bolt from the last one to this one
    if (lastTouched >= 0 && lastTouched !== primary) {
      BOLTS.push({ a: lastTouched, b: primary, t: 0, color: col });
      if (BOLTS.length > BOLT_CAP) BOLTS.splice(0, BOLTS.length - BOLT_CAP);
    }
    lastTouched = primary; lastColor = col;
  }
}
function spawnPulses(gi, color) {
  const ns = ADJ[gi] || [], k = Math.min(ns.length, PULSE_PER_FIRE);
  for (let q = 0; q < k; q++) PULSES.push({ a: gi, b: ns[q], t: 0, color });
  if (PULSES.length > PULSE_CAP) PULSES.splice(0, PULSES.length - PULSE_CAP);
}
// a jagged electric arc between two screen points — fades with `alpha` (1→0),
// re-jittered each frame so it crackles. Drawn additively (composite "lighter").
function drawBolt(x1, y1, x2, y2, color, alpha) {
  const segs = 11, dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy) || 1;
  const px = -dy / len, py = dx / len, amp = Math.min(24, len * 0.16);
  ctx.beginPath(); ctx.moveTo(x1, y1);
  for (let s = 1; s < segs; s++) {
    const f = s / segs, j = (Math.random() - 0.5) * amp * Math.sin(f * Math.PI);  // 0 at both ends
    ctx.lineTo(x1 + dx * f + px * j, y1 + dy * f + py * j);
  }
  ctx.lineTo(x2, y2);
  ctx.strokeStyle = rgba(color, 0.85 * alpha); ctx.lineWidth = 1.8; ctx.stroke();  // coloured glow
  ctx.strokeStyle = rgba("#ffffff", 0.6 * alpha); ctx.lineWidth = 0.7; ctx.stroke(); // bright core
}

// ── render ──
let cnv, ctx, dpr = 1, _frame = 0;
function applySize(w, h) {
  view.w = Math.max(1, Math.round(w)); view.h = Math.max(1, Math.round(h));
  dpr = window.devicePixelRatio || 1; cnv.width = view.w * dpr; cnv.height = view.h * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
// depth of a node in [0 far .. 1 near], from its rotated z
const depthOf = (a) => Math.max(0, Math.min(1, a.srz / cloudR * 0.5 + 0.5));

// ── sphere shell ── a faint lat/long wireframe at sphereR, rotated by the same
// camera as the nodes, so the cloud reads as sitting *inside* a sphere. Each
// segment's alpha rides its depth (back half dim, front half brighter), which is
// what sells the 3D roundness. Drawn behind the nodes (right after the bg clear).
function drawSphere() {
  if (!NODES.length) return;
  const R = sphereR, cy = Math.cos(view.yaw), sy = Math.sin(view.yaw), cp = Math.cos(view.pitch), sp = Math.sin(view.pitch);
  const cx = view.w / 2, cyc = view.h / 2, s = view.scale;
  const P = (x, y, z) => {
    const x1 = x * cy + z * sy, z1 = -x * sy + z * cy;
    const y2 = y * cp - z1 * sp, z2 = y * sp + z1 * cp;
    const proj = FOCAL / (FOCAL - z2);
    return { sx: cx + view.tx + x1 * s * proj, sy: cyc + view.ty + y2 * s * proj, z: z2 };
  };
  const SEG = 48, RINGS = 6;
  ctx.globalCompositeOperation = "source-over";
  ctx.lineWidth = 0.85;
  const arc = (fn) => {
    let prev = null;
    for (let i = 0; i <= SEG; i++) {
      const p = fn(i / SEG);
      if (prev) {
        const depth = Math.max(0, Math.min(1, ((p.z + prev.z) / 2) / R * 0.5 + 0.5));
        ctx.strokeStyle = rgba(PAL.gold, 0.08 + 0.30 * depth);
        ctx.beginPath(); ctx.moveTo(prev.sx, prev.sy); ctx.lineTo(p.sx, p.sy); ctx.stroke();
      }
      prev = p;
    }
  };
  for (let mr = 0; mr < RINGS; mr++) {        // meridians — great circles through the poles
    const lon = mr * Math.PI / RINGS, cl = Math.cos(lon), sl = Math.sin(lon);
    arc((t) => { const a = 6.2832 * t, ca = Math.cos(a), sa = Math.sin(a); return P(R * ca * cl, R * sa, R * ca * sl); });
  }
  for (let l = 1; l < RINGS; l++) {           // latitudes — parallels (skip the poles)
    const lat = -Math.PI / 2 + Math.PI * l / RINGS, cr = Math.cos(lat) * R, yy = Math.sin(lat) * R;
    arc((t) => { const a = 6.2832 * t; return P(cr * Math.cos(a), yy, cr * Math.sin(a)); });
  }
}

function draw() {
  if (!ctx) return;
  const r = cnv.getBoundingClientRect();
  if (Math.round(r.width) !== view.w || Math.round(r.height) !== view.h) { applySize(r.width, r.height); fitView(); }
  if (alpha > 0) tick();
  view.yaw += AUTO_SPIN;                 // constant very-slow auto-rotate (drag adds on top)
  _frame++;
  projectAll();
  for (const [gi, c] of charge) { c.v *= 0.94; if (c.fresh) { c.fresh = false; spawnPulses(gi, c.color); } if (c.v < 0.02) charge.delete(gi); }

  ctx.globalCompositeOperation = "source-over";
  ctx.fillStyle = PAL.bg; ctx.fillRect(0, 0, view.w, view.h);
  drawSphere();                          // faint wireframe shell behind the cloud

  // focus set (Obsidian hover behaviour): hovered node + its neighbours
  const h = view.hover;
  const focus = h >= 0 ? new Set([h, ...(ADJ[h] || [])]) : null;

  // edges — faint; focus/fire/hover brighten, the rest dims away
  for (const e of LINKS) {
    const a = NODES[e.s], b = NODES[e.t];
    const ca = charge.get(e.s), cb = charge.get(e.t), heat = Math.max(ca ? ca.v : 0, cb ? cb.v : 0);
    const inFocus = focus && (e.s === h || e.t === h);
    ctx.beginPath(); ctx.moveTo(a.sx, a.sy); ctx.lineTo(b.sx, b.sy);
    if (heat > 0.02) { ctx.strokeStyle = rgba((ca || cb).color, 0.3 + 0.6 * heat); ctx.lineWidth = 0.6 + 1.4 * heat; }
    else if (inFocus) { ctx.strokeStyle = rgba(PAL.dim, 0.55); ctx.lineWidth = 0.9; }
    else { ctx.strokeStyle = rgba(PAL.line, focus ? 0.03 : 0.07); ctx.lineWidth = 0.5; }
    ctx.stroke();
  }
  // signal pulses (additive) — interpolate in projected screen space
  ctx.globalCompositeOperation = "lighter";
  for (let k = PULSES.length - 1; k >= 0; k--) {
    const pu = PULSES[k]; pu.t += PULSE_SPEED;
    if (pu.t >= 1) { PULSES.splice(k, 1); continue; }
    const A = NODES[pu.a], B = NODES[pu.b], x = A.sx + (B.sx - A.sx) * pu.t, y = A.sy + (B.sy - A.sy) * pu.t;
    const g = ctx.createRadialGradient(x, y, 0, x, y, 4); g.addColorStop(0, rgba(pu.color, 0.85)); g.addColorStop(1, rgba(pu.color, 0));
    ctx.beginPath(); ctx.arc(x, y, 4, 0, 6.2832); ctx.fillStyle = g; ctx.fill();
  }
  // glow on charged + hovered (additive)
  for (let i = 0; i < NODES.length; i++) {
    const a = NODES[i], c = charge.get(i);
    if (!c && i !== h) continue;
    const col = c ? c.color : PAL.gold, v = c ? c.v : 0.6, gr = (6 + 11 * v) * a.sps;
    const g = ctx.createRadialGradient(a.sx, a.sy, 0, a.sx, a.sy, gr);
    g.addColorStop(0, rgba(col, Math.min(0.9, 0.4 + v))); g.addColorStop(1, rgba(col, 0));
    ctx.beginPath(); ctx.arc(a.sx, a.sy, gr, 0, 6.2832); ctx.fillStyle = g; ctx.fill();
  }
  // breathing glow on the last-touched file — persists after the flare decays, so
  // "where we are" stays visible. Radius + alpha ride a slow sine (the breath).
  if (lastTouched >= 0 && NODES[lastTouched]) {
    const a = NODES[lastTouched], col = lastColor || PAL.gold, breathe = 0.5 + 0.5 * Math.sin(_frame * BREATHE_SPEED);
    const gr = (9 + 8 * breathe) * a.sps;
    const g = ctx.createRadialGradient(a.sx, a.sy, 0, a.sx, a.sy, gr);
    g.addColorStop(0, rgba(col, 0.3 + 0.4 * breathe)); g.addColorStop(1, rgba(col, 0));
    ctx.beginPath(); ctx.arc(a.sx, a.sy, gr, 0, 6.2832); ctx.fillStyle = g; ctx.fill();
  }
  // lightning bolts — energy jumping from the previous file to the new one
  for (let k = BOLTS.length - 1; k >= 0; k--) {
    const bo = BOLTS[k]; bo.t += BOLT_SPEED;
    const A = NODES[bo.a], B = NODES[bo.b];
    if (bo.t >= 1 || !A || !B) { BOLTS.splice(k, 1); continue; }
    drawBolt(A.sx, A.sy, B.sx, B.sy, bo.color, 1 - bo.t);
  }
  // nodes — painted back-to-front so nearer ones sit on top; size + alpha carry depth
  ctx.globalCompositeOperation = "source-over";
  const order = NODES.map((_, i) => i).sort((i, j) => NODES[i].srz - NODES[j].srz);
  for (const i of order) {
    const a = NODES[i], c = charge.get(i), depth = depthOf(a), isLast = i === lastTouched;
    const rad = (1.4 + Math.min(4.5, a.deg * 0.34) + (c ? 1.4 * c.v : 0) + (isLast ? 1.3 : 0)) * a.sps;
    const dimmed = focus && !focus.has(i) && !c && !isLast;
    ctx.beginPath(); ctx.arc(a.sx, a.sy, Math.max(0.5, rad), 0, 6.2832);
    ctx.fillStyle = c ? c.color : isLast ? rgba(lastColor || PAL.gold, 0.95) : rgba(a.color, dimmed ? 0.14 : (0.4 + 0.55 * depth));
    ctx.fill();
  }
  // section labels — one per cluster (skip the tiny ones), drawn faint at the
  // anchor so the blobs read as "jebrim · quest-log", "dev · bank", etc. Dimmed
  // hard while a node is focused so they don't fight the hover labels.
  {
    const cy_ = Math.cos(view.yaw), sy_ = Math.sin(view.yaw), cp_ = Math.cos(view.pitch), sp_ = Math.sin(view.pitch);
    ctx.font = "600 9px ui-monospace, monospace"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    for (const c of CLUSTERS) {
      if (c.n < 5) continue;
      const x1 = c.ax * cy_ + c.az * sy_, z1 = -c.ax * sy_ + c.az * cy_;
      const y2 = c.ay * cp_ - z1 * sp_, z2 = c.ay * sp_ + z1 * cp_;
      const proj = FOCAL / (FOCAL - z2);
      const sx = view.w / 2 + view.tx + x1 * view.scale * proj, sy = view.h / 2 + view.ty + y2 * view.scale * proj;
      const depth = Math.max(0, Math.min(1, z2 / cloudR * 0.5 + 0.5));
      ctx.fillStyle = rgba(PAL.gold, (h >= 0 ? 0.16 : 0.5) * (0.5 + 0.5 * depth));
      ctx.fillText(c.name.replace("·", " · "), sx, sy);
    }
  }
  // label: hovered node always; neighbours + hubs when zoomed in
  ctx.font = "10px ui-monospace, monospace"; ctx.textAlign = "left"; ctx.textBaseline = "middle";
  if (h >= 0 && NODES[h]) {
    ctx.fillStyle = PAL.ink; ctx.fillText(NODES[h].label, NODES[h].sx + 7, NODES[h].sy);
    if (view.scale > 0.9) for (const nb of (ADJ[h] || [])) { const a = NODES[nb]; ctx.fillStyle = rgba(PAL.dim, 0.8); ctx.fillText(a.label, a.sx + 6, a.sy); }
  } else if (view.scale > 1.5) {
    for (const a of NODES) if (a.deg >= 8) { ctx.fillStyle = rgba(PAL.dim, 0.7 * depthOf(a)); ctx.fillText(a.label, a.sx + 6, a.sy); }
  }
}

async function loadGraph() {
  let g; try { g = await (await fetch("./graph.json")).json(); } catch { return; }
  const n = g.nodes.length, R = 13 * Math.cbrt(n);
  // one anchor per section (the per-node `cluster`), spread on a sphere via the
  // golden angle so sections sit apart; nodes seed at their anchor + jitter and
  // the force sim pulls them home (CLUSTER_GRAV), so each section reads as a blob.
  const clNames = [...new Set(g.nodes.map((nd) => nd.cluster || "misc"))];
  const AR = R * 2.3, m = clNames.length;                // anchor-sphere radius (wider = sections more separated)
  CLUSTERS = clNames.map((name, k) => {
    const dy = 1 - (k / Math.max(1, m - 1)) * 2;
    const dr = Math.sqrt(Math.max(0, 1 - dy * dy)), th = k * 2.399963;
    return { name, ax: Math.cos(th) * dr * AR, ay: dy * AR, az: Math.sin(th) * dr * AR, n: 0, grav: CLUSTER_GRAV, seedR: 0.22 * R };
  });
  const clIndex = new Map(CLUSTERS.map((c, k) => [c.name, k]));
  // Count each section first, then size its spread by node count: a BIG section
  // (dev ≈ half the notes) is held LOOSER (lower grav) and SEEDED WIDER so it
  // relaxes into a region instead of packing into one dense blob; a small section
  // keeps the full pull + tight seed and stays a tidy clump. This is the de-blob.
  for (const nd of g.nodes) CLUSTERS[clIndex.get(nd.cluster || "misc")].n++;
  for (const c of CLUSTERS) {
    c.grav = CLUSTER_GRAV * Math.max(0.4, Math.min(1, 9 / Math.sqrt(c.n || 1)));
    c.seedR = 0.22 * R * Math.max(1, Math.min(4.5, Math.sqrt(c.n) / 3.5));
  }
  NODES = g.nodes.map((nd, i) => {
    const ci = clIndex.get(nd.cluster || "misc"), c = CLUSTERS[ci], jr = c.seedR;
    return { gi: i, id: nd.id, label: nd.label, deg: nd.deg, color: nodeColor(nd.group), cl: ci,
      x: c.ax + (Math.random() - 0.5) * jr, y: c.ay + (Math.random() - 0.5) * jr, z: c.az + (Math.random() - 0.5) * jr,
      vx: 0, vy: 0, vz: 0 };
  });
  LINKS = g.links;
  baseByName = new Map(); ADJ = NODES.map(() => []);
  g.nodes.forEach((nd, i) => { const bn = nd.id.split("/").pop().toLowerCase(); if (!baseByName.has(bn)) baseByName.set(bn, []); baseByName.get(bn).push(i); });
  for (const e of LINKS) { ADJ[e.s].push(e.t); ADJ[e.t].push(e.s); }
  PULSES = []; BOLTS = []; lastTouched = -1; lastColor = null; alpha = 1;
  for (let k = 0; k < 170 && alpha > 0.02; k++) tick();
  fitView();
  if (titleEl) titleEl.textContent = `${NODES.length} notes · ${LINKS.length} links`;
}

// ── mount into the feed dock ──
let titleEl, _raf = 0, _poll = 0, _cleanups = [];
export function mountBrain(host) {
  if (!host || host._brainMounted) return () => {};
  host._brainMounted = true;
  host.style.cssText = ["position:relative", "width:100%", "aspect-ratio:1", "flex:none",
    `background:${PAL.bg}`, `border-bottom:1px solid ${PAL.line}`, "overflow:hidden", "font-family:ui-monospace,monospace"].join(";");

  // Real titlebar in the shared header family (.brain-head — styled in styles.css
  // to match topbar/console/feed: grain+gradient bg, gold underline, corner
  // rivets, gold title). Absolutely positioned, so it overlays the top of the
  // force-graph canvas like a panel titlebar.
  const head = document.createElement("div");
  head.className = "brain-head";
  const tag = document.createElement("span"); tag.textContent = "BRAIN";
  titleEl = document.createElement("span"); titleEl.textContent = "loading…"; titleEl.className = "brain-head-sub";
  const spacer = document.createElement("span"); spacer.style.flex = "1";
  const recenter = mkBtn("center", () => { view.tx = 0; view.ty = 0; fitView(); });  // reset pan + zoom-to-fit
  const reheat = mkBtn("re-settle", () => { alpha = 1; });
  head.append(tag, titleEl, spacer, recenter, reheat);

  cnv = document.createElement("canvas");
  cnv.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab";
  ctx = cnv.getContext("2d");
  host.append(cnv, head);

  // LEFT-drag pans the map (tx/ty), RIGHT-drag orbits the camera (yaw/pitch);
  // the auto-spin keeps running on top of either. e.button: 0 = left, 2 = right.
  const onDown = (e) => {
    view.drag = true; view.dragMode = e.button === 2 ? "rotate" : "pan";
    view.mx = e.clientX; view.my = e.clientY; view.downX = e.clientX; view.downY = e.clientY; view.moved = false;
    cnv.style.cursor = view.dragMode === "rotate" ? "grabbing" : "move";
  };
  const onUp = () => {
    // a clean LEFT click (pan that never moved) on a node opens its file popup
    if (view.drag && view.dragMode === "pan" && !view.moved && view.hover >= 0) openNode(NODES[view.hover]);
    view.drag = false; view.dragMode = null; if (cnv) cnv.style.cursor = "grab";
  };
  const onCtx = (e) => e.preventDefault();   // let right-drag rotate without popping the menu
  const onMove = (e) => {
    if (view.drag) {
      const dx = e.clientX - view.mx, dy = e.clientY - view.my;
      if (view.dragMode === "rotate") {
        view.yaw -= dx * 0.006;        // inverted Y-axis rotation (drag-right spins the other way)
        view.pitch = Math.max(-1.35, Math.min(1.35, view.pitch + dy * 0.006));
      } else {
        view.tx += dx; view.ty += dy;
      }
      view.mx = e.clientX; view.my = e.clientY;
      if (Math.hypot(e.clientX - view.downX, e.clientY - view.downY) > 5) view.moved = true;  // a real drag, not a click
      return;
    }
    const rect = cnv.getBoundingClientRect();
    if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) { view.hover = -1; return; }
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    // hit-test against the projected (a.sx/a.sy) coords cached by the last frame
    let best = -1, bd = 11; for (let i = 0; i < NODES.length; i++) { const a = NODES[i]; if (a.sx == null) continue; const d = Math.hypot(a.sx - mx, a.sy - my); if (d < bd) { bd = d; best = i; } }
    view.hover = best;
  };
  const onWheel = (e) => {
    e.preventDefault(); e.stopPropagation();
    // zoom toward the cursor, not the panel centre: keep the point under the mouse
    // fixed by shifting the pan as we scale. screen = centre + pan + world*scale,
    // so for scale*=k the pan must satisfy tx' = (mx-cx)(1-k) + tx*k.
    const rect = cnv.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const prev = view.scale, next = Math.max(0.05, Math.min(12, prev * (e.deltaY < 0 ? 1.12 : 0.89)));
    const k = next / prev;
    view.tx = (mx - view.w / 2) * (1 - k) + view.tx * k;
    view.ty = (my - view.h / 2) * (1 - k) + view.ty * k;
    view.scale = next;
  };
  cnv.addEventListener("pointerdown", onDown);
  window.addEventListener("pointerup", onUp);
  window.addEventListener("pointermove", onMove);
  cnv.addEventListener("wheel", onWheel, { passive: false });
  cnv.addEventListener("contextmenu", onCtx);
  _cleanups = [() => cnv.removeEventListener("pointerdown", onDown), () => window.removeEventListener("pointerup", onUp),
    () => window.removeEventListener("pointermove", onMove), () => cnv.removeEventListener("wheel", onWheel),
    () => cnv.removeEventListener("contextmenu", onCtx)];

  loadGraph();
  poll(); _poll = setInterval(poll, 2000);
  const loop = () => { draw(); _raf = requestAnimationFrame(loop); };
  _raf = requestAnimationFrame(loop);

  return () => { cancelAnimationFrame(_raf); clearInterval(_poll); for (const c of _cleanups) c(); _cleanups = []; closePop();
    host._brainMounted = false; ctx = null; cnv = null; };
}

async function poll() {
  let items; try { items = (await (await fetch("/api/feed")).json()).items || []; } catch { return; }
  if (firstPoll) { for (const it of items) if ((it.ts || 0) > seenMaxTs) seenMaxTs = it.ts; firstPoll = false; return; }
  for (const it of items) if ((it.ts || 0) > seenMaxTs) ingest(it);
  for (const it of items) if ((it.ts || 0) > seenMaxTs) seenMaxTs = it.ts;
}
// ── file popup ── click a node → fetch its file (path-safe /api/file) and show
// it in a themed modal over the whole app. Markdown renders via md.js; anything
// else shows as plain text. Close on ✕, Esc, or backdrop click.
let _pop = null;
function _popKey(e) { if (e.key === "Escape") closePop(); }
function closePop() { if (_pop) { _pop.remove(); _pop = null; document.removeEventListener("keydown", _popKey); } }
async function openNode(node) {
  if (!node || !node.id) return;
  closePop();
  const back = document.createElement("div"); back.className = "brain-pop-back";
  back.innerHTML = `<div class="brain-pop">
      <div class="brain-pop-head">
        <span class="brain-pop-title"></span><span class="brain-pop-path"></span>
        <button class="brain-pop-x" title="close">✕</button>
      </div>
      <div class="brain-pop-body"><div class="brain-pop-msg">loading…</div></div>
    </div>`;
  back.querySelector(".brain-pop-title").textContent = node.label;
  back.querySelector(".brain-pop-path").textContent = node.id;
  const body = back.querySelector(".brain-pop-body");
  back.querySelector(".brain-pop-x").addEventListener("click", closePop);
  back.addEventListener("pointerdown", (e) => { if (e.target === back) closePop(); });
  document.body.append(back);
  _pop = back;
  document.addEventListener("keydown", _popKey);
  try {
    const j = await (await fetch("/api/file?path=" + encodeURIComponent(node.id))).json();
    if (_pop !== back) return;                       // popup was closed/replaced while loading
    if (!j.ok) { body.innerHTML = `<div class="brain-pop-msg">${escHtml(j.error || "unavailable")}</div>`; return; }
    if (/\.md$/i.test(node.id)) body.innerHTML = `<div class="b-text">${mdToHtml(j.text)}</div>`;
    else body.innerHTML = `<pre class="brain-pop-code">${escHtml(j.text)}</pre>`;
    body.scrollTop = 0;
  } catch {
    if (_pop === back) body.innerHTML = `<div class="brain-pop-msg">failed to load</div>`;
  }
}

function mkBtn(label, fn) {
  // OSRS bevelled stud, matching the cockpit's .newbtn/.icon-btn/.release so the
  // brain header's button reads like the others' (release/new/bell).
  const b = document.createElement("button"); b.textContent = label;
  b.style.cssText = ["color:var(--ink)", "background:linear-gradient(#4a3c22,#342a17)",
    "border:1px solid var(--gold-dk)", "border-top-color:color-mix(in srgb, var(--gold) 55%, transparent)",
    "border-radius:4px", "padding:2px 9px", "cursor:pointer",
    "font:600 9px 'RuneScape UF','Trebuchet MS',Verdana,sans-serif", "letter-spacing:.05em",
    "box-shadow:inset 0 1px 0 color-mix(in srgb, var(--gold) 30%, transparent), 0 1px 2px rgba(0,0,0,.5)",
    "text-shadow:0 1px 0 #000", "pointer-events:auto"].join(";");
  b.addEventListener("mouseenter", () => { b.style.filter = "brightness(1.18)"; });
  b.addEventListener("mouseleave", () => { b.style.filter = ""; });
  b.addEventListener("click", fn); return b;
}

export const __test = {
  get NODES() { return NODES; }, get ADJ() { return ADJ; }, get PULSES() { return PULSES; }, get view() { return view; },
  tick, fitView, ingest, extractMd, nodeColor, blendHex, charge: () => charge,
  get alpha() { return alpha; }, set alpha(v) { alpha = v; }, set firstPoll(v) { firstPoll = v; }, set seenMaxTs(v) { seenMaxTs = v; },
};
