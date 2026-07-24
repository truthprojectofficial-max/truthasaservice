# OGIR Budget + Future Projections (Conservative)

> Created 2026-07-24. Internal. Conservative estimates — assume
> slow adoption, no viral moments, steady solo-operator pace.
> Sealed to chain: `BUDGET_AND_PROJECTIONS_2026_07_24`

---

## CURRENT SPEND (what you've already paid)

| Item | Cost | Date | One-off or recurring? |
|------|------|------|---------------------|
| SignMyCode/Certera EV cert (1yr + token + shipping) | $429.99 USD (~$650 AUD) | 2026-07-24 | Annual (renew ~2027-07) |
| Domain ordergetitright.com | ~$10 USD (~$15 AUD) | 2026-07-24 | Annual (renews 2027-07-24) |
| Ollama Cloud Pro | ~$20/mo USD (~$30 AUD/mo) | Ongoing | Monthly auto-charge |
| **Total spent today** | **~$665 AUD** | | |

---

## MONTHLY BURN (current — no paying clients yet)

| Item | Cost/mo AUD | Status |
|------|------------|--------|
| Ollama Cloud Pro | $30 | Active (card auto-charge) |
| Cloudflare Workers | $0 | Free tier (100k req/day) |
| Cloudflare R2 | $0 | Free tier (10GB storage) |
| Cloudflare KV | $0 | Free tier (100k reads/day) |
| Supabase | $0 | Free tier (500MB DB) |
| GitHub | $0 | Free (public repo, unlimited Actions) |
| Google OAuth | $0 | Free |
| Domain (amortised) | $1.25/mo ($15/yr ÷ 12) | — |
| EV cert (amortised) | $54/mo ($650/yr ÷ 12) | — |
| Internet (you'd pay anyway) | $0 | — |
| **Total monthly burn** | **~$30 AUD/mo** ($360/yr) | |

**Annual burn (current):** ~$360 + $665 = **~$1,025 AUD/yr**

---

## MONTHLY BURN (after upgrades — when paying clients start)

| Item | Cost/mo AUD | When | Why |
|------|------------|------|-----|
| Ollama Cloud Pro | $30 | Now | LLM for agent tools |
| Supabase Pro | $38 ($25 USD) | Before public launch | Kills 7-day pause, daily backups, 8GB DB |
| Cloudflare Workers Paid | $8 ($5 USD) | If >100k req/day | 10M requests/mo |
| Professional indemnity insurance | ~$50/mo | First paying client | Legal protection |
| **Total monthly burn (upgraded)** | **~$126 AUD/mo** | | |

**Annual burn (upgraded):** ~$1,512 + $665 (cert/domain) = **~$2,177 AUD/yr**

---

## REVENUE PROJECTIONS (conservative)

### Assumptions (conservative)
- No clients for first 3 months (building, calibrating, marketing)
- Month 4: 2 per-case audits ($25 each)
- Month 6: 5 per-case + 1 Pro license ($49)
- Month 12: 10 per-case + 3 Pro licenses
- No enterprise contracts in year 1 (realistic for a new solo tool)

### Year 1 projection

| Month | Per-case audits | Pro licenses | Enterprise | Revenue AUD | Cumulative |
|-------|----------------|-------------|------------|------------|-----------|
| 1-3 | 0 | 0 | 0 | $0 | $0 |
| 4 | 2 × $38 | 0 | 0 | $76 | $76 |
| 5 | 3 × $38 | 0 | 0 | $114 | $190 |
| 6 | 5 × $38 | 1 × $75 | 0 | $265 | $455 |
| 7 | 5 × $38 | 1 × $75 | 0 | $265 | $720 |
| 8 | 7 × $38 | 2 × $75 | 0 | $416 | $1,136 |
| 9 | 8 × $38 | 2 × $75 | 0 | $454 | $1,590 |
| 10 | 10 × $38 | 2 × $75 | 0 | $530 | $2,120 |
| 11 | 10 × $38 | 3 × $75 | 0 | $605 | $2,725 |
| 12 | 12 × $38 | 3 × $75 | 0 | $681 | $3,406 |

**Year 1 revenue (conservative): ~$3,406 AUD**
**Year 1 costs: ~$2,177 AUD**
**Year 1 net: ~$1,229 AUD profit** (barely break-even — this is realistic for a solo tool's first year)

### Year 2 projection (conservative)

| Item | Volume | Price | Revenue |
|------|--------|-------|---------|
| Per-case audits | 200/yr (~17/mo) | $38 | $7,600 |
| Pro licenses | 15/yr | $75 | $1,125 |
| Enterprise support | 1 contract | $760/mo ($500 USD) | $9,120 |
| **Total Year 2 revenue** | | | **~$17,845 AUD** |
| **Year 2 costs** | | | **~$2,500 AUD** (cert renewal + higher Supabase) |
| **Year 2 net** | | | **~$15,345 AUD** |

### Year 3 projection (conservative)

| Item | Volume | Price | Revenue |
|------|--------|-------|---------|
| Per-case audits | 500/yr | $38 | $19,000 |
| Pro licenses | 40/yr | $75 | $3,000 |
| Enterprise support | 3 contracts | $760/mo each | $27,360 |
| **Total Year 3 revenue** | | | **~$49,360 AUD** |
| **Year 3 costs** | | | **~$5,000 AUD** (cert renewal, higher Cloudflare, accountant) |
| **Year 3 net** | | | **~$44,360 AUD** |

---

## BREAK-EVEN ANALYSIS

**Break-even point:** when revenue = monthly burn

| Scenario | Break-even | How |
|----------|-----------|-----|
| Current burn ($30/mo) | 1 per-case audit/mo | 1 × $38 > $30 |
| Upgraded burn ($126/mo) | 4 per-case audits/mo | 4 × $38 > $126 |
| With insurance ($176/mo) | 5 per-case audits/mo | 5 × $38 > $176 |

**You break even at 4-5 audits per month.** That's 1 audit per week.
Very achievable for a solo operator.

---

## CASH FLOW TIMELINE

```
Month 1-3:  Spend $30/mo, earn $0.   Net: -$90
Month 4:    Spend $30/mo, earn $76.  Net: +$46 (first profit!)
Month 6:    Spend $126/mo (upgraded), earn $265. Net: +$139
Month 12:   Spend $176/mo, earn $681. Net: +$505
Year 2:     Spend ~$200/mo, earn ~$1,487/mo. Net: +$1,287/mo
Year 3:     Spend ~$417/mo, earn ~$4,113/mo. Net: +$3,696/mo
```

---

## WHAT TO DO WITH THE BUDGET

### Now (before any clients)
- [ ] Cancel Ollama Cloud if you're not using it (saves $30/mo — you can re-subscribe when you need it)
- [ ] Keep everything else on free tiers
- [ ] Don't buy insurance yet (wait for first paying client)
- [ ] Don't upgrade Supabase yet (wait for public launch)

### When first client pays
- [ ] Upgrade Supabase to Pro ($38/mo) — kills the 7-day pause
- [ ] Buy professional indemnity insurance (~$50/mo)
- [ ] Set aside 30% of revenue for tax (don't spend it all)

### When revenue > $500/mo
- [ ] Talk to an accountant about Pty Ltd registration
- [ ] Consider hiring a junior dev (10 hrs/wk, ~$800/mo) to handle:
  - Tauri ↔ Supabase sync code
  - Cases table + trial board
  - Automation (cron backups, health checks)

### When revenue > $2,000/mo
- [ ] Register Pty Ltd ($500-900)
- [ ] Register GST (mandatory if turnover > $75k/yr)
- [ ] Get a proper accountant ($100-200/mo)

---

## THE SWISS ARMY KNIFE PROBLEM

You said you're "working with a swiss army knife and only using the corkscrew."
That's accurate. Here's what you're paying for but not using:

| Service | What you pay for | What you use | Wasted |
|---------|-----------------|-------------|--------|
| Ollama Pro | 50× more cloud usage, 3 concurrent models | Local models only | $30/mo wasted? |
| Cloudflare Workers | 100k req/day | ~1 req/day (health checks) | $0 (free tier) |
| Cloudflare R2 | 10GB storage | 0 (no binaries yet) | $0 (free tier) |
| Supabase | 500MB DB, 50k auth users | 1 user (you) | $0 (free tier) |
| GitHub | Unlimited Actions minutes | 0 runs (no tags pushed) | $0 (free) |
| EV cert | Code signing | Not yet (token in transit) | $54/mo amortised |

**The only real waste is Ollama Pro ($30/mo) IF you're not using cloud models.**
If you only run local models, cancel Ollama Pro and save $360/yr.

---

**This budget is conservative. Real numbers could be better or worse.
The break-even point is 4-5 audits/month. That's the number to watch.**