# OGIR Startup Guide — How to Start, Which Model, What to Use

> **Read this before you open any tool.** Last refreshed 2026-07-27.
> If you're an agent: this doc tells you which model you should be running
> on and what you are / are not allowed to touch. If you're the operator:
> this tells you which tool to launch for the job you have.

---

## 1. The Golden Rule

**The chain is the source of truth.** Only the **build agent** (opencode
+ `glm-5.2:cloud`) is allowed to write to the chain, the vault, or git.
Every other tool is **read-only on the project** — it can think, research,
and draft, but it must not seal, commit, or push.

If a tool is not the build agent and it tries to seal a block, that
block is **unwitnessed** and must be treated as suspect (this is what
happened with the nemotron session on 2026-07-27 — see
`04_Validation/handovers/handover_next_session_2026-07-27.md`, marked
SUPERSEDED).

---

## 2. The Four Scenarios — pick the right one

| Job you have | Tool | Model | Touches chain? | Touches git? | Section |
|---|---|---|---|---|---|
| Sealed project work (code, docs, fixes that must be witnessed) | opencode | `glm-5.2:cloud` | YES | YES | §3 |
| Research / reasoning / review (think out loud, no changes) | opencode (read-only mode) | `glm-5.2:cloud` | NO | NO | §4 |
| Long headless agent session (browser, tools, research) | Hermes | `minimax-m3:cloud` | NO | NO | §5 |
| Pure code drafting (write code, no ritual, no chain) | Aider | `qwen2.5-coder` (local) | NO | NO (sandbox) | §6 |

**Why `glm-5.2:cloud` for both build and reasoning?** You chose it for
reasoning. It's also the build default because it's the only model that
reliably runs the 5-check SIGN_ON ritual without hand-holding. Using it
for both keeps the reasoning quality available when you need to think
inside a build session.

**Why not `nemotron-3-super:cloud` for anything?** It's the model that
hedged, looped, ignored instructions to re-read the handover, and
produced an unwitnessed handover on 2026-07-27. It is **not approved**
for any OGIR work. If you have a reason to use it, seal a
`MODEL_APPROVAL_NEMOTRON_<date>` block first explaining why.

---

## 3. Scenario A — Direct project work (the build agent)

**Use when:** you want to change code, docs, or config AND have the
change sealed to the Merkle chain and committed to git.

**Tool:** opencode
**Model:** `ollama/glm-5.2:cloud` (the default — do not change it)
**Config:** `opencode.json` + `.opencode/agent/build.md` (repo root)

### How to start

1. Open a terminal in the project root:
   `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`
2. Launch opencode. It will auto-load the build agent from
   `.opencode/agent/build.md`.
3. The agent MUST run the SESSION START RITUAL as its first action:
   - `verify_chain` → MATCH
   - read `04_Validation/handovers/HANDOVER_LOG.md` (last block)
   - read `INDEX.md`
   - run `python -m pytest tests/ -q` → 400+ passed
   - seal `AGENT_SIGN_ON_OPENCODE` to the chain
4. If the agent's first action is NOT `verify_chain`, the ritual
   enforcement failed. Stop and tell the operator.

### What this agent can touch

- `02_Technical/` source code
- `04_Validation/` docs
- `03_Vault/` (via `vault_io.append_block` only — never direct edits)
- git commit + push (after SIGN_OFF)

### What this agent must NOT do

- Skip the ritual
- Seal anything without a chain block
- Push without a SIGN_OFF block
- Use a different model without a sealed `MODEL_APPROVAL` block

---

## 4. Scenario B — Reasoning / review session (read-only)

**Use when:** you want to think through a problem, review options,
analyze something, or get a second opinion — WITHOUT changing the
project. The session is **read-only**: no chain writes, no git commits,
no file edits.

**Tool:** opencode (same tool, different mode)
**Model:** `ollama/glm-5.2:cloud` (best reasoning model you have)
**Config:** same `opencode.json`, but you tell the agent "read-only
session, do not seal, do not commit, do not edit files."

### How to start

1. Open a terminal in the project root.
2. Launch opencode. The build agent loads.
3. Tell the agent: **"Read-only reasoning session. Do not run the
   chain ritual, do not seal, do not commit, do not edit any file. I
   want to think through [problem]."**
4. The agent can read any file, search the repo, run read-only commands
   (`verify_chain`, `pytest`, grep, glob). It must NOT call
   `vault_io.append_block`, `git commit`, `git push`, or edit any file.
5. When you have your answer, close the session. No sign-off needed
   because nothing was sealed.

### When to switch to Scenario A

When you've reasoned your way to a decision and want it enacted: open
a fresh build-agent session (Scenario A), give it the conclusion, and
let it seal + commit the work.

### Why "no touch, read-only" matters

A reasoning session that seals blocks pollutes the chain with
half-formed thoughts. A reasoning session that commits pollutes git
with unreviewed drafts. The chain and git are for **decisions, not
deliberation**. Keep deliberation in read-only mode.

---

## 5. Scenario C — Headless Hermes

**Use when:** you want a long-running agent with browser access, tool
use, personas, memory, and multi-turn research. Hermes is your
general-purpose AI assistant — NOT part of the OGIR runtime.

**Tool:** Hermes
**Model:** `minimax-m3:cloud` (the Hermes default in
`C:\Users\justo\AppData\Local\hermes\config.yaml`)
**Config:** `C:\Users\justo\AppData\Local\hermes\config.yaml`

### How to start

1. Double-click `hermes-browser-launcher.bat` in the project root
   (starts headless Chrome on port 9222 for Hermes browser tool).
2. Run `hermes` in a terminal.

### What Hermes can touch in the OGIR repo

- **Read:** any file (for research, context, answering questions)
- **Write:** ONLY files outside the sealed project tree — e.g.
  `.hermes/plans/`, notes in `C:\Users\justo\`, temp files. Hermes
  must NOT edit `02_Technical/`, `03_Vault/`, `04_Validation/`, or
  git-tracked files without operator review.
- **Seal:** NO. Hermes is not a chain witness. If Hermes produces a
  conclusion you want enacted, bring it to a Scenario A build-agent
  session.
- **Commit/push:** NO.

### The `ogir-builder` persona (NOT YET WIRED — open item)

The plan is to add an `ogir-builder` persona to Hermes config.yaml that
bakes in these constraints. Until that's done, the operator must
enforce the read-only rule by instruction. See
`04_Validation/runbooks/HERMES_CONFIG_TODO_2026-07-24.md`.

---

## 6. Scenario D — Code-only sandbox (Aider)

**Use when:** you want to draft code (write functions, refactor,
experiment) with no ritual, no chain, no consequences. Aider proposes;
the sealed chain disposes.

**Tool:** Aider
**Model:** `ollama/qwen2.5-coder:7b-instruct-q4_K_M` (local, offline)
**Sandbox:** `C:\AIDERTESTBOX` (zero-trust — Aider is muzzled, see
`.github/copilot-instructions.md` for the 10 hard rules)

### How to start

1. Open a terminal in `C:\AIDERTESTBOX`.
2. Run `aider` (it auto-loads the local qwen2.5-coder model).
3. Draft code. Aider works in the sandbox copy — it does NOT touch the
   live project tree.
4. When you have a draft you want, copy the file(s) into the real
   project tree and open a Scenario A build-agent session to review,
   test, seal, and commit.

### Why a sandbox

Aider has no chain awareness and no ritual. If it wrote directly to
the project, its changes would be un-witnessed. The sandbox keeps the
drafting separate from the sealing.

### When you want the cloud coder instead of local

If the local 7B is too weak for complex code, you can point Aider at
`qwen2.5-coder` (cloud) by changing the model in the Aider config. The
cloud variant is larger/unquantized — better for hard problems, needs
network. Use local when offline.

---

## 7. How to switch models — the correct way

**For the build agent (opencode):** edit the `model:` frontmatter in
`.opencode/agent/build.md`, then restart opencode. The model is
declared on line 4:

```yaml
---
model: ollama/glm-5.2:cloud
---
```

Change it to e.g. `ollama/qwen2.5-coder:cloud` and restart. **But:**
any model change for the build agent must be sealed as a
`MODEL_APPROVAL_<model>_<date>` block first, recording why and the test
result. The build agent's job is reliability (the ritual), not raw code
speed — only change it if you have a reason and you've tested it.

**For Hermes:** edit `model.default:` in
`C:\Users\justo\AppData\Local\hermes\config.yaml`, then restart Hermes.

**For Aider:** edit the Aider model config in `C:\AIDERTESTBOX`.

**Never** put a model config in `04_Validation/` — that's where the
broken `opencode.json` duplicate lived (now deleted). The only opencode
config that matters is the one at the **repo root**.

---

## 8. Model reference — what's available

### Cloud models (via Ollama Cloud — remote, needs network)

| Model | Best for | Notes |
|---|---|---|
| `glm-5.2:cloud` | Build agent, reasoning, review | The project default. Reliable instruction-following. |
| `minimax-m3:cloud` | Hermes general sessions | Your "mini-3". The Hermes default. |
| `qwen2.5-coder` (cloud) | Code drafting (stronger than local) | Use when local 7B is too weak. |
| `nemotron-3-super:cloud` | **NOT APPROVED** | Hedged + looped on 2026-07-27. Do not use. |

### Local models (offline, on `D:\OllamaModels`, ~50GB)

| Model | Size | Best for |
|---|---|---|
| `Qwen2.5-coder:latest` | 7.6B / 4.7GB | Code drafting (Aider's default) |
| `qwen3.5:9b` | 9.7B / 6.6GB | General / reasoning (offline) |
| `llama3.1:8b` | 8B / 4.9GB | General (offline) |
| `DeepSeek-R1-Distill-Qwen-7B-uncensored` | 7.6B / 6.3GB | Reasoning (R1 distill, offline) |
| `reasoncritic` (FableForge) | 8.2B / 5GB | Reasoning/critique (offline) |
| `gemma3:latest` | 4.3B / 3.3GB | Small general |
| `Llama3.2:latest` | 3.2B / 2GB | Tiny general |
| + 5 others (uncensored/unhinged variants) | | (not recommended for OGIR) |

---

## 9. The 04_Validation/ folder map

(Use this to navigate — the folder was 117 flat files before
2026-07-27. It is now sorted into 10 named folders.)

| Folder | What's in it | Count |
|---|---|---|
| `handovers/` | HANDOVER_LOG.md + all handover_next_session_* + HANDOVER_TO_* | 9 |
| `session_logs/` | SESSION_LOG, SESSION_REPORT, WHY_THIS_FAILED, OLLAMA_TIMEOUT | 4 |
| `build_directives/` | BUILD_DIRECTIVE*, TODO_FULL, MASTER_TODO*, MASTER_TICK_LIST, OGIR_TODO, OPEN_ITEMS | 9 |
| `go_to_market/` | GTM_*, BUSINESS_*, BUDGET_*, PROMOTIONAL_*, MARKETING_*, UI_NAV, TELEGRAM_REJECTION, TAGLINE | 11 |
| `legal_privacy/` | LEGAL_*, PRIVACY_*, NDB_*, ENGAGEMENT_LETTER, CLA_TEMPLATE, IP_RIGHTS | 6 |
| `runbooks/` | SUPABASE_*, HERMES_*, REPO_MOVE, RUNBOOK_*, PASSWORD_REGISTRY, OPERATOR_NOTE, **this file** | 10 |
| `methodology_calibration/` | EVAL_*, OGIR_CALIBRATION*, PRE_2021*, VERIFIED_TRUTHS, HARVESTING, RESPONSIBILITY_SPLIT, DIMINISHING_RETURNS, S_QOL_SWB, AI_INTERACTION*, ANOMALY | 20 |
| `architecture_assessment/` | OGIR_ASSESSMENT*, OGIR_PROJECT_STATE, OGIR_ARCH_DIAGRAM, RESEARCH_COMPAT, BBFB_INTEGRATION, GEM_*, RECONCILIATION, HEAD_TO_TOE, ACCREDITATION, VERIFIED_INTAKE, AUDIT_* | 18 |
| `paper_backup/` | STAGE_PAPER_*, PAPER_BACKUP_CARD*, KNOWN_CHAIN_ARTEFACTS, FILE_INDEX, CHAIN_SUMMARY | 10 |
| `reference_misc/` | SPECS, INTRODUCTION, TROUBLESHOOTING, REPO_SKELETON, GIT_WORKFLOW, AGENT_SIGNOFF_POLICY, MAINTENANCE_PLAN, CHANGELOG, logs, zips, PDFs, YELLOW_RIBBON | 21 |
| (pre-existing) `hardcopy/` `logs/` `pre_2021_intake/` `reports/` `scripts/` `squeal-reports/` | unchanged | — |

**Total: 117 files sorted into 10 new folders + 6 pre-existing subdirs. 0 files flat.**

---

## 10. Quick start — the 30-second version

```
JOB: change project code/docs        → opencode (build agent, glm-5.2:cloud)
JOB: think/review, no changes        → opencode (read-only, glm-5.2:cloud, tell it "read-only")
JOB: long research with browser      → Hermes (minimax-m3:cloud)
JOB: draft code in sandbox           → Aider (qwen2.5-coder local, C:\AIDERTESTBOX)
```

**Never use `nemotron-3-super:cloud` for OGIR work.**
**Never put model configs in `04_Validation/`.**
**Only the build agent seals to the chain.**