"""
Order Get It Right -- Agentic REPL.

The agentic REPL wires the five unconnected agents (Tauri shell,
third_party_assistant.py, discovery_agent, monitor_agent,
InventoryAgent) into a single user-facing flow by giving a local
LLM (Ollama) the tool functions in agentic_repl_tools.py and
looping on its tool_calls.

Architecture:
  * This file lives in 02_Technical/tools/ alongside
    discovery_agent.py -- BOTH are operator CLI tools, NOT part of
    the audit runtime. The no-network audit on 02_Technical/src/
    is unaffected.
  * The tool functions (in agentic_repl_tools.py) call the FastAPI
    runtime at http://127.0.0.1:3000 over HTTP. The agentic REPL
    does NOT import from src/engines or src/agents directly -- the
    same boundary rule tests/ follows. The agentic REPL is a
    normal HTTP client of the audit pipeline.
  * Ollama is reached over stdlib urllib.request -- the project is
    stdlib-only (no `ollama` Python package, no `requests`). On
    this host (2026-07-17): `qwen3.5:9b` (default, confirmed
    tool-calling) and `llama3.1:8b` (also tool-capable). The
    earlier default `tcoxav/aegis:latest` (1.5B Qwen2) was
    confirmed tool-capable on a prior host but is not currently
    loaded.
  * The chat loop follows Ollama's reference pattern
    (https://ollama.com/blog/tool-support): POST /api/chat with
    messages+tools; if the response has tool_calls, send each
    result back as a {role: "tool"} message and POST again; loop
    until the model returns a plain assistant message with no
    tool_calls.

Usage:
  # from the project root
  python -m tools.agentic_repl
  python -m tools.agentic_repl --model qwen3.5:9b
  python -m tools.agentic_repl --prompt "is the chain intact?"

This file is closed in OPEN_ITEMS_AND_REFERENCE.md item D5
("Order Get It Right as a product, not a sequence of CLI
invocations").
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

# Force stdout to UTF-8 so model output containing non-cp1252
# characters (e.g. U+2713 check mark from qwen3.5) does not crash
# the REPL on Windows consoles. On POSIX UTF-8 locales this is a
# no-op. See agentic_repl end-to-end test for the regression.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

# Local sibling -- the tool function definitions.
# This is an intra-tools/ import, not a cross-runtime import.
from tools import agentic_repl_tools as _tools


# ---------------------------------------------------------------------------
# Ollama HTTP helper -- one place to handle timeouts and errors
# ---------------------------------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OGIR_AGENT_MODEL", "qwen3.5:9b")
# Default tool-calling model. Probed and confirmed on 2026-07-17:
# qwen3.5:9b returns structured tool_calls for the OGIR tool
# schema. llama3.1:8b also supports tool calling in general but
# qwen3.5 produces cleaner JSON. The earlier default tcoxav/aegis
# is a 1.5B Qwen2 model that was confirmed tool-capable on a
# previous host but is not currently loaded.

# Default tool-calling model advertised in the help text -- the
# operator can override with --model. The agent will warn (not
# fail) if Ollama is unreachable.
SYSTEM_PROMPT = """You are the Order Get It Right agent -- a local, air-gapped
assistant for Justin Barnett's Order Get It Right audit pipeline.

You have nine tools, all of which call the local FastAPI audit server at
http://127.0.0.1:3000. Use them to answer the operator's questions
about:
  * the 54-pattern deception scan (audit_text, list_ontology)
  * the 8-case evaluation suite (evaluate_suite)
  * the Merkle truth ledger (verify_chain, seal_custom_event, add_fact,
    list_facts)
  * the full orchestrator agent chain (orchestrator_process)
  * the system status (get_status)

Be concise. When you run a tool, briefly state the result. When you
seal a fact or event, confirm what you sealed. Never invent Merkle
roots or block numbers -- the tools return them from the chain.
"""


def _ollama_chat(model: str, messages: List[Dict[str, Any]],
                 tools: List[Dict[str, Any]],
                 timeout: int = 60) -> Dict[str, Any]:
    """POST one turn to Ollama. Returns the full response dict so
    the caller can decide whether to dispatch tool_calls or stop.

    If Ollama is unreachable, returns a {_error: ...} dict. The
    caller (the REPL loop) decides whether to retry, warn, or bail.
    """
    url = f"{OLLAMA_URL}/api/chat"
    body: Dict[str, Any] = {"model": model, "messages": messages, "stream": False}
    if tools:
        body["tools"] = tools
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.URLError as e:
        return {"_error": f"Ollama unreachable at {url}: {e}"}
    except urllib.error.HTTPError as e:
        return {"_error": f"Ollama HTTP {e.code} on {url}: {e.reason}"}
    except json.JSONDecodeError as e:
        return {"_error": f"Ollama returned non-JSON: {e}"}


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------
def _dispatch_tool_calls(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Given an Ollama response, execute every tool_call it returned
    and produce the {role: "tool"} messages Ollama expects next.

    Ollama returns tool_calls as a list (not always one element).
    Some models return parallel tool_calls; we honour all of them
    in a single round trip.

    The tool function's output is already a JSON string (per
    agentic_repl_tools.py); we pass it through as `content` to
    Ollama. If the function is unknown, we return an _error
    string in the tool result so the model can recover.
    """
    tool_messages: List[Dict[str, Any]] = []
    for call in response.get("message", {}).get("tool_calls", []) or []:
        fn = call.get("function", {}) or {}
        name = fn.get("name", "")
        # Ollama sends arguments as either a dict or a JSON string,
        # depending on the model. Normalise to a dict.
        args = fn.get("arguments", {}) or {}
        if isinstance(args, str):
            try:
                args = json.loads(args) if args.strip() else {}
            except json.JSONDecodeError:
                args = {"_raw": args}
        func = _tools.TOOL_FUNCTIONS.get(name)
        if func is None:
            content = json.dumps({"_error": f"unknown tool: {name}"})
        else:
            try:
                content = func(**args) if isinstance(args, dict) else func(args)
            except TypeError as e:
                content = json.dumps({"_error": f"bad arguments for {name}: {e}"})
            except Exception as e:  # noqa: BLE001 -- we want all errors
                content = json.dumps({"_error": f"{name} raised: {e}"})
        tool_messages.append({
            "role": "tool",
            "name": name,
            "content": content,
        })
    return tool_messages


# ---------------------------------------------------------------------------
# One full turn -- model thinks, may call tools, may answer
# ---------------------------------------------------------------------------
def _one_turn(model: str, messages: List[Dict[str, Any]],
              tools: List[Dict[str, Any]],
              max_tool_rounds: int = 6) -> Dict[str, Any]:
    """Run one user turn end-to-end: keep dispatching tool_calls
    until the model returns a final message (no tool_calls) or we
    hit max_tool_rounds (prevents runaway loops on a stubborn
    model).

    Returns the final assistant message dict. The caller is
    responsible for printing it.
    """
    for _ in range(max_tool_rounds):
        r = _ollama_chat(model, messages, tools)
        if "_error" in r:
            return {"role": "assistant", "content": r["_error"]}
        msg = r.get("message", {}) or {}
        # If the model wants to call tools, dispatch and loop.
        if msg.get("tool_calls"):
            # Push the model's tool_calls message onto history so
            # Ollama sees its own reasoning on the next turn.
            messages.append(msg)
            tool_results = _dispatch_tool_calls(r)
            messages.extend(tool_results)
            continue
        # No tool_calls -- this is the final answer. Append to
        # history (so the next user turn has context) and return.
        messages.append(msg)
        return msg
    # Hit the cap; tell the user.
    return {
        "role": "assistant",
        "content": f"(stopped after {max_tool_rounds} tool rounds -- model would not produce a final answer)",
    }


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------
BANNER = f"""
================================================================================
  Order Get It Right -- Agentic REPL
  Ollama: {OLLAMA_URL}
  Model:  {{model}}
  Tools:  9 (audit, eval, verify, facts, seal, status, ontology, orchestrator, ...)
  Audit:  calls http://127.0.0.1:3000 -- the FastAPI audit server
  Air-gapped: the runtime makes no outbound network calls.
================================================================================
Type a question, 'quit' to exit.
"""


def _format_assistant(msg: Dict[str, Any]) -> str:
    """Print the assistant's reply. Strip empty content (the model
    sometimes returns a content='' alongside tool_calls, which
    would print a blank line for no reason). Re-encode through
    UTF-8 with replacement so non-cp1252 glyphs (e.g. the
    U+2713 check mark returned by qwen3.5) do not crash the
    REPL on legacy Windows consoles."""
    content = (msg.get("content") or "").strip()
    if not content:
        return "(no text response)"
    return content.encode("utf-8", errors="replace").decode("utf-8", errors="replace")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Order Get It Right agentic REPL (Ollama tool calling)",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Ollama model tag (default: {DEFAULT_MODEL}). Must support tool calling.",
    )
    parser.add_argument(
        "--prompt", default=None,
        help="Run a single prompt and exit (non-interactive). Useful for scripts.",
    )
    parser.add_argument(
        "--max-rounds", type=int, default=6,
        help="Max tool-call rounds per turn (default 6). Prevents runaway loops.",
    )
    args = parser.parse_args(argv)

    print(BANNER.format(model=args.model))

    # Up-front Ollama reachability check. If Ollama is down, tell
    # the operator -- don't silently fail later in the loop.
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as r:
            if r.status != 200:
                print(f"WARNING: Ollama returned HTTP {r.status} on /api/tags")
    except (urllib.error.URLError, OSError) as e:
        print(f"WARNING: Ollama unreachable at {OLLAMA_URL}: {e}")
        print("  Start Ollama with: ollama serve")
        print("  The REPL will still start; tool calls will fail until Ollama is up.")
        print()

    tools_schema = _tools.TOOLS
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if args.prompt is not None:
        # Non-interactive mode -- one prompt, one answer, exit.
        messages.append({"role": "user", "content": args.prompt})
        msg = _one_turn(args.model, messages, tools_schema, args.max_rounds)
        print(f"\n> {args.prompt}\n")
        print(_format_assistant(msg))
        return 0

    # Interactive REPL.
    while True:
        try:
            line = input("\nagent> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[agentic repl exiting]")
            return 0
        if not line:
            continue
        if line.lower() in ("quit", "exit"):
            print("[agentic repl exiting]")
            return 0
        messages.append({"role": "user", "content": line})
        t0 = time.time()
        msg = _one_turn(args.model, messages, tools_schema, args.max_rounds)
        dt = time.time() - t0
        print(f"\n{_format_assistant(msg)}\n  [{dt:.1f}s]")


if __name__ == "__main__":
    sys.exit(main())
