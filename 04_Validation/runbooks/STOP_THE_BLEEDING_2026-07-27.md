# STOP THE BLEEDING — Every Dollar Accounted For

> Date: 2026-07-27
> Operator: "i want to make sure i dont lose any more money its been
> over a thousand dollars in three weeks"
> Purpose: Account for every dollar spent, identify every recurring
> charge, and give the operator a precise kill-switch list.
> Sealed to chain.

---

## THE TOTAL DAMAGE — 3 weeks (Jul 4 - Jul 27, 2026)

### Every charge found across the billing files:

| # | Service | Date(s) | Amount USD | Amount AUD (~1.5x) | Recurring? |
|---|---------|---------|-----------|---------------------|------------|
| 1 | **OpenAI** | Jul 10 | $1.03 | ~$1.55 | API usage |
| 2 | **OpenAI** | Jul 11 | $0.001 | ~$0.01 | API usage |
| 3 | **OpenAI** (BILLING txt) | Jul 11 | $159.24 ×2 + $30 + $16 + $143 + $15 | **$471.48** | **MASSIVE — see below** |
| 4 | **Ollama Pro** | Jul 16 | $20.00 | ~$30 | Monthly sub |
| 5 | **Ollama extra usage** | Jul 16-27 (25 × $5 charges) | $125.00 | ~$188 | **PER-USE — see below** |
| 6 | **SignMyCode/Certera EV cert** | Jul 24 | $429.99 | ~$645 | One-off (1yr) |
| 7 | **Google Cloud** | Jul 3 | $22.61 | ~$34 | Unknown |
| 8 | **Microsoft** | Jul (date unclear) | $10.00 | ~$15 | Monthly? |
| 9 | **Starlink** | Jul (monthly) | $500 + $80/mo | ~$870 + $120/mo | Monthly |
| 10 | **FLEX** | Jul 20 (4 charges) | Unknown | Unknown | Unknown |

### The operator's "$1,000+ in 3 weeks" — where it went:

| Category | USD | AUD (approx) |
|----------|-----|---------------|
| OpenAI (the big one) | ~$471 | ~$707 |
| Ollama (Pro + extra usage) | ~$145 | ~$218 |
| SignMyCode EV cert | $430 | ~$645 |
| Google Cloud | $23 | ~$34 |
| Microsoft | $10 | ~$15 |
| **Total found** | **~$1,079** | **~$1,619** |

The operator said "over a thousand dollars in three weeks." The numbers
confirm it. The biggest single bleed is **OpenAI at ~$471 USD in one
day (Jul 11)** — two charges of $159.24, plus $30, $16, $143, and $15
on the same day. That is not normal API usage. That is a runaway
session or a leaked key being used.

---

## THE OPENAI BLEED — what happened

The BILLING txt file says:
- "OPEN AI 159.24 11TH JULY TWICE!!!!!! AND 30 MOR SAME DAY"
- "10TH JULY 16 PLUS 143 PLUS 15"

So on Jul 10-11, OpenAI charged:
- $159.24 × 2 = $318.48 (Jul 11)
- $30 (Jul 11, same day)
- $16 (Jul 10)
- $143 (Jul 10)
- $15 (Jul 10)
- **Total: $522.48 USD in 2 days (~$784 AUD)**

The OpenAI API key `sk-svcacct-ou0TD1H...` was leaked in git history
and was live in Hermes .env line 498. The operator revoked it on
2026-07-24 (block 40923). But the charges happened Jul 10-11 — BEFORE
the revocation. Either:
1. The leaked key was used by someone else (the key was in git history
   on GitHub, which was public), OR
2. A runaway Hermes session burned through API credits, OR
3. Both.

**The key is now revoked. The bleed should have stopped on Jul 24.**
But the operator should verify no NEW OpenAI charges have appeared
since Jul 24. The CSV export shows $0 for Jul 12-27 (only $1.03 on
Jul 9 and $0.001 on Jul 10 in the CSV — the CSV may not capture the
big charges, which could be subscription/batch billing rather than
daily API usage).

---

## THE OLLAMA BLEED — $145 USD and climbing

The Ollama billing shows:
- $20/mo Pro subscription (started Jul 16)
- 25 × $5 "extra usage" charges (Jul 16-27) = $125

The $5 extra-usage charges are AUTOMATIC — every time the cloud usage
quota is exceeded, Ollama charges $5 to the card on file. 25 charges
in 11 days means the agent is hitting the quota repeatedly.

**This bleed is ACTIVE RIGHT NOW.** Every session that uses
`glm-5.2:cloud` (this model) may be consuming Ollama cloud credits.
The next billing date is August 15, 2026, but the $5 extra-usage
charges hit in real time.

---

## KILL SWITCH — every recurring charge and how to stop it

### 1. Ollama — ACTIVE BLEED ($20/mo + $5 per overage)
- **Stop the $5 overage:** Switch to local models only (qwen2.5:7b,
  deepseek-r1, llama3.1:8b — all on D:\OllamaModels). Stop using
  cloud models.
- **Cancel Pro:** Log into ollama.com/settings → Cancel subscription.
  Saves $20/mo. You can re-subscribe when you need cloud models.
- **Card:** Mastercard •••• 9011, expires 12/2029
- **Status: OPERATOR ACTION — do this today**

### 2. OpenAI — KEY REVOKED, verify no new charges
- Key `sk-svcacct-ou0TD1H...` revoked 2026-07-24 (block 40923).
- **Verify:** Check platform.openai.com/settings/billing for any
  charges AFTER Jul 24. If there are new charges, the key is still
  live somewhere (check Hermes .env line 498 — delete it if still
  there).
- **Also:** Delete the OpenAI API key entirely if you're not using
  OpenAI. You don't need it for OGIR (the runtime is air-gapped,
  the build agent uses Ollama).
- **Status: VERIFY — operator action**

### 3. Google Cloud — $22.61 on Jul 3
- The OGIR project uses Google Cloud Console only for the OAuth
  client (Drive picker, PKCE — no client secret needed).
- $22.61 is unusual for a free-tier OAuth client. Check if something
  else is running on the Google Cloud project.
- **Verify:** console.cloud.google.com → Billing → check for active
  resources (VMs, storage, APIs with billing enabled). Shut down
  anything you didn't explicitly start.
- **Status: VERIFY — operator action**

### 4. Microsoft — $10 (date unclear)
- This is likely a Microsoft 365 / OneDrive subscription.
- $10/mo is normal for M365 Personal. Not a bleed, but verify it's
  the right plan and you're not paying for a business tier you don't
  need.
- **Status: LOW PRIORITY — verify when convenient**

### 5. Starlink — $500 + $80/mo
- This is the operator's internet connection. Not an OGIR cost
  (you'd pay this regardless). But $500 is a large one-off —
  likely hardware deposit or first-month + shipping.
- **Status: NOT OGIR — personal expense, no action needed**

### 6. SignMyCode/Certera — $429.99 (one-off, already paid)
- EV code signing cert, 1 year. Not recurring until ~2027-07.
- No action needed now. Set a calendar reminder for 2027-06 to
  decide whether to renew or shop around.
- **Status: PAID — no action until 2027-07**

### 7. FLEX — 4 charges on Jul 20, amounts unknown
- "FLEX 20 JULY 4" — 4 charges on Jul 20. Unknown what this is.
- Could be Flex (the streaming service), FlexTools, or something else.
- **Verify:** Check bank statement for "FLEX" on Jul 20. Cancel if
  it's a subscription you don't use.
- **Status: VERIFY — operator action**

### 8. Supabase — $0 (free tier)
- Currently free. Do NOT upgrade to Pro until you have paying
  clients. The 7-day pause risk is real but only matters if the
  project is idle for a week — if you're working daily, it won't
  pause.
- **Status: DO NOT UPGRADE YET**

### 9. Cloudflare — $0 (free tier)
- Workers, R2, KV all on free tier. Domain renewal is annual
  (~$15 AUD, renews 2027-07-24).
- **Status: NO ACTION NEEDED**

### 10. GitHub — $0 (free, public repo)
- **Status: NO ACTION NEEDED**

---

## PRIORITY ORDER — do these in this sequence

| Priority | Action | Saves | Time |
|----------|--------|-------|------|
| **1. TODAY** | Cancel Ollama Pro + stop using cloud models | $20/mo + $5/overage (~$50-100/mo) | 5 min |
| **2. TODAY** | Verify OpenAI billing — check for charges after Jul 24 | If still charging: ~$150+/day | 5 min |
| **3. TODAY** | Delete OpenAI key from Hermes .env line 498 if still there | Prevents future bleed | 2 min |
| **4. THIS WEEK** | Check Google Cloud billing ($22.61) — shut down unused resources | Unknown | 10 min |
| **5. THIS WEEK** | Check FLEX charges on Jul 20 — cancel if unwanted | Unknown | 5 min |
| **6. LOW** | Verify Microsoft $10/mo is the right plan | Maybe $5/mo if downgrading | 5 min |

---

## WHAT THE BUILD AGENT CAN DO RIGHT NOW

The Ollama bleed is caused by using `glm-5.2:cloud` (this model). The
operator can switch the build agent to a LOCAL model to stop the
cloud-usage charges immediately. Available local models on
D:\OllamaModels:
- Qwen2.5-coder (local 7B)
- qwen3.5:9b
- llama3.1:8b
- DeepSeek-R1-Distill-Qwen-7B
- gemma3
- Llama3.2

Switching to a local model stops the Ollama cloud overage charges
instantly. The tradeoff: local models are smaller and may be less
capable. But $50-100/mo in overage charges is not worth the
capability difference for a project that is not yet earning revenue.

**The decision to switch models is an operator action** — it requires
changing `opencode.json` and restarting opencode. The build agent
cannot change its own model mid-session.