# Repository Guidelines

Order Get It Right — Truth as a Service. A deterministic, air-gapped
business audit and valuation engine. Every audit decision is sealed
to a SHA-256 Merkle chain. Same input + same config = same output,
on any host. No network in the runtime. No LLM in the audit path.

This file is the contributor guide. Read it before you change anything.

## Project Structure & Module Organization

The project follows the strict 00-99 spatial boundary hierarchy
enforced by `tests/test_00_99_boundary.py`:

```
00_Strategy/        axioms, mission, 6 non-negotiables (STRATEGY.md, GOVERNANCE.md)
01_Methodology/     human-readable math, no code (DECEPTION_ONTOLOGY.md, MATHEMATICS.md, REAL_OPTIONS_LATTICE.md)
02_Technical/       THE PROGRAM
  config/           constants.py (the 19 named constants), exceptions.py
  src/              runtime (agents/, engines/, io/, server/)
  tools/            operator CLI surface (out-of-runtime; uses urllib)
  tauri-shell/       Rust + JS desktop binary
  web/              single-file dark-themed HTML UI
  03_Vault/         the Merkle chain (facts_registry.json)
  04_Validation/    local copy of changelog
03_Vault/           (legacy; the live chain is 02_Technical/03_Vault/)
04_Validation/      17 docs + hardcopy/ + scripts/ + squeal-reports/ + logs/
99_Archive/         frozen snapshots
data/               inbox (5 SEED samples) + outbox + samples
deploy/             deploy.ps1 + build-tauri.ps1
launchers/          4 .bat files (server, audit, verify, build)
tests/              8 test files, 72 collected (70 pass + 2 skip-guard on a source-only host)
```

The single legal interface to the vault is `02_Technical/src/io/vault_io.py`.
Code in `02_Technical/` cannot import from `03_Vault/` or `04_Validation/`.
Tests cannot import from `src/` except `from src.server.app import app`
(whitelisted, the only FastAPI surface the tests mount).

## Build, Test, and Development Commands

All commands run from the project root unless noted.

```
python -m pytest tests/ -v                        # 70 pass + 2 skip-guard (Tauri junction not present; Ollama tool-calling model not loaded)
python -m src.verify_chain                        # MATCH + Merkle root
python -m src.verify_chain --print-refs            # 6 reference fingerprints
python -m src.audit_cli --inbox data/inbox --outbox data/outbox
python -m src.third_party_assistant                # onyx> REPL (12 commands)
python -m src.onyx_cli ledger                      # 11 subcommands
python 04_Validation/scripts/audit_no_network.py   # 0 network imports (PASS)
python 04_Validation/scripts/phase_4_refresh_fingerprints.py
powershell -File deploy/deploy.ps1 -DryRun         # 14-step dry-run report
.\launchers\Verify-Chain.bat
.\launchers\Verify-Tests.bat
.\launchers\Build-Tauri-Desktop.bat
```

Python 3.12+ (tested on 3.14.6). The runtime is pure stdlib; the 10 third-party
packages in `02_Technical/requirements.txt` are pure-Python and vendorable.

## Coding Style & Naming Conventions

- **Indentation:** 4 spaces. No tabs. Python 3.12+ syntax only (no PEP 695
  type aliases in runtime; `tests/test_b4_python_312_compat.py` enforces).
- **Naming:** `snake_case` for functions and variables, `PascalCase` for
  Pydantic BaseModels, `UPPER_SNAKE_CASE` for constants in
  `config/constants.py`, `DD-NNN` for deception patterns (zero-padded 3
  digits, sequential).
- **Type hints:** required on every public function.
  `from __future__ import annotations` is allowed; PEP 604 `X | None` is
  not yet detected by the Ollama schema builder.
- **Determinism:** no `random`, no `time.time()`, no `datetime.utcnow()`.
  Use `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`.
- **Canonical JSON:** every `json.dumps` MUST pass through
  `_canonical_default` (see `02_Technical/src/utils/canonical.py`) with
  `sort_keys=True, separators=(",", ":")`. Never write a `default=str`
  band-aid.
- **Chain seal:** every state-changing operation calls
  `vault_io.append_block` with `event_type` in `SCREAMING_SNAKE_CASE`.
  NIZK proof is a SHA-256 of the canonical JSON payload plus the
  operator identity constant.

## Testing Guidelines

- **Framework:** pytest 9.x. Project config in `pyproject.toml`.
- **Boundary:** tests go through the HTTP API only. The 00-99 boundary
  test enforces this with an AST scan; importing `src.agents.X` or
  `src.engines.X` in a test file fails the suite.
- **Skip-guard pattern:** tests for host-dependent functionality
  (Tauri build, Ollama tool-calling) use `pytest.skip(...)` with a
  clear message naming the missing dependency. See
  `tests/test_b3_host_dependent.py` for the model.
- **Naming:** `test_*.py`, one feature per file. The file docstring must
  state the OPEN_ITEMS id it closes (e.g. "Closes OPEN_ITEMS B3").
- **Coverage:** no coverage gate. The 70 tests cover every public HTTP
  endpoint, the orchestrator end-to-end, the MCP job lifecycle, the
  ontology integrity, the boundary, the no-network claim, the
  determinism promise, the Python 3.12 compat, the deploy dry-run,
  the agentic REPL schemas, and the canonical JSON hardening tests.
  Adding a public function without a test is a build regression.
- **Run order:** `tests/test_00_99_boundary.py` MUST run first; any
  later test that imports `src.server.app` will fail with a confusing
  error if the path setup is missing.

## Commit & Pull Request Guidelines

This project does not currently use Git (the chain is the version
control). The changelog is `04_Validation/changelog.log` (JSONL, one line
per cycle). Format:

```json
{"binId": "codex-on-Justo", "timestamp": "2026-07-12T03:14:16Z", "type": "change",
 "summary": "<one-line>", "details": "<file:line + before/after + test result>"}
```

Types: `change` (code modified), `observation` (daily cycle), `incident`
(something broke), `rollback` (rolled back to a prior USB), `marker`
(chain-only seal), plus named one-shot events
(`OPEN_ITEMS_X_CLOSED_2026_07_12`, `FORK_RESOLVED_2026_07_16`).

If/when Git is adopted: commit subject is the `summary`; body lists the
files changed with `file:line` references. PR descriptions must include:
(1) chain root before and after, (2) new test count, (3) OPEN_ITEMS id
closed, (4) a paste of the relevant `04_Validation/RECONCILIATION_*` or
`CONTEXT_WINDOW.md` section. Any change to `config/constants.py` is a
`CONSTANTS_BUMP` and requires a sealed block.

## Architecture Overview (one paragraph)

Five named agents — Form_Entry, Audit_Review, Lattice_Compute, Ledger_Seal,
Affidavit — wired by the `Orchestrator` (one runtime entry point) through
`AgentJobDelegator` (MCP hand-off, URN `OGIR:<SPACE>:<ACTION>`). Every
state change is sealed to the Merkle chain via `vault_io.append_block`.
Every audit input runs the 4-gate pipeline: 54-pattern Deception ontology
v3.9 + Shannon entropy, BBFB engine (LAW multiplicative veto + GRACE
quadratic penalty + FRUIT weighted product + CVS), Real-Options compound
binomial lattice, Decision gate. The runtime is pure stdlib Python; the
agentic REPL (Ollama tool calling) is an optional operator CLI that
calls the FastAPI server at `127.0.0.1:3000`. The Tauri shell wraps the
same engine as a native WebView2 binary.

## Security & Configuration Tips

- `NO_NETWORK=1` is enforced by `audit_no_network.py`. The runtime cannot
  reach the network. Do not add network imports; the boundary test will
  fail.
- `TAU_EXTRACTION_CEILING = 0.10` is enforced by `TauFirewall` in
  `02_Technical/src/agents/tau_firewall.py`. Heavy operations call
  `assert_within_ceiling(label)`. Do not bypass the firewall.
- The 19 constants in `02_Technical/config/constants.py` are the
  entire runtime. A `CONSTANTS_BUMP` requires a sealed block recording
  the old value, the new value, the reason, and the test result.
- The hard-copy backup is at `04_Validation/hardcopy/`. The Merkle root
  on the paper card is the trust anchor. Refresh on every quarterly
  cycle.
- The operator identity is `PROJECT_OPERATOR = "Justin Barnett"`. The
  boundary test enforces no other identity can claim to operate the
  build without forking the source tree and updating the constant.