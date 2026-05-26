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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(Path(__file__).resolve().parents[2]),
                    help="vault root (default: developer-braindead/)")
    ap.add_argument("--apply", action="store_true", help="write edits (default: dry-run)")
    ap.add_argument("--prefix", default=None,
                    help="restrict rewrites to one ID prefix, e.g. S or D")
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
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
