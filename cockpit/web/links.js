// links.js — make file-path tokens click-to-open in the cockpit (S160). A path in
// the transcript prose or the terminal grid becomes a link; a plain click opens
// the file in its default app on the host (HTML → browser, …), Alt/Ctrl/Cmd-click
// reveals it in its folder (Explorer, file selected — "I don't want to navigate
// there by hand"). The actual open is server-side (/api/open-path → os.startfile),
// the same bridge api_open_vscode uses — so it works from the pywebview window AND
// a remote browser alike: it opens on the HOST, which is where the files live.

// Conservative path matcher, shared by the transcript linkifier and the xterm
// provider so they agree. Requires at least one `seg/` AND a dotted extension on
// the last segment (1–8 ext chars), with an optional drive prefix and an optional
// :line[:col] tail. The dotted-extension requirement keeps ratios/dates/fractions
// like `2/3/5` or `06/04` from being mistaken for paths.
const PATH_RE =
  /(?:[A-Za-z]:[\/\\]|[\/\\])?(?:[\w.\-~]+[\/\\])+[\w.\-~]*\.[A-Za-z0-9]{1,8}(?::\d+(?::\d+)?)?/g;

// Fire the backend opener. reveal=true → open the containing folder (file selected)
// instead of the file itself. Best-effort; never throws into a click handler.
export async function openPath(path, reveal) {
  if (!path) return false;
  try {
    const q = `/api/open-path?path=${encodeURIComponent(path)}${reveal ? "&reveal=1" : ""}`;
    const r = await fetch(q);
    return r.ok && (await r.json()).ok;
  } catch {
    return false;
  }
}

// Wrap path tokens in an HTML STRING (already escaped by md.js) with clickable
// anchors, without touching text inside existing tags or anchors. md.js runs this
// on its rendered output, so everything that flows through mdToHtml (agent prose,
// user/thinking bubbles) gets clickable paths inside dangerouslySetInnerHTML. The
// anchors carry no href — the global delegate below handles the click.
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
    parts[i] = parts[i].replace(
      PATH_RE,
      (m) =>
        `<a class="pathlink" data-path="${m.replace(/"/g, "&quot;")}" ` +
        `title="click to open · Alt-click to reveal in folder">${m}</a>`,
    );
  }
  return parts.join("");
}

// Register an xterm link provider so path tokens in the terminal grid are
// clickable too. xterm calls provideLinks per hovered line; we scan that line and
// hand back ranges. Built-in API — no addon/vendor file needed. Plain click opens,
// Alt/Ctrl/Cmd-click reveals.
export function registerTermLinks(term) {
  if (!term || !term.registerLinkProvider) return;
  term.registerLinkProvider({
    provideLinks(y, cb) {
      let line = null;
      try {
        line = term.buffer.active.getLine(y - 1); // y is 1-based; getLine is 0-based
      } catch {}
      if (!line) {
        cb(undefined);
        return;
      }
      const text = line.translateToString(true);
      const links = [];
      PATH_RE.lastIndex = 0;
      let m;
      while ((m = PATH_RE.exec(text)) !== null) {
        const path = m[0];
        links.push({
          range: { start: { x: m.index + 1, y }, end: { x: m.index + path.length, y } },
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
