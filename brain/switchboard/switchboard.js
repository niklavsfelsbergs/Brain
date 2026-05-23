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

function buildRow(record, thisSid8) {
  const state = deriveSessionState(record);
  const row = document.createElement('div');
  row.className = 'sb-row';
  row.dataset.state = state;
  row.dataset.sid8 = record.sid8 || '';
  if (thisSid8 && record.sid8 === thisSid8) row.classList.add('sb-this');

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

  // Click → focus that terminal pane. Shift-click copies sid8 instead.
  row.addEventListener('click', (ev) => {
    if (!record.sid8) return;
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
  const ordered = sortSessions(sessions);
  if (!ordered.length) {
    const empty = document.createElement('div');
    empty.className = 'sb-empty';
    empty.textContent = 'no sessions found';
    listEl.appendChild(empty);
    countEl.textContent = '0';
    return;
  }
  let live = 0, waiting = 0;
  for (const r of ordered) {
    const s = deriveSessionState(r);
    if (s !== 'ended') live++;
    if (s === 'waiting_for_user') waiting++;
  }
  countEl.textContent = waiting > 0
    ? `${live} live · ${waiting} waiting`
    : `${live} live`;
  for (const r of ordered) listEl.appendChild(buildRow(r, thisSid8));
}

export function initSwitchboard(opts = {}) {
  const listEl = document.getElementById('sbList');
  const countEl = document.getElementById('sbCount');
  if (!listEl || !countEl) return;

  const thisSid8 = opts.sid8 || '';

  let cached = [];
  let polling = false;
  async function pollSwitchboard() {
    if (polling) return;
    polling = true;
    try {
      const res = await fetch('state-switchboard.json?_=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) return;
      const j = await res.json();
      cached = (j && Array.isArray(j.sessions)) ? j.sessions : [];
      renderInto(listEl, countEl, cached, thisSid8);
    } catch (_) {
      // file may not exist yet — silent retry next tick
    } finally {
      polling = false;
    }
  }

  pollSwitchboard();
  setInterval(pollSwitchboard, POLL_MS);
  // Re-render every second so ages tick without re-fetching.
  setInterval(() => { if (cached.length) renderInto(listEl, countEl, cached, thisSid8); }, 1000);
}
