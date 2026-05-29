# tools/

Standalone brain utilities. Not part of the cockpit or either brain's knowledge —
just scripts the principal runs.

## read_comms.py — read a comms log aloud, one voice per speaker

Turns a brain comms conversation into speech using Microsoft **edge-tts** (free
neural voices, no API key). Each speaker gets a distinct voice, so a dialogue
plays back as a conversation instead of a monotone block.

### Setup

```
py -m pip install edge-tts
```

edge-tts streams from a Microsoft endpoint, so synthesis needs internet. No
account, no key, no per-use cost.

### Use

```
# the whole gielinor comms dialogue -> an mp3 under tools/out/
py tools/read_comms.py

# just the most recent conversation, and play it when done
py tools/read_comms.py --last-conversation --speak

# an exact line range of any comms file (precise — recommended for one thread)
py tools/read_comms.py --lines 196:256 --out talk.mp3

# read a different comms log
py tools/read_comms.py --file developer-braindead/comms/active.md --lines 1:80

# override a speaker's voice; see the map
py tools/read_comms.py --voice jebrim=en-US-EricNeural
py tools/read_comms.py --list-voices
```

### Flags

| Flag | Effect |
|---|---|
| `--file PATH` | comms file to read (default: `gielinor/comms/active.md`) |
| `--lines A:B` | restrict to a 1-indexed inclusive line range |
| `--last-conversation` | only entries from the last `OPEN` onward |
| `--include-open` | also voice `OPEN`/`CLOSING`/`UPDATE` bodies (default: `→ @` dialogue only) |
| `--out PATH` | output mp3 (default: `tools/out/comms-<timestamp>.mp3`) |
| `--speak` | play the mp3 after generating (Windows/macOS/Linux) |
| `--voice actor=VOICE` | override one speaker's voice (repeatable) |
| `--rate` / `--volume` | edge-tts prosody, e.g. `--rate=-10%` |
| `--no-speaker-tags` | don't announce the speaker name before each turn |
| `--list-voices` | print the speaker→voice map and exit |

### Default voices

The newer **Multilingual** voices are the most natural / conversational ones
edge-tts offers (tuned for dialogue, not announcing):
`Braindead → en-US-AndrewMultilingualNeural` · `Jebrim → en-US-BrianMultilingualNeural`
· `Zezima → en-US-EmmaMultilingualNeural` · `Guthix → en-US-AvaMultilingualNeural`
· `Wisp → en-US-BrianNeural`. Unknown speakers draw from a pool in first-seen
order. Override any with `--voice actor=VOICE`; list every available voice with
`edge-tts --list-voices`.

### Notes / limits

- **Parsing** keys on the comms header shape `[ts] <actor>-<sid> <kind> …`; the
  actor before the `-` selects the voice. Both `→` and `->` dialogue markers are
  recognized.
- **`--lines` is exact; `--last-conversation` is a convenience** that starts at
  the last `OPEN`. When two speakers post back-to-back OPENs (as in a staged
  cross-brain chat), it begins at the *second* OPEN — use `--lines` to capture
  both openers.
- **mp3 stitching** is a byte-concatenation of per-turn edge-tts clips, which
  plays cleanly in normal players. If some player chokes on the joins, install
  `ffmpeg` and re-encode, or play the per-turn clips.
- Outputs land in `tools/out/` (git-ignored).
```
