# A-002 — Main brain is Obsidian-style markdown with wiki-links

**Status.** `working`. Opened in [[S001_dev_brain_architecture]].

Markdown files with `[[wiki-link]]` syntax form the main brain. Wiki-links are *load-bearing* for the agent's associative retrieval, not decorative for humans. Implies small files, dense linking, stable filenames.

**Replace when.** [[Q-001]] (retrieval mechanism) lands. If the chosen mechanism is markdown-grep or markdown-as-index, this assumption converts to a [[D-NNN]]. If embeddings or a non-markdown store wins, this gets revised or replaced.
