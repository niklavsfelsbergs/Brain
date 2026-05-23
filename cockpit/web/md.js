// Minimal, safe markdown → HTML. Escapes first, then a small block + inline subset.

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inline(s) {
  return s
    .replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
}

export function mdToHtml(text) {
  const lines = esc(text || "").split("\n");
  const out = [];
  let inCode = false;
  let codeBuf = [];
  let listBuf = null;
  const flushList = () => {
    if (listBuf) {
      out.push("<ul>" + listBuf.map((li) => `<li>${inline(li)}</li>`).join("") + "</ul>");
      listBuf = null;
    }
  };
  for (const ln of lines) {
    if (/^```/.test(ln)) {
      if (inCode) {
        out.push(`<pre><code>${codeBuf.join("\n")}</code></pre>`);
        codeBuf = [];
        inCode = false;
      } else {
        flushList();
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      codeBuf.push(ln);
      continue;
    }
    const h = ln.match(/^(#{1,3})\s+(.*)$/);
    if (h) {
      flushList();
      out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`);
      continue;
    }
    const li = ln.match(/^\s*[-*]\s+(.*)$/);
    if (li) {
      (listBuf = listBuf || []).push(li[1]);
      continue;
    }
    if (/^\s*---+\s*$/.test(ln)) {
      flushList();
      out.push("<hr>");
      continue;
    }
    const q = ln.match(/^>\s?(.*)$/);
    if (q) {
      flushList();
      out.push(`<blockquote>${inline(q[1])}</blockquote>`);
      continue;
    }
    if (ln.trim() === "") {
      flushList();
      continue;
    }
    flushList();
    out.push(`<p>${inline(ln)}</p>`);
  }
  if (inCode) out.push(`<pre><code>${codeBuf.join("\n")}</code></pre>`);
  flushList();
  return out.join("");
}
