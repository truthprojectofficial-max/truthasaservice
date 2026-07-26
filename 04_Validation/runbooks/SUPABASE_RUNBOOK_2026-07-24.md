# Supabase Runbook — 2026-07-24

> Project: https://qqbrpqdbxhypkvvsjble.supabase.co
> Operator: Justin Barnett
> Tables: customers, scans, affidavits
> Plan: Free (upgrade to Pro before public launch)

## Dashboard map — what each sidebar section is for

| Section | What it does | When to open it | Touch it? |
|---------|-------------|-----------------|-----------|
| **Home** | Usage gauges (DB size, MAU, egress) | Monthly glance | Monitor only |
| **Table Editor** | View/edit table rows | Never | NO — chain is truth, not these rows |
| **SQL Editor** | Run SQL (migrations, checks) | After schema changes | Yes, for checks |
| **Authentication** | Users, providers, signup rules | Once to set up, then monitor | Yes, once |
| **Database** | RLS policies, SSL, backups | Once to configure | Yes, once |
| **Storage** | File buckets (images, PDFs) | Skip | NO — you scan text |
| **Edge Functions** | Serverless functions | Skip | NO — violates air-gap |
| **Logs** | Postgres + Auth logs | When something breaks | Check on failure |
| **Reports** | Usage + advisor reports | Monthly | Monitor only |
| **Settings** | API keys, DB password, billing | Once, then rotate if leaked | Yes, once |

## ONE-TIME SETUP (do these, then don't touch settings again)

### 1. Enable 2FA on your Supabase account
- Path: Account (top-right) → Account → MFA
- Why: Stops someone hijacking your whole DB
- Time: 2 min

### 2. Enable SSL enforcement
- Path: Dashboard → Database → Settings → SSL Configuration
- Toggle: **Enforce SSL → ON**
- Time: 30 sec

### 3. Enable email confirmations
- Path: Dashboard → Authentication → Providers → Email
- Toggle: **Confirm email → ON**
- Toggle: **Enable Email Signup → ON** (or OFF if invite-only)
- Time: 30 sec

### 4. Enable Google OAuth provider
- Path: Dashboard → Authentication → Providers → Google
- Toggle: **Enable → ON**
- Paste your Google Client ID: `626612745795-lita38fhggqne53td0pfu23bsd8mc6ur.apps.googleusercontent.com`
- Paste your Google Client Secret (from Google Cloud Console — NOT in the repo)
- Set the redirect URI: `https://qqbrpqdbxhypkvvsjble.supabase.co/auth/v1/callback`
- Also add this callback URL to your Google Cloud Console OAuth client
- Time: 5 min

### 5. Set Tauri redirect URL
- Path: Dashboard → Authentication → URL Configuration
- Add to Redirect URLs: `ordergetitright://auth/callback`
- Set Site URL to: `https://ordergetitright.com` (or your Tauri scheme)
- Time: 1 min

### 6. Verify RLS policies
- Path: Dashboard → SQL Editor → New query
- Paste and run:
```sql
select relname, relrowsecurity
from pg_class
where relname in ('customers','scans','affidavits') and relkind='r';
```
- All three must show `true`
- Then check:
```sql
select schemaname, tablename, policyname, cmd, roles
from pg_policy
where tablename in ('customers','scans','affidavits');
```
- Each table needs at least 1 policy
- `scans` and `affidavits` must be `to authenticated` (NOT `to anon`/`to public`)
- Time: 2 min

### 7. Disable public signup (if you want invite-only)
- Path: Dashboard → Authentication → Providers → Email
- Toggle: **Enable Email Signup → OFF**
- Add users manually: Dashboard → Authentication → Users → Add user
- Time: 1 min

### 8. Save the DB password
- Path: Dashboard → Project Settings → Database → Database password
- Reset it if you don't have it saved. Store in a password manager.
- Time: 1 min

## Free tier limits (what you're on now)

| Resource | Free limit | Your usage |
|----------|-----------|------------|
| Database size | 500 MB | Tiny (3 tables, few rows) |
| Storage | 1 GB | 0 (you don't use storage) |
| Auth users | 50,000 | 1 (you) |
| API requests | Unlimited | Low |
| Egress | 5 GB/mo | Low |
| Daily backups | NONE | Must self-backup |
| **Inactivity pause** | **7 days = paused** | Risk if you go a week without a login |

## Pro tier ($25/mo) — upgrade before public launch

| What you get | Why it matters |
|-------------|---------------|
| Daily backups (7-day retention) | Essential for a chain-of-trust product |
| Never paused | The 7-day inactivity pause kills you if no one signs in |
| 8 GB database | Way more than 500 MB |
| 100 GB storage | Not needed now |
| Remove Supabase branding from auth emails | Professional |
| Leaked-password protection | Blocks known-breached passwords |
| Log retention 7 days (vs 1 day) | More debugging window |

## Auto-deduction setup (Pro tier — when you upgrade)

1. Go to Dashboard → Organization → Billing → **Payment methods**
2. Click **Add payment method**
3. Enter your bank card details (Visa/Mastercard debit or credit)
4. Go to Dashboard → Organization → Billing → **Subscriptions**
5. Click **Upgrade** → select **Pro** ($25/mo)
6. Confirm the card on file
7. Toggle **Spend caps → ON** (prevents surprise bills — caps overage at your plan limit)
8. The card is charged monthly on the date you upgraded

**Automation policy:** Once on Pro, Supabase auto-charges the card
monthly. You don't need to do anything. Check your bank statement
monthly for the $25 USD charge (~$38-42 AUD depending on exchange rate).

## The 3 things you'll touch regularly (after setup)

1. **Home** — glance at usage gauges (monthly)
2. **SQL Editor** — run the RLS check after any schema change
3. **Authentication → Users** — check for unexpected signups (monthly)

## What NOT to touch (ever)

- **Table Editor** — don't edit audit rows manually. The Merkle chain
  in 03_Vault is the truth anchor; these Postgres rows are the sync
  copy. Manual edits desync them.
- **Storage** — you don't need it. Skip.
- **Edge Functions** — violates the air-gap. Skip.
- **Network Restrictions** — optional. Only restrict if you're sure
  your CI IP is static.

## Free-tier backup schedule (do this weekly)

```powershell
# Install Supabase CLI if not installed:
# npm install -g supabase

# Weekly backup to 04_Validation/hardcopy/
supabase db dump --project-ref qqbrpqdbxhypkvvsjble --data-only -f "04_Validation\hardcopy\supabase_backup_$(Get-Date -Format 'yyyy-MM-dd').sql"
```

Store the backup alongside your paper Merkle root card in
`04_Validation/hardcopy/`. Refresh on every quarterly cycle (per
AGENTS.md).