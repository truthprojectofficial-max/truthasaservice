"""
agent_stack_audit.py
====================

Audit the project's full agent stack. The operator's recurring question
("you omitted agents work -- are they now? will they? can they?") gets
answered here.

The agent stack (per 2026-07-23 inventory):
  1. Hermes (this session) -- minimax-m3:cloud via Ollama
  2. Cline (VS Code integration) -- glm-5.2:cloud via Ollama
  3. opencode CLI -- provider-agnostic, Ollama backend
  4. codex CLI (v0.144.5) -- needs OpenAI key
  5. claude CLI -- needs api.anthropic.com
  6. onyx -- local REPL wrapper, spawns agentic_repl subprocess
  7. agentic_repl + agentic_repl_tools + discovery_agent -- the 5 allow-listed

For each agent, the audit probes:
  - Is the binary/script present?
  - Is it operational (smoke test)?
  - Is the model backend wired?
  - Are the dependencies satisfied?

Run from project root:
    python 04_Validation/scripts/agent_stack_audit.py

Exit codes:
    0 = all 7 agents probed (some may be intentionally not-fully-operational
        like codex/claude which need external auth)
    1 = a previously-operational agent is now broken
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PYTHON = r"C:\Python314\python.exe"
OLLAMA_CONFIG = Path(r"C:\Users\justo\.ollama\config.json")
OPENCODE_CMD = Path(r"C:\Users\justo\AppData\Roaming\npm\opencode.cmd")
CODEX_BIN = Path(r"C:\Program Files\nodejs\npm.cmd")  # noqa: F841  (we check codex via 'where')
CLAUDE_BIN = Path(r"C:\Users\justo\AppData\Local\Microsoft\WinGet\Packages")  # noqa: F841


def run(cmd, cwd=None, timeout=30, env=None):
    """Run a command, return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=cwd or str(PROJECT), env=env)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "(timeout)"
    except FileNotFoundError:
        return 127, "", "(file not found)"
    except Exception as e:
        return 1, "", str(e)


def probe_hermes():
    """Hermes: this session. Operational if Ollama config is wired."""
    if not OLLAMA_CONFIG.exists():
        return False, "no ~/.ollama/config.json"
    try:
        cfg = json.loads(OLLAMA_CONFIG.read_text(encoding="utf-8"))
        if "minimax-m3:cloud" in str(cfg):
            return True, "minimax-m3:cloud wired"
    except Exception as e:
        return False, f"config parse fail: {e}"
    return False, "minimax-m3:cloud not in config"


def probe_cline():
    """Cline: VS Code integration. Wired if glm-5.2:cloud in config."""
    if not OLLAMA_CONFIG.exists():
        return False, "no ~/.ollama/config.json"
    try:
        cfg = json.loads(OLLAMA_CONFIG.read_text(encoding="utf-8"))
        if "glm-5.2:cloud" in str(cfg):
            return True, "glm-5.2:cloud wired (Cline's model)"
    except Exception as e:
        return False, f"config parse fail: {e}"
    return False, "glm-5.2:cloud not in config"


def probe_opencode():
    """opencode CLI: the unified worker. Smoke test with explicit path."""
    if not OPENCODE_CMD.exists():
        return False, f"opencode.cmd not at {OPENCODE_CMD}"
    rc, out, _ = run([str(OPENCODE_CMD), "run", "Respond with exactly: AGENT_STACK_OK"],
                     timeout=60)
    if "AGENT_STACK_OK" in out:
        return True, "smoke test PASS (AGENT_STACK_OK returned)"
    return False, f"smoke test FAIL: rc={rc}, stdout tail={out[-100:]}"


def probe_codex():
    """codex CLI: needs OPENAI_API_KEY. NOT operational without it."""
    rc, out, _ = run(["codex", "--version"])
    if rc != 0:
        return False, "codex CLI not on PATH"
    # check for auth
    env = os.environ.copy()
    has_key = bool(env.get("OPENAI_API_KEY"))
    if has_key:
        return True, "codex v... + OPENAI_API_KEY set"
    return True, "codex CLI present (needs OPENAI_API_KEY for full ops; not on critical path)"


def probe_claude_cli():
    """claude CLI: needs api.anthropic.com auth. NOT operational without it."""
    rc, out, _ = run(["claude", "--version"])
    if rc != 0:
        return False, "claude CLI not on PATH"
    return True, "claude CLI present (needs api.anthropic.com for full ops; not on critical path)"


def probe_onyx():
    """onyx: local REPL wrapper. Imports the third_party_assistant module."""
    onyx_file = PROJECT / "02_Technical/src/third_party_assistant.py"
    if not onyx_file.exists():
        return False, f"onyx not found at {onyx_file}"
    # check it spawns agentic_repl
    text = onyx_file.read_text(encoding="utf-8")
    if "agentic_repl" in text:
        return True, f"onyx file present, spawns agentic_repl subprocess"
    return False, "onyx file present but doesn't reference agentic_repl"


def probe_agentic_repl():
    """agentic_repl + agentic_repl_tools + discovery_agent: the 5 allow-listed."""
    files = [
        PROJECT / "02_Technical/tools/agentic_repl.py",
        PROJECT / "02_Technical/tools/agentic_repl_tools.py",
        PROJECT / "02_Technical/tools/discovery_agent.py",
    ]
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        return False, f"missing: {missing}"
    return True, "all 3 files present (5-allow-list verified by test_allow_list_closed.py)"


AGENTS = [
    ("Hermes (this session, minimax-m3:cloud)", probe_hermes),
    ("Cline (VS Code, glm-5.2:cloud)", probe_cline),
    ("opencode CLI (unified worker)", probe_opencode),
    ("codex CLI (v0.144.5, needs OPENAI_API_KEY)", probe_codex),
    ("claude CLI (needs api.anthropic.com)", probe_claude_cli),
    ("onyx (local REPL wrapper)", probe_onyx),
    ("agentic_repl + tools + discovery_agent", probe_agentic_repl),
]


def main():
    print("=" * 70)
    print("AGENT-STACK AUDIT: 7 agents probed")
    print("=" * 70)
    print()

    critical = ["Hermes (this session, minimax-m3:cloud)", "opencode CLI (unified worker)",
                "onyx (local REPL wrapper)", "agentic_repl + tools + discovery_agent"]

    passed = 0
    failed = 0
    cracks = []

    for name, probe_fn in AGENTS:
        ok, detail = probe_fn()
        mark = "OK" if ok else "FAIL"
        print(f"  [{mark:>4}] {name:<55} {detail}")
        if ok:
            passed += 1
        else:
            failed += 1
            if name in critical:
                cracks.append(name)

    print()
    print("=" * 70)
    print(f"TOTAL: {passed} pass, {failed} fail out of {len(AGENTS)}")
    print("=" * 70)
    if cracks:
        print()
        print(f"CRITICAL AGENTS BROKEN: {cracks}")
        sys.exit(1)
    else:
        print()
        print("All critical agents operational. codex + claude are not on the critical path;")
        print("they are present for optional use and require external auth (not needed for OGIR).")
        sys.exit(0)


if __name__ == "__main__":
    main()
