---
description: "Use when adding imports, writing code in 02_Technical/, or writing tests. Enforces the no-network air-gap and the 00-99 spatial boundary. A network import fails the suite and breaks the legal no-black-box claim."
---

# Airgap and Boundary Skill

Two rules that cannot be broken. Both are enforced by tests.

## Rule 1: No network in the runtime

The runtime (`02_Technical/src/`) cannot reach the network. This is a
non-negotiable. The legal claim depends on it: no black box, no cloud
calls, no hidden network dependency.

### What is forbidden in `02_Technical/src/`

- `import requests`, `import urllib`, `import httpx`, `import aiohttp`
- `import socket` (unless loopback-only, on the allow-list)
- Any `http://` or `https://` URL in runtime code
- Any cloud SDK (`boto3`, `google.cloud`, `supabase`)
- `import asyncio` for network I/O

### How to verify

```powershell
python 04_Validation/scripts/audit_no_network.py
# Expected: 111 CLEAN, 0 FAIL (or 119 CLEAN, 0 FAIL)
```

Run this after any code change in `02_Technical/src/`.

### The allow-list (closed set)

Only these loopback/local exceptions are permitted:
- `urllib` in `02_Technical/tools/` (operator CLI surface, out-of-runtime)
- Loopback `127.0.0.1:3000` for the FastAPI server
- The Ollama tool-calling REPL (optional, operator CLI, not in audit path)

The allow-list is a closed set. Adding to it requires a sealed block.

## Rule 2: The 00-99 boundary

```
00_Strategy/        axioms, mission, non-negotiables (docs only)
01_Methodology/     human-readable math, no code
02_Technical/       THE PROGRAM (config/, src/, tools/, tauri-shell/, web/)
03_Vault/           the live Merkle chain (data, not source)
04_Validation/      logs, docs, scripts (not source)
99_Archive/         frozen snapshots
```

### Import rules

| Code location | Can import from | Cannot import from |
|---------------|----------------|-------------------|
| `02_Technical/src/` | `config/`, `src.*` | `03_Vault/`, `04_Validation/` |
| `02_Technical/tools/` | `config/`, `src.*`, `urllib` | `03_Vault/`, `04_Validation/` |
| `tests/` | `from src.server.app import app` (only whitelist) | `src.agents.*`, `src.engines.*` |

### The single vault interface

The ONLY legal interface to the vault is `02_Technical/src/io/vault_io.py`.
No code reads or writes `03_Vault/facts_registry.json` directly. All
sealing goes through `vault_io.append_block`.

### How it is enforced

`tests/test_00_99_boundary.py` runs an AST scan. It MUST run first. Any
test file that imports `src.agents.X` or `src.engines.X` fails the suite.

## The rule

The air-gap is not a preference. It is the legal foundation of the
"no black box" claim. The boundary is not a suggestion. It is the
structure that keeps the audit path clean. Both are test-enforced.
Breaking either fails the suite and invalidates the trust anchor.