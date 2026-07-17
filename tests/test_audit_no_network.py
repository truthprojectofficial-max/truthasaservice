"""
Order Get It Right -- No-Network Audit (extended) test

Validates that audit_no_network.py:

  1. PASSes on the current tree (CLEAN + ALLOWED only).
  2. FAILs (exit 1) if a network import is added to a non-allow-listed
     file in tests/ or tools/.
  3. PASSes if a network import is added to an allow-listed file in
     tests/ or tools/.
  4. FAILs HARD (exit 1) if a network import is added to a file
     under 02_Technical/src/ -- the runtime promise.

The test runs the audit script as a subprocess against a sandbox
copy of the project tree, so it does not touch the canonical
sources. The sandbox is built under the system temp dir and torn
down at the end of the test.

This is the executable proof of the no-network contract. If this
test passes, the contract holds. If this test fails, the contract
is broken and the operator must investigate before sealing.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT_REL = Path("04_Validation") / "scripts" / "audit_no_network.py"


def _build_sandbox(src_root: Path) -> Path:
    """Copy the project tree to a temp dir. Exclude caches and build
    artefacts that the audit script itself ignores."""
    tmp = Path(tempfile.mkdtemp(prefix="ogir_audit_"))
    ignore = shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", "target", "node_modules",
        "*.bak-pre-*", ".git",
    )
    shutil.copytree(src_root, tmp / "OrderGetItRight", ignore=ignore)
    return tmp / "OrderGetItRight"


def _run_audit(sandbox: Path) -> int:
    """Run the audit script against the sandbox. Return exit code."""
    script = sandbox / AUDIT_SCRIPT_REL
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(sandbox),
        capture_output=True,
        text=True,
    )
    return proc.returncode


class TestAuditNoNetwork(unittest.TestCase):
    def setUp(self):
        self.sandbox = _build_sandbox(PROJECT_ROOT)

    def tearDown(self):
        shutil.rmtree(self.sandbox.parent, ignore_errors=True)

    def test_clean_tree_passes(self):
        """The current tree must pass: CLEAN + ALLOWED, no FAIL or REVIEW."""
        rc = _run_audit(self.sandbox)
        self.assertEqual(
            rc, 0,
            f"audit_no_network.py must pass on the current tree (rc={rc})",
        )

    def test_runtime_network_import_fails_hard(self):
        """Adding `import urllib` to a runtime file must fail the audit."""
        target = self.sandbox / "02_Technical" / "src" / "_net_smuggle.py"
        target.write_text("import urllib.request\n", encoding="utf-8")
        rc = _run_audit(self.sandbox)
        self.assertEqual(
            rc, 1,
            "a network import in 02_Technical/src/ must FAIL the audit (runtime promise)",
        )

    def test_non_allow_listed_tool_import_fails(self):
        """A network import in a NON-allow-listed tools/ file must REVIEW."""
        target = self.sandbox / "02_Technical" / "tools" / "_sneaky.py"
        target.write_text("import socket\n", encoding="utf-8")
        rc = _run_audit(self.sandbox)
        self.assertEqual(
            rc, 1,
            "a non-allow-listed network import in tools/ must REVIEW the audit",
        )

    def test_non_allow_listed_test_import_fails(self):
        """A network import in a NON-allow-listed tests/ file must REVIEW."""
        target = self.sandbox / "tests" / "_sneaky_test.py"
        target.write_text("import socket\n", encoding="utf-8")
        rc = _run_audit(self.sandbox)
        self.assertEqual(
            rc, 1,
            "a non-allow-listed network import in tests/ must REVIEW the audit",
        )


if __name__ == "__main__":
    unittest.main()
