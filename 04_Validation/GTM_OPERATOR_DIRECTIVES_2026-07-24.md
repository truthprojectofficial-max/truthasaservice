# GTM Operator Directives -- What You Do, In Order

**Date:** 2026-07-24
**Author:** opencode session (chain caching + finish-line triage)
**Scope:** The 5 GTM-plan blocks that are operator actions, not code. Code
for blocks A/E/G is already done; B/C/D/F need your hands on external
consoles. This file is the exact click-by-click for each, plus what I need
from you to wire the results back into the code.

Each directive has: WHAT, WHERE (URL/console), WHO (you or me), INPUTS (what
you paste back to me), and VERIFY (how we confirm it landed).

The blocks are independent -- do them in any order, but B (Supabase)
unblocks the most downstream work (scan history, RLS, the dashboard).

---

## Block B -- Supabase (database backend)

### WHAT
Create the Supabase project and apply the schema so the Tauri shell can
store scan history + affidavits per-customer with row-level security.

### WHERE (you)
1. https://supabase.com/dashboard -- sign in, click **New project**
2. Name: `ordergetitright` (or any name). Region: closest to you (e.g.
   `Sydney (ap-southeast-2)` for AU). DB password: generate + save it.
3. Wait ~2 min for provisioning. Open **SQL Editor** -> **New query**.
4. Paste the entire contents of
   `02_Technical/supabase/migrations/0001_initial.sql` and click **Run**.
   Expected: "Success. No rows returned." (DDL -- no rows is correct.)
5. Open **Table Editor** -- confirm 3 tables exist: `customers`, `scans`,
   `affidavits`.

### WHO
- **You:** create project, run the SQL, paste back the 3 values below.
- **Me:** wire the URL + anon key into the Tauri frontend + add a
  `02_Technical/config/supabase.py` client wrapper + a test that connects.

### INPUTS (paste back to me)
After step 4, open **Project Settings** -> **API** and copy:
1. **Project URL** (looks like `https://<ref>.supabase.co`)
2. **anon public** key (the public anon key, NOT the service_role key)
3. The **project ref** (the `<ref>` in the URL, or Settings -> General)

### VERIFY
- I add `02_Technical/config/supabase.py` + a `tests/test_supabase_live.py`
  (skip-guarded like B3) that opens a client, inserts a probe scan into a
  throwaway customer, reads it back, deletes it. PASS = backend live.
- You run `python -m pytest tests/test_supabase_live.py -q` and see 1 pass.

### NOTES
- The schema is the lie-detector schema (customers + scans + affidavits),
  NOT the order-management schema from the 893-line research. The SQL file
  header documents why. Do not apply any older `0001_initial.sql` from git
  history -- there were two prior attempts (Option C, then profiles+audits)
  that the operator corrected.
- RLS is on for all 3 tables. The `handle_new_user` trigger auto-creates a
  customer row on signup. You do not need to seed any data by hand.
- Free tier is fine for now (500 MB DB, 1 GB file storage).

---

## Block C -- Google OAuth (Drive file picker)

### WHAT
Register a Google OAuth client so the Tauri app can open the Google Drive
file picker and import a user's document into a scan. The code in
`02_Technical/src-tauri/src/commands.rs` is already written (PKCE S256,
`drive.file` scope, loopback listener) -- it just needs a real client ID.

### WHERE (you)
1. https://console.cloud.google.com/ -- sign in with a Google account.
2. Create a project (or pick an existing one). Name: `ordergetitright`.
3. **APIs & Services** -> **OAuth consent screen**:
   - User type: **External** (you can switch to Internal later if you have
     a Google Workspace; External is fine for now).
   - App name: `Order Get It Right`. Support email: yours.
   - Scopes: add `.../auth/drive.file`, `openid`, `email`, `profile`.
   - Add yourself as a **test user** (External apps in testing mode only
     allow listed test users -- add your Google account email here).
   - Save.
4. **APIs & Services** -> **Credentials** -> **Create Credentials** ->
   **OAuth client ID**:
   - Application type: **Desktop app** (NOT Web app -- this is a Tauri
     native app using a loopback redirect, not a server with a fixed
     redirect URI).
   - Name: `Order Get It Right Desktop`.
   - Create.
5. Copy the **Client ID** (looks like
   `123456789-abc...apps.googleusercontent.com`). The Client Secret is NOT
   needed for PKCE flow -- do not paste it anywhere.

### WHY `drive.file` and not `drive`
- `drive.file` only lets the app see files it created OR files the user
  picks via the Google Picker. This bypasses Google's 100-user brand
  verification audit (restricted `drive` scope triggers it). The code in
  `commands.rs:33` already uses `drive.file`.

### WHO
- **You:** register the consent screen + client, paste back the Client ID.
- **Me:** replace the `OPERATOR_SET_IN_TAURI_CONFIG` placeholder in
  `commands.rs:178` with the real ID, wire it into `tauri.conf.json` as a
  build config value, add a test that the ID is set (no placeholder left).

### INPUTS (paste back to me)
1. The **OAuth Client ID** string.

### VERIFY
- I add `tests/test_oauth_client_id_set.py` that asserts
  `commands.rs::CLIENT_ID` != the placeholder. PASS = no placeholder.
- Later (after the Tauri build works): you run `cargo tauri dev`, click
  "Import from Drive", sign in to Google in the browser, and the file
  picker opens. That is the end-to-end verify.

### NOTES
- The redirect URI is `http://127.0.0.1:<dynamic port>` -- the code binds
  a free port at runtime (`commands.rs:59`). You do NOT need to configure
  a redirect URI in the Google console for "Desktop app" type; the
  loopback redirect is allowed by spec. If Google prompts for authorized
  redirect URIs anyway, add `http://127.0.0.1` (no port) -- the code's
  dynamic port still matches the loopback-spec rule.
- The app stays in "Testing" mode until you publish. While in testing,
  only the test users you listed can sign in. That's fine for dev.

---

## Block D -- Cloudflare R2 + Workers (binary + update host)

### WHAT
Create the Cloudflare resources so the Tauri auto-updater can check for
new versions and download signed binaries. Two pieces:
1. An R2 bucket holding the release binaries (`.msi`, `.dmg`, `.AppImage`).
2. A Worker at `update.ordergetitright.com` that reads release metadata
   from KV and returns the Tauri updater manifest.

The Worker code is already written
(`02_Technical/cloudflare-worker/src/index.js`, 4 routes). The
`wrangler.toml` has the KV + R2 bindings commented out -- they need real
IDs.

### WHERE (you)
1. https://dash.cloudflare.com/ -> sign up / sign in.
2. **R2** (left sidebar) -> **Create bucket** -> Name:
   `ordergetitright-releases`. Note the bucket name.
3. **Workers & Pages** -> **Create application** -> **Worker** ->
   name it `ordergetitright-updater`. Deploy the starter (we'll overwrite
   it).
4. Install the Wrangler CLI locally:
   `npm install -g wrangler` then `wrangler login` (opens browser, auth
   Cloudflare).
5. From `02_Technical/cloudflare-worker/`, run:
   `wrangler kv:namespace create UPDATES_KV`
   Copy the `id` it prints.
6. **DNS:** add a custom domain `update.ordergetitright.com` to the Worker
   (Workers & Pages -> your worker -> **Triggers** -> **Add Custom
   Domain**). You must own `ordergetitright.com` in Cloudflare's DNS for
   this. If you don't own the domain yet, register it first (Block D
   prerequisite), or skip the custom domain and use the
   `<worker-name>.<account>.workers.dev` URL temporarily.

### WHO
- **You:** create R2 bucket, create Worker, create KV namespace, paste
  back the KV id + your Cloudflare account ID.
- **Me:** uncomment + fill the `wrangler.toml` bindings with the real IDs,
  write a `tests/test_cloudflare_worker_bindings.py` that asserts no
  placeholder remains, and give you the exact `wrangler deploy` command.

### INPUTS (paste back to me)
1. The **KV namespace id** from step 5.
2. Your **Cloudflare account ID** (dash.cloudflare.com -> right sidebar
   when viewing any resource, or the URL
   `https://dash.cloudflare.com/<account-id>`).
3. Confirm whether you own `ordergetitright.com` in Cloudflare DNS. If not,
   I'll configure the updater to use the `workers.dev` URL for now.

### VERIFY
- I run `wrangler deploy` (or you do -- needs your login). Then:
  `curl https://update.ordergetitright.com/health` (or the workers.dev
  URL) returns `{"ok": true}`. That is the Worker live verify.
- Later: on first signed release, you upload the binary to R2 + write the
  version metadata to KV; the Tauri app polls `/latest` and offers the
  update. That is the end-to-end verify.

### NOTES
- R2 free tier: 10 GB storage, 1 million class A ops/month. Plenty for a
  few release binaries.
- Workers free tier: 100k requests/day. Fine for an updater poll.
- The Worker reads `UPDATES_KV` for the manifest. The key format is
  `<platform>:latest` (e.g. `windows:latest`), value is JSON with
  `version`, `pub_date`, `url`, `signature`. The
  `02_Technical/cloudflare-worker/src/index.js` route
  `/:platform/:clientVersion` returns 204 (up-to-date) or the manifest
  (newer version). You only write to KV on release; I'll give you the
  exact `wrangler kv:key put` command when we cut v1.

---

## Block F -- Code signing (Apple Developer ID + Windows EV cert)

### WHAT
Get the signing identities so the Tauri build can produce installers that
the OS will run without a "unknown publisher" warning, and so the
auto-updater can verify update signatures (Tauri's updater checks the
binary against a pubkey baked into the app).

This is the most expensive block (real money + identity verification) and
the longest lead time (Apple: ~1 week; Windows EV cert: 1-7 days). Start
it first if you want to ship.

### WHERE (you)

#### Apple (macOS builds)
1. https://developer.apple.com/programs/ -- enroll in **Apple Developer
   Program**. Cost: USD $99/year. Requires your real identity (driver's
   license etc.) -- Apple verifies it; takes 1-7 days.
2. Once enrolled, create a **Developer ID Application** certificate (this
   is the one for distributing outside the App Store):
   - https://developer.apple.com/account/resources/certificates/list
   - **+** -> **Developer ID Application** -> follow the CSR flow.
3. Create a **provisioning profile** is NOT needed (that's iOS). For
   macOS notarization you also need an **App-specific password**:
   appleid.apple.com -> Sign-In & Security -> App-Specific Passwords.

#### Windows (Windows builds)
1. Buy an **EV Code Signing Certificate** (OV is cheaper but Windows
   SmartScreen takes weeks to trust an OV cert; EV is trusted immediately).
   Sources:
   - https://www.digicert.com/signing/code-signing-certificates (EV, ~$399/yr)
   - https://www.ssl.com/buy-code-signing-certificates (EV)
   - Sectigo / GlobalSign also sell EV certs.
2. The CA verifies your identity (business registration or personal ID)
   -- 1-7 days. They issue the cert on a hardware token (USB) for EV;
   you must sign on a machine with the token plugged in.
3. Export the cert to a `.pfx` (with private key) for the CI build, OR
   keep the token for local signing and use a cloud signing service
   (e.g. Azure Key Vault, SignPath Foundation free for OSS -- worth a
   look if you want free Windows signing for an open-source project).

### WHO (where and who does that)
- **You:** enroll + pay + pass identity verification for both Apple and
  Windows. Export the signing material. Paste back the public-key hashes
  (NOT the private keys).
- **Me:** wire the secrets into `.github/workflows/release-pipeline.yml`
  (the secrets are already named there: `APPLE_CERTIFICATE`,
  `TAURI_SIGNING_PRIVATE_KEY`, `WINDOWS_CERTIFICATE`). I add a
  `tests/test_signing_secrets_documented.py` that asserts the workflow
  references all required secrets (not their values -- just the names).

### INPUTS (paste back to me)
1. **Tauri updater pubkey**: run
   `npx @tauri-apps/cli signer generate -w .tauri/ogir-updater.key`
   from `02_Technical/src-tauri/`. It prints a **public key** (safe to
   share) and writes a **private key** (DO NOT share -- you'll add it as
   the `TAURI_SIGNING_PRIVATE_KEY` GitHub secret). Paste me the public key
   -- it goes into `tauri.conf.json` `plugins.updater.pubkey`.
2. **Apple Developer ID**: once you have the cert, export it as a `.p12`
   with a password. You'll add the base64 of the `.p12` as the
   `APPLE_CERTIFICATE` GitHub secret and the password as
   `APPLE_CERTIFICATE_PASSWORD`. Tell me when done -- I'll confirm the
   workflow expects them.
3. **Windows cert**: once you have the `.pfx`, add its base64 as the
   `WINDOWS_CERTIFICATE` secret and the password as
   `WINDOWS_CERTIFICATE_PASSWORD`. Tell me when done.

### VERIFY
- After secrets are set: you push a `v0.1.0` git tag. The GH Actions
  `release-pipeline.yml` runs on the 4-platform matrix. The
  `compile-binaries` job signs the macOS + Windows installers. The
  `seal-release` job runs `verify_chain` + `ogir_assessment` and appends
  a release block to the chain. You get a GitHub Release with signed
  artifacts. That is the end-to-end verify.
- The Tauri updater pubkey check: the app, on launch, polls
  `update.ordergetitright.com/latest`; if a newer version exists it
  downloads the binary and verifies the signature against the baked-in
  pubkey. A tampered binary is rejected. This only works once Block D
  (Cloudflare) + Block F (signing) are both done.

### NOTES
- **Do not paste any private keys, .p12 passwords, or cert files to me.**
  Only the Tauri updater *public* key is safe to paste. Everything else
  goes straight into GitHub repository secrets
  (https://github.com/<you>/<repo>/settings/secrets/actions). I never
  need to see the values; I only need to know they're set.
- If you want to defer signing: the build still works unsigned. You just
  get "unknown publisher" warnings on Windows and Gatekeeper prompts on
  macOS, and the auto-updater signature check is skipped. Ship unsigned
  for dev, sign for public release.
- SignPath Foundation (https://signpath.org/) offers free EV code signing
  for verified open-source projects. Worth applying to if you open-source
  the repo -- saves the ~$399/yr Windows EV cert cost.

---

## Tier 4 -- Lie-detector product claims (what "claims" means)

### WHAT
"Claims" = the accuracy numbers you put on the product. Right now the
chain + git log record two calibration runs:
- 2026-07-22: 118 cases, **89% accuracy, 100% recall, 100% neg-precision**.
- 2026-07-24: 8 acceptance cases, **100% accuracy/precision/recall, F1=1.0**.

The 8-case 100% is the operator-acceptance suite (the 8 cases you signed
off on). It is NOT a generalization claim -- 8 cases is too few to claim
"100% accurate" publicly. The 118-case 89% is the broader claim, but it's
from one session and has not been re-run on a fresh dataset.

Tier 4 is: **make the accuracy claim defensible.** Three steps:

1. **Re-run calibration on a fresh 100 cases.** The 118-case set was built
   in one session; a fresh 100-case set (new text, same labelling method)
   proves the 89% is not overfit to that set. Target: >=85% accuracy with
   >=95% recall (the product is a lie-detector; false negatives -- missing
   a deceptive text -- are worse than false positives).
2. **Adversarial test.** Hand-craft 20-30 texts designed to fool the
   scanner: true statements phrased deceptively, lies phrased plainly,
   high-entropy truthful text, low-entropy lies. This is the "red team"
   pass. Document which patterns fired correctly and which missed. Each
   miss is a new DD-NNN pattern or a threshold tweak (sealed as a
   CONSTANTS_BUMP).
3. **Publish the claim with the evidence.** The affidavit generator
   already cites Makita v Sprowles + ACCC v Valve + Section 177. The
   public claim should be: "89% accuracy on a 118-case calibration set
   (2026-07-22); re-verified on a fresh 100-case set (date) at X%."
   Anything stronger (e.g. "100% accurate") is not defensible until the
   fresh set + adversarial test back it.

### WHO
- **You:** source the fresh 100 cases (real text -- contracts, vendor
  emails, witness statements -- that you can label deceptive/truthful
  with ground truth). The 8 acceptance cases were yours; the 100 need to
  be new. This is the hard part -- good labelled data is the bottleneck.
- **Me:** run the eval suite against the new cases, produce the
  per-pattern confusion matrix, write the adversarial test file, propose
  threshold bumps, seal each calibration run to the chain.

### INPUTS (from you to me)
1. A directory of 100 labelled cases (same format as the existing
   `data/samples/` -- one file per case, with the expected
   `is_deceptive` + `expected_patterns` in a sidecar or filename
   convention). Tell me the path and I'll wire it into
   `02_Technical/scripts/run_eval_suite.sh`.
2. (Optional) 20-30 adversarial texts you wrote, labelled, in the same
   format.

### VERIFY
- `python 02_Technical/scripts/run_eval_suite.sh --suite fresh-100` prints
  the accuracy/precision/recall/F1. The run is sealed to the chain
  (`CALIBRATION_RERUN_<date>`). The affidavit generator cites the latest
  calibration. The public claim matches the sealed number.

### WHY THIS IS THE PRODUCT, NOT THE AUDIT
`WHY_THIS_FAILED.md` line 60: "The operator's verdict: the audit is not
the work. The lie detector is the work. The audit is a witness; the lie
detector is the product." Tier 4 is the lie detector's accuracy. The
audit scripts (Blocks A/E/G, the 31 probes, the chain) are the wrapper.
Tier 4 is what the wrapper wraps. Without a defensible accuracy claim,
the product is a 19 KB scanner with nice infrastructure around it.

---

## Summary -- what to start now

| Block | Cost | Lead time | Unblocks |
|-------|------|-----------|----------|
| B Supabase | free | 5 min | scan history, dashboard, live tests |
| C Google OAuth | free | 10 min | Drive import in Tauri |
| D Cloudflare | free | 15 min | auto-updater host |
| F Apple+Windows signing | ~$500/yr | 1-7 days | signed releases, updater verify |
| Tier 4 calibration | your time | 1-3 days sourcing cases | defensible accuracy claim |

**Start F first** (longest lead time, real money). Do B/C/D in one sitting
(free, fast, unblocks me). Tier 4 when you have the cases.

When you paste back any of the inputs above, I'll wire them in, add the
matching test, and run the verify step. Each block produces one chain
block + one git commit.