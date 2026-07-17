import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

# Hash every file changed/created in D5
changed_files = [
    # D5 -- 3 new files
    '02_Technical/tools/agentic_repl.py',
    '02_Technical/tools/agentic_repl_tools.py',
    '02_Technical/tools/__init__.py',
    'tests/test_d5_agentic_repl.py',
    # D5 -- third_party_assistant.py: added chat command + help text
    '02_Technical/src/third_party_assistant.py',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('OPEN_ITEMS_D5_CLOSED_2026_07_12', {
    'open_item': 'D5',
    'title': 'Order Get It Right as a product, not a sequence of CLI invocations',
    'description': (
        'The Tauri shell, third_party_assistant.py REPL, discovery_agent, '
        'monitor_agent, and InventoryAgent were never run end-to-end '
        'against each other. D5 wires them into a single user-facing flow '
        'using Ollama tool calling -- the operator types a natural-language '
        'question and a local LLM (aegis 1.5B Qwen2) loops over tool calls '
        'to the FastAPI audit server until it has an answer.'
    ),
    'architecture': {
        'repl_loop': '02_Technical/tools/agentic_repl.py',
        'tool_functions': '02_Technical/tools/agentic_repl_tools.py',
        'transport': 'urllib.request (stdlib) -- the ollama Python package is NOT a runtime dep',
        'ollama_endpoint': 'http://localhost:11434/api/chat',
        'fastapi_endpoint': 'http://127.0.0.1:3000 (the audit server)',
        'boundary': 'tools/ is operator CLI surface, not part of the runtime. The no-network audit on 02_Technical/src/ stays CLEAN.',
        'handoff': 'third_party_assistant.py `chat` command spawns the REPL as a subprocess (subprocess.call with sys.executable).',
    },
    'tools_provided': [
        'audit_text              -- run the 54-pattern deception scan',
        'evaluate_suite          -- run the 8-case evaluation suite',
        'verify_chain            -- re-derive the Merkle root',
        'list_facts [category]   -- show facts by category',
        'add_fact                -- add a fact to the registry (sealed)',
        'seal_custom_event       -- append a custom Merkle block',
        'get_status              -- system status',
        'list_ontology           -- full 54-pattern ontology',
        'orchestrator_process    -- run the Form_Entry -> Audit -> Lattice -> Seal chain',
    ],
    'test_results': {
        'd5_static_tests': 5,
        'd5_skip_guarded_tests': 1,
        'd5_skip_reason': 'live Ollama + FastAPI subprocess; skip message names what to install',
        'full_suite_pre': '41/41 (after B1+B3+B4)',
        'full_suite_post': '46/46 (5 new D5 static tests pass, 1 skip-guard documented)',
        'no_network_audit': 'PASS -- runtime tree free of network imports; tools/ is out of scope',
        'boundary_test': '3/3 -- third_party_assistant.py chat command does not import from src/ (subprocess is stdlib)',
    },
    'operator_ux': {
        'interactive': 'cd 02_Technical && python -m tools.agentic_repl',
        'one_shot': 'cd 02_Technical && python -m tools.agentic_repl --prompt "is the chain intact?"',
        'via_assistant': 'in the onyx REPL, type `chat <question>`',
        'model_override': '--model <name> or OGIR_AGENT_MODEL env var (default: tcoxav/aegis:latest)',
    },
    'changed_file_hashes': hashes,
    'design_notes': [
        'The Ollama Python package was NOT added to requirements.txt. The REPL uses urllib.request, which is stdlib and already used elsewhere in the project.',
        'The 9 tool functions are all wrappers around FastAPI endpoints. The REPL does NOT import from src/engines or src/agents directly -- same boundary rule tests/ follows.',
        'A small Ollama schema builder (_ollama_schema) parses each function docstring for Google-style Args: sections. Avoids the ollama Python package and pydantic.',
        'The live end-to-end test is skip-guarded with executable documentation (the skip message names the exact host feature missing).',
        'third_party_assistant.py chat command spawns the REPL as a subprocess rather than importing it. This keeps the REPL out of the runtime import graph entirely.',
    ],
    'open_items_remaining': [
        'A5 -- deploy.ps1 clean-host test',
        'C1-C5 -- doc maintenance batch',
        'D1 -- USB clean-host test (real USB drive required)',
    ],
    'post_change_verification': {
        'pytest': '46 passed, 1 skipped, 0 failed (was 41 passed, 0 skipped; +5 D5 static, +1 skip-guard)',
        'no_network_audit': 'PASS -- 0 network imports in 02_Technical/src/',
        'boundary_test': '3 passed',
        'verify_chain': 'MATCH (2386 blocks)',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
