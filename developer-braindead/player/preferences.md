# preferences.md — Niklavs's working preferences

> Source of truth: `~/.claude/CLAUDE.md`. This file mirrors the relevant subset and adds project-local refinements. When the global file changes, refresh here.

## Coding

- **Polars over pandas** unless interfacing with a pandas-only library.
- **Parquet over CSV** for intermediate data.
- **f-strings over `.format()`**.
- **`pathlib` over `os.path`**.
- **SQL goes in `sql/` folder**, never inline in Python.

## Collaboration boundaries

- **Always ask before committing.**
- **Never drop or truncate tables without asking.**
- **Don't refactor code Niklavs didn't ask to change.**

## Project-local additions

- *None yet. Land here as they emerge.*

## How these interact with identity

These are *constraints* — what to do and not do. They're distinct from [[I-001]]-style postures, which are *how to decide* at forks in the road. The constraints set the perimeter; postures govern inside it.
