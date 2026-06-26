# Don't ship blank/placeholder columns when the real data is reachable by another path

**Observation ([[S372_0888690d_orwo-wolfen-returns|S372]], 2026-06-26).** Building the DHL-meeting Excel, the Redshift MCP disconnected mid-session. I added the requested invoice-detail columns (invoice number, ident, dates, weight) but left them as `—` placeholders, reasoning "can't fabricate lookup keys, the live export fills them later." Niklavs' reaction: *"wtf no invoice number? all the new columns are blank."*

**What was wrong.** The MCP being down is not the same as "can't query." A prior ORWO session had already established the fallback: connect to Redshift **directly** via `redshift_connector` with the `tcg_nfe` creds in `NFE/.env` (host/port/db from `brain/.mcp.json`'s connection string). I had that pattern in my own resume/comms history and didn't reach for it — I accepted the degraded artifact instead of exhausting the path to the real data. Once I did connect, the full 14,522-line export landed in minutes.

**The lesson.** When a primary data tool fails, **exhaust the alternate paths to the real data before shipping a degraded deliverable** — especially when a fallback is already documented in my own history. A placeholder-filled artifact handed to the principal reads as "didn't do the work," even when the reasoning (don't fabricate keys) was locally sound. The right move was: pull real, or say "I can't get this until X" — not ship blanks framed as "pending."

**Related.** [[feedback_check_own_memory_before_working_repo]] (the fallback was in my own record), the verify-the-thing reflex. Also surfaced a real formatting bug the same turn (euro `#,##0` rounded €3.35→€3) — small-magnitude euro columns need 2dp.
