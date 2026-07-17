# Order Get It Right -- Truth as a Service

**Version:** 1.0.0  **Build:** 2026-07-12  **Operator:** Justin Barnett

A deterministic business audit and valuation engine. The market can
hand it any business documents and receive a defensible, legally-grounded
verdict without a black box, without a network call, and without a
hosted model.

## What it does

1. Ingests any business document (.txt, .docx, .pdf)
2. Extracts structured evidence (price, spec, warranty, compliance)
3. Runs the four-gate deterministic pipeline:
   - **Deception Gate** -- 54-pattern ontology v3.9 + Shannon entropy
   - **BBFB Gate** -- LAW (multiplicative veto) + GRACE (quadratic penalty) + FRUIT (weighted product)
   - **Real-Options Lattice** -- two-stage compound binomial valuation
   - **Decision Gate** -- GO / DEFER / TEST FIRST / REJECT
4. Generates Markdown, PDF, and DOCX reports
5. Drafts a Section 56 ACL demand letter and a Section 177 Affidavit
6. Seals every action to a Merkle truth ledger
7. Records every operator-observed incident and change to a human-readable changelog

## Two delivery shapes, one engine

The Python engine is the source of truth. The Tauri shell is a thin,
auditable wrapper that ships the engine as a single double-clickable
desktop binary.

| Surface | What you run | How to build it |
|---------|--------------|------------------|
| **Python install** | `python -m uvicorn src.server:app --port 3000` | `deploy\deploy.ps1` |
| **CLI audit** | `python -m src.audit_cli --inbox <dir> --outbox <dir>` | `deploy\deploy.ps1` |
| **Tauri desktop** | Double-click `OrderGetItRight.exe` | `deploy\build-tauri.ps1` |

Both run on the **same Python engine**, so a verdict produced on a
Python install is byte-identical to one produced in the Tauri shell.

## Layout

```
00_Strategy\      Governance charter and operating mandate
01_Methodology\   Human-readable mathematics (no code)
02_Technical\     Python engine + Tauri shell + web UI
   config\        constants.py, exceptions.py
   src\           runtime modules
   document_engine\ extractors, parser, report writer, pipeline
   middleware\    tracing, session tracking
   services\      audit, BBFB, lattice, ledger, facts, squeal, ACL,
                  affidavit, evaluation
   tauri-shell\    Rust shell (Cargo.toml, src/, capabilities)
   web\           single-file HTML/JS UI
03_Vault\         facts_registry.json, Merkle chain
04_Validation\    changelog.log, deploy.log, audit.log, reports/
99_Archive\       frozen snapshots
data\             sample inboxes, default outbox
deploy\           deploy.ps1, build-tauri.ps1
tests\            pytest suite
docs\             operator and developer guides
```

## How to install

### Windows (one command)

```powershell
cd C:\path\to\OrderGetItRight
.\deploy\deploy.ps1
```

This provisions the Python runtime, installs the dependencies, and
drops four launchers under `C:\OrderGetItRight\launchers\`:

- `Start-Server.bat` -- boots the web UI on `http://127.0.0.1:3000`
- `Run-AuditCli.bat` -- headless batch audit
- `Verify-Tests.bat` -- runs the test suite
- `Build-Tauri-Desktop.bat` -- builds the double-clickable binary

### Tauri desktop binary

The Tauri shell lives at `02_Technical\tauri-shell\`. To build:

```powershell
$env:OGIR_BUILD_TAURI = "1"
.\deploy\deploy.ps1
```

On a host with Rust + Node.js + WebView2, the result is a single
`.msi` / `.nsis` installer in `02_Technical\tauri-shell\target\release\bundle\`.

## How to record a change or an incident

When something fails or the operator changes a constant, the
operator opens the **Changelog** tab in the UI (or the `04_Validation\changelog.log`
file on disk) and writes a one-line summary plus details. Every entry
records:

- the timestamp (ISO 8601)
- the type (`incident` / `change` / `rollback` / `observation`)
- the `bin_id` of the exact binary that was running
- a free-form description

This is the **human-facing counterpart to the Merkle truth ledger**:
the ledger proves what the engine decided; the changelog records what
the operator noticed. Both are required.

## Tests

```
python -m pytest tests/ -v
```

70 tests covering health, status, deception, BBFB, evaluation, ACL
demand, facts, ledger, ontology integrity, document engine, changelog,
MCP job lifecycle, orchestrator end-to-end, canonical JSON hardening,
boundary enforcement, host-dependent deployment, Python 3.12
compatibility, agentic REPL, normalization, and deploy dry-run.

On a source-only host the suite returns 70 passed and 2 skipped:
the Tauri junction test skips when `C:\OrderGetItRight` is not present,
and the Ollama tool-calling test skips when no tool-capable model is
loaded.

## Non-negotiables

1. **Determinism** -- same input + same config = same output, on any host.
2. **No black boxes** -- every formula is in `01_Methodology\`.
3. **Truth ledger** -- every action sealed to a SHA-256 Merkle chain.
4. **Tau firewall** -- 10% extraction ceiling is enforced.
5. **Portable** -- Python install or Tauri binary. Both run the same engine.
6. **Human-documentable** -- every change and incident is recorded with
   the bin_id of the exact binary that was running.
