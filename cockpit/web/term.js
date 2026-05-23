// term.js — the embedded real-terminal view (S066 B). Runs interactive `claude`
// in a PTY via the backend /pty bridge and renders it with xterm.js. This is the
// subscription-billed path (no headless `claude -p`); a real TTY also gives Esc
// and AskUserQuestion/ExitPlanMode for free.
//
// Like fleet.js's SessionConn, a TermConn lives independent of the view: its
// xterm + WebSocket stay alive when you switch to another row, so the cockpit
// runs a *fleet* of terminals. The Preact <Term/> just re-parents the live
// xterm element on mount. Styling is inline to stay off the shared styles.css.

import { useEffect, useRef } from "preact/hooks";
import { html } from "htm/preact";
import { setName } from "./names.js";

// xterm + fit addon are UMD globals from web/vendor/*, loaded in index.html.
const XTerm = window.Terminal;
const FitAddonNS = window.FitAddon;

const live = new Map(); // cid  -> TermConn
const bySid8 = new Map(); // sid8 -> TermConn
let SEQ = 0;

// Owned session uuids persist so a reopened cockpit can resume them from disk
// (claude --resume) instead of starting fresh. release()/close() forgets one.
const OWNED = "cockpit-owned-terms";
function loadOwned() {
  try {
    return JSON.parse(localStorage.getItem(OWNED) || "[]");
  } catch {
    return [];
  }
}
function saveOwned(arr) {
  try {
    localStorage.setItem(OWNED, JSON.stringify([...new Set(arr)]));
  } catch {}
}
function addOwned(uuid) {
  if (!uuid) return;
  const a = loadOwned();
  if (!a.includes(uuid)) saveOwned([...a, uuid]);
}
function removeOwned(uuid) {
  saveOwned(loadOwned().filter((x) => x !== uuid));
}

class TermConn {
  constructor(opts = {}) {
    this.kind = "term"; // lets main.js tell us apart from a SessionConn
    this.cid = "t" + ++SEQ;
    this.id = null; // sid8, announced by the server
    this.sessionId = null;
    this.seed = opts.seed || null;
    this.resumeId = opts.resumeId || null; // uuid to reattach to (persistence)
    this.drive = true;
    this.label = "";
    this._linebuf = ""; // mirror of the current input line, for /rename interception

    this.container = document.createElement("div");
    this.container.style.cssText = "width:100%;height:100%;";

    this.term = new XTerm({
      cursorBlink: true,
      fontFamily: 'ui-monospace, "Cascadia Code", Consolas, monospace',
      fontSize: 13,
      scrollback: 8000,
      // warm interior to fit the OSRS wood/parchment frame (the S066 reskin
      // leaves the terminal interior to us): --bg ground, --ink text, gold cursor.
      theme: { background: "#17120b", foreground: "#f1e7c4", cursor: "#e6b450" },
    });
    this.fit = FitAddonNS ? new FitAddonNS.FitAddon() : null;
    if (this.fit) this.term.loadAddon(this.fit);
    this.term.open(this.container);

    this.term.onData((d) => this._handleData(d));
    this.term.onResize(({ cols, rows }) => this._send({ type: "resize", cols, rows }));

    live.set(this.cid, this);
    this._connect();
  }

  _send(obj) {
    if (this.ws && this.ws.readyState === 1) this.ws.send(JSON.stringify(obj));
  }

  // Best-effort /rename interception. We mirror the current input line as the
  // user types; when they hit Enter on a line that is exactly `/rename <name>`,
  // the cockpit claims it: backspace away what was typed (so Claude's input box
  // clears) and swallow the Enter (so Claude never submits it), then apply the
  // label. Cursor moves / pastes can desync the mirror — accepted per the user.
  _handleData(d) {
    if (d === "\r" || d === "\n") {
      const m = /^\/rename\s+(.+)$/.exec(this._linebuf.trim());
      if (m && this.id) {
        const name = m[1].trim().slice(0, 48);
        if (this._linebuf.length) this._send({ type: "input", data: "\x7f".repeat(this._linebuf.length) });
        this._linebuf = "";
        setName(this.id, name); // updates board row + console title
        return; // swallow the Enter — Claude never sees the command
      }
      this._linebuf = "";
    } else if (d === "\x7f" || d === "\b") {
      this._linebuf = this._linebuf.slice(0, -1);
    } else if (d.length === 1 && d.charCodeAt(0) >= 0x20) {
      this._linebuf += d;
    } else if (d.charCodeAt(0) < 0x20) {
      this._linebuf = ""; // control / escape (arrows, Ctrl-U, Ctrl-C): drop the mirror
    }
    this._send({ type: "input", data: d });
  }

  _connect() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const cols = this.term.cols || 120;
    const rows = this.term.rows || 30;
    const mode = this.resumeId ? `resume=${this.resumeId}` : "launch=claude";
    const ws = new WebSocket(`${proto}://${location.host}/pty?${mode}&cols=${cols}&rows=${rows}`);
    this.ws = ws;
    ws.onmessage = (e) => {
      let f;
      try {
        f = JSON.parse(e.data);
      } catch {
        return;
      }
      if (f.t === "out") this.term.write(f.d);
      else if (f.t === "session") {
        this.sessionId = f.sessionId;
        this.id = f.sid8;
        bySid8.set(f.sid8, this);
        addOwned(f.sessionId); // remember it so a reopened cockpit can resume it
        if (this.seed) {
          this._seedSoon(this.seed);
          this.seed = null;
        }
      }
    };
    ws.onclose = () => this.term.write("\r\n\x1b[2m[session ended]\x1b[0m\r\n");
  }

  // The claude TUI needs a beat to paint before it accepts input. Type the
  // composed first message, then Enter. Heuristic delay — if it misses, the
  // line is sitting in the prompt and the user just presses Enter.
  _seedSoon(text) {
    setTimeout(() => this._send({ type: "input", data: text + "\r" }), 3000);
  }

  fitNow() {
    if (!this.fit) return;
    try {
      this.fit.fit();
    } catch {}
  }

  close() {
    try {
      this.ws && this.ws.close();
    } catch {}
    try {
      this.term.dispose();
    } catch {}
    if (this.id) bySid8.delete(this.id);
    removeOwned(this.sessionId); // released → don't resume it next open
    live.delete(this.cid);
  }
}

// Start a fresh interactive-claude terminal; `seed` is the composed first
// message (e.g. "Hey Jebrim, …"), auto-typed once the TUI is up.
export function openTerm(seed) {
  return new TermConn({ seed: seed || null });
}

// Reattach to a saved session by uuid (claude --resume). No seed — it continues
// the existing conversation. Used on cockpit open to restore owned terminals.
export function resumeTerm(uuid) {
  return new TermConn({ resumeId: uuid });
}

// The owned session uuids to restore on cockpit open.
export function ownedTermIds() {
  return loadOwned();
}

// Live cockpit-driven terminals (announced, has an sid8). The board merges these
// so a session the cockpit itself is running is always visible/clickable — even
// before it fires a hook event (e.g. a freshly-resumed, still-idle session).
export function liveTerms() {
  const out = [];
  for (const c of live.values()) {
    if (c.id) out.push({ sid8: c.id, sessionId: c.sessionId, label: c.label });
  }
  return out;
}

// A live terminal already hosting this board session, if any (row click → it).
export function termForSid8(sid8) {
  return bySid8.get(sid8) || null;
}

export function Term({ conn }) {
  const ref = useRef(null);
  useEffect(() => {
    const host = ref.current;
    if (host && conn.container.parentNode !== host) host.appendChild(conn.container);
    // size after the element is laid out, then once more after paint
    conn.fitNow();
    const t = setTimeout(() => conn.fitNow(), 60);
    const onResize = () => conn.fitNow();
    window.addEventListener("resize", onResize);
    conn.term.focus();
    return () => {
      clearTimeout(t);
      window.removeEventListener("resize", onResize);
      // intentionally NOT detaching/disposing — the terminal stays alive when
      // you switch rows; release() tears it down.
    };
  }, [conn]);
  // padding insets xterm from the gold frame; bg matches the xterm interior so
  // the inset reads as one warm surface (box-sizing:border-box → fit stays right).
  return html`<div style="width:100%;height:100%;padding:8px 12px;background:#17120b;" ref=${ref}></div>`;
}
