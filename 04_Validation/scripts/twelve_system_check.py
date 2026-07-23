#!/usr/bin/env python3
"""
12-system pre-flight check for the OrderGetItRight project.

Run this when the operator asks "all systems up" or starts a coding
session. Prints a 12-row table with [OK]/[!!] per system.

Usage:
    C:/Python314/python.exe 04_Validation/scripts/twelve_system_check.py
    # or via the skill loader
    python -c "from hermes_tools import execute_python; ..."
"""
import json
import os
import re
import subprocess
import sys

PROJECT = r'C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight'
PYTHON = r'C:\Python314\python.exe'
OPENCODE = r'C:\Users\justo\AppData\Roaming\npm\opencode.cmd'

def run(cmd, **kwargs):
    """Run a command and return (rc, stdout, stderr)."""
    r = subprocess.run(cmd, capture_output=True, text=True,
                       timeout=kwargs.pop('timeout', 60), **kwargs)
    return r.returncode, r.stdout, r.stderr

def check(name):
    """Decorator: print [OK]/[!!] per check. Returns the original fn unchanged."""
    def deco(fn):
        def wrapper(*args, **kwargs):
            try:
                ok, detail = fn(*args, **kwargs)
            except Exception as e:
                ok, detail = False, f"EXCEPTION: {e}"
            mark = "[OK]  " if ok else "[!!]  "
            print(f"  {mark}{name:<28} {'PASS' if ok else 'FAIL'}  {detail}")
            return ok
        return wrapper
    return deco

# 1. Ollama config
@check("1. Ollama config")
def check_1():
    cfg = json.load(open(os.path.expanduser('~/.ollama/config.json'), encoding='utf-8'))
    models = cfg.get('integrations', {}).get('opencode', {}).get('models', [])
    return bool(models), f"models={models}"

# 2. Ollama running
@check("2. ollama list")
def check_2():
    rc, out, _ = run(['ollama', 'list'], timeout=15)
    n = len(out.splitlines()) - 1
    return rc == 0 and n > 0, f"models={n}"

# 3. opencode smoke test
@check("3. opencode smoke")
def check_3():
    rc, out, err = run([OPENCODE, 'run', 'Respond with exactly: OPENCODE_OLLAMA_OK'], timeout=60)
    return 'OPENCODE_OLLAMA_OK' in out, f"rc={rc}"

# 4. chain
@check("4. chain MATCH")
def check_4():
    rc, out, _ = run([PYTHON, '-m', 'src.verify_chain'],
                     cwd=os.path.join(PROJECT, '02_Technical'), timeout=60)
    match = 'MATCH' in out and 'BROKEN' not in out
    bc = root = None
    for line in out.splitlines():
        if 'Block count' in line:
            bc = line.split(':')[1].strip()
        if 'root' in line.lower() and ':' in line and 'BLOCK' not in line.upper():
            parts = line.split(':', 1)
            if len(parts) == 2 and len(parts[1].strip()) > 20:
                root = parts[1].strip()[:32]
    return match, f"{bc} blocks, root {root}..." if bc else "no chain"

# 5. targeted tests
@check("5. targeted tests")
def check_5():
    rc, out, _ = run([PYTHON, '-m', 'pytest',
                      'tests/test_tagline_rebrand.py',
                      'tests/test_allow_list_closed.py',
                      'tests/test_audit_no_network.py',
                      'tests/test_which_canonical.py',
                      'tests/test_handover_drift_check.py',
                      'tests/test_post_seal_bark.py',
                      'tests/test_no_network_modules_anywhere.py',
                      'tests/test_tauri_config_valid.py',
                      '-q'], cwd=PROJECT, timeout=120)
    m = re.search(r'(\d+) passed', out)
    return rc == 0 and m, f"{m.group(1) if m else '?'} passed"

# 6. git state
@check("6. git state")
def check_6():
    rc, out, _ = run(['git', '-C', PROJECT, 'rev-parse', '--abbrev-ref', 'HEAD'])
    branch = out.strip()
    return branch == 'ogir-build-2026-07-18', f"branch={branch}"

# 7. worktrees
@check("7. worktrees")
def check_7():
    rc, out, _ = run(['git', '-C', PROJECT, 'worktree', 'list'])
    return len(out.strip().splitlines()) == 1, f"count={len(out.strip().splitlines())}"

# 8. opencode db
@check("8. opencode db")
def check_8():
    db = os.path.expanduser(r'~/.local/share/opencode/opencode.db')
    if not os.path.exists(db):
        return False, "missing"
    return True, f"size={os.path.getsize(db)} B"

# 9. spawn branches
@check("9. spawn branches")
def check_9():
    rc, out, _ = run(['git', '-C', PROJECT, 'branch', '-a'])
    sb = [l for l in out.splitlines() if 'spawn/' in l]
    return len(sb) == 0, f"count={len(sb)} (expected 0)"

# 10. INDEX.md step 0
@check("10. INDEX.md step 0")
def check_10():
    idx = open(os.path.join(PROJECT, 'INDEX.md'), encoding='utf-8').read()
    return 'STEP 0 IS A HARD GATE' in idx and 'Verify local-Ollama stack' in idx, "gate present"

# 11. rebrand
@check("11. rebrand test")
def check_11():
    rc, out, _ = run([PYTHON, '-m', 'pytest', 'tests/test_tagline_rebrand.py', '-q'],
                     cwd=PROJECT, timeout=30)
    return '5 passed' in out, "5/5"

# 12. hygiene
@check("12. deterministic_hygiene")
def check_12():
    rc, out, _ = run([PYTHON, '04_Validation/scripts/deterministic_hygiene.py', '--json-only'],
                     cwd=PROJECT, timeout=300)
    try:
        j = json.loads(out)
        return j.get('verdict') == 'GREEN', f"verdict={j.get('verdict')}"
    except Exception:
        return False, "parse fail"

def main():
    print('=' * 60)
    print('12-SYSTEM CHECK (OrderGetItRight pre-flight)')
    print('=' * 60)
    results = []
    for fn in [check_1, check_2, check_3, check_4, check_5, check_6,
               check_7, check_8, check_9, check_10, check_11, check_12]:
        results.append(fn())
    print('=' * 60)
    fails = [name for name, ok in zip(
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
        results) if not ok]
    if not fails:
        print('OVERALL: ALL 12 SYSTEMS UP')
        return 0
    else:
        print(f'OVERALL: {len(fails)} ISSUES: {fails}')
        return 1

if __name__ == '__main__':
    sys.exit(main())
