# Ollama timeout disaster -- operational note

## Incident

During the ClineCLI build sessions, the local Ollama server repeatedly
threw timeout warnings. Those timeouts disconnected ClineCLI from the
project, breaking the operator's workflow even though the deterministic
engine underneath was unaffected.

## Root cause

ClineCLI treated the local Ollama model as a required dependency for
tool-calling. When Ollama hung or timed out, the entire assistant
surface failed. The engine itself (Python stdlib, no network) kept
working, but the operator could no longer reach it through Cline.

## Why this cannot happen in Order Get It Right

The deterministic audit engine in `02_Technical/src/` has **no Ollama
dependency**:

- `src/engines/` -- no Ollama imports, no network calls.
- `src/server/` -- no Ollama imports; the FastAPI runtime is pure Python.
- `src/agents/orchestrator.py` -- deterministic hand-off chain, no LLM.
- `src/agents/audit_review_agent.py` -- uses "ollama" only as a keyword
  marker in third-party-assistant detection, not as a runtime.

Ollama appears only in `02_Technical/tools/agentic_repl.py`, which is
an **optional operator convenience** -- a natural-language chat shell
that calls the already-running FastAPI server. If Ollama is down, the
engine continues to work through:

- the web UI (`web/index.html` served by FastAPI)
- the CLI (`python -m src.audit_cli`)
- the Tauri desktop binary
- direct HTTP API calls

## Contract

1. The engine must never require Ollama to produce a verdict.
2. Ollama-dependent code must live only under `02_Technical/tools/`.
3. Any test that requires Ollama must be skip-guarded, not a hard gate.
4. The agentic REPL must warn on Ollama unreachability and degrade,
   not crash the operator's session.

## Mitigations already in place

- `agentic_repl.py` reaches Ollama over stdlib `urllib.request`, not a
  third-party package.
- It checks `/api/tags` at startup and prints a warning if Ollama is
  unreachable.
- Tool calls return `{"_error": ...}` when Ollama fails; the REPL keeps
  running.
- `tests/test_d5_agentic_repl.py` skips the end-to-end test when the
  FastAPI server or Ollama is unavailable.

## Operator action if Ollama misbehaves

1. Do not restart the audit workflow. The engine is independent.
2. Use the web UI, CLI, or Tauri binary instead of the agentic REPL.
3. If Ollama is needed for the REPL, run `ollama serve` in a separate
   terminal and confirm `http://localhost:11434/api/tags` responds.
4. If timeouts persist, stop using the REPL until Ollama is stable;
   the deterministic engine does not need it.

## Sealed

This note is a project-level contract. Any future change that moves
Ollama into the runtime path must be rejected or require a deliberate
architecture decision recorded in the chain.
