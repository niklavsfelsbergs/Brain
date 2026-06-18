#!/usr/bin/env python3
"""jebrim_usage.py — premium one-page snapshot of how Jebrim is *used*.

v2 (value-first). Rebuilt from the brain-recon findings: the old commit/quest/
file-count panels measured the brain repo's bookkeeping by-product, not the work.
This version leads with the value story and carries two health diagnostics.

Panels:
  - headline stats (projects, deliverables, sub-agents, knowledge, lessons, days)
  - PROJECT ARCS — work grouped into real multi-session projects (span, sessions,
    sub-agents, flagship deliverable); the unit the work actually happens in
  - DOMAINS — depth x freshness (rich/fresh vs thin/stale), not a domain count
  - JOB-TO-BE-DONE mix — the recurring ask-shapes (reconcile / model / report / …)
  - DELIVERABLES — named outputs tagged by the repo they live in (most are NOT
    in the brain repo — the brain holds the by-product)
  - LESSON RECURRENCE (health) — confirmed lessons that fire AGAIN as fresh
    mistakes; high recurrence = the lesson isn't sticking
  - GRADUATION (health) — quests graduated/week + the honest in-progress split
    (closed-but-ungraduated vs genuinely live) + days since last alch

Static: regenerate to refresh. Reads only; writes a single HTML file. Stdlib only.
Curated bits (flagship deliverables, repo tags) are marked CURATED — they can't be
derived because the real deliverables live in other repos the brain doesn't track.

Usage:
    python tools/jebrim_usage.py [--out card.html] [--open] [--data]
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import webbrowser
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JEBRIM = ROOT / "gielinor" / "players" / "jebrim"
QC = JEBRIM / "quest-log" / "completed"
QP = JEBRIM / "quest-log" / "in-progress"
REL = "gielinor/players/jebrim"

# ── palette (premium dark + gold foil) ──────────────────────────────────────
GOLD, GOLD_HI, GOLD_LO = "#e8b75a", "#ffe2a0", "#b07d27"
INK, MUTED, FAINT = "#ece3cf", "#9a8d6f", "#6b6149"
FRESH, WARM, STALE = "#8fce5a", "#e8b03a", "#7d7256"
REPEAT = "#e0683f"  # recurrence highlight
# distinct categorical hues (job-mix — must visibly separate)
CAT = {
    "Reconcile": "#5ba3c9", "Model / build": "#e8b75a", "Report / present": "#c98f5b",
    "Investigate": "#d96a6a", "Audit / verify": "#b07fc9", "Research": "#7fae5a",
    "Housekeeping": "#8a8270",
}

# ── project + classification definitions ────────────────────────────────────
# first-match priority (specific -> broad). (name, regex, kind, flagship[CURATED])
PROJECT_DEFS = [
    ("Housekeeping & tooling",
     r"alch|_g\d_|bankstand|respawn|rulebook|\bskill\b|ritual|vocab|readiness|"
     r"run-yourself|session-close|hygiene|scaffold",
     "tooling", "shipping-agent training · alching · rulebook revamps"),
    ("UPS retention",
     r"retention|cell-grain|parcel-grain",
     "client", "UPS retention curve (parcel + cell grain)"),
    ("US / LucaNet recon",
     r"lucanet|quickbooks|us-entity|\bpcs\b|reconcil|us-mart|us-cost",
     "client", "3-way US invoice ↔ mart ↔ ledger reconciliation"),
    ("SCM dashboard",
     r"\bscm\b|dashboard|breakdown|resizable|shift-tab|nextjs|onta?rac|"
     r"\bcsv\b|deviation|avgcost|\bbench\b|completeness|cutover|gold-cutover",
     "client", "live SCM cost dashboard — perf/crash/label/column fixes shipped"),
    ("EU Tender 2026",
     r"tender|hermes|re-?rat|rerate|routing-report|decision-report|annualiz|"
     r"no-hermes|savings-decomp|portfolio-scor|guell|maersk|austrian|\bgri\b",
     "client", "€1.9M savings final report + 9 carrier rate engines"),
    ("Shipping mart & agent",
     r"\bmart\b|shipping-agent|shipping_mart|ttyd|talk-to-your|coverage|"
     r"oversized|dimension|destination|gap-analysis|merchone|picanova|prodorder|"
     r"\bdq\b|lineage|temp-track|order-?item",
     "tooling", "gold shipping_mart cutover + the shipping-agent"),
    ("Carrier cost & contracts",
     r"carrier|rate-card|fuel|\bdpd\b|\bgls\b|\bdhl\b|fedex|yodel|\bups\b|"
     r"invoice|\bfif\b|orwo|contract|expected-cost|truck|linehaul|passthrough",
     "client", "per-carrier rate cards, fuel mechanics, invoice-DQ reconciliation"),
    ("Foundations / infra",
     r"bi-etl|bi_etl|\bnfe\b|redshift|\bpipeline\b|\betl\b|orient|repo-orient|"
     r"clickup|scaffold|template|connection|\bprobe\b|\bwalk\b|harness|census|"
     r"sql_pipeline|api-and-data|frontend",
     "tooling", "repo orientation, ETL/Redshift recon, SQL+API scaffolding"),
]
PROJECT_FALLBACK = ("Other / one-off", None, "client", "assorted one-off pulls")

# CURATED — the recurring ask-shapes, frequency-ordered from the brain-recon
# session read (~22 sessions). Values are approximate % shares, not file counts.
JOB_CURATED = {
    "Reconcile": 26, "Model / build": 22, "Report / present": 18,
    "Investigate": 16, "Audit / verify": 10, "Research": 4, "Housekeeping": 4,
}

# job-to-be-done classifier (kept for reference; display uses JOB_CURATED).
JOB_DEFS = [
    ("Audit / verify", r"audit|red-team|verif|trust-gate|defensib|limit-test|"
                       r"security|readiness|sanity"),
    ("Reconcile", r"reconcil|vs-|-vs-|delta|disagree|mismatch|lineage|trace|"
                  r"cross-check|equivocation|grain"),
    ("Report / present", r"report|summary|deck|pptx|management|final|present|board|"
                         r"annualiz|headline"),
    ("Investigate", r"fix|bug|debug|crash|oom|503|root-cause|why|investigat|"
                    r"false|regress|perf|staleness"),
    ("Model / build", r"engine|\brate\b|model|re-?rat|curve|retention|savings|build|"
                      r"pipeline|etl|cutover|\bsql\b|matrix|multiplier|baseline"),
    ("Research", r"research|market|sketch|study|concept|rateproof|prep|survey"),
    ("Housekeeping", r"alch|_g\d_|bankstand|respawn|rulebook|ritual|vocab|harvest|"
                     r"close-session|hygiene|scaffold"),
]

# recurrence families (first match). (name, regex)
FAMILY_DEFS = [
    ("Act only when asked", r"act.?only|go-ahead|merited|question is not|asked to|"
                            r"not a go|don'?t.{0,6}act"),
    ("Lens / grain / population", r"\blens\b|grain|population|currency|subset|"
                                  r"order-month|invoice-date|date lens|blend"),
    ("Close the blast radius", r"blast|all tabs|sibling|regress|enumerate|downstream|"
                               r"chain-regen|both ways|companion"),
    ("Verify the source / basis", r"verif|\bsource\b|inherited|provenance|populated|"
                                  r"rate-type|ground.?truth|\bbasis\b|measurement|"
                                  r"borrowed|fixture|comment"),
]
RECUR_RE = re.compile(
    r"recurr|recurred|recurs|\btwice\b|one-off|\bS145\b|\bS160\b|keeps happening|"
    r"again caught|not the first", re.I)
GRAD_MARK_RE = re.compile(
    r"CLOSING|no pending|nothing pending|shipped|harvest done|graduat|wrapped|"
    r"hand-?off|close-?ritual|moved to completed|posted|deliverable.{0,12}(done|ship)|"
    r"session closed|\bdone\b|✅|✓|complete", re.I)


def sh(args: list[str]) -> str:
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout
    except Exception:
        return ""


def count_md(path: Path, recursive=False) -> int:
    if not path.exists():
        return 0
    it = path.rglob("*.md") if recursive else path.glob("*.md")
    return sum(1 for p in it if not p.name.startswith("_"))


def parse_digest(fp: Path) -> dict:
    pats, corp, cur = [], [], None
    text = fp.read_text(encoding="utf-8", errors="replace").splitlines()
    if not text or text[0].strip() != "---":
        return {"patterns": pats, "corpus": corp}
    for line in text[1:]:
        if line.strip() == "---":
            break
        if line.startswith("patterns:"):
            cur = pats; continue
        if line.startswith("corpus:"):
            cur = corp; continue
        if line and not line.startswith(" ") and ":" in line:
            cur = None; continue
        if cur is not None and line.lstrip().startswith("- "):
            cur.append(line.lstrip()[2:].strip())
    return {"patterns": pats, "corpus": corp}


def git_creation_dates(relpath: str) -> dict:
    """path -> first-seen (added) date, in one git pass."""
    out = sh(["git", "log", "--diff-filter=A", "--date=short",
              "--format=@%ad", "--name-only", "--", relpath])
    created, cur = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            cur = line[1:].strip()
        elif line.strip() and cur:
            created.setdefault(line.strip(), cur)  # first add wins
    return created


def git_last_date(paths: list[str]):
    if not paths:
        return None
    out = sh(["git", "log", "-1", "--format=%ad", "--date=short", "--", *paths]).strip()
    try:
        return dt.date.fromisoformat(out) if out else None
    except ValueError:
        return None


def first_match(text: str, defs):
    for entry in defs:
        name, rgx = entry[0], entry[1]
        if rgx and re.search(rgx, text, re.I):
            return name
    return None


def session_token(stem: str) -> str:
    m = re.match(r"([SBG]-?\d+|OPEN|recon|template|scaffold|connection)", stem, re.I)
    return m.group(1).upper() if m else stem.split("_")[0].upper()


def collect() -> dict:
    today = dt.date.today()
    deleg_re = re.compile(r"_[dgp]\d{1,2}_")

    # ---- creation dates (one git pass over the quest-log) ----
    created = git_creation_dates(f"{REL}/quest-log/")

    def cdate(p: Path):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        d = created.get(rel)
        if d:
            return dt.date.fromisoformat(d)
        m = re.search(r"(20\d\d-\d\d-\d\d)", p.stem)  # filename date fallback
        return dt.date.fromisoformat(m.group(1)) if m else None

    comp = [p for p in QC.glob("*.md") if not p.name.startswith("_")]
    prog = [p for p in QP.glob("*.md") if not p.name.startswith("_")]
    all_q = comp + prog

    # ---- project arcs ----
    proj = {}
    order = [d[0] for d in PROJECT_DEFS] + [PROJECT_FALLBACK[0]]
    meta = {d[0]: {"kind": d[2], "flag": d[3]} for d in PROJECT_DEFS}
    meta[PROJECT_FALLBACK[0]] = {"kind": PROJECT_FALLBACK[2], "flag": PROJECT_FALLBACK[3]}
    for nm in order:
        proj[nm] = {"name": nm, "count": 0, "sessions": set(), "agents": 0,
                    "dates": [], **meta[nm]}
    for p in all_q:
        nm = first_match(p.stem, PROJECT_DEFS) or PROJECT_FALLBACK[0]
        e = proj[nm]
        e["count"] += 1
        e["sessions"].add(session_token(p.stem))
        if deleg_re.search(p.stem):
            e["agents"] += 1
        d = cdate(p)
        if d:
            e["dates"].append(d)
    projects = []
    for nm in order:
        e = proj[nm]
        if e["count"] == 0:
            continue
        e["first"] = min(e["dates"]) if e["dates"] else None
        e["last"] = max(e["dates"]) if e["dates"] else None
        e["nsess"] = len(e["sessions"])
        projects.append(e)
    projects.sort(key=lambda x: x["count"], reverse=True)
    client_files = sum(e["count"] for e in projects if e["kind"] == "client")
    tooling_files = sum(e["count"] for e in projects if e["kind"] == "tooling")

    # ---- job-to-be-done mix ----
    # CURATED from the brain-recon session read (slugs are topic-named not verb-named,
    # so an auto-count from filenames is unreliable; this encodes the recon's
    # frequency-ordered finding across ~22 sessions read).
    job = dict(JOB_CURATED)

    # ---- domains (depth x freshness) ----
    quest_names = [p.name.lower() for p in all_q]
    note_paths = [str(p.relative_to(JEBRIM)).lower()
                  for p in (JEBRIM / "bank" / "notes").rglob("*.md")]
    haystack = quest_names + note_paths
    domains = []
    for fp in sorted((JEBRIM / "bank" / "domains").glob("*.md")):
        if fp.name.startswith("_"):
            continue
        m = parse_digest(fp)
        pats = [x.lower() for x in m["patterns"]]
        hits = sum(1 for h in haystack if any(pt in h for pt in pats)) if pats else 0
        size = hits + len(m["corpus"])
        cp = [f"{REL}/{c}" for c in m["corpus"]] or [str(fp.relative_to(ROOT))]
        last = git_last_date(cp) or git_last_date([str(fp.relative_to(ROOT))])
        age = (today - last).days if last else None
        domains.append({"name": fp.stem, "size": size,
                        "corpus": len(m["corpus"]), "age": age})
    domains.sort(key=lambda d: d["size"], reverse=True)

    # ---- work rhythm (quests completed per week) ----
    def week_key(d):
        return d - dt.timedelta(days=d.weekday())
    grad = Counter()
    for p in comp:
        d = cdate(p)
        if d:
            grad[week_key(d)] += 1
    grad_weeks = [(w, grad[w]) for w in sorted(grad)]

    # ---- knowledge moat growth (cumulative notes + lessons by week) ----
    def cumulative(relpath):
        cd = git_creation_dates(relpath)
        dates = sorted(dt.date.fromisoformat(v) for v in cd.values())
        series, run = {}, 0
        for d in dates:
            run += 1
            series[week_key(d)] = run
        return series
    notes_series = cumulative(f"{REL}/bank/notes/")
    less_series = cumulative(f"{REL}/examine/confirmed/")

    # ---- current focus: per-project recency (newest file touched) ----
    focus = []
    for e in projects:
        if e["name"] == PROJECT_FALLBACK[0] or not e["last"]:
            continue
        focus.append({"name": e["name"], "age": (today - e["last"]).days,
                      "nsess": e["nsess"], "kind": e["kind"]})
    focus.sort(key=lambda f: f["age"])

    # ---- headline counts ----
    commits = int(sh(["git", "rev-list", "--count", "HEAD", "--", REL]).strip() or "0")
    # sessions = wrap-ups performed. SNNN is allocated at close (one per close
    # ritual; a reopened session gets a fresh SNNN each close), so distinct SNNN
    # across the quest-log = total wrap-ups all-time. Cross-checks vs comms
    # CLOSING entries (159, but comms only began ~05-27 so it misses early ones).
    snn = set()
    for p in all_q:
        for num in re.findall(r"(?<![A-Za-z])[Ss](\d{1,4})(?![\dA-Za-z])", p.stem):
            snn.add(int(num))
    sessions = len(snn)
    parsed = sorted(d for d in (cdate(p) for p in all_q) if d)
    born = parsed[0] if parsed else today
    active_days = len(set(parsed))

    # quests = TOP-LEVEL quests; sub-agent traces (_d1_/_g1_/_p1_) are fan-out
    # WITHIN a session, not independent quests — counting them made quests > sessions.
    comp_parent = sum(1 for p in comp if not deleg_re.search(p.stem))
    prog_parent = sum(1 for p in prog if not deleg_re.search(p.stem))
    sub_quests = sum(1 for p in comp + prog if deleg_re.search(p.stem))

    return dict(
        today=today, born=born, lifespan=(today - born).days, active_days=active_days,
        projects=projects, client_files=client_files, tooling_files=tooling_files,
        job=job, domains=domains, grad_weeks=grad_weeks,
        notes_series=notes_series, less_series=less_series, focus=focus,
        in_progress=prog_parent, completed=comp_parent, sub_quests=sub_quests,
        commits=commits, sessions=sessions,
        notes=count_md(JEBRIM / "bank" / "notes", recursive=True),
        lessons=count_md(JEBRIM / "examine" / "confirmed"),
        n_projects=len([p for p in projects if p["name"] != PROJECT_FALLBACK[0]]),
    )


# CURATED — flagship deliverables (name, repo, project). The brain doesn't track
# cross-repo outputs; this is hand-maintained from the quest-log record.
DELIVERABLES = [
    ("Shipping mart → gold cutover", "bi-analytics", "Shipping mart & agent"),
    ("shipping_data_mart_v1 gap analysis (HTML)", "brain→ETL", "Shipping mart & agent"),
    ("EU Tender — 9 carrier rate engines", "NFE", "EU Tender 2026"),
    ("EU Tender — full-year cost matrix (25.8M rows)", "NFE", "EU Tender 2026"),
    ("EU Tender — management deck + final reports", "NFE", "EU Tender 2026"),
    ("EU Tender — 80-agent red-team audit", "brain", "EU Tender 2026"),
    ("Shipping-savings re-rating engine (trust-gated)", "NFE", "Carrier cost"),
    ("FIF monthly report skill (UPS ORWO)", "NFE", "Carrier cost"),
    ("SCM dashboard fixes (perf/crash/labels/cols)", "picanova/bi-analytics", "SCM dashboard"),
    ("UPS retention curve (parcel + cell grain)", "NFE", "UPS retention"),
    ("RateProof business concept + market research", "brain", "Strategy"),
]


# ── SVG / HTML builders ─────────────────────────────────────────────────────
def stat(value, label):
    return f'<div class="stat"><div class="v">{value}</div><div class="l">{label}</div></div>'


def build_arcs(projects):
    """Aligned magnitude bars (HTML) — all start at the left, length = sessions,
    color = client/system, span as readable text. Sorted biggest-first."""
    if not projects:
        return ""
    rows = []
    top = max(p["nsess"] for p in projects) or 1

    def fmt(d):
        return d.strftime("%b ") + str(d.day) if d else "—"
    for p in sorted(projects, key=lambda p: p["nsess"], reverse=True):
        w = max(4, round(100 * p["nsess"] / top))
        span = f'{fmt(p["first"])} – {fmt(p["last"])}'
        rows.append(
            f'<div class="prow">'
            f'<div class="plabel"><div class="pname">{p["name"]}</div>'
            f'<div class="pflag">{p["flag"]}</div></div>'
            f'<div class="pbarwrap"><div class="pbar {p["kind"]}" style="width:{w}%"></div></div>'
            f'<div class="pmeta"><b>{p["nsess"]}</b> sessions<span>{span}</span></div>'
            f'</div>')
    return f'<div class="arcs">{"".join(rows)}</div>'


def svg_domains(domains, maxw=250):
    if not domains:
        return ""
    top = max(d["size"] for d in domains) or 1
    rowh, labw = 29, 120
    rows = []
    for i, d in enumerate(domains):
        y = i * rowh
        bw = max(3, int(maxw * d["size"] / top))
        age = d["age"]
        dot, lab = ((FRESH, f"{age}d") if age is not None and age <= 4 else
                    (WARM, f"{age}d") if age is not None and age <= 10 else
                    (STALE, f"{age}d" if age is not None else "—"))
        rows.append(
            f'<text x="0" y="{y + 16}" fill="{INK}" font-size="12.5" '
            f'font-family="Inter,sans-serif">{d["name"]}</text>'
            f'<rect x="{labw}" y="{y + 5}" width="{maxw}" height="15" rx="4" '
            f'fill="#ffffff" fill-opacity="0.05"/>'
            f'<rect x="{labw}" y="{y + 5}" width="{bw}" height="15" rx="4" fill="url(#goldbar)"/>'
            f'<text x="{labw + bw + 7}" y="{y + 16}" fill="{GOLD_HI}" font-size="11" '
            f'font-family="Inter,sans-serif" font-weight="600">{d["size"]}</text>'
            f'<circle cx="{labw + maxw + 38}" cy="{y + 12}" r="5" fill="{dot}"/>'
            f'<text x="{labw + maxw + 48}" y="{y + 16}" fill="{MUTED}" font-size="10" '
            f'font-family="Inter,sans-serif">{lab}</text>')
    h = len(domains) * rowh
    return (f'<svg width="{labw + maxw + 88}" height="{h}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="goldbar" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{GOLD_LO}"/><stop offset="1" stop-color="{GOLD_HI}"/>'
            f'</linearGradient></defs>{"".join(rows)}</svg>')


def svg_jobmix(job, w=420):
    total = sum(job.values()) or 1
    items = sorted(job.items(), key=lambda kv: kv[1], reverse=True)
    segs, lx = [], 0
    for name, val in items:
        sw = w * val / total
        segs.append(f'<rect x="{lx:.1f}" y="0" width="{sw:.1f}" height="22" '
                    f'fill="{CAT.get(name, MUTED)}"><title>{name}: {val} '
                    f'({100 * val / total:.0f}%)</title></rect>')
        lx += sw
    bar = (f'<svg width="{w}" height="22" xmlns="http://www.w3.org/2000/svg">'
           f'<clipPath id="rb"><rect width="{w}" height="22" rx="5"/></clipPath>'
           f'<g clip-path="url(#rb)">{"".join(segs)}</g></svg>')
    legend = "".join(
        f'<div class="leg"><span class="dot" style="background:{CAT.get(n, MUTED)}"></span>'
        f'<span class="ln">{n}</span><span class="lv">{v}</span>'
        f'<span class="lp">{100 * v / total:.0f}%</span></div>'
        for n, v in items)
    return bar + f'<div class="legends">{legend}</div>'


def svg_focus(focus):
    """current focus — projects by recency; active (<=14d) bright, dormant dimmed."""
    if not focus:
        return ""
    rows = []
    for f in focus:
        age = f["age"]
        active = age <= 14
        dot = (FRESH if age <= 4 else WARM if age <= 14 else STALE)
        agelab = ('today' if age == 0 else f'{age}d ago') if active else 'dormant'
        op = "1" if active else "0.5"
        rows.append(
            f'<div class="frow" style="opacity:{op}">'
            f'<span class="fdot" style="background:{dot}"></span>'
            f'<span class="fname">{f["name"]}</span>'
            f'<span class="fsess">{f["nsess"]} sess</span>'
            f'<span class="fage">{agelab}</span></div>')
    return f'<div class="focus">{"".join(rows)}</div>'


def svg_growth(notes_series, less_series, born, today, notes_total, lessons_total,
               w=440, h=140):
    pad_l, pad_b, pad_t = 6, 22, 14
    start = born - dt.timedelta(days=born.weekday())
    weeks = []
    cur = start
    while cur <= today:
        weeks.append(cur)
        cur += dt.timedelta(days=7)
    if len(weeks) < 2:
        weeks.append(start + dt.timedelta(days=7))
    top = max(notes_total, lessons_total, 1)

    def fill(series, total):
        out, run = [], 0
        for wk in weeks:
            run = series.get(wk, run)
            out.append(run)
        out[-1] = total  # pin endpoint to the true working-tree count
        return out

    def poly(vals, color, label, lastv):
        n = len(weeks)
        pts = []
        for i, v in enumerate(vals):
            x = pad_l + (w - pad_l - 80) * i / max(1, n - 1)
            y = (h - pad_b) - (h - pad_b - pad_t) * v / top
            pts.append(f"{x:.1f},{y:.1f}")
        endx = pad_l + (w - pad_l - 80)
        endy = (h - pad_b) - (h - pad_b - pad_t) * vals[-1] / top
        return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
                f'stroke-width="2.5" stroke-linejoin="round"/>'
                f'<circle cx="{endx:.1f}" cy="{endy:.1f}" r="3.5" fill="{color}"/>'
                f'<text x="{endx + 8:.1f}" y="{endy + 4:.1f}" fill="{color}" '
                f'font-size="12" font-weight="700" font-family="Inter,sans-serif">'
                f'{label} {vals[-1]}</text>')
    nv, lv = fill(notes_series, notes_total), fill(less_series, lessons_total)
    base = (h - pad_b)
    axis = (f'<line x1="{pad_l}" y1="{base}" x2="{w - 80}" y2="{base}" '
            f'stroke="{FAINT}" stroke-opacity="0.4"/>'
            f'<text x="{pad_l}" y="{h - 6}" fill="{MUTED}" font-size="9" '
            f'font-family="Inter,sans-serif">{born.strftime("%b ") + str(born.day)}</text>'
            f'<text x="{w - 80}" y="{h - 6}" fill="{MUTED}" font-size="9" text-anchor="end" '
            f'font-family="Inter,sans-serif">now</text>')
    return (f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">{axis}'
            f'{poly(lv, GOLD_HI, "lessons", lv[-1])}'
            f'{poly(nv, "#8fb0d0", "notes", nv[-1])}</svg>')


def svg_grad(grad_weeks, w=440, h=128):
    if not grad_weeks:
        return ""
    top = max(v for _, v in grad_weeks) or 1
    n = len(grad_weeks)
    bw = max(14, min(46, (w - 20) // max(1, n) - 8))
    gap = ((w - 20) - bw * n) / max(1, n)
    bars = []
    for i, (wk, v) in enumerate(grad_weeks):
        bh = int((h - 44) * v / top)  # reserve 16px top for the value label
        x = 10 + i * (bw + gap)
        y = h - 22 - bh
        bars.append(
            f'<rect x="{x:.0f}" y="{y}" width="{bw}" height="{bh}" rx="3" fill="url(#gg)">'
            f'<title>week of {wk}: {v} quests completed</title></rect>'
            f'<text x="{x + bw / 2:.0f}" y="{y - 4}" fill="{GOLD_HI}" font-size="10" '
            f'text-anchor="middle" font-family="Inter,sans-serif">{v}</text>'
            f'<text x="{x + bw / 2:.0f}" y="{h - 8}" fill="{MUTED}" font-size="9" '
            f'text-anchor="middle" font-family="Inter,sans-serif">{wk.strftime("%b ") + str(wk.day)}</text>')
    return (f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="gg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{FRESH}"/><stop offset="1" stop-color="#5a8a36"/>'
            f'</linearGradient></defs>{"".join(bars)}</svg>')


def render(d) -> str:
    named = [p for p in d["projects"] if p["name"] != PROJECT_FALLBACK[0]]
    other_ct = sum(p["count"] for p in d["projects"] if p["name"] == PROJECT_FALLBACK[0])
    arcs = build_arcs(named)
    doms = svg_domains(d["domains"])
    jobm = svg_jobmix(d["job"])
    cf, tf = d["client_files"], d["tooling_files"]
    ct_tot = cf + tf or 1
    focus = svg_focus(d["focus"])
    grad = svg_grad(d["grad_weeks"])
    growth = svg_growth(d["notes_series"], d["less_series"], d["born"], d["today"],
                        d["notes"], d["lessons"])
    head = "".join([
        stat(d["sessions"], "sessions"),
        stat(d["commits"], "commits"),
        stat(d["completed"], "quests done"),
        stat(d["in_progress"], "in progress"),
        stat(d["n_projects"], "projects"),
        stat(d["notes"], "bank notes"),
        stat(d["lessons"], "lessons"),
        stat(d["active_days"], "active days"),
    ])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jebrim — usage</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{{--gold:{GOLD};--gold-hi:{GOLD_HI};--gold-lo:{GOLD_LO};
    --ink:{INK};--muted:{MUTED};--faint:{FAINT};--repeat:{REPEAT};}}
  *{{box-sizing:border-box}}
  html,body{{margin:0;height:100%}}
  body{{background:#0e0b07;
    color:var(--ink);font-family:"Inter",system-ui,sans-serif;
    padding:34px 28px 40px;min-height:100%;-webkit-font-smoothing:antialiased;
    -webkit-print-color-adjust:exact;print-color-adjust:exact;}}
  /* fixed, viewport-anchored backdrop — one soft warm glow, no drift */
  body::before{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
    background:
      radial-gradient(1100px 520px at 50% -10%,rgba(60,46,24,.55) 0%,transparent 60%),
      radial-gradient(130% 100% at 50% 25%,transparent 58%,rgba(0,0,0,.5) 100%);}}
  .card{{max-width:1020px;margin:0 auto;position:relative;z-index:1;}}
  .top{{display:flex;align-items:center;justify-content:space-between;gap:18px;}}
  .id{{display:flex;align-items:center;gap:16px;}}
  .crest{{filter:drop-shadow(0 2px 6px rgba(232,183,90,.35));flex:none;}}
  .name{{font-family:"Cinzel",serif;font-weight:800;font-size:40px;line-height:1;
    letter-spacing:2px;background:linear-gradient(180deg,var(--gold-hi),var(--gold) 55%,var(--gold-lo));
    -webkit-background-clip:text;background-clip:text;color:transparent;
    filter:drop-shadow(0 1px 0 rgba(0,0,0,.5));}}
  .sub{{color:var(--muted);font-size:13px;}}
  .sub b{{color:var(--ink);font-weight:600;}}
  .badge{{font-size:11px;color:var(--gold-hi);border:1px solid rgba(232,183,90,.4);
    border-radius:999px;padding:5px 12px;letter-spacing:1px;text-transform:uppercase;
    background:rgba(232,183,90,.06);white-space:nowrap;}}
  .rule{{height:2px;margin:14px 0 22px;border-radius:2px;
    background:linear-gradient(90deg,transparent,var(--gold-lo) 8%,var(--gold-hi) 50%,var(--gold-lo) 92%,transparent);
    box-shadow:0 0 14px rgba(232,183,90,.25);}}
  .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:10px;}}
  .statnote{{font-size:11.5px;color:var(--muted);margin-bottom:22px;text-align:center;}}
  .statnote b{{color:var(--gold-hi);font-weight:700;font-variant-numeric:tabular-nums;}}
  .stat{{position:relative;border-radius:12px;padding:14px;overflow:hidden;
    background:linear-gradient(180deg,rgba(255,240,205,.05),rgba(0,0,0,.18));
    border:1px solid rgba(232,183,90,.16);
    box-shadow:0 6px 18px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.05);}}
  .stat::before{{content:"";position:absolute;inset:0 0 auto 0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(255,226,160,.6),transparent);}}
  .stat .v{{font-size:26px;font-weight:800;color:var(--gold-hi);line-height:1;
    font-variant-numeric:tabular-nums;}}
  .stat .l{{font-size:10px;color:var(--muted);text-transform:uppercase;
    letter-spacing:.8px;margin-top:7px;}}
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;}}
  .panel{{border-radius:14px;padding:18px 20px;
    background:linear-gradient(180deg,rgba(255,240,205,.035),rgba(0,0,0,.22));
    border:1px solid rgba(232,183,90,.14);
    box-shadow:0 10px 30px rgba(0,0,0,.40),inset 0 1px 0 rgba(255,255,255,.04);
    transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;}}
  .panel:hover{{transform:translateY(-2px);border-color:rgba(232,183,90,.30);}}
  .panel.wide{{grid-column:1 / -1;}}
  .phead{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;gap:10px;}}
  h2{{font-size:12px;font-weight:700;color:var(--gold);text-transform:uppercase;
    letter-spacing:1.4px;margin:0;}}
  .note{{font-size:11px;color:var(--muted);}}
  .note b{{color:var(--gold-hi);font-weight:700;}}
  .warn{{color:var(--warm,#e8b03a);font-weight:700;}}
  .legends{{margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:2px 18px;}}
  .leg{{display:flex;align-items:center;gap:8px;font-size:12px;padding:3px 0;}}
  .leg .dot{{width:11px;height:11px;border-radius:3px;flex:none;}}
  .leg .ln{{flex:1;color:var(--ink);}}
  .leg .lv{{color:var(--gold-hi);font-weight:600;font-variant-numeric:tabular-nums;}}
  .leg .lp{{color:var(--muted);width:36px;text-align:right;font-variant-numeric:tabular-nums;}}
  /* project bars */
  .arcs{{margin-top:2px;}}
  .prow{{display:flex;align-items:center;gap:18px;padding:9px 0;
    border-bottom:1px solid rgba(232,183,90,.07);}}
  .prow:last-child{{border-bottom:none;}}
  .plabel{{width:290px;flex:none;}}
  .pname{{font-size:13.5px;font-weight:600;color:var(--ink);}}
  .pflag{{font-size:11px;color:#b8ac8e;margin-top:2px;line-height:1.35;}}
  .pbarwrap{{flex:1;background:rgba(255,255,255,.05);border-radius:5px;height:15px;}}
  .pbar{{height:100%;border-radius:5px;}}
  .pbar.client{{background:linear-gradient(90deg,var(--gold-lo),var(--gold-hi));}}
  .pbar.tooling{{background:linear-gradient(90deg,#566080,#9aa6cc);}}
  .pmeta{{width:118px;flex:none;text-align:right;font-size:11px;color:var(--muted);}}
  .pmeta b{{color:var(--gold-hi);font-weight:700;font-size:14px;
    font-variant-numeric:tabular-nums;}}
  .pmeta span{{display:block;font-size:10px;margin-top:1px;}}
  .kc{{padding-left:14px;position:relative;margin-left:6px;}}
  .kc::before{{content:"";position:absolute;left:0;top:50%;transform:translateY(-50%);
    width:9px;height:9px;border-radius:2px;}}
  .kc.client::before{{background:var(--gold);}}
  .kc.tooling::before{{background:#8a96bc;}}
  .focus{{margin-top:2px;}}
  .frow{{display:flex;align-items:center;gap:10px;padding:7px 0;font-size:13px;
    border-bottom:1px solid rgba(232,183,90,.07);}}
  .frow:last-child{{border-bottom:none;}}
  .fdot{{width:9px;height:9px;border-radius:50%;flex:none;}}
  .fname{{flex:1;color:var(--ink);}}
  .fsess{{color:var(--muted);font-size:11px;font-variant-numeric:tabular-nums;}}
  .fage{{color:var(--gold-hi);font-size:11px;width:74px;text-align:right;
    font-variant-numeric:tabular-nums;}}
  .foot{{color:var(--faint);font-size:11px;margin-top:20px;text-align:right;}}
  .foot code{{color:var(--muted);}}
  @media (max-width:900px){{.stats{{grid-template-columns:repeat(2,1fr)}}
    .grid{{grid-template-columns:1fr}}}}
</style></head>
<body><div class="card">
  <div class="top">
    <div class="id">
      <svg class="crest" width="46" height="46" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="ring" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="{GOLD_HI}"/><stop offset="0.5" stop-color="{GOLD}"/>
          <stop offset="1" stop-color="{GOLD_LO}"/></linearGradient></defs>
        <circle cx="24" cy="24" r="22" fill="none" stroke="url(#ring)" stroke-width="2.5"/>
        <circle cx="24" cy="24" r="18" fill="rgba(0,0,0,.35)" stroke="{GOLD_LO}" stroke-opacity="0.5"/>
        <g stroke="url(#ring)" stroke-width="2" fill="none" stroke-linejoin="round">
          <path d="M24 13 L34 18.5 L34 29.5 L24 35 L14 29.5 L14 18.5 Z"/>
          <path d="M14 18.5 L24 24 L34 18.5 M24 24 L24 35" stroke-width="1.5"/></g>
      </svg>
      <span class="name">JEBRIM</span>
      <span class="sub">shipping &amp; data analyst — defensibility second<br>
        born <b>{d["born"].isoformat()}</b> · <b>{d["lifespan"]}</b> days
        · active <b>{d["active_days"]}</b></span>
    </div>
    <span class="badge">usage ledger</span>
  </div>
  <div class="rule"></div>
  <div class="stats">{head}</div>
  <div class="statnote"><b>{d["sessions"]}</b> sessions →
    <b>{d["completed"]}</b> quests (≈1 per session) ·
    +<b>{d["sub_quests"]}</b> sub-agent traces from fan-out
    (one session can spawn 15+ dwarves)</div>

  <div class="panel wide">
    <div class="phead"><h2>Projects — where the work goes</h2>
      <span class="note">bar = sessions ·
        <span class="kc client">client {100 * cf / ct_tot:.0f}%</span>
        <span class="kc tooling">system {100 * tf / ct_tot:.0f}%</span></span></div>
    {arcs}
    <div class="note" style="margin-top:12px">+{other_ct} one-off / cross-cutting
      files outside a named project. <b>EU Tender</b> is the spine — 53 sessions
      across the full lifespan.</div>
  </div>

  <div class="grid">
    <div class="panel">
      <div class="phead"><h2>Current focus — recency</h2>
        <span class="note">newest file touched · ● live ○ dormant</span></div>
      {focus}
    </div>
    <div class="panel">
      <div class="phead"><h2>Job to be done</h2>
        <span class="note">ask-shapes · recon-derived</span></div>
      {jobm}
    </div>
  </div>

  <div class="grid">
    <div class="panel">
      <div class="phead"><h2>Work rhythm</h2>
        <span class="note">quests completed / week</span></div>
      {grad}
    </div>
    <div class="panel">
      <div class="phead"><h2>Knowledge moat — cumulative</h2>
        <span class="note">the compounding asset</span></div>
      {growth}
    </div>
  </div>

  <div class="grid">
    <div class="panel wide">
      <div class="phead"><h2>Domains — depth × freshness</h2>
        <span class="note">bar = corpus+work · dot = last touched</span></div>
      {doms}
      <div class="note" style="margin-top:12px">~80% of knowledge is shipping-cost;
        bi-etl / nfe-repo are thin lineage stubs going stale.</div>
    </div>
  </div>

  <div class="foot">generated {d["today"].isoformat()} ·
    <code>tools/jebrim_usage.py</code> · static snapshot · job-mix recon-derived</div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Generate Jebrim's usage card.")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "jebrim-card.html"))
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--data", action="store_true", help="print computed data summary")
    args = ap.parse_args()
    d = collect()
    if args.data:
        print("PROJECTS:")
        for p in d["projects"]:
            print(f"  {p['name']:26} files={p['count']:3} sess={p['nsess']:3} "
                  f"{p['first']}..{p['last']} [{p['kind']}]")
        print(f"client/tooling files: {d['client_files']}/{d['tooling_files']}")
        print("JOB MIX:", dict(d["job"]))
        print("FOCUS:", [(f["name"], f"{f['age']}d") for f in d["focus"]])
        print("WORK/WEEK:", [(str(w), v) for w, v in d["grad_weeks"]])
        print("NOTES SERIES:", {str(k): v for k, v in d["notes_series"].items()})
        print("LESS SERIES:", {str(k): v for k, v in d["less_series"].items()})
        print(f"sessions {d['sessions']} commits {d['commits']} completed {d['completed']} "
              f"in_progress {d['in_progress']} notes {d['notes']} lessons {d['lessons']} "
              f"active_days {d['active_days']} projects {d['n_projects']}")
    html = render(d)
    out = Path(args.out)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}  ({len(html):,} bytes)")
    if args.open:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
