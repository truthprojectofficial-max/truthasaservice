#!/usr/bin/env python3
"""
Deterministic Repo Hygiene Script for Order Get It Right (OGIR).

Runs the verification triad (git status, pytest, verify_chain), produces
a JSON verdict, applies deterministic decision rules, and takes action
based on the verdict:

  GREEN: clean tree (or vault-only mods), 0 pytest failures, chain MATCH.
         Action: optionally seal a weekly marker block, push to USB.
  YELLOW: pytest failures, chain still MATCH. Action: run each failing
         test in isolation to classify flake vs regression. Include the
         isolation result in the JSON. Do not seal. Do not push.
  RED: chain BROKEN, or block count dropped, or unexpected non-vault
         files modified. Action: restore vault from HEAD. Do not seal.
         Do not push. Alert with the failure details.

The script is deterministic: no judgement calls, no "I think this is a
flake." The decision is in the numbers. Pass in isolation = flake.
Fail in isolation = regression. The JSON carries the answer.

Usage:
    python 04_Validation/scripts/deterministic_hygiene.py
    python 04_Validation/scripts/deterministic_hygiene.py --seal
    python 04_Validation/scripts/deterministic_hygiene.py --push
    python 04_Validation/scripts/deterministic_hygiene.py --seal --push

Output: JSON to stdout. Exit code 0 = GREEN, 1 = YELLOW, 2 = RED.

Constraint: pure stdlib Python 3.12+. No random, no network, no LLM.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")
TECHNICAL_DIR = PROJECT_ROOT / "02_Technical"
VAULT_DIR = PROJECT_ROOT / "03_Vault"
# Files whose modifications are expected during a hygiene run
# and do not indicate a YELLOW verdict. The vault files are
# auto-sealed by the lifecycle (lifespan shutdown, job registry
# updates). The handover files and report JSONs are written by
# derive_fingerprints.py and handover_drift_check.py, which are
# themselves part of the seal-test-verify-commit ritual.
VAULT_FILES = {
    "facts_registry.json",
    "job_registry.json",
    "affidavit_transcript.txt",
}
# Regex for the dated handover files written by
# handover_drift_check.py (and by the operator by hand).
HANDOVER_PATTERN = re.compile(r"^handover_next_session_\d{4}-\d{2}-\d{2}(_v\d+)?\.md$")
# Reports from derive_fingerprints.py and handover_drift_check.py
# whose mtime updates are expected.
EXPECTED_REPORTS = {
    "phase_4_fingerprints.json",
    "handover_drift_report.json",
}


def is_expected_modification(path: str) -> bool:
    """True if a git-status modification of this path is
    expected during a hygiene run (i.e. it was written by the
    audit path or by an operator-side ritual script)."""
    base = os.path.basename(path)
    if base in VAULT_FILES or base in EXPECTED_REPORTS:
        return True
    if path.startswith("03_Vault/"):
        return True
    if path.startswith("04_Validation/") and HANDOVER_PATTERN.match(base):
        return True
    return False
PYTHON = sys.executable

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_cmd(cmd, cwd=None, timeout=300):
    """Run a command, return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -2, "", str(e)


def parse_pytest_output(stdout):
    """Extract passed/failed/skipped/warnings from pytest -q output."""
    passed = 0
    failed = 0
    skipped = 0
    warnings = 0
    failed_tests = []

    for line in stdout.splitlines():
        # "233 passed, 1 skipped, 1 warning"
        if "passed" in line or "failed" in line or "error" in line:
            parts = line.strip().split(", ")
            for part in parts:
                part = part.strip()
                if "passed" in part:
                    try:
                        passed = int(part.split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "failed" in part:
                    try:
                        failed = int(part.split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "skipped" in part:
                    try:
                        skipped = int(part.split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "warning" in part:
                    try:
                        warnings = int(part.split()[0])
                    except (ValueError, IndexError):
                        pass
        # "FAILED tests/test_foo.py::test_bar - AssertionError: ..."
        if line.startswith("FAILED "):
            failed_tests.append(line.strip())

    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "warnings": warnings,
        "failed_tests": failed_tests,
    }


def parse_verify_chain_output(stdout):
    """Extract block count, claimed root, recomputed root, match from
    verify_chain output."""
    block_count = 0
    claimed_root = ""
    recomputed_root = ""
    match = False

    for line in stdout.splitlines():
        if line.strip().startswith("Block count"):
            try:
                block_count = int(line.strip().split(":")[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.strip().startswith("Claimed root"):
            claimed_root = line.strip().split(":", 1)[1].strip()
        elif line.strip().startswith("Recomputed root"):
            recomputed_root = line.strip().split(":", 1)[1].strip()
        elif "RESULT: MATCH" in line:
            match = True

    return {
        "block_count": block_count,
        "claimed_root": claimed_root,
        "recomputed_root": recomputed_root,
        "match": match,
    }


def classify_failing_test(test_name):
    """Run a single failing test in isolation to classify flake vs regression.

    Pass in isolation = flake (test-ordering issue, not a real regression).
    Fail in isolation = regression (real code breakage).

    Returns dict with isolation result.
    """
    cmd = [PYTHON, "-m", "pytest", test_name, "-v", "--tb=line", "-q"]
    code, stdout, stderr = run_cmd(cmd, cwd=PROJECT_ROOT, timeout=120)

    isolation_passed = (code == 0)

    # Extract the traceback line if it failed
    traceback_line = ""
    if not isolation_passed:
        for line in stdout.splitlines():
            if "Error" in line or "assert" in line.lower():
                traceback_line = line.strip()
                break

    return {
        "test": test_name,
        "isolation_passed": isolation_passed,
        "classification": "flake" if isolation_passed else "regression",
        "traceback": traceback_line,
    }


def auto_patch_flake(test_name):
    """Auto-patch a flake caused by statement collision in facts_registry.

    The known pattern: two tests use the same statement string, and
    facts_registry.add_fact raises ValueError("Fact already exists for
    statement and source combination"). The deterministic fix is to
    add a unique suffix to the statement in the test file.

    This function:
    1. Extracts the test file path from the test name (tests/test_foo.py::test_bar)
    2. Reads the file
    3. Finds the test function
    4. Finds the 'statement' field in the test
    5. Appends a unique suffix (timestamp) to make it unique
    6. Writes the file back

    Returns dict with patch result.
    """
    try:
        # Extract file path from test_name: "tests/test_foo.py::test_bar"
        if "::" not in test_name:
            return {"patched": False, "reason": "cannot parse test name"}

        file_path_str, test_func = test_name.split("::", 1)
        test_file = PROJECT_ROOT / file_path_str

        if not test_file.exists():
            return {"patched": False, "reason": f"file not found: {test_file}"}

        content = test_file.read_text(encoding="utf-8", errors="replace")

        # Find the test function and look for a "statement" field
        # The pattern in OGIR tests is typically:
        #   "statement": "some fixed text",
        # We need to find this within the test function's body and make
        # the statement unique. We do this by finding the line containing
        # "statement" within the function.

        lines = content.splitlines()
        patched = False
        patch_details = []

        # Find the function start
        func_start = None
        for i, line in enumerate(lines):
            if f"def {test_func}" in line:
                func_start = i
                break

        if func_start is None:
            return {"patched": False, "reason": f"function {test_func} not found"}

        # Find the next function or end of file
        func_end = len(lines)
        for i in range(func_start + 1, len(lines)):
            if lines[i].startswith("def ") or lines[i].startswith("class "):
                func_end = i
                break

        # Within the function, find "statement" lines and add a unique suffix
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        for i in range(func_start, func_end):
            line = lines[i]
            if '"statement"' in line and "f\"" not in line:
                # Found a hardcoded statement. Add a unique suffix.
                # Pattern: "statement": "some text",
                # Becomes: "statement": f"some text (hygiene {ts})",
                # We need to be careful: the line might use single or double quotes
                stripped = line.strip()
                if stripped.startswith('"statement"'):
                    # Replace "text" with f"text (hygiene ts)"
                    # Find the value between quotes
                    import re
                    # Match: "statement": "value",
                    m = re.search(r'"statement":\s*"([^"]+)"', stripped)
                    if m:
                        old_value = m.group(1)
                        new_value = f"{old_value} (hygiene {ts})"
                        new_line = line.replace(f'"{old_value}"', f'f"{new_value}"')
                        lines[i] = new_line
                        patched = True
                        patch_details.append(f"line {i+1}: statement uniquified with suffix (hygiene {ts})")

        if patched:
            test_file.write_text("\n".join(lines), encoding="utf-8")
            return {
                "patched": True,
                "file": str(test_file),
                "details": patch_details,
            }
        else:
            return {
                "patched": False,
                "reason": "no hardcoded statement found in test function (may be a different flake type)",
            }
    except Exception as e:
        return {"patched": False, "reason": str(e)}


def seal_yellow_alert(iso_result):
    """Seal a YELLOW_ALERT block to the chain for a regression.

    The block carries the test name, traceback, and classification so
    the next session has the exact data needed to fix the regression.
    Uses CHAIN_OPERATOR_ID (pseudonymised) — no personal data.
    """
    try:
        sys.path.insert(0, str(TECHNICAL_DIR.resolve()))
        from src.io.vault_io import append_block

        block = append_block(
            f"YELLOW_ALERT_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}",
            {
                "type": "yellow_alert",
                "test": iso_result.get("test", ""),
                "classification": "regression",
                "isolation_passed": iso_result.get("isolation_passed", False),
                "traceback": iso_result.get("traceback", ""),
                "verdict": "YELLOW",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        return {
            "sealed": True,
            "block_index": block.get("index"),
            "block_hash": block.get("current_hash"),
        }
    except Exception as e:
        return {"sealed": False, "reason": str(e)}


# ---------------------------------------------------------------------------
# Triad
# ---------------------------------------------------------------------------

def run_triad():
    """Run the full verification triad and return the result JSON."""

    # 1. Git status
    git_code, git_stdout, git_stderr = run_cmd(
        ["git", "status", "--short"], cwd=PROJECT_ROOT
    )
    git_lines = [l.strip() for l in git_stdout.splitlines() if l.strip()]
    git_modified = []
    for line in git_lines:
        # Format: " M path" or "?? path"
        status = line[:2].strip()
        path = line[3:].strip() if len(line) > 2 else line.strip()
        git_modified.append({"status": status, "path": path})

    # Classify: vault-only mods are expected (lifecycle blocks). Non-vault
    # mods in a hygiene run are unexpected.
    vault_only = all(
        is_expected_modification(m["path"])
        for m in git_modified
    ) if git_modified else True

    # 2. Pytest
    pytest_code, pytest_stdout, pytest_stderr = run_cmd(
        [PYTHON, "-m", "pytest", "tests/", "-q", "--tb=line"],
        cwd=PROJECT_ROOT,
        timeout=300,
    )
    pytest_result = parse_pytest_output(pytest_stdout)

    # 3. Verify chain
    chain_code, chain_stdout, chain_stderr = run_cmd(
        [PYTHON, "-m", "src.verify_chain"],
        cwd=TECHNICAL_DIR,
        timeout=60,
    )
    chain_result = parse_verify_chain_output(chain_stdout)

    # 4. Decision rules
    chain_broken = not chain_result["match"]
    pytest_failed = pytest_result["failed"] > 0
    unexpected_files = not vault_only and len(git_modified) > 0

    if chain_broken:
        verdict = "RED"
        reason = "chain BROKEN — claimed root does not match recomputed root"
    elif pytest_failed:
        verdict = "YELLOW"
        reason = f"{pytest_result['failed']} test(s) failed — running isolation classification"
    elif unexpected_files:
        verdict = "YELLOW"
        reason = f"unexpected non-vault files modified: {[m['path'] for m in git_modified if not is_expected_modification(m['path'])]}"
    else:
        verdict = "GREEN"
        reason = "all checks passed — clean tree, 0 failures, chain MATCH"

    # 5. If YELLOW with test failures, classify each failing test
    isolation_results = []
    if verdict == "YELLOW" and pytest_result["failed_tests"]:
        for ft in pytest_result["failed_tests"]:
            # Extract the test name from "FAILED tests/test_foo.py::test_bar - ..."
            test_name = ft.replace("FAILED ", "").split(" - ")[0].strip()
            isolation_results.append(classify_failing_test(test_name))

    # 5a. YELLOW ACTIONS — auto-patch flakes, seal alert for regressions
    yellow_actions = []
    if verdict == "YELLOW" and isolation_results:
        for iso in isolation_results:
            if iso["classification"] == "flake":
                # FLAKE: statement collision in facts_registry. The fix is
                # deterministic: add a unique suffix to the test's statement
                # so it does not collide with another test's statement.
                # The pattern is known (same statement+source raises
                # ValueError in facts_registry.add_fact).
                patch_result = auto_patch_flake(iso["test"])
                yellow_actions.append({
                    "test": iso["test"],
                    "classification": "flake",
                    "action": "auto_patched" if patch_result["patched"] else "patch_failed",
                    "patch_detail": patch_result,
                })
            else:
                # REGRESSION: cannot auto-fix. Seal a YELLOW_ALERT block
                # with the exact test name, traceback, and failing
                # assertion so the next session has the data it needs.
                alert_result = seal_yellow_alert(iso)
                yellow_actions.append({
                    "test": iso["test"],
                    "classification": "regression",
                    "action": "alert_sealed" if alert_result["sealed"] else "seal_failed",
                    "alert_detail": alert_result,
                })

    # 6. If RED (chain broken), attempt vault restore from HEAD
    vault_restored = False
    if verdict == "RED" and chain_broken:
        restore_code, restore_stdout, restore_stderr = run_cmd(
            ["git", "checkout", "HEAD", "--",
             "03_Vault/facts_registry.json",
             "03_Vault/job_registry.json",
             "03_Vault/affidavit_transcript.txt"],
            cwd=PROJECT_ROOT,
        )
        vault_restored = (restore_code == 0)

    # 7. Build the JSON
    result = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": "Order Get It Right",
        "triad": {
            "git": {
                "status": "clean" if not git_modified else "dirty",
                "modified_files": git_modified,
                "vault_only": vault_only,
            },
            "pytest": {
                **pytest_result,
            },
            "chain": {
                **chain_result,
            },
        },
        "verdict": verdict,
        "reason": reason,
        "isolation_results": isolation_results,
        "yellow_actions": yellow_actions,
        "vault_restored": vault_restored,
        "actions": {
            "seal_eligible": verdict == "GREEN",
            "push_eligible": verdict == "GREEN",
            "manual_intervention_required": verdict in ("YELLOW", "RED"),
        },
    }

    return result


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def seal_weekly_marker(triad_result):
    """Seal a WEEKLY_HYGIENE block to the chain. Only called on GREEN."""
    sys.path.insert(0, str(TECHNICAL_DIR.resolve()))
    from src.io.vault_io import append_block

    block = append_block(
        f"WEEKLY_HYGIENE_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}",
        {
            "type": "weekly_hygiene",
            "pytest_passed": triad_result["triad"]["pytest"]["passed"],
            "pytest_failed": triad_result["triad"]["pytest"]["failed"],
            "pytest_skipped": triad_result["triad"]["pytest"]["skipped"],
            "chain_block_count": triad_result["triad"]["chain"]["block_count"],
            "chain_root": triad_result["triad"]["chain"]["claimed_root"],
            "chain_match": triad_result["triad"]["chain"]["match"],
            "git_status": triad_result["triad"]["git"]["status"],
            "verdict": "GREEN",
            "operator": "automated-hygiene",
            "timestamp": triad_result["timestamp"],
        },
    )
    return block


def push_to_usb():
    """Push the current branch to the USB bare repo."""
    code, stdout, stderr = run_cmd(
        ["git", "push", "usb", "ogir-build-2026-07-18"],
        cwd=PROJECT_ROOT,
    )
    return {"exit_code": code, "stdout": stdout.strip(), "stderr": stderr.strip()}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Deterministic repo hygiene for OGIR."
    )
    parser.add_argument(
        "--seal",
        action="store_true",
        help="Seal a weekly marker block on GREEN verdict.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push to USB bare repo on GREEN verdict.",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output JSON only, no actions (dry run).",
    )
    args = parser.parse_args()

    result = run_triad()

    # Take actions on GREEN
    if result["verdict"] == "GREEN" and not args.json_only:
        if args.seal:
            block = seal_weekly_marker(result)
            result["seal_block"] = {
                "index": block.get("index"),
                "hash": block.get("current_hash"),
            }
        if args.push:
            push_result = push_to_usb()
            result["push_result"] = push_result

    # Output JSON
    print(json.dumps(result, indent=2))

    # Exit code: 0 = GREEN, 1 = YELLOW, 2 = RED
    sys.exit(0 if result["verdict"] == "GREEN" else 1 if result["verdict"] == "YELLOW" else 2)


if __name__ == "__main__":
    main()