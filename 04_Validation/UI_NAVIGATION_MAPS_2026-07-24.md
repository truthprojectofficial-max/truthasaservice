# UI Navigation Maps — Cloudflare, Supabase, GitHub (Typed Path Only)

> Created 2026-07-24. For Justin. No clicking around looking for things.
> Type the path, land on the page, do the thing, leave.
> Sealed to chain: `UI_NAVIGATION_MAPS_2026_07_24`

---

## WHY THIS EXISTS

You said your biggest headache is navigating dashboards by clicking
around. These maps give you the typed URL path to every page you need.
No "settings → options → advanced → security" clicking. Just type
the URL and land there.

---

## CLOUDFLARE (dash.cloudflare.com)

### Direct URLs (type these into your browser)

| What you want to do | URL (type this) |
|---------------------|----------------|
| Dashboard home | `https://dash.cloudflare.com` |
| Domain management (ordergetitright.com) | `https://dash.cloudflare.com/?to=/:account/domains` |
| DNS records | `https://dash.cloudflare.com/?to=/:account/ordergetitright.com/dns/records` |
| Worker (ordergetitright-updater) | `https://dash.cloudflare.com/?to=/:account/workers/services/view/ordergetitright-updater` |
| Worker health check (live) | `https://update.ordergetitright.com/health` |
| Worker latest manifest | `https://update.ordergetitright.com/latest` |
| R2 bucket (ordergetitright-releases) | `https://dash.cloudflare.com/?to=/:account/r2/buckets/ordergetitright-releases` |
| KV namespace (UPDATES_KV) | `https://dash.cloudflare.com/?to=/:account/workers/kv/namespaces/f726dd2f0de24c32b8af87fef5e06895` |
| Billing | `https://dash.cloudflare.com/?to=/:account/billing` |
| Profile / MFA settings | `https://dash.cloudflare.com/?to=/:account/profile/members` |
| WHOIS privacy | `https://dash.cloudflare.com/?to=/:account/registrar/ordergetitright.com` |

### What to touch (once, then leave alone)
- **DNS records** — only if adding a new subdomain
- **Worker** — only if redeploying (`npx wrangler deploy` from CLI)
- **R2 bucket** — only when uploading a new release binary
- **KV** — only when updating the release manifest
- **Billing** — check monthly (should be $0 on free tier)
- **MFA** — enable ONCE, then never touch again

### What NOT to touch
- Page Rules, Firewall Rules, Rate Limiting — leave default
- Analytics — glance monthly, don't configure anything
- Workers Logs — only if the Worker breaks

---

## SUPABASE (supabase.com)

### Direct URLs (type these into your browser)

| What you want to do | URL (type this) |
|---------------------|----------------|
| Dashboard home | `https://supabase.com/dashboard` |
| OGIR project home | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble` |
| Table Editor (view tables) | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/editor` |
| SQL Editor (run migrations) | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/sql/new` |
| Authentication → Users | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/auth/users` |
| Authentication → Providers | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/auth/providers` |
| Authentication → URL Config | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/auth/url-configuration` |
| Database → Policies (RLS) | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/database/policies` |
| Database → Backups | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/database/backups` |
| Settings → API (keys) | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/settings/api` |
| Settings → Database (password) | `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble/settings/database` |
| Billing | `https://supabase.com/dashboard/org/_/billing` |
| Account → MFA | `https://supabase.com/dashboard/account` |

### What to touch (once, then leave alone)
- **SQL Editor** — run 0001 + 0002 migrations (once each)
- **Auth → Providers** — enable Email + Google (once)
- **Auth → URL Config** — set redirect URLs (once)
- **Settings → Database** — save the DB password (once)
- **Account → MFA** — enable 2FA (once)

### What to check periodically
- **Table Editor** — glance at row counts (monthly)
- **Auth → Users** — check for unexpected signups (monthly)
- **Database → Backups** — confirm Pro daily backups exist (after upgrade)

### What NOT to touch
- Storage — you don't use it
- Edge Functions — you don't use it
- Realtime — leave default
- Logs — only if something breaks

---

## GITHUB (github.com)

### Direct URLs (type these into your browser)

| What you want to do | URL (type this) |
|---------------------|----------------|
| Repo home | `https://github.com/truthprojectofficial-max/truthasaservice` |
| Settings (general) | `https://github.com/truthprojectofficial-max/truthasaservice/settings` |
| Settings → Pages | `https://github.com/truthprojectofficial-max/truthasaservice/settings/pages` |
| Settings → Secrets (Actions) | `https://github.com/truthprojectofficial-max/truthasaservice/settings/secrets/actions` |
| Settings → Collaborators | `https://github.com/truthprojectofficial-max/truthasaservice/settings/access` |
| Actions (CI/CD runs) | `https://github.com/truthprojectofficial-max/truthasaservice/actions` |
| Releases | `https://github.com/truthprojectofficial-max/truthasaservice/releases` |
| Issues | `https://github.com/truthprojectofficial-max/truthasaservice/issues` |
| Pull Requests | `https://github.com/truthprojectofficial-max/truthasaservice/pulls` |
| Insights (analytics) | `https://github.com/truthprojectofficial-max/truthasaservice/pulse` |
| Profile settings | `https://github.com/settings/profile` |
| Security (2FA) | `https://github.com/settings/security` |
| Personal access tokens | `https://github.com/settings/tokens` |
| Billing | `https://github.com/settings/billing` |

### What to touch (once, then leave alone)
- **Settings → Pages** — enable Pages, set source to /docs, set custom domain (once)
- **Settings → Secrets** — add WINDOWS_CERTIFICATE + password when cert arrives (once)
- **Settings → Security** — enable 2FA (once)
- **Profile** — add bio + link to ordergetitright.com (once)

### What to touch periodically
- **Actions** — check for failed runs (after you push a tag)
- **Releases** — check the release page after CI runs (after v0.1.0)
- **Issues** — if you open the repo to public, check for bug reports

### What NOT to touch
- Settings → Webhooks — leave default
- Settings → Branches — don't add branch protection yet (you're solo)
- Settings → Integrations — don't install apps you don't understand

---

## THE 10-MINUTE MONTHLY CHECK (type 3 URLs)

1. `https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble` — check usage gauges
2. `https://dash.cloudflare.com/?to=/:account/billing` — confirm $0 charge
3. `https://github.com/truthprojectofficial-max/truthasaservice/actions` — check for failures

That's it. 3 URLs, 10 minutes, done.