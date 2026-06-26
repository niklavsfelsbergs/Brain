#!/usr/bin/env python3
"""brain_map.py — the Map of Gielinor.

A single-glance architectural map of the brain. NOT a force-directed graph
(Obsidian / cockpit brain.js show link *topology*, where a node's position is
emergent and meaningless); this is a *map*, where position encodes the
architecture: the global layers ridge the top, the gates form a wall, the
players are houses, and the dev brain is Braindead's workshop in the corner.

The LAYOUT is authored (every known layer has a fixed home, so the picture your
memory latches onto stays the same), but the CONTENTS are live: it walks the
real tree at generation time and fills each region with file counts, freshness,
and a few attention-flags. Generated each run, so it never drifts the way a
hand-drawn map would. A top-level dir the layout doesn't know about lands in an
"unplaced" margin rather than silently vanishing.

Aesthetic is lifted from developer-braindead/experiments/brain-presentation
(the OSRS deck) and cockpit/web/styles.css, so it's coherent with both. The
RuneScape UF font is base64-embedded → the output is one self-contained file
that opens, moves, and prints anywhere.

Usage:  python tools/brain_map.py            # writes the default output + prints the path
        python tools/brain_map.py --open      # also opens it in the browser
        python tools/brain_map.py -o PATH      # custom output path

Stdlib only. Read-only over the brain tree.
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import html
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = BRAIN_ROOT / "developer-braindead" / "experiments" / "brain-map" / "index.html"
FONT_WOFF = BRAIN_ROOT / "developer-braindead" / "experiments" / "brain-presentation" / "runescape-uf.woff"

NOW = _dt.datetime.now()
NOW_TS = NOW.timestamp()

# ── scan ──────────────────────────────────────────────────────────────────
# Per-layer stats from the live tree: how many notes, and how recently touched.


def scan(rel: str, pattern: str = "*.md", exclude_prefix: str | None = None) -> dict:
    """Count files + find the freshest mtime under a layer path (recursive)."""
    base = BRAIN_ROOT / rel
    if not base.exists():
        return {"count": 0, "days": None, "missing": True}
    files = [p for p in base.rglob(pattern) if p.is_file()]
    if exclude_prefix:
        files = [p for p in files if not p.name.startswith(exclude_prefix)]
    if not files:
        return {"count": 0, "days": None}
    latest = max(p.stat().st_mtime for p in files)
    return {"count": len(files), "days": (NOW_TS - latest) / 86400.0}


def freshness_class(days) -> str:
    """Map age-of-freshest-file to a dot class — hot / warm / cool / cold."""
    if days is None:
        return "cold"
    if days <= 2:
        return "hot"
    if days <= 14:
        return "warm"
    if days <= 45:
        return "cool"
    return "cold"


# ── the authored layout ─────────────────────────────────────────────────────
# Each layer: (relpath, label, {flags}). The renderer turns these into chips.
# `heavy_over` flags a layer that has grown past a soft cap (an attention
# pointer, NOT a verdict — judgment stays with the reader). `stub` flags a layer
# meant to carry weight that's nearly empty.


def layer(rel, label, heavy_over=None, note=""):
    s = scan(rel)
    flags = []
    if s.get("missing"):
        flags.append(("missing", "no such layer"))
    elif s["count"] == 0:
        flags.append(("empty", "empty"))
    if heavy_over is not None and s["count"] > heavy_over:
        flags.append(("heavy", f"heavy ({s['count']})"))
    return {"label": label, "rel": rel, "note": note, "flags": flags, **s}


def build_model() -> dict:
    """Walk the tree into the authored regions."""
    global_ridge = [
        layer("gielinor/examine", "examine", note="self-model"),
        layer("gielinor/niksis8", "niksis8", note="who Niklavs is"),
        layer("gielinor/keepsake", "keepsake", note="always-surface pins"),
        layer("gielinor/lorebook", "lorebook", note="self-improvement log (D-NNN)"),
        layer("gielinor/meta", "meta", note="the rulebook"),
        layer("gielinor/spellbook", "spellbook", note="rituals + skills"),
        layer("gielinor/comms", "comms", note="inter-session coordination"),
    ]

    def house(name, rel_base, actor, role, sublayers):
        return {
            "name": name,
            "actor": actor,
            "role": role,
            "sublayers": [layer(f"{rel_base}/{r}", lbl, heavy_over=hv) for (r, lbl, hv) in sublayers],
        }

    houses = [
        house("JEBRIM", "gielinor/players/jebrim", "jebrim", "the analyst", [
            ("bank", "bank", None),
            ("bank/domains", "domains", None),
            ("research", "research", None),
            ("quest-log/in-progress", "quests open", 8),
            ("inventory", "inventory", 30),
            ("examine", "examine", None),
            ("niksis8_character", "niksis8·char", None),
            ("keepsake", "keepsake", None),
        ]),
        house("ZEZIMA", "gielinor/players/zezima", "zezima", "the partner", [
            ("bank", "bank", None),
            ("research", "research", None),
            ("quest-log/in-progress", "quests open", 8),
            ("examine", "examine", None),
            ("niksis8_character", "niksis8·char", None),
            ("keepsake", "keepsake", None),
        ]),
        house("GUTHIX", "gielinor/deities/guthix", "guthix", "the caretaker god", [
            ("bank", "bank", None),
            ("proposals", "proposals", None),
            ("quest-log/in-progress", "bankstand open", None),
            ("keepsake", "keepsake", None),
        ]),
    ]

    workshop = [
        layer("developer-braindead/bank/decisions", "decisions", note="D-NNN build history"),
        layer("developer-braindead/quest-log", "quest-log", note="session log (SNNN)"),
        layer("developer-braindead/bank", "bank", note="plan + build-lessons"),
        layer("developer-braindead/spellbook", "spellbook", note="dev rituals"),
        layer("developer-braindead/examine", "examine", note="dev self-model"),
    ]

    # gates — the six architectural guarantees + the hook count
    hooks = [p for p in (BRAIN_ROOT / "gielinor" / ".claude" / "hooks").glob("*.py")]
    guarantees = [
        "no confirmed/ writes",
        "no deletes",
        "dwarf boundary",
        "gnome boundary",
        "penguin boundary",
        "no sub-spawn",
    ]
    rituals = ["respawn", "alching", "bankstanding", "drafts-triage", "close-session"]

    # anything top-level the layout doesn't place
    placed = {"examine", "niksis8", "keepsake", "lorebook", "meta", "spellbook",
              "comms", "players", "deities", ".claude", "AGENTS.md", "CLAUDE.md",
              "CLAUDE.local.md", "narration.txt", "ticks.md"}
    unplaced = []
    for p in sorted((BRAIN_ROOT / "gielinor").iterdir()):
        if p.name not in placed and not p.name.startswith("."):
            unplaced.append(p.name)

    # vitals — brain-wide totals, the at-a-glance health/scale summary
    def count_all(rel, pattern="*.md"):
        base = BRAIN_ROOT / rel
        return len([p for p in base.rglob(pattern) if p.is_file()]) if base.exists() else 0

    total_notes = count_all("gielinor") + count_all("developer-braindead")
    lore_d = count_all("gielinor/lorebook", "D-*.md")
    dev_d = count_all("developer-braindead/bank/decisions", "D-*.md")
    dev_sessions = count_all("developer-braindead/quest-log", "S*.md")
    quests_done = (count_all("gielinor/players/jebrim/quest-log/completed")
                   + count_all("gielinor/players/zezima/quest-log/completed"))
    born = _dt.date(2026, 5, 20)
    age = (NOW.date() - born).days
    vitals = [
        ("born", f"2026-05-20 · day {age}"),
        ("notes across the brain", f"{total_notes:,}"),
        ("inhabitants", "2 players + 1 deity"),
        ("decisions", f"{lore_d} self · {dev_d} build"),
        ("dev sessions logged", f"{dev_sessions}"),
        ("player quests done", f"{quests_done}"),
    ]

    return {
        "global_ridge": global_ridge,
        "houses": houses,
        "workshop": workshop,
        "hooks_n": len(hooks),
        "guarantees": guarantees,
        "rituals": rituals,
        "unplaced": unplaced,
        "vitals": vitals,
    }


# ── render ───────────────────────────────────────────────────────────────────


def _font_face() -> str:
    if not FONT_WOFF.exists():
        return ""
    b64 = base64.b64encode(FONT_WOFF.read_bytes()).decode("ascii")
    return (
        "@font-face{font-family:'RuneScape UF';font-style:normal;font-weight:400;"
        f"src:local('RuneScape UF'),url(data:font/woff;base64,{b64}) format('woff');}}"
    )


def _chip(l: dict) -> str:
    """One layer chip: name, count, freshness dot, any attention flags."""
    fc = freshness_class(l.get("days"))
    cnt = "" if l.get("missing") else f'<span class="cnt">{l["count"]}</span>'
    flags = "".join(f'<span class="flag {k}">{html.escape(t)}</span>' for k, t in l["flags"])
    note = f'<span class="note">{html.escape(l["note"])}</span>' if l.get("note") else ""
    return (
        f'<div class="chip" title="{html.escape(l["rel"])}">'
        f'<span class="dot {fc}"></span>'
        f'<span class="lbl">{html.escape(l["label"])}</span>{cnt}{note}{flags}'
        f"</div>"
    )


def render(m: dict) -> str:
    ridge = "".join(_chip(l) for l in m["global_ridge"])

    houses = ""
    for h in m["houses"]:
        chips = "".join(_chip(l) for l in h["sublayers"])
        houses += (
            f'<div class="house" data-actor="{h["actor"]}">'
            f'<div class="house-head"><span class="house-name">{html.escape(h["name"])}</span>'
            f'<span class="house-role">{html.escape(h["role"])}</span></div>'
            f'<div class="house-body">{chips}</div>'
            f"</div>"
        )

    shields = "".join(f'<span class="shield">{html.escape(g)}</span>' for g in m["guarantees"])
    roads = "".join(f'<span class="road">{html.escape(r)}</span>' for r in m["rituals"])
    workshop = "".join(_chip(l) for l in m["workshop"])
    vitals = "".join(
        f'<div class="vital"><span class="k">{html.escape(k)}</span><span class="v">{html.escape(str(v))}</span></div>'
        for k, v in m["vitals"]
    )
    unplaced = ""
    if m["unplaced"]:
        items = "".join(f'<span class="unplaced-item">{html.escape(u)}</span>' for u in m["unplaced"])
        unplaced = f'<div class="unplaced">unplaced (add to layout): {items}</div>'

    stamp = NOW.strftime("%Y-%m-%d %H:%M")
    font = _font_face()

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Brain — a Map of Gielinor</title>
<style>
{font}
:root{{
  --bg:#17120b; --wood:#2a2114; --wood-2:#3a2e1a; --wood-dk:#0c0905;
  --line:#6e5a2c; --gold:#f5c542; --gold-soft:#e3b73c; --gold-dk:#8f6d1e;
  --parch:#e9dcb0; --parch-2:#ddcb95; --parch-edge:#c9b076;
  --ink:#2c2110; --ink-soft:#5a472a; --ink-faint:#8a7748;
  --jebrim:#6fa3d6; --zezima:#cf8fb8; --guthix:#7fc4a0; --dev:#e0a94a;
  --danger:#c0492f;
  --grain:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.4'/%3E%3C/svg%3E");
  font-family:'RuneScape UF','Trebuchet MS',Verdana,sans-serif;
}}
*{{box-sizing:border-box;}}
html,body{{margin:0;min-height:100%;background:radial-gradient(ellipse at top,#2a1f12 0%,#17120b 58%,#0c0905 100%);color:var(--ink);}}
body::before{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;background:var(--grain);opacity:.13;mix-blend-mode:overlay;}}

#stage{{position:relative;z-index:1;display:flex;justify-content:center;padding:4vmin 3vmin;}}
.world{{
  width:min(1240px,96vw);
  background:linear-gradient(180deg,var(--parch) 0%,var(--parch-2) 100%);
  border-radius:14px;border:3px solid var(--gold-dk);
  box-shadow:0 0 0 7px var(--wood),0 0 0 9px var(--gold-dk),0 28px 60px rgba(0,0,0,.6),inset 0 0 70px rgba(120,90,40,.22);
  overflow:hidden;position:relative;
}}
.world::after{{content:"";position:absolute;inset:0;pointer-events:none;background:var(--grain);opacity:.09;mix-blend-mode:multiply;}}
.rivet{{position:absolute;width:11px;height:11px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffe28a,#8f6d1e 70%,#5a430f);box-shadow:0 1px 2px rgba(0,0,0,.6);z-index:6;}}
.rivet.tl{{top:9px;left:9px;}} .rivet.tr{{top:9px;right:9px;}} .rivet.bl{{bottom:9px;left:9px;}} .rivet.br{{bottom:9px;right:9px;}}

.cartouche{{background:linear-gradient(180deg,var(--wood-2),var(--wood));border-bottom:3px solid var(--gold-dk);padding:16px 30px 14px;position:relative;}}
.cartouche::after{{content:"";position:absolute;inset:0;background:var(--grain);opacity:.18;mix-blend-mode:overlay;pointer-events:none;}}
.kicker{{font-size:12px;letter-spacing:.34em;text-transform:uppercase;color:var(--gold-soft);opacity:.85;}}
.title{{font-size:30px;line-height:1.05;color:var(--gold);text-shadow:0 2px 0 #6b4f10,0 0 14px rgba(245,197,66,.25);margin:3px 0 0;}}
.stamp{{position:absolute;right:30px;bottom:14px;font-size:11px;color:var(--gold-soft);opacity:.7;letter-spacing:.05em;}}

.region{{padding:14px 26px;}}
.region-label{{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:8px;border-bottom:1px dashed var(--parch-edge);padding-bottom:4px;}}
.chips{{display:flex;flex-wrap:wrap;gap:7px;}}

.chip{{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.28);border:1px solid var(--parch-edge);border-radius:7px;padding:5px 9px;font-size:13px;color:var(--ink);}}
.chip .lbl{{font-weight:600;}}
.chip .cnt{{background:var(--wood);color:var(--parch);border-radius:9px;padding:0 6px;font-size:11px;font-weight:700;}}
.chip .note{{color:var(--ink-faint);font-size:11px;font-style:italic;}}
.dot{{width:8px;height:8px;border-radius:50%;flex:none;box-shadow:0 0 4px rgba(0,0,0,.25) inset;}}
.dot.hot{{background:#f5c542;box-shadow:0 0 7px rgba(245,197,66,.9);}}
.dot.warm{{background:#cf9a3a;}}
.dot.cool{{background:#9a8552;}}
.dot.cold{{background:none;border:1.5px solid #b3a06f;}}
.flag{{font-size:10px;font-weight:700;letter-spacing:.04em;border-radius:5px;padding:1px 6px;text-transform:uppercase;}}
.flag.heavy{{background:rgba(192,73,47,.16);color:#9c3a23;border:1px solid rgba(192,73,47,.4);}}
.flag.empty,.flag.missing{{background:rgba(90,71,42,.14);color:var(--ink-soft);border:1px solid var(--parch-edge);}}

/* the gate wall — crenellated band between global + the inhabited region */
.gates{{margin:6px 26px;background:linear-gradient(180deg,#b7a16d,#a98f57);border:2px solid var(--gold-dk);border-radius:8px;padding:11px 16px 13px;position:relative;box-shadow:inset 0 2px 6px rgba(0,0,0,.18);}}
.gates::before{{content:"";position:absolute;left:0;right:0;top:-9px;height:9px;background:repeating-linear-gradient(90deg,#a98f57 0 16px,transparent 16px 28px);}}
.gates-label{{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#4a3a18;font-weight:700;margin-bottom:7px;}}
.gates-label b{{color:#3a2c10;}}
.shields{{display:flex;flex-wrap:wrap;gap:6px;}}
.shield{{font-size:11px;background:#4a3c20;color:var(--parch);border:1px solid var(--gold-dk);border-radius:5px;padding:3px 9px;letter-spacing:.02em;}}

.houses{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:8px 26px 4px;align-items:start;}}
.house{{border:1px solid var(--parch-edge);border-top:3px solid var(--actor,#888);border-radius:9px;overflow:hidden;background:rgba(255,255,255,.2);}}
.house[data-actor=jebrim]{{--actor:var(--jebrim);}}
.house[data-actor=zezima]{{--actor:var(--zezima);}}
.house[data-actor=guthix]{{--actor:var(--guthix);}}
.house-head{{background:linear-gradient(180deg,var(--wood-2),var(--wood));border-bottom:1px solid var(--gold-dk);padding:8px 12px;display:flex;align-items:baseline;gap:9px;}}
.house-name{{color:var(--actor);font-weight:700;font-size:16px;letter-spacing:.04em;text-shadow:0 1px 2px rgba(0,0,0,.55);}}
.house-role{{color:var(--parch-edge);font-size:11px;font-style:italic;}}
.house-body{{padding:10px;display:flex;flex-wrap:wrap;gap:6px;}}

.lowlands{{display:grid;grid-template-columns:1.5fr 1fr;gap:14px;padding:6px 26px 6px;align-items:stretch;}}
.workshop{{border:1px solid var(--parch-edge);border-top:3px solid var(--dev);border-radius:9px;overflow:hidden;background:rgba(224,169,74,.09);}}
.workshop .house-head{{background:linear-gradient(180deg,var(--wood-2),var(--wood));border-bottom:1px solid var(--gold-dk);}}
.workshop .house-name{{color:var(--dev);}}
.vitals{{border:1px solid var(--parch-edge);border-top:3px solid var(--gold-dk);border-radius:9px;overflow:hidden;background:rgba(255,255,255,.2);display:flex;flex-direction:column;}}
.vitals .house-head{{background:linear-gradient(180deg,var(--wood-2),var(--wood));border-bottom:1px solid var(--gold-dk);}}
.vitals .house-name{{color:var(--gold-soft);}}
.vitals-body{{padding:9px 13px;display:flex;flex-direction:column;justify-content:space-around;flex:1;font-size:13px;}}
.vital{{display:flex;justify-content:space-between;gap:10px;border-bottom:1px dashed var(--parch-edge);padding:4px 0;}}
.vital:last-child{{border-bottom:none;}}
.vital .k{{color:var(--ink-soft);}} .vital .v{{font-weight:700;color:var(--ink);}}
.road-strip{{display:flex;align-items:center;gap:0;flex-wrap:wrap;}}
.road{{background:#cdb583;border:1px solid var(--parch-edge);color:var(--ink);font-size:12px;font-weight:600;padding:5px 12px;position:relative;}}
.road:not(:last-child)::after{{content:"\\2192";margin:0 -4px 0 8px;color:var(--ink-soft);font-weight:700;}}
.road:first-child{{border-radius:7px 0 0 7px;}} .road:last-child{{border-radius:0 7px 7px 0;}}

.legend{{display:flex;flex-wrap:wrap;gap:16px;align-items:center;padding:12px 26px 18px;border-top:1px dashed var(--parch-edge);margin-top:6px;font-size:11px;color:var(--ink-soft);}}
.legend .key{{display:inline-flex;align-items:center;gap:5px;}}
.unplaced{{padding:6px 26px 16px;font-size:11px;color:var(--danger);}}
.unplaced-item{{background:rgba(192,73,47,.12);border:1px solid rgba(192,73,47,.4);border-radius:5px;padding:1px 7px;margin-left:5px;}}
</style></head>
<body><div id="stage"><div class="world">
  <i class="rivet tl"></i><i class="rivet tr"></i><i class="rivet bl"></i><i class="rivet br"></i>

  <div class="cartouche">
    <div class="kicker">a structured-markdown cognitive system</div>
    <h1 class="title">The Brain &mdash; a Map of Gielinor</h1>
    <div class="stamp">generated {stamp}</div>
  </div>

  <div class="region">
    <div class="region-label">Global &middot; the agent-wide layers (every player inherits these)</div>
    <div class="chips">{ridge}</div>
  </div>

  <div class="gates">
    <div class="gates-label">The Gates &middot; <b>{m['hooks_n']} hook scripts</b> enforce <b>6 guarantees</b> &mdash; you propose, the gates hold the line</div>
    <div class="shields">{shields}</div>
  </div>

  <div class="region" style="padding-bottom:2px">
    <div class="region-label">The inhabited region &middot; players (houses) + the caretaker god</div>
  </div>
  <div class="houses">{houses}</div>

  <div class="region">
    <div class="region-label">The roads &middot; rituals that move work through the world</div>
    <div class="road-strip">{roads}</div>
  </div>

  <div class="lowlands">
    <div class="workshop">
      <div class="house-head"><span class="house-name">Braindead's Workshop</span></div>
      <div class="house-body">{workshop}</div>
    </div>
    <div class="vitals">
      <div class="house-head"><span class="house-name">VITALS</span></div>
      <div class="vitals-body">{vitals}</div>
    </div>
  </div>

  <div class="legend">
    <span class="key"><span class="dot hot"></span> touched &le;2d</span>
    <span class="key"><span class="dot warm"></span> &le;2wk</span>
    <span class="key"><span class="dot cool"></span> &le;6wk</span>
    <span class="key"><span class="dot cold"></span> older</span>
    <span class="key"><span class="flag heavy">heavy</span> past a soft cap &mdash; attention, not a verdict</span>
    <span class="key"><span class="cnt" style="background:var(--wood);color:var(--parch);border-radius:9px;padding:0 6px">N</span> notes in the layer</span>
  </div>
  {unplaced}
</div></div></body></html>"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate the Map of Gielinor (brain-map.html).")
    ap.add_argument("-o", "--out", default=str(DEFAULT_OUT), help="output HTML path")
    ap.add_argument("--open", action="store_true", help="open the result in the browser")
    args = ap.parse_args(argv)

    model = build_model()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(model), encoding="utf-8")
    print(f"brain_map: wrote {out}")
    if model["unplaced"]:
        print(f"brain_map: NOTE unplaced top-level layers (add to layout): {', '.join(model['unplaced'])}")
    if args.open:
        import webbrowser
        webbrowser.open(out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
