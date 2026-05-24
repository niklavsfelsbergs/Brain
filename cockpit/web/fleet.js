// fleet.js — read-only transcript view for sessions the cockpit does NOT drive
// (VS Code sessions, ended/off-board rows). A SessionConn here owns no process:
// it loads the session's on-disk transcript via /history and renders it through
// the Console. Switching away leaves nothing running.
//
// Live, drivable sessions run through the PTY terminal (term.js) — the S066 B
// pivot put interactive claude on the subscription. The old headless `claude -p`
// /chat WS driver (place / openOwned / SessionConn.connect) was removed in S073:
// it was metered post-2026-06-15 AND had become dead code (the client placed and
// resumed every session through the PTY, never through /chat).

let SEQ = 0; // stable client-side view key per conn

class SessionConn {
  constructor(id) {
    this.cid = "c" + ++SEQ; // stable view key
    this.id = id;
    this.drive = false; // peek is always read-only — Console hides the composer
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
  close() {
    /* no process to stop — a peek owns nothing */
  }
}

// Read-only peek (VS Code sessions, ended/off-board rows): transient, no WS,
// transcript loaded from /history.
export function openPeek(id) {
  const c = new SessionConn(id);
  c.model.status = "read-only — running in VS Code";
  c.loadHistory(id);
  return c;
}

// A peek owns no process; release is a no-op kept so main.js's onRelease wiring
// (shared with the drivable PTY path) resolves cleanly.
export function release(_id) {}
