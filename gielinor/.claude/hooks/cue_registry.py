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
#   name         str        short id; used in the ritual-log event + the nudge header.
#   patterns     list[str]  raw regex strings (compiled case-insensitively by the hook).
#                           Narrow on purpose: a false positive costs one advisory
#                           line, but over-firing turns the nudge into wallpaper.
#   message      str        the nudge body injected as additionalContext.
#   skip_actors  tuple[str] per-session actors for whom this entry does NOT fire
#                           (read from the status sidecar). Default skips braindead
#                           (the dev brain builds the brain, not domain analysis).
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
            "Shipping/mart topic detected (\"{matched}\"). Before writing SQL or "
            "interpreting any shipping_mart figure: load `shipping-agent/how_to.md` §0 "
            "+ `reference/{{mart-contract,tables}}.md`, OR spawn the shipping-agent "
            "(subagent_type: shipping-agent), which loads the rulebook by construction. "
            "Don't reason about the mart from memory — the contract holds the cost-basis "
            "rules, schema (incl. dims / length_plus_girth_cm), and DQ quirks. "
            "(sibling of grounding-cue; see skill calling-the-shipping-agent.)"
        ),
        "skip_actors": DEFAULT_SKIP_ACTORS,
    },

    # --- add the next domain here as one row ---------------------------------
    # Worked example (commented = inert until a real knowledge home is confirmed):
    #
    # {
    #     "name": "eu-tender",
    #     "patterns": [r"\beu[_ -]?tender\b", r"\btender 2026\b", r"\bincumbent\b"],
    #     "message": (
    #         "EU tender topic detected (\"{matched}\"). Load the canonical docs/ "
    #         "+ players/jebrim/bank/notes/projects/eu_tender_2026.md before "
    #         "reasoning about carrier status — the per-carrier tables drift; "
    #         "run the Step-8 cascade if you touch them."
    #     ),
    #     "skip_actors": DEFAULT_SKIP_ACTORS,
    # },
]
