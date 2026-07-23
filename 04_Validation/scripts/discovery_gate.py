#!/usr/bin/env python3
"""
Discovery gate -- 5-check pre-flight for the local-Ollama stack.

Run this BEFORE proposing any auth flow. If any check fails, the local
stack is misconfigured. Fix Ollama first; do NOT propose API keys, OAuth,
or login flows.

Usage:
    python 02_Technical/_tmp_5check.py
    # or copy to 04_Validation/scripts/discovery_gate.py and run from there
"""
import json
import os
import subprocess
import sys

OPENCODE = r'C:\Users\justo\AppData\Roaming\npm\opencode.cmd'
PYTHON = r'C:\Python314\python.exe'

def header(s):
    print('=' * 60)
    print(s)
    print('=' * 60)

def run(cmd, **kwargs):
    r = subprocess.run(cmd, capture_output=True, text=True,
                       timeout=kwargs.pop('timeout', 60), **kwargs)
    return r.returncode, r.stdout, r.stderr

# 1. Ollama config wired
header('1. Ollama config wired for opencode')
try:
    cfg = json.load(open(os.path.expanduser('~/.ollama/config.json'), encoding='utf-8'))
    models = cfg.get('integrations', {}).get('opencode', {}).get('models', [])
    if models:
        print(f'  PASS: opencode models = {models}')
        c1 = True
    else:
        print('  FAIL: no opencode models in config')
        c1 = False
except Exception as e:
    print(f'  FAIL: {e}')
    c1 = False

# 2. Ollama running
header('2. ollama list (running)')
rc, out, err = run(['ollama', 'list'], timeout=15)
n = len(out.splitlines()) - 1
if rc == 0 and n > 0:
    print(f'  PASS: {n} models loaded')
    c2 = True
else:
    print(f'  FAIL: {err[:200] or "no models"}')
    c2 = False

# 3. opencode smoke test
header('3. opencode smoke test (the gate)')
rc, out, err = run([OPENCODE, 'run', 'Respond with exactly: OPENCODE_OLLAMA_OK'], timeout=60)
if 'OPENCODE_OLLAMA_OK' in out:
    print('  PASS: opencode returned the marker')
    c3 = True
else:
    print(f'  FAIL: stdout={out[-100:].strip()}')
    c3 = False

# 4. opencode db exists
header('4. opencode db')
db = os.path.expanduser(r'~/.local/share/opencode/opencode.db')
if os.path.exists(db):
    print(f'  PASS: {os.path.getsize(db)} B')
    c4 = True
else:
    print('  FAIL: db not found')
    c4 = False

# 5. chain still MATCH (if in a project)
header('5. chain MATCH (optional)')
project = r'C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight'
if os.path.exists(os.path.join(project, '02_Technical')):
    rc, out, _ = run([PYTHON, '-m', 'src.verify_chain'],
                     cwd=os.path.join(project, '02_Technical'), timeout=60)
    if 'MATCH' in out and 'BROKEN' not in out:
        bc = next((l.split(':')[1].strip() for l in out.splitlines() if 'Block count' in l), '?')
        print(f'  PASS: {bc} blocks, chain MATCH')
        c5 = True
    else:
        print('  FAIL: chain not MATCH')
        c5 = False
else:
    print('  SKIP: not in OrderGetItRight project')
    c5 = True  # not applicable

# Summary
print('=' * 60)
results = {'1': c1, '2': c2, '3': c3, '4': c4, '5': c5}
fails = [k for k, v in results.items() if not v]
if not fails:
    print('GATE: ALL 5 CHECKS PASS. The local stack is operational. Do NOT propose auth.')
    sys.exit(0)
else:
    print(f'GATE: {len(fails)} CHECKS FAILED: {fails}')
    print('  The local stack is misconfigured. Fix Ollama first.')
    print('  Do NOT propose API keys, OAuth, or login flows.')
    sys.exit(1)
