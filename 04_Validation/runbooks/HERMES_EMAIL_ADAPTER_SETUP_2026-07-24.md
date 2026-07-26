# Hermes Email Adapter Setup — 2026-07-24

> Operator: Justin Barnett
> **Email: truth.project.official@gmail.com (PROJECT account — not personal)**
> Hermes install: `C:\Users\justo\AppData\Local\hermes\`
> Config: `.env` at that path (search for `EMAIL_` — lines may shift, do not rely on line numbers)

## Why

Hermes can read your inbox (IMAP) and send alerts (SMTP) so it
notifies you when: chain seals land, tests fail, Worker health
changes, cert expiry approaches. This is the operator alert layer,
NOT part of the OGIR audit runtime (which stays air-gapped).

## Step 1 — Generate a Gmail App Password

Gmail requires an App Password (not your normal password) because
2FA is enabled on your account.

1. Open your browser, go to: `https://myaccount.google.com`
2. Click **Security** (left sidebar, icon looks like a shield)
3. Scroll down to the section titled **"Signing in to Google"**
4. Confirm **2-Step Verification** shows as **ON**. If it says OFF,
   click it, follow Google's setup, come back here.
5. In the same "Signing in to Google" section, find **App passwords**
   (it's below 2-Step Verification). Click it.
6. You may need to re-enter your Google password.
7. In the "App name" box, type: `hermes-email-adapter`
8. Click **Create**
9. Google shows a 16-character password in yellow (format:
   `xxxx xxxx xxxx xxxx`). **Copy it exactly, spaces included.**
10. **IMPORTANT: Paste it ONLY into the Hermes `.env` file (Step 2
    below). Do NOT paste it into this doc, any doc, any chat, any
    email, any file that is git-tracked. The `.env` is gitignored.
    That is the only safe place for it.**
11. You will NOT see this password again. If you lose it, delete
    it in Google and generate a new one.

## Step 2 — Edit Hermes .env

File: `C:\Users\justo\AppData\Local\hermes\.env`

Open it in Notepad or your editor. Press Ctrl+F, search for
`EMAIL_ADDRESS`. If the lines are commented out (start with `#`),
remove the `#`. Set them to:

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

Replace `xxxx xxxx xxxx xxxx` with the App Password from Step 1
(spaces included, exactly as Google shows it).

**Save the file. Do not commit it — it is in the Hermes install
directory, which is outside the git repo and gitignored.**

## Step 3 — Enable IMAP in Gmail

1. Open `https://mail.google.com` (log in as
   truth.project.official@gmail.com)
2. Click the **gear icon** (top right) → **See all settings**
3. Click the **Forwarding and POP/IMAP** tab
4. Find **IMAP access** section → select **Enable IMAP**
5. Click **Save Changes** at the bottom

If you skip this, Hermes will get "IMAP connection refused."

## Step 4 — Install + start the email gateway

In a PowerShell terminal:

```powershell
hermes gateway setup
```

This opens a menu. Look for the option labelled **Email** (it may
not be #9 — the menu order changes between Hermes versions). Select
it. Confirm the settings match what you put in `.env`. Save.

```powershell
hermes gateway install
hermes gateway start
```

Then verify it's running:

```powershell
hermes gateway status
```

Should show Email as "running".

## Step 5 — Test it

Send a test email to `truth.project.official@gmail.com` from
another account (e.g. your personal Gmail) with subject
"OGIR TEST ALERT". Within 15 seconds Hermes should see it
(check `hermes gateway status`).

To test outbound, ask Hermes:
"Send an email to truth.project.official@gmail.com with subject
TEST and body 'email adapter working'"

## What Hermes can do with email once wired

- Poll the project inbox every 15 seconds for new mail
- Read, summarise, and respond to emails you forward to it
- Send alerts when: chain seals, test failures, Worker health
- Trigger OGIR scans from inbound email (future: a cron job that
  picks up emails with subject "SCAN:" and runs the audit)

## Security

- The App Password is stored ONLY in Hermes `.env`
  (`C:\Users\justo\AppData\Local\hermes\.env`) — NOT in the OGIR
  repo, NOT in git, NOT in OneDrive, NOT in any doc.
- Gmail App Passwords can be revoked at any time at
  `https://myaccount.google.com` → Security → App passwords
- The email adapter is in the Hermes build layer, NOT in the OGIR
  runtime. The audit engine stays air-gapped.
- **The prior App Password `szun yvie bnpb hran` is COMPROMISED** —
  it touched a tracked file. Delete it in Google App Passwords
  before generating the new one.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Authentication failed" | Regenerate the App Password, make sure 2FA is ON first |
| "IMAP connection refused" | Gmail settings → Forwarding and POP/IMAP → Enable IMAP → Save |
| Hermes doesn't see new mail | Search .env for `EMAIL_POLL_INTERVAL`, make sure it's uncommented, restart gateway |
| "Less secure app" warning | Not applicable — App Passwords bypass that warning |
| Can't find "App passwords" in Google | 2-Step Verification must be ON first. It only appears after 2FA is enabled |