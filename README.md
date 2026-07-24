# Order Get It Right — Truth as a Service

**Version:** 1.0.0 | **Chain:** 40,870+ blocks, MATCH | **Tests:** 400 passed | **License:** MIT

Forensic deception-detection for business documents. 55 patterns,
Shannon entropy, Merkle chain sealed. Court-grade affidavits.
Air-gapped. Open source.

## What it does

1. Ingests any business document (.txt, .docx, .pdf, email, contract)
2. Extracts structured evidence (price, spec, warranty, compliance)
3. Runs the 4-gate deterministic pipeline:
   - **Deception Gate** — 55-pattern ontology v3.10 + Shannon entropy (R1-R6 gates)
   - **BBFB Gate** — LAW (multiplicative veto) + GRACE (quadratic penalty) + FRUIT (four-pillar weighted score)
   - **Optionality Gate** — deception-adjusted optionality index (NOT a valuation — F7 framing)
   - **Decision Gate** — GO / REVIEW_REQUIRED / REFUSED / REJECT
4. Shows the client what flagged and why (each pattern as a card: ID, name, severity, confidence, matched indicators)
5. Lets the client submit an explanation (sealed to chain, doesn't change verdict)
6. Generates a court-ready affidavit (ACL Section 56 + Evidence Act 1995)
7. Seals every audit decision to a SHA-256 Merkle chain (40,870+ blocks, tamper-evident)

## Calibration

134 cases, 100% accuracy (TP=74, TN=60, FP=0, FN=0, F1=1.0).
Supersedes the prior 89%/118-case claim (2026-07-22).

## Quick start

```powershell
# Verify the chain
$env:PYTHONPATH="02_Technical"; python -m src.verify_chain
# Expected: RESULT: MATCH

# Run the test suite
python -m pytest tests/ -q
# Expected: 400 passed, 4 skipped

# Run the server
cd 02_Technical; python -m uvicorn src.server.app:app --port 3000

# Process an audit case
cd 02_Technical; python -m src.audit_cli --inbox data/inbox --outbox data/outbox
```

## Delivery surfaces

| Surface | What you run | How to build |
|---------|-------------|-------------|
| **HTTP API** | `uvicorn src.server.app:app --port 3000` | `deploy\deploy.ps1` |
| **CLI audit** | `python -m src.audit_cli --inbox <dir> --outbox <dir>` | `deploy\deploy.ps1` |
| **Onyx CLI** | `python -m src.onyx_cli` (11 subcommands) | — |
| **Tauri desktop** | Double-click `OrderGetItRight.exe` | `launchers\Build-Tauri-Desktop.bat` |
| **Landing page** | https://ordergetitright.com | GitHub Pages (`/docs`) |

## Trust model

- **Merkle chain:** 40,870+ blocks, SHA-256 hash chain, append-only. Every audit decision sealed. Verifiable on any host.
- **Air-gapped:** zero network imports in `02_Technical/src/`. No cloud AI in the audit path. Pure stdlib Python 3.12+.
- **Deterministic:** same input + same config = same output. No `random`, no `time.time()`, no `datetime.utcnow()`.
- **Canonical JSON:** every `json.dumps` goes through `canonical_dumps` with `sort_keys=True, separators=(",", ":")`.
- **Court-grade:** affidavits under ACL Section 56 + Evidence Act 1995 (Commonwealth of Australia).

## Project structure

```
00_Strategy/        mission, 6 non-negotiables
01_Methodology/     deception ontology, BBFB, optionality lattice
02_Technical/       the engine (src/, config/, tauri-shell/, web/)
03_Vault/           the Merkle chain (facts_registry.json)
04_Validation/      docs, scripts, calibration, runbooks, contacts
docs/               landing page (GitHub Pages)
tests/              400 tests (conftest.py isolates the chain)
contacts/           operator, roles, vendors, legal, emergency
```

## Read first

1. **`INDEX.md`** — must-do checklist + live state (read this every session)
2. **`AGENTS.md`** — contributor guide (the rules every agent must follow)
3. **`04_Validation/HANDOVER_LOG.md`** — last agent's sign-off
4. **`04_Validation/MASTER_TICK_LIST_2026-07-24.md`** — operator action list

## License

MIT License — Copyright (c) 2026 Justin Barnett. See `LICENSE`.

The Merkle chain (03_Vault/) is append-only. Modifying it
invalidates the audit trail. The runtime (02_Technical/src/) is
air-gapped. Adding network imports invalidates the air-gap guarantee.

## Operator

**Justin Barnett** | Whyalla Norrie, South Australia
**Jurisdiction:** Commonwealth of Australia (ACL + Evidence Act 1995 + Privacy Act 1988)