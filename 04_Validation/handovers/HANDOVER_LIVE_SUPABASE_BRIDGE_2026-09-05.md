# LIVE SUPABASE BRIDGE STATUS — 2026-09-05

**From:** opencode (local bridge operator, Windows/PowerShell, non-admin)
**To:** GPT-5.3-Codex (GitHub Copilot session `095386c0-49d0-433a-a7bb-563832897b23`)
**Re:** Your 4 handover questions. Answered from the live project, not from docs.

You asked for this status on return:

```
schema applied: yes/no
email auth enabled: yes/no
anon key available: yes/no
live sign-in tested: yes/no
```

---

## Answers

| Question | Status | Evidence |
|---|---|---|
| Schema applied | **YES** | All 3 migrations in `02_Technical/supabase/migrations/` are applied. Live DB has all 8 tables: `customers`, `orders`, `order_files`, `scans`, `affidavits`, `documents`, `document_requests`, `cases`. RLS enabled on every one. 0 rows, 0 auth users (clean slate). |
| Email auth enabled | **YES** | Live probe via `POST /auth/v1/token?grant_type=password` with dummy credentials returned HTTP 400 `invalid_credentials` (not `provider_disabled` / `signup_disabled`) — the email/password provider is live and reachable. No user has signed up yet, so "confirm email" behavior is untested. |
| Anon key available | **YES** | Publishable key `sb_publishable_...` is live and verified against the project URL (matches `get_publishable_keys`); it works for REST calls. Note: the Tauri shell reads `OGIR_SUPABASE_ANON_KEY` — this publishable key serves that purpose. Legacy anon JWT also exists and is enabled. |
| Live sign-in tested | **NO** | No auth users exist (total_users = 0). Requires creating a first user (sign-up) — needs the Tauri shell or a curl signup, plus a decision on whether the first sign-up should be performed by the operator. Left to operator/Codex by design. |

## Bridge wiring (complete on my side)

- GitHub: SSH key authenticates as `truthprojectofficial-max`. Remote `truthasaservice` reachable and fetched.
- Supabase: MCP server connected to project `qqbrpqdbxhypkvvsjble` (AWS ap-northeast-1 / Tokyo). URL + publishable key verified live.
- Project status is **PAUSED** per AGENTS.md — no deploys, no migrations, no spend. This handover does not change that. The env var `GITHUB_PERSONAL_ACCESS_TOKEN` on this machine is **invalid (401)** — the leaked PAT from INDEX.md "MUST DO" section has expired, consistent with it being revoked as instructed.

## SECURITY FINDINGS from live DB (needs action when project resumes)

Verified by querying `pg_policies` and function definitions directly:

1. **CRITICAL — `search_documents` is a live data leak.** It is `SECURITY DEFINER` (bypasses RLS) and callable by `anon` via `/rest/v1/rpc/search_documents` without signing in. Worse, when `filter_customer_id IS NULL` it searches **all customers' documents** and returns `LEFT(d.content_text, 500)` — 500 chars of any customer's uploaded document content to the public internet. Fix when resuming:
   ```sql
   revoke execute on function public.search_documents(text, uuid) from public, anon, authenticated;
   -- then either make it security invoker with an auth.uid() check inside,
   -- or move it out of the exposed public schema.
   ```
2. **HIGH — `customers` public read.** Policy "Allow public read access to customers" is `TO public` with `USING (true)` — anyone with the publishable key can read every customer row (contact emails, business names, ABNs). Fix:
   ```sql
   drop policy "Allow public read access to customers" on public.customers;
   create policy "customers_select_own" on public.customers
     for select to authenticated
     using ((select auth.uid()) = id);
   ```
3. **MEDIUM — UPDATE policies missing `WITH CHECK`.** `customers`, `orders`, `scans`, `affidavits` UPDATE policies have `USING (auth.uid() = customer_id/id)` but **no `WITH CHECK`** — a signed-in user can reassign a row to another user. Per repo AGENTS.md and Supabase best practice: every UPDATE needs both `USING` and `WITH CHECK`. Fix pattern:
   ```sql
   alter policy "Allow individual update access to own scans" on public.scans
     with check ((select auth.uid()) = customer_id);
   -- (repeat for orders, customers, affidavits)
   ```
4. **MEDIUM — `handle_new_user` SECURITY DEFINER callable by anon/authenticated** via REST. It only inserts a customer row on signup trigger — but per the standard fix, revoke public execute:
   ```sql
   revoke execute on function public.handle_new_user() from public;
   ```
   (Trigger calls it as the trigger owner, so revoking PUBLIC execute does not break signup.)
5. **LOW — `orders` has no public INSERT with_check issue** (has WITH CHECK) — OK. `order_files` INSERT OK. DELETE policies don't need WITH CHECK (only ALL/UPDATE do). `cases`/`documents`/`document_requests` policies are correct (TO authenticated + ownership, TO service_role).
6. **RLS role scope note:** Most policies are `TO public` which covers `anon`+`authenticated`+`service_role`+`authenticated` roles. `TO authenticated` + ownership is the tighter pattern per repo AGENTS.md — the current `TO public` INSERT policies do block anonymous inserts because their WITH CHECK requires `auth.uid() = customer_id` (which is NULL for anon), so anon can't actually insert. They work, but should be normalized to `TO authenticated` when resuming.

## Next steps (when resumed)

1. Operator decides: fix security findings now or on resume (project is PAUSED — I did not change the DB).
2. First live end-to-end test: sign-up via Tauri shell or curl (`POST /auth/v1/signup`) → `handle_new_user` trigger creates customer row → run audit → save scan → load recent scans.
3. After fixes: re-run `supabase db advisors` / MCP `get_advisors` — target 0 lints.
4. Tauri Linux host libs (glib-2.0, gobject-2.0) remain a non-blocking local build issue — not fixable from this bridge, does not block Supabase work.

## Keys & credentials (for operator)

- Publishable key: safe for browser/Tauri UI (`OGIR_SUPABASE_ANON_KEY` value = publishable key `sb_publishable_...`).
- Service role key: needed only for live admin tests (`tests/test_supabase_live.py`), never commit.
- The invalid `GITHUB_PERSONAL_ACCESS_TOKEN` env var on the Windows machine should be removed or regenerated by the operator — gh CLI currently can't authenticate; SSH works fine.

---

**Hand-off note:** This file is informational — no DB change, no schema change, no spend. Vault chain verified MATCH before writing (block height 41094, per `04_Validation/handovers/HANDOVER_LOG.md`). Local Next.js scaffold in `C:\Users\justo\work\truthproject-official-max\` is NOT part of this repo — it is a separate paused Supabase scaffold, kept local per its own AGENTS.md.