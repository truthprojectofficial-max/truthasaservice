# Hermes Email Config + Initiating Directives

> Created 2026-07-24. Internal.
> What you must do to wire Hermes email, and what Hermes does once wired.
> Sealed to chain: `HERMES_EMAIL_INITIATION_2026_07_24`

---

## PART 1: WHAT YOU MUST DO (operator actions only)

These are the steps only you (Justin) can do. Hermes cannot do
these for you.

### Step 1: Generate a Gmail App Password (5 min)

1. Go to https://myaccount.google.com/security
2. Under "Signing in to Google" → confirm **2-Step Verification is ON**
3. Scroll to **App passwords** → click
4. Type the name: `hermes-email-adapter`
5. Copy the 16-character password it shows (format: `xxxx xxxx xxxx xxxx`)
6. You will NOT see it again — write it down

### Step 2: Fill in Hermes .env (2 min)

File: `C:\Users\justo\AppData\Local\hermes\.env`

Find lines 377-385 (all commented with `#`). Replace with:

```
EMAIL_ADDRESS=truth.project.official@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_POLL_INTERVAL=15
EMAIL_ALLOWED_USERS=truth.project.official@gmail.com
EMAIL_HOME_ADDRESS=truth.project.official@gmail.com
```

Replace `xxxx xxxx xxxx xxxx` with the App Password from Step 1.

### Step 3: Install the email gateway (2 min)

In PowerShell:

```powershell
hermes gateway setup
# Choose #9 (Email)
# Confirm the settings match above
# Save

hermes gateway install
hermes gateway start
```

### Step 4: Test it (1 min)

Send a test email to `truth.project.official@gmail.com` from
another account with subject "OGIR TEST ALERT". Within 15 seconds
Hermes should see it.

Then ask Hermes:
"Send an email to truth.project.official@gmail.com with subject
TEST and body 'email adapter working'"

### Step 5: Verify the gateway is running

```powershell
hermes gateway status
```

Should show Email as "running".

---

## PART 2: WHAT HERMES DOES ONCE WIRED (the directives)

### Hermes's email role in the OGIR system

Hermes is the **operator alert layer**, NOT part of the OGIR audit
runtime. The audit engine stays air-gapped. Hermes sits outside the
runtime, in the build layer, and does these things:

### What Hermes monitors (inbound email)

1. **New mail alerts** — Hermes polls the inbox every 15 seconds.
   When a new email arrives, Hermes can:
   - Summarise it
   - Flag it if it contains a client request (subject starts with "AUDIT:" or "SCAN:")
   - Alert the operator via the Hermes TUI

2. **Client intake** — when a client emails with a document to audit:
   - Hermes reads the email
   - Extracts the text attachment
   - Drafts a case card for the trial board
   - Alerts the operator "New case from <client>: <subject>"

### What Hermes sends (outbound alerts)

Hermes sends email alerts when these events happen:

| Event | Trigger | Email subject | Recipient |
|-------|---------|--------------|-----------|
| Chain seal | `vault_io.append_block` completes | `[OGIR] Block NNNNN sealed: EVENT_TYPE` | operator |
| Test failure | `pytest` returns non-zero | `[OGIR] TEST FAILED: N tests` | operator |
| Worker health | Health check returns non-200 | `[OGIR] Worker DOWN` | operator |
| Cert expiry | EV cert expires in <30 days | `[OGIR] EV cert expiring` | operator |
| Domain expiry | Domain expires in <60 days | `[OGIR] Domain expiring` | operator |
| Daily check | Cron at 8am | `[OGIR] Daily report: chain N blocks, N tests, Worker OK` | operator |
| Breach detected | NDB response plan triggered | `[OGIR] BREACH: <description>` | operator + OAIC |

### Hermes email directives (the rules Hermes follows)

1. **Only send to the operator** — `EMAIL_ALLOWED_USERS=truth.project.official@gmail.com`. No third-party recipients.
2. **Never email client data** — Hermes summaries the subject, never the audit content.
3. **Never email secrets** — no keys, passwords, tokens, or chain hashes in email bodies.
4. **Short and factual** — every alert is <160 characters where possible. "[OGIR] Block 40876 sealed: SYSTEM_WIDE_AUDIT_FIXES"
5. **No marketing** — Hermes never sends promotional emails. Only system alerts.
6. **Poll, don't push** — Hermes uses IMAP poll (15s interval), not push notifications. The inbox is read-only for Hermes; it never deletes or modifies emails.

### What Hermes does NOT do

- Hermes does NOT touch the OGIR runtime (`02_Technical/src/`)
- Hermes does NOT seal chain blocks directly (the operator or the engine does that)
- Hermes does NOT send emails on behalf of the operator without the operator asking
- Hermes does NOT read the chain (it reads the bark log instead — `04_Validation/scripts/last_seal.log`)
- Hermes does NOT access the Supabase DB or the Cloudflare account
- Hermes does NOT make decisions — it alerts, the operator decides

---

## PART 3: SEPARATION OF CONCERNS (filing this doc)

This document is filed at:
`04_Validation/HERMES_EMAIL_INITIATION_2026-07-24.md`

It is separate from:
- `HERMES_EMAIL_ADAPTER_SETUP_2026-07-24.md` (the technical setup steps)
- `HERMES_CONFIG_TODO_2026-07-24.md` (the persona + anti-fabrication config)
- `AGENT_SIGNOFF_POLICY_2026-07-24.md` (the sign-on/off protocol)

Each document has a single purpose:
- **SETUP doc** = how to install the email adapter (technical)
- **CONFIG doc** = how to muzzle Hermes (persona + guardrails)
- **INITIATION doc** = what Hermes does once wired (directives + role)
- **SIGNOFF doc** = how Hermes signs on and off (protocol)

No overlap. No confusion. File each separately.