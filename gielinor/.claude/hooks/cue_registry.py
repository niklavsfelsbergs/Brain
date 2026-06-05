#!/usr/bin/env python
# cue_registry.py — the domain-knowledge-grounding registry.
#
# Data, not logic. Each entry maps a set of prompt cues to "the canonical
# knowledge home for this domain isn't loaded unless you load it — go load it
# (or spawn its specialist) before reasoning from memory." The hook that reads
# this table is `domain-cue-reminder.py`.
#
# WHY a registry (the generalization, 2026-06-02, dev session S-this):
#   The shipping/mart reflex was first built (S124) as a standalone copy of
#   grounding-cue-reminder.py — a whole hook file + its own settings.json
#   registration. The brain has *several* domains with the same shape: a
#   canonical knowledge home that won't get loaded unless something fires
#   (shipping → shipping-agent/reference; EU tender → docs/ + the tender bank
#   notes; SCM dashboard → its vocab notes; the carrier contract corpus). Every
#   such domain as a fresh copy-pasted hook is the tax this table removes:
#   **the Nth domain is one row here, not a new file.**
#
# This is DISTINCT from grounding-cue-reminder.py. That hook is the *identity*
# reflex — "a continuation cue means YOUR OWN past work is on disk; go read it"
# (own-memory; D-028). This registry is the *domain* reflex — "this topic has an
# external knowledge home that is authoritative; go load IT" (knowledge-home).
# Different semantics, kept separate on purpose. grounding-cue is untouched.
#
# SCHEMA — each entry is a dict:
#   name            str        short id; used in the ritual-log event + the nudge header.
#   patterns        list[str]  raw regex strings (compiled case-insensitively by the hook).
#                              Narrow on purpose: a false positive costs one advisory
#                              line, but over-firing turns the nudge into wallpaper.
#   message         str        the nudge LEAD line — topic + the one-line "why ground."
#                              `{matched}` is substituted with the cue that fired. Keep it
#                              short: the file list / loader / drift note live in the
#                              structured fields below, not here (avoids prose<->field drift).
#   canonical_files list[str]  the authoritative knowledge home — the files to read before
#                              reasoning. May be in-brain paths (deploy notes) or EXTERNAL-
#                              repo paths (shipping: the picanova/shipping-agent repo). Label
#                              external ones so the reader knows they're not in this tree.
#   specialist      str|None   the sub-agent that loads this home BY CONSTRUCTION (e.g.
#                              shipping-agent). Omit when the home is just files to read
#                              (deploy notes have no specialist). [optional]
#   freshness       str        how drift-prone the home is + the revalidate trigger — when
#                              a remembered version is stale and you must re-read. [optional]
#   read_before     str        the concrete read-before-answering directive: what NOT to do
#                              from memory, and the load-bearing rules the home carries.
#   inline_homes    list[str]  gielinor-relative paths whose CONTENTS get force-INLINED into
#                              context (not just named), ONCE per session per domain. This is
#                              the §X.4 keepsake move applied to domain knowledge: a directive
#                              only NAMES a read; inlining FORCES it. Use ONLY for small,
#                              in-tree homes — the hook caps total bytes (INLINE_BYTE_CAP) and
#                              falls back to naming if the set is too big, so an external repo
#                              or a large reference set must stay out of this list (name it in
#                              canonical_files / point at the specialist instead). [optional]
#   skip_actors     tuple[str] per-session actors for whom this entry does NOT fire
#                              (read from the status sidecar). Default skips braindead
#                              (the dev brain builds the brain, not domain analysis).
#
# WHY the structured fields (Y.5, 2026-06-03 — the Codex-audit enrichment):
#   Codex asked for a cue -> {canonical files, source repos, agents, freshness,
#   read-before-answering} manifest. Rather than a NEW parallel structure (which
#   would trip the brain's most-repeated failure mode — over-formalizing a reachable
#   capability), those dimensions are added as fields on THIS table: it was already
#   the cue->knowledge-home router, so it's the right home for "which files, how
#   fresh, read-before." `domain-cue-reminder.py` renders the nudge FROM these
#   fields (single source of truth; the lead `message` no longer re-states the
#   paths). Fields are optional + the renderer degrades gracefully, so an entry can
#   still carry message alone.
#
# To add a domain: append one dict. No hook edit, no new settings.json line.
# A commented EU-tender stub is at the bottom as the worked example.

# Default actors to skip for any entry that doesn't override skip_actors.
DEFAULT_SKIP_ACTORS = ("braindead",)

DOMAINS = [
    # --- entry #1: shipping / mart -------------------------------------------
    # Ported VERBATIM from S124's shipping-cue-reminder.py (patterns + message),
    # so this registry *aligns with* that work rather than reinventing it.
    # Failure it fixes (verified live, S124): mart work done as Jebrim-PRINCIPAL
    # without loading the shipping-agent reference — speculated about whether the
    # mart even carries dimensions when tables.md answers it in one line. The
    # knowledge guarantee is baked into the shipping-agent SUB-AGENT config
    # ("Read first: how_to.md in full"); the principal path had no trigger.
    {
        "name": "shipping",
        "patterns": [
            r"\bshipping\b",
            r"\bshipment",                       # shipment, shipments
            r"\bmart\b", r"shipping[_ -]?mart",
            r"\bcarrier",                        # carrier, carriers
            r"\bparcel",
            r"\bfreight\b",
            r"\bsurcharge",
            r"\bgirth\b", r"\boversize",
            r"\btender\b",                       # EU carrier tender work
            r"\b(LPS|OML)\b",
            # carrier names — unambiguous tokens, word-boundaried.
            # Bare "report" / "cost" are deliberately EXCLUDED — too broad; that's
            # how a nudge becomes wallpaper.
            r"\b(UPS|DHL|DPD|GLS|USPS|FedEx|Maersk|Asendia|OnTrac|Yodel|Hermes|Schenker|ORWO|Picturator|PicaAPI)\b",
        ],
        "message": (
            "Shipping/mart topic detected (\"{matched}\"). The mart's contract is "
            "authoritative — don't reason about the shipping_mart from memory."
        ),
        # External knowledge home: these live in the picanova/shipping-agent repo,
        # NOT this brain tree. The reliable loader is the specialist (it loads the
        # rulebook by construction), so prefer spawning it over hand-reading paths.
        "canonical_files": [
            "picanova/shipping-agent repo: how_to.md §0",
            "picanova/shipping-agent repo: reference/mart-contract.md",
            "picanova/shipping-agent repo: reference/tables.md",
        ],
        "specialist": "shipping-agent (subagent_type: shipping-agent)",
        "freshness": (
            "Home is an external repo, not this tree — a remembered schema is the "
            "stale-by-default case; spawn the specialist (or re-read the reference) "
            "rather than trusting recall of the mart shape or cost-basis rules."
        ),
        "read_before": (
            "Load the canonical files (or spawn the specialist) before writing SQL or "
            "interpreting any shipping_mart figure — the contract holds the cost-basis "
            "rules, schema (incl. dims / length_plus_girth_cm), and DQ quirks. "
            "(sibling of grounding-cue; see skill calling-the-shipping-agent.)"
        ),
        "skip_actors": DEFAULT_SKIP_ACTORS,
    },

    # --- entry #2: deploy / schema -------------------------------------------
    # Closes knowledge-miss regression cases 8 + 9 (the cheap sibling §X.4 left
    # open). Both are deploy-time hazards whose knowledge home is jebrim's deploy
    # bank notes, never loaded at the moment of the change:
    #   case 8 (S098): a serving change filtered on a NEW column before the data
    #     was regenerated -> filtered views 500'd while "All" worked. Rule: when a
    #     change adds a column the serving filters on, regenerate the data
    #     before/with the serving deploy.
    #   case 9 (S143): a deploy-critical FIF lookup caught by a blanket *.csv/data
    #     .gitignore was nearly architected-around. Rule: a gitignored deploy-
    #     critical config is a DEFECT to fix (scoped !negation), not a constraint.
    # Patterns are deploy-domain-specific (deploy/schema/migration/DAG/FIF/
    # gitignore/column-add) -- not bare "config"/"data" (wallpaper risk).
    {
        "name": "deploy-schema",
        "patterns": [
            r"\bdeploy",                          # deploy, deployment, deploying, deployed
            r"\bschema\b",
            r"\bmigration\b", r"\bmigrate",
            r"\bbackfill", r"\bregenerate\b",
            r"\bDAG\b",
            r"\bgitignore", r"\.gitignore\b",
            r"\bFIF\b",
            r"\bnew column\b", r"add(?:ing|ed)?\s+(?:a\s+)?column",
        ],
        "message": (
            "Deploy/schema topic detected (\"{matched}\"). Don't reason about deploy "
            "ordering from memory — jebrim's deploy bank notes are authoritative."
        ),
        # In-brain knowledge home (verified paths under this tree). No specialist —
        # these are notes to read, not a sub-agent's domain.
        "canonical_files": [
            "players/jebrim/bank/notes/projects/bi_analytics_deploy_topology.md",
            "players/jebrim/bank/notes/projects/scm_alerts_entity_split.md",
            "players/jebrim/bank/notes/projects/2026-05-28-ups-orwo-fif-data-quirks.md",
        ],
        "freshness": (
            "Deploy topology evolves with each serving change — re-read before a "
            "schema/serving deploy rather than trusting a remembered ordering."
        ),
        "read_before": (
            "Before changing a serving schema, adding a column a view filters on, "
            "scheduling a DAG, or touching a deploy-time config, load the canonical "
            "notes. Two load-bearing rules they hold: (1) when a change adds a column "
            "the serving FILTERS on, regenerate the data before/with the serving "
            "deploy, else filtered views 500 while 'All' works (S098); (2) a deploy-"
            "critical config/lookup caught by a blanket *.csv/data .gitignore is a "
            "DEFECT to fix with a scoped !negation, not a constraint to architect "
            "around (S143 FIF)."
        ),
        # These three notes are small + in-tree (~7.5 KB total), so their CONTENTS
        # are force-inlined once per session per domain — the §X.4 keepsake move
        # applied to domain knowledge. (Shipping deliberately has NO inline_homes:
        # its home is an external repo / large reference set; it stays name-only and
        # routes to the specialist instead.)
        "inline_homes": [
            "players/jebrim/bank/notes/projects/bi_analytics_deploy_topology.md",
            "players/jebrim/bank/notes/projects/scm_alerts_entity_split.md",
            "players/jebrim/bank/notes/projects/2026-05-28-ups-orwo-fif-data-quirks.md",
        ],
        "skip_actors": DEFAULT_SKIP_ACTORS,
    },

    # --- add the next domain here as one row ---------------------------------
    # Worked example (commented = inert until a real knowledge home is confirmed):
    #
    # {
    #     "name": "eu-tender",
    #     "patterns": [r"\beu[_ -]?tender\b", r"\btender 2026\b", r"\bincumbent\b"],
    #     "message": (
    #         "EU tender topic detected (\"{matched}\"). The canonical tender docs are "
    #         "authoritative — don't reason about carrier status from memory."
    #     ),
    #     "canonical_files": [
    #         "docs/ (the canonical tender doc set)",
    #         "players/jebrim/bank/notes/projects/eu_tender_2026.md",
    #     ],
    #     # no specialist — files to read, not a sub-agent's domain.
    #     "freshness": (
    #         "Per-carrier status tables DRIFT as replies land — re-read before "
    #         "stating any carrier's status; run the Step-8 cascade if you touch them."
    #     ),
    #     "read_before": (
    #         "Load the canonical docs + tender bank note before reasoning about "
    #         "carrier status, pricing, or round state."
    #     ),
    #     "skip_actors": DEFAULT_SKIP_ACTORS,
    # },
]
