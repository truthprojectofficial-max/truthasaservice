# GitHub Copilot Instructions — OGIR

> This file muzzles GitHub Copilot when it works in this repo.
> Copilot is a coding assistant, NOT an auditor. It proposes;
> the sealed chain disposes.

## The project

Order Get It Right (OGIR) is a deterministic, air-gapped forensic
lie-detector. Every audit decision is sealed to a SHA-256 Merkle
chain in 03_Vault/facts_registry.json. Same input + same config =
same output, on any host. No network in the runtime. No LLM in the
audit path.

## Hard rules Copilot MUST follow

### 1. Never modify these directories
- `03_Vault/` — the Merkle chain. Append-only. NEVER edit, truncate, or re-derive.
- `04_Validation/hardcopy/` — paper trust anchor. NEVER touch.
- `99_Archive_Historical/` — sealed historical records. NEVER touch.
- `99_Archive/` — frozen snapshots. NEVER touch.

### 2. No network imports in 02_Technical/src/
The runtime is air-gapped. Do NOT add `urllib`, `socket`, `http.client`,
`requests`, `aiohttp`, `httpx`, or any network library to any file
under `02_Technical/src/`. The boundary test
(`tests/test_00_99_boundary.py`) enforces this.

### 3. Every state change must seal to the chain
Any code change that affects audit state must call
`vault_io.append_block(event_type, payload)` before committing.
The event_type is in SCREAMING_SNAKE_CASE. The payload includes
`files_changed`, `fix_id`, and `operator`.

### 4. Canonical JSON only
Every `json.dumps` must go through `src.utils.canonical.canonical_dumps`
with `sort_keys=True, separators=(",", ":")`. Never use `default=str`.

### 5. Determinism
No `random`, no `time.time()`, no `datetime.utcnow()`.
Use `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`.

### 6. Python 3.12+ syntax
4 spaces indentation. No tabs. `snake_case` for functions/variables,
`PascalCase` for Pydantic models, `UPPER_SNAKE_CASE` for constants.

### 7. The seal-test-verify-commit ritual
Every code change:
1. Edit the source
2. Run `python -m pytest tests/ -q` → must pass (400+ passed)
3. Run `python -m src.verify_chain` → must be MATCH
4. Seal: `vault_io.append_block("EVENT_TYPE", payload)`
5. Commit: `git commit -m "EVENT_TYPE: block NNNNN sealed. ..."`

### 8. Tests go through the HTTP API only
Tests cannot import from `src/` except `from src.server.app import app`.
The boundary test enforces this with an AST scan.

### 9. The operator is Justin Barnett
`PROJECT_OPERATOR = "Justin Barnett"` in `config/constants.py`.
The chain uses `CHAIN_OPERATOR_ID = "OGIR-OPERATOR"` (pseudonymised).

### 10. Read AGENTS.md before making changes
The full contributor guide is in `AGENTS.md`. Read it.
Follow the 00-99 spatial boundary hierarchy. Follow the naming
conventions. Follow the commit guidelines.

## What Copilot should suggest
- Refactoring that preserves determinism
- New test cases for the evaluation suite
- Documentation improvements
- Bug fixes that include a sealed chain block

## What Copilot should NOT suggest
- Network libraries in 02_Technical/src/
- Editing files in 03_Vault/ or 04_Validation/hardcopy/
- Skipping the chain seal on a state change
- Non-canonical JSON serialisation
- Non-deterministic code (random, time.time, utcnow)