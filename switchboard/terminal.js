// terminal.js — embedded agent chat panel (S060, slice 3).
//
// The third switchboard panel. Each rail pill is a conversation with a headless
// `claude` driven over the stream-json protocol (see server.py /chat). Instead
// of a terminal grid it renders a real chat: user bubbles, streaming assistant
// text, tool-call cards, and a plain input box. No xterm, no CDN dependency.
//
// The server mints each session's id and announces it, so a pill knows its
// sid8 — letting a switchboard row click jump to its conversation (via focus.js).

import { registerInAppFocus } from './focus.js';

let seq = 0;
let activeId = null;
const convos = [];   // see makeConvo() for shape

let panelEl, stackEl, railEl, toggleEl;

export function initTerminal() {
  panelEl = document.getElementById('terminalbox');
  stackEl = document.getElementById('termStack');
  railEl = document.getElementById('termTabs');
  toggleEl = document.getElementById('termToggle');
  const newBtn = document.getElementById('termNew');
  if (!panelEl || !stackEl || !railEl || !toggleEl) return;

  toggleEl.addEventListener('click', () => togglePanel());
  if (newBtn) newBtn.addEventListener('click', () => spawnConvo());
  registerInAppFocus(focusBySid8);
}

function setPanelOpen(open) {
  panelEl.classList.toggle('open', open);
  document.body.classList.toggle('term-open', open);
  toggleEl.classList.toggle('on', open);
}

function togglePanel() {
  const open = !panelEl.classList.contains('open');
  setPanelOpen(open);
  if (open && convos.length === 0) spawnConvo();
}

// ─── conversation lifecycle ────────────────────────────────────────────────

function spawnConvo() {
  setPanelOpen(true);
  const id = ++seq;

  // pane: scrollable message list + input bar
  const pane = document.createElement('div');
  pane.className = 'term-pane chat-pane';
  pane.dataset.id = String(id);
  const msgs = document.createElement('div');
  msgs.className = 'chat-msgs';
  const bar = document.createElement('div');
  bar.className = 'chat-input';
  const ta = document.createElement('textarea');
  ta.rows = 1;
  ta.placeholder = 'type a message…  (Enter to send · Shift+Enter for newline)';
  ta.spellcheck = false;
  const send = document.createElement('button');
  send.type = 'button';
  send.className = 'chat-send';
  send.textContent = 'Send';
  bar.append(ta, send);
  pane.append(msgs, bar);
  stackEl.appendChild(pane);

  // rail pill
  const tab = document.createElement('div');
  tab.className = 'term-tab';
  tab.dataset.id = String(id);
  const dot = document.createElement('span');
  dot.className = 'tt-dot';
  const label = document.createElement('span');
  label.className = 'tt-label';
  label.textContent = 'starting…';
  const close = document.createElement('button');
  close.className = 'tt-close';
  close.type = 'button';
  close.textContent = '×';
  close.title = 'End this session';
  tab.append(dot, label, close);
  railEl.appendChild(tab);

  const c = makeConvo(id, { pane, msgs, ta, send, tab, dot, label });
  convos.push(c);

  tab.addEventListener('click', (e) => { if (e.target !== close) activate(id); });
  close.addEventListener('click', (e) => { e.stopPropagation(); closeConvo(id); });
  send.addEventListener('click', () => submit(c));
  ta.addEventListener('input', () => autosize(ta));
  ta.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(c); }
  });

  activate(id);
  connect(c);
}

function makeConvo(id, els) {
  return {
    id, sid8: null, sessionId: null, ws: null,
    ...els,
    cur: null,            // current assistant message: { bubble, body, raw, streamed }
    tools: new Map(),     // tool_use_id → { card, bodyEl }
    thinkingEl: null,
    ended: false,
  };
}

function connect(c) {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${proto}://${location.host}/chat`);
  c.ws = ws;
  setDot(c, 'connecting');
  ws.onopen = () => setDot(c, 'live');
  ws.onmessage = (e) => {
    let m;
    try { m = JSON.parse(e.data); } catch { return; }
    if (m.t === 'session') {
      c.sid8 = m.sid8; c.sessionId = m.sessionId;
      c.label.textContent = m.sid8;
      c.tab.title = m.sessionId || m.sid8;
    } else if (m.t === 'event') {
      handleEvent(c, m.ev);
    } else if (m.t === 'stderr') {
      systemLine(c, m.d, true);
    } else if (m.t === 'exit') {
      c.ended = true;
      setDot(c, 'closed');
      systemLine(c, 'session ended');
      c.ta.disabled = true; c.send.disabled = true;
    }
  };
  ws.onclose = () => { if (!c.ended) setDot(c, 'closed'); };
  ws.onerror = () => setDot(c, 'err');
}

function submit(c) {
  const text = c.ta.value.trim();
  if (!text || !c.ws || c.ws.readyState !== 1) return;
  addUserBubble(c, text);
  c.ws.send(JSON.stringify({ type: 'input', text }));
  c.ta.value = '';
  autosize(c.ta);
  showThinking(c);
}

// ─── claude stream-json event handling ──────────────────────────────────────

function handleEvent(c, ev) {
  switch (ev.type) {
    case 'system':
      if (ev.subtype === 'status' && ev.status === 'requesting') showThinking(c);
      break;
    case 'stream_event': {
      const e = ev.event || {};
      if (e.type === 'message_start') { startAssistant(c); hideThinking(c); }
      else if (e.type === 'content_block_start' && e.content_block?.type === 'tool_use') {
        upsertToolCard(c, e.content_block);
      } else if (e.type === 'content_block_delta') {
        const d = e.delta || {};
        if (d.type === 'text_delta') { startAssistant(c); appendAssistantText(c, d.text); }
      } else if (e.type === 'message_stop') {
        c.cur = null;
      }
      break;
    }
    case 'assistant':
      for (const block of (ev.message?.content || [])) {
        if (block.type === 'text') {
          startAssistant(c);
          if (!c.cur.streamed) setAssistantText(c, block.text);
        } else if (block.type === 'tool_use') {
          upsertToolCard(c, block);
        }
      }
      break;
    case 'user':
      for (const block of (ev.message?.content || [])) {
        if (block.type === 'tool_result') {
          setToolResult(c, block.tool_use_id, block.content, block.is_error);
        }
      }
      break;
    case 'result':
      hideThinking(c);
      c.cur = null;
      resultDivider(c, ev);
      break;
    default:
      break;   // rate_limit_event, etc.
  }
}

// ─── rendering ──────────────────────────────────────────────────────────────

function addUserBubble(c, text) {
  const wrap = el('div', 'msg msg-user');
  wrap.append(el('div', 'msg-who', 'you'));
  const body = el('div', 'msg-body');
  body.innerHTML = renderMarkdown(text);
  wrap.append(body);
  c.msgs.appendChild(wrap);
  scroll(c);
}

function startAssistant(c) {
  if (c.cur) return;
  const wrap = el('div', 'msg msg-asst');
  wrap.append(el('div', 'msg-who', 'claude'));
  const body = el('div', 'msg-body');
  wrap.append(body);
  c.msgs.appendChild(wrap);
  c.cur = { bubble: wrap, body, raw: '', streamed: false };
  scroll(c);
}

function appendAssistantText(c, delta) {
  if (!c.cur) return;
  c.cur.streamed = true;
  c.cur.raw += delta;
  c.cur.body.innerHTML = renderMarkdown(c.cur.raw);
  scroll(c);
}

function setAssistantText(c, full) {
  if (!c.cur) return;
  c.cur.raw = full;
  c.cur.body.innerHTML = renderMarkdown(full);
  scroll(c);
}

function upsertToolCard(c, block) {
  const id = block.id;
  let entry = c.tools.get(id);
  const inputStr = summarizeInput(block.input);
  if (!entry) {
    const card = el('div', 'tool-card');
    const head = el('div', 'tool-head');
    head.append(el('span', 'tool-glyph', '⚙'));
    head.append(el('span', 'tool-name', block.name || 'tool'));
    const inp = el('span', 'tool-input');
    head.append(inp);
    const result = el('div', 'tool-result');
    result.style.display = 'none';
    card.append(head, result);
    // place inside the current assistant bubble if open, else loose
    (c.cur ? c.cur.bubble : c.msgs).appendChild(card);
    entry = { card, inpEl: inp, resultEl: result };
    c.tools.set(id, entry);
  }
  if (inputStr) entry.inpEl.textContent = inputStr;
  scroll(c);
}

function setToolResult(c, id, content, isError) {
  const entry = c.tools.get(id);
  if (!entry) return;
  const text = toolResultText(content);
  entry.resultEl.textContent = text.length > 600 ? text.slice(0, 600) + ' …' : text;
  entry.resultEl.style.display = '';
  entry.card.classList.toggle('is-error', !!isError);
  scroll(c);
}

function resultDivider(c, ev) {
  const cost = typeof ev.total_cost_usd === 'number' ? `$${ev.total_cost_usd.toFixed(3)}` : '';
  const dur = typeof ev.duration_ms === 'number' ? `${(ev.duration_ms / 1000).toFixed(1)}s` : '';
  const bits = [dur, cost].filter(Boolean).join(' · ');
  const d = el('div', 'turn-end', bits || 'done');
  if (ev.is_error) d.classList.add('is-error');
  c.msgs.appendChild(d);
  scroll(c);
}

function showThinking(c) {
  if (c.thinkingEl) return;
  const t = el('div', 'msg msg-asst thinking');
  t.append(el('div', 'msg-who', 'claude'));
  t.append(el('div', 'msg-body', '•••'));
  c.msgs.appendChild(t);
  c.thinkingEl = t;
  scroll(c);
}

function hideThinking(c) {
  if (c.thinkingEl) { c.thinkingEl.remove(); c.thinkingEl = null; }
}

function systemLine(c, text, isErr) {
  const d = el('div', 'sys-line' + (isErr ? ' is-error' : ''), text);
  c.msgs.appendChild(d);
  scroll(c);
}

// ─── tab / panel plumbing ───────────────────────────────────────────────────

function activate(id) {
  activeId = id;
  for (const t of convos) {
    const on = t.id === id;
    t.pane.classList.toggle('show', on);
    t.tab.classList.toggle('active', on);
  }
  const c = byId(id);
  if (c) setTimeout(() => c.ta && c.ta.focus(), 30);
}

function closeConvo(id) {
  const c = byId(id);
  if (!c) return;
  try { if (c.ws) c.ws.close(); } catch { /* ignore */ }
  c.pane.remove();
  c.tab.remove();
  const i = convos.indexOf(c);
  if (i >= 0) convos.splice(i, 1);
  if (activeId === id) {
    const next = convos[convos.length - 1];
    if (next) activate(next.id);
    else { activeId = null; setPanelOpen(false); }
  }
}

function focusBySid8(sid8) {
  if (!sid8) return false;
  const c = convos.find((t) => t.sid8 === sid8);
  if (!c) return false;
  setPanelOpen(true);
  activate(c.id);
  return true;
}

// ─── helpers ────────────────────────────────────────────────────────────────

function byId(id) { return convos.find((t) => t.id === id); }
function setDot(c, state) { if (c.dot) c.dot.dataset.state = state; }
function scroll(c) { c.msgs.scrollTop = c.msgs.scrollHeight; }

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

function autosize(ta) {
  ta.style.height = 'auto';
  ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
}

function summarizeInput(input) {
  if (!input || typeof input !== 'object') return '';
  // favour the most informative single field
  for (const k of ['command', 'file_path', 'path', 'pattern', 'query', 'url', 'description', 'prompt']) {
    if (input[k]) return String(input[k]).replace(/\s+/g, ' ').slice(0, 140);
  }
  const keys = Object.keys(input);
  return keys.length ? `{ ${keys.slice(0, 4).join(', ')} }` : '';
}

function toolResultText(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content.map((b) => (typeof b === 'string' ? b : (b && b.text) || '')).join('\n');
  }
  if (content && content.text) return content.text;
  return content == null ? '' : JSON.stringify(content);
}

// Small, conservative markdown → HTML. Escapes first (defensive even on
// localhost), then code fences, inline code, bold, and links. Newlines → <br>.
function renderMarkdown(src) {
  const parts = String(src).split('```');
  let html = '';
  for (let i = 0; i < parts.length; i++) {
    if (i % 2 === 1) {
      let block = parts[i];
      const nl = block.indexOf('\n');
      if (nl >= 0) block = block.slice(nl + 1);   // drop the ```lang line
      html += '<pre class="md-pre"><code>' + esc(block.replace(/\n$/, '')) + '</code></pre>';
    } else {
      html += inlineMd(parts[i]);
    }
  }
  return html;
}

function inlineMd(t) {
  t = esc(t);
  t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  t = t.replace(/\n/g, '<br>');
  return t;
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
