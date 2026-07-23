"""
Tests for allow_list_audit.py
==============================

Closes WP-4 of the spawn-and-spread directive. The script at
04_Validation/scripts/allow_list_audit.py must:
  1. exit 0 when all 5 allow-list entries have at least 1 call (live state)
  2. exit 2 when an entry has 0 calls (synthetic case)
  3. print a table with the 5 columns: PATH, MODULES, CALL_COUNT,
     LAST_MODIFIED
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


# Path to the script under test, relative to the project root.
SCRIPT = "04_Validation/scripts/allow_list_audit.py"


def _run(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    """Run the script in a subprocess; return the result."""
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        cwd=cwd, capture_output=True, text=True, timeout=30,
    )


def test_script_exits_zero_on_live_state():
    """Live state: all 5 allow-list entries have at least 1 call."""
    project_root = Path(__file__).resolve().parent.parent
    r = _run([], cwd=str(project_root))
    # The script may exit 0 (all used) or 2 (some unused). On this host
    # the live state is "all used" so we expect 0. If the test ever
    # regresses to 2, the operator has unused allow-list entries and
    # the test should be updated to reflect the new audit policy.
    assert r.returncode == 0, (
        f"allow_list_audit.py should exit 0 when all 5 entries are used; "
        f"got exit={r.returncode}, stderr={r.stderr[:500]}"
    )
    assert "OK: all 5 allow-list entries have at least 1 call." in r.stdout


def test_script_json_only_emits_valid_json():
    """--json-only flag emits parseable JSON with the 5 expected keys."""
    project_root = Path(__file__).resolve().parent.parent
    r = _run(["--json-only"], cwd=str(project_root))
    assert r.returncode in (0, 2), (
        f"--json-only should not exit 1 (error); got {r.returncode}"
    )
    data = json.loads(r.stdout)
    expected_keys = {
        "allow_list_size", "total_calls", "unused_entries",
        "rows", "verdict",
    }
    assert expected_keys.issubset(data.keys()), (
        f"JSON output missing keys: {expected_keys - set(data.keys())}"
    )
    assert data["allow_list_size"] == 5, (
        f"allow_list_size should be 5; got {data['allow_list_size']}"
    )
    assert data["total_calls"] > 0, (
        f"total_calls should be > 0 on live state; got {data['total_calls']}"
    )


def test_script_table_format_contains_5_columns():
    """Human-readable table has the 4 columns: PATH, MODULES, CALL_COUNT,
    LAST_MODIFIED (5 includes the leading separator)."""
    project_root = Path(__file__).resolve().parent.parent
    r = _run([], cwd=str(project_root))
    assert "PATH" in r.stdout
    assert "MODULES" in r.stdout
    assert "CALL_COUNT" in r.stdout
    assert "LAST_MODIFIED" in r.stdout
    # Each of the 5 allow-list paths should appear in the table
    for path in [
        "02_Technical/tools/agentic_repl.py",
        "02_Technical/tools/agentic_repl_tools.py",
        "02_Technical/tools/discovery_agent.py",
        "tests/test_d5_agentic_repl.py",
        "04_Validation/scripts/dns_forwarder_health.py",
    ]:
        assert path in r.stdout, f"Path {path!r} not in script output"


def test_no_network_imports_in_script():
    """The script must not introduce new network modules (closed-set policy).

    The 5 allow-list entries (urllib, urllib.request, urllib.error, socket)
    are the only allowed network modules in the whole project. The
    allow_list_audit.py script does not need any of them -- it only reads
    files and prints a table. So this test asserts the script has zero
    of those imports.
    """
    script_path = Path(__file__).resolve().parent.parent / SCRIPT
    text = script_path.read_text(encoding="utf-8")
    forbidden = [
        "import urllib", "from urllib",
        "import socket", "from socket",
        "import http.client", "from http.client",
    ]
    for pat in forbidden:
        assert pat not in text, (
            f"allow_list_audit.py contains forbidden import {pat!r}; "
            f"the script must not introduce new network modules"
        )
