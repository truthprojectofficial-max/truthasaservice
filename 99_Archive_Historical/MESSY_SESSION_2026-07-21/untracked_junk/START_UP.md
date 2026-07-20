# START UP — Order Get It Right (v1.0.0)

> One page. Read this first. Everything you need to start, run, and keep the
> project running lives here. Operator of record: **Justin Barnett**.

---

## 1. What this project is

**Order Get It Right (OGIR)** is a *deterministic* business-audit and
valuation engine — "Truth as a Service". The market can hand it any
business document (.txt, .docx, .pdf) and receive a defensible,
legally-grounded verdict **without a black box, without a network call,
and without a hosted model**.

The whole pipeline is deterministic: same input + same config = same
verdict on any host. Every decision is sealed to a SHA-256 Merkle chain
(`03_Vault/`) so it is **tamper-evident** and verifiable offline.

---

## 2. How many / per / what can it do (the spec sheet)

| Question | Answer |
|---|---|
| **How many** source modules? | **45** Python modules under `02_Technical/src/` (**7,603 lines**) |
| **How many** agents? | **9**: `form_entry`, `evidence_parser`*, `affidavit`, `lattice_compute`, `audit_review`, `ledger_seal`, `monitor`, `orchestrator`, `tau_firewall` (+ `inventory`, `job_delegator` helpers) |
| **How many** tests? | **23** test files (`tests/test_*.py`) — boundary, maintenance, smoke, ontology, vault, orchestrator, evidence, etc. |
| **How many** audit blocks sealed? | **27,437** blocks on the chain (live, grows with use) |
| **How big** is the vault? | **35.93 MB** (`03_Vault/`); chain journal 0.08 MB, compacted registry 13.69 MB |
| **Per** document: what does it do? | Ingest -> extract evidence -> run **4 gates** -> emit Markdown/PDF/DOCX report + draft a Section 56 ACL demand letter and Section 177 Affidavit |
| **The 4 gates?** | (1) **Deception Gate** -- 54-pattern ontology v3.9 + Shannon entropy; (2) **BBFB Gate** -- LAW (multiplicative veto) + GRACE (quadratic penalty) + FRUIT (weighted product); (3) **Optionality Lattice** -- two-stage compound binomial lattice -> deception-adjusted optionality index; (4) **Decision Gate** -- GO / DEFER / TEST FIRST / REJECT |
| **Decision?** | GO / DEFER / TEST FIRST / REJECT |
| **Can do** offline? | **Yes.** No LLM, no network -- pure Python. |
| **Can do** host-reproducible? | Deterministic verdict/scores/decision; chain is **tamper-evident**, not byte-reproducible across runs (timestamps differ). |
| **Best purpose?** | Defensible business audit / valuation where every decision is on a tamper-evident chain the operator can re-verify offline. Not a hosted SaaS; not an LLM black box. |
| **Python?** | 3.14 (works 3.12+) |
| **Platform?** | Windows (Tauri shell) / Python web server / headless CLI |

\* evidence parsing is via `evidence_parser` (see `src/`).

---

## 3. Start it -- the three ways

All commands run from **`02_Technical/`** unless stated.

### A. Headless CLI (no GUI, fastest -- recommended for audits)

```powershell
cd c:\OrderGetItRight\02_Technical
python -m src.agents.orchestrator                # run one job end-to-end
python -m src.verify_chain                         # verify the whole chain
python -m src.maintenance.scheduler --once --cadence daily   # daily health
python -m src.maintenance.scheduler --once --cadence hourly  # hourly health
```

> Or, even simpler -- run the launcher from the project root and pick a
> number: `cd c:\OrderGetItRight` then `.\start.py`.

### B. Web server

```powershell
cd "...\02_Technical"
python -m uvicorn src.web:app --port 8000     # then open http://localhost:8000
```

### C. Tauri desktop shell (double-clickable)

Open `02_Technical\tauri-shell\` in your Tauri toolchain and build, or run
the shipped binary. The shell wraps the same Python pipeline.

---

## 4. The maintenance layer -- set it and forget it (Option C)

The maintenance layer is **deterministic, no LLM, no network**. It runs 7
routines and seals one block per daily run. **Nothing on a green run
means everything is fine.**

### Drag-strip performance (live, post Options A+B)

| Segment | Time | Notes |
|---|---:|---|
| Reaction time (module reload) | **1 ms** | |
| 60 ft (first block seal) | **5 ms** | + 7 ms root recompute |
| Trap speed (full-chain verify, 27,437 blocks) | **212 ms** | **129,302 blocks/sec** |
| Hourly suite (4 routines) | **306 ms** | PASS |
| Daily suite (7 routines, the quarter mile) | **~10.4 s** | PASS (was 16.5 s before Option B) |

The only "slow" routine is `monitor_briefing` (~10 s) -- a keyword sweep over
the 35 MB vault affidavit. Everything else is sub-quarter-second.

### 7 maintenance routines

```
chain_integrity   chain re-derives to the observed root (MATCH/BROKEN)
job_journal_tail  journal tail == registry == jobs count
vault_growth      block-count delta since last run
disk_usage        vault / outbox / logs / squeal sizes
squeal_backlog    count of squeal-* files (threshold 50)
constants_checksum SHA-1 of config/constants.py (catches silent edits)
monitor_briefing  MonitorAgent oversight sweep + hide-pattern scan
```

### Install the scheduler (Windows Task Scheduler)

From **anywhere**, run once:

```powershell
cd c:\OrderGetItRight\scripts
.\install_scheduler.ps1
```

This creates two tasks:

- **`OGIR-Maintenance-Hourly`** -- every hour, ~0.3 s, **no seal**.
- **`OGIR-Maintenance-Daily`** -- daily at **03:00**, ~10 s, **seals one block**.

Options:

```powershell
.\install_scheduler.ps1 -DailyTime 02:30      # different daily time
.\install_scheduler.ps1 -NoSeal              # read-only observation install
.\install_scheduler.ps1 -Uninstall          # remove both tasks
```

Check it's working:

```powershell
Get-ScheduledTask -TaskName OGIR-Maintenance-*
Start-ScheduledTask -TaskName OGIR-Maintenance-Hourly   # fire it now
```

Reports land in `04_Validation\maintenance_reports\`. On **FAIL** a
`04_Validation\squeal-reports\squeal-*` file is written -- that's your red
flag. Green run = no squeal file.

### Run maintenance manually (no scheduler)

```powershell
cd "...\02_Technical"
python -m src.maintenance.scheduler --once --cadence daily          # seals a block
python -m src.maintenance.scheduler --once --cadence daily --no-seal # observation
python -m src.maintenance.scheduler --loop --interval 3600 --cadence hourly  # foreground loop
```

---

## 5. Where everything lives (the map)

```
OrderGetItRight/
|-- README.md                  <- project overview
|-- START_UP.md                <- THIS FILE (start here)
|-- 00_Strategy/               GOVERNANCE.md, STRATEGY.md
|-- 01_Methodology/            DECEPTION_ONTOLOGY, MATHEMATICS, REAL_OPTIONS_LATTICE
|-- 02_Technical/              THE CODE
|   |-- src/
|   |   |-- agents/            9 agents (form_entry, lattice, audit, seal, monitor...)
|   |   |-- maintenance/       health.py + reporter.py + scheduler.py (CLI)
|   |   |-- io/                vault_io (Merkle chain append/verify/compact)
|   |   `-- web/               FastAPI app
|   `-- tauri-shell/           desktop wrapper
|-- 03_Vault/                  facts_chain.jsonl + facts_registry.json (THE CHAIN)
|-- 04_Validation/             reports, changelog.log, squeal-reports/, maintenance_reports/
|-- scripts/
|   `-- install_scheduler.ps1  <- Option C installer
`-- tests/                     23 test_*.py files
```

---

## 6. Verify integrity any time

```powershell
cd "...\02_Technical"
python -m src.verify_chain          # full Merkle re-derivation (~212 ms, 129k blocks/sec)
```

Output `matches=True` = the chain re-derives from genesis to the current
root. This is the trust anchor -- run it whenever you want peace of mind.

---

## 7. The operator's three habits

1. **Daily glance** at `04_Validation\maintenance_reports\` -- PASS = good,
   a new `squeal-*` file = investigate.
2. **Verify the chain** (`python -m src.verify_chain`) before relying on a
   verdict in anger.
3. **Read the MonitorAgent briefing** before any legal use -- it is the
   human-in-the-loop oversight record. Sign it; seal it
   (`seal MONITOR_BRIEFING_SIGNED <briefing>`).

---

*Deterministic. No LLM. No network. Tamper-evident. Operator: Justin Barnett.*