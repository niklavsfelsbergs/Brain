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

import { formatWall, formatMinute, humanizeAction } from './state.js';
import { recordEvent } from './activity.js';

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
// S053 declutter state:
let lastMinuteLabel = null;     // last "HH:MM" rendered by the time-rail
let lastStreamSpeaker = null;   // last speaker in the action/intent run
let searchQuery = '';           // live chat search (lowercased)

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
  // Keep a live search consistent as new entries stream in.
  if (searchQuery && li.classList.contains('log-entry')) {
    li.classList.toggle('search-hide', !li.textContent.toLowerCase().includes(searchQuery));
  }
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

// Insert a faint "── HH:MM ──" rail whenever the wall-clock minute changes, so
// individual lines can drop their per-line timestamp. Huge declutter on the
// action stream where a dozen lines used to each carry [HH:MM:SS].
function maybeTimeRail(tsInput) {
  const label = formatMinute(tsInput != null ? tsInput : new Date());
  if (!label || label === lastMinuteLabel) return;
  lastMinuteLabel = label;
  const rail = document.createElement('div');
  rail.className = 'time-rail';
  rail.innerHTML = `<span>${label}</span>`;
  appendLogEntry(rail);
}

// D-014 + S053: chat-style line. `opts.stream` marks the action/intent stream
// that participates in speaker-run collapsing — a run of one speaker shows the
// name once, continuations indent under a tinted rule and drop the timestamp.
// `opts.bodyHtml` injects pre-built markup (action glyphs); else `body` is
// escaped. `opts.sid8` tags the row so switchboard hover can flash it.
function logChatLine(actor, body, cls = '', speaker = 'system', tsInput = null, opts = {}) {
  maybeTimeRail(tsInput);
  const stream = opts.stream === true;
  const continuation = stream && speaker === lastStreamSpeaker;

  const li = document.createElement('div');
  li.className = 'log-entry ' + cls + (continuation ? ' cont' : '');
  li.setAttribute('data-speaker', speaker);
  if (opts.sid8) li.setAttribute('data-sid8', opts.sid8);

  const bodyHtml = opts.bodyHtml != null ? opts.bodyHtml : escapeHtml(body);
  if (continuation) {
    li.innerHTML = `<span class="cont-gutter"></span>${bodyHtml}`;
  } else {
    const tStr = formatWall(tsInput != null ? tsInput : new Date());
    li.innerHTML = `<span class="t">[${tStr}]</span>` +
                   `<span class="user">${escapeHtml(actor)}</span> ${bodyHtml}`;
  }
  appendLogEntry(li);
  lastStreamSpeaker = stream ? speaker : null;
  return li;
}

// S053: commits render as OSRS-style "drop" banners — a milestone, not a chat
// murmur. Always breaks a speaker-run and carries data-commit for the COMMITS
// tab (which filters on the flag, cross-actor).
function logCommitBanner(actor, detail, speaker, tsInput, sid8) {
  maybeTimeRail(tsInput);
  const li = document.createElement('div');
  li.className = 'log-entry commit-drop';
  li.setAttribute('data-speaker', speaker);
  li.setAttribute('data-commit', '1');
  if (sid8) li.setAttribute('data-sid8', sid8);
  li.innerHTML =
    `<span class="cd-spark">✦</span>` +
    `<span class="cd-label">COMMIT</span>` +
    `<span class="cd-actor">${escapeHtml(actor)}</span>` +
    `<span class="cd-detail">${escapeHtml(detail || 'changes')}</span>`;
  appendLogEntry(li);
  bumpTabUnread('commits');
  lastStreamSpeaker = null;
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
  const sid8 = rec.sid8 || '';

  // Feed the per-session sparkline (switchboard reads activity.js back).
  recordEvent(sid8, tsMs);

  if (rec.kind === 'action') {
    const a = humanizeAction(text);
    if (a.isCommit) {
      logCommitBanner(displayName, a.body, speaker, tsMs, sid8);
      return;
    }
    const bodyHtml =
      `<span class="act-glyph ${a.cls}">${escapeHtml(a.glyph)}</span>` +
      `<span class="act-body">${escapeHtml(a.body)}</span>`;
    logChatLine(displayName, a.body, 'action ' + a.cls, speaker, tsMs,
                { stream: true, bodyHtml, sid8 });
    return;
  }
  if (rec.kind === 'intent') {
    logChatLine(displayName, text, 'intent', speaker, tsMs, { stream: true, sid8 });
    return;
  }
  if (rec.kind === 'commit') {
    logCommitBanner(displayName, text, speaker, tsMs, sid8);
    return;
  }
  const cls = (rec.kind === 'narrate' || rec.kind === 'system') ? rec.kind : '';
  logChatLine(displayName, text, cls, speaker, tsMs, { sid8 });
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

  // S053: live chat search — slim header input filters entries by text.
  const searchEl = document.getElementById('logSearch');
  if (searchEl) {
    const applySearch = () => {
      searchQuery = searchEl.value.trim().toLowerCase();
      logEl.classList.toggle('searching', !!searchQuery);
      logEl.querySelectorAll('.log-entry').forEach(el => {
        el.classList.toggle('search-hide',
          !!searchQuery && !el.textContent.toLowerCase().includes(searchQuery));
      });
    };
    searchEl.addEventListener('input', applySearch);
    // "/" focuses search from anywhere; Esc clears + blurs.
    document.addEventListener('keydown', (e) => {
      const tag = (document.activeElement && document.activeElement.tagName) || '';
      if (e.key === '/' && document.activeElement !== searchEl && !/^(INPUT|TEXTAREA)$/.test(tag)) {
        e.preventDefault();
        searchEl.focus();
      } else if (e.key === 'Escape' && document.activeElement === searchEl) {
        searchEl.value = '';
        applySearch();
        searchEl.blur();
      }
    });
  }

  // S053: two-way actor link — switchboard hover dispatches `sb-hover`; flash
  // the matching session's chat lines (by sid8). Empty detail clears.
  document.addEventListener('sb-hover', (e) => {
    logEl.querySelectorAll('.log-entry.actor-flash').forEach(el => el.classList.remove('actor-flash'));
    const sid8 = e.detail && e.detail.sid8;
    if (!sid8) return;
    logEl.querySelectorAll(`.log-entry[data-sid8="${CSS.escape(sid8)}"]`)
      .forEach(el => el.classList.add('actor-flash'));
  });

  // Live-only: poll comms + chat.ndjson. Static page (no ?live=1) leaves the
  // panel empty — the operator pulls up a frozen surface for inspection.
  if (live) {
    initCommsFeed();
    initChatNdjson();
  }
}
