"""
test_no_network_modules_anywhere.py
====================================

The post-rewrite test: verify that NO file in the 5-allow-list (now removed)
still uses urllib/socket/http.client. The test is a hard-fail for any
network import in any of the 5 files.

This is the GREEN-gate for step 1 of the 4-step fix path.
"""
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]

# The 5 files that must not use urllib/socket/http.client
FORBIDDEN_FILES = [
    "02_Technical/tools/agentic_repl.py",
    "02_Technical/tools/agentic_repl_tools.py",
    "02_Technical/tools/discovery_agent.py",
    "04_Validation/scripts/dns_forwarder_health.py",
    "tests/test_d5_agentic_repl.py",
]

# The forbidden network modules (any of these in the file = fail)
FORBIDDEN_MODULES = ["urllib", "urllib.request", "urllib.error", "socket", "http.client"]


def _has_network_module(text: str) -> list[str]:
    """Return list of forbidden module names found in the text."""
    found = []
    for m in FORBIDDEN_MODULES:
        # match "import X" or "from X import ..."
        if re.search(rf"^\s*(from|import)\s+{re.escape(m)}\b", text, re.MULTILINE):
            found.append(m)
    return found


def test_no_forbidden_file_uses_urllib():
    """The 5 files must not use urllib. None of them."""
    for f in FORBIDDEN_FILES:
        text = (PROJECT / f).read_text(encoding="utf-8")
        found = _has_network_module(text)
        assert "urllib" not in found and "urllib.request" not in found and "urllib.error" not in found, (
            f"{f} still uses urllib: {found}"
        )


def test_no_forbidden_file_uses_socket():
    """The 5 files must not use socket. None of them."""
    for f in FORBIDDEN_FILES:
        text = (PROJECT / f).read_text(encoding="utf-8")
        found = _has_network_module(text)
        assert "socket" not in found, f"{f} still uses socket: {found}"


def test_no_forbidden_file_uses_http_client():
    """The 5 files must not use http.client. None of them."""
    for f in FORBIDDEN_FILES:
        text = (PROJECT / f).read_text(encoding="utf-8")
        found = _has_network_module(text)
        assert "http.client" not in found, f"{f} still uses http.client: {found}"


def test_all_5_files_still_exist():
    """Sanity check: the 5 files exist (the rewrite target set)."""
    for f in FORBIDDEN_FILES:
        assert (PROJECT / f).exists(), f"missing: {f}"


def test_audit_no_network_has_no_allow_list():
    """audit_no_network.py must no longer have an ALLOW_LIST dict."""
    audit = PROJECT / "04_Validation/scripts/audit_no_network.py"
    text = audit.read_text(encoding="utf-8")
    assert "ALLOW_LIST" not in text, (
        f"audit_no_network.py still has ALLOW_LIST. The allow-list must be removed."
    )


def test_allow_list_closed_test_now_tests_for_zero():
    """test_allow_list_closed.py must test for ZERO entries, not 5."""
    test = PROJECT / "tests/test_allow_list_closed.py"
    text = test.read_text(encoding="utf-8")
    # the new contract: ALLOW_LIST has 0 entries
    # find any reference to 5 in the test
    assert "5 entries" not in text and "len(allow_list) == 5" not in text, (
        f"test_allow_list_closed.py still asserts 5 entries. Update to test for 0."
    )
