// term.js — the embedded real-terminal view (S066 B). Runs interactive `claude`
// in a PTY via the backend /pty bridge and renders it with xterm.js. This is the
// subscription-billed path (no headless `claude -p`); a real TTY also gives Esc
// and AskUserQuestion/ExitPlanMode for free.
//
// Like fleet.js's SessionConn, a TermConn lives independent of the view: its
// xterm + WebSocket stay alive when you switch to another row, so the cockpit
// runs a *fleet* of terminals. The Preact <Term/> just re-parents the live
// xterm element on mount. Styling is inline to stay off the shared styles.css.

import { useEffect, useRef, useState } from "preact/hooks";
import { html } from "htm/preact";
import { setName, nameFor } from "./names.js";
import { registerTermLinks } from "./links.js";

// xterm + fit addon are UMD globals from web/vendor/*, loaded in index.html.
const XTerm = window.Terminal;
const FitAddonNS = window.FitAddon;

const live = new Map(); // cid  -> TermConn
const bySid8 = new Map(); // sid8 -> TermConn
let SEQ = 0;

// Gap between pasting a composed message and sending the submitting CR. Must
// exceed claude's fast-input/paste-coalesce window so the CR isn't folded into
// the paste (which would land as a literal newline, not a submit). See
// submitComposed. ~110ms is imperceptible to the user but clears the window.
const COMPOSE_SUBMIT_DELAY_MS = 110;

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

// Auto-label persistence (S095). DISTINCT from the manual /rename store (names.js,
// keyed by sid8). This remembers the label a terminal was PLACED with — the actor
// name like "Jebrim", or "chat" for a playerless session — keyed by the durable
// session uuid. Without it, a resumed session loses its auto-name: resumeTerm()
// starts with an empty label and an idle just-resumed session has no hook actor
// attribution yet, so the board falls back to the bare "chat". On the board a
// manual rename still wins (nameFor(sid8) is checked first); this only feeds the
// auto-name fallback so "Jebrim" survives a restart instead of degrading to "chat".
const TERM_LABELS = "cockpit-term-labels";
function loadTermLabel(uuid) {
  if (!uuid) return "";
  try {
    return (JSON.parse(localStorage.getItem(TERM_LABELS) || "{}") || {})[uuid] || "";
  } catch {
    return "";
  }
}
function saveTermLabel(uuid, label) {
  if (!uuid || !label) return;
  try {
    const m = JSON.parse(localStorage.getItem(TERM_LABELS) || "{}") || {};
    if (m[uuid] === label) return;
    m[uuid] = label;
    localStorage.setItem(TERM_LABELS, JSON.stringify(m));
  } catch {}
}

class TermConn {
  constructor(opts = {}) {
    this.kind = "term"; // lets main.js tell us apart from a SessionConn
    this.cid = "t" + ++SEQ;
    this.id = null; // sid8, announced by the server
    this.sessionId = null;
    this.seed = opts.seed || null;
    // submitSeed false: type the seed into the prompt WITHOUT a trailing CR, so
    // the user continues from a prewritten address (place modal). Default true
    // preserves the old "seed = whole first message, auto-sent" behavior.
    this.submitSeed = opts.submitSeed !== false;
    this.placedName = ""; // user-chosen name from the place modal; applied on connect
    this.resumeId = opts.resumeId || null; // uuid to reattach to (persistence)
    this.drive = true;
    // Restore the auto-label on resume so a reopened "Jebrim" session keeps its
    // name instead of degrading to "chat" (S095). A manual rename still overrides
    // this on the board. New sessions start blank; main.js sets the placement
    // label, which is persisted when the session announces (below).
    this.label = this.resumeId ? loadTermLabel(this.resumeId) : "";
    this._linebuf = ""; // mirror of the current input line, for /rename interception
    // Output write-batching + "stick to bottom" state. Claude's TUI renders by
    // clear-screen-then-full-rewrite; that burst fires scroll events xterm reads as
    // a user scroll-up, so it stops following output and locks at the top (xterm.js
    // #5620). We batch the burst into one write/frame and re-pin to bottom after it
    // renders — but only while _follow is true, and ONLY a real wheel-up clears it.
    this._follow = true;
    this._wq = ""; // pending output queue
    this._wraf = 0; // rAF id for the pending flush
    // Esc-cancel tracking. No hook fires on an interrupt (Stop only fires on
    // natural completion), so a cancelled turn's status stays stuck at busy. The
    // cockpit SEES the Esc keystroke here, so it can tell the board to clear
    // busy→idle at once. Set on Esc, cleared on the next submit. (S083)
    this._interruptedAt = 0;

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
    // Make path tokens in the terminal grid clickable → open the file / reveal the
    // folder on the host (S160). Built-in link provider, no addon needed.
    registerTermLinks(this.term);

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
      this._diag("keydown"); // [term-diag] opt-in: window.__TERMDIAG (no-op otherwise)
      // Esc cancels the running turn — record it (no hook fires on interrupt) so the
      // board can clear a stuck busy→idle immediately. Let Esc through to claude.
      if (e.key === "Escape") {
        this._interruptedAt = Date.now();
        // Clear any half-typed line so it can't merge into the next message. The
        // line lives in claude's in-terminal input box; Esc cancels the turn but
        // leaves the box as-is, so a later composed send would prepend it.
        // Backspace away the mirrored chars (best-effort, same trick as /rename),
        // then let Esc through to claude to interrupt. (S086)
        if (this._linebuf.length) this._send({ type: "input", data: "\x7f".repeat(this._linebuf.length) });
        this._linebuf = "";
      }
      const ctrlV = (e.key === "v" || e.key === "V") && (e.ctrlKey || e.metaKey) && !e.altKey;
      const shiftIns = e.key === "Insert" && e.shiftKey;
      if (ctrlV || shiftIns) {
        this._pasteFromClipboard();
        return false; // don't let xterm send a raw ^V to the PTY
      }
      // Ctrl/Cmd+C copies the selection — the reflexive expectation — but ONLY when
      // something is selected. With no selection it falls through so xterm still sends
      // \x03 and interrupts the PTY (and Esc already interrupts here too, so claiming
      // Ctrl+C for copy costs nothing). The clipboard WRITE goes through the backend
      // bridge for the same reason paste reads from it: WebView2 gates the native
      // navigator.clipboard path; the server's clipboard IS the user's. (S087)
      const ctrlC = (e.key === "c" || e.key === "C") && (e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey;
      if (ctrlC && this.term.hasSelection()) {
        this._copyToClipboard(this.term.getSelection());
        return false; // copied the selection — swallow, don't fire SIGINT at the PTY
      }
      // Shift+Enter → newline, not submit. The terminal can't encode Shift+Enter on
      // the wire (legacy mode sends the same \r as Enter), but THIS handler sees
      // e.shiftKey — so we just send claude the byte for its DOCUMENTED universal
      // newline: Ctrl+J = LF = 0x0A. Per Claude Code docs (code.claude.com/docs/en/
      // terminal-config): "press Ctrl+J … works in every terminal with no setup."
      // History: S072 sent 0x0A and saw nothing, but that was an ancient claude build,
      // never re-verified on fresh code; the four attempts since — kitty ESC[13;2u
      // (unnegotiated), Alt+Enter \x1b\r, backslash+Enter \\\r, bracketed paste — ALL
      // still submitted on current code. \\\r likely loses a burst race (the CR is
      // handled before the \ commits to the line buffer); a lone 0x0A has no such
      // race and needs no protocol. Back to the documented primitive. (S081c.)
      if (e.key === "Enter" && e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey) {
        // preventDefault so the browser doesn't ALSO deliver Enter to xterm's
        // hidden textarea: `return false` stops xterm's own keydown path, but in
        // this WebView2 build the textarea can still emit a \r that submits
        // ALONGSIDE our \n (the likely reason 6 byte-attempts all "submitted").
        // Belt-and-suspenders — kill both default paths, send only the LF. (S083)
        e.preventDefault();
        if (window.__TERMDIAG) console.log("[term-diag] shift+enter caught -> sending \\n (0x0A)");
        this._linebuf = "";
        this._send({ type: "input", data: "\n" });
        return false; // swallow xterm's \r (submit stays plain Enter)
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
        // [term-diag issue#3] capture scroll geometry to disk so the "scroll-up
        // locks, can't scroll-down" stuck state lands in term-fit-diag.log. rAF so
        // the sample reflects the POST-scroll geometry. Throttled (120ms) so a wheel
        // burst doesn't flood the log. STRIP with the rest of the diag once fixed.
        const now = Date.now();
        if (now - (this._wheelDiagAt || 0) > 120) {
          this._wheelDiagAt = now;
          requestAnimationFrame(() => this._diag("wheel" + (e.deltaY < 0 ? "Up" : "Dn"), true));
        }
      },
      { passive: true },
    );

    this.term.onData((d) => this._handleData(d));
    // Route every xterm resize through the coalescer, not a direct _send. fit.fit()
    // + the over-fit guard's row-shrink loop + a zoom/RO burst each fire several
    // onResize events in quick succession; one setwinsize per event STORMS ConPTY
    // (pywinpty), which corrupts its screen buffer mid-redraw and leaves claude's
    // TUI repainting its input box on the wrong rows. Coalescing collapses a burst
    // into one trailing send of the final size. (S094)
    this.term.onResize(({ cols, rows }) => this._queueResize(cols, rows));

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
        // Skip while hidden/zero-size. When <Term> is display:none under the
        // transcript view the container collapses to 0×0 and RO fires; fitting a
        // 0-box drives FitAddon to its 2-col minimum (and resizes the PTY to 2
        // cols) — the "terminal renders ~3 chars wide after a toggle" bug. RO
        // fires again with a real box when the view comes back. (S093)
        if (!this.container.clientWidth || !this.container.clientHeight) return;
        this._fitRaf = requestAnimationFrame(() => {
          this._fitRaf = 0;
          this.fitNow();
          if (this._follow) this._pinBottom();
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

  // Coalesce outgoing PTY resizes (trailing-debounced). A single fitNow fires up to
  // ~5 onResize events (fit.fit() + the over-fit guard's row-shrink loop), and
  // fitNow itself runs on every RO tick / zoom notch / transcript re-show — so the
  // naive "setwinsize per onResize" sent a STORM that corrupts ConPTY's buffer and
  // garbles claude's redraw. Hold only the latest size; send once 60ms after the
  // burst settles. The ws.onopen resync covers the very first frame (this timer can
  // fire while the WS is still CONNECTING, where _send no-ops). (S094)
  _queueResize(cols, rows) {
    this._pendingSize = { cols, rows };
    if (this._resizeTimer) clearTimeout(this._resizeTimer);
    this._resizeTimer = setTimeout(() => {
      this._resizeTimer = 0;
      const s = this._pendingSize;
      this._pendingSize = null;
      if (!s) return;
      if (window.__TERMDIAG) console.log("[term-diag] resize -> PTY", s.cols, s.rows);
      this._send({ type: "resize", cols: s.cols, rows: s.rows });
    }, 60);
  }

  // Send a message composed in the fixed compose-bar (TermComposer) straight to
  // the PTY, instead of typing into claude's in-terminal prompt. THIS is what
  // lets the user scroll the terminal history freely while writing: the prompt
  // lives in the scroll grid, but the compose-bar is a separate fixed element
  // below the xterm. Plain prompts + Enter only — interactive TUI bits (slash
  // autocomplete, @-picker, plan approval, AskUserQuestion arrow-menus) still
  // need a click into the terminal itself. (S086)
  submitComposed(text) {
    const t = String(text || "").replace(/\r\n?/g, "\n").replace(/\n+$/, "");
    if (!t.trim()) return false;
    // /rename parity with terminal-typed input — claim it, don't send to claude.
    const m = /^\/rename\s+(.+)$/.exec(t.trim());
    if (m && this.id) {
      setName(this.id, m[1].trim().slice(0, 48));
      return true;
    }
    if (!this.ws || this.ws.readyState !== 1) return false; // not connected yet — keep the text
    // Clear any text the user half-typed directly into claude's in-terminal box
    // (the terminal is focused by default) so it can't get prepended to this
    // composed message. Best-effort via the _linebuf mirror — same as /rename.
    if (this._linebuf.length) this._send({ type: "input", data: "\x7f".repeat(this._linebuf.length) });
    this._interruptedAt = 0; // a submit means the session is live again (stop the busy→idle override)
    this._linebuf = "";
    this._follow = true; // jump back to the newest so the message + reply are in view
    // Insert the text as a bracketed paste, THEN submit with a separate, delayed
    // CR. claude enables DECSET 2004, so term.paste wraps the content in
    // \x1b[200~…\x1b[201~ and claude inserts it into its input box WITHOUT
    // submitting — single- or multi-line, any content. The bug this fixes: a
    // text+"\r" burst (or paste+immediate-CR) arrives inside claude's fast-input/
    // paste-coalesce window, so the trailing CR is folded into the paste and lands
    // as a LITERAL NEWLINE in the prompt instead of submitting — the "I press
    // Enter and the text just sits in the terminal" symptom. The delayed, separate
    // CR clears that window so claude sees a clean Enter. (Same timing family as
    // the seed first-message send.)
    this.term.paste(t);
    setTimeout(() => {
      this._send({ type: "input", data: "\r" });
      this._pinBottom();
    }, COMPOSE_SUBMIT_DELAY_MS);
    this._pinBottom();
    return true;
  }

  // Esc from the compose-bar cancels the running turn (parity with Esc typed in
  // the terminal). Record _interruptedAt so the board clears a stuck busy→idle at
  // once — no hook fires on an interrupt. Cleared on the next submit. (S086)
  sendEsc() {
    this._interruptedAt = Date.now();
    // Clear any half-typed in-terminal line first (see submitComposed), then Esc.
    if (this._linebuf.length) this._send({ type: "input", data: "\x7f".repeat(this._linebuf.length) });
    this._linebuf = "";
    this._send({ type: "input", data: "\x1b" });
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

  // Write the current selection to the clipboard. Backend bridge first (the reliable
  // path inside WebView2, mirroring _pasteFromClipboard); navigator.clipboard.writeText
  // as the fallback for the plain-browser case. Best-effort — a failure just means the
  // copy silently didn't take, never throws into the key handler. (S087)
  async _copyToClipboard(text) {
    if (!text) return;
    try {
      const r = await fetch("/api/clipboard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (r.ok && (await r.json()).ok) return;
    } catch {}
    try {
      if (navigator.clipboard && navigator.clipboard.writeText)
        await navigator.clipboard.writeText(text);
    } catch {}
  }

  // Pin the viewport to the newest output. xterm's displayed line (scrollToBottom →
  // ydisp) and the native .xterm-viewport scrollbar must be driven TOGETHER — moving
  // one without the other desyncs them (thumb adrift, prompt below the fold). Every
  // geometry change that can shift the row count re-pins through here while _follow.
  _pinBottom() {
    try {
      this._syncViewport(); // scrollHeight must reflect the true buffer before we pin to it
      this.term.scrollToBottom();
      const vp = this.container.querySelector(".xterm-viewport");
      if (vp) vp.scrollTop = vp.scrollHeight;
    } catch {}
  }

  _isAtBottom() {
    // xterm's BUFFER is authoritative (viewportY >= baseY). The native
    // .xterm-viewport scrollbar is NOT trustworthy here: its scrollHeight lags the
    // buffer by ~one viewport when output arrives off-bottom (or on a fresh open),
    // so "scrollTop is maxed" reads true while ydisp is still rows short of baseY.
    // Trusting that stale signal (the old EITHER branch) was the bug: a wheel-down
    // capped at the native floor, _isAtBottom false-positived, and _follow flipped
    // on while genuinely above the bottom — the prompt + compose bar locked below
    // the fold until a keystroke (issue#3, 2026-05-27 trace: wheelDn viewportY=120
    // baseY=191 follow=true). The native fallback survives only if the buffer read
    // throws. (Supersedes the S081 H2 EITHER rule; the over-fit guard's mid-stream
    // index wobble is moot now — _syncViewport keeps scrollHeight honest.)
    try {
      const b = this.term.buffer.active;
      return b.viewportY >= b.baseY;
    } catch {}
    try {
      const vp = this.container.querySelector(".xterm-viewport");
      if (vp) {
        const slack = this._cellHeight() || 24;
        return vp.scrollHeight - vp.clientHeight - vp.scrollTop <= slack;
      }
    } catch {}
    return true;
  }

  // Force xterm's render service to recompute the .xterm-viewport scroll area so
  // its scrollHeight tracks the live buffer length. Without this the native scroll
  // area lags the buffer by ~one viewport when output arrives off-bottom or on a
  // fresh open, so a wheel-down caps short of the true bottom (issue#3). refresh()
  // marks the row range dirty → onRender → viewport syncScrollArea; cheap and
  // idempotent within a frame.
  _syncViewport() {
    try {
      this.term.refresh(0, this.term.rows - 1);
    } catch {}
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
        // Always resync the native scroll area to the grown buffer — even when NOT
        // following — so a user scrolled up to read can still wheel down to the
        // true bottom (the scrollHeight lag was what stranded them; issue#3).
        this._syncViewport();
        if (follow) this._pinBottom();
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
      this._interruptedAt = 0; // a submit means the session is live again — stop the busy→idle override
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
    // [term-diag] opt-in: log control bytes xterm sends to the PTY. After a
    // shift+enter this reveals whether a stray \r (code 13) ALSO leaks through —
    // the smoking gun for "newline still submits." window.__TERMDIAG = 1.
    if (window.__TERMDIAG && d.charCodeAt(0) < 0x20)
      console.log("[term-diag] onData->PTY ctrl:", JSON.stringify(d), "codes", [...d].map((c) => c.charCodeAt(0)));
    this._send({ type: "input", data: d });
  }

  _connect() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const cols = this.term.cols || 120;
    const rows = this.term.rows || 30;
    const mode = this.resumeId ? `resume=${this.resumeId}` : "launch=claude";
    // /pty is token-gated (S085): the backend bakes a per-process secret into the
    // served HTML as window.__CT; send it or the handshake is rejected (403).
    const tok = window.__CT ? `&token=${encodeURIComponent(window.__CT)}` : "";
    const ws = new WebSocket(`${proto}://${location.host}/pty?${mode}&cols=${cols}&rows=${rows}${tok}`);
    this.ws = ws;
    // Authoritative size resync the instant the pipe is live. The launch cols/rows
    // in the URL above were read off this.term.cols at CONSTRUCTION — before <Term/>
    // attached the container — so they can be xterm's default 80×24, not the real
    // fitted size. Any fitNow that fired while the WS was still CONNECTING had its
    // resize frame silently dropped (_send no-ops unless readyState===1). Without
    // this, the PTY can sit at the wrong width forever: claude wraps its input box
    // at one width while xterm paints at another, stacking box borders on the wrong
    // rows (the Image-1 garble). Re-fit now and send the true size directly (skip
    // the coalescer's delay) so they agree from the first paint. (S094)
    ws.onopen = () => {
      this.fitNow();
      if (window.__TERMDIAG) console.log("[term-diag] ws open -> resync", this.term.cols, this.term.rows);
      this._send({ type: "resize", cols: this.term.cols, rows: this.term.rows });
    };
    ws.onmessage = (e) => {
      let f;
      try {
        f = JSON.parse(e.data);
      } catch {
        return;
      }
      if (f.t === "out") this._write(f.d);
      else if (f.t === "session") {
        // Re-announce (f.rotated): claude rotated its session id inside this PTY
        // (a /clear, or a new task in the same shell). The server detected the
        // new live id; swap ours so liveTerms reports the CURRENT sid8 — the
        // board then dedups against the manifest row instead of showing a stale
        // drivable ghost beside a read-only real row. Drop the old key/owned-uuid
        // so the row collapses and a reopened cockpit resumes the current convo.
        const prevId = this.id;
        const prevSessionId = this.sessionId;
        // [rename-diag] opt-in: `window.__RENAMEDIAG = 1` traces the carry path in
        // the console (zero-cost no-op when the flag is unset). The always-on
        // server-side rename-diag.log writer was removed once the orphan bug was fixed.
        if (window.__RENAMEDIAG)
          console.log("[rename-diag] session frame", { prevId, sid8: f.sid8, rotated: !!f.rotated, resumeId: this.resumeId, nameForNew: nameFor(f.sid8) });
        if (prevId && prevId !== f.sid8) {
          // Carry the /rename label (localStorage, keyed by sid8) across the id
          // rotation. A /clear or a `claude --resume` (cockpit reopen) mints a new
          // id; without this the label is orphaned under the old sid8 and the row
          // comes back unnamed. Disk-backed labels are carried server-side in
          // ptybridge._carry_disk_name; this is the localStorage half. Try the
          // immediate predecessor, then fall back to the resume anchor's sid8 —
          // on a restart the name was last keyed under the resume uuid, which
          // prevId may no longer equal once claude rotates off it. (S093b)
          const anchor = this.resumeId ? this.resumeId.slice(0, 8) : "";
          const carried = nameFor(prevId) || (anchor ? nameFor(anchor) : "");
          if (carried && !nameFor(f.sid8)) setName(f.sid8, carried);
          if (window.__RENAMEDIAG)
            console.log("[rename-diag] carry", { prevId, anchor, carried, applied: nameFor(f.sid8) });
          bySid8.delete(prevId);
        }
        if (prevSessionId && prevSessionId !== f.sessionId) removeOwned(prevSessionId);
        this.sessionId = f.sessionId;
        this.id = f.sid8;
        bySid8.set(f.sid8, this);
        addOwned(f.sessionId); // remember it so a reopened cockpit can resume it
        if (this.label) saveTermLabel(f.sessionId, this.label); // keep the auto-name across resume (S095)
        // A name typed in the place modal becomes the board row name (same store
        // as /rename), now that the sid8 is known. Don't clobber a rename that
        // already landed under this sid8.
        if (this.placedName && !nameFor(f.sid8)) setName(f.sid8, this.placedName);
        if (this.seed) {
          this._seedSoon(this.seed);
          this.seed = null;
        }
      }
    };
    ws.onclose = () => this.term.write("\r\n\x1b[2m[session ended]\x1b[0m\r\n");
  }

  // The claude TUI needs a beat to paint before it accepts input. Type the seed,
  // then (if submitSeed) Enter. Heuristic delay — if it misses, the line is
  // sitting in the prompt and the user just presses Enter. With submitSeed false
  // (place modal) the seed is a prewritten address the user continues from, so no
  // CR — and no fast-input/CR-fold risk, since there's no trailing CR to fold.
  _seedSoon(text) {
    setTimeout(
      () => this._send({ type: "input", data: this.submitSeed ? text + "\r" : text }),
      3000,
    );
  }

  // ── [term-diag] S081/S083 — fit/scroll geometry, the instrument for the
  // recurring prompt-below-fold bug. Prints the numbers needed to tell H1
  // (over-fit: overfit>0, bottom row below the clip) from H2 (scroll-desync:
  // overfit~0 but viewportY/scrollTop disagree) WITHOUT guessing the fix again.
  // Two call sites: keydown (throttled) + the <Term/> open pin loop (force=true,
  // the decisive f1/f8/f40 samples — bypass the throttle so none are dropped).
  //
  // Console output stays opt-in (`window.__TERMDIAG = 1` in DevTools) — a
  // zero-cost no-op when the flag is unset. (The transient disk sink that
  // POSTed each open-frame line to /api/termdiag → switchboard/term-fit-diag.log
  // was removed once the prompt-below-fold bug was fixed; the backend route went
  // with it.)
  _diag(why, force = false) {
    const now = Date.now();
    if (!force && now - (this._diagAt || 0) < 250) return;
    this._diagAt = now;
    try {
      const frame = this.container.closest(".term-frame") || this.container.parentElement;
      const cell = this._cellHeight();
      const rows = this.term.rows, cols = this.term.cols;
      const fh = frame ? frame.clientHeight : -1;
      const used = rows * cell;
      const overPx = used - (fh - 16); // 16 = .term-host vertical padding
      const b = this.term.buffer.active;
      const vp = this.container.querySelector(".xterm-viewport");
      const line =
        `${why} cid=${this.cid} frameH=${fh} rows=${rows} cols=${cols} ` +
        `cellH=${cell.toFixed(2)} rows*cellH=${used.toFixed(1)} overfit=${overPx.toFixed(1)}px ` +
        `follow=${this._follow} viewportY=${b.viewportY} baseY=${b.baseY} ` +
        `vp.scrollTop=${vp ? vp.scrollTop : "?"} vp.scrollHeight=${vp ? vp.scrollHeight : "?"} ` +
        `vp.clientHeight=${vp ? vp.clientHeight : "?"}`;
      if (window.__TERMDIAG) console.log("[term-diag] " + line);
    } catch (e) {
      if (window.__TERMDIAG) console.log("[term-diag] error", e);
    }
  }

  fitNow() {
    if (!this.fit) return;
    // Never fit a hidden/zero-size box (display:none under the transcript view) —
    // FitAddon would collapse cols to its 2-col minimum and resize the PTY with
    // it, leaving the terminal a few chars wide when you switch back. Bail until
    // it has a real box; the ResizeObserver re-fires when it reappears. (S093)
    if (this.container.clientWidth < 2 || this.container.clientHeight < 2) return;
    try {
      this.fit.fit();
      // Over-fit guard (S081). The fit addon floors rows = frameContentHeight /
      // cellHeight, but it reads `.term-host`'s getComputedStyle height — which in
      // this WebView2 build can come back a hair taller than the box that actually
      // PAINTS inside `.term-frame{overflow:hidden}` (the zoomed `.console-head`
      // sibling consumes a non-integer 50×--zoom px of the flex column, and the
      // flex:1 terminal div's reported vs painted height can disagree by up to ~a
      // row). When rows×cellHeight exceeds the frame's real clientHeight, the
      // bottom row — the live `>` prompt after a turn — renders below the clip and
      // is invisible until a keystroke forces a cursor scroll. Floor can't catch
      // this because the error is in the height it measured, not in the division.
      // So: re-measure against the ACTUAL painted frame and shrink by a row while
      // the terminal physically overflows it. Cheap, bounded, reversible.
      const cell = this._cellHeight();
      const frame = this.container.closest(".term-frame") || this.container.parentElement;
      if (cell > 0 && frame) {
        let guard = 0;
        // 8px top + 8px bottom .term-host padding (styles.css .term-host).
        const pad = 16;
        let shrank = false;
        while (this.term.rows > 1 && this.term.rows * cell > frame.clientHeight - pad && guard++ < 4) {
          this.term.resize(this.term.cols, this.term.rows - 1);
          shrank = true;
        }
        // [term-diag issue#3] a resize here reflows xterm and re-syncs the native
        // viewport scroll area — if it fires while the user is scrolled up it can
        // collapse scrollHeight and lock the down-scroll. Log when it actually
        // shrinks so the trace shows whether fitNow is the thing breaking scroll.
        if (shrank) this._diag("overfit-shrink", true);
      }
    } catch {}
  }

  // Re-fit + re-pin to bottom across a short multi-frame window when the terminal
  // becomes VISIBLE again. The <Term> mount pin loop runs once when a row is
  // selected; if that selection happened while the transcript view was up, the
  // terminal mounted display:none (0-height frame) so the loop's fitNow bailed and
  // _pinBottom no-op'd — the terminal never fit/pinned. Flipping back to terminal
  // then only triggers a SINGLE RO fit+pin, which can land before the layout's
  // scrollHeight settles, leaving the prompt below the fold until a keystroke (the
  // "textbox stuck on a session opened from transcript view" trace — term-fit-diag
  // showed `open … frameH=0`, then recovery only on the next `keydown`; S095).
  // main.js calls this on the transcript→terminal flip. Mirrors the open pin loop:
  // skip frames while still hidden, fit the first few visible frames, pin every
  // visible frame. A wheel-up (_follow=false) ends it so it never fights a reader.
  reshow() {
    if (this._reshowRaf) cancelAnimationFrame(this._reshowRaf);
    this._follow = true;
    let n = 0, fits = 0;
    const FRAMES = 40; // ~0.66s @60fps — outlasts the display:none→visible relayout
    const step = () => {
      const visible = this.container.clientWidth >= 2 && this.container.clientHeight >= 2;
      if (visible && this._follow) {
        if (fits < 6) { this.fitNow(); fits++; } // fit through the early reflow frames
        this._pinBottom();                        // ydisp → bottom AND native thumb
      }
      this._reshowRaf = (this._follow && ++n < FRAMES) ? requestAnimationFrame(step) : 0;
    };
    this._reshowRaf = requestAnimationFrame(step);
  }

  // Rendered cell (row) height in px. Prefer xterm's measured render dimensions.
  // Fallback: visible viewport height / visible row count — NOT scrollHeight /
  // buffer.active.length, which divides by the whole 8000-line scrollback (not the
  // rendered rows) and yields a plausible-but-wrong number. Used by the over-fit
  // guard and the [term-diag] block.
  _cellHeight() {
    try {
      const h = this.term._core?._renderService?.dimensions?.css?.cell?.height;
      if (h > 0) return h;
    } catch {}
    try {
      const vp = this.container.querySelector(".xterm-viewport");
      if (vp && this.term.rows > 0) return vp.clientHeight / this.term.rows;
    } catch {}
    return 0;
  }

  // Reconnect this terminal in place after a wake-from-sleep (S161). The sleep
  // dropped the WS, so ptybridge ran its finally and terminated the old claude;
  // we force-close our (possibly half-open) socket so the server is sure to tear
  // it down, then resume the SAME conversation in a fresh PTY (claude --resume) on
  // the existing xterm + board identity — NO page reload, so only terminals that
  // were actually open get revived (the full owned-history resume stays a reopen-
  // only thing; that's what was resurrecting old "0s" sessions). Safe against a
  // double-writer: the old proc is already gone, and the short delay lets the
  // server's terminate + transcript release land before --resume reopens it.
  reconnect() {
    const uuid = this.sessionId || this.resumeId;
    if (!uuid) return; // never announced a session — nothing to resume onto
    this.resumeId = uuid; // _connect reads resumeId → resume mode (claude --resume)
    this._interruptedAt = 0;
    try { if (this.ws) this.ws.close(); } catch {}
    this.ws = null;
    this.term.write("\r\n\x1b[2m[reconnecting after wake…]\x1b[0m\r\n");
    setTimeout(() => this._connect(), 1000);
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
    if (this._reshowRaf) {
      cancelAnimationFrame(this._reshowRaf);
      this._reshowRaf = 0;
    }
    if (this._resizeTimer) {
      clearTimeout(this._resizeTimer);
      this._resizeTimer = 0;
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

// Start a fresh interactive-claude terminal. `seed` is auto-typed once the TUI
// is up. opts.submit (default true) auto-sends it; submit:false prewrites it as
// an address the user continues from (place modal — e.g. "Hey Jebrim, ").
export function openTerm(seed, opts = {}) {
  return new TermConn({ seed: seed || null, submitSeed: opts.submit !== false });
}

// Reattach to a saved session by uuid (claude --resume). No seed — it continues
// the existing conversation. Used on cockpit open to restore owned terminals.
export function resumeTerm(uuid) {
  return new TermConn({ resumeId: uuid });
}

// Hand a cockpit session off to THIS client. Asks the backend to terminate the
// PTY currently driving it (on whatever client owns it), then — only if one was
// actually terminated — resumes the conversation here in a fresh PTY. The
// `found` gate is the safety invariant: if no live cockpit PTY drove the session
// (a VS Code session, or one already gone) we do NOT resume, so this never
// becomes a second writer on the same transcript. Returns the new driven
// TermConn, or null if the takeover could not be performed.
export async function handoffAndResume(sessionId) {
  if (!sessionId) return null;
  const sid8 = sessionId.slice(0, 8);
  const tok = window.__CT ? `&token=${encodeURIComponent(window.__CT)}` : "";
  let found = false;
  try {
    const r = await fetch(`/api/handoff?sid8=${encodeURIComponent(sid8)}${tok}`, { method: "POST" });
    const j = await r.json();
    found = !!(j && j.ok && j.found);
  } catch {
    return null;
  }
  if (!found) return null;
  // brief beat so the terminated claude exits + releases the transcript file
  // before `claude --resume` reopens it.
  await new Promise((res) => setTimeout(res, 400));
  return resumeTerm(sessionId);
}

// The owned session uuids to restore on cockpit open.
export function ownedTermIds() {
  return loadOwned();
}

// Reconnect every IN-MEMORY terminal after a wake from sleep (S161). Scoped to the
// `live` map — terminals actually open in THIS page — so old/closed owned sessions
// are NOT resurrected (the full owned-set resume only happens via resume-on-open on
// a genuine reopen). Returns the count reconnected. Called by main.js's wake-gap
// detector instead of a page reload (reload wiped this map and rebuilt it from the
// whole owned history — the "old sessions pop up at 0s" bug).
export function reconnectTermsAfterWake() {
  let n = 0;
  for (const c of live.values()) {
    c.reconnect();
    n++;
  }
  return n;
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

// True if the cockpit saw an Esc-cancel in this session's own terminal and the
// user hasn't submitted again since. No hook fires on interrupt, so the manifest
// stays stuck at busy; the board uses this to clear busy→idle at once. Cleared on
// the next submit (see _handleData). (S083)
export function termInterrupted(sid8) {
  const c = bySid8.get(sid8);
  return !!(c && c._interruptedAt);
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
      // A zoom-driven font change shifts the row count; fitNow alone repositions
      // nothing, so the prompt can land below the fold. Re-pin while following. (S083)
      if (c._follow) c._pinBottom();
    }
  });
}

// Refit every live terminal to its container (font unchanged). Called when the
// console column changes width — panel collapse/expand or a divider drag.
export function fitTerms() {
  for (const c of live.values()) {
    c.fitNow();
    if (c._follow) c._pinBottom(); // a width change can shift rows — re-pin or the prompt clips (S083)
  }
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
    let raf = 0, n = 0;
    const PIN_FRAMES = 48; // ~0.8s @60fps — outlasts WebView2's re-parent/fit relayout
    const pin = () => {
      if (!conn._follow) { raf = 0; return; } // user scrolled up → leave them there
      if (n < 6) conn.fitNow();               // re-fit through the early reflow frames
      conn._pinBottom();                      // ydisp → bottom AND native thumb, together
      if (n === 1 || n === 8 || n === 40) conn._diag(`open f${n}`, true); // [term-diag] → disk (issue #2)
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

// A fixed compose-bar rendered (by main.js) as a sibling BELOW <Term/>. Typing
// here pipes to the PTY via conn.submitComposed, so the terminal history above
// can be scrolled freely while you write — the in-terminal prompt is part of the
// scroll grid, this bar isn't. Enter sends, Shift+Enter inserts a newline, Esc
// cancels the running turn. It's an additive convenience for the read-back-while-
// composing case, not a replacement: interactive TUI prompts still want a click
// into the terminal. Lives outside the terminal's unscaled subtree, so it scales
// with the UI zoom like the column header does (styles.css .term-composer). (S086)
export function TermComposer({ conn }) {
  const [text, setText] = useState("");
  const taRef = useRef(null);
  const resetHeight = () => {
    const ta = taRef.current;
    if (ta) ta.style.height = "";
  };
  const submit = () => {
    if (conn.submitComposed(text)) {
      setText("");
      resetHeight();
    }
  };
  const onInput = (e) => {
    setText(e.target.value);
    const ta = e.target; // autogrow up to the CSS max-height, then the textarea scrolls
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 280) + "px";
  };
  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    } else if (e.key === "Escape") {
      e.preventDefault();
      conn.sendEsc();
      setText(""); // also clear what's typed in the bar itself
      resetHeight();
    }
  };
  return html`<div class="term-composer">
    <textarea
      ref=${taRef}
      class="term-compose-input"
      value=${text}
      onInput=${onInput}
      onKeyDown=${onKeyDown}
      placeholder=""
      rows="1"
    ></textarea>
    <button
      class="term-esc"
      onClick=${() => { conn.sendEsc(); setText(""); resetHeight(); }}
      title="cancel the running turn (Esc)"
      style="flex:none;padding:0 14px;border:1px solid var(--gold-dk);border-radius:6px;background:transparent;color:var(--ink-faint);cursor:pointer;font:inherit;"
    >esc</button>
    <button class="term-send" onClick=${submit} title="send to the terminal (Enter)">send</button>
  </div>`;
}
