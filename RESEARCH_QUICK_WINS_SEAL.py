"""
Seal the research-driven quick wins to the Merkle chain.

Closes the HIGH/MEDIUM severity findings from
04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md (Areas 1, 2, 4)
that are one-line or near-one-line fixes:

  * requirements.txt: bump fastapi>=0.118.3 and pydantic>=2.12.0 for
    explicit Python 3.14 support (Area 1, finding 1.1, HIGH).
  * deploy.ps1: $null guard on Get-Item -Force .LinkType so
    OneDrive cloud-only and UNC reparse points do not emit a
    misleading WARN (Area 2, finding 2.1, MEDIUM-HIGH).
  * tauri.conf.json: add webviewInstallMode.downloadBootstrapper
    so the MSI can bootstrap WebView2 on hosts that lack it
    (Area 4, finding 4.2 / 4.8, MEDIUM).

Operator explicitly excluded gauge changes (constants.py) and
the Ollama model swap from this session; those remain OPEN_ITEMS
for operator-driven calls.

Sealed as block N (one block after the latest host block).
"""
import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

changed_files = [
    '02_Technical/requirements.txt',
    'deploy/deploy.ps1',
    '02_Technical/tauri-shell/tauri.conf.json',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('OPEN_ITEMS_RESEARCH_QUICK_WINS_2026_07_12', {
    'open_items': ['A_research_quick_wins'],
    'context': (
        "Cross-program compatibility research report landed in this "
        "session. Operator explicitly chose to apply the one-line "
        "fixes (requirements.txt, deploy.ps1, tauri.conf.json) "
        "and to leave the gauge adjustments and Ollama model swap "
        "out of scope. Operator's framing: 'its about getting it "
        "right not right now'."
    ),
    'fix_1_requirements_python_314': {
        'file': '02_Technical/requirements.txt',
        'change': (
            "fastapi>=0.115.0 -> fastapi>=0.118.3 and pydantic>=2.8.0 "
            "-> pydantic>=2.12.0. Only 0.118.3+ and 2.12.0+ have "
            "explicit Python 3.14 support in their test matrices. "
            "A fresh pip install on Python 3.14.6 with the old bounds "
            "would resolve to versions that pre-date the 3.14 "
            "support milestones. Source: FastAPI 0.118.3 release "
            "notes (2025-10-10), pydantic 2.12.0 changelog."
        ),
        'severity_fixed': 'HIGH',
    },
    'fix_2_deploy_onedrive_unc_guard': {
        'file': 'deploy/deploy.ps1',
        'change': (
            "Get-Item -Force .LinkType may return $null on OneDrive "
            "Files On-Demand cloud-only paths and UNC reparse points. "
            "The previous code did .LinkType -in @('SymbolicLink','Junction') "
            "which on a $null .LinkType falls through to the misleading "
            "'real directory' WARN branch. The fix routes the value "
            "through a separate $DetectedLinkType variable and tests "
            "for $null before the -in check."
        ),
        'severity_fixed': 'MEDIUM-HIGH',
    },
    'fix_3_tauri_webview_bootstrapper': {
        'file': '02_Technical/tauri-shell/tauri.conf.json',
        'change': (
            "Added bundle.windows.webviewInstallMode = "
            "{type: 'downloadBootstrapper'} so the Tauri installer "
            "can fetch the WebView2 bootstrapper on hosts that lack "
            "WebView2 (Win 10 hosts without Edge / WebView2 "
            "preinstalled, hosts with Edge auto-updates disabled "
            "by GPO). The 2 MB bootstrapper is downloaded at install "
            "time. Win 11 24H2 hosts are unaffected (WebView2 is "
            "preinstalled)."
        ),
        'severity_fixed': 'MEDIUM',
    },
    'audit_results': {
        'pytest': '60 passed, 1 skipped, 0 failed (50 prior + 10 new canonical-JSON)',
        'a5_dry_run_tests': '4/4 PASS (the $null guard did not break the dry-run JSON-report contract)',
        'no_network_audit': 'PASS -- 40 .py files under 02_Technical/src, all CLEAN',
        'boundary_test': '3/3 PASS (canonical.py docstring reworded to avoid hardcoded path literals)',
        'verify_chain': 'MATCH (will be re-run after this seal)',
    },
    'out_of_scope_this_session': {
        'gauges': (
            "Operator decision: leave SHANNON_ANOMALY_THRESHOLD=4.5, "
            "DECEPTION_PROBABILITY_VETO=0.75 unchanged. Research "
            "recommended tightening to 4.0 and 0.65 respectively, "
            "but gauges are operator policy. OPEN for operator call."
        ),
        'ollama_model_swap': (
            "Operator decision: do the qwen2:1.5b -> qwen3:1.7b "
            "swap out of session. Operator framing: 'its about "
            "getting it right not right now'."
        ),
        'canonical_json_helper': (
            "Sealed as the NEXT block (its own seal, not part of A). "
            "Larger engineering change: new module + 3 integration "
            "sites + 10 new regression tests."
        ),
    },
    'changed_file_hashes': hashes,
    'post_change_verification': {
        'pytest': '60 passed, 1 skipped, 0 failed',
        'no_network_audit': 'PASS',
        'verify_chain': 'MATCH (will be re-run after this seal)',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
