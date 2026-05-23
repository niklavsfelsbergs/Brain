// switchboard.js — left panel.
//
// Polls state-switchboard.json (written by status-sidecar.py on every
// turn-bracketing hook event) and renders one row per live Claude Code
// session. Click a row to focus the matching VS Code terminal pane.
//
// Row layout (top to bottom):
//   line 1: dot + actor name + state chip + age
//   line 2: subtitle (≤100 chars, human-language summary) — from record.subtitle
//
// The subtitle source swap (S052): pre-S052 this row showed intent text or
// latest-action; now status-sidecar.py composes a single `subtitle` field per
// session record and we render that. Falls back to empty string when absent.

import { sbAgeSec, deriveSessionState } from './state.js';
import { dispatchFocus, copySid8 } from './focus.js';
import { activityBuckets, latestAction } from './activity.js';
import { getSetting } from './settings.js';

// Actors shown in the roster legend (fills the dead space below the rows and
// teaches the color language the chat panel uses). Keyed to the --<actor>-dot
// CSS vars via the .lg-<actor> swatch classes in styles.css.
const LEGEND_ACTORS = [
  'jebrim', 'zezima', 'braindead', 'guthix',
  'wisp', 'dwarves', 'gnomes', 'penguins',
];

const SPARK_BUCKETS = 16;

// ─── Session rename (localStorage, keyed by sid8) ───
// The server is GET-only, so labels live in the browser. Keyed by sid8 so a
// label rides with that specific session (distinguishes parallel same-actor
// sessions). Falls back to Actor·N when no label is set.
const NAMES_KEY = 'sb-session-names';
let editing = false;            // pause re-render while a row is being renamed
let requestRender = () => {};   // wired by initSwitchboard

function getNames() {
  try { return JSON.parse(localStorage.getItem(NAMES_KEY) || '{}'); }
  catch (_) { return {}; }
}
function setSessionName(sid8, label) {
  const names = getNames();
  if (label) names[sid8] = label; else delete names[sid8];
  try { localStorage.setItem(NAMES_KEY, JSON.stringify(names)); } catch (_) {}
}

// Draw a per-session activity sparkline from the shared activity store: one bar
// per time-bucket over the last few minutes, scaled to the busiest bucket.
function renderSpark(el, sid8) {
  const buckets = activityBuckets(sid8, SPARK_BUCKETS);
  const max = Math.max(1, ...buckets);
  el.textContent = '';
  let any = false;
  for (const v of buckets) {
    const bar = document.createElement('span');
    bar.className = 'sb-bar' + (v ? ' on' : '');
    bar.style.height = (v ? (16 + Math.round((v / max) * 84)) : 0) + '%';
    el.appendChild(bar);
    if (v) any = true;
  }
  el.classList.toggle('sb-spark-quiet', !any);
}

function buildLegend(container) {
  if (!container) return;
  container.textContent = '';
  const key = document.createElement('div');
  key.className = 'sb-legend-key';
  for (const a of LEGEND_ACTORS) {
    const item = document.createElement('span');
    item.className = 'lg-item';
    item.innerHTML = `<span class="lg-swatch lg-${a}"></span>` +
                     a.charAt(0).toUpperCase() + a.slice(1);
    key.appendChild(item);
  }
  container.appendChild(key);
  const caption = document.createElement('div');
  caption.className = 'sb-legend-caption';
  caption.id = 'sbLegendCaption';
  container.appendChild(caption);
}

const POLL_MS = 2000;

const STATE_RANK = {
  waiting_for_user: 0, working: 1, alching: 2, waiting_for_subagents: 3,
  closing: 4, idle: 5, wrapped_up: 6, ended: 7, unknown: 8,
};
const STATE_LABEL = {
  waiting_for_user: 'WAITING', working: 'WORKING', alching: 'ALCHING',
  waiting_for_subagents: 'AWAITING CREW', closing: 'CLOSING',
  idle: 'IDLE', wrapped_up: 'WRAPPED UP', ended: 'ENDED', unknown: '?',
};

function formatAge(sec) {
  sec = Math.floor(sec);
  if (sec < 60) return sec + 's';
  if (sec < 3600) return Math.floor(sec / 60) + 'm';
  return Math.floor(sec / 3600) + 'h';
}

// Sort: waiting_for_user first (most urgent), then working, then closing,
// then idle, then ended. Within a state, newest activity first.
function sortSessions(sessions) {
  return sessions.slice().sort((a, b) => {
    const sa = deriveSessionState(a), sb = deriveSessionState(b);
    const ra = STATE_RANK[sa] ?? 9, rb = STATE_RANK[sb] ?? 9;
    if (ra !== rb) return ra - rb;
    return (b.last_event_ts || 0) - (a.last_event_ts || 0);
  });
}

function actorLabel(record) {
  const name = (record.actor || 'unknown');
  if (!name || name === 'unknown') return 'Pending...';
  const cap = name.charAt(0).toUpperCase() + name.slice(1);
  const inst = (record.instance && record.instance > 1) ? '·' + record.instance : '';
  return cap + inst;
}

// Render the row's name cell. A custom name (set via rename) BECOMES the
// prominent label; the original actor drops to a small "· Zezima" hint so the
// session stays identifiable. sid8 trails as the unique key.
function fillWho(who, record) {
  who.textContent = '';
  const base = actorLabel(record);
  const custom = record.sid8 ? (getNames()[record.sid8] || '') : '';
  who.classList.toggle('renamed', !!custom);

  const name = document.createElement('span');
  name.className = 'sb-name';
  name.textContent = custom || base;
  who.appendChild(name);

  if (custom) {
    const orig = document.createElement('span');
    orig.className = 'sb-orig';
    orig.textContent = base;
    who.appendChild(orig);
  }
  const sid = document.createElement('span');
  sid.className = 'sb-sid';
  sid.textContent = record.sid8 || '';
  who.appendChild(sid);
}

// Open the inline rename editor for a row's name cell. Triggered by the ✎
// button (single click) — sets `editing` synchronously so the poll/age-ticker
// re-render pauses before it can rebuild the row out from under the input.
function startRename(who, record) {
  if (!record.sid8) return;
  editing = true;
  const input = document.createElement('input');
  input.className = 'sb-rename-input';
  input.value = getNames()[record.sid8] || '';
  input.placeholder = 'rename this session…';
  who.textContent = '';
  who.classList.remove('renamed');
  who.appendChild(input);
  input.focus();
  input.select();
  const finish = (save) => {
    if (save) setSessionName(record.sid8, input.value.trim());
    editing = false;
    requestRender();
  };
  input.addEventListener('click', (e) => e.stopPropagation());
  input.addEventListener('keydown', (e) => {
    e.stopPropagation();
    if (e.key === 'Enter') finish(true);
    else if (e.key === 'Escape') finish(false);
  });
  input.addEventListener('blur', () => finish(true));
}

// ─── Sound on WAITING (toggle lives in the COMMS bar; flag via settings.js) ───
let audioCtx = null;
let prevWaiting = new Set();
let chimePrimed = false;          // skip the first poll so we don't chime on load

function ensureAudio() {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
  } catch (_) { /* WebAudio unavailable */ }
  return audioCtx;
}

function playChime() {
  const ctx = ensureAudio();
  if (!ctx) return;
  const now = ctx.currentTime;
  // soft rising two-note ping — present but not startling
  for (const [freq, delay] of [[784, 0], [1175, 0.13]]) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = freq;
    osc.connect(gain); gain.connect(ctx.destination);
    gain.gain.setValueAtTime(0.0001, now + delay);
    gain.gain.exponentialRampToValueAtTime(0.14, now + delay + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + delay + 0.4);
    osc.start(now + delay);
    osc.stop(now + delay + 0.45);
  }
}

// Chime once when any session newly enters WAITING (edge-triggered per sid8).
function chimeForWaiting(sessions) {
  const nowWaiting = new Set();
  for (const r of sessions) {
    if (r.sid8 && deriveSessionState(r) === 'waiting_for_user') nowWaiting.add(r.sid8);
  }
  if (chimePrimed && getSetting('sound')) {
    for (const sid of nowWaiting) {
      if (!prevWaiting.has(sid)) { playChime(); break; }   // one ping per poll
    }
  }
  prevWaiting = nowWaiting;
  chimePrimed = true;
}

function buildRow(record, thisSid8, heroSid8) {
  const state = deriveSessionState(record);
  const row = document.createElement('div');
  row.className = 'sb-row';
  row.dataset.state = state;
  row.dataset.sid8 = record.sid8 || '';
  if (thisSid8 && record.sid8 === thisSid8) row.classList.add('sb-this');
  if (heroSid8 && record.sid8 === heroSid8) row.classList.add('sb-hero');

  const dot = document.createElement('div');
  dot.className = 'sb-dot';
  row.appendChild(dot);

  const who = document.createElement('div');
  who.className = 'sb-who';
  fillWho(who, record);
  row.appendChild(who);

  const stateChip = document.createElement('div');
  stateChip.className = 'sb-state';
  stateChip.textContent = STATE_LABEL[state] || state;
  row.appendChild(stateChip);

  const age = document.createElement('div');
  age.className = 'sb-age';
  age.textContent = formatAge(sbAgeSec(record));
  row.appendChild(age);

  // S061: opening message (row 2). The session's first user prompt, captured
  // once by status-sidecar.py — a stable human handle for tracking, shown even
  // while the actor is still "Pending..." (no intent narrated yet). Hidden when
  // absent so old records (pre-S061) don't leave an empty gap.
  const firstPrompt = document.createElement('div');
  firstPrompt.className = 'sb-firstprompt';
  const fp = (record.first_prompt || '').replace(/^﻿/, '').trim();
  if (fp) firstPrompt.textContent = '“' + fp + '”';
  else firstPrompt.style.display = 'none';
  row.appendChild(firstPrompt);

  // S061: current action (row 3) — a live, ≤80-char heartbeat. Prefer the
  // client-side store (fed by the chat panel every 2s, so it ticks even during
  // a long lone-session turn) → hook-stamped latest_action (first-paint
  // fallback) → the composed subtitle. Strip BOM defensively.
  const subtitle = document.createElement('div');
  subtitle.className = 'sb-intent';
  let actionText = (latestAction(record.sid8)
                    || record.latest_action
                    || record.subtitle
                    || '').replace(/^﻿/, '').trim();
  if (actionText.length > 80) actionText = actionText.slice(0, 79) + '…';
  subtitle.textContent = actionText || '—';
  row.appendChild(subtitle);

  // Per-session activity sparkline (row 3) — cadence over the last few minutes.
  const spark = document.createElement('div');
  spark.className = 'sb-spark';
  renderSpark(spark, record.sid8);
  row.appendChild(spark);

  // S056: rename button (✎). Single click opens the inline rename — replaced the
  // double-click, which raced the per-second re-render. stopPropagation so the
  // row's focus-click doesn't also fire.
  if (record.sid8) {
    const edit = document.createElement('button');
    edit.type = 'button';
    edit.className = 'sb-edit';
    edit.textContent = '✎';
    edit.title = 'rename this session';
    edit.addEventListener('click', (ev) => {
      ev.stopPropagation();
      startRename(who, record);
    });
    row.appendChild(edit);
  }

  // Two-way link: hovering a row flashes that session's chat lines.
  row.addEventListener('mouseenter', () => {
    document.dispatchEvent(new CustomEvent('sb-hover', { detail: { sid8: record.sid8 } }));
  });
  row.addEventListener('mouseleave', () => {
    document.dispatchEvent(new CustomEvent('sb-hover', { detail: { sid8: null } }));
  });

  // Click → focus that terminal pane. Shift-click copies sid8 instead. (Rename
  // is the ✎ button now, so the row click can focus immediately — no dbl-click.)
  row.addEventListener('click', (ev) => {
    if (!record.sid8 || editing) return;
    if (ev.shiftKey) {
      copySid8(record.sid8).then((ok) => {
        if (ok) {
          row.style.outline = '2px solid #ffcb46';
          setTimeout(() => { row.style.outline = ''; }, 350);
        }
      });
      return;
    }
    row.style.outline = '2px solid #2e7a2e';
    setTimeout(() => { row.style.outline = ''; }, 350);
    dispatchFocus(record.sid8);
  });
  row.title = `${record.session_id || record.sid8}\n` +
              `project: ${record.project_dir || '?'}\n` +
              `state: ${state}\n` +
              `click → focus terminal pane\n` +
              `shift-click → copy sid8`;
  return row;
}

function renderInto(listEl, countEl, sessions, thisSid8) {
  listEl.innerHTML = '';
  const caption = document.getElementById('sbLegendCaption');
  if (!sessions.length) {
    const empty = document.createElement('div');
    empty.className = 'sb-empty';
    empty.textContent = 'no sessions found';
    listEl.appendChild(empty);
    countEl.textContent = '0';
    if (caption) caption.textContent = 'awaiting sessions…';
    return;
  }
  const ordered = sortSessions(sessions);
  let live = 0, waiting = 0, heroSid8 = null;
  for (const r of ordered) {
    const s = deriveSessionState(r);
    if (s !== 'ended') live++;
    if (s === 'waiting_for_user') { waiting++; if (!heroSid8) heroSid8 = r.sid8; }
  }
  countEl.textContent = waiting > 0
    ? `${live} live · ${waiting} waiting`
    : `${live} live`;
  if (caption) {
    caption.textContent = `${ordered.length} session${ordered.length === 1 ? '' : 's'} tracked` +
      (waiting > 0 ? ` · ${waiting} need${waiting === 1 ? 's' : ''} you` : '');
  }
  for (const r of ordered) listEl.appendChild(buildRow(r, thisSid8, heroSid8));
}

export function initSwitchboard(opts = {}) {
  const listEl = document.getElementById('sbList');
  const countEl = document.getElementById('sbCount');
  if (!listEl || !countEl) return;

  buildLegend(document.getElementById('sbLegend'));

  // Browsers gate WebAudio behind a user gesture — unlock on first interaction
  // so the WAITING chime can fire later from the poll loop.
  document.addEventListener('pointerdown', ensureAudio, { once: true });

  const thisSid8 = opts.sid8 || '';

  // Pause re-rendering while the pointer is over the list. The board rebuilds
  // every row once a second (age ticker); without this, a double-click to rename
  // straddles a rebuild — the 2nd click lands on a freshly-created element and no
  // dblclick fires (the "top row won't rename" bug). Hovering freezes the DOM so
  // any interaction (rename, selection) is stable; updates resume on mouseleave.
  let hovering = false;
  listEl.addEventListener('mouseenter', () => { hovering = true; });
  listEl.addEventListener('mouseleave', () => { hovering = false; });
  const renderPaused = () => editing || hovering;

  let cached = [];
  let polling = false;
  requestRender = () => renderInto(listEl, countEl, cached, thisSid8);
  async function pollSwitchboard() {
    if (polling) return;
    polling = true;
    try {
      const res = await fetch('state-switchboard.json?_=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) return;
      const j = await res.json();
      cached = (j && Array.isArray(j.sessions)) ? j.sessions : [];
      chimeForWaiting(cached);
      if (!renderPaused()) renderInto(listEl, countEl, cached, thisSid8);
    } catch (_) {
      // file may not exist yet — silent retry next tick
    } finally {
      polling = false;
    }
  }

  pollSwitchboard();
  setInterval(pollSwitchboard, POLL_MS);
  // Re-render every second so ages tick without re-fetching. Paused mid-rename
  // and while hovering (so interactions don't race the rebuild).
  setInterval(() => { if (cached.length && !renderPaused()) renderInto(listEl, countEl, cached, thisSid8); }, 1000);
}
