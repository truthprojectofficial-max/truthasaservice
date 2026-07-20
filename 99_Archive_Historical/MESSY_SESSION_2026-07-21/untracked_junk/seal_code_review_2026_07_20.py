"""Seal CODE_REVIEW_SEALED_2026_07_20 to the Merkle chain.

Records the 2026-07-20 second-pass code review: the six findings (two
HIGH/MEDIUM bugs fixed in the job-journal append path, one LOW comment
fix, three ACCEPTED-as-is), the SHA-256 of every changed file and every
new doc, and the before/after chain state.

Run from the project root:

    python 04_Validation/scripts/seal_code_review_2026_07_20.py

2026-07-20. Order Get It Right. Cline (act mode), at the operator's
request. Second pass: review -> fix -> regression test -> docs -> seal.
"""

import sys
import os
import hashlib
import subprocess
from datetime import datetime, timezone

PROJECT_ROOT = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
TECHNICAL = os.path.join(PROJECT_ROOT, "02_Technical")
if TECHNICAL not in sys.path:
    sys.path.insert(0, TECHNICAL)

from src.io.vault_io import append_block, merkle_stats


def sha256_of(rel_path):
    p = os.path.join(PROJECT_ROOT, rel_path)
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


before = merkle_stats()
before_count = before["blockCount"]
before_root = before["merkleRoot"]
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

payload = {
    "review_type": "second_pass_code_review",
    "review_date": "2026-07-20",
    "reviewer": "Cline (act mode)",
    "operator": "Justin Barnett",
    "scope": "vault_io (facts chain + job journal), server/app lifespan, session_tracker, evidence_parser, real_options_lattice, bbfb_engine",
    "findings": {
        "F1_job_append_unlocked": {"severity": "HIGH", "file": "src/io/vault_io.py append_job_upsert", "root_cause": "critical section had no cross-process lock; same race that forked facts chain at block 25250", "fix": "_file_lock refactor + new _job_append_lock wraps whole upsert", "test": "test_concurrent_job_upserts_do_not_lose_state", "status": "FIXED"},
        "F2_job_tail_count_never_advanced": {"severity": "MEDIUM", "file": "src/io/vault_io.py append_job_upsert", "root_cause": "tail jobCount propagated stale; never incremented on new-job upsert (test caught 1 != 16)", "fix": "recompute tail jobCount from _materialise_job_registry() inside lock", "test": "test_concurrent_job_upserts_do_not_lose_state", "status": "FIXED"},
        "F3_app_lifespan_comment_wrong": {"severity": "LOW", "file": "src/server/app.py _lifespan", "root_cause": "comment claimed race would leave chain 'still verify but missing blocks'; actually FORKED it", "fix": "rewrote comment to reflect lock fix and real failure mode", "status": "FIXED"},
        "F4_session_tracker_unlocked": {"severity": "NEGLIGIBLE", "file": "src/server/session_tracker.py", "decision": "left as-is; best-effort by design; documented in care manual", "status": "ACCEPTED"},
        "F5_warranty_ratio_zero_default": {"severity": "NONE", "file": "src/engines/bbfb_engine.py", "decision": "intended conservative gate; no failure data => cannot assert warranty adequacy", "status": "ACCEPTED"},
        "F6_lattice_evidence_math": {"severity": "NONE", "file": "real_options_lattice.py, evidence_parser.py", "decision": "CRR standard; _safe_ratio + _clamp correct; deterministic regex", "status": "SOUND"},
    },
    "changed_files": {
        "02_Technical/src/io/vault_io.py": sha256_of("02_Technical/src/io/vault_io.py"),
        "02_Technical/src/server/app.py": sha256_of("02_Technical/src/server/app.py"),
        "tests/test_job_journal.py": sha256_of("tests/test_job_journal.py"),
    },
    "new_docs": {
        "04_Validation/INSTRUCTION_AND_CARE_MANUAL_2026-07-20.md": sha256_of("04_Validation/INSTRUCTION_AND_CARE_MANUAL_2026-07-20.md"),
        "04_Validation/HANDOVER_NEXT_SESSION_2026-07-20.md": sha256_of("04_Validation/HANDOVER_NEXT_SESSION_2026-07-20.md"),
        "04_Validation/REVIEW_AND_SEAL_2026-07-20.md": sha256_of("04_Validation/REVIEW_AND_SEAL_2026-07-20.md"),
    },
    "test_result": {"fast_suite": "63 passed (vault_journal, job_journal, vault_reseed_guard, smoke, evidence_parser, f7_deep_lattice_wired, f7_spec_value_curve)", "new_regression_test": "FAILED before fix (tail jobCount 1 != 16), PASSES after"},
    "chain_state": {"before_block_count": before_count, "before_merkle_root": before_root},
    "sealed_at": now,
}

print("=== Sealing CODE_REVIEW_SEALED_2026_07_20 ===")
print("  before block count :", before_count)
print("  before merkle root :", before_root)
block = append_block("CODE_REVIEW_SEALED_2026_07_20", payload)
print("  seal block index   :", block.get("index"))
print("  seal block hash    :", block.get("current_hash"))

print("\n=== Verifying chain after seal ===")
res = subprocess.run([sys.executable, "-m", "src.verify_chain"], cwd=TECHNICAL, capture_output=True, text=True)
print(res.stdout[-1200:])

after = merkle_stats()
print("\n=== After state ===")
print("  after block count  :", after["blockCount"])
print("  after merkle root  :", after["merkleRoot"])
print("\nDone. Record the seal block index/hash in 04_Validation/REVIEW_AND_SEAL_2026-07-20.md section 4.")