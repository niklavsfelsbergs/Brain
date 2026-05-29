// brain.js — the brain map. Two levels over the real vault graph
// (cockpit/web/graph.json, exported by cockpit/graph-export.py):
//
//   OVERVIEW  — every cognitive AREA as its own labelled bubble (player × layer:
//               Jebrim·quest-log, Guthix, identity, dev·bank, …). Size = node
//               count. CALM at rest (parchment on dark); a bubble GLOWS in colour
//               only when a note inside it fires — so you read WHERE the brain is
//               working at a glance. Click a bubble to drill in.
//   EXPAND    — that one area's notes as a force graph: nodes + [[links]], neon
//               bloom, signal pulses down synapses, comet trails. "← back" returns.
//
// Colour = activity, not decoration (the fix for "too colourful"); no hull
// polygons (the fix for "too polygonal"). Docked as a square at the top of the
// feed column; sizes its canvas off its real rendered box each frame, so it's
// agnostic to the .app-grid zoom:1.35 it lives under. No deps, no build.

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
// activity colour by feed kind (the ONLY colour at rest is parchment)
function fireColor(kind, text) {
  if (kind === "needs_you") return cssVar("--answers", "#ff5d8f");
  if (kind === "done") return cssVar("--wrapped", "#34c0ad");
  if (kind === "intent" || kind === "comms") return cssVar("--alching", "#b07ad8");
  if (/^Reading\b/i.test(text)) return cssVar("--crew", "#5a9fe0");
  if (/^(Editing|Writing|Creating)\b/i.test(text)) return PAL.gold;
  return PAL.dim;
}
function rgba(hex, a) {
  const h = hex.replace("#", "");
  return `rgba(${parseInt(h.slice(0,2),16)},${parseInt(h.slice(2,4),16)},${parseInt(h.slice(4,6),16)},${a})`;
}

// ── data ──
let RAW = { nodes: [], links: [] };
let clusterOf = [];            // global node idx -> cluster index
let CLUSTERS = [];             // {key,label,idxs,count,x,y,vx,vy,r,charge,color}
let CEDGES = [];               // inter-cluster connectors {a,b,w}
let baseByName = new Map();    // basename -> [global node idx]
let nodeCharge = new Map();    // global node idx -> {v,color,fresh}
let seenMaxTs = 0, firstPoll = true;

const MISC_MIN = 5;            // clusters smaller than this fold into "<area>·misc"
const TRAIL = 0.4, PULSE_SPEED = 0.05, PULSE_CAP = 500, PULSE_PER_FIRE = 8;

// ── view / mode ──
const view = { w: 320, h: 320, scale: 1, tx: 0, ty: 0, mode: "overview",
               drag: false, moved: false, mx: 0, my: 0, downX: 0, downY: 0, hover: -1 };
let SUB = null;                // expand mode: {idxs, pos:[{gi,x,y,vx,vy}], local, edges, adj, alpha, ci}

const projX = (x) => view.w / 2 + view.tx + x * view.scale;
const projY = (y) => view.h / 2 + view.ty + y * view.scale;
const unX = (sx) => (sx - view.w / 2 - view.tx) / view.scale;
const unY = (sy) => (sy - view.h / 2 - view.ty) / view.scale;

// ── generic 2D force tick (used for bubbles and for a cluster's nodes) ──
function force2d(P, E, { rep, l0, spr, grav }, alpha) {
  const n = P.length;
  for (let i = 0; i < n; i++) {
    const a = P[i];
    for (let j = i + 1; j < n; j++) {
      const b = P[j];
      const dx = b.x - a.x, dy = b.y - a.y, d2 = dx * dx + dy * dy || 0.01, d = Math.sqrt(d2);
      const f = (rep * alpha) / d2, ux = dx / d, uy = dy / d;
      a.vx -= ux * f; a.vy -= uy * f; b.vx += ux * f; b.vy += uy * f;
    }
  }
  for (const e of E) {
    const a = P[e.s], b = P[e.t];
    const dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 0.01;
    const f = spr * alpha * (d - l0), ux = dx / d, uy = dy / d;
    a.vx += ux * f; a.vy += uy * f; b.vx -= ux * f; b.vy -= uy * f;
  }
  for (const a of P) {
    a.vx += -a.x * grav * alpha; a.vy += -a.y * grav * alpha;
    a.vx *= 0.82; a.vy *= 0.82;
    a.x += Math.max(-30, Math.min(30, a.vx)); a.y += Math.max(-30, Math.min(30, a.vy));
  }
}

function foldKey(key, count) {
  if (count >= MISC_MIN || !key.includes("·")) return key;
  return key.split("·")[0] + "·misc";
}

function buildClusters() {
  // count raw clusters, fold the singletons, then assign every node a final cluster
  const rawCount = new Map();
  for (const nd of RAW.nodes) rawCount.set(nd.cluster, (rawCount.get(nd.cluster) || 0) + 1);
  const finalKey = (raw) => foldKey(raw, rawCount.get(raw) || 0);

  clusterByKey_idx.clear(); CLUSTERS = []; clusterOf = new Array(RAW.nodes.length);
  RAW.nodes.forEach((nd, gi) => {
    const key = finalKey(nd.cluster);
    let ci = clusterByKey_idx.get(key);
    if (ci === undefined) {
      ci = CLUSTERS.length;
      CLUSTERS.push({ key, label: key, idxs: [], x: 0, y: 0, vx: 0, vy: 0, r: 8, charge: 0, color: PAL.dim });
      clusterByKey_idx.set(key, ci);
    }
    CLUSTERS[ci].idxs.push(gi); clusterOf[gi] = ci;
  });
  for (const c of CLUSTERS) { c.count = c.idxs.length; c.r = 7 + Math.sqrt(c.count) * 3.2; }

  // inter-cluster connectors (aggregate link weights between distinct clusters)
  const w = new Map();
  for (const e of RAW.links) {
    const a = clusterOf[e.s], b = clusterOf[e.t];
    if (a === b) continue;
    const k = a < b ? a + "," + b : b + "," + a;
    w.set(k, (w.get(k) || 0) + 1);
  }
  CEDGES = [...w].map(([k, weight]) => { const [a, b] = k.split(",").map(Number); return { a, b, w: weight }; });
}
const clusterByKey_idx = new Map();

function layoutOverview() {
  const n = CLUSTERS.length || 1, R = 26 * Math.sqrt(n);
  CLUSTERS.forEach((c, i) => { const t = (i / n) * 6.2832 * 4, rr = R * Math.sqrt(i / n);
    c.x = Math.cos(t) * rr; c.y = Math.sin(t) * rr; c.vx = 0; c.vy = 0; });
  const E = CEDGES.map((e) => ({ s: e.a, t: e.b }));
  let a = 1;
  for (let k = 0; k < 260; k++) { force2d(CLUSTERS, E, { rep: 4200, l0: 120, spr: 0.04, grav: 0.02 }, a); a *= 0.99; }
  // collide — push overlapping bubbles apart so labels stay legible
  for (let pass = 0; pass < 60; pass++) for (let i = 0; i < CLUSTERS.length; i++) for (let j = i + 1; j < CLUSTERS.length; j++) {
    const A = CLUSTERS[i], B = CLUSTERS[j], dx = B.x - A.x, dy = B.y - A.y;
    const d = Math.hypot(dx, dy) || 0.01, min = A.r + B.r + 14;
    if (d < min) { const p = (min - d) / 2, ux = dx / d, uy = dy / d; A.x -= ux * p; A.y -= uy * p; B.x += ux * p; B.y += uy * p; }
  }
  fitTo(CLUSTERS.map((c) => ({ x: c.x, y: c.y, r: c.r })));
}

function fitTo(pts) {
  if (!pts.length) return;
  let minx = 1e9, miny = 1e9, maxx = -1e9, maxy = -1e9;
  for (const p of pts) { const r = p.r || 0; minx = Math.min(minx, p.x - r); miny = Math.min(miny, p.y - r); maxx = Math.max(maxx, p.x + r); maxy = Math.max(maxy, p.y + r); }
  const gw = maxx - minx || 1, gh = maxy - miny || 1, pad = 26;
  view.scale = Math.min((view.w - pad) / gw, (view.h - pad) / gh, 3);
  view.tx = -((minx + maxx) / 2) * view.scale; view.ty = -((miny + maxy) / 2) * view.scale;
}

// ── expand a cluster into its node sub-graph ──
function enterExpand(ci) {
  const c = CLUSTERS[ci]; if (!c) return;
  const local = new Map(); c.idxs.forEach((gi, k) => local.set(gi, k));
  const R = 12 * Math.sqrt(c.idxs.length) + 4;
  const pos = c.idxs.map((gi, k) => { const t = k * 2.399; const rr = R * Math.sqrt(k / c.idxs.length);
    return { gi, x: Math.cos(t) * rr, y: Math.sin(t) * rr, vx: 0, vy: 0 }; });
  const edges = [], adj = pos.map(() => []);
  for (const e of RAW.links) { const a = local.get(e.s), b = local.get(e.t);
    if (a !== undefined && b !== undefined) { edges.push({ s: a, t: b }); adj[a].push(b); adj[b].push(a); } }
  SUB = { ci, idxs: c.idxs, pos, local, edges, adj, alpha: 1, pulses: [] };
  for (let k = 0; k < 60 && SUB.alpha > 0.02; k++) { force2d(pos, edges, { rep: 900, l0: 40, spr: 0.06, grav: 0.02 }, SUB.alpha); SUB.alpha *= 0.985; }
  fitTo(pos);
  view.mode = "expand"; view.hover = -1;
  if (titleEl) titleEl.textContent = `${c.label} · ${c.count}`;
  if (backBtn) backBtn.style.display = "inline-block";
}
function exitExpand() {
  SUB = null; view.mode = "overview"; view.hover = -1;
  fitTo(CLUSTERS.map((c) => ({ x: c.x, y: c.y, r: c.r })));
  if (titleEl) titleEl.textContent = `${CLUSTERS.length} areas · ${RAW.nodes.length} notes`;
  if (backBtn) backBtn.style.display = "none";
}

// ── live firing ──
function extractMd(text) { const out = [], rx = /([\w.\-]+\.md)/g; let m; while ((m = rx.exec(text))) out.push(m[1].toLowerCase()); return out; }
function ingest(it) {
  const kind = it.kind || "action", text = it.text || "", col = fireColor(kind, text);
  for (const name of extractMd(text)) {
    const hits = baseByName.get(name); if (!hits) continue;
    for (const gi of hits) {
      nodeCharge.set(gi, { v: 1, color: col, fresh: true });
      const ci = clusterOf[gi]; if (ci != null) { CLUSTERS[ci].charge = 1; CLUSTERS[ci].color = col; }
    }
  }
}

// ── render ──
let cnv, ctx, dpr = 1;
function applySize(w, h) {
  view.w = Math.max(1, Math.round(w)); view.h = Math.max(1, Math.round(h));
  dpr = window.devicePixelRatio || 1; cnv.width = view.w * dpr; cnv.height = view.h * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
function washTrail() { ctx.globalCompositeOperation = "source-over"; ctx.fillStyle = rgba(PAL.bg, TRAIL); ctx.fillRect(0, 0, view.w, view.h); }
function vignette() {
  const vg = ctx.createRadialGradient(view.w/2, view.h/2, Math.min(view.w, view.h)*0.32, view.w/2, view.h/2, Math.max(view.w, view.h)*0.62);
  vg.addColorStop(0, "rgba(0,0,0,0)"); vg.addColorStop(1, rgba(PAL.bg, 0.5));
  ctx.fillStyle = vg; ctx.fillRect(0, 0, view.w, view.h);
}

function draw() {
  if (!ctx) return;
  const r = cnv.getBoundingClientRect();
  if (Math.round(r.width) !== view.w || Math.round(r.height) !== view.h) {
    applySize(r.width, r.height);
    view.mode === "expand" && SUB ? fitTo(SUB.pos) : fitTo(CLUSTERS.map((c) => ({ x: c.x, y: c.y, r: c.r })));
  }
  for (const c of CLUSTERS) c.charge *= 0.97;              // cluster glow always decays
  if (view.mode === "expand" && SUB) drawExpand(); else drawOverview();
}

function drawOverview() {
  washTrail();
  // connectors between areas — faint, thicker where more links cross
  ctx.globalCompositeOperation = "source-over";
  for (const e of CEDGES) {
    const A = CLUSTERS[e.a], B = CLUSTERS[e.b];
    ctx.beginPath(); ctx.moveTo(projX(A.x), projY(A.y)); ctx.lineTo(projX(B.x), projY(B.y));
    ctx.strokeStyle = rgba(PAL.line, 0.05 + Math.min(0.18, e.w * 0.01)); ctx.lineWidth = Math.min(2.4, 0.4 + e.w * 0.12); ctx.stroke();
  }
  // bubbles
  for (let i = 0; i < CLUSTERS.length; i++) {
    const c = CLUSTERS[i], x = projX(c.x), y = projY(c.y), rad = c.r * view.scale, hot = c.charge;
    if (hot > 0.02) {                                       // activity glow (additive)
      ctx.globalCompositeOperation = "lighter";
      const g = ctx.createRadialGradient(x, y, rad * 0.4, x, y, rad + 16 * hot);
      g.addColorStop(0, rgba(c.color, 0.35 * hot)); g.addColorStop(1, rgba(c.color, 0));
      ctx.beginPath(); ctx.arc(x, y, rad + 16 * hot, 0, 6.2832); ctx.fillStyle = g; ctx.fill();
      ctx.globalCompositeOperation = "source-over";
    }
    ctx.beginPath(); ctx.arc(x, y, rad, 0, 6.2832);
    ctx.fillStyle = rgba(PAL.panel, 0.55 + 0.25 * hot);
    ctx.fill();
    ctx.lineWidth = i === view.hover ? 2 : 1;
    ctx.strokeStyle = hot > 0.02 ? rgba(c.color, 0.4 + 0.5 * hot) : rgba(PAL.line, i === view.hover ? 0.9 : 0.55);
    ctx.stroke();
    // label
    ctx.font = (i === view.hover ? "600 " : "") + "10px ui-monospace, monospace";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillStyle = hot > 0.05 ? rgba(c.color, 0.95) : rgba(PAL.dim, i === view.hover ? 1 : 0.8);
    ctx.fillText(c.label, x, y);
  }
  vignette();
}

function drawExpand() {
  if (SUB.alpha > 0.02) { force2d(SUB.pos, SUB.edges, { rep: 900, l0: 40, spr: 0.06, grav: 0.02 }, SUB.alpha); SUB.alpha *= 0.985; }
  // decay node firing; on a fresh fire launch pulses down its local synapses
  for (const [gi, c] of nodeCharge) { c.v *= 0.94;
    if (c.fresh) { c.fresh = false; const li = SUB.local.get(gi); if (li !== undefined) spawnPulses(li, c.color); }
    if (c.v < 0.02) nodeCharge.delete(gi); }

  washTrail();
  const P = SUB.pos;
  // edges — bowed, calm at rest, hot when an endpoint fires
  ctx.globalCompositeOperation = "source-over";
  for (const e of SUB.edges) {
    const a = P[e.s], b = P[e.t], ca = nodeCharge.get(a.gi), cb = nodeCharge.get(b.gi);
    const heat = Math.max(ca ? ca.v : 0, cb ? cb.v : 0);
    const ax = projX(a.x), ay = projY(a.y), bx = projX(b.x), by = projY(b.y);
    const dx = bx - ax, dy = by - ay, len = Math.hypot(dx, dy) || 1;
    ctx.beginPath(); ctx.moveTo(ax, ay);
    ctx.quadraticCurveTo((ax + bx) / 2 + (-dy / len) * len * 0.12, (ay + by) / 2 + (dx / len) * len * 0.12, bx, by);
    if (heat > 0.02) { ctx.strokeStyle = rgba((ca || cb).color, 0.3 + 0.6 * heat); ctx.lineWidth = 0.6 + 1.6 * heat; }
    else { ctx.strokeStyle = rgba(PAL.line, 0.12); ctx.lineWidth = 0.5; }
    ctx.stroke();
  }
  // bloom glow on charged nodes (additive)
  ctx.globalCompositeOperation = "lighter";
  for (const p of P) { const c = nodeCharge.get(p.gi); if (!c) continue;
    const x = projX(p.x), y = projY(p.y), gr = 6 + 11 * c.v;
    const g = ctx.createRadialGradient(x, y, 0, x, y, gr); g.addColorStop(0, rgba(c.color, Math.min(0.9, 0.5 + c.v))); g.addColorStop(1, rgba(c.color, 0));
    ctx.beginPath(); ctx.arc(x, y, gr, 0, 6.2832); ctx.fillStyle = g; ctx.fill(); }
  // pulses
  for (let k = SUB.pulses.length - 1; k >= 0; k--) { const pu = SUB.pulses[k]; pu.t += PULSE_SPEED;
    if (pu.t >= 1) { SUB.pulses.splice(k, 1); continue; }
    const A = P[pu.a], B = P[pu.b], x = projX(A.x + (B.x - A.x) * pu.t), y = projY(A.y + (B.y - A.y) * pu.t);
    const g = ctx.createRadialGradient(x, y, 0, x, y, 4); g.addColorStop(0, rgba(pu.color, 0.9)); g.addColorStop(1, rgba(pu.color, 0));
    ctx.beginPath(); ctx.arc(x, y, 4, 0, 6.2832); ctx.fillStyle = g; ctx.fill(); }
  // node cores — calm parchment at rest, activity colour on fire
  ctx.globalCompositeOperation = "source-over";
  const deg = (li) => SUB.adj[li].length;
  for (let li = 0; li < P.length; li++) { const p = P[li], c = nodeCharge.get(p.gi);
    const rad = (1.6 + Math.min(4.5, deg(li) * 0.5)) * (c ? 1 + 1.2 * c.v : 1);
    ctx.beginPath(); ctx.arc(projX(p.x), projY(p.y), rad, 0, 6.2832);
    ctx.fillStyle = c ? c.color : rgba(PAL.faint, 0.7); ctx.fill(); }
  // hover label
  if (view.hover >= 0 && P[view.hover]) { const p = P[view.hover];
    ctx.font = "10px ui-monospace, monospace"; ctx.textAlign = "left"; ctx.textBaseline = "middle";
    ctx.fillStyle = PAL.ink; ctx.fillText(RAW.nodes[p.gi].label, projX(p.x) + 7, projY(p.y)); }
  vignette();
}
function spawnPulses(li, color) {
  const ns = SUB.adj[li] || [], k = Math.min(ns.length, PULSE_PER_FIRE);
  for (let q = 0; q < k; q++) SUB.pulses.push({ a: li, b: ns[q], t: 0, color });
  if (SUB.pulses.length > PULSE_CAP) SUB.pulses.splice(0, SUB.pulses.length - PULSE_CAP);
}

async function loadGraph() {
  let g; try { g = await (await fetch("./graph.json")).json(); } catch { return; }
  RAW = g;
  baseByName = new Map();
  g.nodes.forEach((nd, i) => { const bn = nd.id.split("/").pop().toLowerCase();
    if (!baseByName.has(bn)) baseByName.set(bn, []); baseByName.get(bn).push(i); });
  buildClusters();
  layoutOverview();
  if (titleEl) titleEl.textContent = `${CLUSTERS.length} areas · ${RAW.nodes.length} notes`;
}

// ── mount into the feed dock ──
let titleEl, backBtn, _raf = 0, _poll = 0, _cleanups = [];
export function mountBrain(host) {
  if (!host || host._brainMounted) return () => {};
  host._brainMounted = true;
  host.style.cssText = ["position:relative", "width:100%", "aspect-ratio:1", "flex:none",
    `background:${rgba(PAL.bg, 0.6)}`, `border-bottom:1px solid ${PAL.line}`, "overflow:hidden", "font-family:ui-monospace,monospace"].join(";");

  const head = document.createElement("div");
  head.style.cssText = ["position:absolute", "top:0", "left:0", "right:0", "z-index:2", "display:flex", "align-items:center", "gap:8px",
    "padding:3px 7px", `color:${PAL.dim}`, "font:600 9px ui-monospace,monospace", "letter-spacing:.07em", "pointer-events:none", "text-shadow:0 1px 3px #000"].join(";");
  const dot = document.createElement("span");
  dot.style.cssText = `width:5px;height:5px;border-radius:50%;background:${PAL.gold};box-shadow:0 0 6px ${PAL.gold}`;
  backBtn = mkBtn("← back", exitExpand); backBtn.style.display = "none";
  const tag = document.createElement("span"); tag.textContent = "BRAIN";
  titleEl = document.createElement("span"); titleEl.textContent = "loading…"; titleEl.style.color = PAL.faint;
  head.append(dot, tag, titleEl, gap(), backBtn);

  cnv = document.createElement("canvas");
  cnv.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab";
  ctx = cnv.getContext("2d");
  host.append(cnv, head);

  const onDown = (e) => { view.drag = true; view.moved = false; view.mx = e.clientX; view.my = e.clientY; view.downX = e.clientX; view.downY = e.clientY; cnv.style.cursor = "grabbing"; };
  const onUp = (e) => {
    cnv.style.cursor = "grab";
    if (view.drag && !view.moved) {           // a click (not a drag)
      if (view.mode === "overview" && view.hover >= 0) enterExpand(view.hover);
    }
    view.drag = false;
  };
  const onMove = (e) => {
    if (view.drag) {
      if (Math.abs(e.clientX - view.downX) + Math.abs(e.clientY - view.downY) > 4) view.moved = true;
      view.tx += e.clientX - view.mx; view.ty += e.clientY - view.my; view.mx = e.clientX; view.my = e.clientY; return;
    }
    const rect = cnv.getBoundingClientRect();
    if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) { view.hover = -1; return; }
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    view.hover = hitTest(mx, my);
    cnv.style.cursor = (view.mode === "overview" && view.hover >= 0) ? "pointer" : "grab";
  };
  const onWheel = (e) => {
    e.preventDefault(); e.stopPropagation();
    const rect = cnv.getBoundingClientRect(), cx = e.clientX - rect.left, cy = e.clientY - rect.top;
    const gx = unX(cx), gy = unY(cy);
    view.scale = Math.max(0.15, Math.min(10, view.scale * (e.deltaY < 0 ? 1.12 : 0.89)));
    view.tx = cx - view.w / 2 - gx * view.scale; view.ty = cy - view.h / 2 - gy * view.scale;
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

function hitTest(mx, my) {
  if (view.mode === "overview") {
    for (let i = 0; i < CLUSTERS.length; i++) { const c = CLUSTERS[i]; if (Math.hypot(projX(c.x) - mx, projY(c.y) - my) <= c.r * view.scale) return i; }
    return -1;
  }
  if (SUB) { let best = -1, bd = 9; for (let li = 0; li < SUB.pos.length; li++) { const p = SUB.pos[li]; const d = Math.hypot(projX(p.x) - mx, projY(p.y) - my); if (d < bd) { bd = d; best = li; } } return best; }
  return -1;
}

async function poll() {
  let items; try { items = (await (await fetch("/api/feed")).json()).items || []; } catch { return; }
  if (firstPoll) { for (const it of items) if ((it.ts || 0) > seenMaxTs) seenMaxTs = it.ts; firstPoll = false; return; }
  for (const it of items) if ((it.ts || 0) > seenMaxTs) ingest(it);
  for (const it of items) if ((it.ts || 0) > seenMaxTs) seenMaxTs = it.ts;
}

function mkBtn(label, fn) {
  const b = document.createElement("button"); b.textContent = label;
  b.style.cssText = [`color:${PAL.dim}`, `background:${rgba(PAL.bg,0.7)}`, `border:1px solid ${PAL.line}`, "border-radius:4px",
    "padding:1px 6px", "cursor:pointer", "font:9px ui-monospace,monospace", "pointer-events:auto"].join(";");
  b.addEventListener("click", fn); return b;
}
function gap() { const s = document.createElement("span"); s.style.flex = "1"; return s; }

// test surface (harmless in browser)
export const __test = {
  get RAW() { return RAW; }, get CLUSTERS() { return CLUSTERS; }, get CEDGES() { return CEDGES; },
  get clusterOf() { return clusterOf; }, get SUB() { return SUB; }, get view() { return view; },
  buildClusters: () => { buildClusters(); }, layoutOverview, enterExpand, exitExpand, ingest, extractMd,
  nodeCharge: () => nodeCharge, foldKey,
  set RAW(v) { RAW = v; }, set firstPoll(v) { firstPoll = v; }, set seenMaxTs(v) { seenMaxTs = v; },
};
