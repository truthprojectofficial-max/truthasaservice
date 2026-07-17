import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

# Hash every file changed in C1-C5
changed_files = [
    # C1 -- live Merkle root + refresh policy
    '04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt',
    # C2 -- IP file: v3.8 -> v3.9, 52 -> 54 patterns, severities, agentic REPL
    '04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt',
    # C3 -- maintenance plan: InventoryAgent, agentic REPL, current test counts
    '04_Validation/MAINTENANCE_PLAN.txt',
    # C4 (already covered in C2 + C3) + SPECS.txt v3.8/52 -> v3.9/54
    '04_Validation/SPECS.txt',
    '04_Validation/hardcopy/OPERATOR_MANUAL.txt',
    # C5 -- Section 7 added
    '00_Strategy/STRATEGY.md',
    # Latent fix in runtime
    '02_Technical/src/agents/orchestrator.py',
    # Live Merkle root refresh
    '04_Validation/YELLOW_RIBBON.md',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('OPEN_ITEMS_C1_C5_CLOSED_2026_07_12', {
    'open_items_closed': ['C1', 'C2', 'C3', 'C4', 'C5'],
    'C1_quick_reference_card': {
        'change': 'Live Merkle root refreshed (1801 -> 2504 blocks; root 96425dc0... -> 1739978a...). Added refresh policy: re-print when root changes, on operator handoff, or every 30 days.',
        'file': '04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt',
    },
    'C2_ip_audit': {
        'change': 'Audited INTELLECTUAL_PROPERTY_RIGHTS.txt against current build. Fixed: (a) v3.8 -> v3.9 references at lines 60-61, 246-253; (b) 52-pattern -> 54-pattern at lines 60-61, 131-142, 246-253; (c) pattern ID range DD-001 to DD-052 -> DD-001 to DD-054; (d) added the agentic REPL to the methodology list at line 67-68. Note: requirements.txt claim (line 124-129) is still accurate -- 10 packages, all present in 02_Technical/requirements.txt.',
        'file': '04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt',
    },
    'C3_maintenance_plan_reconciliation': {
        'change': 'MAINTENANCE_PLAN.txt was last refreshed when test counts were 28/28. Reconciled to current state: (a) added InventoryAgent to the operator tools list at the maintenance contract (line 351-352); (b) added the agentic REPL to the same list; (c) fixed stale test count references -- 3/3 boundary + 2/2 normalize + 22/22 smoke + 28/28 evaluation -> 3/3 boundary + 2/2 normalize + 27/27 smoke + 50/50 full suite + 1 skip-guard; (d) renumbered the weekly/quarterly/annual cycle steps to match the new test step; (e) fixed 52-pattern -> 54-pattern references; (f) replaced `python -m unittest` with `python -m pytest` to match pyproject.toml.',
        'file': '04_Validation/MAINTENANCE_PLAN.txt',
    },
    'C4_inventory_agent_documentation': {
        'change': 'Added InventoryAgent to the IP file (line 67-68 and the right-to-extend list at line 207-208) and to the maintenance plan (line 351-352). Added agentic REPL to both. The orchestrator itself lists five agents -- the InventoryAgent is reachable via the REPL or via direct import, not via the orchestrator; documented in the maintenance plan.',
        'files': ['04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt', '04_Validation/MAINTENANCE_PLAN.txt'],
    },
    'C5_strategy_section_7': {
        'change': 'Added Section 7 to STRATEGY.md -- "Status: Operational, Not Finished". The build is operational (every gate works, every test passes, every chain seals) but is not finished and is not meant to be finished. A frozen artefact decays; a maintained artefact evolves. The chain records the evolution. The section frames the build as a living artefact -- used, not displayed; maintained, not frozen; audited by a third party, not trusted on the operator word alone. Removed implicit v3.8 references throughout the file.',
        'file': '00_Strategy/STRATEGY.md',
    },
    'latent_fixes': {
        'orchestrator_docstring': '02_Technical/src/agents/orchestrator.py:10 -- "52-pattern deception scan" -> "54-pattern deception scan". The docstring was stale (the ontology is 3.9 / 54 patterns).',
        'yellow_ribbon_root': '04_Validation/YELLOW_RIBBON.md -- refreshed REF-5 and the live root to 2504 blocks / 1739978a...; updated the test count from 28/28 to 50/50 in the third-party audit checklist (line 192-197); refreshed the document header to reflect the A5 seal.',
        'operator_manual': '04_Validation/hardcopy/OPERATOR_MANUAL.txt -- "52-pattern" -> "54-pattern" + "v3.8" -> "v3.9" in the agent table and four-gates list.',
        'specs_sheet': '04_Validation/SPECS.txt -- F-05 52-pattern ontology v3.8 / 14 CRITICAL 32 HIGH 6 MEDIUM -> 54-pattern v3.9 / 15 CRITICAL 35 HIGH 4 MEDIUM (counts from the actual deception_ontology_data.py); NF-01 and NF-04 52-pattern -> 54-pattern; closing paragraph 52-pattern v3.8 -> 54-pattern v3.9.',
    },
    'audit_results': {
        'pytest': '50 passed, 1 skipped, 0 failed (no regressions from C1-C5 doc work)',
        'no_network_audit': 'PASS -- doc-only changes do not affect the runtime tree',
        'boundary_test': '3/3 -- the only src/ change was a docstring in orchestrator.py, no new imports',
    },
    'changed_file_hashes': hashes,
    'post_change_verification': {
        'v3.8_52pattern_in_04_Validation': '0 occurrences remaining (verified by grep)',
        'stale_test_count_in_04_Validation': '0 occurrences remaining (verified by grep)',
        'pytest': '50 passed, 1 skipped, 0 failed',
        'no_network_audit': 'PASS',
        'verify_chain': 'MATCH (will be re-run after this seal)',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
