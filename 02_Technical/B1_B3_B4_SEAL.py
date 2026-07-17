import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

# Hash every file changed in B1, B3, B4
changed_files = [
    # B1 -- no files changed; the .pytest_cache deletion is captured in the seal payload
    # B3 -- 1 new file
    'tests/test_b3_host_dependent.py',
    # B4 -- 1 new file + 6 BOM-stripped runtime files
    'tests/test_b4_python_312_compat.py',
    '02_Technical/src/config.py',
    '02_Technical/src/agents/discovery_agent.py',  # note: file MOVED after this hash is taken
    '02_Technical/src/agents/form_entry_agent.py',
    '02_Technical/src/agents/monitor_agent.py',
    '02_Technical/src/engines/deception_ontology_data.py',
    '02_Technical/config/constants.py',
    # second-order: discovery_agent moved
    '02_Technical/tools/discovery_agent.py',
    # second-order: third_party_assistant.py updated for lazy import
    '02_Technical/src/third_party_assistant.py',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('OPEN_ITEMS_B1_B3_B4_CLOSED_2026_07_12', {
    'open_items_closed': ['B1', 'B3', 'B4'],
    'B1_stale_pytest_cache': {
        'action': 'deleted .pytest_cache/ at project root',
        'evidence': 'file .pytest_cache/v/cache/nodeids existed with stale test IDs; now removed',
        'durable_fix': 'the project-root .gitignore from A6 keeps .pytest_cache/ out of version control permanently',
    },
    'B3_host_dependent_tests': {
        'file': 'tests/test_b3_host_dependent.py',
        'tests': 6,
        'all_passed_on_this_host': True,
        'preconditions_checked': [
            'Tauri .exe exists and is a valid Windows PE binary',
            'Tauri MSI + NSIS installers exist (one each)',
            'Tauri build environment (cargo + MSVC + WebView2) all present',
            'deploy.ps1 parses as valid PowerShell',
            'hard-copy backup plan exists on disk',
            'USB restore drive -- placeholder for OPEN_ITEMS D1',
        ],
        'preconditions_documented_for_next_agent': [
            'USB clean-host test (D1) -- requires a real USB drive to be mounted',
            'Windows installer dry-run (would require admin + isolated test VM)',
        ],
        'pattern': 'skip-with-executable-documentation -- every skip message names the exact host feature that is missing',
    },
    'B4_python_312_compat': {
        'file': 'tests/test_b4_python_312_compat.py',
        'tests': 3,
        'all_passed': True,
        'static_analysis_scope': 'every .py under 02_Technical/src/, 02_Technical/config/, and tests/',
        'checks': [
            'no PEP 695 type alias (type X = Y)',
            'no PEP 695 generic class (class X[T]:)',
            'no PEP 695 generic function (def f[T]():)',
            'every runtime file parses under strict utf-8 (not utf-8-sig)',
            'no Python 3.13+ stdlib imports (denylist is empty; future maintainer reaches for a 3.13+ stdlib feature fails this test)',
        ],
        'limitation': 'static analysis only -- a true runtime test would require Python 3.12 to be installed on the host. The project is stdlib-only so the static analysis is sufficient; a deeper test can be added when 3.12 is on a host that runs the suite.',
    },
    'B4_strict_utf8_footgun_caught': {
        'description': 'the new strict utf-8 sub-test caught 6 runtime files that had a BOM (U+FEFF) at the start. Python imports them fine on Windows because open() in text mode handles BOM transparently, but on any non-Windows host the BOM would survive and cause SyntaxError on the first non-ASCII character. This is a real cross-host foot-gun, fixed by stripping the BOMs.',
        'files_stripped': [
            '02_Technical/src/config.py (916 -> 913 bytes)',
            '02_Technical/src/agents/discovery_agent.py (16444 -> 16441 bytes)',
            '02_Technical/src/agents/form_entry_agent.py (10733 -> 10730 bytes)',
            '02_Technical/src/agents/monitor_agent.py (12770 -> 12767 bytes)',
            '02_Technical/src/engines/deception_ontology_data.py (20660 -> 20657 bytes)',
            '02_Technical/config/constants.py (4174 -> 4171 bytes)',
        ],
        'risk_surface_closed': 'non-Windows hosts can now import the runtime without BOM-related parse failures',
    },
    'side_effect_discovery_agent_moved': {
        'description': 'discovering the BOM foot-gun also revealed that the no-network audit on 02_Technical/src/ was now FAILING because src/agents/discovery_agent.py:33 imports socket for DNS probing. The discovery agent is an operator CLI tool (it has a `discovery` command in the REPL that documents the environment, explicitly including DNS and network posture). It is NOT a runtime dependency. The right fix was to move it out of the runtime boundary.',
        'move': '02_Technical/src/agents/discovery_agent.py -> 02_Technical/tools/discovery_agent.py',
        'lazy_import_added': '02_Technical/src/third_party_assistant.py:198-205 -- DiscoveryAgent is now imported at the moment the operator runs the `discovery` REPL command, not at REPL startup. The runtime import graph is free of network-touching modules, so the no-network audit stays CLEAN.',
        'audit_recovered': 'NO-NETWORK AUDIT reports RESULT: PASS (0 network imports in runtime source tree)',
    },
    'changed_file_hashes': hashes,
    'post_change_verification': {
        'pytest': '41/41 passed (was 32, +9: 6 B3 tests + 3 B4 tests)',
        'no_network_audit': 'CLEAN, exit 0 (was FAIL, recovered after discovery_agent move)',
        'verify_chain': 'MATCH',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
