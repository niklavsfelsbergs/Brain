# Shipping-agent — colleague onboarding message

**As-of:** 2026-05-27. Reusable paste-in message for onboarding a new person to the shipping agent via the Claude app. Stored here (not in `shipping-agent/` itself) so it's retrievable on principal cue without shipping the canned message + credential inside the agent repo. Source: built in a Jebrim session for the 2026-05-26 shipping-agent presentation; delivery preamble (open app / open folder / paste) added 2026-05-27 per principal ([[S101_612683db_shipping-agent-access-split|S101]]).

## What it is

A single message a colleague pastes into Claude Code (after installing the Claude app and opening it in a code folder). It clones the repo, writes `.env`, installs deps, smoke-tests the Redshift connection, and ends by pitching what the agent can do. Fully hands-off — the colleague provides nothing.

## How to share it (delivery preamble)

Give the colleague these three steps first — they get them to the paste point:

1. Open the Claude app → navigate to **</> Code**.
2. Open the folder where you want the agent to live (Documents, or some working folder of yours).
3. Paste the message below and let Claude walk you through the setup.

## The message (send verbatim)

```
You're installing the Shipping Data Mart agent from scratch on this machine. Do
the whole setup yourself, and when it works, tell me what you can do.

1. Check git and Python 3 are installed (git --version, python --version). If
   either is missing, tell me how to install it on this machine and stop here.
2. Clone the repo into the current folder:
   git clone https://github.com/picanova/shipping-agent.git
   If a GitHub sign-in prompt appears, I'll log in with the account that has
   access to this repo. Then move into the shipping-agent folder.
3. Create a .env file in the shipping-agent folder with exactly these two lines:
   REDSHIFT_USER=ship_mart_ro
   REDSHIFT_PASSWORD=ShpMart_Ro!7xQ2vK9pLm
4. Install dependencies: python -m pip install -r requirements.txt
5. Smoke-test the connection:
   python harness/connect_redshift.py --query "SELECT 1"
   If it fails, tell me whether it looks like a credentials or a network/VPN
   problem, and what to do next.
6. Read how_to.md so you know your rules and scope.
7. Finish by telling me: that setup is done and I should open the shipping-agent
   folder as my project to start asking questions, what this agent is, the kinds
   of questions I can ask, your limits (read-only, shipping_mart gold schema
   only), and 3 example questions I could ask right now.
```

## Prerequisites outside the message's control

- **Repo access.** `picanova/shipping-agent` is now org-owned (migrated off the personal `niklavsfelsbergs` account 2026-05-25). Access is governed by org/repo membership: colleagues need to be added to the repo (or be org members with access) and sign in to GitHub on first clone. No secrets live in the repo — the `ship_mart_ro` password is in this message — so granting internal members access is low-risk; full public visibility is a separate governance call now that Picanova owns it.
- **Redshift reachability.** Host is AWS `eu-central-1`. If it's VPN-only, step 5 is where that surfaces.

## Credential note

The `ship_mart_ro` password is embedded above. It's the read-only, gold-only mart user — blast radius is SELECT on `shipping_mart.*`. Acceptable for internal distribution; rotate this note if the password changes.
