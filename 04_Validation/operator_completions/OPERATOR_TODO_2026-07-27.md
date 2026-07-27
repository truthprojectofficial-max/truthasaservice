# OPERATOR TODO — What you need to do, in order, with how-to

> **This file is for you (Justin), not for the agent.** Last refreshed
> 2026-07-27. When you're done with an item, tick the box. When you
> don't understand one, come back and say "I didn't do X" — that's
> the system working.
>
> **Prioritized.** Do them top to bottom. The top ones block the most.

---

## PRIORITY 1 — Security (do today, 15 min)

### 1.1 Revoke the compromised Gmail App Password
**Why:** The password `szun yvie bnpb hran` touched a tracked file.
Even though it never went into git, treat it as stolen.
**How:**
1. Open `https://myaccount.google.com` (log in as
   truth.project.official@gmail.com)
2. Click **Security** (left sidebar)
3. Find **App passwords** (under "Signing in to Google")
4. Find `hermes-email-adapter` in the list → click **Delete**
**Done when:** the password is gone from Google's list.
**After:** don't generate a new one yet — do that in Priority 3
when you're ready to wire Hermes.

### 1.2 Enable 2FA on the 3 services that don't have it
**Why:** Your bus-factor is 1. If someone gets one password, they
get everything. 2FA is the second lock.
**How (Cloudflare):**
1. Go to `https://dash.cloudflare.com`
2. Click your profile (top right) → **My Profile**
3. Click **Authentication** → **Enable Two-Factor Authentication**
4. Follow prompts (need your phone)
**How (Supabase):**
1. Go to `https://supabase.com/dashboard`
2. Click your account (top right) → **Account Settings**
3. Look for **MFA** or **Two-Factor** → enable
**How (GitHub):**
1. Go to `https://github.com/settings/security`
2. Find **Two-factor authentication** → **Enable**
3. Follow prompts (need your phone or an authenticator app)
**Done when:** all 3 show 2FA as enabled.

---

## PRIORITY 2 — Password manager (do this week, 30 min)

### 2.1 Install Bitwarden and store all credentials
**Why:** You have 12+ accounts with passwords in your head and
plaintext files. One bus, everything dies. Bitwarden is free,
encrypted, and means you don't have to remember anything.
**How:**
1. Go to `https://bitwarden.com` → **Get Started** (free)
2. Create an account with a strong master password (write this
   one down on paper — it's the one password you can't recover)
3. Download the Bitwarden desktop app (Windows)
4. Add entries for every account from the password registry:
   `04_Validation/runbooks/PASSWORD_REGISTRY_AND_BCP_2026-07-24.md`
   — each one: name, username, password, URL
5. When done, shred the plaintext password notes
**Done when:** all accounts from the registry are in Bitwarden.

---

## PRIORITY 3 — Wire Hermes email (do when ready, 20 min)

> **Prerequisite:** Priority 1.1 done (old password revoked).
> **Read:** `04_Validation/runbooks/HERMES_EMAIL_ADAPTER_SETUP_2026-07-24.md`
> (this doc has been corrected — it now uses the project email and
> has real button-by-button paths, not "go find it")

### 3.1 Generate new Gmail App Password (project account)
**How:** Follow the corrected SETUP doc, Step 1. The email is
`truth.project.official@gmail.com` — NOT your personal one.

### 3.2 Fill in Hermes .env
**How:** Follow SETUP doc, Step 2. Open
`C:\Users\justo\AppData\Local\hermes\.env`, search for `EMAIL_`,
uncomment the lines, paste the new password. Save.

### 3.3 Enable IMAP in Gmail
**How:** Follow SETUP doc, Step 3. Gmail settings → Forwarding and
POP/IMAP → Enable IMAP → Save.

### 3.4 Start the gateway
**How:** Follow SETUP doc, Step 4. PowerShell:
`hermes gateway setup` → find Email in the menu → `hermes gateway
install` → `hermes gateway start` → `hermes gateway status`.

### 3.5 Test it
**How:** Follow SETUP doc, Step 5. Send yourself a test email.

### 3.6 Add the ogir-builder persona to Hermes
**How:** Open `C:\Users\justo\AppData\Local\hermes\config.yaml`.
Under `agent.personalities:`, add a new entry. Read
`04_Validation/runbooks/HERMES_CONFIG_TODO_2026-07-24.md` for the
exact text. Set `agent.personality: ogir-builder` and enable
`tool_loop_guardrails.hard_stop_enabled: true`.
**Done when:** `hermes gateway status` shows Email running and
Hermes has the ogir-builder persona active.

---

## PRIORITY 4 — Move repo out of OneDrive (do when you have a quiet hour)

### 4.1 Move to C:\OrderGetItRight
**Why:** OneDrive sync corrupted the vault once already. The vault
is the trust anchor — it can't be in a sync folder.
**How:** Read `04_Validation/runbooks/REPO_MOVE_RUNBOOK_2026-07-24.md`
— it has the full step-by-step. Summary: copy the folder to
`C:\OrderGetItRight`, verify chain + tests pass from the new
location, then exclude the old path from OneDrive sync.
**Done when:** `python -m src.verify_chain` runs from
`C:\OrderGetItRight` and says MATCH.

---

## PRIORITY 5 — Supabase hardening (do this week, 30 min)

### 5.1-5.7 Seven settings to flip
**How:** Read `04_Validation/runbooks/SUPABASE_RUNBOOK_2026-07-24.md`
and the Supabase section of the master tick list. Each item is one
button click in the Supabase dashboard. The runbook has the path
for each one.
**Items:** 2FA, SSL, email confirmations, Google OAuth, Tauri
redirect URL, RLS verify, DB password save.

---

## PRIORITY 6 — When the cert token arrives (1-2 weeks)

### 6.1 Export .pfx and wire GitHub secrets
**How:** Read the "WHEN CERT TOKEN ARRIVES" section of the tick
list. Plug in the USB token, export to .pfx, add 2 GitHub secrets,
push the v0.1.0 tag.
**Done when:** GitHub Actions builds + signs the Windows installer
automatically.

---

## PRIORITY 7 — Before public launch

### 7.1-7.8 The launch checklist
**Items:** Upgrade Supabase to Pro, make repo public, enable GitHub
Pages, set repo description + topics, update profile bio, print
business cards, set up email signature.
**How:** Each one is in the master tick list with the URL to go to.

---

## AGENT TODO — what the next build session should do (prioritized)

> These are NOT operator items. These are what the agent works on
> when you say "continue."

1. ~~**Permission profiles in opencode.json**~~ DONE (session 3) —
   read-only "reasoning" agent added, build agent stays full-permission.
2. ~~**MCP skills from project knowledge**~~ DONE (session 3) — 22
   skills built (16 from patterns + heavy-lifting + 5 existing).
   8 MCP servers wired (memory, git, sequential-thinking, github,
   filesystem, fetch, time, supabase-disabled).
3. ~~**Operator completion file automation**~~ DONE (session 3) —
   `04_Validation/scripts/generate_operator_todo.py` built and tested.
4. **The 2 AI-dialect false negatives** — Hedged Authority +
   Fabricated Output patterns. Research done (DD-070 Authority Mimicry
   + DD-071 Work-Claim Without Evidence proposed). See
   `04_Validation/methodology_calibration/AI_DIALECT_FALSE_NEGATIVES_RESEARCH_2026-07-27.md`.
   Next: write the patterns + eval cases + calibrate + code review.
5. **Tauri-Supabase sync code** — schema exists, app has no sync.
6. **Automation layer** — cron backups, health checks, dead-man's
   switch (depends on Priority 3 Hermes being wired).
7. **STARTUP_GUIDE rewrite** — operator said it imposed conditions
   and was too long. Rewrite as a slim one-page reference.
8. **Firecrawl investigation** — who they are, legitimacy, how they
   got operator's details. Research started (website fetched), report
   not yet written.
9. **GRPO/corporate intent research** — from the SEARCH CONVO file.
   Turn into OGIR methodology or skill.
10. **Truth Engine dashboard** — operator wants to talk about it
    before building. The React component from the Melvin file.
11. **Auctus business plan** — DONE (session 3). Written to
    `BUSINESS_PLAN_OGIR_2026-07-27.md`. Operator to review.

---

## WHAT WAS DONE THIS SESSION (session 3, 2026-07-27)

- SIGN_ON block 40966. Chain MATCH at 40,962. Tests 404 passed.
- Built 16 opencode skills from 38 inventoried patterns (8 critical +
  6 high + 2 medium). 22 total skills now. Sealed SKILLS_BUILD (40970).
- Added read-only "reasoning" agent to opencode.json (edit/bash/todowrite/
  task/external_directory = deny). Build agent stays full-permission.
- Built heavy-lifting skill (agent does terminal/automation work).
- Created operator todo auto-generator script
  (`04_Validation/scripts/generate_operator_todo.py`).
- Wrote AI-dialect false negatives research (DD-070 + DD-071 proposed,
  no code changes). Sealed PERMISSION_PROFILES_AND_HEAVY_LIFTING (40990).
- Wired 4 new MCP servers (github, filesystem, fetch, time). Supabase
  wired but disabled (needs OAuth). 8 total. Sealed MCP_SERVERS_EXPANDED
  (40994).
- Pushed all commits to GitHub (first push — PAT stored in Windows
  Credential Manager, GIT_CONFIG_NOSYSTEM=1 to bypass system GCM).
- Wrote Auctus business plan (`BUSINESS_PLAN_OGIR_2026-07-27.md`).
- Read all 10 files in Documents\My Project\. Identified: Firecrawl
  email, GRPO research, Truth Engine dashboard, Auctus pitch.
- Operator rotated GitHub PAT (exposed in terminal output earlier).
- Firecrawl research started (website fetched, report not written).
- Chain: 40,994 blocks, MATCH. Tests: 404 passed, 4 skipped, 0 failed.

## WHAT'S BROKEN
- Nothing. Chain MATCH. Tests pass.

## CHAIN STATE: MATCH at 40,994 blocks
## TEST STATE: 404 passed, 4 skipped, 0 failed
## GIT: Pushed to origin. Uncommitted: business plan (outside repo),
  Firecrawl research (not yet written).