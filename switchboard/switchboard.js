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
import { activityBuckets } from './activity.js';

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
  waiting_for_user: 0, working: 1, closing: 2, idle: 3, ended: 4, unknown: 5,
};
const STATE_LABEL = {
  waiting_for_user: 'WAITING', working: 'WORKING', closing: 'CLOSING',
  idle: 'IDLE', ended: 'ENDED', unknown: '?',
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
  who.textContent = actorLabel(record);
  const sid = document.createElement('span');
  sid.className = 'sb-sid';
  sid.textContent = record.sid8 || '';
  who.appendChild(sid);
  const custom = record.sid8 ? getNames()[record.sid8] : '';
  if (custom) {
    const label = document.createElement('span');
    label.className = 'sb-label';
    label.textContent = custom;
    who.appendChild(label);
  }
  // Double-click the name to rename (inline edit → localStorage).
  if (record.sid8) {
    who.title = 'double-click to rename';
    who.addEventListener('dblclick', (ev) => {
      ev.stopPropagation();
      editing = true;
      const input = document.createElement('input');
      input.className = 'sb-rename-input';
      input.value = getNames()[record.sid8] || '';
      input.placeholder = 'name this session…';
      who.textContent = '';
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
    });
  }
  row.appendChild(who);

  const stateChip = document.createElement('div');
  stateChip.className = 'sb-state';
  stateChip.textContent = STATE_LABEL[state] || state;
  row.appendChild(stateChip);

  const age = document.createElement('div');
  age.className = 'sb-age';
  age.textContent = formatAge(sbAgeSec(record));
  row.appendChild(age);

  // S052: subtitle replaces the old intent / latest-action lines. One
  // human-language line composed server-side (status-sidecar.py) — up to 100
  // chars. Strip BOM defensively in case the upstream writer left one.
  const subtitle = document.createElement('div');
  subtitle.className = 'sb-intent';
  const subtitleText = (record.subtitle || '').replace(/^﻿/, '');
  subtitle.textContent = subtitleText || '—';
  row.appendChild(subtitle);

  // Per-session activity sparkline (row 3) — cadence over the last few minutes.
  const spark = document.createElement('div');
  spark.className = 'sb-spark';
  renderSpark(spark, record.sid8);
  row.appendChild(spark);

  // Two-way link: hovering a row flashes that session's chat lines.
  row.addEventListener('mouseenter', () => {
    document.dispatchEvent(new CustomEvent('sb-hover', { detail: { sid8: record.sid8 } }));
  });
  row.addEventListener('mouseleave', () => {
    document.dispatchEvent(new CustomEvent('sb-hover', { detail: { sid8: null } }));
  });

  // Click → focus that terminal pane. Shift-click copies sid8 instead.
  row.addEventListener('click', (ev) => {
    if (!record.sid8 || editing || ev.detail > 1) return;   // ignore dbl-click's 2nd click
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

  const thisSid8 = opts.sid8 || '';

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
      if (!editing) renderInto(listEl, countEl, cached, thisSid8);
    } catch (_) {
      // file may not exist yet — silent retry next tick
    } finally {
      polling = false;
    }
  }

  pollSwitchboard();
  setInterval(pollSwitchboard, POLL_MS);
  // Re-render every second so ages tick without re-fetching. Paused mid-rename.
  setInterval(() => { if (cached.length && !editing) renderInto(listEl, countEl, cached, thisSid8); }, 1000);
}
