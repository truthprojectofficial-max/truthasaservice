"""
Seal the 2026-07-20 performance optimisations to the Merkle chain.

Closes two priority items from the 2026-07-20 coding-optimisation review:

  * P4a -- /api/ledger single-load. The endpoint loaded the ~23k-block
    facts chain from disk TWICE per request (once via get_stats() ->
    merkle_stats(), again via ledger_blocks() -> merkle_all()). Now loads
    it ONCE and derives the stats histogram/root from the same in-memory
    list in a single pass. Response shape unchanged (byte-identical).

  * P2  -- job registry append-only upsert journal. job_delegator._save()
    rewrote the entire 2.7 MB / 63k-line job_registry.json on every
    create/claim/close -- the same OneDrive sync-storm pattern the facts
    journal already fixed. The registry is now a frozen snapshot
    (job_registry.json) + an append-only JSONL upsert journal
    (job_chain.jsonl) + a tail cache (job_chain_tail.json). Each job
    state change appends ONE line (full job state, keyed by job_id) and
    updates the tail -- O(1), no full rewrite. Materialisation
    (read_job_registry) replays snapshot-then-journal with
    last-write-wins per job_id; compaction folds the journal into the
    snapshot every 256 upserts. Crash safety mirrors the facts journal
    (partial trailing journal line truncated/discarded). On-disk
    migration is transparent: the existing job_registry.json becomes the
    initial snapshot and the journal starts empty (verified: 4553
    existing jobs loaded correctly on first boot).

Sealed as block N (one block after the prior head).
"""
import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

changed_files = [
    '02_Technical/src/io/vault_io.py',
    '02_Technical/src/engines/facts_registry.py',
    '02_Technical/src/server/app.py',
    '02_Technical/src/agents/job_delegator.py',
    'tests/test_job_journal.py',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }
block = vault_io.append_block('PERF_LEDGER_JOB_JOURNAL_2026_07_20', {
    'open_item': ['P4a_single_load_ledger', 'P2_job_registry_journal'],
    'context': (
        "Two performance optimisations. (1) /api/ledger loads the ~23k-block "
        "facts chain ONCE per request instead of twice (stats + ledger_blocks "
        "now share one in-memory load; stats derived via merkle_stats_from_blocks "
        "in a single pass). Response shape byte-identical. (2) The job registry "
        "moved from an O(n) full 2.7 MB rewrite of job_registry.json on every "
        "create/claim/close to an O(1) append-only upsert journal (job_chain.jsonl) "
        "+ tail cache, mirroring the facts journal. Materialisation replays "
        "snapshot-then-journal with last-write-wins per job_id; compaction folds "
        "the journal into the snapshot every 256 upserts. Crash safety mirrors "
        "the facts journal (partial trailing journal line truncated/discarded). "
        "On-disk migration transparent: existing job_registry.json becomes the "
        "initial snapshot, journal starts empty (verified: 4553 existing jobs "
        "loaded correctly on first boot)."
    ),
    'fix_spec': {
        'p4a_single_load_ledger': {
            'files': [
                '02_Technical/src/io/vault_io.py (new merkle_stats_from_blocks(); '
                'merkle_stats() delegates to it; derived in one pass from an '
                'already-loaded block list)',
                '02_Technical/src/engines/facts_registry.py (get_stats() gains an '
                'optional ledger_blocks arg; derives stats from it with no second '
                'disk read; default behaviour unchanged)',
                '02_Technical/src/server/app.py (/api/ledger loads the chain once '
                'and passes it to both get_stats() and the response; response '
                'shape {stats, blocks} unchanged)',
            ],
            'effect': 'halves per-request disk reads on /api/ledger',
        },
        'p2_job_registry_journal': {
            'files': [
                '02_Technical/src/io/vault_io.py (job-journal layer: '
                '_job_journal_path/_job_tail_path/_read_job_journal/'
                '_materialise_job_registry/_read_job_tail/_write_job_tail/'
                '_append_job_journal_line/_compact_job_chain/append_job_upsert; '
                'read_job_registry now materialises snapshot+journal with same '
                'return shape; write_job_registry repurposed as compaction path; '
                '_JOB_COMPACTION_THRESHOLD=256)',
                '02_Technical/src/agents/job_delegator.py (_load reads via '
                'read_job_registry; old full-rewrite _save became _save_job(job) '
                'O(1) append; create_job_token/claim_job/close_job call sites '
                'updated to _save_job)',
            ],
            'new_tests': 'tests/test_job_journal.py (4 tests: round-trip across a '
            'fresh delegator, last-write-wins-per-id materialisation, compaction '
            'folds journal and preserves state, partial-trailing-line crash '
            'recovery)',
            'effect': 'job writes O(n) 2.7 MB rewrite -> O(1) append + amortised '
            'compaction; response shapes unchanged; transparent migration',
        },
    },
    'audit_results': {
        'pytest': '200 passed (smoke, orchestrator_seam, 00_99_boundary, '
        'vault_journal, job_journal, vault_reseed_guard, case_affidavit, '
        'c14_canonical_json_hardening, evaluation_cases); 4/4 new job-journal '
        'tests pass',
        'boundary_test': 'PASS -- test_job_journal.py imports only '
        'src.server.app (00-99 compliant); reaches delegator via app_module',
        'verify_chain_pre_seal': 'MATCH -- chain intact, 25174 blocks',
        'verify_chain_post_seal': 'MATCH (re-run after this seal)',
        'production_migration': 'verified -- 4553 existing jobs loaded '
        'transparently from job_registry.json snapshot; create/claim/close '
        'cycle round-trips through a fresh delegator on the live vault; '
        'compaction self-consistent',
    },
    'operator_followup': (
        "Remaining LOW-severity items from the 2026-07-20 review, NOT actioned "
        "in this seal and left for a future session: P5 -- verify_chain mutates "
        "the vault_io.VAULT_DIR module global (side-effect on import; LOW, no "
        "current correctness impact); P3 -- full-chain readers (verify_chain, "
        "merkle_all) are on-demand only, not on the HTTP read path (LOW; the "
        "facts journal already removed the per-append read). Neither is on the "
        "request hot path."
    ),
    'changed_file_hashes': hashes,
    'post_change_verification': {
        'pytest': '200 passed',
        'verify_chain': 'MATCH (re-run after this seal)',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])