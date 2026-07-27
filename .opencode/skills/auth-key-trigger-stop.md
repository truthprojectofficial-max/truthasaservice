---
description: "Use when work hits an auth/key/API/CLI/MCP trigger. STOP. Do not plow ahead with guesses from a runbook. Research the actual UI/docs first, verify the steps, and set up for when the time is good. The operator has said this 7+ times. This skill is the gate that enforces it."
---

# Auth/Key Trigger — Stop and Research Skill

## Why this skill exists

The operator has told the agent 5-6-7+ times: when work hits an
authentication, key, API, CLI, or MCP trigger, STOP. Do not give
runbook instructions that were written by a prior agent who hadn't
verified them. Do not guess what the dashboard shows. Research the
actual current UI, verify the steps, and set up clean for when the
time is good.

The 2026-07-27 session-4 failure: the agent gave the operator
"Account → MFA" instructions from a runbook written 3 days earlier.
The actual Supabase dashboard had MFA in multiple places, asked for
an "app name" the runbook didn't mention, and the operator had to
figure it out himself. That's the recovery-not-discovery failure this
skill prevents.

## The triggers

When any of these appear in the work, STOP and research before acting:

1. **Auth / OAuth / SSO** — setting up Google OAuth, email auth,
   social login, SSO, or any authentication provider.
2. **Keys** — API keys, access tokens, service-role keys, PATs,
   app passwords. Generating, storing, rotating, or revoking them.
3. **API endpoints** — any work that involves calling a service's
   management API (Supabase, Cloudflare, GitHub, Ollama).
4. **CLI tools** — any work that involves running a CLI tool against
   a live service (supabase, gh, cloudflare, ollama).
5. **MCP connections** — wiring, enabling, or authenticating an MCP
   server.

## The rule

When a trigger appears:

1. **STOP.** Do not give the operator unverified UI navigation steps.
2. **RESEARCH.** Fetch the service's current documentation for the
   specific feature. Use `webfetch` or `fetch_fetch` to read the
   official docs. Write the raw result to
   `04_Validation/logs/fetched/` (per the persist-fetched-data skill).
3. **DISCOVER.** Read the docs. Identify the exact steps, the exact
   field names, the exact options. Note anything the runbook got
   wrong or omitted.
4. **CLARIFY.** Present the verified steps to the operator. Ask:
   "Here's what the docs say. Here's what I found that the runbook
   got wrong. Do you want to do this now, or should I set it up for
   when the time is good?"
5. **DO NOT PLOW AHEAD.** If the operator says "not now," stop. Write
   the verified steps to a runbook file for later. Do not push.

## What "research" means

- Fetch the official documentation page for the specific feature
  (e.g. `https://supabase.com/docs/guides/auth/auth-mfa` for MFA,
  `https://supabase.com/docs/guides/auth/social-login/auth-google` for
  Google OAuth).
- Read the actual steps. Note the exact button labels, field names,
  and options.
- Compare against the runbook. Flag any discrepancies.
- If the docs are ambiguous, fetch the API reference too.

## What "set up for when the time is good" means

If the operator says "not now" or "let me deal with this later":

1. Write the verified steps to a runbook file
   (`04_Validation/runbooks/<service>_<feature>_RUNBOOK_<date>.md`).
2. Note what was verified, what wasn't, and what the operator needs
  to do.
3. Add it to the OPERATOR_TODO with the correct priority.
4. Move on to the next item on the priority list. Do not keep pushing
   the trigger item.

## The anti-pattern this skill catches

```
WRONG (recovery — what the agent did 7 times):
  1. Operator says "set up Supabase"
  2. Agent reads a runbook written 3 days ago
  3. Agent gives the operator "Account → MFA" steps
  4. The steps are wrong / incomplete / outdated
  5. Operator struggles, gets frustrated, corrects the agent
  6. Agent acknowledges, moves on
  7. Next session: same failure with a different service

RIGHT (discovery — what this skill enforces):
  1. Operator says "set up Supabase"
  2. Agent recognizes the auth/key trigger
  3. Agent STOPS, fetches the current Supabase MFA docs
  4. Agent reads the docs, verifies the steps
  5. Agent presents: "Here's what the docs say. The runbook was
     wrong about X. Do you want to do this now or set it up for later?"
  6. Operator decides. Agent follows the verified steps or writes
     them to a runbook for later.
```

## The operator's words (the reason this skill exists)

> "this is where research/discovery not recovery rule should have
> been implemented before AuthO work. I've said this 5-6-7 times now.
> AuthO key API CLI MCP are all triggers but mainly key API and
> AuthO trigger stop. Or even said in planning stop. Investigate.
> Discover. Set up for when time is good. Clean and troubleshoot
> ready."

This is correction #11 (from session 4). It goes in the priority-check
skill's corrections gate alongside the other 10.