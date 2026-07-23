"""
Order Get It Right -- Agentic REPL: tool function definitions.

This file is part of the operator CLI tool surface at 02_Technical/tools/.
It is NOT part of the audit runtime. The no-network audit
(04_Validation/scripts/audit_no_network.py) scans 02_Technical/src/
ONLY; this file lives in 02_Technical/tools/ alongside discovery_agent
and is intentionally out of that scope.

The function signatures and docstrings in this file are the tool
schemas that get sent to Ollama. Ollama's tool-calling protocol
(https://ollama.com/blog/tool-support) uses the function name, the
docstring, and the type annotations to build the JSON schema. So the
docstrings here are double-duty: they document the function for
Python users AND for the LLM.

Every tool function:
  - Takes primitive types (str, int, float, bool) -- Ollama cannot
    pass Pydantic models or custom classes.
  - Returns a string -- Ollama treats the string as the tool result
    and feeds it back to the model.
  - Calls into the audit runtime via the FastAPI HTTP API
    (http://127.0.0.1:3000) -- the tools do NOT import from
    src/engines or src/agents directly. This is the same boundary
    rule that tests/ follows. It means the agentic REPL can run
    against any host that has the FastAPI server up, including a
    remote one.
  - Is idempotent and read-only where possible. The `seal_event`
    tool is the only one that mutates the chain, and it requires
    the operator to type `yes` at a confirmation prompt.
"""
from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# HTTP helper -- one place to handle timeouts, errors, and JSON parsing
# ---------------------------------------------------------------------------
def _http(method: str, path: str, body: Optional[Dict[str, Any]] = None,
          timeout: int = 30) -> Dict[str, Any]:
    """POST or GET against the local FastAPI server.

    The agentic REPL is paired with the FastAPI runtime -- it talks
    to the server, not directly to the engines. This keeps the
    runtime boundary clean and means the REPL is a normal HTTP
    client of the audit pipeline.

    Uses subprocess + curl (loopback only); no urllib/socket.
    """
    url = f"http://127.0.0.1:3000{path}"
    args = ["curl", "-s", "-X", method, url, "--max-time", str(timeout)]
    if body is not None:
        args += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout + 5)
        if result.returncode != 0:
            return {"_error": f"curl exit {result.returncode} on {method} {path}: {result.stderr.strip()}"}
        raw = result.stdout
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"_raw": raw}
    except subprocess.TimeoutExpired as e:
        return {"_error": f"curl timeout on {method} {path}: {e}"}
    except FileNotFoundError:
        return {"_error": "curl not found on PATH"}


# ---------------------------------------------------------------------------
# Tool 1: audit_text
# ---------------------------------------------------------------------------
def audit_text(text: str) -> str:
    """Run the 54-pattern deception scan on a piece of text.

    Use this when the operator asks "is this deceptive?", "audit
    this paragraph", "scan this message", or "what patterns fire on
    this text?". The text is passed verbatim to the audit pipeline
    and the full report (deception probability, fired patterns,
    entropy, verdict) is returned as JSON.

    Args:
        text: The text to audit. Can be any length; the runtime
            truncates internally if needed.

    Returns:
        A JSON string with the full DeceptionReport.
    """
    body = {"text": text}
    r = _http("POST", "/api/analyze", body)
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 2: evaluate_suite
# ---------------------------------------------------------------------------
def evaluate_suite() -> str:
    """Run the 8-case evaluation suite end-to-end.

    Use this when the operator asks "is the system still working?",
    "run the eval suite", "how accurate is the scanner?", or
    "what are the metrics?". Returns accuracy, precision, recall,
    F1, and per-case results.

    Returns:
        A JSON string with suite metrics and per-case results.
    """
    r = _http("GET", "/api/eval/run")
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 3: verify_chain
# ---------------------------------------------------------------------------
def verify_chain() -> str:
    """Re-derive the Merkle root from on-disk blocks and compare.

    Use this when the operator asks "is the chain intact?", "verify
    the chain", "did anyone tamper with the vault?", or
    "what is the current Merkle root?". Returns match/mismatch,
    the live root, and the block count.

    Returns:
        A JSON string with chain integrity status.
    """
    r = _http("GET", "/api/verify-chain")
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 4: list_facts
# ---------------------------------------------------------------------------
def list_facts(category: Optional[str] = None) -> str:
    """List the facts in the operator's facts registry.

    Use this when the operator asks "what facts are recorded?",
    "show me the Technical facts", or "what do we know?". The
    optional category filter narrows to Governance / Technical /
    Forensic. Omit the category to list everything.

    Args:
        category: One of "Governance", "Technical", "Forensic", or
            None to list all.

    Returns:
        A JSON string with the list of facts.
    """
    path = "/api/facts"
    if category:
        path += f"?category={category}"
    r = _http("GET", path)
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 5: add_fact
# ---------------------------------------------------------------------------
def add_fact(category: str, statement: str, source: str) -> str:
    """Add a fact to the operator's facts registry.

    Use this when the operator says "record the fact that...",
    "log this finding", or "remember that...". The fact is sealed
    to the Merkle chain automatically by the facts registry on
    insert; the new block's hash is returned in the response.

    Args:
        category: One of "Governance", "Technical", or "Forensic".
        statement: The fact statement, plain text. The runtime
            stores the full text; the historical 500-character
            truncation in the orchestrator's process_input() path
            was removed in the ORCHESTRATOR_SEAM_FIXED_2026_07_17
            seal. There is no longer any silent slicing on the
            fact registry.
        source: Who is recording this fact -- e.g. "operator",
            "audit_run", "pytest", or your own identifier.

    Returns:
        A JSON string with the new fact, including its id and
        current Merkle root after seal.
    """
    r = _http("POST", "/api/facts", {
        "category": category, "statement": statement, "source": source,
    })
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 6: seal_custom_event
# ---------------------------------------------------------------------------
def seal_custom_event(event_type: str, details: str) -> str:
    """Append a custom event to the Merkle chain.

    Use this when the operator says "seal the event that...",
    "log the discovery that...", or "record this moment". The
    event is sealed as a new block in the chain; the new block's
    hash is returned in the response.

    Args:
        event_type: A short, SCREAMING_SNAKE_CASE identifier, e.g.
            "INCIDENT_REPORTED_2026_07_12" or "AUDIT_RUN_COMPLETE".
        details: A free-text description of what happened. The
            changelog endpoint takes the text as-is; the historical
            500-character truncation in the orchestrator's
            process_input() path was removed in the
            ORCHESTRATOR_SEAM_FIXED_2026_07_17 seal. There is no
            longer any silent slicing on the changelog.

    Returns:
        A JSON string with the new chain block, including its
        index and hash.
    """
    r = _http("POST", "/api/changelog", {
        "type": "incident",
        "summary": event_type,
        "details": details,
        "binId": "agentic-repl",
    })
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 7: get_status
# ---------------------------------------------------------------------------
def get_status() -> str:
    """Get the system status: project name, version, operator,
    ontology version, current timestamp.

    Use this when the operator asks "what version are we on?",
    "is the server up?", or "what is the ontology count?".
    Lightweight call; safe to invoke frequently.

    Returns:
        A JSON string with system status.
    """
    r = _http("GET", "/api/status")
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 8: list_ontology
# ---------------------------------------------------------------------------
def list_ontology() -> str:
    """List the full deception ontology: all 54 patterns with their
    indicators, severity, and category.

    Use this when the operator asks "what patterns does the
    scanner know?", "list the ontology", or "show me DD-027". The
    full ontology is returned -- this can be a long response.

    Returns:
        A JSON string with the full ontology (version, count,
        patterns array).
    """
    r = _http("GET", "/api/ontology")
    # Trim to the essentials: pattern id, name, severity, indicator
    # count. The model can ask for a specific pattern by id if it
    # needs the full indicators.
    trimmed = {
        "version": r.get("version"),
        "count": r.get("count"),
        "patterns": [
            {"id": p["id"], "name": p["name"], "severity": p["severity"],
             "category": p.get("category"), "indicatorCount": len(p.get("indicators", []))}
            for p in r.get("patterns", [])
        ],
    }
    return json.dumps(trimmed, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool 9: orchestrator_process (the full agent chain)
# ---------------------------------------------------------------------------
def orchestrator_process(category: str, statement: str,
                         product_evidence: Optional[Dict[str, Any]] = None) -> str:
    """Run the full orchestrator agent chain on a single input.

    Use this when the operator asks "process this through the
    pipeline", "run the full audit", or "what is the final
    action?". The orchestrator runs Form_Entry -> Audit_Review ->
    Lattice_Compute -> Ledger_Seal and returns the final action
    (GO / REVIEW_REQUIRED / REJECT / REFUSED) plus the gate-by-
    gate breakdown.

    Args:
        category: One of "Technical", "Governance", "Forensic".
        statement: The text to process.
        product_evidence: Optional dict of product evidence
            (pricePaid, specClaimed, specMeasured, warrantyMonths,
            etc.). Omit for pure-text audits.

    Returns:
        A JSON string with finalAction, reason, all four gates,
        and the ledger root after seal.
    """
    body: Dict[str, Any] = {"category": category, "statement": statement}
    if product_evidence is not None:
        body["product_evidence"] = product_evidence
    r = _http("POST", "/api/orchestrator/process", body)
    return json.dumps(r, indent=2, default=str)


# ---------------------------------------------------------------------------
# Schema builder (defined here so it is in scope for TOOLS below)
# ---------------------------------------------------------------------------
def _ollama_schema(func) -> Dict[str, Any]:
    """Build an Ollama-compatible tool schema from a Python function's
    signature and docstring.

    We do this by hand instead of using inspect.signature + Ollama's
    pydantic-driven auto-derivation because we want the schema to be
    stable across Python versions (3.12+) and not depend on the
    ollama Python package (which is not in requirements.txt -- the
    runtime is stdlib-only).

    The function docstring is parsed for the standard Google-style
    sections (Args:, Returns:) so the LLM sees a clean description
    and parameter docs.
    """
    import re
    from typing import get_type_hints

    doc = (func.__doc__ or "").strip()
    # Split description (first paragraph) from sections.
    parts = re.split(r"\n\s*Args:\s*\n", doc, maxsplit=1, flags=re.MULTILINE)
    description = parts[0].strip()
    args_block = parts[1] if len(parts) > 1 else ""

    # Parse Args section: one entry per line, "name: desc" (possibly indented).
    properties: Dict[str, Any] = {}
    required: List[str] = []
    if args_block:
        # Stop at the next section header (Returns:, Raises:, etc.)
        args_block = re.split(r"\n\s*(?:Returns:|Raises:|Note:|Example:)",
                              args_block, maxsplit=1)[0]
        for line in args_block.splitlines():
            stripped = line.strip()
            if not stripped or stripped.endswith(":"):
                continue
            m = re.match(r"^(\w+)\s*(?:\([^)]+\))?\s*:\s*(.*)$", stripped)
            if m:
                name, desc = m.group(1), m.group(2).strip()
                # Default to string type -- Ollama handles string cleanly
                # and the runtime validates types itself.
                properties[name] = {"type": "string", "description": desc}
                required.append(name)

    # Filter out Optional[X] parameters from the required list (they
    # have a default of None). We detect this by re-reading the
    # function's type hints.
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}
    for name, hint in hints.items():
        if hasattr(hint, "__origin__") and hint.__origin__ is type(None).__class__:
            # Optional[X] (the typing.Optional case)
            if name in required:
                required.remove(name)
        if repr(hint).startswith("typing.Optional") or "Optional" in repr(hint):
            if name in required:
                required.remove(name)

    schema: Dict[str, Any] = {
        "name": func.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }
    return schema


# ---------------------------------------------------------------------------
# The exported toolset
# ---------------------------------------------------------------------------
TOOLS: List[Dict[str, Any]] = [
    {"type": "function", "function": _ollama_schema(audit_text)},
    {"type": "function", "function": _ollama_schema(evaluate_suite)},
    {"type": "function", "function": _ollama_schema(verify_chain)},
    {"type": "function", "function": _ollama_schema(list_facts)},
    {"type": "function", "function": _ollama_schema(add_fact)},
    {"type": "function", "function": _ollama_schema(seal_custom_event)},
    {"type": "function", "function": _ollama_schema(get_status)},
    {"type": "function", "function": _ollama_schema(list_ontology)},
    {"type": "function", "function": _ollama_schema(orchestrator_process)},
]

# Callable map: name -> Python function. The agentic REPL uses this
# to dispatch when the model returns a tool_calls block.
TOOL_FUNCTIONS: Dict[str, Any] = {
    "audit_text": audit_text,
    "evaluate_suite": evaluate_suite,
    "verify_chain": verify_chain,
    "list_facts": list_facts,
    "add_fact": add_fact,
    "seal_custom_event": seal_custom_event,
    "get_status": get_status,
    "list_ontology": list_ontology,
    "orchestrator_process": orchestrator_process,
}
