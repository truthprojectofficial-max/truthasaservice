# OGIR Resources List + Contract Review + Situation Indicators

> Created 2026-07-24. Internal. For Justin â€” your stuff, your
> contracts, your reminders. Everything I found across the project.
> Sealed to chain: `RESOURCES_AND_CONTRACTS_REVIEW_2026_07_24`

---

## PART 1: YOUR HARDWARE (what you own)

| Item | Model/Detail | Where it lives | Status |
|------|-------------|---------------|--------|
| **Laptop** | MSI Prestige 16 Studio (Intel Core Ultra, 8GB VRAM RTX 4060-class, 32GB RAM) | Your desk | Primary machine, all work done here |
| **Phone** | Unknown model (NOT confirmed as Pixel 7a â€” no file mentions it) | With you | Vodafone 5G, number 0480569941, USB-C tether backup (MAC AA-D0-75-05-D8-D8) |
| **Internet** | Starlink (primary, dish installed) + Vodafone 5G tether (backup) | Roof / phone | Starlink: 46-111ms, unlimited. Starlink Mini as portable backup dish (12V) |
| **D: drive** | microSD 64GB (in the laptop, never removed) | Slot in laptop | 51GB used (50GB Ollama models), 8GB free â€” **nearly full** |
| **External SSD** | Nextech-class 2TB (recommended) | Unknown if connected | D: is currently a microSD, not the Nextech. May need to confirm |
| **USB token** | SafeNet eToken (FIPS 140-2 Level 2) | Shipping to Whyalla Norrie | Certera EV cert, purchased 2026-07-24, 1-2 weeks delivery |
| **Paper card** | Printed Merkle root | With your docs | **STALE** â€” shows 35,595 blocks, live is 40,878+ |
| **Offsite USB** | Not yet created | N/A | OPEN â€” go to Whyalla bank, clone repo to USB, store in safe deposit box |

### Hardware you DON'T have but might need
- [ ] External SSD 2TB (for Ollama models â€” D: microSD is nearly full)
- [ ] Second USB stick (for offsite backup at the bank)
- [ ] Printer access (to refresh the paper Merkle root card)

---

## PART 2: YOUR SOFTWARE (what's installed)

| Tool | Version | Path | What it does |
|------|---------|------|-------------|
| **Python** | 3.14.6 | `C:\Python314` | OGIR runtime |
| **Ollama** | 0.32.3 | `C:\Users\justo\AppData\Local\Programs\Ollama` | Local LLM runtime (11 models, 50GB on D:) |
| **Hermes** | v0.18.2 | `C:\Users\justo\AppData\Local\hermes` | Agent framework (build tool) |
| **Aider** | Latest | `C:\AIDERTESTBOX` (sandbox) | Drafting tool (zero trust) |
| **Rust** | 1.97.0 | `C:\Users\justo\.cargo\bin` | Tauri build toolchain |
| **Node.js** | LTS | `C:\Program Files\nodejs` | Tauri + wrangler |
| **Git** | Latest | System | Source control |
| **WebView2** | 150.0.4078.65 | System | Tauri runtime dependency |
| **WSL Ubuntu** | 24.04 | Registered, stopped | For LDDE work (not OGIR runtime) |
| **Unbound DNS** | 1.25.1 | Local 127.0.0.1:53 | DNS resolver |
| **Ruff** | Latest | Python env | Linter (configured in Aider) |

### Software you DON'T have but might need
- [ ] **Bitwarden** (password manager â€” recommended, free, open-source)
- [ ] **VS Code** (or any IDE â€” not mentioned anywhere, you may use a different editor)
- [ ] **Docker** (rejected for OGIR runtime, but useful for Aider sandboxing)

---

## PART 3: YOUR SERVICES + CONTRACTS (with price review reminders)

### Contracts with recurring costs â€” REVIEW THESE

| # | Service | What you pay | Contract term | Renewal date | Price change risk | Review action |
|---|---------|-------------|---------------|-------------|-----------------|---------------|
| 1 | **Ollama Cloud Pro** | $20/mo USD (~$30 AUD) | Monthly, cancel anytime | Ongoing | **Check if they raised the price.** Ollama pricing page: https://ollama.com/pricing. You said you "just paid Ollama again" â€” verify the charge matches $20/mo | [ ] Log into ollama.com/settings, check billing history, confirm $20/mo |
| 2 | **SignMyCode/Certera EV cert** | $429.99 USD (~$650 AUD) | 1 year, purchased 2026-07-24 | ~2027-07 | **They WILL charge full price on renewal.** Check if renewal is auto or manual. SignMyCode doesn't auto-renew (one-time purchase). Watch for a renewal email in ~11 months | [ ] Set calendar reminder for 2027-06: "renew or shop around for EV cert" |
| 3 | **Cloudflare domain** | ~$10/yr USD (~$15 AUD) | Annual, renews 2027-07-24 | 2027-07-24 | **Cloudflare sells at cost (no markup).** Price is stable. But verify the renewal email when it comes | [ ] Check Cloudflare billing for auto-renew status |
| 4 | **Supabase Free** | $0 | Free tier, unlimited | N/A | **Free tier may change limits.** Supabase has reduced free limits before. Check https://supabase.com/pricing quarterly | [ ] Quarterly: check if free tier limits changed |
| 5 | **GitHub Free** | $0 | Free, unlimited | N/A | **Stable.** Actions minutes are free for public repos | [ ] No action needed |
| 6 | **Google OAuth** | $0 | Free | N/A | **Stable.** Google may add verification requirements if you exceed 100 users | [ ] No action needed until 100+ users |
| 7 | **Starlink** | Unknown (not in docs) | Monthly? | Ongoing | **Starlink has raised prices.** Check your Starlink bill. Residential AU is ~$139/mo + hardware. Verify at https://starlink.com | [ ] Check Starlink bill â€” is it still the same price? |
| 8 | **Vodafone 5G** | Unknown (not in docs) | Monthly phone plan | Ongoing | **Phone plan may have price changes.** Check your Vodafone bill | [ ] Check Vodafone bill â€” any price increase? |
| 9 | **Microsoft OneDrive** | Unknown (not in docs) | Monthly/annual | Ongoing | **OneDrive may have raised prices.** Check your Microsoft 365 subscription | [ ] Check if OneDrive/MS365 price increased |
| 10 | **Bank card** | N/A | N/A | Expires ?? | **Card expiry = all auto-charges stop.** Check your card expiry date. If it expires soon, update it on Ollama, Cloudflare, Supabase (when Pro) | [ ] Check card expiry date â€” update before it lapses |

### Contracts that are free (no price risk)

| Service | Plan | Cost | Notes |
|---------|------|------|-------|
| Cloudflare Workers | Free | $0 | 100k req/day â€” you use ~1/day |
| Cloudflare R2 | Free | $0 | 10GB storage â€” you use 0 |
| Cloudflare KV | Free | $0 | 100k reads/day â€” you use ~1/day |
| Supabase | Free | $0 | 500MB DB â€” you use <1MB |
| GitHub | Free | $0 | Public repo, unlimited Actions |
| Google OAuth | Free | $0 | Drive.file scope only |

### Contracts you DON'T have yet but will need

| Service | When | Cost | Why |
|---------|------|------|-----|
| Supabase Pro | Before public launch | $25/mo USD | Kills 7-day pause, daily backups |
| Professional indemnity insurance | First paying client | ~$50/mo | Legal protection |
| Apple Developer ID | When you want macOS signed | $99/yr | macOS builds signed (currently blocked) |
| Bitwarden | ASAP | $0 (free tier) | Password manager |
| External SSD 2TB | When D: fills | ~$100-150 | Ollama models outgrowing the microSD |

---

## PART 4: SITUATION INDICATORS (what needs attention now)

This is the "is it true you can write up a situation that needs
indicating toward what's best" part. Here's every situation I see
that needs your attention, ranked by urgency:

### RED â€” do this now (today)

1. **3 leaked keys not revoked** â€” GitHub PAT, OpenAI, Ollama. Anyone with git history has access. Revoke at:
   - github.com/settings/tokens
   - platform.openai.com/api-keys
   - ollama.com/settings

2. **OpenAI key was still live in Hermes .env** â€” I removed it tonight, but if anyone accessed your machine between when it was pasted and now, they had free OpenAI access. The key is now commented out. Still must revoke.

3. **Vault in OneDrive** â€” the repo move runbook is ready. Every day you stay in OneDrive, the vault can corrupt again. It already happened once.

4. **D: drive nearly full** (8GB free of 64GB) â€” you can't add Ollama models. If the drive fills completely, Ollama will crash. Either: (a) delete unused models, (b) buy a 2TB external SSD and move OLLAMA_MODELS there, (c) cancel Ollama Cloud if you don't use it (saves $30/mo + 50GB disk).

### AMBER â€” do this week

5. **No 2FA on any service** â€” Cloudflare, Supabase, GitHub all have 2FA available but none enabled. If any account is compromised, everything is gone.

6. **No password manager** â€” all credentials are in your head or in plaintext .env files. If you forget one, you can't recover it without a password reset. Bitwarden is free.

7. **No offsite backup** â€” the sealed envelope + USB + paper card plan exists but hasn't been done. If your house burns down, the chain survives (it's on GitHub) but the cloud accounts are unrecoverable.

8. **Bus factor = 1** â€” nobody else knows any password, has any access, or knows what OGIR is. If you're hit by a bus, the business dies with you. Fill in at least the emergency backup contact.

9. **Paper Merkle root card is stale** â€” shows 35,595 blocks, live is 40,878+. Reprint: run `python -m src.verify_chain`, print the output, put it in the sealed envelope.

10. **Postcode discrepancy** â€” some docs say 5608, some say 5086. Whyalla Norrie is 5608. The 5086 docs are from 2026-07-22 (older). Confirm your correct postcode and update any stale docs.

### GREEN â€” do this month

11. **Starlink price check** â€” check your bill. Starlink raised residential prices in 2024-2025. Verify you're still paying what you expect.

12. **Vodafone price check** â€” check your phone bill. Mobile plans can have price hikes mid-contract.

13. **OneDrive/MS365 price check** â€” Microsoft raised M365 prices. Verify your subscription.

14. **EV cert renewal reminder** â€” set a calendar reminder for 2027-06: "renew or shop around." SignMyCode doesn't auto-renew.

15. **Supabase free tier limits** â€” check quarterly. Supabase has reduced free limits before (storage, auth users, egress).

16. **Card expiry** â€” check when your bank card expires. If it lapses, all auto-charges (Ollama, Cloudflare domain, Supabase Pro) stop silently.

### BLUE â€” do when you have time

17. **Buy external SSD 2TB** â€” move Ollama models off the nearly-full microSD. Frees D: for other uses. ~$100-150.

18. **Print business cards** â€” Vistaprint ~$20 for 100. Name, title, ordergetitright.com, phone, email.

19. **Set up email signature** â€” "Justin Barnett | Order Get It Right â€” Verified Processor | ordergetitright.com"

20. **Post on community boards** â€” Whirlpool, Reddit r/ausbusiness, Whyalla community boards. Only AFTER the repo is public + landing page live + v0.1.0 downloadable.

---

## PART 5: THE "WHAT'S BEST" RECOMMENDATIONS

Based on everything I've seen across your project today, here's
what I'd recommend you do â€” in order â€” when you wake up:

### First 10 minutes
1. Revoke the 3 leaked keys (GitHub, OpenAI, Ollama)
2. Check your Starlink bill (has it gone up?)
3. Check your card expiry date

### First hour
4. Enable 2FA on GitHub, Supabase, Cloudflare
5. Install Bitwarden (free)
6. Store all credentials from the password registry in Bitwarden

### This week
7. Move the repo out of OneDrive (runbook ready)
8. Wire Hermes email (5 steps in the initiation doc)
9. Add the ogir-builder persona to Hermes config
10. Go to the Whyalla bank â€” put USB + paper card + sealed envelope in a safe deposit box
11. Fill in the emergency backup contact (a person you trust)
12. Refresh the paper Merkle root card (run verify_chain, print)

### This month
13. Check all bills (Starlink, Vodafone, OneDrive, Ollama)
14. Set calendar reminders for cert renewal (2027-06) + domain renewal (2027-07)
15. When the EV cert token arrives: export .pfx â†’ GitHub secrets â†’ tag v0.1.0
16. Buy external SSD if D: is too full
17. Consider cancelling Ollama Cloud Pro if you only use local models (saves $30/mo)

---

**This document is your resources list, your contract review, and
your situation indicators. Read it. Act on the red items. The green
items can wait. The blue items can wait until you have paying clients.**