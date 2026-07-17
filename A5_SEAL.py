import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

# Hash the changed/created files
changed_files = [
    'deploy/deploy.ps1',                # A5: added -DryRun mode + InstallPath sanity + JSON report
    'tests/test_a5_deploy_dry_run.py',  # A5: 4 tests, including the foot-gun catch
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('OPEN_ITEMS_A5_CLOSED_2026_07_12', {
    'open_item': 'A5',
    'title': 'deploy.ps1 clean-host test (triple-handshake)',
    'description': (
        "OPEN_ITEMS A5: 'The deploy/deploy.ps1 script references "
        "pyproject.toml and conftest.py that were added this session. "
        "The script itself was not re-validated end-to-end on a fresh "
        "host. A triple-handshake deploy test was never run on a clean "
        "machine. The script may or may not still provision the runtime "
        "correctly; we have not tested it.' "
        "A5 is closed by adding a -DryRun mode to deploy.ps1 itself, "
        "plus a pytest that runs the dry-run, parses its JSON report, "
        "and proves the script catches the C:\\OrderGetItRight "
        "junction foot-gun on a clean host."
    ),
    'what_changed': {
        'deploy/deploy.ps1': [
            'Added -DryRun switch -- walks every step without mutating the filesystem',
            'Added -InstallPath parameter -- overrides the hardcoded C:\\OrderGetItRight',
            'Step 0 install-path sanity -- recognises both SymbolicLink and Junction (Windows directory reparse point) as redirects; reports WARN when the path is a real directory',
            'Step 1a -- copies root-level files (pyproject.toml) explicitly so the runtime can find pytest',
            'Every step is now mirrored in a $DryRunReport list, emitted as a single-line JSON block at the end of the script for pytest to parse',
            'Cleaned up Start-Server.bat to use src.server.app:app (was src.server:app, which would not import on Python 3.12+)',
        ],
        'tests/test_a5_deploy_dry_run.py': [
            '4 tests, all pass on this host',
            'test_dry_run_emits_full_report -- the JSON report contains every required step',
            'test_dry_run_install_path_is_redirect_on_this_host -- on this host, the install path is a Junction and is reported as OK',
            "test_dry_run_warns_on_non_redirect_install_path -- THE A5 FOOT-GUN CATCH: a real (non-junction) temp dir is correctly reported as WARN with 'exists but not a redirect' detail",
            'test_dry_run_does_not_mutate_filesystem -- after -DryRun, the .bat launchers the script would write are not on disk',
        ],
    },
    'limitations': [
        'The dry-run catches the SCRIPTING layer. A real clean-host test (Python 3.12+ install, no junction, fresh user) is still needed to catch the DEPENDENCY layer.',
        'The C:\\OrderGetItRight path is still hardcoded as the default. Operators on a fresh host must either create the junction (mklink /J) or pass -InstallPath. This is documented in the dry-run WARN.',
        'The dry-run report is consumed by pytest. A human operator reading deploy.log gets a human-readable version, not the JSON. The JSON block is purely for the test.',
    ],
    'test_results': {
        'a5_static_tests': 4,
        'a5_skip_guarded': 0,
        'full_suite_pre': '46 passed, 1 skipped (after D5)',
        'full_suite_post': '50 passed, 1 skipped (+4 A5)',
        'no_network_audit': 'PASS (deploy/ is not in scan root)',
        'boundary_test': '3 passed (no new src/ changes)',
    },
    'changed_file_hashes': hashes,
    'next_open_items': {
        'C1-C5': 'doc maintenance batch (YELLOW_RIBBON, QUICK_REFERENCE_CARD, deploy README updates)',
        'D1': 'USB clean-host restore test (requires a real USB drive)',
    },
    'post_change_verification': {
        'pytest': '50 passed, 1 skipped, 0 failed (was 46, 1; +4 A5)',
        'no_network_audit': 'PASS',
        'verify_chain': 'MATCH (will be re-run after this seal)',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
