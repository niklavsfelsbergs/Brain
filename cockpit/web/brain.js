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

const cssVar = (n, f) => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || f;
const PAL = {
  bg:   cssVar("--bg", "#17120b"),
  panel:cssVar("--panel", "#2a2114"),
  line: cssVar("--line", "#6e5a2c"),
  ink:  cssVar("--ink", "#f1e7c4"),
  dim:  cssVar("--ink-dim", "#cdb985"),
  faint:cssVar("--ink-faint", "#9d8a5c"),
  gold: cssVar("--gold", "#e3b73c"),
};
// regional hue per group — used MUTED at rest (mostly parchment, a hint of hue)
const GROUP_HUE = {
  jebrim: cssVar("--crew", "#5a9fe0"), zezima: cssVar("--answers", "#ff5d8f"),
  guthix: cssVar("--alching", "#b07ad8"), identity: cssVar("--gold", "#e3b73c"),
  "gielinor-core": cssVar("--wrapped", "#34c0ad"), gielinor: cssVar("--ship", "#46c8d8"),
  dev: cssVar("--ink-faint", "#9d8a5c"), infra: "#7d6f8f",
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
// calm node colour: 35% regional hue + 65% parchment-dim → distinguishable, not loud
const nodeColorCache = {};
const nodeColor = (g) => (nodeColorCache[g] ||= blendHex(GROUP_HUE[g] || PAL.faint, PAL.dim, 0.35));
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
let baseByName = new Map();
let charge = new Map();      // gi -> {v,color,fresh}
let PULSES = [];
let seenMaxTs = 0, firstPoll = true, alpha = 0;
const TRAIL_OFF = true;      // clean hard-clear each frame (Obsidian look, no smear)
const PULSE_SPEED = 0.05, PULSE_CAP = 500, PULSE_PER_FIRE = 8;

// 3D camera: yaw/pitch orbit + a constant very-slow auto-spin. The cloud is
// centred at the origin (gravity holds it there), so there's no pan — drag
// rotates, wheel zooms. Projection is weak-perspective (nearer nodes a touch
// bigger + brighter); per-node screen coords are cached on the node each frame
// by projectAll() so the renderer + hover hit-test read a.sx/a.sy.
const view = { w: 320, h: 320, scale: 1, yaw: 0, pitch: 0.32, drag: false, mx: 0, my: 0, hover: -1 };
const AUTO_SPIN = 0.0010;     // rad/frame — one revolution ≈ 105s at 60fps, very slow
let cloudR = 200, FOCAL = 520; // sphere radius + perspective focal length (set in fitView)

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
    a.sx = cx + x1 * s * proj;
    a.sy = cyc + y2 * s * proj;
  }
}

// ── 3D force sim: repulsion + link springs + center gravity, cooling ──
const REP = 820, SPR = 0.05, L0 = 36, GRAV = 0.02;
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
    a.vx += -a.x * GRAV * alpha; a.vy += -a.y * GRAV * alpha; a.vz += -a.z * GRAV * alpha;
    a.vx *= 0.82; a.vy *= 0.82; a.vz *= 0.82;
    a.x += Math.max(-30, Math.min(30, a.vx)); a.y += Math.max(-30, Math.min(30, a.vy)); a.z += Math.max(-30, Math.min(30, a.vz));
  }
  alpha *= 0.985;
}
function fitView() {
  if (!NODES.length) return;
  let R = 1;
  for (const a of NODES) { const d = Math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z); if (d > R) R = d; }
  cloudR = R; FOCAL = R * 2.6;
  const pad = 34, half = Math.min(view.w, view.h) / 2 - pad;
  const maxProj = FOCAL / (FOCAL - R);     // the nearest possible node, biggest projection
  view.scale = Math.max(0.05, half / (R * maxProj));
}

// ── live firing ──
function extractMd(text) { const out = [], rx = /([\w.\-]+\.md)/g; let m; while ((m = rx.exec(text))) out.push(m[1].toLowerCase()); return out; }
function ingest(it) {
  const kind = it.kind || "action", text = it.text || "", col = fireColor(kind, text);
  for (const name of extractMd(text)) { const hits = baseByName.get(name); if (hits) for (const gi of hits) charge.set(gi, { v: 1, color: col, fresh: true }); }
}
function spawnPulses(gi, color) {
  const ns = ADJ[gi] || [], k = Math.min(ns.length, PULSE_PER_FIRE);
  for (let q = 0; q < k; q++) PULSES.push({ a: gi, b: ns[q], t: 0, color });
  if (PULSES.length > PULSE_CAP) PULSES.splice(0, PULSES.length - PULSE_CAP);
}

// ── render ──
let cnv, ctx, dpr = 1;
function applySize(w, h) {
  view.w = Math.max(1, Math.round(w)); view.h = Math.max(1, Math.round(h));
  dpr = window.devicePixelRatio || 1; cnv.width = view.w * dpr; cnv.height = view.h * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
// depth of a node in [0 far .. 1 near], from its rotated z
const depthOf = (a) => Math.max(0, Math.min(1, a.srz / cloudR * 0.5 + 0.5));
function draw() {
  if (!ctx) return;
  const r = cnv.getBoundingClientRect();
  if (Math.round(r.width) !== view.w || Math.round(r.height) !== view.h) { applySize(r.width, r.height); fitView(); }
  if (alpha > 0) tick();
  view.yaw += AUTO_SPIN;                 // constant very-slow auto-rotate (drag adds on top)
  projectAll();
  for (const [gi, c] of charge) { c.v *= 0.94; if (c.fresh) { c.fresh = false; spawnPulses(gi, c.color); } if (c.v < 0.02) charge.delete(gi); }

  ctx.globalCompositeOperation = "source-over";
  ctx.fillStyle = PAL.bg; ctx.fillRect(0, 0, view.w, view.h);

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
  // nodes — painted back-to-front so nearer ones sit on top; size + alpha carry depth
  ctx.globalCompositeOperation = "source-over";
  const order = NODES.map((_, i) => i).sort((i, j) => NODES[i].srz - NODES[j].srz);
  for (const i of order) {
    const a = NODES[i], c = charge.get(i), depth = depthOf(a);
    const rad = (1.4 + Math.min(4.5, a.deg * 0.34) + (c ? 1.4 * c.v : 0)) * a.sps;
    const dimmed = focus && !focus.has(i) && !c;
    ctx.beginPath(); ctx.arc(a.sx, a.sy, Math.max(0.5, rad), 0, 6.2832);
    ctx.fillStyle = c ? c.color : rgba(a.color, dimmed ? 0.14 : (0.4 + 0.55 * depth));
    ctx.fill();
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
  const R = 13 * Math.cbrt(g.nodes.length), n = g.nodes.length;
  // seed as a filled ball: golden-angle directions (even angular spread) at radii
  // that fill the volume, so the 3D force sim starts from a sphere not a disc.
  NODES = g.nodes.map((nd, i) => {
    const dy = 1 - (i / Math.max(1, n - 1)) * 2;       // 1 .. -1 (latitude)
    const dr = Math.sqrt(Math.max(0, 1 - dy * dy));    // ring radius at that latitude
    const th = i * 2.399963;                            // golden angle (longitude)
    const rr = R * Math.cbrt((i + 0.5) / n);            // fill the ball, not just its shell
    return { gi: i, label: nd.label, deg: nd.deg, color: nodeColor(nd.group),
      x: Math.cos(th) * dr * rr, y: dy * rr, z: Math.sin(th) * dr * rr, vx: 0, vy: 0, vz: 0 };
  });
  LINKS = g.links;
  baseByName = new Map(); ADJ = NODES.map(() => []);
  g.nodes.forEach((nd, i) => { const bn = nd.id.split("/").pop().toLowerCase(); if (!baseByName.has(bn)) baseByName.set(bn, []); baseByName.get(bn).push(i); });
  for (const e of LINKS) { ADJ[e.s].push(e.t); ADJ[e.t].push(e.s); }
  PULSES = []; alpha = 1;
  for (let k = 0; k < 110 && alpha > 0.02; k++) tick();
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
  const reheat = mkBtn("re-settle", () => { alpha = 1; });
  head.append(tag, titleEl, spacer, reheat);

  cnv = document.createElement("canvas");
  cnv.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab";
  ctx = cnv.getContext("2d");
  host.append(cnv, head);

  // drag = orbit the camera (yaw/pitch); the auto-spin keeps running on top
  const onDown = (e) => { view.drag = true; view.mx = e.clientX; view.my = e.clientY; cnv.style.cursor = "grabbing"; };
  const onUp = () => { view.drag = false; if (cnv) cnv.style.cursor = "grab"; };
  const onMove = (e) => {
    if (view.drag) {
      view.yaw += (e.clientX - view.mx) * 0.006;
      view.pitch = Math.max(-1.35, Math.min(1.35, view.pitch + (e.clientY - view.my) * 0.006));
      view.mx = e.clientX; view.my = e.clientY; return;
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
    view.scale = Math.max(0.05, Math.min(12, view.scale * (e.deltaY < 0 ? 1.12 : 0.89)));
  };
  cnv.addEventListener("pointerdown", onDown);
  window.addEventListener("pointerup", onUp);
  window.addEventListener("pointermove", onMove);
  cnv.addEventListener("wheel", onWheel, { passive: false });
  _cleanups = [() => cnv.removeEventListener("pointerdown", onDown), () => window.removeEventListener("pointerup", onUp),
    () => window.removeEventListener("pointermove", onMove), () => cnv.removeEventListener("wheel", onWheel)];

  loadGraph();
  poll(); _poll = setInterval(poll, 2000);
  const loop = () => { draw(); _raf = requestAnimationFrame(loop); };
  _raf = requestAnimationFrame(loop);

  return () => { cancelAnimationFrame(_raf); clearInterval(_poll); for (const c of _cleanups) c(); _cleanups = [];
    host._brainMounted = false; ctx = null; cnv = null; };
}

async function poll() {
  let items; try { items = (await (await fetch("/api/feed")).json()).items || []; } catch { return; }
  if (firstPoll) { for (const it of items) if ((it.ts || 0) > seenMaxTs) seenMaxTs = it.ts; firstPoll = false; return; }
  for (const it of items) if ((it.ts || 0) > seenMaxTs) ingest(it);
  for (const it of items) if ((it.ts || 0) > seenMaxTs) seenMaxTs = it.ts;
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
