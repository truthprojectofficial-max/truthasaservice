# Password / Access Registry + Business Continuity Plan (BCP)

> Created 2026-07-24. Internal — NOT for clients, NOT for public.
> The "hit by bus" document. If Justin is gone tomorrow, this is
> how the business survives.
> Sealed to chain: `PASSWORD_REGISTRY_AND_BCP_2026_07_24`

---

## CRITICAL — DO THIS FIRST

The OpenAI key `sk-svcacct-ou0TD1H...` is **still live in plaintext**
at `C:\Users\justo\AppData\Local\hermes\.env` line 498. It was purged
from the git repo but NOT from the Hermes install. **Revoke it now**
at https://platform.openai.com/api-keys, then delete line 498 from
the Hermes .env.

---

## PART 1: Password / Access Registry

Every account that keeps OGIR running. Where the credential lives,
who has it, what happens if Justin is gone.

### Format: Account → Credential location → Bus factor

| # | Service | What it controls | Credential location | Who has it | If Justin is gone |
|---|---------|-----------------|-------------------|------------|-------------------|
| 1 | **Cloudflare** | Domain (ordergetitright.com), Workers, R2, KV | Email login at dash.cloudflare.com. 2FA status UNKNOWN. | Justin only | Domain lapses 2027-07-24, Worker goes dark, nobody can deploy |
| 2 | **Supabase** | Postgres DB, Auth, 3 tables | Email login at supabase.com. DB password NOT saved in a password manager. 2FA NOT enabled. | Justin only | DB pauses after 7 days inactivity, then auto-purge risk |
| 3 | **Google Cloud Console** | OAuth client (Drive picker) | Email login at console.cloud.google.com. Client Secret not needed (PKCE). | Justin only | OAuth client orphaned, Drive import breaks |
| 4 | **GitHub** | Source repo, Actions CI/CD, 10 secrets | Account `truthprojectofficial-max`. PAT leaked in git history (NOT revoked yet). 2FA status UNKNOWN. | Justin only | Repo goes orphan, nobody can push or set secrets |
| 5 | **SignMyCode/Certera** | Windows EV code signing cert (1 year) | Customer ID #1015571. USB token shipping to Whyalla Norrie. .pfx password will be set by Justin. | Justin only | Cert unrenewable in 2027-07, nobody can sign Windows builds |
| 6 | **Ollama** | Cloud LLM subscription (Pro/Max) | Email login at ollama.com/settings. API key leaked (NOT revoked yet). | Justin only | Subscription continues billing until card expires |
| 7 | **OpenAI** | (if still active) API key | **STILL LIVE in Hermes .env line 498.** Leaked in git history. NOT revoked. | Justin only | Anyone with git history has free OpenAI access |
| 8 | **Hermes** | Agent framework, email adapter, all tool configs | `C:\Users\justo\AppData\Local\hermes\.env` (plaintext, 25KB). Contains the live OpenAI key. | Justin only | Agent framework inaccessible |
| 9 | **OneDrive** | Backs up the source tree (corrupts the vault) | Microsoft account. | Justin only | Sync stops, last-known state frozen |
| 10 | **Bank card** | Auto-charges: Ollama ($20/mo), Supabase Pro ($25/mo when upgraded), Cloudflare ($0), domain renewal (~$10/yr) | Bank details at the bank. | Justin only | Auto-charges continue until card expires or is cancelled |
| 11 | **Tauri updater private key** | Signs update binaries | `02_Technical/src-tauri/.tauri/ogir-updater.key` (gitignored, on disk) | Justin only | Nobody can sign updates, auto-updater breaks |
| 12 | **GitHub Actions secrets (10)** | CI/CD signing + deployment | Set by Justin at repo/settings/secrets/actions. NOT recorded anywhere. | Justin only | Nobody knows which secrets are set, nobody can rotate them |

### Password manager

**There is NO password manager in use.** The Supabase DB password,
Cloudflare/Supabase service keys, and Gmail App Password are all
unstored or in plaintext .env files.

**RECOMMENDED:** Install Bitwarden (free, open-source, audited).
Store every credential from the table above in it. Share the
Bitwarden vault with one trusted person as the BCP backup.

### 2FA status

| Service | 2FA enabled? | Action |
|---------|--------------|--------|
| Cloudflare | UNKNOWN | Enable NOW |
| Supabase | NOT enabled (tick unchecked) | Enable NOW |
| GitHub | UNKNOWN | Enable NOW |
| Google | Unknown (2-Step Verification likely on) | Verify |
| Ollama | UNKNOWN | Enable if available |
| OpenAI | UNKNOWN | Revoke the key instead |
| Microsoft (OneDrive) | UNKNOWN | Verify |

---

## PART 2: Business Continuity Plan (BCP)

### The "hit by bus" scenario

If Justin is unavailable tomorrow (medical, accident, worse),
here's what happens to each system and what the successor needs:

| System | What happens | Time to fail | What successor needs |
|--------|-------------|--------------|---------------------|
| Merkle chain | Stays valid (on disk) | Never | USB stick + paper root card + verify_chain command |
| GitHub repo | Stays live (public after open-sourcing) | Never | GitHub account access OR a clone of the repo |
| Cloudflare Worker | Stays live (free tier) | ~never | Cloudflare login to redeploy or change KV |
| Domain | Expires 2027-07-24 | 12 months | Cloudflare login to renew |
| Supabase DB | Pauses after 7 days | 7 days | Supabase login to unpause |
| Tauri binary | Stays installed on user machines | Never | Nothing (already shipped) |
| Auto-updater | Stops finding new versions | Immediate (no new releases) | Tauri updater private key to sign new releases |
| Ollama billing | Card keeps getting charged | Until card expires | Bank access to cancel |
| EV cert | Valid until ~2027-07 | 12 months | SignMyCode account to renew |

### The sealed envelope (what to prepare NOW)

Put these in a physical sealed envelope and store at **two** offsite
locations (bank safe deposit + trusted family member):

1. **USB stick** with the full repo (run `git clone` to a USB)
2. **Printed Merkle root card** (run `python -m src.verify_chain`, print the root + block count)
3. **A4 sheet** with:
   - Project path: `C:\OrderGetItRight` (after repo move)
   - Verify command: `$env:PYTHONPATH="02_Technical"; python -m src.verify_chain`
   - Test command: `python -m pytest tests/ -q`
   - GitHub repo: `github.com/truthprojectofficial-max/truthasaservice`
4. **Sealed envelope** with:
   - Cloudflare login email + password
   - Supabase login email + password + DB password
   - GitHub login email + password
   - Google Cloud Console login email + password
   - SignMyCode customer ID + login
   - Ollama login email + password
   - Tauri updater private key password
   - Bitwarden master password (once set up)
5. **The passphrase** (12+ characters) that protects the USB stick

### Dead man's switch

**None exists.** Options:
- **Hermes email adapter** (once wired) can send a weekly "I'm alive"
  email. If it stops, the recipient knows something is wrong.
- **Cloudflare Worker health check** — if the Worker goes down, a
  cron job could alert. Not wired yet.
- **Simple option:** tell one trusted person "if you don't hear from
  me by Friday every week, open the sealed envelope at the bank."

### Successor roles (who takes over)

| Role | Who | What they need |
|------|-----|----------------|
| **New operator** | [TO FILL — trusted person] | Sealed envelope + USB + paper card |
| **Legal contact** | [TO FILL — external counsel] | Engagement letter, chain access |
| **Emergency contact** | [TO FILL — backup person] | Phone number, knows the sealed envelope location |

---

## PART 3: What to do NOW (the BCP checklist)

- [ ] Revoke OpenAI key at platform.openai.com/api-keys
- [ ] Revoke GitHub PAT at github.com/settings/tokens
- [ ] Revoke Ollama key at ollama.com/settings
- [ ] Delete line 498 from `C:\Users\justo\AppData\Local\hermes\.env` (the live OpenAI key)
- [ ] Enable 2FA on Cloudflare (dash.cloudflare.com → My Profile → MFA)
- [ ] Enable 2FA on Supabase (supabase.com → Account → MFA)
- [ ] Enable 2FA on GitHub (github.com/settings/security)
- [ ] Install Bitwarden (https://bitwarden.com — free, open-source)
- [ ] Store ALL credentials from the table above in Bitwarden
- [ ] Share the Bitwarden vault with one trusted person
- [ ] Print the current Merkle root card (run verify_chain, print the output)
- [ ] Clone the repo to a USB stick
- [ ] Write the A4 sheet with project path + commands + GitHub URL
- [ ] Write the sealed envelope with all service logins + passwords
- [ ] Store the USB + paper card + A4 sheet + sealed envelope at 2 offsite locations
- [ ] Fill in the successor roles (new operator, legal contact, emergency backup)
- [ ] Set up a weekly "I'm alive" check with one trusted person
- [ ] Cancel the Ollama cloud subscription if not needed (saves $20-100/mo)

---

**This document is internal. Sealed to the chain. Not for clients.**