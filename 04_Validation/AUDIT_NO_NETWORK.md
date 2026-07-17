# AUDIT_NO_NETWORK

**Date:** 2026-07-17 (extended: tools/, tests/, scripts/; allow-list documented)
**Status:** PASS — 62 CLEAN, 4 ALLOWED, 0 REVIEW, 0 FAIL
**Closes:** OPEN_ITEMS_AND_REFERENCE.md D2

## What this document proves

The build's strongest portability promise is "zero network calls in the runtime". The second-strongest is "operator tools and tests are honest about the network they touch". Until 2026-07-17, the first promise was an artefact (`audit_no_network.py` against `02_Technical/src/`) and the second was an aspiration. This document is the artefact for both.

A third party with the project folder can re-verify both promises in under 30 seconds on any machine with Python 3.12+ installed and no network access. The verification needs nothing but the project folder and the Python standard library.

## How to verify

```bash
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
python 04_Validation/scripts/audit_no_network.py
```

Expected output (last lines):

```
Summary: CLEAN=62  ALLOWED=4  REVIEW=0  FAIL=0
RESULT: PASS -- runtime is offline; tools/ and tests/ are on the allow-list.
The 'no network calls in the runtime, allow-list only outside' promise holds.
```

Exit code: `0` (zero) on a clean build, `1` (one) if any file is REVIEW or FAIL.

There is also an executable test:

```bash
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
python -m pytest tests/test_audit_no_network.py -v
```

Expected: 4/4 pass. The test runs the audit script as a subprocess against a sandboxed copy of the project tree, then mutates the sandbox (adds a network import to a non-allow-listed file, etc.) and confirms the verdict flips. It is the executable proof of the contract.

## Scope

The audit now covers every `.py` file in the project, not just the runtime:

| Scope | Path | Verdict on network import |
|---|---|---|
| Runtime | `02_Technical/src/` | **HARD FAIL** — the runtime promise is broken |
| Operator tools | `02_Technical/tools/` | ALLOWED if on the allow-list; REVIEW otherwise |
| Tests | `tests/` | ALLOWED if on the allow-list; REVIEW otherwise |
| Audit scripts | `04_Validation/scripts/` | ALLOWED if on the allow-list; REVIEW otherwise |
| Vendored runtime | any other bundled tree (none today) | ALLOWED if on the allow-list; REVIEW otherwise |

The runtime is the only scope where a network import is unconditionally fatal. Outside the runtime, a network import is allowed only with an explicit entry in `ALLOW_LIST` in the audit script and a one-line justification in this document. The justification is the contract; the allow-list is the check.

## Verdict taxonomy

- **CLEAN** — the file has no network imports.
- **ALLOWED** — the file has a network import that is on the allow-list for that path.
- **REVIEW** — the file has a network import that is NOT on the allow-list. The operator must decide: remove the import, or add the file + module to the allow-list and document it here.
- **FAIL** (`NETWORK_IMPORT_FOUND`) — the file is inside the runtime tree and has a network import. The runtime promise is broken. This is always a hard failure regardless of any allow-list.

A build is PASS only when every file is CLEAN or ALLOWED.

## The Allow-List

Four files in the project legitimately import network modules. Each has a one-line justification.

### `02_Technical/tools/agentic_repl.py` — `urllib.request`, `urllib.error`

The agentic REPL is the operator's natural-language interface to the audit engine. It talks to a local Ollama instance at `http://127.0.0.1:11434` (the default Ollama bind address) using the stdlib `urllib.request` module. The project is stdlib-only — no `requests`, no `httpx`, no `ollama` Python package. The REPL does NOT touch the public internet. On a host with Ollama running, the REPL exchanges JSON with `127.0.0.1:11434` over loopback. The default model on this host is `qwen3.5:9b` (tool-capable; see OPEN_ITEMS_AND_REFERENCE.md B5).

### `02_Technical/tools/agentic_repl_tools.py` — `urllib.request`, `urllib.error`

The tool-call layer for the agentic REPL. The REPL itself delegates every tool call (`audit_text`, `seal_fact`, `verify_root`, `get_bbfb`, etc.) to the local FastAPI server on `127.0.0.1:3000`, again using stdlib `urllib.request`. Same justification as `agentic_repl.py`: localhost, loopback, stdlib, no public internet.

### `02_Technical/tools/discovery_agent.py` — `socket`

The discovery agent is the operator's DNS / TCP probe. It is invoked explicitly via `onyx> discovery <target_label>` in the third-party assistant REPL. It is not loaded by the audit runtime; it is not imported by any audit path; it does not run during a normal audit. The "operator reaches the network" tool is on the allow-list because that is what the operator asked for when the project was designed.

### `tests/test_d5_agentic_repl.py` — `urllib.request`, `urllib.error`

The D5 end-to-end test exercises the agentic REPL by replaying its Ollama tool-call flow. The test must use the same library the REPL uses (`urllib.request`) so the test is a faithful exercise of the real path. This is the one and only test that touches the network; it is skip-guarded on hosts where Ollama is not running, and is the single environment-dependent skip in the test suite.

## Modules flagged as network-touching

| Module | Why it's flagged |
|---|---|
| `urllib`, `urllib2`, `urllib3` | HTTP client family |
| `requests`, `httpx`, `aiohttp` | Third-party HTTP clients |
| `http`, `http.client` | Standard library HTTP |
| `socket`, `ssl`, `socketserver` | TCP / TLS primitives |
| `smtplib`, `imaplib`, `poplib` | Email protocols |
| `ftplib`, `telnetlib` | Legacy file / shell protocols |
| `asyncio` | Concurrency that, while not networking itself, can be used to drive sockets in this context — flagged for operator review |
| `xmlrpc`, `xmlrpc.client`, `xmlrpc.server` | RPC over HTTP |
| `httplib` | Legacy HTTP client (pre-`http.client` rename) |

The script reads the AST only. It does not import the modules. It does not execute any of the project code. It cannot accidentally phone home because it has no way to.

## Current state (as of 2026-07-17)

```
NO-NETWORK AUDIT (extended) -- 66 .py files
  runtime:   51  (02_Technical/src/ -- hard-fail scope)
  tools/:     4  (operator CLI tools)
  tests/:     9  (pytest)
  scripts/:  11  (04_Validation/scripts/)
Summary: CLEAN=62  ALLOWED=4  REVIEW=0  FAIL=0
```

51 runtime files scanned (all CLEAN), 4 operator tools scanned (3 ALLOWED + 1 CLEAN for the empty `__init__.py`), 9 test files scanned (1 ALLOWED + 8 CLEAN), 11 audit scripts scanned (all CLEAN). The "no network calls in the runtime, allow-list only outside" promise holds.

## What is NOT covered by this audit

1. **Dynamic imports.** The script only catches `import X` and `from X import ...` statements. A `__import__("urllib")` inside a function body would not be caught. A code review must complement this static check.
2. **Subprocess / shell-out.** If a future change invokes `subprocess.run(["curl", ...])` or `os.system("wget ...")` to fetch data, that is not caught by this audit. The test suite's boundary rule (`tests/` may not import from `src/`, except for `src.server.app`) is enforced by a separate test (`tests/test_00_99_boundary.py`).
3. **Compile-time constants.** Strings like `"https://example.com"` embedded as constants in code are not flagged. They would only become network calls if executed. The audit scans imports, not strings.
4. **Files outside the four scopes.** If a future contributor adds a `.py` file to `02_Technical/deploy/`, `02_Technical/tauri-shell/`, or anywhere else, that file is NOT in the current scope. The recommended path is to add the new scope to `ALLOWED_SCOPES` in the script and document it here.

## How to extend

If a new module is added to the runtime that legitimately needs the network (e.g. an "online verification" feature), the recommended path is:

1. Move the network-touching code out of `02_Technical/src/` and into a separate tool under `02_Technical/tools/`, `deploy/`, or `04_Validation/scripts/`.
2. Add the file to the allow-list in `audit_no_network.py` and document it in this file.
3. The runtime stays offline.
4. The deploy script invokes the network-touching CLI as a build step, not as a runtime step.
5. `audit_no_network.py` continues to pass.

If a new tool in `02_Technical/tools/` or `tests/` legitimately needs the network, add it to the allow-list with a one-line justification. Do not "fix" the audit by silently expanding the network scope — the audit's job is to be honest about it.

## When in doubt

If a change introduces a network import outside the allow-list, `audit_no_network.py` will fail. Read the failure message, decide whether the network call is intentional, and either:

- Remove the import (recommended — runtime stays offline).
- Move the offending code to a non-runtime location and add it to the allow-list.
- If the runtime itself needs the network, that is a fork in the project. STOP. The runtime promise is one of the six non-negotiables (STRATEGY.md §3). Talk to the operator before changing it.

The default is: **runtime stays offline. Tools are honest about the network they touch. The chain is the proof.**

---

*This document is sealed to the Merkle chain. To prove it has not been edited, re-derive the Merkle root and compare it to the value in `YELLOW_RIBBON.md` REF-5.*
