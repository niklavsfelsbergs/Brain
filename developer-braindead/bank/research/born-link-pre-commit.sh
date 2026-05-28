#!/bin/sh
# born-link pre-commit hook — auto-wrap resolvable links + BLOCK malformed ones
# in staged gielinor/ markdown. Enforces the §O.9 born-linked discipline at the
# commit (durability) boundary so the graph stops re-rotting.
#
# INSTALL (run from the repo root; do this when no sibling session is committing):
#   cp developer-braindead/bank/research/born-link-pre-commit.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
# UNINSTALL:  rm .git/hooks/pre-commit
#
# Behaviour: auto-wraps bare [[ID]] / unwrapped prose IDs in staged gielinor .md
# and re-stages them; FAILS the commit (exit 1) on a malformed [[..md]] / [[../x]]
# wikilink with a list to fix. Scope + exclusions live in born-link-lint.py.

ROOT="$(git rev-parse --show-toplevel)"
LINT="$ROOT/developer-braindead/bank/research/born-link-lint.py"

# staged gielinor markdown (Added/Copied/Modified), as gielinor-relative paths
STAGED=$(git diff --cached --name-only --diff-filter=ACM -- gielinor \
         | grep '\.md$' | sed 's#^gielinor/##')
[ -z "$STAGED" ] && exit 0

CSV=$(printf '%s\n' "$STAGED" | tr '\n' ',' | sed 's/,$//')

# Run the fixer+linter. stdout = FIX\t<rel> lines (re-stage targets);
# stderr = human report + the BLOCK list. Non-zero exit => malformed link => abort.
OUT=$(python "$LINT" --vault "$ROOT/gielinor" --files "$CSV") || exit 1

# Re-stage files the auto-wrap modified.
printf '%s\n' "$OUT" | while IFS="$(printf '\t')" read -r tag rel; do
    [ "$tag" = "FIX" ] && [ -n "$rel" ] && git add "gielinor/$rel"
done
exit 0
