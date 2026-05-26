#!/usr/bin/env python3
"""Obsidian full-stem link migration (Option A, per the obsidian-fit spec).

Rewrites bare ID-prefix wikilinks (`[[S060]]`, `[[D-027]]`) to the full filename
stem (`[[S060_..._slug]]`) so stock Obsidian resolves them by exact filename.

Mechanism: link-TEXT rewrite only. NO file renames, NO deletes -> the hooks and
cockpit that parse `SNNN_sid8_slug.md` filenames are untouched; fully reversible
via git. Dry-run is the default; --apply writes the edits.

Generic over ID prefixes (S- quests, D- decisions, ...). In the dev brain the D-
links are already full-stem (S098), so a run here naturally only rewrites S-links.
Reusable for the gielinor pass (§O.4) by pointing --vault at gielinor/.

Spec: bank/research/obsidian-fit-and-migration-spec.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Leading ID token on a filename stem or in a link: S060, S081, D-027, B-002, ...
ID_RE = re.compile(r"^([A-Z]{1,2}-?\d+)(?:_|$)")
# A bare ID link target (no slug): exactly an ID token.
BARE_ID_RE = re.compile(r"^[A-Z]{1,2}-?\d+$")
# A sub-agent run-log token: dwarf/penguin/gnome/foreman + index (d1, p2, g1, f3).
SUBAGENT_RE = re.compile(r"^[dpgf]\d+$")
# A wikilink occurrence: [[ ... ]] (inner captured).
LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
# Fenced code block fence.
FENCE_RE = re.compile(r"^\s*(```|~~~)")

# Docs that *describe* the linking convention with illustrative [[..]] examples;
# the S098 self-clobber lesson. Rewrites landing here are surfaced for manual review
# rather than trusted blindly. (Relative to vault root.)
CONVENTION_DOCS = {
    "bank/_about.md",
    "spellbook/entry-formats.md",
    "bank/research/obsidian-fit-and-migration-spec.md",
    "bank/research/obsidian-link-migrate.py",  # this file
}


def id_of(stem: str) -> str | None:
    m = ID_RE.match(stem)
    return m.group(1) if m else None


def is_main(stem: str, id_tok: str) -> bool:
    """Main entry = not a _dN/_pN/_gN/_fN sub-log and not a -resume file."""
    if "resume" in stem.lower():
        return False
    rest = stem[len(id_tok):].lstrip("_")
    tokens = rest.split("_")
    return not any(SUBAGENT_RE.match(t) for t in tokens)


def build_index(vault: Path):
    """id -> {'files': [stems], 'mains': [stems]} over every .md in the vault."""
    index: dict[str, dict[str, list[str]]] = {}
    for p in vault.rglob("*.md"):
        if "/.git/" in p.as_posix():
            continue
        stem = p.stem
        tok = id_of(stem)
        if not tok:
            continue
        entry = index.setdefault(tok, {"files": [], "mains": []})
        entry["files"].append(stem)
        if is_main(stem, tok):
            entry["mains"].append(stem)
    return index


def resolve_targets(index):
    """id -> resolved full stem (unambiguous only). Plus flagged + sole-sub maps."""
    resolved, flagged, sole_sub = {}, {}, {}
    for tok, e in index.items():
        mains, files = e["mains"], e["files"]
        if len(mains) == 1:
            resolved[tok] = mains[0]
        elif len(mains) == 0 and len(files) == 1:
            resolved[tok] = files[0]
            sole_sub[tok] = files[0]
        elif len(mains) == 0 and len(files) > 1:
            flagged[tok] = ("no-main", sorted(files))
        else:  # >1 main
            flagged[tok] = ("multi-main", sorted(mains))
    return resolved, flagged, sole_sub


def inline_code_spans(line: str):
    """Char ranges covered by `inline code` so we don't rewrite example links."""
    spans, i, n = [], 0, len(line)
    while i < n:
        if line[i] == "`":
            j = line.find("`", i + 1)
            if j == -1:
                break
            spans.append((i, j))
            i = j + 1
        else:
            i += 1
    return spans


def in_span(pos, spans):
    return any(a <= pos <= b for a, b in spans)


def scan(vault: Path, resolved, flagged, existing_stems):
    """Walk every .md, classify each [[link]]. Returns rewrites + tallies."""
    rewrites = []          # (relpath, lineno, old_link, new_link, target_id, in_conv_doc)
    flag_hits: dict[str, int] = {}
    dangling: dict[str, int] = {}
    already = 0
    for p in sorted(vault.rglob("*.md")):
        if "/.git/" in p.as_posix():
            continue
        rel = p.relative_to(vault).as_posix()
        in_conv = rel in CONVENTION_DOCS
        fenced = False
        for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE_RE.match(line):
                fenced = not fenced
                continue
            if fenced:
                continue
            spans = inline_code_spans(line)
            for m in LINK_RE.finditer(line):
                if in_span(m.start(), spans):
                    continue
                inner = m.group(1)
                target = inner.split("|", 1)[0].split("#", 1)[0].strip()
                if not target:
                    continue
                tok = id_of(target) or (target if BARE_ID_RE.match(target) else None)
                if target in existing_stems:
                    if BARE_ID_RE.match(target) is None:
                        already += 1
                    continue
                if BARE_ID_RE.match(target):
                    if target in resolved:
                        # preserve an explicit display alias if the author set one
                        disp = inner.split("|", 1)[1] if "|" in inner else None
                        new_inner = resolved[target] + (f"|{disp}" if disp else "")
                        rewrites.append((rel, lineno, m.group(0),
                                         f"[[{new_inner}]]", target, in_conv))
                    elif target in flagged:
                        flag_hits[target] = flag_hits.get(target, 0) + 1
                    else:
                        dangling[target] = dangling.get(target, 0) + 1
                # else: full-stem-but-no-file / placeholder / code-ref -> leave
    return rewrites, flag_hits, dangling, already


# ----------------------------------------------------------------------------
# PROSE-WRAP MODE (§O.6) — wrap UNBRACKETED, resolvable ID refs as [[stem|ID]].
# Distinct from links-mode above (which only rewrites already-bracketed
# [[bare-ID]]). The display alias preserves the on-page text verbatim so prose
# reads unchanged; only the graph gains an edge. link-TEXT only, no renames.
# ----------------------------------------------------------------------------

# An unbracketed ID token in prose: S023, D-027, B-002, Q-008, ...
# - not preceded by a word char, '[' (a [[link), or '-' (mid-token);
# - not followed by a word char or '-'  -> a full stem like S014_a is SKIPPED
#   (the '_' is a word char, so the lookahead fails) and so are code-ref dashes.
# Require >=2 digits to avoid "S3 bucket" / "A1" style false hits; the
# resolve-to-a-real-file guard is the true filter, this just trims noise.
PROSE_ID_RE = re.compile(r"(?<![\w\[#-])([A-Z]{1,2}-?\d{2,4})(?![\w-])")

# Docs that *illustrate* the ID/anchor convention rather than reference real
# entries — prose hits here are surfaced for review, not auto-applied.
PROSE_CONVENTION_DOCS = {
    "meta/layer-routing.md",
    "meta/death-and-spawn.md",
    "spellbook/rituals/respawn.md",
    "spellbook/rituals/close-session.md",
    "bank/_about.md",
    "spellbook/entry-formats.md",
    "spellbook/respawn-ritual.md",
    "spellbook/session-close.md",
    "bank/research/obsidian-fit-and-migration-spec.md",
    "bank/research/obsidian-link-migrate.py",
}


# Dirs whose files are valid link TARGETS but not wrap SOURCES (§O.6 scope):
# volatile working state + superseded/turned-down content. Live curated layers
# + quest-log are in scope; these are not.
SKIP_SRC_RE = re.compile(
    r"/(inventory|archive|rejected)/"
    r"|/comms/"                      # append-only operational log, concurrently written
    r"|/experiments/"                # runtime/build artifacts (state-comms dumps)
    r"|(^|/)last-alched\.md$"        # operational alching pointer, not knowledge
)

# Body / rulebook / ritual files: user-only governance read as INSTRUCTIONS, not
# curated knowledge. Wikilink syntax adds noise there for marginal graph value, so
# they're out of the prose-wrap scope (§O.6 sign-off was knowledge + quest-log).
# Covers: CLAUDE.md, gielinor meta/ + spellbook/rituals/, dev-brain spellbook/ root
# rituals (respawn-ritual.md, session-close.md live directly in spellbook/).
BODY_RULEBOOK_RE = re.compile(
    r"(^|/)CLAUDE\.md$"
    r"|(^|/)meta/"
    r"|(^|/)spellbook/rituals/"
    r"|^spellbook/[^/]+\.md$"
)


def wikilink_spans(line: str):
    """Char ranges covered by [[ ... ]] so we don't re-wrap inside a link."""
    spans = []
    for m in LINK_RE.finditer(line):
        spans.append((m.start(), m.end() - 1))
    return spans


def scope_root(rel: str) -> str | None:
    """Resolution scope for a file: its gielinor player subtree, else whole vault.
    A jebrim note's `S023` should prefer jebrim's S023 over another player's."""
    m = re.match(r"players/([^/]+)/", rel)
    return f"players/{m.group(1)}/" if m else None


def build_index_rich(vault: Path):
    """id -> {'files': [(stem, rel)], 'mains': [(stem, rel)]} — like build_index
    but keeps each entry's vault-relative path for scope-aware resolution."""
    index: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for p in vault.rglob("*.md"):
        if "/.git/" in p.as_posix():
            continue
        stem = p.stem
        tok = id_of(stem)
        if not tok:
            continue
        rel = p.relative_to(vault).as_posix()
        entry = index.setdefault(tok, {"files": [], "mains": []})
        entry["files"].append((stem, rel))
        if is_main(stem, tok):
            entry["mains"].append((stem, rel))
    return index


def _stem_exists(stem: str, rindex) -> bool:
    e = rindex.get(id_of(stem) or "")
    return bool(e and any(s == stem for (s, _) in e["files"]))


def resolve_prose(tok: str, rel: str, rindex):
    """(stem, status). status in {ok, sole-sub, flagged, dangling}.
    A §O.6 dupe-resolution override (vault-local target only) wins first; then
    scope-first: a unique main inside the file's own player subtree; else a
    vault-unique main; else a sole sub-log; else flagged for manual call."""
    rule = PROSE_DUPE_RESOLUTION.get(tok)
    if rule:
        for substr, stem in rule:
            if substr in rel and _stem_exists(stem, rindex):
                return stem, "ok"
        # rule exists but no target resolves in this vault -> normal logic / dangling
    e = rindex.get(tok)
    if not e:
        return None, "dangling"
    mains, files = e["mains"], e["files"]
    root = scope_root(rel)
    if root:
        scoped = [s for (s, r) in mains if r.startswith(root)]
        if len(scoped) == 1:
            return scoped[0], "ok"
        if len(scoped) > 1:
            return None, "flagged"
    if len(mains) == 1:
        return mains[0][0], "ok"
    if len(mains) == 0 and len(files) == 1:
        return files[0][0], "sole-sub"
    if len(mains) == 0:
        return None, "flagged"
    return None, "flagged"  # >1 main, no scope disambiguation


# §O.6 dupe disambiguation (S105), principal-reviewed. For each ambiguous ID, an
# ordered list of (rel-substring, target-stem); first substring found in the file's
# vault-relative path wins, "" is the default. An override only fires if its target
# stem is a real file IN THE CURRENT VAULT (so a gielinor "S038" ref — cross-brain,
# no gielinor file — falls through to dangling per §O.5, never to a dev stem).
# Reasoning per ID lives in the S105 quest-log.
PROSE_DUPE_RESOLUTION = {
    # same-session copies / clear canonical — wrap all to the main entry
    "S014": [("", "S014_2026-05-21_shipping-data-mart-ttyd-howto")],
    "S049": [("", "S049_17e701eb_visualizer_state_aware_motion_and_action_line")],
    "S060": [("", "S060_brain_self_audit_and_plan_reconciliation")],
    "S076": [("", "S076_949a59cf_scm-alert-engine-audit")],
    "D-012": [("", "D-012_close_session_harvest_pump")],
    # namespace collision: bank/main-brain-construction/ has its own D-NNN scheme
    "D-001": [("main-brain-construction/", "D-001_phase-1-scaffold"),
              ("", "D-001_two_brain_split")],
    "D-002": [("main-brain-construction/", "D-002_player_invocation_by_address"),
              ("", "D-002_folder_name")],
    # genuinely-different sessions sharing a number — disambiguated by topic/path
    "S038": [("cockpit-vscode", "S038_vscode_claude_focus_extension"),
             ("S086_86020a52", "S038_vscode_claude_focus_extension"),
             ("", "S038_brain_underutilization_diagnosis")],
    "S086": [("D-030", "S086_86020a52_cockpit-terminal-compose-bar"),
             ("build-lessons", "S086_86020a52_cockpit-terminal-compose-bar"),
             ("", "S086_e668ec7e_brain-technical-docs")],
    "S062": [("push-denial", "S062_7f1aecf4_shipping-agent-euro-precision-and-build-report"),
             ("S065_", "S062_7f1aecf4_shipping-agent-euro-precision-and-build-report"),
             ("S075_", "S062_7f1aecf4_shipping-agent-euro-precision-and-build-report"),
             ("", "S062_249eb38a_shipping-agent-citation-leak-test")],
}


def _prefix_of(tok: str) -> str:
    m = re.match(r"^([A-Z]{1,2}-?)", tok)
    return m.group(1) if m else tok


def scan_prose(vault: Path, rindex, prefix):
    """Walk every .md, find unbracketed resolvable ID tokens, classify.
    Returns rewrites + flagged + dangling tallies.

    Only tokens whose prefix actually labels a file in this vault are even
    considered — so line-refs (L2448), product names (M365), task tags (T11),
    quarters (Q10), week tags (CW48) never enter the report. The resolve-guard
    is the real safety net; this just keeps the dry-run honest."""
    known_prefixes = {_prefix_of(k) for k in rindex}
    rewrites = []     # (rel, lineno, old_text, new_text, tok, in_conv)
    flagged: dict[str, int] = {}
    dangling: dict[str, int] = {}
    self_skips = 0
    for p in sorted(vault.rglob("*.md")):
        if "/.git/" in p.as_posix():
            continue
        rel = p.relative_to(vault).as_posix()
        if SKIP_SRC_RE.search("/" + rel) or BODY_RULEBOOK_RE.search(rel):
            continue
        in_conv = rel in PROSE_CONVENTION_DOCS
        own_id = id_of(p.stem)  # skip a file's self-reference
        fenced = False
        for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE_RE.match(line):
                fenced = not fenced
                continue
            if fenced:
                continue
            code = inline_code_spans(line)
            links = wikilink_spans(line)
            for m in PROSE_ID_RE.finditer(line):
                pos = m.start()
                if in_span(pos, code) or in_span(pos, links):
                    continue
                tok = m.group(1)
                if _prefix_of(tok) not in known_prefixes:
                    continue
                if prefix and not tok.startswith(prefix):
                    continue
                if own_id and tok == own_id:
                    self_skips += 1
                    continue
                stem, status = resolve_prose(tok, rel, rindex)
                if status in ("ok", "sole-sub"):
                    old = tok
                    new = f"[[{stem}|{tok}]]"
                    rewrites.append((rel, lineno, old, new, tok, in_conv))
                elif status == "flagged":
                    flagged[tok] = flagged.get(tok, 0) + 1
                else:
                    dangling[tok] = dangling.get(tok, 0) + 1
    return rewrites, flagged, dangling, self_skips


def run_prose(vault: Path, prefix, apply: bool):
    rindex = build_index_rich(vault)
    rewrites, flagged, dangling, self_skips = scan_prose(vault, rindex, prefix)

    print(f"# Obsidian PROSE-WRAP (§O.6) — {'APPLY' if apply else 'DRY-RUN'}")
    print(f"# vault: {vault}")
    print(f"# prefix filter: {prefix or '(none)'}\n")

    by_file: dict[str, int] = {}
    by_id: dict[str, int] = {}
    conv_hits = []
    for rel, ln, old, new, tid, in_conv in rewrites:
        by_file[rel] = by_file.get(rel, 0) + 1
        by_id[tid] = by_id.get(tid, 0) + 1
        if in_conv:
            conv_hits.append((rel, ln, old, new))

    print("## SUMMARY")
    print(f"  wraps proposed     : {len(rewrites)}  "
          f"({len(by_id)} distinct IDs, {len(by_file)} files)")
    print(f"  FLAGGED (ambiguous): {len(flagged)} IDs, "
          f"{sum(flagged.values())} occurrences NOT wrapped (manual call)")
    print(f"  dangling           : {len(dangling)} IDs, "
          f"{sum(dangling.values())} occurrences (no file in scope; left)")
    print(f"  self-refs skipped  : {self_skips}")
    print(f"  convention-doc hits: {sum(1 for _ in conv_hits)} (REVIEW)\n")

    if flagged:
        print("## FLAGGED — ambiguous (>1 main, no scope split), NOT wrapped")
        for tok in sorted(flagged):
            cands = rindex.get(tok, {}).get("mains", [])
            print(f"  {tok}  ({flagged[tok]} occurrences) candidates:")
            for stem, r in sorted(cands):
                print(f"      - {stem}   [{r}]")
        print()

    if conv_hits:
        print("## CONVENTION-DOC wraps (review — may be illustrative)")
        for rel, ln, old, new in conv_hits:
            print(f"  {rel}:{ln}  {old} -> {new}")
        print()

    if dangling:
        print("## dangling (no matching file in scope; left as-is)")
        for tok in sorted(dangling):
            print(f"  {tok}  x{dangling[tok]}")
        print()

    print("## PER-ID wrap counts")
    for tok in sorted(by_id):
        print(f"  {tok} x{by_id[tok]:>3}")
    print()

    print("## PER-FILE wrap counts")
    for rel in sorted(by_file):
        print(f"  {by_file[rel]:>3}  {rel}")
    print()

    if apply:
        # Apply per-file. Within a line, replace each old token occurrence that
        # is NOT already inside a link/code span — handled by re-scanning the
        # line and rebuilding it so we never double-wrap or touch a skipped hit.
        edits: dict[str, list[tuple[int, str, str]]] = {}
        for rel, ln, old, new, tid, in_conv in rewrites:
            edits.setdefault(rel, []).append((ln, old, new))
        for rel, items in edits.items():
            p = vault / rel
            lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
            # group desired wraps per line number
            per_line: dict[int, list[tuple[str, str]]] = {}
            for ln, old, new in items:
                per_line.setdefault(ln, []).append((old, new))
            for ln, pairs in per_line.items():
                raw = lines[ln - 1]
                nl = "\n" if raw.endswith("\n") else ""
                line = raw[: -len(nl)] if nl else raw
                code = inline_code_spans(line)
                links = wikilink_spans(line)
                # rebuild left-to-right, wrapping only safe ID hits
                out, last = [], 0
                want = {old for old, _ in pairs}
                for m in PROSE_ID_RE.finditer(line):
                    if m.group(1) not in want:
                        continue
                    if in_span(m.start(), code) or in_span(m.start(), links):
                        continue
                    out.append(line[last:m.start()])
                    out.append(f"[[{_stem_for(m.group(1), rel, rindex)}|{m.group(1)}]]")
                    last = m.end()
                out.append(line[last:])
                lines[ln - 1] = "".join(out) + nl
            p.write_text("".join(lines), encoding="utf-8")
        print(f"\n# APPLIED {len(rewrites)} wraps across {len(edits)} files.")
    else:
        print("\n# DRY-RUN — nothing written. Re-run with --apply to write.")


def _stem_for(tok, rel, rindex):
    stem, _ = resolve_prose(tok, rel, rindex)
    return stem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(Path(__file__).resolve().parents[2]),
                    help="vault root (default: developer-braindead/)")
    ap.add_argument("--apply", action="store_true", help="write edits (default: dry-run)")
    ap.add_argument("--prefix", default=None,
                    help="restrict rewrites to one ID prefix, e.g. S or D")
    ap.add_argument("--mode", choices=("links", "prose"), default="links",
                    help="links = rewrite bracketed [[bare-ID]] (§O.4, default); "
                         "prose = wrap UNBRACKETED resolvable IDs as [[stem|ID]] (§O.6)")
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    if args.mode == "prose":
        run_prose(vault, args.prefix, args.apply)
        return
    index = build_index(vault)
    resolved, flagged, sole_sub = resolve_targets(index)
    existing_stems = {s for e in index.values() for s in e["files"]}
    # also count non-ID-prefixed .md as resolvable exact stems (guthix, etc.)
    for p in vault.rglob("*.md"):
        existing_stems.add(p.stem)

    if args.prefix:
        resolved = {k: v for k, v in resolved.items() if k.startswith(args.prefix)}
        flagged = {k: v for k, v in flagged.items() if k.startswith(args.prefix)}

    rewrites, flag_hits, dangling, already = scan(vault, resolved, flagged, existing_stems)

    print(f"# Obsidian link migration — {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"# vault: {vault}")
    print(f"# prefix filter: {args.prefix or '(none)'}\n")

    by_file: dict[str, int] = {}
    by_id: dict[str, int] = {}
    conv_hits = []
    for rel, ln, old, new, tid, in_conv in rewrites:
        by_file[rel] = by_file.get(rel, 0) + 1
        by_id[tid] = by_id.get(tid, 0) + 1
        if in_conv:
            conv_hits.append((rel, ln, old, new))

    print("## SUMMARY")
    print(f"  rewrites proposed : {len(rewrites)}  "
          f"({len(by_id)} distinct IDs, {len(by_file)} files)")
    print(f"  already resolves  : {already} full-stem links left as-is")
    print(f"  FLAGGED (dupes)   : {len(flagged)} IDs, "
          f"{sum(flag_hits.values())} link occurrences NOT rewritten")
    print(f"  dangling          : {len(dangling)} IDs, "
          f"{sum(dangling.values())} occurrences (no file; left)")
    print(f"  convention-doc hits: {len(conv_hits)} (REVIEW manually)\n")

    print("## FLAGGED — real dupes / ambiguous, NOT rewritten (human call)")
    if flagged:
        for tok in sorted(flagged):
            kind, cands = flagged[tok]
            hits = flag_hits.get(tok, 0)
            print(f"  [[{tok}]]  ({kind}, {hits} link occurrences) candidates:")
            for c in cands:
                print(f"      - {c}")
    else:
        print("  (none)")
    print()

    if sole_sub:
        print("## sole-sub groups (no main entry; resolved to the only file)")
        for tok in sorted(sole_sub):
            print(f"  [[{tok}]] -> {sole_sub[tok]}")
        print()

    if conv_hits:
        print("## CONVENTION-DOC rewrites (review — may be illustrative examples)")
        for rel, ln, old, new in conv_hits:
            print(f"  {rel}:{ln}  {old} -> {new}")
        print()

    if dangling:
        print("## dangling bare-ID links (no matching file; left as-is)")
        for tok in sorted(dangling):
            print(f"  [[{tok}]]  x{dangling[tok]}")
        print()

    print("## PER-ID rewrite targets")
    for tok in sorted(by_id):
        print(f"  [[{tok}]] x{by_id[tok]:>3}  ->  [[{resolved[tok]}]]")
    print()

    print("## DETAIL — every proposed rewrite (file:line)")
    cur = None
    for rel, ln, old, new, tid, in_conv in rewrites:
        if rel != cur:
            print(f"\n  {rel}")
            cur = rel
        flag = "  <CONV>" if in_conv else ""
        print(f"    L{ln}: {old} -> {new}{flag}")

    if args.apply:
        edits = {}
        for rel, ln, old, new, tid, in_conv in rewrites:
            edits.setdefault(rel, []).append((old, new))
        for rel, pairs in edits.items():
            p = vault / rel
            text = p.read_text(encoding="utf-8")
            for old, new in pairs:
                text = text.replace(old, new)
            p.write_text(text, encoding="utf-8")
        print(f"\n# APPLIED {len(rewrites)} rewrites across {len(edits)} files.")
    else:
        print("\n# DRY-RUN — nothing written. Re-run with --apply to write.")


if __name__ == "__main__":
    main()
