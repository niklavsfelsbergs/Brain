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
    // Output write-batching + "stick to bottom" state. Claude's TUI renders by
    // clear-screen-then-full-rewrite; that burst fires scroll events xterm reads as
    // a user scroll-up, so it stops following output and locks at the top (xterm.js
    // #5620). We batch the burst into one write/frame and re-pin to bottom after it
    // renders — but only while _follow is true, and ONLY a real wheel-up clears it.
    this._follow = true;
    this._wq = ""; // pending output queue
    this._wraf = 0; // rAF id for the pending flush

    this.container = document.createElement("div");
    this.container.style.cssText = "width:100%;height:100%;";

    this.term = new XTerm({
      cursorBlink: true,
      fontFamily: 'ui-monospace, "Cascadia Code", Consolas, monospace',
      // sized via xterm because the terminal subtree is counter-scaled to net
      // 1.0 (see .term-host in styles.css), not via the global --zoom (1.35).
      // 13 × 1.35 ≈ the prior visual size.
      fontSize: 18,
      scrollback: 8000,
      // warm interior to fit the OSRS wood/parchment frame (the S066 reskin
      // leaves the terminal interior to us): --bg ground, --ink text, gold cursor.
      theme: { background: "#17120b", foreground: "#f1e7c4", cursor: "#e6b450" },
    });
    this.fit = FitAddonNS ? new FitAddonNS.FitAddon() : null;
    if (this.fit) this.term.loadAddon(this.fit);
    this.term.open(this.container);

    // Paste in WebView2 (pywebview). Two things conspire against the normal path:
    // the .term-host CSS transform makes xterm's textarea-paste handler unreliable
    // (same class of breakage the counter-scale already works around for selection),
    // and WebView2 doesn't reliably deliver Ctrl+V as a native paste event anyway.
    // So we own paste explicitly: intercept Ctrl/Cmd+V and Shift+Insert at keydown,
    // pull the text from the backend clipboard bridge (/api/clipboard — the server
    // is on 127.0.0.1, so its clipboard IS the user's), and feed it through
    // term.paste() (handles bracketed-paste wrapping + emits onData). The native
    // paste listener stays as a fast path for environments where it does fire; both
    // funnel through _doPaste, which dedups so a single Ctrl+V can't paste twice.
    this.term.attachCustomKeyEventHandler((e) => {
      if (e.type !== "keydown") return true;
      const ctrlV = (e.key === "v" || e.key === "V") && (e.ctrlKey || e.metaKey) && !e.altKey;
      const shiftIns = e.key === "Insert" && e.shiftKey;
      if (ctrlV || shiftIns) {
        this._pasteFromClipboard();
        return false; // don't let xterm send a raw ^V to the PTY
      }
      return true;
    });
    this.container.addEventListener(
      "paste",
      (e) => {
        e.preventDefault();
        e.stopPropagation();
        const t = (e.clipboardData && e.clipboardData.getData("text")) || "";
        if (t) this._doPaste(t);
        else this._pasteFromClipboard();
      },
      true,
    );

    // Only a deliberate wheel-up stops us following the bottom; scrolling back down
    // to the bottom resumes it. The TUI's clear/rewrite scroll churn never touches
    // _follow, so a completed turn stays pinned to the newest output.
    this.container.addEventListener(
      "wheel",
      (e) => {
        if (e.deltaY < 0) this._follow = false;
        else if (e.deltaY > 0 && this._isAtBottom()) this._follow = true;
      },
      { passive: true },
    );

    this.term.onData((d) => this._handleData(d));
    this.term.onResize(({ cols, rows }) => this._send({ type: "resize", cols, rows }));

    live.set(this.cid, this);
    this._connect();
  }

  _send(obj) {
    if (this.ws && this.ws.readyState === 1) this.ws.send(JSON.stringify(obj));
  }

  // Single funnel for all paste sources, with a short dedup window so the keydown
  // handler and a native paste event firing for the same Ctrl+V don't double up.
  _doPaste(text) {
    if (!text) return;
    const now = Date.now();
    if (text === this._lastPasteText && now - (this._lastPasteAt || 0) < 250) return;
    this._lastPasteText = text;
    this._lastPasteAt = now;
    this.term.paste(text);
  }

  // Pull clipboard text and paste it. Tries the backend bridge first (works in the
  // webview without clipboard permissions); falls back to the async Clipboard API
  // for the case where the cockpit is opened in a plain browser pointed at a remote
  // server (where the server's clipboard wouldn't be the user's).
  async _pasteFromClipboard() {
    let text = "";
    try {
      const r = await fetch("/api/clipboard");
      if (r.ok) text = (await r.json()).text || "";
    } catch {}
    if (!text) {
      try {
        if (navigator.clipboard && navigator.clipboard.readText)
          text = await navigator.clipboard.readText();
      } catch {}
    }
    this._doPaste(text);
  }

  _isAtBottom() {
    try {
      const b = this.term.buffer.active;
      return b.viewportY >= b.baseY;
    } catch {
      return true;
    }
  }

  // Batch PTY output into one write per animation frame, then re-pin to the bottom
  // after it renders (write's callback fires post-parse). Batching collapses the
  // TUI's clear/rewrite burst so xterm sees one coherent frame instead of many
  // half-states; the post-render scrollToBottom counters the spurious scroll the
  // clear-screen would otherwise leave us in. Gated on _follow so a user who scrolled
  // up to read history is never yanked back down.
  _write(data) {
    this._wq += data;
    if (this._wraf) return;
    this._wraf = requestAnimationFrame(() => {
      this._wraf = 0;
      const d = this._wq;
      this._wq = "";
      if (!d) return;
      const follow = this._follow;
      this.term.write(d, () => {
        if (follow) this.term.scrollToBottom();
      });
    });
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
      if (f.t === "out") this._write(f.d);
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
    if (this._wraf) {
      cancelAnimationFrame(this._wraf);
      this._wraf = 0;
    }
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
    // Re-parenting the xterm element on open/row-switch resets its viewport to the
    // top of the scrollback, and fit() reflows the row count — so the scroll-to-
    // newest must happen AFTER fit + layout commit. A synchronous scrollToBottom
    // races the reflow and lands at the top; for a still-streaming session the next
    // write re-pins it (you never notice), but for an IDLE one (agent done thinking,
    // no more output) nothing corrects it and you're stuck at the top. Fix: fit, then
    // scroll on the next two frames (past xterm's renderer committing the new dims),
    // and once more after a short beat as a belt-and-suspenders for WebView2's slower
    // transform/relayout under .term-host.
    conn._follow = true; // opening/switching to a row → follow the newest output
    let raf1 = 0, raf2 = 0;
    const settle = () => {
      conn.fitNow();
      raf1 = requestAnimationFrame(() => {
        conn.term.scrollToBottom();
        raf2 = requestAnimationFrame(() => conn.term.scrollToBottom());
      });
    };
    settle();
    const t = setTimeout(settle, 120);
    const onResize = () => conn.fitNow();
    window.addEventListener("resize", onResize);
    conn.term.focus();
    return () => {
      clearTimeout(t);
      cancelAnimationFrame(raf1);
      cancelAnimationFrame(raf2);
      window.removeEventListener("resize", onResize);
      // intentionally NOT detaching/disposing — the terminal stays alive when
      // you switch rows; release() tears it down.
    };
  }, [conn]);
  // The cockpit scales the whole UI with CSS `zoom` (--zoom) on .app-grid, but
  // xterm.js can't live under a scaled ancestor — mouse→cell mapping drifts so a
  // selection lands rows below the pointer and the fit comes up short. .term-frame
  // is a normal flex item (so the column layout is safe); the inner .term-host
  // counter-scales with `transform` (visual-only — can't disturb layout footprint
  // like zoom did) back to net 1.0, and .term-frame clips any spill. Terminal size
  // comes from xterm fontSize, not the zoom. See styles.css .term-frame/.term-host.
  return html`<div class="term-frame"><div class="term-host" ref=${ref}></div></div>`;
}
