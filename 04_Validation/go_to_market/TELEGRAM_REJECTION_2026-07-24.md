# Telegram Gateway Rejection — Sealed Decision

> Sealed: 2026-07-24
> Decision: Telegram is REJECTED as an OGIR Hermes gateway.
> Operator quote: "telegram is a drug selling app"
> This decision is sealed to the chain so it cannot be silently
> reintroduced.

## The decision

Telegram will NOT be used as a Hermes gateway platform for OGIR.
The operator assessed Telegram as unsuitable ("a drug selling app")
and directed that the email adapter be used instead.

## What this means

1. The `TELEGRAM_BOT_TOKEN` and related env vars in Hermes `.env`
   (lines 359-368) will remain commented out. Do NOT fill them in.
2. Hermes email adapter (IMAP/SMTP via Gmail App Password) is the
   chosen alert path. See `HERMES_EMAIL_ADAPTER_SETUP_2026-07-24.md`.
3. If a future agent suggests Telegram as an alert channel, this
   decision takes precedence. Reversal requires operator approval
   + a sealed `TELEGRAM_RECONSIDERED` block.
4. The Telegram platform slot in Hermes config remains unused.

## Why email was chosen over Telegram

- Email is universal — every client has email, not everyone has Telegram
- Email is auditable — IMAP leaves a trail, Telegram messages vanish
- Email works through Starlink + Vodafone tether without a separate app
- The operator rejected Telegram on principle, not on technical grounds

## What about SMS?

SMS via Twilio is the backup if true offline-capable alerts are
needed. See `HERMES_EMAIL_INITIATION_2026-07-24.md` section on
Twilio. Cost: ~$1-2/mo + $0.05/msg. Not wired yet — deferred until
the operator decides offline alerts are needed.