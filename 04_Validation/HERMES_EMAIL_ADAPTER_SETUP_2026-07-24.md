# Hermes Email Adapter Setup — 2026-07-24

> Operator: Justin Barnett
> Email: JUSTINBARNETT1966@GMAIL.COM
> Hermes install: C:\Users\justo\AppData\Local\hermes\
> Config: .env at that path (line 377-385, all commented out)

## Why

Hermes can read your inbox (IMAP) and send alerts (SMTP) so it
notifies you when: chain seals land, tests fail, Worker health
changes, cert expiry approaches. This is the operator alert layer,
NOT part of the OGIR audit runtime (which stays air-gapped).

## Step 1 — Generate a Gmail App Password

Gmail requires an App Password (not your normal password) because
2FA is enabled on your account.

1. Go to https://myaccount.google.com/security
2. Under "Signing in to Google" → **2-Step Verification** (must be ON)
3. Scroll to **App passwords** → click
4. Name it: `hermes-email-adapter`
5. Copy the 16-character password it shows (format: `xxxx xxxx xxxx xxxx`)
6. Save it somewhere — you can't see it again

## Step 2 — Edit Hermes .env

File: `C:\Users\justo\AppData\Local\hermes\.env`

Find lines 377-385 (all commented with `#`). Uncomment and fill:

```
EMAIL_ADDRESS=JUSTINBARNETT1966@GMAIL.COM
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_POLL_INTERVAL=15
EMAIL_ALLOWED_USERS=JUSTINBARNETT1966@GMAIL.COM
EMAIL_HOME_ADDRESS=JUSTINBARNETT1966@GMAIL.COM
```

Replace `xxxx xxxx xxxx xxxx` with the App Password from Step 1
(spaces included, exactly as Google shows it).

## Step 3 — Install + start the email gateway

In a PowerShell terminal:

```powershell
hermes gateway setup
# Choose #9 (Email)
# Confirm the settings
# Save

hermes gateway install
hermes gateway start
```

## Step 4 — Verify

Send a test email to JUSTINBARNETT1966@GMAIL.COM from another
account with subject "OGIR TEST ALERT". Within 15 seconds Hermes
should see it (check `hermes gateway status`).

To send an outbound alert, ask Hermes:
"Send an email to JUSTINBARNETT1966@GMAIL.COM with subject TEST and body 'email adapter working'"

## What Hermes can do with email once wired

- Poll your inbox every 15 seconds for new mail
- Read, summarise, and respond to emails you forward to it
- Send alerts when: chain seals, test failures, Worker health
- Trigger OGIR scans from inbound email (future: a cron job that
  picks up emails with subject "SCAN:" and runs the audit)

## Security

- The App Password is stored in Hermes `.env` (not in the OGIR repo,
  not in git, not in OneDrive)
- Gmail App Passwords can be revoked at any time at
  https://myaccount.google.com/security → App passwords
- The email adapter is in the Hermes build layer, NOT in the OGIR
  runtime. The audit engine stays air-gapped.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Authentication failed" | Regenerate the App Password, make sure 2FA is ON first |
| "IMAP connection refused" | Check Gmail settings → POP/IMAP → IMAP must be enabled |
| Hermes doesn't see new mail | Check EMAIL_POLL_INTERVAL is uncommented, restart gateway |
| "Less secure app" warning | Not applicable — App Passwords bypass that warning |