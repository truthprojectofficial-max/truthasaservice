"""Order Get It Right -- operator CLI tools (out-of-runtime).

Modules in this package are operator-facing CLI tools, not parts
of the audit runtime. The no-network audit
(04_Validation/scripts/audit_no_network.py) scans
02_Technical/src/ ONLY; this directory is intentionally out of
that scope.

Modules:
  * discovery_agent    -- network/DNS reconnaissance for the
                          operator's environment
  * agentic_repl       -- Ollama-backed agent loop calling the
                          FastAPI audit server
  * agentic_repl_tools -- tool function definitions sent to
                          Ollama
"""
