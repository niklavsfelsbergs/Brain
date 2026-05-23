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
import { recordEvent, recordAction } from './activity.js';
import { getSetting, setSetting } from './settings.js';

const LOG_BOTTOM_THRESHOLD = 12;
const MAX_ENTRIES = 500;

// S056: chat is filtered by category channel, not per-actor. Each channel is a
// mute toggle in the OSRS bottom bar — muting hides those entries (via a class
// on the scroll, CSS does the rest) and arriving traffic flashes the button.
const CHANNELS = ['players', 'subagents', 'braindead', 'guthix', 'commits'];
const SPEAKER_CHANNEL = {
  jebrim: 'players', zezima: 'players', wisp: 'players',
  dwarves: 'subagents', gnomes: 'subagents', penguins: 'subagents',
  braindead: 'braindead', guthix: 'guthix',
};
function entryChannel(speaker, isCommit) {
  if (isCommit) return 'commits';
  return SPEAKER_CHANNEL[speaker] || null;   // system / unknown → always shown
}

// Module-scope state. Set up by `initChat`; the helpers below capture closures
// over these via the wired setup.
let logEl = null;
let jumpLatestBtn = null;
let jumpLatestCountEl = null;
let logScrollLocked = false;
let logUnreadCount = 0;
const chanUnread = Object.fromEntries(CHANNELS.map(c => [c, 0]));
// S053 declutter state:
let lastMsgTs = null;           // ts (ms) of the last rendered message — gap drives the rail
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

function renderChannelFlash(channel) {
  const btn = document.querySelector(`.cb-chan[data-chan="${channel}"]`);
  if (btn) btn.classList.toggle('has-unread', chanUnread[channel] > 0);
}

// Bump unread only for a channel that's currently muted (its traffic is hidden);
// the button flashes so the operator knows something arrived behind the mute.
function bumpChannelUnread(channel) {
  if (!channel || !(channel in chanUnread)) return;
  if (getSetting(channel)) return;     // visible → nothing unread
  chanUnread[channel]++;
  renderChannelFlash(channel);
}

function clearChannelUnread(channel) {
  if (channel in chanUnread) { chanUnread[channel] = 0; renderChannelFlash(channel); }
}
function clearAllUnread() { for (const c of CHANNELS) clearChannelUnread(c); }

function appendLogEntry(li) {
  logEl.appendChild(li);
  while (logEl.childNodes.length > MAX_ENTRIES) logEl.removeChild(logEl.firstChild);
  bumpChannelUnread(entryChannel(li.getAttribute('data-speaker'), li.hasAttribute('data-commit')));
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

// Time-rail policy (S056): NOT a per-minute clock. A "── HH:MM ──" divider is
// inserted only when a message arrives after a real lull (≥ RAIL_GAP_MS of
// silence) — an active conversation shows none; a rail marks "picked back up at
// HH:MM". Driven by the gap since the last message, not by the minute ticking.
const RAIL_GAP_MS = 3 * 60 * 1000;
function tsToMs(tsInput) {
  if (tsInput == null) return Date.now();
  if (typeof tsInput === 'number') return tsInput;
  const d = Date.parse(tsInput);
  return isNaN(d) ? Date.now() : d;
}
function maybeTimeRail(tsInput) {
  const tsMs = tsToMs(tsInput);
  const gap = (lastMsgTs == null) ? Infinity : (tsMs - lastMsgTs);
  lastMsgTs = tsMs;
  if (gap < RAIL_GAP_MS) return;        // messages still flowing — no rail
  const label = formatMinute(tsMs);
  if (!label) return;
  const last = logEl && logEl.lastElementChild;
  if (last && last.classList.contains('time-rail')) last.remove();
  const rail = document.createElement('div');
  rail.className = 'time-rail';
  rail.innerHTML = `<span>${label}</span>`;
  appendLogEntry(rail);
  // After a lull, re-show the next line's speaker name (run no longer continuous).
  lastStreamSpeaker = null;
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
    li.innerHTML = `<span class="cont-gutter"></span><span class="body">${bodyHtml}</span>`;
  } else {
    // No per-line timestamp (S056). Name + body are separate flex columns so a
    // wrapped body line aligns under the body text, never under the username.
    li.innerHTML = `<span class="user">${escapeHtml(actor)}</span><span class="body">${bodyHtml}</span>`;
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
  appendLogEntry(li);   // appendLogEntry bumps the commits channel via data-commit
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

// S056: comms `kind` → a compact colored pill instead of inline "OPEN — ".
const KIND_META = {
  OPEN:      { cls: 'pill-open',   label: 'OPEN' },
  SCAFFOLD:  { cls: 'pill-open',   label: 'OPEN' },
  UPDATE:    { cls: 'pill-update', label: 'UPDATE' },
  CLOSING:   { cls: 'pill-done',   label: 'DONE' },
  ABANDONED: { cls: 'pill-done',   label: 'GONE' },
};
function kindPill(kind) {
  if (kind.startsWith('→') || kind.startsWith('->')) {
    const m = /(?:→|->)\s*@?(\S+)/.exec(kind);
    const target = (m ? m[1] : '').replace(/^[a-z]+-/i, '');  // braindead-e433ac17 → e433ac17
    return { cls: 'pill-dialog', label: '↪', target };
  }
  const meta = KIND_META[kind] || { cls: 'pill-open', label: kind };
  return { cls: meta.cls, label: meta.label, target: '' };
}
// Trim hook/comms filler + the @actor-sid8 mention tokens (the hex means
// nothing to a human reader) so each line reads as one tight clause.
function cleanLine(s) {
  return String(s == null ? '' : s)
    .replace(/(?:→|->)?\s*@?[a-z][a-z0-9_]*-[0-9a-f]{8}\b/gi, '')   // → @braindead-e433ac17
    .replace(/^(Completed|Shipped|Done):?\s+/i, '')
    .replace(/\s{2,}/g, ' ')
    .replace(/^[\s—–:-]+/, '')                                      // tidy leftover leading dashes
    .trim();
}

// Render comms text as HTML with the machine detail de-emphasized: backtick
// `code` spans + inline file/line refs (foo.css, ~L301) render dimmed monospace
// so the human-prose reads through them (S056). Input is plain text; output HTML.
function renderCommsText(s) {
  return String(s == null ? '' : s).split(/(`[^`]+`)/g).map(part => {
    if (part.length > 1 && part.startsWith('`') && part.endsWith('`')) {
      return `<span class="code-ref">${escapeHtml(part.slice(1, -1))}</span>`;
    }
    // Escaped first; the patterns below only match plain word/dot/dash/tilde
    // runs (no HTML metachars), so wrapping them in a span stays safe.
    return escapeHtml(part).replace(
      /(~?[A-Za-z0-9_-]+\.(?:css|js|py|md|json|ts|html|txt)\b|~L\d+(?:-\d+)?)/g,
      '<span class="code-ref">$1</span>'
    );
  }).join('');
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
  const displayName = actor.charAt(0).toUpperCase() + actor.slice(1);   // sid8 demoted to hover (S056)
  const headerCls = classForKind(entry.kind);
  const pill = kindPill(entry.kind);

  // Pill + the whole message as one block (all body lines joined). Collapsed to
  // 2 lines by default; a clear chevron expands it. The ↪ pill alone signals a
  // dialog; the sid8 target is dropped (hex is meaningless to a human).
  const full = entry.body.map(cleanLine).filter(Boolean).join('  ');
  let bodyHtml = `<span class="kind-pill ${pill.cls}">${escapeHtml(pill.label)}</span>`;
  if (full) bodyHtml += `<span class="comms-preview">${renderCommsText(full)}</span>`;

  const headerEl = logChatLine(displayName, '', headerCls, speaker, null, { bodyHtml });
  if (!headerEl) return;
  if (sid8) headerEl.title = `${actor}-${sid8}`;

  // Clamp to 2 lines; only offer the toggle when the message actually overflows
  // (measured). Short entries (the new gist-first discipline) show in full.
  const bodyEl = headerEl.querySelector('.body');
  headerEl.classList.add('comms-collapsed');
  if (bodyEl && bodyEl.scrollHeight > bodyEl.clientHeight + 2) {
    const toggle = document.createElement('span');
    toggle.className = 'comms-toggle';
    toggle.textContent = '⌄';
    toggle.title = 'show full message';
    headerEl.appendChild(toggle);
    headerEl.style.cursor = 'pointer';
    headerEl.addEventListener('click', () => {
      const open = headerEl.classList.toggle('comms-expanded');
      headerEl.classList.toggle('comms-collapsed', !open);
      toggle.textContent = open ? '⌃' : '⌄';
    });
  } else {
    headerEl.classList.remove('comms-collapsed');
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

// Valid data-speaker values (drive the per-actor tints/bullets in styles.css).
const SPEAKERS = new Set([...Object.keys(SPEAKER_CHANNEL), 'commits']);

function chatNdjsonSpeaker(actor) {
  const a = String(actor || '').toLowerCase();
  if (SPEAKERS.has(a)) return a;
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
    recordAction(sid8, a.body, tsMs);   // S061: feed the switchboard's live action line
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

// ─── OSRS bottom bar: channel mutes + settings toggles (S056) ───
//
// Channels are visibility mutes (multi-select), not a single-select filter —
// you can watch Players + Braindead while muting Sub-agent noise. Mute state +
// the Actions/Sound toggles persist via settings.js. "All" un-mutes everything;
// "Clear" wipes the visible log (it refills from the next poll).

function applyBar() {
  // Per-channel visibility classes on the scroll; CSS hides the muted entries.
  for (const c of CHANNELS) logEl.classList.toggle('mute-' + c, !getSetting(c));
  logEl.classList.toggle('hide-actions', !getSetting('actions'));

  document.querySelectorAll('.cb-chan').forEach(btn => {
    const c = btn.dataset.chan;
    const on = !!getSetting(c);
    btn.classList.toggle('off', !on);
    const st = btn.querySelector('.cb-state');
    if (st) st.textContent = on ? 'On' : 'Off';
    if (on) clearChannelUnread(c);     // showing again → drop the flash
  });
  document.querySelectorAll('.cb-toggle').forEach(btn => {
    const on = !!getSetting(btn.dataset.set);
    btn.classList.toggle('off', !on);
    const st = btn.querySelector('.cb-state');
    if (st) st.textContent = on ? 'On' : 'Off';
  });
  const allBtn = document.querySelector('.cb-all');
  if (allBtn) allBtn.classList.toggle('active', CHANNELS.every(c => getSetting(c)));
}

function initChatBar() {
  document.querySelectorAll('.cb-chan').forEach(btn => {
    btn.addEventListener('click', () => {
      const c = btn.dataset.chan;
      setSetting(c, !getSetting(c));
      applyBar();
    });
  });
  document.querySelectorAll('.cb-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const k = btn.dataset.set;
      setSetting(k, !getSetting(k));
      applyBar();
    });
  });
  const allBtn = document.querySelector('.cb-all');
  if (allBtn) allBtn.addEventListener('click', () => {
    for (const c of CHANNELS) setSetting(c, true);
    clearAllUnread();
    applyBar();
  });
  const clearBtn = document.querySelector('.cb-report');
  if (clearBtn) clearBtn.addEventListener('click', () => {
    logEl.innerHTML = '';
    lastMsgTs = null;
    lastStreamSpeaker = null;
  });
  applyBar();   // reflect persisted settings on first paint
}

// ─── public entry ───────────────────────────────────────────────
export function initChat(opts = {}) {
  const live = !!opts.live;

  logEl = document.getElementById('logScroll');
  jumpLatestBtn = document.getElementById('jumpLatest');
  jumpLatestCountEl = document.getElementById('jumpLatestCount');
  if (!logEl) return;

  // S056: wire the OSRS bottom bar (channel mutes + settings toggles).
  initChatBar();

  // I2: scroll-lock + jump-to-latest pip.
  logEl.addEventListener('scroll', () => {
    const wasLocked = logScrollLocked;
    logScrollLocked = !isLogAtBottom();
    if (wasLocked && !logScrollLocked) logUnreadCount = 0;
    updateJumpLatestButton();
  });
  if (jumpLatestBtn) jumpLatestBtn.addEventListener('click', scrollLogToLatest);

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
