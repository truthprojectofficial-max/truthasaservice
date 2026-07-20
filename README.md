# Order Get It Right — Verified Processor

**Version:** 1.0.0  **Build:** 2026-07-21  **Operator:** Justin Barnett

A deterministic business audit-valuation engine. It does not do audit *or* valuation; it does both, plus deception detection, and produces a single legally-grounded verdict. It runs without a black box, without a network call, and without a hosted model.

## What it does

1. Ingests any business document (.txt, .docx, .pdf)
2. Extracts structured evidence (price, spec, warranty, compliance)
3. Runs the unified four-gate deterministic pipeline:
   - **Deception Gate** -- 55-pattern ontology v3.10 + Shannon entropy (R1-R6 structural co-text gates)
   - **BBFB Gate** -- LAW (multiplicative veto) + GRACE (quadratic penalty) + FRUIT (four-pillar weighted score)
   - **Optionality Gate** -- two-stage compound binomial lattice producing a deception-adjusted optionality index
   - **Decision Gate** -- GO / DEFER / TEST FIRST / REJECT
4. Generates Markdown, PDF, and DOCX reports
5. Drafts a Section 56 ACL demand letter and a Section 177 Affidavit
6. Seals every action to a SHA-256 Merkle truth ledger
7. Records every operator-observed incident and change to a human-readable changelog

## Two delivery shapes, one engine

The Python engine is the source of truth. The Tauri shell is a thin, auditable wrapper that ships the engine as a single double-clickable desktop binary.

| Surface | What you run | How to build it |
|---------|--------------|------------------|
| **Python install** | `python -m uvicorn src.server:app --port 3000` | `deploy\deploy.ps1` |
| **CLI audit** | `python -m src.audit_cli --inbox <dir> --outbox <dir>` | `deploy\deploy.ps1` |
| **Tauri desktop** | Double-click `OrderGetItRight.exe` | `deploy\build-tauri.ps1` |

Both run on the **same Python engine**, so a verdict produced on a Python install is byte-identical to one produced in the Tauri shell.

## Layout

```
00_Strategy\      Governance charter and operating mandate
01_Methodology\   Human-readable mathematics (no code)
02_Technical\     Python engine + Tauri shell + web UI
   config\        constants.py (named constants), exceptions.py
   src\           runtime
      agents\     orchestrator, job_delegator, 5 agents, tau_firewall,
                  inventory_agent, monitor_agent
      engines\    deception_scanner, bbfb_engine, real_options_lattice,
                  evaluation_service, acl_demand_generator,
                  legal_affidavit_generator, facts_registry,
                  squeal_protocol, deception_ontology_data,
                  evaluation_cases, unified_audit_engine
      io\         vault_io, evidence_parser, extractors, pipeline,
                  report_writer
      server\     app, session_tracker, tracing
      utils\      canonical
   tauri-shell\   Rust + JS desktop binary
   web\          single-file HTML/JS UI
03_Vault\         facts_registry.json, Merkle chain
04_Validation\    changelog.log, deploy.log, audit.log, reports/, governance docs
99_Archive\       frozen snapshots
99_Archive_Historical\  messy-session and drift archives
data\             sample inboxes, default outbox
deploy\           deploy.ps1, build-tauri.ps1
tests\           pytest suite
docs\             operator and developer guides
```

## How to install

### Windows

Open PowerShell as Administrator, `cd` to the project directory, and run:

```powershell
.\deploy\deploy.ps1
```

This provisions the Python runtime, installs the dependencies, and drops four launchers under `C:\OrderGetItRight\launchers\`:

- `Start-Server.bat` -- boots the web UI on `http://127.0.0.1:3000`
- `Run-AuditCli.bat` -- headless batch audit
- `Verify-Tests.bat` -- runs the test suite
- `Build-Tauri-Desktop.bat` -- builds the double-clickable binary

### Tauri desktop binary

```powershell
$env:OGIR_BUILD_TAURI = "1"
.\deploy\deploy.ps1
```

On a host with Rust + Node.js + WebView2, the result is a single `.msi` / `.nsis` installer in `02_Technical\tauri-shell\target\release\bundle\`.

## How to record a change or an incident

When something fails or the operator changes a constant, the operator opens the **Changelog** tab in the UI (or the `04_Validation\changelog.log` file on disk) and writes a one-line summary plus details. Every entry records:

- the timestamp (ISO 8601)
- the type (`incident` / `change` / `rollback` / `observation`)
- the `bin_id` of the exact binary that was running
- a free-form description

This is the **human-facing counterpart to the Merkle truth ledger**: the ledger proves what the engine decided; the changelog records what the operator noticed. Both are required.

## Tests

```
python -m pytest tests/ -v
```

The suite covers health, status, deception, BBFB, evaluation, ACL demand, facts, ledger, ontology integrity, document engine, changelog, MCP job lifecycle, orchestrator end-to-end, canonical JSON hardening, boundary enforcement, host-dependent deployment, Python 3.12 compatibility, agentic REPL, normalization, deploy dry-run, governance reference docs, Tauri signing reference, and legal precedents.

## Non-negotiables

1. **Determinism** -- same input + same config = same verdict, same scores, same decision -- on any host.
2. **No black boxes** -- every formula is in `01_Methodology\`.
3. **Truth ledger** -- every action sealed to a SHA-256 Merkle chain.
4. **Tau firewall** -- 10% extraction ceiling is enforced.
5. **Portable** -- Python install or Tauri binary. Both run the same engine.
6. **Human-documentable** -- every change and incident is recorded with the `bin_id` of the exact binary that was running.
7. **Unified process** -- deception, value, and decision gates run together through one orchestrator, producing a single negating-human-error verdict.
