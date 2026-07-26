# MASTER TICK-LIST — 2026-07-24

> Print this. Tick it off. When all are done, destroy this file and
> write a new one. This is the operator's action list, not the
> agent's. The agent (me) can't do these — only you can.

---

## CRITICAL — do tonight (5 min)

- [ ] Revoke GitHub PAT → https://github.com/settings/tokens → delete `github_pat_11CH7NUY...`
- [ ] Revoke OpenAI key → https://platform.openai.com/api-keys → delete `sk-svcacct-ou0TD1H...`
- [ ] Revoke Ollama key → https://ollama.com/settings → delete `380b8fa6...`

---

## THIS WEEK (when back from Adelaide)

### Supabase (see SUPABASE_RUNBOOK_2026-07-24.md)
- [ ] Enable 2FA → Dashboard → Account → MFA
- [ ] Enable SSL → Dashboard → Database → Settings → SSL → ON
- [ ] Enable email confirmations → Dashboard → Auth → Providers → Email
- [ ] Enable Google OAuth → Dashboard → Auth → Providers → Google → paste Client ID
- [ ] Set Tauri redirect URL → Dashboard → Auth → URL Configuration → add `ordergetitright://auth/callback`
- [ ] Verify RLS → SQL Editor → run the check query
- [ ] Save/reset DB password → Dashboard → Settings → Database

### Cloudflare
- [ ] Verify WHOIS privacy ON → https://dash.cloudflare.com → Registrar → WHOIS Privacy

### Hermes (see HERMES_EMAIL_ADAPTER_SETUP_2026-07-24.md + HERMES_CONFIG_TODO_2026-07-24.md)
- [ ] Generate Gmail App Password → https://myaccount.google.com/security → 2-Step Verification → App passwords
- [ ] Fill in .env EMAIL_* vars → `C:\Users\justo\AppData\Local\hermes\.env` lines 377-385
- [ ] Add `ogir-builder` persona → edit `config.yaml` under `agent.personalities`
- [ ] Set `agent.personality: ogir-builder` in config.yaml
- [ ] Switch model to `qwen2.5-coder` → edit `config.yaml` `model.default`
- [ ] Enable `tool_loop_guardrails.hard_stop_enabled: true` in config.yaml
- [ ] Tighten hard_stop thresholds (exact_failure: 3, idempotent_no_progress: 3)
- [ ] Start email gateway → `hermes gateway setup` → #9 → `hermes gateway install` → `hermes gateway start`

### GitHub
- [ ] Create new PAT → https://github.com/settings/tokens → name `ogir-local-push` → 90-day expiry

### Repo (when you have time — not urgent but important)
- [ ] Move repo out of OneDrive → copy to `C:\OrderGetItRight` → verify chain + tests → exclude old path from sync

---

## WHEN CERT TOKEN ARRIVES (1-2 weeks)

- [ ] Plug in USB token (Certera eToken)
- [ ] Export to .pfx (with private key)
- [ ] Add GitHub secret `WINDOWS_CERTIFICATE` (base64 of .pfx)
- [ ] Add GitHub secret `WINDOWS_CERTIFICATE_PASSWORD`
- [ ] Push release tag: `git tag v0.1.0 && git push origin v0.1.0`
- [ ] Verify: GitHub Actions builds + signs the Windows installer

---

## BEFORE PUBLIC LAUNCH

- [ ] Supabase: upgrade to Pro ($25/mo, auto-deducted) → kills 7-day pause + daily backups
- [ ] Supabase: add card for auto-deduction → Dashboard → Org → Billing → Payment methods
- [ ] GitHub: make repo public
- [x] Add LICENSE file (MIT) — DONE
- [x] Write `.github/copilot-instructions.md` — DONE
- [x] Set up Aider sandbox at `C:\AIDERTESTBOX` — DONE
- [x] Create landing page (`docs/index.html` for GitHub Pages) — DONE
- [ ] Enable GitHub Pages (repo Settings → Pages → /docs → ordergetitright.com)
- [ ] GitHub: set repo description + topics (forensics, audit, deception-detection, merkle-chain, tauri, python, open-source)
- [ ] GitHub: update profile bio ("Verified Processor — building OGIR, a forensic lie-detector")
- [ ] Print business cards (~$20 Vistaprint)
- [ ] Set up email signature

---

## BOOK WORK (from due diligence scan, 2026-07-24)

### Dropped items — now filed
- [x] Telegram rejection sealed (TELEGRAM_REJECTION_2026-07-24.md) — DONE
- [ ] Invoice/payment record storage schema — not built. Need a `invoices` table when paying clients start
- [ ] Supabase/OGIR operator training course — not created. The runbook IS the training material for now
- [ ] Run ALL 160+ corpus files through the engine — only samples run. Future: bulk-process via API

### Partial items — still open
- [ ] EV cert receipt: stored in 04_Validation/Signmycode.pdf — keep for tax
- [ ] Domain receipt: stored in 04_Validation/ordergetitright.com_ownership_letter.pdf.crdownload — keep for tax
- [ ] SmartScreen reputation building: EV cert gives immediate reputation (no OV waiting period). Already covered by the EV purchase
- [ ] GitHub maintainer type: currently individual (truthprojectofficial-max). Switch to org when you register Pty Ltd
- [ ] Automation policy: cron backups, health checks, dead-man's switch — NOT WIRED. All manual. Future work

### Due diligence scorecard
- 22 of 33 topics: DONE
- 9 of 33 topics: PARTIAL (operator action needed)
- 4 of 33 topics: DROPPED (now filed — 1 sealed, 3 deferred)
- 0 NOT ANSWERED

---

## MONTHLY (set calendar reminders)

- [ ] Check Supabase usage → Dashboard → Home (DB size, MAU, egress)
- [ ] Check Cloudflare usage → Dashboard → Analytics
- [ ] Check GitHub Actions → repo → Actions tab
- [ ] Run Supabase backup → `supabase db dump --data-only -f backup.sql` (Free tier)
- [ ] Check for unexpected Supabase signups → Dashboard → Auth → Users
- [ ] Verify chain → `python -m src.verify_chain` → must be MATCH

---

## NEVER DO

- [ ] ~~Edit audit rows in Supabase Table Editor~~
- [ ] ~~Use Supabase Edge Functions~~
- [ ] ~~Add network imports to 02_Technical/src/~~
- [ ] ~~Touch 03_Vault/ or 04_Validation/hardcopy/ manually~~
- [ ] ~~Run Hermes without ogir-builder persona~~
- [ ] ~~Push .env, .pfx, or any key to git~~
- [ ] ~~Run git push --force~~
- [ ] ~~Store the vault in OneDrive (move it)~~