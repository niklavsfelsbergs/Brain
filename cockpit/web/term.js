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

// Terminal font tracks the UI zoom. The .term-host subtree is counter-scaled to
// net 1.0 (so xterm gets true pixels — see styles.css), which means the global
// `zoom` does NOT grow the terminal text on its own; we scale xterm's fontSize by
// --zoom instead. BASE_FONT 13 × the default --zoom 1.35 ≈ the prior 18px.
const BASE_FONT = 13;
function uiZoom() {
  const v = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--zoom"));
  return v > 0 ? v : 1.35;
}
function termFontFor(z) {
  return Math.max(8, Math.round(BASE_FONT * z));
}
function setTermFont(term, f) {
  try {
    if (term.options) term.options.fontSize = f; // xterm 5
    else if (term.setOption) term.setOption("fontSize", f); // xterm 4
  } catch {}
}

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
      // 1.0 (see .term-host in styles.css), not via the global --zoom. We track
      // the zoom by scaling fontSize ourselves (BASE_FONT × --zoom), so the
      // terminal text grows/shrinks with the rest of the UI.
      fontSize: termFontFor(uiZoom()),
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
      // Shift+Enter → insert a newline instead of submitting. Plain xterm sends \r
      // for both Enter and Shift+Enter (indistinguishable in legacy keyboard mode),
      // so Shift+Enter just submits. Iteration history: S072 sent bare \n (LF) —
      // claude's TUI ignores it; S078 sent the CSI-u ESC[13;2u — that only works
      // once claude has negotiated the kitty keyboard protocol, which this PTY/
      // WebView2 build evidently does NOT, so it still failed. ESC+CR (\x1b\r) is
      // the Alt/Option+Enter byte, which claude's input binds to newline-insert
      // with no terminal-protocol setup required — the protocol-independent path.
      // Submit (plain Enter, \r) untouched. (S080 — UNVERIFIED; if it still fails,
      // next fallback is literal backslash + CR "\\\r", the documented \<Enter>.)
      if (e.key === "Enter" && e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey) {
        this._linebuf = "";
        this._send({ type: "input", data: "\x1b\r" });
        return false; // swallow xterm's \r
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
        if (e.ctrlKey || e.metaKey) return; // Ctrl+wheel is the cockpit zoom gesture, not scroll
        if (e.deltaY < 0) this._follow = false;
        else if (e.deltaY > 0 && this._isAtBottom()) this._follow = true;
      },
      { passive: true },
    );

    this.term.onData((d) => this._handleData(d));
    this.term.onResize(({ cols, rows }) => this._send({ type: "resize", cols, rows }));

    // Keep xterm sized to its container through EVERY layout change — the flex
    // settle right after open, panel collapse/divider drag, zoom reflow, re-parent
    // onto a different-sized host. Relying on the mount fit + window 'resize' +
    // explicit fitTerms()/applyTermZoom() calls left gaps where xterm's row count
    // drifted from the visible box: stale rows lingered at the bottom and the
    // prompt could sit below the fold. A ResizeObserver on the host closes them.
    // rAF-debounced (a resize burst reflows once/frame); re-pins to bottom after
    // the refit while following. No feedback loop — fitting xterm's canvas doesn't
    // change the 100%×100% container's box. (S078)
    this._fitRaf = 0;
    if (window.ResizeObserver) {
      this._ro = new ResizeObserver(() => {
        if (this._fitRaf) return;
        this._fitRaf = requestAnimationFrame(() => {
          this._fitRaf = 0;
          this.fitNow();
          if (this._follow) {
            this.term.scrollToBottom();
            const vp = this.container.querySelector(".xterm-viewport");
            if (vp) vp.scrollTop = vp.scrollHeight;
          }
        });
      });
      this._ro.observe(this.container);
    }

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
        if (!follow) return;
        // Drive BOTH, same as the <Term> open pin loop: scrollToBottom() moves
        // xterm's displayed line (ydisp → screen render), but the native
        // .xterm-viewport's scrollTop must be synced too or it desyncs — thumb
        // adrift, prompt below the fold while output streams. S077 fixed this on
        // the open path only; the streaming path here was still scrollToBottom-only.
        this.term.scrollToBottom();
        const vp = this.container.querySelector(".xterm-viewport");
        if (vp) vp.scrollTop = vp.scrollHeight;
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
    if (this._fitRaf) {
      cancelAnimationFrame(this._fitRaf);
      this._fitRaf = 0;
    }
    try {
      this._ro && this._ro.disconnect();
    } catch {}
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

// Re-read --zoom and rescale every live terminal's font, then refit. Called by
// main.js whenever the UI zoom changes. rAF-coalesced so a rapid Ctrl+wheel
// burst reflows xterm once per frame, not once per notch.
let _zoomRaf = 0;
export function applyTermZoom() {
  if (_zoomRaf) return;
  _zoomRaf = requestAnimationFrame(() => {
    _zoomRaf = 0;
    const f = termFontFor(uiZoom());
    for (const c of live.values()) {
      setTermFont(c.term, f);
      c.fitNow();
    }
  });
}

// Refit every live terminal to its container (font unchanged). Called when the
// console column changes width — panel collapse/expand or a divider drag.
export function fitTerms() {
  for (const c of live.values()) c.fitNow();
}

export function Term({ conn }) {
  const ref = useRef(null);
  useEffect(() => {
    const host = ref.current;
    if (host && conn.container.parentNode !== host) host.appendChild(conn.container);
    // Re-parenting the xterm element on open/row-switch resets the viewport and
    // fit() reflows the row count. The subtle failure here is a SCROLLBAR DESYNC,
    // not a "stuck at top": scrollToBottom() moves xterm's displayed line (ydisp)
    // so the SCREEN renders the newest output (prompt visible, looks bottom-ed),
    // but the native .xterm-viewport element's scrollTop is left at 0 because at
    // sync time its scrollHeight wasn't laid out yet. Thumb at top, content at
    // bottom — and a wheel-down off scrollTop=0 maps back to a line near the TOP,
    // so the screen "jumps up." Fix: every frame for a short window, drive BOTH —
    // scrollToBottom() for the render AND the viewport element's scrollTop directly
    // so the native thumb agrees with ydisp. Re-fit through the early reflow frames;
    // bail the instant the user wheels up (_follow flips false). Same pin-every-
    // frame philosophy as the console history view (console.js).
    conn._follow = true; // opening/switching to a row → follow the newest output
    const vp = conn.container.querySelector(".xterm-viewport"); // the native scroll element
    let raf = 0, n = 0;
    const PIN_FRAMES = 48; // ~0.8s @60fps — outlasts WebView2's re-parent/fit relayout
    const pin = () => {
      if (!conn._follow) { raf = 0; return; } // user scrolled up → leave them there
      if (n < 6) conn.fitNow();               // re-fit through the early reflow frames
      conn.term.scrollToBottom();             // ydisp → bottom (drives the screen render)
      if (vp) vp.scrollTop = vp.scrollHeight; // and sync the native scrollbar thumb to match
      raf = ++n < PIN_FRAMES ? requestAnimationFrame(pin) : 0;
    };
    conn.fitNow();
    raf = requestAnimationFrame(pin);
    const onResize = () => conn.fitNow();
    window.addEventListener("resize", onResize);
    conn.term.focus();
    return () => {
      if (raf) cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      // intentionally NOT detaching/disposing — the terminal stays alive when
      // you switch rows; release() tears it down.
    };
  }, [conn]);
  // xterm.js can't live under a scaled ancestor — mouse→cell mapping drifts so a
  // selection lands rows below the pointer and the fit comes up short. Since S073
  // the --zoom lives on the side pillars/rails/console-head, NOT on the terminal's
  // ancestry: .term-frame and .term-host carry no zoom and no transform, so xterm
  // gets a clean 1:1 coordinate system. The terminal tracks the zoom knob via its
  // FONT (term.js termFontFor × --zoom), not its box. See styles.css .term-frame.
  return html`<div class="term-frame"><div class="term-host" ref=${ref}></div></div>`;
}
