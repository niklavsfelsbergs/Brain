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

// xterm + fit addon are UMD globals from web/vendor/*, loaded in index.html.
const XTerm = window.Terminal;
const FitAddonNS = window.FitAddon;

const live = new Map(); // cid  -> TermConn
const bySid8 = new Map(); // sid8 -> TermConn
let SEQ = 0;

class TermConn {
  constructor(seed) {
    this.kind = "term"; // lets main.js tell us apart from a SessionConn
    this.cid = "t" + ++SEQ;
    this.id = null; // sid8, announced by the server
    this.sessionId = null;
    this.seed = seed || null;
    this.drive = true;
    this.label = "";

    this.container = document.createElement("div");
    this.container.style.cssText = "width:100%;height:100%;";

    this.term = new XTerm({
      cursorBlink: true,
      fontFamily: 'ui-monospace, "Cascadia Code", Consolas, monospace',
      fontSize: 13,
      scrollback: 8000,
      theme: { background: "#0d1117", foreground: "#d6dde6", cursor: "#e6b450" },
    });
    this.fit = FitAddonNS ? new FitAddonNS.FitAddon() : null;
    if (this.fit) this.term.loadAddon(this.fit);
    this.term.open(this.container);

    this.term.onData((d) => this._send({ type: "input", data: d }));
    this.term.onResize(({ cols, rows }) => this._send({ type: "resize", cols, rows }));

    live.set(this.cid, this);
    this._connect();
  }

  _send(obj) {
    if (this.ws && this.ws.readyState === 1) this.ws.send(JSON.stringify(obj));
  }

  _connect() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const cols = this.term.cols || 120;
    const rows = this.term.rows || 30;
    const ws = new WebSocket(`${proto}://${location.host}/pty?launch=claude&cols=${cols}&rows=${rows}`);
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
    live.delete(this.cid);
  }
}

// Start a fresh interactive-claude terminal; `seed` is the composed first
// message (e.g. "Hey Jebrim, …"), auto-typed once the TUI is up.
export function openTerm(seed) {
  return new TermConn(seed || null);
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
  return html`<div style="width:100%;height:100%;background:#0d1117;" ref=${ref}></div>`;
}
