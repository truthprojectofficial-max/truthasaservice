# GTM Operator Answers -- Paste Your Values Here

When you finish each block on the external console, paste the values
below. I will read this file and wire them in. Do NOT paste anything
to the chat -- put it here, save, and tell me "answers file updated".

Fill in the lines marked `PASTE:`. Leave a block blank if not done yet.
I will only wire in the blocks that have all their values filled.

======================================================================
BLOCK B -- SUPABASE (you created the project + ran the SQL)
======================================================================

Project URL:
PASTE: https://<ref>.supabase.co

anon public key (Project Settings -> API -> anon public):
PASTE: eyJ...

service_role key (Project Settings -> API -> service_role -- ONLY for the
round-trip live test, NOT for the Tauri app; safe to leave blank if you
don't want the live test to insert/delete probe rows):
PASTE: eyJ...

Did 0001_initial.sql run clean in the SQL Editor? (yes / what error):
PASTE:

======================================================================
BLOCK C -- GOOGLE OAuth (you registered a Desktop app client)
======================================================================

OAuth Client ID (console.cloud.google.com -> Credentials -> your Desktop
client -> Client ID, looks like 123456789-abc...apps.googleusercontent.com):
PASTE:

Client Secret is NOT needed (PKCE flow). Leave it blank.

Did you add yourself as a test user on the OAuth consent screen? (yes/no):
PASTE:

======================================================================
BLOCK D -- CLOUDFLARE (you created R2 + Worker + KV)
======================================================================

KV namespace id (from `wrangler kv:namespace create UPDATES_KV`):
PASTE:

Cloudflare account ID (dash.cloudflare.com -> the account id in the URL
or right sidebar):
PASTE:

Do you own ordergetitright.com in Cloudflare DNS? (yes / no, use workers.dev):
PASTE:

======================================================================
BLOCK F -- CODE SIGNING (Apple + Windows -- longest lead time)
======================================================================

Do NOT paste private keys, .p12 passwords, or cert files here. Only the
public Tauri updater key. Everything else goes straight to GitHub
repository secrets (https://github.com/<you>/<repo>/settings/secrets/actions).

Tauri updater PUBLIC key (from
`npx @tauri-apps/cli signer generate -w .tauri/ogir-updater.key` -- it
prints the public key; the private key stays in the file, do NOT paste it):
PASTE:

Apple Developer Program enrolled? (yes / in progress / not started):
PASTE:

Windows EV cert purchased? (yes / in progress / not started / using SignPath):
PASTE:

GitHub secrets set? (list which: APPLE_CERTIFICATE, APPLE_CERTIFICATE_PASSWORD,
TAURI_SIGNING_PRIVATE_KEY, TAURI_SIGNING_PRIVATE_KEY_PASSWORD,
WINDOWS_CERTIFICATE, WINDOWS_CERTIFICATE_PASSWORD):
PASTE:

======================================================================
BLOCK TIER 4 -- CALIBRATION CASES (when you have them)
======================================================================

Path to a directory of 100 labelled cases (same format as data/samples/):
PASTE:

Path to 20-30 adversarial red-team texts (optional, same format):
PASTE:

======================================================================
NOTES FOR ME (anything else you want me to know)
======================================================================

PASTE:

======================================================================
HOW I READ THIS
======================================================================

When you say "answers file updated", I will:
  1. Read this file.
  2. For each block with all values filled, wire them into the matching
     code file (supabase.py / commands.rs / wrangler.toml / tauri.conf.json).
  3. Add or update the verify test for that block.
  4. Run the verify step + report back here.
  5. Leave blocks with blank PASTE: lines alone -- no partial wiring.