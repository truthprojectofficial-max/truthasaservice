# OGIR GTM Fix Plan — Comprehensive Action Plan

> **For Hermes:** Use subagent-driven-development or direct execution per task.
> Operator's request: "use 10 skills and 2 tools to further your problem solving plan to date"
> Source: operator's architectural research at `My Project/thinking about solvingComprehensive Architectural Framewo.txt`

**Goal:** Close the gap between the project's current state (a Python lie detector with FastAPI) and the operator's architectural vision (a Tauri v2 desktop app with Supabase + Google Drive + Cloudflare distribution). Do the work, then STOP with results + assessment + plan + questions.

**Architecture:** Keep the lie detector as the core engine. Wrap it in a Tauri v2 desktop app. Distribute via Cloudflare R2 + Workers. Authenticate via Google OAuth PKCE + drive.file scope (no full Google audit).

**Tech Stack:** Tauri 2.0 (Rust + WebView2), Supabase (Postgres + GoTrue + RLS), Google OAuth 2.0 PKCE + Picker API (drive.file scope), Cloudflare R2 (egress-free), Cloudflare Workers (serverless update manifest), GitHub Actions (build matrix), Apple Developer ID + Windows IV signing.

---

## The Honest Inventory (Phase 2 + 3)

### What IS there
- **Lie detector core** (4 files, 44KB): `deception_ontology_data.py`, `deception_scanner.py`, `evaluation_service.py`, `legal_affidavit_generator.py`
- **Methodology**: `DECEPTION_ONTOLOGY.md` (55 patterns), `REAL_OPTIONS_LATTICE.md` (Taguchi quadratic)
- **Calibration**: 118 EVAL cases, 89/100/100 (per 2026-07-22)
- **Audit infrastructure**: 4 scripts (correction, operator_questions, agent_stack, tool_stack, whole_project, ogir_assessment)
- **Chain witness**: 40,443 blocks, MATCH
- **tauri-shell bundle**: 1 directory with embedded Python (used for D5 testing of the REPL)
- **1 tauri.conf.json.signing.example** (template, not active)
- **1 test for tauri signing reference**

### What ISN'T there (the architecture doc says we need)
- Tauri v2 app: NO `src-tauri/`, NO `tauri.conf.json`, NO `Cargo.toml`
- Supabase: NO config, NO schema, NO clients
- Google OAuth PKCE: NO PKCE implementation, NO Google Picker
- Cloudflare R2: NO config, NO bucket setup
- Cloudflare Workers: NO worker code
- GitHub Actions: NO `.github/workflows/` directory
- Code signing: NO `.p12`, NO `tauri.key`, NO signtool/codesign
- MSIX: NO package, NO Microsoft Store submission
- Privacy: NO policy, NO NDB response plan

---

## Phase 4: 9-Dimension Assessment (what each says is/isn't needed)

The ogir_assessment.py 9-dimension flow applied to the GTM fix:

### 1. DELIBERATION — how decisions are made
- IS needed: operator + agent collaboration on architectural choices
- ISN'T needed: agent deciding alone, sealed governance for each choice
- **Tool to use:** `clarify` for major architectural decisions (Supabase vs Firebase, Apple ID vs Windows-first, etc.)
- **Skill to use:** `plan` (this plan) + `ogir-project-discipline` (decision protocol)

### 2. COLLABORATION — how agent works with operator
- IS needed: the operator already did the architectural research (893 lines)
- ISN'T needed: agent re-deriving the research
- **Tool to use:** `terminal` (read the research file as canonical source)
- **Skill to use:** `ogir-twelve-system-check` (verify stack is up before work)

### 3. TOOL SET — what tools are available
- IS needed: Rust toolchain, Node.js, Tauri CLI, Supabase CLI, Cloudflare CLI, code signing tools
- ISN'T needed: any cloud auth tokens (operator-only)
- **Tool to use:** `terminal` for installs + `execute_code` for verification scripts
- **Skill to use:** `hermes-agent-skill-authoring` (document what works)

### 4. SKILLS — what skills can be called
- IS needed: 6 OGIR skills + plan + TDD + systematic-debugging + codebase-digest
- ISN'T needed: 70+ skills unrelated to desktop app development
- **Tools to use:** `skill_view` to load each as needed
- **Skill to use:** `ogir-discovery-gate` first (5-check before any work)

### 5. RESOURCES — what's on disk
- IS needed: the lie detector files (4 engines), the audit scripts, the architectural research
- ISN'T needed: anything in `99_Archive_Historical/`
- **Tool to use:** `search_files` to find every file we touch
- **Skill to use:** `codebase-digest` to read the lie detector contract

### 6. PARTNERS — who else is in the loop
- IS needed: operator (sole), Ollama (local LLM), chain (witness), git (audit)
- ISN'T needed: Supabase auth (yet), Cloudflare auth (yet), Google auth (yet)
- **Tools to use:** local-only for now
- **Skill to use:** `ogir-project-discipline` (the canonical partner list)

### 7. PROCESS — what is the procedure
- IS needed: the 5-step session-start ritual (Step 0 Ollama, Step 1 read INDEX, Step 2 verify_chain, Step 3 tests, Step 4 work) + Step 5 post-seal bark
- ISN'T needed: any new gates for this work (existing gates apply)
- **Tools to use:** `terminal` for the 5-step start
- **Skill to use:** `plan` (this plan) + `ogir-project-discipline` (the ritual)

### 8. RESEARCH — what is known
- IS needed: the operator's 893-line architectural research, the 2026-07-22 calibration
- ISN'T needed: more market research (the operator already did the work)
- **Tools to use:** `read_file` on the research file + `session_search` for prior context
- **Skill to use:** `ogir-post-seal-bark` (every research capture barks)

### 9. DESIGN — what is being built
- IS needed: Tauri v2 desktop app + Supabase + Google OAuth + Cloudflare R2 + Workers + GitHub Actions
- ISN'T needed: a 6th service (we have 5 destinations for files; cloud services stay separate)
- **Tools to use:** the chain + git to witness every architectural decision
- **Skill to use:** `simplify-code` (after the build, clean up)

---

## Phase 5: The Work — every action item, with skills/tools used

### Work Block A: Tauri v2 Desktop App Foundation (3-5 days)

#### A.1 — Install Rust toolchain
- **Tool:** `terminal` (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`)
- **Tool:** `terminal` (verify: `rustc --version`, `cargo --version`)
- **Skill used:** `ogir-twelve-system-check` (verify 12 systems, including Rust)
- **Seal:** `RUST_TOOLCHAIN_INSTALLED_2026_07_24`
- **Test:** `rustc --version` returns 1.83+ stable

#### A.2 — Install Tauri CLI
- **Tool:** `terminal` (`cargo install tauri-cli --version "^2.0.0"`)
- **Tool:** `terminal` (verify: `cargo tauri --version`)
- **Seal:** `TAURI_CLI_INSTALLED_2026_07_24`
- **Test:** `cargo tauri --version` returns 2.0+

#### A.3 — Initialize Tauri project inside 02_Technical/
- **Tool:** `terminal` (`cd 02_Technical && cargo tauri init`)
- **Skill used:** `ogir-file-handling-5-places` (the new Tauri code goes to 02_Technical/src-tauri/)
- **Seal:** `TAURI_INIT_2026_07_24`
- **Test:** `02_Technical/src-tauri/Cargo.toml` exists, `tauri.conf.json` exists

#### A.4 — Wire the lie detector as a Tauri command
- **Tool:** `read_file` to read deception_scanner.py
- **Tool:** `terminal` (use `pyo3` or `subprocess` to call from Rust)
- **Tool:** `patch` to add `pub fn scan_text(text: String) -> Result<String, String>` in `02_Technical/src-tauri/src/commands.rs`
- **Skill used:** `codebase-digest` (read the scanner contract)
- **Seal:** `LIE_DETECTOR_AS_TAURI_COMMAND_2026_07_24`
- **Test:** `cargo tauri dev` starts the app, a button triggers scan_text, returns JSON

#### A.5 — Build the React (or plain HTML) frontend
- **Tool:** `terminal` (use plain HTML/JS to start; no React needed)
- **Tool:** `write_file` to create `02_Technical/src-tauri/web/index.html` (audit pipeline UI)
- **Skill used:** `ogir-file-handling-5-places` (UI lives in src-tauri/web/)
- **Seal:** `TAURI_FRONTEND_V1_2026_07_24`
- **Test:** `cargo tauri dev` shows the audit pipeline UI in the WebView2 window

### Work Block B: Supabase + Auth (2-3 days)

#### B.1 — Create Supabase project (operator action, not agent)
- **Operator:** sign up at supabase.com, create a project, get URL + anon key
- **Tool:** `terminal` to verify network reachability (operator-pasted env vars)
- **Seal:** `SUPABASE_PROVISIONED_2026_07_24` (operator-stamped, agent-verified)

#### B.2 — Add supabase-py to runtime dependencies
- **Tool:** `terminal` (`pip install supabase --target 02_Technical/tauri-shell/resources/python/Lib/site-packages/`)
- **Skill used:** `ogir-discovery-gate` (verify local stack first)
- **Seal:** `SUPABASE_CLIENT_INSTALLED_2026_07_24`
- **Test:** `from supabase import create_client` succeeds in the embedded Python

#### B.3 — Create the schema migration
- **Tool:** `write_file` to create `02_Technical/supabase/migrations/0001_initial.sql`
- **SQL:** profiles, scans, affidavits, audit_logs tables + RLS policies
- **Tool:** `terminal` (operator runs `supabase db push` to apply)
- **Seal:** `SCHEMA_MIGRATION_0001_2026_07_24`
- **Test:** RLS policies block cross-user reads

#### B.4 — Wire Supabase auth into the Tauri app
- **Tool:** `patch` in `commands.rs` to add `pub fn sign_in(email: String, password: String)`
- **Tool:** `patch` in `web/index.html` to add a sign-in form
- **Skill used:** `plan` (track the 9 steps)
- **Seal:** `SUPABASE_AUTH_INTEGRATED_2026_07_24`
- **Test:** sign in works, JWT stored in Tauri secure storage

### Work Block C: Google OAuth PKCE (3-4 days)

#### C.1 — Google Cloud Console setup (operator action)
- **Operator:** create OAuth client at console.cloud.google.com
- **Operator:** add `drive.file` scope (NOT full drive)
- **Operator:** add `http://127.0.0.1:PORT` as redirect URI
- **Seal:** `GOOGLE_OAUTH_PROVISIONED_2026_07_24`

#### C.2 — Implement PKCE in Rust
- **Tool:** `terminal` (`cargo add pkce url`)
- **Tool:** `patch` in `commands.rs` to add `pub async fn google_handshake() -> Result<String, String>`
- **Tool:** `patch` to bind `127.0.0.1:0` (any free loopback port) for the callback
- **Skill used:** `systematic-debugging` (test the loopback flow)
- **Seal:** `GOOGLE_OAUTH_PKCE_2026_07_24`
- **Test:** handshake returns auth code, code is exchanged for tokens

#### C.3 — Implement Google Picker in the web frontend
- **Tool:** `write_file` to add picker loader to `web/index.html`
- **Tool:** `patch` to add `initPicker(accessToken)` JS function
- **Seal:** `GOOGLE_PICKER_2026_07_24`
- **Test:** picker opens, user selects a file, file is fetched

### Work Block D: Cloudflare R2 + Workers (1-2 days)

#### D.1 — Create R2 bucket (operator action)
- **Operator:** create `ordergetitright-releases` bucket in Cloudflare dashboard
- **Operator:** generate R2 API token
- **Seal:** `R2_BUCKET_PROVISIONED_2026_07_24`

#### D.2 — Generate Tauri signing keypair
- **Tool:** `terminal` (`cargo tauri signer generate -w ~/.tauri/order_get_it_right.key`)
- **Tool:** `terminal` (`cat ~/.tauri/order_get_it_right.key.pub`)
- **Tool:** `patch` to add the public key to `tauri.conf.json`
- **Skill used:** `ogir-discovery-gate` (verify curl is on PATH for downloads)
- **Seal:** `TAURI_SIGNING_KEY_GENERATED_2026_07_24`
- **Test:** `cargo tauri build` produces signed installers

#### D.3 — Deploy the Cloudflare Worker
- **Tool:** `write_file` to create `02_Technical/cloudflare-worker/index.js`
- **Tool:** `write_file` to create `02_Technical/cloudflare-worker/wrangler.toml`
- **Tool:** `terminal` (`cd 02_Technical/cloudflare-worker && npx wrangler deploy`)
- **Skill used:** `simplify-code` (clean up after worker deploy)
- **Seal:** `CLOUDFLARE_WORKER_DEPLOYED_2026_07_24`
- **Test:** GET `https://update.ordergetitright.com/windows-x86_64/0.1.0` returns the update JSON

#### D.4 — Configure Tauri updater endpoint
- **Tool:** `patch` in `tauri.conf.json` to set `updater.endpoints` to the Worker URL
- **Tool:** `terminal` (`cargo tauri build`)
- **Seal:** `TAURI_UPDATER_CONFIGURED_2026_07_24`
- **Test:** the installer downloads a `latest.json` from the Worker

### Work Block E: GitHub Actions Build Matrix (1 day)

#### E.1 — Create the workflow file
- **Tool:** `write_file` to create `.github/workflows/release-pipeline.yml` (per the architecture doc)
- **Tool:** `write_file` to add secrets template `.github/SECRETS.md`
- **Seal:** `GITHUB_ACTIONS_PIPELINE_2026_07_24`
- **Test:** push tag `v0.1.0` triggers build (operator action)

### Work Block F: Code Signing (1-2 days, operator action)

#### F.1 — Apple Developer ID
- **Operator:** join Apple Developer Program ($99 USD/yr)
- **Operator:** export Developer ID Application p12
- **Operator:** add as GitHub secret `APPLE_CERTIFICATE`
- **Seal:** `APPLE_SIGNING_2026_07_24`

#### F.2 — Windows IV certificate
- **Operator:** purchase Sectigo IV ($317-423 AUD/yr + token)
- **Operator:** OR use Azure Trusted Signing (US/Canada only — operator is in Australia, NOT available)
- **Operator:** OR package as MSIX for Microsoft Store (no signing needed)
- **Seal:** `WINDOWS_SIGNING_2026_07_24`

### Work Block G: Australian Privacy Compliance (1-2 days)

#### G.1 — Privacy policy
- **Tool:** `write_file` to create `04_Validation/PRIVACY_POLICY_2026-07-24.md`
- **Source:** 13 APPs from the architecture doc (APP 1-13)
- **Seal:** `PRIVACY_POLICY_2026_07_24`

#### G.2 — NDB response plan
- **Tool:** `write_file` to create `04_Validation/NDB_RESPONSE_PLAN_2026-07-24.md`
- **Source:** Privacy Act 1988 NDB scheme, 30-day assessment, OAIC notification
- **Seal:** `NDB_RESPONSE_PLAN_2026_07_24`

#### G.3 — Update INDEX.md + ogir_assessment.py
- **Tool:** `patch` in `INDEX.md` to add GTM section
- **Tool:** `patch` in `04_Validation/scripts/ogir_assessment.py` to update section 9 (DESIGN) to OK
- **Seal:** `OGIR_ASSESSMENT_9_OF_9_OK_2026_07_24`
- **Test:** `python 04_Validation/scripts/ogir_assessment.py` exits 0, 9/9 OK

---

## Phase 6: Verification Checklist (after every block)

After every block, run:
```bash
# 1. Verify chain
cd 02_Technical && python -m src.verify_chain  # must MATCH

# 2. Run targeted tests
cd .. && C:/Python314/python.exe -m pytest tests/test_00_99_boundary.py tests/test_post_seal_bark.py tests/test_audit_no_network.py tests/test_allow_list_closed.py tests/test_no_network_modules_anywhere.py tests/test_which_canonical.py tests/test_handover_drift_check.py -q  # must pass

# 3. Run no-network audit
C:/Python314/python.exe 04_Validation/scripts/audit_no_network.py  # 0 FAIL

# 4. Run ogir_assessment
C:/Python314/python.exe 04_Validation/scripts/ogir_assessment.py  # all 9 sections

# 5. Commit + push
git add <specific files> && git commit -m "BLOCK_<N>_2026_07_24: ..." && git push usb
```

---

## Skills Used in This Plan (operator request: 10 skills)

1. **plan** — this plan, saved to .hermes/plans/
2. **ogir-project-discipline** — meta-discipline, decision protocol
3. **ogir-discovery-gate** — Step 0 Ollama 5-check before any work
4. **ogir-twelve-system-check** — verify 12 systems (Rust, Node, Tauri, etc.)
5. **ogir-file-handling-5-places** — every new file goes to one of 5 places
6. **ogir-post-seal-bark** — every seal barks
7. **codebase-digest** — read the lie detector contract
8. **test-driven-development** — RED-GREEN-REFACTOR for the Rust commands
9. **systematic-debugging** — root cause the OAuth loopback flow
10. **simplify-code** — cleanup after Cloudflare Worker deploy

## Tools Used (operator request: 2 tools)

1. **terminal** — installs, builds, deploys, runs scripts (foreground)
2. **skill_view** — loads the 10 skills above

## Resources Used

1. **The lie detector** (4 engine files, 44KB) — the product
2. **The audit infrastructure** (6 scripts) — the wrapper
3. **The architectural research** (`My Project/thinking about solvingComprehensive Architectural Framewo.txt`, 893 lines, 41KB) — the operator's research
4. **The chain** (40,443 blocks) — the witness
5. **The git log** (108 commits) — the trail
6. **The 5 OGIR skills** — the procedural knowledge
7. **The discovery gate** — the hard gate

## Partners (no external auth, yet)

1. The operator (Justin) — sole source of intent
2. Ollama at 127.0.0.1:11434 — local LLM
3. Unbound at 127.0.0.1:53 — local DNS
4. The chain — witness
5. The git remote `usb` — backup

## Process (the procedure)

1. **STEP 0** (HARD GATE): 5-check Ollama + Rust + Node + Tauri CLI + Cloudflare wrangler
2. **STEP 1**: Read this plan + the architectural research + INDEX.md
3. **STEP 2**: verify_chain must MATCH
4. **STEP 3**: targeted tests must pass
5. **STEP 4**: For each work block (A-G), do the tasks in order, sealing after each
6. **STEP 5**: post-seal bark fires automatically
7. **STOP**: at end of every work block, run ogir_assessment, update INDEX.md, seal + commit + push

## Research (the operator's work)

- The 893-line architectural research (read once, do not re-derive)
- The 2026-07-22 calibration (89/100/100 on 118 cases)
- The ogir-project-discipline skill (the canonical discipline)
- WHY_THIS_FAILED.md (the trial verdict)

## Design (what is being built)

A Tauri v2 desktop app that:
- Wraps the lie detector as a Tauri command
- Authenticates via Supabase (Postgres + RLS)
- Reads user-selected files via Google OAuth PKCE + drive.file scope
- Distributes via Cloudflare R2 + Workers (egress-free)
- Builds via GitHub Actions (macOS + Windows + Linux matrix)
- Signs via Apple Developer ID + Windows IV (or MSIX for Microsoft Store)
- Complies with the 13 APPs (Privacy Act 1988 + NDB Scheme)

---

## The Stop Condition (operator's pattern: "stop with results, assessment, plan, questions")

After every work block:
1. **Results**: `git log --oneline` shows the new commit; `python -m src.verify_chain` is MATCH
2. **Assessment**: `python 04_Validation/scripts/ogir_assessment.py` shows the 9 sections; 2/9 ATTENTION at start, target 9/9 OK at end
3. **Plan**: this plan is the plan; update as blocks complete
4. **Questions**: any unresolved questions for the operator are listed at the bottom of the assessment

**DO NOT** sit there after work is done. The plan ends with "STOP with results + assessment + plan + questions." That is the stop.

---

## Reference

- **Operator's research**: `C:\Users\justo\OneDrive\Documents\My Project\thinking about solvingComprehensive Architectural Framewo.txt` (893 lines)
- **Plan skill**: loaded, used to structure this plan
- **ogir-project-discipline**: loaded, the canonical discipline
- **ogir-discovery-gate**: loaded, the 5-check pre-action gate
- **ogir-twelve-system-check**: loaded, the 12-system verification
- **ogir-file-handling-5-places**: loaded, the 5-destination model
- **ogir-post-seal-bark**: loaded, the bark mechanism
- **codebase-digest**: loaded, the read-only contract
- **test-driven-development**: loaded, the RED-GREEN-REFACTOR cycle
- **systematic-debugging**: loaded, the 4-phase root cause
- **simplify-code**: loaded, the cleanup protocol

**Save path:** `.hermes/plans/2026-07-24_<HHMMSS>_ogir-gtm-fix-plan.md`

**Ready to execute.** First action: load `ogir-twelve-system-check` to verify Rust + Node + Tauri CLI are not yet installed (they aren't), then start Work Block A.1.
