// fleet.js — persistent per-session connections + models, independent of the
// view. A placed/owned session keeps its /chat process alive even when you're
// looking at another row: the cockpit runs a *fleet*, not one session at a time.
//
// The console is a pure subscriber to a SessionConn's model; placing/releasing
// happens here. Owned session ids persist in localStorage so a reload can
// resume them from claude's on-disk transcript.

const OWNED_KEY = "cockpit-owned";
function loadOwned() {
  try {
    return new Set(JSON.parse(localStorage.getItem(OWNED_KEY) || "[]"));
  } catch {
    return new Set();
  }
}
function saveOwned(set) {
  try {
    localStorage.setItem(OWNED_KEY, JSON.stringify([...set]));
  } catch {}
}

const owned = loadOwned();
const byId = new Map(); // sessionId -> live drivable SessionConn
let SEQ = 0; // stable client-side key per conn (id arrives async for fresh)

const RESULT_CAP = 4000;
function resultText(content) {
  let text = "";
  if (typeof content === "string") text = content;
  else if (Array.isArray(content))
    text = content.map((b) => (typeof b === "string" ? b : (b && b.text) || "")).join("\n");
  else if (content && typeof content === "object") text = content.text || JSON.stringify(content);
  if (text.length > RESULT_CAP) text = text.slice(0, RESULT_CAP) + " …(truncated)";
  return text;
}

function applyEvent(model, ev) {
  const t = ev.type;
  if (t === "stream_event") {
    const e = ev.event || {};
    if (e.type === "content_block_delta") {
      const d = e.delta || {};
      if (d.type === "text_delta") model.preview.text += d.text || "";
      else if (d.type === "thinking_delta") model.preview.thinking += d.thinking || d.text || "";
    }
    return;
  }
  if (t === "assistant") {
    const blocks = (ev.message || {}).content || [];
    if (!model.curAsst) {
      model.curAsst = { role: "assistant", blocks: [] };
      model.turns.push(model.curAsst);
    }
    for (const b of blocks) {
      if (b.type === "text" && b.text) model.curAsst.blocks.push({ t: "text", text: b.text });
      else if (b.type === "thinking" && (b.thinking || "").trim())
        model.curAsst.blocks.push({ t: "thinking", text: b.thinking });
      else if (b.type === "tool_use") {
        const tb = { t: "tool", id: b.id, name: b.name || "tool", input: b.input || {}, result: null, isError: false };
        model.curAsst.blocks.push(tb);
        if (tb.id) model.toolIndex[tb.id] = tb;
      }
    }
    model.preview = { text: "", thinking: "" };
    return;
  }
  if (t === "user") {
    const blocks = (ev.message || {}).content || [];
    for (const b of blocks) {
      if (b && b.type === "tool_result") {
        const tb = model.toolIndex[b.tool_use_id];
        if (tb) {
          tb.result = resultText(b.content);
          tb.isError = !!b.is_error;
        }
      }
    }
    return;
  }
  if (t === "result") {
    model.turns.push({ role: "divider", cost: ev.total_cost_usd, ms: ev.duration_ms });
    model.curAsst = null;
    model.busy = false;
    model.preview = { text: "", thinking: "" };
  }
}

class SessionConn {
  constructor(id, drive) {
    this.cid = "c" + ++SEQ; // stable view key
    this.id = id; // null until announced (fresh place)
    this.drive = drive;
    this.seed = null; // first message to auto-send on announce
    this.ws = null;
    this.listeners = new Set();
    this.model = { turns: [], curAsst: null, preview: { text: "", thinking: "" }, toolIndex: {}, busy: false, status: "" };
  }
  subscribe(fn) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }
  _emit() {
    for (const l of this.listeners) l();
  }
  connect(resumeId) {
    const q = resumeId ? `?resume=${resumeId}` : "";
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/chat${q}`);
    this.ws = ws;
    this.model.status = "connecting…";
    this._emit();
    ws.onmessage = (e) => {
      let f;
      try {
        f = JSON.parse(e.data);
      } catch {
        return;
      }
      this._onFrame(f);
    };
    ws.onclose = () => {
      this.model.busy = false;
      if (this.model.status !== "exited") this.model.status = "disconnected";
      this._emit();
    };
    ws.onerror = () => {
      this.model.status = "connection error";
      this._emit();
    };
  }
  _onFrame(f) {
    if (f.t === "session") {
      this.model.status = f.resumed ? "resumed · live" : "live";
      if (!this.id) {
        this.id = f.sessionId;
        byId.set(this.id, this);
        owned.add(this.id);
        saveOwned(owned);
        if (this.seed) {
          this.sendInput(this.seed);
          this.seed = null;
        }
      }
    } else if (f.t === "event") applyEvent(this.model, f.ev);
    else if (f.t === "stderr") this.model.turns.push({ role: "sys", text: f.d });
    else if (f.t === "exit") {
      this.model.busy = false;
      this.model.status = "exited";
    }
    this._emit();
  }
  async loadHistory(id) {
    this.model.status = "loading history…";
    this._emit();
    try {
      const r = await fetch(`/history?session=${id}`);
      const j = await r.json();
      this.model.turns = j.turns || [];
      for (const tn of this.model.turns)
        if (tn.role === "assistant")
          for (const b of tn.blocks) if (b.t === "tool" && b.id) this.model.toolIndex[b.id] = b;
    } catch {
      /* leave empty */
    }
    this._emit();
  }
  sendInput(text) {
    const ws = this.ws;
    if (!ws || ws.readyState !== 1) return false;
    this.model.turns.push({ role: "user", blocks: [{ t: "text", text }] });
    this.model.curAsst = null;
    this.model.preview = { text: "", thinking: "" };
    this.model.busy = true;
    ws.send(JSON.stringify({ type: "input", text }));
    this._emit();
    return true;
  }
  interrupt() {
    const ws = this.ws;
    if (ws && ws.readyState === 1) ws.send(JSON.stringify({ type: "interrupt" }));
  }
  close() {
    if (this.ws) try { this.ws.close(); } catch {}
  }
}

export function isOwned(id) {
  return owned.has(id);
}

// Start a fresh drivable session; `seed` is the first message (auto-sent on
// announce). Returns the conn immediately — its id arrives async.
export function place(seed) {
  const c = new SessionConn(null, true);
  c.seed = seed || null;
  c.connect(null);
  return c;
}

// Drive an existing owned session — reuse a live conn, else resume from disk.
export function openOwned(id) {
  let c = byId.get(id);
  if (c) return c;
  c = new SessionConn(id, true);
  byId.set(id, c);
  c.loadHistory(id).then(() => c.connect(id));
  return c;
}

// Read-only peek (VS Code sessions): transient, no WS, history only.
export function openPeek(id) {
  const c = new SessionConn(id, false);
  c.model.status = "read-only — running in VS Code";
  c.loadHistory(id);
  return c;
}

// Terminate an owned session's process and forget it.
export function release(id) {
  const c = byId.get(id);
  if (c) {
    c.close();
    byId.delete(id);
  }
  owned.delete(id);
  saveOwned(owned);
}
