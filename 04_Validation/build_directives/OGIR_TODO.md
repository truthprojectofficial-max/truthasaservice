# OGIR TODO -- WHAT'S LEFT, WITH LINKS

**Last updated:** 2026-07-24 (this session)
**Review at every session start.** Run the verification commands in
`04_Validation/SESSION_LOG_2026-07-24.md` section 6 first.

======================================================================
DONE THIS SESSION (sealed block 40852, pushed to GitHub)
======================================================================
[x] Vault corruption fixed (OneDrive trailing garbage stripped)
[x] Chain integrity restored (git HEAD, 40722 blocks, MATCH)
[x] Chain caching (vault_io.py, F7 suite 78s -> 55s)
[x] GitHub repo: github.com/truthprojectofficial-max/truthasaservice
[x] Block B Supabase: LIVE (https://qqbrpqdbxhypkvvsjble.supabase.co)
[x] Block C Google OAuth: WIRED (client ID in commands.rs)
[x] Block D Cloudflare: LIVE (Worker + R2 + KV)
[x] Block F Tauri updater pubkey: WIRED (tauri.conf.json)
[x] Tier 4 calibration: 134 cases, 100/100/100, F1=1.0
[x] Session log + this TODO documented

======================================================================
TODO -- OPERATOR ACTION (paid / identity-verified)
======================================================================

[ ] WINDOWS EV CODE SIGNING CERTIFICATE
    Why: so Windows builds run without "unknown publisher" warning
          + Tauri updater can verify signed updates
    Cost: ~$299-399/yr
    Lead time: 1-7 days (CA verifies your identity)
    Where to buy (pick one):
      - https://www.ssl.com/buy-code-signing-certificates/ (EV, ~$359)
      - https://www.digicert.com/signing/code-signing-certificates (EV, ~$399)
      - https://sectigo.com (EV, ~$299)
    FREE alternative for open source:
      - https://signpath.org/ -- free EV signing for verified OSS projects
    After you have the .pfx:
      1. Base64-encode it: certutil -encode cert.pfx cert.b64
      2. Go to: https://github.com/truthprojectofficial-max/truthasaservice/settings/secrets/actions
      3. Add secret: WINDOWS_CERTIFICATE = (the base64 string)
      4. Add secret: WINDOWS_CERTIFICATE_PASSWORD = (the .pfx password)
    No code change needed -- .github/workflows/release-pipeline.yml
    already references these secret names.
    WHEN DONE: tell the agent "windows cert done" and it will verify
    by checking the secrets are set (via a test that the workflow
    references them).

[ ] APPLE DEVELOPER ID (BLOCKED -- hit a wall)
    Why: so macOS builds run without Gatekeeper warning
    Cost: $99/yr
    Where: https://developer.apple.com/programs/
    Status: operator hit a brick wall enrolling. NOT pursuing for now.
    macOS builds will ship unsigned (Gatekeeper warning only) until
    this is unblocked.
    WHEN UNBLOCKED: enroll, create a Developer ID Application cert,
    export as .p12, add APPLE_CERTIFICATE + APPLE_CERTIFICATE_PASSWORD
    as GitHub secrets.

[ ] CUSTOM DOMAIN ordergetitright.com
    Why: so the Tauri updater points at update.ordergetitright.com
    instead of the workers.dev URL
    Cost: ~$10-15/yr for the domain
    Where: register in Cloudflare (you already have a Cloudflare account)
      - https://dash.cloudflare.com -> Register Domain -> ordergetitright.com
    After you own it:
      1. Tell the agent "domain registered"
      2. Agent adds the routes block back to wrangler.toml:
         routes = [{ pattern = "update.ordergetitright.com/*", custom_domain = true }]
      3. Agent updates tauri.conf.json updater endpoint back to
         https://update.ordergetitright.com/...
      4. You run: npx wrangler deploy (from 02_Technical/cloudflare-worker/)
      5. Verify: curl.exe https://update.ordergetitright.com/health -> OK

======================================================================
TODO -- AGENT CAN DO (no operator action needed)
======================================================================

[x] Temp-vault fixture for tests (DOING NOW -- see below)

======================================================================
VERIFICATION LINKS (check these are still live)
======================================================================
Supabase dashboard:    https://supabase.com/dashboard/project/qqbrpqdbxhypkvvsjble
Supabase API:         https://qqbrpqdbxhypkvvsjble.supabase.co
Google OAuth console: https://console.cloud.google.com/apis/credentials
Cloudflare dashboard: https://dash.cloudflare.com
Worker health:        https://ordergetitright-updater.truth-project-official.workers.dev/health
GitHub repo:          https://github.com/truthprojectofficial-max/truthasaservice
GitHub secrets:       https://github.com/truthprojectofficial-max/truthasaservice/settings/secrets/actions

======================================================================
THE CHAIN WITNESS (every file that hit home)
======================================================================
Block 40852 | SESSION_WIRED_2026_07_24 | 85f55dfc2e04
Files sealed:
  02_Technical/config/supabase.py          (Block B)
  02_Technical/src-tauri/src/commands.rs    (Block C)
  02_Technical/cloudflare-worker/wrangler.toml (Block D)
  02_Technical/src-tauri/tauri.conf.json    (Block F)
  02_Technical/src/io/vault_io.py           (chain caching)
  tests/test_supabase_live.py
  tests/test_oauth_client_id_set.py
  tests/test_cloudflare_worker_bindings.py
  04_Validation/SESSION_LOG_2026-07-24.md
  04_Validation/OGIR_CALIBRATION_RERUN_2026-07-24.md
  04_Validation/GTM_OPERATOR_DIRECTIVES_2026-07-24.md

Verify the witness:
  $env:PYTHONPATH="02_Technical"; python -m src.verify_chain
  Expected: MATCH at block 40852 (or higher if new seals added)