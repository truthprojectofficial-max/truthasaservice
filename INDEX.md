# Order Get It Right — Project Index

> **Read this first. Every session. No exceptions.**
> Last refreshed 2026-07-24. Chain: 40,860 blocks, MATCH.
> Tests: 400 passed, 4 skipped, 0 failed.

---

## MUST DO — before you touch anything

### 1. Verify the chain (10 sec)
```powershell
$env:PYTHONPATH="02_Technical"; python -m src.verify_chain
# MUST print: RESULT: MATCH -- chain is intact.
# If it doesn't match: git checkout HEAD -- 03_Vault/facts_registry.json
```

### 2. Revoke these keys if not done yet (CRITICAL)
- [ ] GitHub PAT → https://github.com/settings/tokens (token `github_pat_11CH7NUY...` is leaked in git history)
- [ ] OpenAI key → https://platform.openai.com/api-keys (`sk-svcacct-ou0TD1H...` leaked)
- [ ] Ollama key → https://ollama.com/settings (`380b8fa6...` leaked)

### 3. Read the current state
- This file (INDEX.md) — you're reading it
- `04_Validation/SESSION_LOG_2026-07-24.md` — what broke + what got fixed
- `04_Validation/MASTER_TICK_LIST_2026-07-24.md` — the full operator action list

### 4. If the vault is dirty (OneDrive corrupted it)
```powershell
git checkout HEAD -- 03_Vault/facts_registry.json 03_Vault/job_registry.json
# Then re-verify: python -m src.verify_chain
```

---

## WHAT THIS PROJECT IS (30 sec)

**Order Get It Right (OGIR)** — Truth as a Service. A deterministic,
air-gapped forensic lie-detector. Given text, it produces a
DeceptionReport with 55-pattern deception detection, Shannon
entropy, BBFB compliance, optionality lattice, and a legal
affidavit. Every decision sealed to a SHA-256 Merkle chain.

- **Operator:** Justin Barnett
- **Jurisdiction:** Commonwealth of Australia (ACL + Evidence Act 1995)
- **Runtime:** Pure stdlib Python 3.12+ (zero network, zero dependencies)
- **Calibration:** 134 cases, 100% accuracy (F1=1.0)
- **Desktop:** Tauri v2 (Rust + WebView2)

---

## LIVE STATE (2026-07-24)

| What | Value |
|------|-------|
| Chain blocks | 40,860 |
| Chain root | MATCH (re-derives clean) |
| Tests | 400 passed, 4 skipped, 0 failed |
| Ontology | v3.10, 55 patterns, R1-R6 gates |
| Branch | `ogir-build-2026-07-18` |
| GitHub | `github.com/truthprojectofficial-max/truthasaservice` |
| Worker | `https://update.ordergetitright.com/health` → 200 OK |
| Domain | `ordergetitright.com` registered (Cloudflare, expires 2027-07-24) |

---

## GTM STATUS — what's done, what's waiting

| Block | Status | Detail |
|-------|--------|--------|
| B Supabase | LIVE | 5 tables (customers, orders, order_files, scans, affidavits), RLS, Google OAuth wired |
| C Google OAuth | WIRED | Client ID in commands.rs, PKCE S256 |
| D Cloudflare Worker | LIVE | Custom domain + workers.dev both serving |
| D KV manifest | LIVE | v0.1.0 manifest pushed, signatures PENDING |
| F Windows EV cert | PURCHASED | $429.99, Certera, token shipping to SA |
| F Tauri updater pubkey | WIRED | pubkey in tauri.conf.json |
| Apple Developer | BLOCKED | Operator hit a wall, macOS ships unsigned |
| Custom domain | DONE | ordergetitright.com registered + Worker deployed |

---

## THE DOCS YOU NEED (in priority order)

### Start here (every session)
1. **This file** (`INDEX.md`) — you're here
2. **`AGENTS.md`** — the rules every agent must follow
3. **`04_Validation/SESSION_LOG_2026-07-24.md`** — what broke + fixes
4. **`04_Validation/MASTER_TICK_LIST_2026-07-24.md`** — operator action list

### Setup + configuration
5. **`04_Validation/SUPABASE_RUNBOOK_2026-07-24.md`** — Supabase setup guide
6. **`04_Validation/HERMES_EMAIL_ADAPTER_SETUP_2026-07-24.md`** — Hermes email alerts
7. **`04_Validation/HERMES_CONFIG_TODO_2026-07-24.md`** — Hermes persona + anti-fabrication
8. **`04_Validation/GTM_OPERATOR_DIRECTIVES_2026-07-24.md`** — full GTM plan (7 blocks)
9. **`04_Validation/BUSINESS_HANDLING_FLOW_2026-07-24.md`** — code→GitHub→Cloudflare→chain flow chart
10. **`04_Validation/REPO_MOVE_RUNBOOK_2026-07-24.md`** — OneDrive → C:\OrderGetItRight move plan
11. **`04_Validation/AGENT_SIGNOFF_POLICY_2026-07-24.md`** — sign-on/off protocol for Hermes/opencode/Aider
12. **`04_Validation/HANDOVER_LOG.md`** — last agent's sign-off (read this at session start)

### Architecture + methodology
13. **`04_Validation/OGIR_PROJECT_STATE_2026-07-24.md`** — 7-skill project review
14. **`01_Methodology/DECEPTION_ONTOLOGY.md`** — the 55 patterns
15. **`01_Methodology/REAL_OPTIONS_LATTICE.md`** — the optionality gate (F7)
16. **`04_Validation/PRIVACY_POLICY_2026-07-24.md`** — 13 APPs + NDB scheme
17. **`04_Validation/NDB_RESPONSE_PLAN_2026-07-24.md`** — breach response plan
18. **`04_Validation/GIT_WORKFLOW.md`** — Git + chain dual-witness model

### Business + legal
19. **`04_Validation/BUSINESS_MODEL_AND_WORKFLOW_RESEARCH_2026-07-24.md`** — business model + trial board + recall + contacts
20. **`04_Validation/OGIR_PROCESS_PLAYBOOK_2026-07-24.md`** — 8-stage flow + daily/weekly/monthly rituals
21. **`04_Validation/LEGAL_HANDLING_2026-07-24.md`** — 10-item legal stack + pre-launch checklist
22. **`04_Validation/PROMOTIONAL_DRESSING_2026-07-24.md`** — layman's pitch + public-facing tidy-up
23. **`04_Validation/PASSWORD_REGISTRY_AND_BCP_2026-07-24.md`** — 12 accounts + bus-factor + BCP checklist
24. **`04_Validation/OGIR_CALIBRATION_RERUN_2026-07-24.md`** — 134-case calibration results

### Maintenance
25. **`04_Validation/MAINTENANCE_PLAN.txt`** — 5-cycle maintenance contract
26. **`.github/copilot-instructions.md`** — Copilot muzzle (10 hard rules)
27. **`contacts/`** — operator, roles, vendors, legal, emergency (all sealed to chain)

---

## HOW TO RUN

```powershell
# From project root:

# Verify chain
$env:PYTHONPATH="02_Technical"; python -m src.verify_chain

# Run tests
python -m pytest tests/ -q
# Expected: 400 passed, 4 skipped

# No-network audit
python 04_Validation/scripts/audit_no_network.py
# Expected: 111 CLEAN, 0 FAIL

# Process an audit case
$env:PYTHONPATH="02_Technical"; python -m src.audit_cli --inbox data/inbox --outbox data/outbox

# Deploy Cloudflare Worker
cd 02_Technical\cloudflare-worker; npx wrangler deploy

# Verify Worker health
curl.exe https://update.ordergetitright.com/health
```

---

## THE SEAL-TEST-VERIFY-COMMIT RITUAL

Every code change:
1. Edit the source
2. Run tests: `python -m pytest tests/ -q` → must pass
3. Verify chain: `python -m src.verify_chain` → must MATCH
4. Seal: `vault_io.append_block("EVENT_TYPE_2026_07_XX", payload)`
5. Commit: `git add -A && git commit -m "EVENT_TYPE_...: block NNNNN sealed. ..."`
6. Verify again: `python -m src.verify_chain` → must still MATCH

---

## WHAT NOT TO DO (never)

- Don't edit audit rows in Supabase Table Editor (desyncs the chain)
- Don't add network imports to `02_Technical/src/` (breaks no-network rule)
- Don't touch `03_Vault/` or `04_Validation/hardcopy/` manually (sealed records)
- Don't run Hermes without the `ogir-builder` persona (causes fabrication)
- Don't push `.env`, `.pfx`, or any key to git (gitignored, double-check)
- Don't run `git push --force` (rewrites chain-bearing history)
- Don't use Supabase Edge Functions (violates air-gap)
- Don't store the vault in OneDrive (already corrupted it once — move repo ASAP)

---

## KNOWN ISSUES (open)

| Issue | Status | Fix |
|-------|--------|-----|
| Vault in OneDrive-synced folder | OPEN | Move repo to `C:\OrderGetItRight` (plan in chat history) |
| D: drive nearly full (8GB free) | OPEN | 50GB Ollama models — can't add more without cleanup |
| WSL Ubuntu registered but no vhdx found | OPEN | Investigate before relying on it |
| 3 leaked keys in git history | OPEN | Revocation is the fix (history rewrite would break chain) |
| GitHub Copilot not configured | DEFERRED | Need `.github/copilot-instructions.md` |
| No LICENSE file | DONE | MIT license added |
| Aider sandbox not created | DONE | `C:\AIDERTESTBOX` created, zero-trust muzzle |
| macOS builds unsigned | BLOCKED | Apple Developer enrollment wall |

---

## VERSIONING

- This index: 2026-07-24 (v2.0 — full rewrite, replaces stale 2026-07-23 version)
- Prior version referenced 35,662 blocks, 272 tests, dead docs — all outdated
- Refresh this file at the start of each session if the state has changed