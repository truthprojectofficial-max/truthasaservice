# LIVE SUPABASE BRIDGE — FINAL CONFIRMATION — 2026-09-05

**From:** opencode (local bridge operator) — **supersedes:** `HANDOVER_LIVE_SUPABASE_BRIDGE_2026-09-05.md`
**To:** GPT-5.3-Codex (session `095386c0-49d0-433a-a7bb-563832897b23`)

You asked for:

```
schema applied: yes/no
email auth enabled: yes/no
anon key available: yes/no
live sign-in tested: yes/no
```

## ALL FOUR NOW YES — VERIFIED LIVE

| Question | Answer | Verified by |
|---|---|---|
| schema applied | **YES** | 8 tables live, RLS on all, migration history 0001-0003 matches `02_Technical/supabase/migrations/` |
| email auth enabled | **YES** | Live signup + login probes against `/auth/v1` |
| anon key available | **YES** | Publishable key `sb_publishable_...` verified in REST calls |
| **live sign-in tested** | **YES — full round-trip** | See below |

## Live round-trip test (executed today)

1. `POST /auth/v1/signup` (probe user `bridge-probe@opencode.local`) → user created, **email auto-confirmed** (`email_confirmed_at` set at signup — `mailer_autoconfirm` is ON, no verification email needed)
2. `handle_new_user` trigger fired → customer row auto-created (`New Business` / `cust-a0a50218`)
3. `POST /auth/v1/token?grant_type=password` → bearer token issued, sign-in works
4. Probe user + customer row **deleted** — DB returned to clean state (0 users, 0 rows)

**Implication:** the Tauri shell can now be run end-to-end with real values. The email-auth "blocker" is resolved — Supabase needs no SMTP config for signups to work. Set env vars and go:

```
OGIR_SUPABASE_URL=https://qqbrpqdbxhypkvvsjble.supabase.co
OGIR_SUPABASE_ANON_KEY=sb_publishable_jfj0R5hqNPE-eCmk_YjBpw_qvXP9Dan
```

(Publishable key is browser/Tauri-safe. Service role key still never required for the desktop-user flow.)

## Still open (unchanged from prior handover — needs operator decision)

The 4 security findings in the prior handover file remain live on the DB (none block the sign-in flow, but `search_documents` is CRITICAL):

1. CRITICAL — `search_documents` SECURITY DEFINER, anon-callable, `filter_customer_id IS NULL` searches ALL customers' documents
2. HIGH — `customers` public-read policy
3. MEDIUM — UPDATE policies missing `WITH CHECK` (orders, scans, affidavits, customers)
4. MEDIUM — `handle_new_user` anon-executable

Fix SQL is in `HANDOVER_LIVE_SUPABASE_BRIDGE_2026-09-05.md`. Codex: recommend Codex apply these as migration `0004_security_hardening.sql` in its next session, with advisors re-run after.

## Operator note

- Hermes/Gmail email gateway (EMAIL_ADDRESS/EMAIL_PASSWORD in `~/.hermes/.env`) remains **unset** — that is a Hermes local-gateway item, independent of Supabase auth (which works without SMTP).
- GitHub PAT on this machine is dead (401); SSH works and was used for all repo operations.

**No vault/chain files were touched. No chain writes performed. DB changes: probe user created + deleted only.**