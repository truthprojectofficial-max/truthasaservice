import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  count:', pre['blockCount'])

# Hash every file touched by the model-swap decision
changed_files = [
    '02_Technical/tools/agentic_repl.py',
    'tests/test_d5_agentic_repl.py',
    '04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('MODEL_SWAP_DECISION_2026_07_12', {
    'session': '2026-07-12',
    'title': 'Agentic REPL default model decision',
    'description': (
        'Operator evaluated swapping the agentic REPL default model to '
        'qwen2.5-coder:7b. The swap was rejected because Ollama native pulls '
        'fail/revert on this host, the .ollama directory contains unrelated '
        'tool state that makes paths unreliable, and the model must appear in '
        'ollama list without manual manifest hacks. The project therefore '
        'retains tcoxav/aegis:latest (1.5B Qwen2, tool-calling capable) as '
        'the default. Larger models remain selectable via --model or '
        'OGIR_AGENT_MODEL once they are actually present in Ollama.'
    ),
    'default_model': 'tcoxav/aegis:latest',
    'rejected_model': 'qwen2.5-coder:7b',
    'rejection_reasons': [
        'Ollama pull fails/reverts for 7B downloads on this host',
        '.ollama directory is polluted with non-Ollama files, making direct blob/manifest placement unsafe',
        'Operator policy: model must appear in ollama list natively; manual GGUF/Modelfile workarounds are not acceptable',
    ],
    'changed_file_hashes': hashes,
    'test_results': {
        'pytest_d5': '6 items: 5 passed, 1 skipped (FastAPI server not up in first run)',
        'pytest_d5_live': '1 passed (with FastAPI server up; model called verify_chain)',
        'full_pytest': '61 passed, 1 warning (0 failed)',
        'no_network_audit': 'PASS -- 0 network imports in runtime source tree',
        'boundary_test': '3 passed',
        'verify_chain': 'MATCH',
    },
})

post = vault_io.merkle_stats()
print('SEAL block:', block['index'])
print('POST count:', post['blockCount'])
print('MATCH:', int.from_bytes(bytes.fromhex(block['current_hash']), 'big') == int.from_bytes(bytes.fromhex(post['merkleRoot']), 'big'))
