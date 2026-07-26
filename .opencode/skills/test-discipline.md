---
description: "Use when writing or running tests. Tests must not seal to the live vault — use the temp-vault fixture. One feature per test file. Adding a public function without a test is a build regression. The boundary test must run first. Host-dependent tests use the skip-guard pattern."
---

# Test Discipline Skill

## Rule 1: Tests must not pollute the live chain

Tests must NOT seal to `03_Vault/facts_registry.json`. Use the per-test
temp-vault fixture in `tests/conftest.py`. After a test run that
accidentally seals, restore immediately:
```powershell
git checkout HEAD -- 03_Vault/facts_registry.json 03_Vault/job_registry.json
```

### Why

Test pollution broke the chain once (2026-07-24: a test sealed block
41,919, pushing the live chain out of sync). The temp-vault fixture
was built to prevent this. If you see the chain count jump after a
test run, you have pollution. Restore from git HEAD.

## Rule 2: One feature per test file

- File naming: `test_*.py`
- One feature per file. Do not lump unrelated tests together.
- The file docstring must state the OPEN_ITEMS id it closes:
  ```python
  """Closes OPEN_ITEMS B3."""
  ```

## Rule 3: Every public function needs a test

Adding a public function without a test is a build regression. The 86+
tests cover every public HTTP endpoint, the orchestrator end-to-end,
the MCP job lifecycle, the ontology integrity, the boundary, the
no-network claim, the determinism promise, Python 3.12 compat, the
deploy dry-run, the agentic REPL schemas, and the canonical JSON
hardening tests.

## Rule 4: The skip-guard pattern

Tests for host-dependent functionality (Tauri build, Ollama
tool-calling, Supabase live) use `pytest.skip(...)` with a clear
message naming the missing dependency:
```python
pytest.skip("FastAPI audit server not running on 127.0.0.1:3000. "
            "Start with: cd 02_Technical && python -m uvicorn "
            "src.server.app:app --port 3000")
```

See `tests/test_b3_host_dependent.py` for the model. Never `xfail` —
that marks a known failure as acceptable. Use `skip` to say "this
test needs something the host doesn't have right now."

## Rule 5: The boundary test runs first

`tests/test_00_99_boundary.py` MUST run first. Any later test that
imports `src.server.app` will fail with a confusing error if the path
setup is missing. The boundary test sets up the import whitelist.

## Rule 6: Tests go through the HTTP API only

The only whitelist exception is `from src.server.app import app`.
Tests mount the FastAPI app via `TestClient`. They do NOT import
`src.agents.*` or `src.engines.*` directly — the boundary test's AST
scan fails the suite if they do.

## The rule

Test pollution is a stop-the-world event (restore the vault). Missing
tests are a build regression. The boundary test is run-order-critical.
The skip-guard pattern is for host-dependent features, not for known
failures.