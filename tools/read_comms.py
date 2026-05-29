#!/usr/bin/env python3
"""read_comms.py — read a brain comms log aloud, one voice per speaker.

A reusable comms-to-speech tool built on Microsoft edge-tts (free neural
voices, no API key). It parses any brain comms file (`comms/active.md` shape),
pulls the dialogue, maps each speaker to a distinct voice, and stitches the
turns into a single mp3 — so a conversation plays back as a conversation, not
a monotone wall.

Born 2026-05-30 (Braindead, dev-brain) out of the staged Braindead<->Jebrim
comms conversation. Reusable across any comms log + any roster of speakers.

Examples
--------
  # the whole gielinor comms dialogue -> an mp3 under tools/out/
  py tools/read_comms.py

  # just the latest conversation (everything from the last OPEN onward), and play it
  py tools/read_comms.py --last-conversation --speak

  # a specific line range of any comms file, custom voice for a speaker
  py tools/read_comms.py --file developer-braindead/comms/active.md \
      --lines 196:256 --voice jebrim=en-US-EricNeural --out talk.mp3

  # see the speaker->voice map (and how to list every edge-tts voice)
  py tools/read_comms.py --list-voices

Dependency:  py -m pip install edge-tts   (requires internet at synth time)
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import os
import re
import sys
import tempfile
from pathlib import Path

# --- where the brain root is (this file lives at <root>/tools/read_comms.py) ---
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = ROOT / "gielinor" / "comms" / "active.md"
DEFAULT_OUTDIR = ROOT / "tools" / "out"

# --- speaker -> voice. Two clearly-distinct leads (US vs GB accent) so the
#     conversation reads as two different people; the rest fill the roster. ---
# The newer "Multilingual" voices are the most natural / conversational edge-tts
# offers (tuned for dialogue, not announcing). Two distinct male leads, generic.
VOICE_MAP = {
    "braindead": "en-US-AndrewMultilingualNeural",  # natural, warm
    "jebrim":    "en-US-BrianMultilingualNeural",    # natural, distinct from Andrew
    "zezima":    "en-US-EmmaMultilingualNeural",     # natural female
    "guthix":    "en-US-AvaMultilingualNeural",      # natural, measured
    "wisp":      "en-US-BrianNeural",
}
# Unknown speakers draw from here, in first-seen order.
VOICE_POOL = [
    "en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural",
    "en-US-EmmaMultilingualNeural", "en-US-AvaMultilingualNeural",
    "en-US-AndrewNeural", "en-US-BrianNeural", "en-US-EmmaNeural",
    "en-US-AvaNeural",
]
DISPLAY = {
    "braindead": "Braindead", "jebrim": "Jebrim", "zezima": "Zezima",
    "guthix": "Guthix", "wisp": "Wisp",
}

# [2026-05-30 00:09] braindead-b2e3bea8  -> @jebrim ...   (rest = everything after the id)
_HEADER = re.compile(r"^\[(?P<ts>[^\]]*)\]\s+(?P<id>[A-Za-z]+-[\w.]+)\s*(?P<rest>.*)$")
_ARROWS = ("→", "->")  # the dialogue marker: '→ @target' or '-> @target'


def classify(rest: str) -> str:
    r = rest.lstrip()
    if r.startswith(_ARROWS):
        return "dialogue"
    for kind in ("OPEN", "CLOSING", "UPDATE", "ABANDONED", "NOTE"):
        if r.startswith(kind):
            return kind.lower()
    return "other"


def clean_for_speech(text: str) -> str:
    """Strip markup that reads badly aloud; keep the prose intact."""
    text = text.replace("`", "")
    text = re.sub(r"[<>]", "", text)            # <pathspec> -> pathspec
    text = re.sub(r"\s*[—–]\s*", ", ", text)    # em/en dash -> spoken pause
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_entries(path: Path, line_range: tuple[int, int] | None):
    """Return a list of dicts: {actor, kind, ts, text} in file order."""
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if line_range:
        lo, hi = line_range
        raw = raw[max(0, lo - 1): hi]  # 1-indexed inclusive
    entries: list[dict] = []
    i, n = 0, len(raw)
    while i < n:
        m = _HEADER.match(raw[i])
        if not m:
            i += 1
            continue
        actor = m.group("id").split("-")[0].lower()
        kind = classify(m.group("rest"))
        # collect indented body lines until a blank line / next header / EOF
        body: list[str] = []
        j = i + 1
        while j < n:
            line = raw[j]
            if line.strip() == "" or _HEADER.match(line):
                break
            body.append(line.strip())
            j += 1
        entries.append({
            "actor": actor, "kind": kind, "ts": m.group("ts"),
            "text": clean_for_speech(" ".join(body)),
        })
        i = j
    return entries


def select(entries, include_kinds, last_conversation):
    if last_conversation:
        # everything from the last OPEN onward (the most recent conversation)
        last_open = max((k for k, e in enumerate(entries) if e["kind"] == "open"),
                        default=0)
        entries = entries[last_open:]
    return [e for e in entries if e["kind"] in include_kinds and e["text"]]


def voice_for(actor: str, overrides: dict, assigned: dict) -> str:
    if actor in overrides:
        return overrides[actor]
    if actor in VOICE_MAP:
        return VOICE_MAP[actor]
    if actor not in assigned:
        used = set(assigned.values()) | set(VOICE_MAP.values())
        nxt = next((v for v in VOICE_POOL if v not in used), VOICE_POOL[0])
        assigned[actor] = nxt
    return assigned[actor]


async def synth_segments(segments, out_path: Path, rate: str, volume: str, quiet: bool):
    import edge_tts
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmpdir = Path(tempfile.mkdtemp(prefix="readcomms_"))
    parts: list[Path] = []
    try:
        for idx, (voice, text) in enumerate(segments):
            seg = tmpdir / f"seg_{idx:04d}.mp3"
            kwargs = {}
            if rate:
                kwargs["rate"] = rate
            if volume:
                kwargs["volume"] = volume
            await edge_tts.Communicate(text, voice, **kwargs).save(str(seg))
            parts.append(seg)
            if not quiet:
                preview = text[:60].encode("ascii", "replace").decode()  # console-safe
                print(f"  [{idx + 1}/{len(segments)}] {voice}: {preview}...")
        # edge-tts emits constant-form mp3 frames; byte-concat plays cleanly.
        with open(out_path, "wb") as out:
            for p in parts:
                out.write(p.read_bytes())
    finally:
        for p in parts:
            p.unlink(missing_ok=True)
        try:
            tmpdir.rmdir()
        except OSError:
            pass
    return out_path


def play(path: Path):
    """Play the mp3 and block until it finishes. Windows-first, with fallbacks."""
    if sys.platform == "win32":
        ps = (
            "Add-Type -AssemblyName presentationCore;"
            "$p=New-Object System.Windows.Media.MediaPlayer;"
            f"$p.Open([uri]'{path.resolve().as_posix()}');"
            "$p.Play(); Start-Sleep -Milliseconds 400;"
            "$tries=0; while(-not $p.NaturalDuration.HasTimeSpan -and $tries -lt 50)"
            "{Start-Sleep -Milliseconds 100; $tries++};"
            "if($p.NaturalDuration.HasTimeSpan){"
            "Start-Sleep -Milliseconds ([int]$p.NaturalDuration.TimeSpan.TotalMilliseconds)};"
            "$p.Stop(); $p.Close()"
        )
        os.system(f'powershell -NoProfile -Command "{ps}"')
    elif sys.platform == "darwin":
        os.system(f'afplay "{path}"')
    else:
        if os.system(f'ffplay -nodisp -autoexit -loglevel quiet "{path}"') != 0:
            os.system(f'xdg-open "{path}"')


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read a brain comms log aloud, one voice per speaker.")
    ap.add_argument("--file", type=Path, default=DEFAULT_FILE,
                    help=f"comms file to read (default: {DEFAULT_FILE})")
    ap.add_argument("--lines", help="restrict to a 1-indexed inclusive line range, e.g. 196:256")
    ap.add_argument("--last-conversation", action="store_true",
                    help="only the most recent conversation (from the last OPEN onward)")
    ap.add_argument("--include-open", action="store_true",
                    help="also voice OPEN/CLOSING/UPDATE bodies (default: dialogue only)")
    ap.add_argument("--out", type=Path, default=None, help="output mp3 path")
    ap.add_argument("--speak", action="store_true", help="play the mp3 after generating")
    ap.add_argument("--voice", action="append", default=[], metavar="actor=VOICE",
                    help="override a speaker's voice (repeatable)")
    ap.add_argument("--rate", default="", help="edge-tts rate, e.g. -10%% or +15%%")
    ap.add_argument("--volume", default="", help="edge-tts volume, e.g. +0%%")
    ap.add_argument("--no-speaker-tags", action="store_true",
                    help="don't announce the speaker name before each turn")
    ap.add_argument("--list-voices", action="store_true", help="print the speaker->voice map and exit")
    ap.add_argument("--quiet", action="store_true", help="less console output")
    args = ap.parse_args(argv)

    if args.list_voices:
        print("Speaker -> voice map:")
        for k, v in VOICE_MAP.items():
            print(f"  {DISPLAY.get(k, k):10s} {v}")
        print("\nUnknown speakers draw from the pool:")
        print("  " + ", ".join(VOICE_POOL))
        print("\nList every available edge-tts voice with:  edge-tts --list-voices")
        return 0

    overrides = {}
    for o in args.voice:
        if "=" not in o:
            ap.error(f"--voice expects actor=VOICE, got {o!r}")
        a, v = o.split("=", 1)
        overrides[a.strip().lower()] = v.strip()

    line_range = None
    if args.lines:
        try:
            lo, hi = (int(x) for x in args.lines.split(":", 1))
            line_range = (lo, hi)
        except ValueError:
            ap.error("--lines expects START:END, e.g. 196:256")

    if not args.file.exists():
        print(f"comms file not found: {args.file}", file=sys.stderr)
        return 2

    include = {"dialogue"}
    if args.include_open:
        include |= {"open", "closing", "update"}

    entries = parse_entries(args.file, line_range)
    chosen = select(entries, include, args.last_conversation)
    if not chosen:
        print("no speakable entries found (try --include-open or a wider --lines range)",
              file=sys.stderr)
        return 1

    # build (voice, text) segments, announcing the speaker on each change
    assigned: dict = {}
    segments: list[tuple[str, str]] = []
    last_actor = None
    for e in chosen:
        voice = voice_for(e["actor"], overrides, assigned)
        text = e["text"]
        if not args.no_speaker_tags and e["actor"] != last_actor:
            name = DISPLAY.get(e["actor"], e["actor"].capitalize())
            text = f"{name}. {text}"
        segments.append((voice, text))
        last_actor = e["actor"]

    out = args.out or (DEFAULT_OUTDIR /
                       f"comms-{_dt.datetime.now():%Y%m%d-%H%M%S}.mp3")
    speakers = sorted({e["actor"] for e in chosen})
    print(f"{len(segments)} turns, {len(speakers)} speaker(s): "
          + ", ".join(f"{DISPLAY.get(s, s)}={voice_for(s, overrides, assigned)}" for s in speakers))
    print(f"synthesizing -> {out}")

    try:
        asyncio.run(synth_segments(segments, out, args.rate, args.volume, args.quiet))
    except ModuleNotFoundError:
        print("edge-tts not installed. Run:  py -m pip install edge-tts", file=sys.stderr)
        return 2
    except Exception as exc:  # network / synth failure — report, don't crash silently
        print(f"synthesis failed: {exc}", file=sys.stderr)
        return 2

    size = out.stat().st_size if out.exists() else 0
    print(f"done: {out} ({size:,} bytes)")
    if size == 0:
        print("warning: output is empty", file=sys.stderr)
        return 1
    if args.speak:
        print("playing...")
        play(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
