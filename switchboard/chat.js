// chat.js — right panel.
//
// Three event streams feed this panel:
//   (a) gielinor/comms/active.md + developer-braindead/comms/active.md mirrors
//       (inter-session coordination — OPEN / UPDATE / CLOSING / dialog posts).
//   (b) chat.ndjson — human-language tool-call summaries written by
//       developer-braindead/.claude/hooks/emit-event.py + status-sidecar.py.
//       One JSON object per line; each carries kind, actor, instance, text, ts.
//   (c) intent-narration changes — embedded in chat.ndjson as kind="intent".
//
// All three render through `appendLogEntry` into the same scrolling div.
// Speaker tab filters, jump-to-latest, and unread badges work uniformly across
// sources because every entry carries a `data-speaker` attribute.

import { formatWall } from './state.js';

const LOG_BOTTOM_THRESHOLD = 12;
const MAX_ENTRIES = 500;
const TAB_SPEAKERS = [
  'jebrim', 'zezima', 'dwarves', 'gnomes', 'penguins',
  'wisp', 'braindead', 'guthix', 'commits',
];

// Module-scope state. Set up by `initChat`; the helpers below capture closures
// over these via the wired setup.
let logEl = null;
let jumpLatestBtn = null;
let jumpLatestCountEl = null;
let logScrollLocked = false;
let logUnreadCount = 0;
const tabUnread = Object.fromEntries(TAB_SPEAKERS.map(s => [s, 0]));
const tabBadges = {};

function isLogAtBottom() {
  return logEl.scrollTop + logEl.clientHeight >= logEl.scrollHeight - LOG_BOTTOM_THRESHOLD;
}

function updateJumpLatestButton() {
  if (!jumpLatestBtn) return;
  if (logScrollLocked && logUnreadCount > 0) {
    jumpLatestCountEl.textContent = `${logUnreadCount} new`;
    jumpLatestBtn.classList.add('visible');
  } else if (logScrollLocked) {
    jumpLatestCountEl.textContent = 'latest';
    jumpLatestBtn.classList.add('visible');
  } else {
    jumpLatestBtn.classList.remove('visible');
  }
}

function scrollLogToLatest() {
  logScrollLocked = false;
  logUnreadCount = 0;
  logEl.scrollTop = logEl.scrollHeight;
  updateJumpLatestButton();
}

function renderTabBadge(speaker) {
  const badge = tabBadges[speaker];
  if (!badge) return;
  const n = tabUnread[speaker];
  badge.textContent = n > 0 ? (n > 99 ? '99+' : String(n)) : '';
  badge.classList.toggle('has-unread', n > 0);
}

function bumpTabUnread(speaker) {
  if (!(speaker in tabUnread)) return;
  const active = logEl.getAttribute('data-filter');
  if (!active || active === speaker) return;
  tabUnread[speaker]++;
  renderTabBadge(speaker);
}

function clearTabUnread(speaker) {
  if (speaker === 'all') {
    for (const k of TAB_SPEAKERS) { tabUnread[k] = 0; renderTabBadge(k); }
  } else if (speaker in tabUnread) {
    tabUnread[speaker] = 0;
    renderTabBadge(speaker);
  }
}

function appendLogEntry(li) {
  logEl.appendChild(li);
  while (logEl.childNodes.length > MAX_ENTRIES) logEl.removeChild(logEl.firstChild);
  bumpTabUnread(li.getAttribute('data-speaker'));
  if (logScrollLocked) {
    logUnreadCount++;
    updateJumpLatestButton();
  } else {
    logEl.scrollTop = logEl.scrollHeight;
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

// D-014: chat-style line with username prefix in actor-colored span.
// Renders as "[time] <user>:</user> <body>" — username picks up per-speaker color.
// `tsInput` lets callers stamp historical entries (chat.ndjson carries `ts`).
function logChatLine(actor, body, cls = '', speaker = 'system', tsInput = null) {
  const li = document.createElement('div');
  li.className = 'log-entry ' + cls;
  li.setAttribute('data-speaker', speaker);
  const tStr = formatWall(tsInput != null ? tsInput : new Date());
  li.innerHTML = `<span class="t">[${tStr}]</span>` +
                 `<span class="user">${escapeHtml(actor)}</span> ${escapeHtml(body)}`;
  appendLogEntry(li);
  return li;
}

// ─── comms feed: parse state-comms-<origin>.md → render headers + bodies ───
const HEADER_RE = /^\[([^\]]+)\]\s+(\S+)\s+(.+)$/;
const HEADER_PREVIEW_CHARS = 90;

function parseHeader(line) {
  const m = HEADER_RE.exec(line);
  if (!m) return null;
  return { ts: m[1], who: m[2], kind: m[3].trim() };
}

// An entry is one header line followed by zero or more 2-space-indented body
// lines, separated from neighbours by a blank line. Anything that isn't a
// recognized header is dropped silently (file headers, quotes, --- rules).
function parseEntries(text) {
  const lines = text.split(/\r?\n/);
  const out = [];
  let cur = null;
  for (const raw of lines) {
    const line = raw.replace(/\s+$/, '');
    if (!line) {
      if (cur) { out.push(cur); cur = null; }
      continue;
    }
    if (cur) {
      if (HEADER_RE.test(line)) {
        out.push(cur);
        const h = parseHeader(line);
        cur = h ? { ...h, body: [] } : null;
      } else {
        cur.body.push(line.replace(/^ {1,4}/, ''));
      }
    } else {
      const h = parseHeader(line);
      if (h) cur = { ...h, body: [] };
    }
  }
  if (cur) out.push(cur);
  return out;
}

function classForKind(kind) {
  if (kind === 'OPEN' || kind === 'SCAFFOLD') return 'comms-open';
  if (kind === 'UPDATE') return 'comms-update';
  if (kind === 'CLOSING' || kind === 'ABANDONED') return 'comms-closing';
  if (kind.startsWith('→') || kind.startsWith('->')) return 'comms-dialog';
  return 'comms-open';
}

function splitWho(who) {
  const m = /^([a-z][a-z0-9_]*)-([a-f0-9]{8})$/i.exec(who);
  if (m) return { actor: m[1].toLowerCase(), sid8: m[2] };
  return { actor: who.toLowerCase(), sid8: '' };
}

function buildHeaderText(entry) {
  if (entry.body.length === 0) return entry.kind;
  const first = entry.body[0];
  const truncated = first.length > HEADER_PREVIEW_CHARS;
  const preview = truncated
    ? first.slice(0, HEADER_PREVIEW_CHARS - 1).trimEnd() + '…'
    : first;
  return `${entry.kind} — ${preview}`;
}

function hasHiddenDetail(entry) {
  if (entry.body.length === 0) return false;
  if (entry.body.length > 1) return true;
  return entry.body[0].length > HEADER_PREVIEW_CHARS;
}

function commsEntryKey(entry) {
  return `${entry.ts}|${entry.who}|${entry.kind}`;
}

function renderCommsEntry(entry) {
  const { actor, sid8 } = splitWho(entry.who);
  const speaker = ['jebrim', 'zezima', 'wisp', 'braindead', 'guthix'].includes(actor) ? actor : 'system';
  const displayName = actor.charAt(0).toUpperCase() + actor.slice(1) + (sid8 ? ` · ${sid8}` : '');
  const headerCls = classForKind(entry.kind);
  const entryId = commsEntryKey(entry);
  const headerEl = logChatLine(displayName, buildHeaderText(entry), headerCls, speaker);
  if (hasHiddenDetail(entry) && headerEl) {
    headerEl.classList.add('comms-toggleable');
    headerEl.setAttribute('data-comms-entry', entryId);
    headerEl.addEventListener('click', () => {
      const open = headerEl.classList.toggle('expanded');
      document.querySelectorAll(
        `.comms-body[data-comms-entry="${CSS.escape(entryId)}"]`
      ).forEach(b => b.classList.toggle('show', open));
    });
    for (const line of entry.body) {
      const li = document.createElement('div');
      li.className = 'log-entry comms-body';
      li.setAttribute('data-speaker', speaker);
      li.setAttribute('data-comms-entry', entryId);
      li.innerHTML = `<span class="t">·</span>${escapeHtml(line)}`;
      appendLogEntry(li);
    }
  }
}

function initCommsFeed() {
  const SOURCES = [
    { url: 'state-comms-gielinor.md',  origin: 'gielinor' },
    { url: 'state-comms-braindead.md', origin: 'braindead' },
  ];
  const POLL_MS = 3000;
  // Track last-rendered headers so we don't re-render after a poll. First load
  // primes the seen-set from the full file then renders only the tail — reload
  // doesn't dump history, only NEW entries render.
  const seen = { gielinor: new Set(), braindead: new Set() };
  const primed = { gielinor: false, braindead: false };

  async function pollOne(src) {
    try {
      const res = await fetch(src.url + '?_=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) return;
      const text = await res.text();
      const entries = parseEntries(text);
      if (!primed[src.origin]) {
        const tail = entries.slice(-6);
        for (const e of entries) seen[src.origin].add(commsEntryKey(e));
        for (const e of tail) renderCommsEntry(e);
        primed[src.origin] = true;
        return;
      }
      for (const e of entries) {
        const k = commsEntryKey(e);
        if (seen[src.origin].has(k)) continue;
        seen[src.origin].add(k);
        renderCommsEntry(e);
      }
    } catch (_) {
      // mirror file may not exist yet — silent retry
    }
  }

  async function pollAll() {
    for (const src of SOURCES) await pollOne(src);
  }
  pollAll();
  setInterval(pollAll, POLL_MS);
}

// ─── chat.ndjson: human-language tool-call + intent stream (S052) ───
//
// Each line is one JSON object. Schema (loose; emitter is the authority):
//   { ts, kind, actor, instance, sid8, text }
//   kind ∈ {"action", "intent", ...} — unknown kinds render as plain chat lines.
//
// Re-poll strategy: re-fetch the whole file every NDJSON_POLL_MS, track how
// many lines we've already rendered, append only the new ones. Cheap because
// the file is short (status-sidecar.py rotates / truncates as it grows).

function chatNdjsonSpeaker(actor) {
  const a = String(actor || '').toLowerCase();
  if (TAB_SPEAKERS.includes(a)) return a;
  return 'system';
}

function renderNdjsonRecord(rec) {
  const actor = rec.actor || 'system';
  const instance = (rec.instance && rec.instance > 1) ? '·' + rec.instance : '';
  const displayName = actor.charAt(0).toUpperCase() + actor.slice(1) + instance;
  const speaker = chatNdjsonSpeaker(actor);
  const text = String(rec.text || '');
  // ts on records is unix-seconds (status-sidecar.py convention). Convert to ms.
  const tsMs = (typeof rec.ts === 'number') ? rec.ts * 1000 : rec.ts;
  let cls = '';
  let body = text;
  if (rec.kind === 'intent') {
    cls = 'intent';
    body = text;
  } else if (rec.kind === 'action') {
    cls = 'action';
    body = text;
  } else if (rec.kind === 'commit') {
    cls = 'commit';
  } else if (rec.kind === 'narrate' || rec.kind === 'system') {
    cls = rec.kind;
  }
  logChatLine(displayName, body, cls, speaker, tsMs);
}

function initChatNdjson() {
  const URL = 'chat.ndjson';
  const POLL_MS = 2000;
  let renderedLines = 0;
  let primed = false;
  let polling = false;

  async function poll() {
    if (polling) return;
    polling = true;
    try {
      const res = await fetch(URL + '?_=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) return;
      const text = await res.text();
      const lines = text.split(/\r?\n/).filter(l => l.length > 0);
      if (!primed) {
        // First load: render only the tail so reload doesn't replay history.
        const TAIL = 20;
        const tailStart = Math.max(0, lines.length - TAIL);
        for (let i = tailStart; i < lines.length; i++) {
          try { renderNdjsonRecord(JSON.parse(lines[i])); } catch (_) { /* skip malformed */ }
        }
        renderedLines = lines.length;
        primed = true;
        return;
      }
      // File may have been truncated/rotated — if shorter, reset the cursor.
      if (lines.length < renderedLines) renderedLines = 0;
      for (let i = renderedLines; i < lines.length; i++) {
        try { renderNdjsonRecord(JSON.parse(lines[i])); } catch (_) { /* skip malformed */ }
      }
      renderedLines = lines.length;
    } catch (_) {
      // file may not exist yet — silent retry
    } finally {
      polling = false;
    }
  }

  poll();
  setInterval(poll, POLL_MS);
}

// ─── public entry ───────────────────────────────────────────────
export function initChat(opts = {}) {
  const live = !!opts.live;

  logEl = document.getElementById('logScroll');
  jumpLatestBtn = document.getElementById('jumpLatest');
  jumpLatestCountEl = document.getElementById('jumpLatestCount');
  if (!logEl) return;

  // I4: per-tab unread counter badges.
  document.querySelectorAll('.log-tab').forEach(tab => {
    const speaker = tab.dataset.tab;
    if (TAB_SPEAKERS.includes(speaker)) {
      const badge = document.createElement('span');
      badge.className = 'tab-count';
      tab.appendChild(badge);
      tabBadges[speaker] = badge;
    }
  });

  // I2: scroll-lock + jump-to-latest pip.
  logEl.addEventListener('scroll', () => {
    const wasLocked = logScrollLocked;
    logScrollLocked = !isLogAtBottom();
    if (wasLocked && !logScrollLocked) logUnreadCount = 0;
    updateJumpLatestButton();
  });
  if (jumpLatestBtn) jumpLatestBtn.addEventListener('click', scrollLogToLatest);

  // Speaker-tab filter.
  document.querySelectorAll('.log-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.log-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const v = tab.dataset.tab;
      if (v === 'all') logEl.removeAttribute('data-filter');
      else logEl.setAttribute('data-filter', v);
      clearTabUnread(v);
    });
  });

  // Live-only: poll comms + chat.ndjson. Static page (no ?live=1) leaves the
  // panel empty — the operator pulls up a frozen surface for inspection.
  if (live) {
    initCommsFeed();
    initChatNdjson();
  }
}
