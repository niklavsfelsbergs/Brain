// links.js — make file-path tokens click-to-open in the cockpit (S160). A path in
// the transcript prose or the terminal grid becomes a link; a plain click opens
// the file in its default app on the host (HTML → browser, SQL → VSCode, …),
// Alt/Ctrl/Cmd-click reveals it in its folder (Explorer, file selected — "I don't
// want to navigate there by hand"). The actual open is server-side (/api/open-path
// → os.startfile), the same bridge api_open_vscode uses — so it works from the
// pywebview window AND a remote browser alike: it opens on the HOST, where the
// files live.
//
// Reliability pass (S270): the terminal grid had two "sometimes it opens, sometimes
// it doesn't" gaps — (1) a long path WRAPPED across two grid rows was only ever seen
// one row at a time, so the matcher got a fragment and made no link; (2) a path
// printed without a folder segment (a bare `name.ext`) wasn't matched at all. Both
// fixed below: the terminal provider now rebuilds the full wrapped logical line, and
// uses a looser matcher that also accepts a whitelisted bare filename. A rejected
// open (moved/renamed/outside-repo) now flashes instead of failing silently, so a
// dead click no longer looks identical to "there was no link there."

// Conservative path matcher for the TRANSCRIPT (HTML prose). Requires at least one
// `seg/` AND a dotted extension on the last segment (1–8 ext chars), with an
// optional drive prefix and an optional :line[:col] tail. The dotted-extension +
// mandatory-slash requirement keeps ratios/dates/fractions like `2/3/5` or `06/04`,
// and English prose like `Node.js`, from being mistaken for paths. Prose is
// English-dense, so the transcript stays strict (slash-only) on purpose.
const PATH_RE =
  /(?:[A-Za-z]:[\/\\]|[\/\\])?(?:[\w.\-~]+[\/\\])+[\w.\-~]*\.[A-Za-z0-9]{1,8}(?::\d+(?::\d+)?)?/g;

// A bare `filename.ext` with NO folder segment — only enabled for the TERMINAL grid,
// where output is mostly real filenames rather than prose. Gated two ways to stay
// quiet: a whitelist of code/doc/data extensions (so `e.g`, `claude.ai`, `1.5` don't
// match), and a lookbehind so it never starts inside another token (a slash-path's
// last segment is already covered by PATH_RE). Accepted residual: a prose token that
// is literally `Word.<whitelisted-ext>` (e.g. "Node.js") still matches — terminal
// prose rarely contains those, and a mis-click just flashes "not found" rather than
// opening anything, so the false-negative cure (paths that DON'T open) wins the trade.
const BARE_EXT =
  "html?|sql|md|markdown|py|ipynb|js|mjs|cjs|ts|tsx|jsx|json|jsonl|csv|tsv|parquet|" +
  "css|scss|txt|log|sh|bash|ps1|ya?ml|toml|ini|cfg|env|xml|pdf|png|jpe?g|gif|svg|webp|" +
  "go|rs|java|kt|c|h|cpp|hpp|rb|php|r|sqlx|duckdb|db|xlsx?|docx?|pptx?";
const BARE_RE = new RegExp(
  `(?<![\\w/\\\\.~-])[\\w.\\-~]+\\.(?:${BARE_EXT})(?::\\d+(?::\\d+)?)?(?![\\w.])`,
);

// The terminal matcher: a full slash-path OR a bare whitelisted filename. Slash-form
// is listed first, so a complete path matches as one token (its last segment is never
// re-matched as a bare name). Rebuilt fresh (global) for the per-line scan.
const TERM_PATH_RE = new RegExp(`${PATH_RE.source}|${BARE_RE.source}`, "g");

// Fire the backend opener. reveal=true → open the containing folder (file selected)
// instead of the file itself. Best-effort; never throws into a click handler. On a
// backend rejection (404 moved/renamed, 403 outside repo) it flashes a transient
// notice so the failure is visible rather than indistinguishable from no-link.
export async function openPath(path, reveal) {
  if (!path) return false;
  try {
    const q = `/api/open-path?path=${encodeURIComponent(path)}${reveal ? "&reveal=1" : ""}`;
    const r = await fetch(q);
    let body = {};
    try {
      body = await r.json();
    } catch {}
    if (r.ok && body.ok) return true;
    _flash(`couldn't open ${_short(path)} — ${body.error || `HTTP ${r.status}`}`);
    return false;
  } catch (e) {
    _flash(`couldn't open ${_short(path)} — ${(e && e.message) || "network error"}`);
    return false;
  }
}

// Last path segment (minus any :line tail), for a compact flash label.
function _short(p) {
  const seg = String(p).replace(/:\d+(?::\d+)?$/, "").split(/[\/\\]/).pop();
  return seg || p;
}

// Minimal transient toast for click-to-open failures. One reused element, bottom-
// right, auto-hides. Best-effort; no-op outside a document.
function _flash(msg) {
  if (typeof document === "undefined" || !document.body) return;
  let host = document.getElementById("pathlink-flash");
  if (!host) {
    host = document.createElement("div");
    host.id = "pathlink-flash";
    document.body.appendChild(host);
  }
  host.textContent = msg;
  host.classList.add("show");
  clearTimeout(host._t);
  host._t = setTimeout(() => host.classList.remove("show"), 2400);
}

// Wrap path tokens in an HTML STRING (already escaped by md.js) with clickable
// anchors, without touching text inside existing tags or anchors. md.js runs this
// on its rendered output, so everything that flows through mdToHtml (agent prose,
// user/thinking bubbles) gets clickable paths inside dangerouslySetInnerHTML. The
// anchors carry no href — the global delegate below handles the click. Uses the
// strict slash-only PATH_RE (prose is English-dense).
export function linkifyPaths(htmlStr) {
  if (!htmlStr) return htmlStr;
  const parts = htmlStr.split(/(<[^>]+>)/);
  let inAnchor = 0; // never linkify inside an existing <a>…</a>
  for (let i = 0; i < parts.length; i++) {
    if (i % 2 === 1) {
      const tag = parts[i];
      if (/^<a\b/i.test(tag)) inAnchor++;
      else if (/^<\/a>/i.test(tag)) inAnchor = Math.max(0, inAnchor - 1);
      continue;
    }
    if (inAnchor > 0 || !parts[i]) continue;
    PATH_RE.lastIndex = 0;
    parts[i] = parts[i].replace(
      PATH_RE,
      (m) =>
        `<a class="pathlink" data-path="${m.replace(/"/g, "&quot;")}" ` +
        `title="click to open · Alt-click to reveal in folder">${m}</a>`,
    );
  }
  return parts.join("");
}

// Reconstruct the full (possibly wrapped) logical line that contains 0-based buffer
// row `row`. xterm wraps a long line across consecutive rows, each continuation
// flagged isWrapped; a single getLine sees only one row, so a path that spills past
// the right edge is otherwise unlinkable. Returns the concatenated UNTRIMMED text
// (each row exactly `cols` wide, so a match offset maps cleanly back to row/col) and
// the 0-based index of the row where the logical line begins.
function logicalLine(buf, row, cols) {
  let first = row;
  while (first > 0) {
    const ln = buf.getLine(first);
    if (ln && ln.isWrapped) first--;
    else break;
  }
  let text = "";
  const len = buf.length;
  for (let r = first; r < len; r++) {
    const ln = buf.getLine(r);
    if (!ln) break;
    if (r > first && !ln.isWrapped) break;
    text += ln.translateToString(false); // untrimmed → exactly `cols` chars/row
  }
  return { text, first };
}

// Register an xterm link provider so path tokens in the terminal grid are clickable
// too. xterm calls provideLinks per hovered buffer line (y is 1-based, matching
// getLine(y-1)). We rebuild the wrapped logical line, scan it, and hand back ranges
// that may span multiple rows. Plain click opens, Alt/Ctrl/Cmd-click reveals.
export function registerTermLinks(term) {
  if (!term || !term.registerLinkProvider) return;
  term.registerLinkProvider({
    provideLinks(y, cb) {
      const buf = term.buffer && term.buffer.active;
      if (!buf) {
        cb(undefined);
        return;
      }
      const cols = term.cols || 80;
      let hovered = null;
      try {
        hovered = buf.getLine(y - 1);
      } catch {}
      if (!hovered) {
        cb(undefined);
        return;
      }
      const { text, first } = logicalLine(buf, y - 1, cols);
      const links = [];
      TERM_PATH_RE.lastIndex = 0;
      let m;
      while ((m = TERM_PATH_RE.exec(text)) !== null) {
        const path = m[0];
        if (!path) {
          TERM_PATH_RE.lastIndex++; // guard against a zero-width match looping
          continue;
        }
        const startOff = m.index;
        const endOff = m.index + path.length - 1;
        const sRow = first + Math.floor(startOff / cols);
        const eRow = first + Math.floor(endOff / cols);
        // Only surface links that intersect the hovered row, so the same wrapped
        // line isn't multiply-decorated as the cursor moves across its rows.
        if (y < sRow + 1 || y > eRow + 1) continue;
        links.push({
          range: {
            start: { x: (startOff % cols) + 1, y: sRow + 1 },
            end: { x: (endOff % cols) + 1, y: eRow + 1 },
          },
          text: path,
          activate: (ev) => openPath(path, ev.altKey || ev.ctrlKey || ev.metaKey),
        });
      }
      cb(links.length ? links : undefined);
    },
  });
}

// One document-level delegate handles every .pathlink in the page (transcript,
// feed, console — anywhere mdToHtml output lands), installed once on import. The
// anchors have no href, so preventDefault has nothing to undo; a plain click never
// disturbs a text selection (only a no-drag click reaches here).
let _installed = false;
function _installGlobal() {
  if (_installed || typeof document === "undefined") return;
  _installed = true;
  document.addEventListener("click", (e) => {
    const a = e.target && e.target.closest && e.target.closest("a.pathlink");
    if (!a) return;
    e.preventDefault();
    openPath(a.dataset.path, e.altKey || e.ctrlKey || e.metaKey);
  });
}
_installGlobal();
