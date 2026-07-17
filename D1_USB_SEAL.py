"""
Seal the D1 USB clean-host test to the Merkle chain.

Closes OPEN_ITEMS D1. The D1 USB clean-host test caught three
real-deploy bugs that the A5.1 dry-run could not have caught --
which is exactly why the clean-host test exists (the dry-run
catches the scripting layer; the real deploy catches the
operating-system and execution layer).

Sealed as block 2739.
"""
import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

changed_files = [
    'deploy/deploy.ps1',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('OPEN_ITEMS_D1_USB_CLEAN_HOST_TEST_2026_07_12', {
    'open_item': 'D1',
    'context': (
        "USB clean-host test. The deploy hardened in session 8 (A5.1) was "
        "run end-to-end on a real microSD card against a Windows host. "
        "Three real-deploy bugs were caught that the dry-run could not have "
        "caught -- this is exactly the value of the clean-host test "
        "(the dry-run catches the SCRIPTING layer; the real deploy catches "
        "the OPERATING-SYSTEM and EXECUTION layer)."
    ),
    'test_environment': {
        'storage': 'microSDXC UHS-1 64GB, mounted as D:\\',
        'filesystem': 'exFAT, 60.8GB free, Healthy',
        'card_reader': 'Realtek RTS5208 (PCISTOR\\Disk&Ven_RSPER&Prod_RTS5208LUN0)',
        'host_python': 'C:\\Python314\\python.exe (version 3.14.6)',
        'card_copy_size': '22.9 MB (excluded tauri-shell\\target = 1.6 GB, __pycache__, .pytest_cache, .bak-pre-*)',
    },
    'real_deploy_bugs_caught': {
        '1_step0a_project_root_resolution': {
            'file': 'deploy/deploy.ps1',
            'bug': (
                "Step 0a used (Get-Location).Path for $ProjectRoot. When the "
                "script is launched via powershell -File, the cwd is the "
                "caller's cwd, not the script location. The operator's harness "
                "cwd was C:\\Users\\justo\\.codex, which has no pyproject.toml. "
                "Script refused with pyproject.toml not found -- a correct "
                "refusal, but in the wrong direction. The fix: prefer the "
                "script's own location (Split-Path -Parent $MyInvocation.MyCommand.Path) "
                "with cwd as fallback. Now USB-launchable: any cwd works."
            ),
        },
        '2_step1_mirror_same_tree': {
            'file': 'deploy/deploy.ps1',
            'bug': (
                "When install path == project root (the USB-stick case), "
                "Copy-Item tries to copy each file onto itself and PowerShell "
                "errors with 'Cannot overwrite the item X with itself'. The "
                "source IS the destination, so the mirror is a no-op -- but "
                "PowerShell refuses to do it. The fix: detect SameTree via "
                "Resolve-Path and skip with an INFO log and a dry-run report "
                "entry. The mirror step is correctly identified as a no-op, "
                "not silently skipped."
            ),
        },
        '3_step6_verify_chain_cwd': {
            'file': 'deploy/deploy.ps1',
            'bug': (
                "Step 6 ran 'python -m src.verify_chain' from the script's "
                "cwd (the operator's harness cwd). 'python -m' requires the "
                "cwd to be the package parent (02_Technical). Without the cd, "
                "Python raised ModuleNotFoundError. The fix: Push-Location to "
                "$InstallPath\\02_Technical, run verify, Pop-Location. "
                "try/finally guarantees the Pop-Location even on error."
            ),
        },
    },
    'audit_results': {
        'pytest_host': '50 passed, 1 skipped, 0 failed (no regressions from the 3 fixes)',
        'pytest_card': (
            "NOT RUN on the card -- the card has no Python venv, so pytest "
            "cannot run from the card itself. The host pytest is the "
            "canonical gate; the card deploy is the OPERATING-SYSTEM test."
        ),
        'a5_dry_run_tests': '4/4 PASS (the 3 fixes preserved the dry-run JSON-report contract)',
        'card_deploy': 'DEPLOYMENT COMPLETE -- chain re-derivation returned MATCH on the card',
        'verify_chain_launcher': (
            "PASS -- D:\\OrderGetItRight\\launchers\\Verify-Chain.bat runs "
            "end-to-end against the card vault, returns MATCH at block 2738, "
            "root 5d8bf6748ee8d2873820d582726a752cdc5b9e802d9e2ce8cc150cc5c1ce0f0c"
        ),
        'launcher_templating': (
            "PASS -- Start-Server.bat, Run-AuditCli.bat, Verify-Tests.bat, "
            "Verify-Chain.bat, Build-Tauri-Desktop.bat all templated for D:\\ "
            "and C:\\Python314\\python.exe (the host Python)"
        ),
    },
    'operator_followup': (
        "D1 IS NOW CLOSED. The deploy is verified on a real microSD card on "
        "this host. The next OPEN_ITEMS are: (a) the research agent findings "
        "from the 6-area cross-program review (in flight, not yet reported), "
        "(b) any operator call on the 4 gauges based on the research, "
        "(c) the Tauri desktop build on the card if the operator wants a "
        "portable .exe, (d) the remaining OPEN_ITEMS from the original list."
    ),
    'changed_file_hashes': hashes,
    'post_change_verification': {
        'pytest': '50 passed, 1 skipped, 0 failed',
        'verify_chain_card': 'MATCH (block 2738, root 5d8bf674...)',
        'verify_chain_host': 'MATCH (will be re-run after this seal)',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
