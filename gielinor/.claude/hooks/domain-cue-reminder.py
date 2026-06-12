#!/usr/bin/env python
# domain-cue-reminder.py — make the domain-knowledge-grounding precondition FIRE,
# for ANY registered domain. The generalized successor to shipping-cue-reminder.py.
#
# Failure class (verified live, S124): the agent did domain work that has a
# canonical knowledge home (the shipping_mart, whose contract lives in
# shipping-agent/reference/) without loading that home — reasoned from memory and
# got it wrong (mislabeled OML surcharges as "billing errors"; speculated about
# whether the mart carries dimensions when tables.md answers it in one line). The
# knowledge guarantee is baked into a SUB-AGENT config or a docs/ folder; the
# PRINCIPAL path has no equivalent trigger, and pointers in keepsake/CLAUDE.md are
# passive. Capture is saturated; **triggering** was the gap — and that exact
# lesson was already in memory (S124 "read the reference") yet recurred, which is
# why the fix is a hook, not another note.
#
# This UserPromptSubmit hook is the trigger. It reads `cue_registry.py` (the
# domain table) and, on any domain's cue match, injects a short, NON-BLOCKING
# reminder to load that domain's knowledge home (or spawn its specialist).
#
# Design (mirrors grounding-cue, per the brain's verify-enforcement-fires ethos):
#   - cue match is the load-bearing path; advisory only (additionalContext), never
#     blocks (exit 0 always). A missed nudge costs nothing; a crash that ate a
#     prompt would be the real harm — so every parse/IO failure exits 0 silently.
#   - per-entry actor scope: an entry skips its own skip_actors (default skips
#     dev-brain / braindead) via the per-session status sidecar.
#   - ONE combined nudge: if several domains match the same prompt, emit a single
#     additionalContext block (the entries joined), not N stacked blocks — stacking
#     is how advisories become wallpaper (grounding-cue's §6 over-trust risk).
#
# DISTINCT from grounding-cue-reminder.py: that one is the *identity* reflex
# (continuation cue -> your OWN past work). This one is the *domain* reflex (topic
# -> its external knowledge home). grounding-cue is left untouched.

import json
import os
import re
import sys
from pathlib import Path

# Ritual analytics — best-effort; never breaks the hook.
_SB = Path(__file__).resolve().parents[3] / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k): pass

# The domain table. Import defensively — a broken/missing registry must not break
# the hook (it just means no domain fires).
try:
    from cue_registry import DOMAINS, DEFAULT_SKIP_ACTORS
except Exception:
    DOMAINS = []
    DEFAULT_SKIP_ACTORS = ("braindead",)

STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"

# gielinor/.claude/hooks -> gielinor (for resolving a domain's inline_homes paths).
GIELINOR_ROOT = Path(__file__).resolve().parents[2]

# Total byte ceiling for a domain's force-inlined homes. Over this, the hook falls
# back to NAMING the files (the original nudge) — the mechanical guard that keeps a
# large/external reference set out of every prompt (context-rot is the thing the whole
# §X arc fights). ~12 KB ≈ a few small in-tree notes; deploy-schema's set is ~7.5 KB.
INLINE_BYTE_CAP = 12000

# Hardened actor resolution (S125 _actor.py): status file first, intent-file
# anchor as the anti-race fallback. _actor.py's contract MANDATES that any new
# actor-needing hook use resolve_actor rather than a status-only read — reading
# status alone re-introduces the S124 sidecar-lag race (during the lag window
# actor=='' so the braindead skip wouldn't apply and a dev session would wrongly
# get a domain nudge). Defensive import: fall back to the local status-only read
# if _actor.py is somehow unavailable, so the hook never breaks.
_HOOK_DIR = Path(__file__).resolve().parent
if str(_HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOK_DIR))
try:
    from _actor import resolve_actor
except Exception:
    def resolve_actor(sid8, brain_root=None):
        return _actor_for(sid8)


def _compiled(domains):
    """Compile each domain's patterns once. Bad patterns drop that entry, not the hook."""
    out = []
    for d in domains:
        try:
            rx = re.compile("|".join(d["patterns"]), re.IGNORECASE)
        except Exception:
            continue
        out.append((d, rx))
    return out


# --- §Z.C: per-player domain-digest auto-discovery ---------------------------
# The domain-cue path discovers the ACTIVE player's bank/domains/*.md DIGESTS,
# reads their frontmatter `patterns`, and inlines the matching digest (the §X.3
# force-inline, but discovered-not-hand-listed + digest-not-whole-notes). Adding a
# domain = alching drops a digest file; no hook/registry edit. The global registry
# above stays for EXTERNAL/specialist domains (shipping repo); per-player digests
# are the new primary for a player's OWN topics. See gielinor/players/<p>/bank/
# domains/_about.md + developer-braindead/bank/plan.md §Z.

def _player_root(actor: str):
    """The on-disk home of an actor that may bear a bank/domains/ layer — a player
    (players/<actor>) or a deity (deities/<actor>). None if neither exists."""
    for sub in ("players", "deities"):
        p = GIELINOR_ROOT / sub / actor
        if p.is_dir():
            return p
    return None


def _parse_frontmatter(path: Path) -> dict:
    """Minimal stdlib reader for the digest frontmatter fields this hook needs
    (`patterns` list + `domain`/`title` scalars). NOT a general YAML parser — it
    handles the flat `key: scalar` / `key:`-then-`  - item` shape the digest schema
    uses. A malformed file returns {} (the digest drops out; the hook never breaks)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data, cur_key = {}, None
    for raw in parts[1].splitlines():
        if not raw.strip():
            continue
        item = re.match(r"^\s+-\s+(.*)$", raw)
        if item and cur_key:
            if isinstance(data.get(cur_key), list):
                data[cur_key].append(item.group(1).strip())
            continue
        kv = re.match(r"^([\w-]+):\s*(.*)$", raw)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            cur_key = key
            data[key] = val if val else []
    return data


def _discover_digests(actor: str) -> list:
    """Discover the active player's bank/domains/<slug>.md digests as domain entries
    compatible with the render/inline machinery. `_`-prefixed files are infra
    (skipped); a digest with no `patterns` can't be cued (skipped). The digest file
    itself is the `inline_homes` payload — its body force-inlines on a pattern match,
    once per session, byte-capped, exactly like a registry inline_home."""
    if not actor or actor in ("", "braindead"):
        return []
    root = _player_root(actor)
    if root is None:
        return []
    ddir = root / "bank" / "domains"
    if not ddir.is_dir():
        return []
    out = []
    for f in sorted(ddir.glob("*.md")):
        if f.name.startswith("_"):
            continue
        fm = _parse_frontmatter(f)
        pats = fm.get("patterns") or []
        if not isinstance(pats, list) or not pats:
            continue
        slug = fm.get("domain") or f.stem
        title = fm.get("title") or slug
        rel = f.relative_to(GIELINOR_ROOT).as_posix()
        out.append({
            "name": f"domain-{slug}",
            # frontmatter patterns are literal cue substrings (per the _about), NOT
            # regex like the registry's — escape them so a '+'/'.' in a topic is matched literally.
            "patterns": [re.escape(p) for p in pats if isinstance(p, str) and p],
            "message": (f"Domain digest detected (\"{{matched}}\") — {title}. Your "
                        f"synthesized digest ({rel}) is authoritative; don't re-derive "
                        "this domain from memory."),
            "inline_homes": [rel],
            "skip_actors": DEFAULT_SKIP_ACTORS,
        })
    return out


def _actor_for(sid8: str) -> str:
    """Read the per-session status sidecar to learn the active actor. '' if unknown."""
    if not sid8:
        return ""
    try:
        data = json.loads((STATUS_DIR / f"{sid8}.json").read_text(encoding="utf-8"))
        return (data.get("actor") or "").lower()
    except (OSError, ValueError):
        return ""


# --- [LOR]: lorebook-decision cue arm (knowledge-miss regression case 10) -----
# ~18 lorebook/confirmed/D-NNN decisions never load in player turns; most are
# carried by an always-on file, a ritual read, or a hook, but a handful are
# genuinely missable mid-task (pathspec commits, the PowerShell encoding rule).
# lorebook/_index.md is the synthesized map: per decision, literal cue patterns
# + a ONE-LINE distilled rule. On a pattern match the RULE ITSELF is inlined
# (forcing-over-naming, like §Z.C — but the rule is small enough to BE the
# payload), once per session per decision. After that the entry goes SILENT for
# the session — no name-nudge tail, because lorebook cues ("commit") recur far
# more than topic cues and a per-prompt reminder of an already-inlined 3-line
# rule is wallpaper (grounding-cue §6 over-trust risk). Sub-agents are skipped
# entirely: they work a brief; the principal carries the operating decisions.

LOREBOOK_INDEX = GIELINOR_ROOT / "lorebook" / "_index.md"


def _parse_lorebook_index(path: Path = None) -> list:
    """Parse lorebook/_index.md into cue entries. Only entries carrying BOTH
    `patterns:` and `rule:` are cue-active; the rest document their carrier
    (`carried-by:`) and are inert here. Malformed file -> [] (never breaks)."""
    try:
        text = (path or LOREBOOK_INDEX).read_text(encoding="utf-8")
    except OSError:
        return []
    entries, cur = [], None
    for line in text.splitlines():
        # Header is `## D-NNN — title`, possibly with the ID wikilink-wrapped by
        # the born-link pre-commit hook: `## [[D-NNN_stem|D-NNN]] — title`.
        h = re.match(r"^##\s+(?:\[\[[^\]|]+\|)?(D-\d{3})(?:\]\])?\s+[—-]+\s+(.*)$",
                     line)
        if h:
            cur = {"id": h.group(1), "title": h.group(2).strip(),
                   "patterns": [], "rule": "", "file": ""}
            entries.append(cur)
            continue
        if cur is None:
            continue
        kv = re.match(r"^-\s+(patterns|rule|file):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if key == "patterns":
                cur["patterns"] = [p.strip() for p in val.split(",") if p.strip()]
            else:
                cur[key] = val
    return [e for e in entries if e["patterns"] and e["rule"]]


def _lorebook_blocks(prompt: str, actor: str, sid8: str, is_subagent: bool) -> list:
    """Match the prompt against the cue-active lorebook entries; return
    (name, text) blocks for the combined emission. Once-per-session-per-decision
    via the same .dcue-* sentinel family the domain inline uses."""
    if is_subagent or actor in DEFAULT_SKIP_ACTORS:
        return []
    blocks = []
    for e in _parse_lorebook_index():
        try:
            rx = re.compile("|".join(re.escape(p) for p in e["patterns"]),
                            re.IGNORECASE)
        except Exception:
            continue
        m = rx.search(prompt)
        if not m:
            continue
        name = f"lorebook-{e['id']}"
        sentinel = (STATUS_DIR / f"{sid8}.dcue-{name}") if sid8 else None
        if sentinel and sentinel.exists():
            continue  # rule already in context this session; repeating it is wallpaper
        matched = m.group(0).strip()
        ref = e["file"] or f"lorebook/confirmed/{e['id']}_*.md"
        text = (f"Applicable lorebook decision (\"{matched}\") — {e['id']} "
                f"{e['title']} (in force; full entry: {ref}):\n  {e['rule']}")
        try:
            if sentinel:
                sentinel.parent.mkdir(parents=True, exist_ok=True)
                sentinel.write_text("1", encoding="utf-8")
        except OSError:
            pass
        log_event(f"lorebook-cue:{e['id']}", "inline", sid8=sid8, detail=matched)
        blocks.append((name, text))
    return blocks


def _render(d: dict, matched: str) -> str:
    """Compose the nudge text for one matched domain from its structured fields.

    The lead `message` carries topic + why; the structured fields (canonical_files /
    specialist / freshness / read_before) carry the file list, loader, drift note,
    and read-before directive. Backward-compatible: an entry with only `message`
    renders just that line (every field below is optional)."""
    try:
        lead = (d.get("message") or "").format(matched=matched)
    except Exception:
        lead = d.get("message") or ""
    lines = [lead] if lead else []
    files = d.get("canonical_files") or []
    if files:
        lines.append("  - Canonical knowledge home: " + "; ".join(files))
    specialist = d.get("specialist")
    if specialist:
        lines.append(f"  - Or spawn: {specialist} (loads the home by construction)")
    freshness = d.get("freshness")
    if freshness:
        lines.append("  - Freshness: " + freshness)
    read_before = d.get("read_before")
    if read_before:
        lines.append("  - Read before answering: " + read_before)
    return "\n".join(lines)


def _read_gielinor(rel: str) -> str:
    """Read a gielinor-relative file's contents, '' on any IO error."""
    try:
        return (GIELINOR_ROOT / rel).read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _maybe_inline(d: dict, sid8: str) -> str:
    """Force-inline a domain's inline_homes CONTENTS, once per session per domain.

    Returns the inlined block, or '' to fall back to the name-only nudge. '' happens
    when: the domain declares no inline_homes; the per-(session,domain) sentinel is
    already set (contents are in context from an earlier prompt this session); nothing
    readable; or the total exceeds INLINE_BYTE_CAP (the keep-large-homes-out guard).
    The sentinel is burned ONLY on a real inline, so an over-cap/empty set keeps
    surfacing the name-nudge rather than going silent."""
    homes = d.get("inline_homes") or []
    if not homes:
        return ""
    name = d.get("name", "domain")
    sentinel = (STATUS_DIR / f"{sid8}.dcue-{name}") if sid8 else None
    if sentinel and sentinel.exists():
        return ""  # already inlined this session -> lighter name-nudge from here on

    parts, total = [], 0
    for rel in homes:
        body = _read_gielinor(rel)
        if not body:
            continue
        total += len(body.encode("utf-8"))
        parts.append((rel, body))
    if not parts or total > INLINE_BYTE_CAP:
        return ""  # nothing readable, or too big -> name-only (don't burn the sentinel)

    try:
        if sentinel:
            sentinel.parent.mkdir(parents=True, exist_ok=True)
            sentinel.write_text("1", encoding="utf-8")
    except OSError:
        pass

    out = ["  --- Knowledge-home contents, force-loaded once this session "
           "(don't re-derive these from memory) ---"]
    for rel, body in parts:
        out.append(f"  [{rel}]\n{body}")
    return "\n\n".join(out)


def _emit(blocks: list) -> None:
    """blocks: list of (name, text). Emit ONE combined additionalContext."""
    if len(blocks) == 1:
        msg = blocks[0][1]
    else:
        msg = "Multiple knowledge-home topics detected — ground each before reasoning:\n\n" + \
              "\n\n".join(f"[{name}]\n{text}" for name, text in blocks)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # can't parse — never disrupt a real prompt

    if payload.get("hook_event_name") not in (None, "UserPromptSubmit"):
        return 0

    prompt = payload.get("prompt") or ""

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    sid8 = sid[:8].lower()
    actor = resolve_actor(sid8)

    # Sub-agents read their brief (and the specialist loads its own reference by
    # construction), so the heavier force-inline is principal-path only — they still
    # get the lighter name-nudge, exactly like keepsake-forced-read skips sub-agents.
    is_subagent = bool(payload.get("agent_type"))

    # Static registry domains (external/specialist) + the active player's
    # auto-discovered own-topic digests (§Z.C).
    domains = list(DOMAINS) + _discover_digests(actor)

    blocks = []
    for d, rx in _compiled(domains):
        skip = tuple(d.get("skip_actors", ("braindead",)))
        if actor in skip:
            continue
        m = rx.search(prompt)
        if not m:
            continue
        matched = m.group(0).strip()
        name = d.get("name", "domain")
        text = _render(d, matched)
        inline = "" if is_subagent else _maybe_inline(d, sid8)
        if inline:
            text = text + "\n\n" + inline
            log_event(f"domain-cue:{name}", "inline", sid8=sid8, detail=matched)
        else:
            log_event(f"domain-cue:{name}", "nudge", sid8=sid8, detail=matched)
        blocks.append((name, text))

    # [LOR] lorebook-decision arm — same single combined emission.
    blocks.extend(_lorebook_blocks(prompt, actor, sid8, is_subagent))

    if not blocks:
        return 0  # ordinary prompt — fast, silent pass-through

    _emit(blocks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
