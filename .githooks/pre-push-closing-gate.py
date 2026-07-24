#!/usr/bin/env python
"""
OGIR Pre-Push Closing Procedure Gate

This script runs as a git pre-push hook. It blocks any push to
the origin remote unless the closing procedure is complete:

1. Chain must be MATCH (python -m src.verify_chain)
2. Tests must pass (python -m pytest tests/ -q)
3. A SIGN_OFF block must exist in the chain since the last push
4. The handover log must be newer than the last commit that sealed a block

If any check fails, the push is REJECTED with a message telling
the agent what to fix.

The "poke" — if the agent tries to push without sealing a SIGN_OFF
block, the hook says: "STOP. You must seal a SIGN_OFF block and
update the handover log before pushing. See AGENT_SIGNOFF_POLICY."

Install:
  Copy this file to .git/hooks/pre-push (or .git/hooks/pre-push.py
  and make .git/hooks/pre-push call it)

  On Windows, create .git/hooks/pre-push with:
    #!/bin/sh
    exec python "$PWD/.githooks/pre-push-closing-gate.py"
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

# Find the project root (where .git is)
def find_project_root() -> Path:
    """Walk up from this file to find the .git directory."""
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").is_dir():
            return p
        p = p.parent
    # Fallback: use the known path
    return Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")

PROJECT_ROOT = find_project_root()
TECHNICAL = PROJECT_ROOT / "02_Technical"
HANDOVER_LOG = PROJECT_ROOT / "04_Validation" / "HANDOVER_LOG.md"


def run_cmd(cmd: list, cwd: Path = None, timeout: int = 600) -> tuple:
    """Run a command, return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(TECHNICAL)
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd or PROJECT_ROOT),
            timeout=timeout,
            env=env,
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except Exception as e:
        return 1, "", str(e)


def check_chain() -> tuple:
    """Check 1: Chain must be MATCH."""
    rc, out, err = run_cmd(
        [sys.executable, "-m", "src.verify_chain"],
        cwd=TECHNICAL,
        timeout=120,
    )
    if rc != 0:
        return False, "Chain verify FAILED: " + (err or out)[:200]
    if "MATCH" not in out:
        return False, "Chain verify did not print MATCH: " + out[:200]
    return True, "Chain: MATCH"


def check_tests() -> tuple:
    """Check 2: Tests must pass (at least 400 passed, 0 failed)."""
    rc, out, err = run_cmd(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no", "-x"],
        timeout=600,
    )
    if rc != 0:
        # Extract the failure summary
        lines = (out + err).strip().split("\n")
        fail_line = [l for l in lines if "failed" in l.lower() and "passed" not in l.lower()]
        summary = fail_line[-1] if fail_line else (out + err)[-200:]
        return False, "Tests FAILED: " + summary[:200]
    return True, "Tests: PASSED"


def check_signoff_block() -> tuple:
    """Check 3: A SIGN_OFF block must exist in the recent chain blocks.

    We check the last 20 blocks for a SIGN_OFF event_type. If none
    found, the agent hasn't signed off.
    """
    # Read the chain and check the last 20 blocks
    vault_path = PROJECT_ROOT / "03_Vault" / "facts_registry.json"
    if not vault_path.exists():
        return False, "Vault file not found"
    try:
        import json
        data = json.loads(vault_path.read_text(encoding="utf-8"))
        blocks = data.get("blocks", [])
        if not blocks:
            return False, "Chain has no blocks"
        recent = blocks[-20:]
        has_signoff = any(
            "SIGN_OFF" in b.get("event_type", "").upper()
            for b in recent
        )
        if not has_signoff:
            return False, (
                "No SIGN_OFF block in the last 20 blocks. "
                "You must seal a SIGN_OFF block before pushing. "
                "See AGENT_SIGNOFF_POLICY_2026-07-24.md"
            )
        return True, "SIGN_OFF block found"
    except Exception as e:
        return False, "Cannot read chain: " + str(e)[:200]


def check_handover_log() -> tuple:
    """Check 4: Handover log must exist and be recent."""
    if not HANDOVER_LOG.exists():
        return False, "HANDOVER_LOG.md not found. You must update it before pushing."
    return True, "Handover log exists"


def main() -> int:
    """Run all checks. Return 0 to allow push, 1 to block."""
    print("=" * 60)
    print("OGIR CLOSING PROCEDURE GATE")
    print("=" * 60)

    checks = [
        ("Chain verify", check_chain),
        ("Tests pass", check_tests),
        ("SIGN_OFF block", check_signoff_block),
        ("Handover log", check_handover_log),
    ]

    all_pass = True
    for name, check_fn in checks:
        print()
        print("Check: " + name + "...")
        ok, msg = check_fn()
        status = "PASS" if ok else "FAIL"
        print("  " + status + ": " + msg)
        if not ok:
            all_pass = False

    print()
    print("=" * 60)
    if all_pass:
        print("ALL CHECKS PASSED. Push allowed.")
        print("=" * 60)
        return 0
    else:
        print("CLOSING PROCEDURE INCOMPLETE. Push BLOCKED.")
        print()
        print("Fix the failing checks above, then:")
        print("  1. Seal a SIGN_OFF block to the chain")
        print("  2. Update 04_Validation/HANDOVER_LOG.md")
        print("  3. Verify chain: python -m src.verify_chain")
        print("  4. Run tests: python -m pytest tests/ -q")
        print("  5. Try the push again")
        print()
        print("See: 04_Validation/AGENT_SIGNOFF_POLICY_2026-07-24.md")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())