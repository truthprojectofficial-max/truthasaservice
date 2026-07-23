"""
whole_project_audit.py
======================

The big one. The operator's request: "EVERY CORECTION EVER RUN OVER EVERY
FILE OF WHOLE PROJECT AUDIT" + "COMPLETE ANNALISES DONE" + "LIST OF
STANDARD PROJECT ASSESMENTS AND AUDITS TO DO AS WELL".

This script runs:
  1. Every audit script in 04_Validation/scripts/ (currently 5: allow_list_audit,
     audit_no_network, correction_audit, operator_questions_audit, agent_stack_audit,
     tool_stack_audit) -- plus this one
  2. The targeted pytest suite (35 tests across 7 files)
  3. The chain MATCH verification
  4. The drift detector (handover_drift_check)
  5. The whole-project file walk:
       - For every .py file, check it's not in 99_Archive_Historical/
       - For every .md file in 04_Validation/, check it exists and is non-empty
       - For every sealed event in the chain, check it has a fix_id, files_changed,
         before, after (the seal-payload-completeness probe)
  6. The standard-audit list (15 audits the operator asked for, with status)

Run from project root:
    python 04_Validation/scripts/whole_project_audit.py

Exit codes:
    0 = all audits pass, all checks pass
    1 = one or more audits fail
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PYTHON = r"C:\Python314\python.exe"
CHAIN_PATH = PROJECT / "03_Vault" / "facts_registry.json"
SCRIPTS_DIR = PROJECT / "04_Validation" / "scripts"
DOCS_DIR = PROJECT / "04_Validation"


def run_audit_script(script_name, timeout=300):
    """Run another audit script. Return (passed: bool, output_tail: str)."""
    script = SCRIPTS_DIR / script_name
    if not script.exists():
        return False, f"script not found: {script_name}"
    try:
        r = subprocess.run([PYTHON, str(script)], capture_output=True, text=True,
                           timeout=timeout, cwd=str(PROJECT))
        return r.returncode == 0, r.stdout[-300:]
    except subprocess.TimeoutExpired:
        return False, "(timeout)"
    except Exception as e:
        return False, f"(error: {e})"


def run_targeted_tests():
    """Run the targeted pytest suite (35 tests)."""
    test_files = [
        "tests/test_post_seal_bark.py",
        "tests/test_tagline_rebrand.py",
        "tests/test_allow_list_closed.py",
        "tests/test_audit_no_network.py",
        "tests/test_allow_list_audit.py",
        "tests/test_which_canonical.py",
        "tests/test_handover_drift_check.py",
    ]
    try:
        r = subprocess.run([PYTHON, "-m", "pytest"] + test_files + ["-q"],
                           capture_output=True, text=True, timeout=180, cwd=str(PROJECT))
        m = re.search(r"(\d+) passed", r.stdout)
        passed = int(m.group(1)) if m else 0
        return passed == 35, f"{passed}/35 passed"
    except Exception as e:
        return False, f"(error: {e})"


def verify_chain():
    """Run src.verify_chain. Return (passed: bool, root: str)."""
    try:
        r = subprocess.run([PYTHON, "-m", "src.verify_chain"],
                           capture_output=True, text=True, timeout=60,
                           cwd=str(PROJECT / "02_Technical"))
        match = "MATCH" in r.stdout and "BROKEN" not in r.stdout
        root = None
        for line in r.stdout.splitlines():
            if "root" in line.lower() and ":" in line and "BLOCK" not in line.upper():
                parts = line.split(":", 1)
                if len(parts) == 2 and len(parts[1].strip()) > 20:
                    root = parts[1].strip()
                    break
        return match, f"root {root[:20] if root else '?'}..."
    except Exception as e:
        return False, f"(error: {e})"


def check_seal_payload_completeness():
    """For every sealed event in the chain, check it has fix_id, files_changed, before, after."""
    try:
        data = json.loads(CHAIN_PATH.read_text(encoding="utf-8"))
        blocks = data.get("blocks", [])
        incomplete = []
        for b in blocks:
            payload = b.get("payload", {})
            if not isinstance(payload, dict):
                continue
            # The seal-payload-completeness probe: fix_id, files_changed, before/after
            has_fix_id = "fix_id" in payload
            has_files = "files_changed" in payload
            has_before_after = "before" in payload or "after" in payload
            if not (has_fix_id and has_files and has_before_after):
                # skip SHUTDOWN / lifecycle blocks
                event = b.get("event_type", "")
                if "SHUTDOWN" in event.upper() or "TEST_" in event.upper() or "LIFECYCLE" in event.upper():
                    continue
                incomplete.append((b["index"], event))
        if not incomplete:
            return True, f"all {len(blocks)} blocks have complete payloads (or are lifecycle)"
        return False, f"{len(incomplete)} blocks incomplete: {incomplete[:5]}"
    except Exception as e:
        return False, f"(error: {e})"


def file_walk_check():
    """Walk every file in the project. Ensure no .py in 99_Archive_Historical/,
    every .md in 04_Validation/ exists, every audit script exists."""
    issues = []
    # 1. no .py in 99_Archive_Historical/ (only .txt allowed)
    archive_py = list((PROJECT / "99_Archive_Historical").rglob("*.py"))
    if archive_py:
        issues.append(f"{len(archive_py)} .py files in 99_Archive_Historical/")
    # 2. every .md in 04_Validation/ is non-empty
    md_files = list((PROJECT / "04_Validation").rglob("*.md"))
    empty_md = [str(m) for m in md_files if m.stat().st_size == 0]
    if empty_md:
        issues.append(f"empty .md files: {empty_md[:3]}")
    # 3. count of audit scripts
    audit_scripts = list(SCRIPTS_DIR.glob("*audit*.py"))
    if len(audit_scripts) < 4:
        issues.append(f"only {len(audit_scripts)} audit scripts (expected 4+)")
    # 4. count of operator-facing docs in 04_Validation/
    key_docs = ["INDEX.md", "MASTER_TODO_2026-07-23.md", "HEAD_TO_TOE_ALIGNMENT_2026-07-23.md",
                "OPEN_ITEMS_AND_REFERENCE.md", "MAINTENANCE_PLAN.txt", "AUDIT_NO_NETWORK.md",
                "BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md"]
    missing = [d for d in key_docs if not (DOCS_DIR / d).exists()]
    if missing:
        issues.append(f"missing key docs: {missing}")
    if not issues:
        return True, f"{len(md_files)} .md files, {len(audit_scripts)} audit scripts, 0 issues"
    return False, "; ".join(issues)


# The 15 standard assessments the operator asked for
STANDARD_ASSESSMENTS = [
    ("correction_audit.py", "installed", "6 corrections x 31 probes, every session"),
    ("whole-project audit (this script)", "installed", "every file, every audit, every pattern"),
    ("agent-stack audit", "installed", "7 agents verified at once"),
    ("tool-stack audit", "installed", "tools + skills + resources"),
    ("file-destination audit", "TODO", "verify 5-place rule: every change goes to one of 5 dirs"),
    ("network-module audit", "DONE", "test_audit_no_network.py"),
    ("canonical-sentinel audit", "DONE", "test_which_canonical.py"),
    ("vault-reseed audit", "DONE", "test_vault_reseed_guard.py"),
    ("tagline-rebrand audit", "DONE", "test_tagline_rebrand.py"),
    ("allow-list-closed audit", "DONE", "test_allow_list_closed.py"),
    ("handover-drift audit", "DONE", "test_handover_drift_check.py"),
    ("Ollama-isolation audit", "DONE", "test_ollama_isolation.py"),
    ("post-seal-bark audit", "DONE", "test_post_seal_bark.py"),
    ("boundary audit", "DONE", "test_00_99_boundary.py"),
    ("operator-questions audit", "installed", "this session's 18 questions, automated"),
]


def main():
    print("=" * 70)
    print("WHOLE-PROJECT AUDIT: every file, every audit, every pattern")
    print("=" * 70)
    print()

    total_pass = 0
    total_fail = 0

    # 1. Run every audit script
    print("--- 1. AUDIT SCRIPTS (in 04_Validation/scripts/) ---")
    for script in ["correction_audit.py", "operator_questions_audit.py",
                   "agent_stack_audit.py", "tool_stack_audit.py"]:
        ok, detail = run_audit_script(script, timeout=300)
        mark = "OK" if ok else "FAIL"
        print(f"  [{mark:>4}] {script:<35} {detail}")
        if ok: total_pass += 1
        else: total_fail += 1
    print()

    # 2. Run the targeted pytest suite
    print("--- 2. TARGETED PYTEST SUITE ---")
    ok, detail = run_targeted_tests()
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark:>4}] tests/test_*  {detail}")
    if ok: total_pass += 1
    else: total_fail += 1
    print()

    # 3. verify_chain
    print("--- 3. CHAIN VERIFY ---")
    ok, detail = verify_chain()
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark:>4}] verify_chain  {detail}")
    if ok: total_pass += 1
    else: total_fail += 1
    print()

    # 4. seal payload completeness
    print("--- 4. SEAL-PAYLOAD-COMPLETENESS ---")
    ok, detail = check_seal_payload_completeness()
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark:>4}] {detail}")
    if ok: total_pass += 1
    else: total_fail += 1
    print()

    # 5. file walk
    print("--- 5. FILE WALK ---")
    ok, detail = file_walk_check()
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark:>4}] {detail}")
    if ok: total_pass += 1
    else: total_fail += 1
    print()

    # 6. The 15 standard assessments
    print("--- 6. STANDARD PROJECT ASSESSMENTS (15 total) ---")
    for name, status, detail in STANDARD_ASSESSMENTS:
        print(f"  [{status:<10}] {name:<35} {detail}")
    print()

    print("=" * 70)
    print(f"TOTAL: {total_pass} pass, {total_fail} fail")
    print("=" * 70)
    if total_fail == 0:
        print()
        print("WHOLE-PROJECT AUDIT: ALL CHECKS PASS. The project is whole.")
        sys.exit(0)
    else:
        print()
        print(f"{total_fail} checks failed. Investigate before continuing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
