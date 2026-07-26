---
description: "Use when writing Python in 02_Technical/. Python 3.12+ only. 4-space indent, no tabs. snake_case functions/vars, PascalCase Pydantic models, UPPER_SNAKE_CASE constants. Type hints required on every public function. No PEP 695 type aliases in runtime. from __future__ import annotations is allowed."
---

# Python Style Skill

## Python version

3.12+ (tested on 3.14.6). No syntax that requires a newer version in
runtime code. `tests/test_b4_python_312_compat.py` enforces.

## Indentation

- 4 spaces. No tabs. Ever.
- No mixed indentation in any file.

## Naming conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | `snake_case` | `run_audit_pipeline` |
| Variables | `snake_case` | `deception_score` |
| Pydantic BaseModels | `PascalCase` | `DeceptionReport` |
| Constants (in `config/constants.py`) | `UPPER_SNAKE_CASE` | `LAW_VETO_THRESHOLD` |
| Deception patterns | `DD-NNN` (zero-padded 3 digits) | `DD-057` |

## Type hints

Required on every public function. Private helpers may omit them, but
public functions (anything called from another module) must be typed.

```python
# CORRECT
def run_audit(text: str, config: AuditConfig) -> DeceptionReport:

# WRONG
def run_audit(text, config):
```

## What is allowed

- `from __future__ import annotations` — allowed, enables postponed
  evaluation of annotations.
- PEP 604 `X | None` — technically works but NOT yet detected by the
  Ollama schema builder. Use `Optional[X]` from `typing` for public
  function signatures that the schema builder reads.

## What is forbidden in runtime

- PEP 695 type aliases (`type X = ...`) in `02_Technical/src/` — the
  B4 test fails the build.
- `default=str` in `json.dumps` — breaks determinism (see the
  `determinism-and-canonical-json` skill).
- `import random`, `time.time()`, `datetime.utcnow()` — breaks
  determinism.

## The runtime is pure stdlib

The 10 third-party packages in `02_Technical/requirements.txt` are
pure-Python and vendorable. No C extensions, no network libs. The
runtime has zero network dependencies.

## The rule

4 spaces, snake_case, type hints, no PEP 695, no randomness. The B4
test and the boundary test enforce these. A style violation that
passes the tests is still a style violation — fix it.