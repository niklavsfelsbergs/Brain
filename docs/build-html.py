#!/usr/bin/env python3
"""Build a single self-contained HTML version of the docs/ tree.

Reads the markdown pages in order, rewrites inter-page links to in-page
anchors, leaves links to source files (../gielinor/..., ../cockpit/..., etc.)
as relative links (they resolve when the HTML is opened from inside the repo),
and writes one portable, offline-openable file: docs/brain-docs.html.

Regenerate after editing any docs/*.md:   python docs/build-html.py

Requires: python-markdown (pip install markdown).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("python-markdown not installed. Run: pip install markdown")

DOCS = Path(__file__).resolve().parent

# (filename, short nav label) in reading order.
PAGES = [
    ("README.md", "Index"),
    ("01-orientation.md", "01 · Orientation"),
    ("02-glossary.md", "02 · Glossary"),
    ("03-layers-and-memory.md", "03 · Layers & memory"),
    ("04-write-discipline.md", "04 · Write discipline"),
    ("05-actors-and-modes.md", "05 · Actors & modes"),
    ("06-rituals.md", "06 · Rituals"),
    ("07-communication-and-coordination.md", "07 · Communication"),
    ("08-enforcement-and-hooks.md", "08 · Enforcement & hooks"),
    ("09-cockpit.md", "09 · The cockpit"),
    ("10-dev-brain.md", "10 · The dev brain"),
    ("11-appendix.md", "11 · Appendix"),
]

PAGE_FILES = {fn for fn, _ in PAGES}


def page_anchor(filename: str) -> str:
    """docs page filename -> in-document section id."""
    stem = filename[:-3] if filename.endswith(".md") else filename
    return "page-" + stem.lower()


def gh_slugify(value: str, separator: str = "-") -> str:
    """GitHub-compatible heading slug, so HTML ids match the markdown's
    on-GitHub anchors and the hand-written #fragments resolve."""
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"\s+", separator, value)
    return value


_LINK_RE = re.compile(r"\]\(\s*(?P<target>[^)\s]+)\s*\)")
_DOCS_LINK_RE = re.compile(r"^(?:\./)?(?P<file>README\.md|\d\d-[a-z0-9-]+\.md)(?P<frag>#.*)?$")


def rewrite_links(md_text: str) -> str:
    """Rewrite links between docs pages into in-page anchors. Links pointing
    outside docs/ (source files) are left untouched."""

    def repl(m: re.Match) -> str:
        target = m.group("target")
        dm = _DOCS_LINK_RE.match(target)
        if not dm:
            return m.group(0)  # external / source link — leave as-is
        frag = dm.group("frag")
        if frag:  # link to a specific anchor within another page
            return f"]({frag})"
        return f"](#{page_anchor(dm.group('file'))})"

    return _LINK_RE.sub(repl, md_text)


def main() -> None:
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "attr_list", "sane_lists", "toc"],
        extension_configs={"toc": {"slugify": gh_slugify}},
    )

    sections, nav = [], []
    for filename, label in PAGES:
        path = DOCS / filename
        if not path.exists():
            sys.exit(f"missing page: {filename}")
        md.reset()
        body = md.convert(rewrite_links(path.read_text(encoding="utf-8")))
        anchor = page_anchor(filename)
        sections.append(f'<section id="{anchor}" class="doc-page">\n{body}\n</section>')
        nav.append(f'<a href="#{anchor}" data-target="{anchor}">{label}</a>')

    html = TEMPLATE.format(nav="\n".join(nav), content="\n\n".join(sections))
    out = DOCS / "brain-docs.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}  ({len(html):,} bytes, {len(PAGES)} pages)")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Brain — technical documentation</title>
<style>
  :root {{
    --bg:#11130f; --panel:#181b14; --ink:#e6e3d6; --mut:#9a9684; --line:#2c3024;
    --gold:#d6b24a; --gold-dim:#8c7530; --link:#cdb86a; --code-bg:#0e100b; --accent:#3f7a6a;
    --warn:#caa24a;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{
    margin:0; background:var(--bg); color:var(--ink);
    font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
  }}
  .layout {{
    display:grid;
    grid-template-columns:280px minmax(0, 1fr);
    min-height:100vh;
  }}
  /* Sidebar */
  nav {{
    position:sticky; top:0; align-self:start; height:100vh; overflow-y:auto;
    background:var(--panel); border-right:1px solid var(--line); padding:26px 18px;
  }}
  nav .brand {{ font-weight:700; letter-spacing:.04em; color:var(--gold); font-size:15px;
    margin:0 0 4px 8px; text-transform:uppercase; }}
  nav .sub {{ color:var(--mut); font-size:12px; margin:0 0 18px 8px; }}
  nav a {{
    display:block; padding:7px 10px; margin:2px 0; border-radius:6px;
    color:var(--ink); text-decoration:none; font-size:14px; border-left:2px solid transparent;
  }}
  nav a:hover {{ background:rgba(214,178,74,.08); }}
  nav a.active {{ background:rgba(214,178,74,.13); border-left-color:var(--gold); color:var(--gold); }}
  /* Content */
  main {{
    width:100%;
    max-width:920px;
    margin:0 auto;
    padding:48px 56px 120px;
  }}
  .doc-page {{ padding-bottom:40px; margin-bottom:40px; border-bottom:1px dashed var(--line); }}
  .doc-page:last-child {{ border-bottom:none; }}
  h1,h2,h3,h4 {{ line-height:1.25; font-weight:650; scroll-margin-top:24px; }}
  h1 {{ font-size:30px; color:var(--gold); margin:.2em 0 .6em; }}
  h2 {{ font-size:22px; margin:1.7em 0 .5em; padding-bottom:.25em; border-bottom:1px solid var(--line); }}
  h3 {{ font-size:17px; margin:1.4em 0 .4em; color:#d9d3bf; }}
  h4 {{ font-size:15px; margin:1.2em 0 .3em; color:var(--mut); text-transform:uppercase; letter-spacing:.03em; }}
  p {{ margin:.7em 0; }}
  a {{ color:var(--link); text-decoration:none; border-bottom:1px solid rgba(205,184,106,.25); }}
  a:hover {{ border-bottom-color:var(--link); }}
  strong {{ color:#f1eedd; }}
  ul,ol {{ padding-left:1.4em; }}
  li {{ margin:.25em 0; }}
  hr {{ border:none; border-top:1px solid var(--line); margin:2em 0; }}
  code {{ background:var(--code-bg); border:1px solid var(--line); border-radius:4px;
    padding:.1em .4em; font:13.5px/1.4 "SFMono-Regular",Consolas,"Liberation Mono",monospace; color:#d8cfa6; }}
  pre {{ background:var(--code-bg); border:1px solid var(--line); border-radius:8px;
    padding:16px 18px; overflow-x:auto; }}
  pre code {{ background:none; border:none; padding:0; color:#cfd6c4; font-size:13px; line-height:1.5; }}
  blockquote {{ margin:1.2em 0; padding:.6em 1.1em; background:rgba(63,122,106,.08);
    border-left:3px solid var(--accent); border-radius:0 6px 6px 0; color:#cdd6c8; }}
  blockquote strong {{ color:var(--warn); }}
  table {{ border-collapse:collapse; width:100%; margin:1.1em 0; font-size:14px; display:block; overflow-x:auto; }}
  th,td {{ border:1px solid var(--line); padding:8px 11px; text-align:left; vertical-align:top; }}
  th {{ background:rgba(214,178,74,.08); color:var(--gold); font-weight:600; }}
  tr:nth-child(even) td {{ background:rgba(255,255,255,.015); }}
  .topbar {{ display:none; }}
  @media (max-width:820px) {{
    .layout {{ grid-template-columns:1fr; }}
    nav {{ position:static; height:auto; border-right:none; border-bottom:1px solid var(--line); }}
    main {{ padding:28px 22px 80px; }}
  }}
</style>
</head>
<body>
<div class="layout">
  <nav>
    <p class="brand">The Brain</p>
    <p class="sub">technical documentation</p>
    {nav}
  </nav>
  <main>
    {content}
  </main>
</div>
<script>
  // Scroll-spy: highlight the nav entry for the section in view.
  const links = [...document.querySelectorAll('nav a')];
  const byId = Object.fromEntries(links.map(a => [a.dataset.target, a]));
  const obs = new IntersectionObserver((entries) => {{
    entries.forEach(e => {{
      if (e.isIntersecting) {{
        links.forEach(a => a.classList.remove('active'));
        (byId[e.target.id] || {{}}).classList?.add('active');
      }}
    }});
  }}, {{ rootMargin: '-10% 0px -80% 0px', threshold: 0 }});
  document.querySelectorAll('section.doc-page').forEach(s => obs.observe(s));
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
