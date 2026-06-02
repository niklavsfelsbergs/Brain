#!/bin/sh
# born-link pre-commit hook — auto-wrap resolvable links + BLOCK malformed ones
# in staged markdown of BOTH brains (gielinor + developer-braindead). Enforces the
# §O.9 born-linked discipline at the commit (durability) boundary so the graph
# stops re-rotting. Each vault resolves links against its OWN files (per-brain
# vaults), so cross-brain refs correctly stay dangling (not blocked).
#
# INSTALL (run from the repo root; do this when no sibling session is committing):
#   cp developer-braindead/bank/research/born-link-pre-commit.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
# UNINSTALL:  mv .git/hooks/pre-commit /tmp/   (block-deletes refuses `rm`)
#
# Behaviour per vault: auto-wraps bare [[ID]] / unwrapped prose+anchor IDs in
# staged .md and re-stages them; FAILS the commit (exit 1) on a malformed
# [[..md]] / [[../x]] wikilink with a fix-list. Scope + exclusions: born-link-lint.py.

ROOT="$(git rev-parse --show-toplevel)"
LINT="$ROOT/developer-braindead/bank/research/born-link-lint.py"
FAIL=0

for VAULT in gielinor developer-braindead; do
    STAGED=$(git diff --cached --name-only --diff-filter=ACM -- "$VAULT" \
             | grep '\.md$' | sed "s#^$VAULT/##")
    [ -z "$STAGED" ] && continue
    CSV=$(printf '%s\n' "$STAGED" | tr '\n' ',' | sed 's/,$//')
    if OUT=$(python "$LINT" --vault "$ROOT/$VAULT" --files "$CSV"); then
        # re-stage files the auto-wrap modified (FIX\t<rel> lines on stdout).
        # tr -d '\r': the linter prints under Windows text-mode stdout (CRLF), so
        # without this `rel` keeps a trailing \r and `git add "..md\r"` fails
        # ("did not match", \r renders as ?), leaving auto-wraps dirty for a 2nd commit.
        printf '%s\n' "$OUT" | tr -d '\r' | while IFS="$(printf '\t')" read -r tag rel; do
            [ "$tag" = "FIX" ] && [ -n "$rel" ] && git add "$VAULT/$rel"
        done
    else
        FAIL=1   # malformed link in this vault -> abort; auto-wraps stay in worktree
    fi
done

# §Y.1 — keep the AGENTS.md mirror in sync with the CLAUDE.md chain.
# Codex (and other non-Claude agents) read AGENTS.md but do NOT resolve @import,
# so the rulebook must be inlined physically there. sync_agents_md.py flattens
# each CLAUDE.md's @import chain into its sibling AGENTS.md. If THIS commit stages
# any CLAUDE.md or gielinor meta/*.md (the imported sources), regenerate the
# mirror and re-stage the AGENTS.md so it travels in the same commit (no drift).
# Editing a source by pathspec? Include the AGENTS.md path(s) in your pathspec.
if git diff --cached --name-only --diff-filter=ACM \
   | grep -Eq '(^|/)CLAUDE\.md$|(^|/)meta/.*\.md$'; then
    python "$ROOT/tools/sync_agents_md.py" >/dev/null 2>&1 || true
    for A in AGENTS.md gielinor/AGENTS.md developer-braindead/AGENTS.md; do
        git add "$A" 2>/dev/null || true
    done
fi

exit $FAIL
