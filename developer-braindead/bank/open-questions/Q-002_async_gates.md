# Q-002 — Async gates: what does "ask before irreversible" mean when the principal is unavailable?

**Status.** `working` — partial position landed as [[A-003]]. Opened in [[S001]].

User's position so far ([[A-003]]): HITL during build phase is fine; architecture must leave room for future autonomy. Open: the exact mechanism for "ask" when the user is asleep — block? queue and notify? messaging-bridge approval surface (Telegram-style)? Shape of decision affects Phase 2/3 substrate.
