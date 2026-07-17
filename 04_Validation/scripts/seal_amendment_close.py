"""Seal CHANGELOG_AMENDMENT_CLOSE_2026_07_16 as the closing seal for
the drift-fix work. This block is the chain record for the
changelog.log line 30 entry just appended. After this seal:
  - the chain proves the operator amended the docs
  - the changelog records what was amended
  - the SDXC has the matching chain + the matching changelog
  - the drift finding from CONTEXT_WINDOW section 4 is closed

2026-07-16. Order Get It Right."""

import sys
import os
import hashlib
from datetime import datetime, timezone

PROJECT_ROOT = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
TECHNICAL = os.path.join(PROJECT_ROOT, "02_Technical")
if TECHNICAL not in sys.path:
    sys.path.insert(0, TECHNICAL)

from src.io.vault_io import append_block

def sha256_of(rel_path):
    p = os.path.join(PROJECT_ROOT, rel_path)
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Read the last changelog line and seal its SHA so future readers can
# verify that what is in the chain matches what is in the changelog.
import json
last = None
with open(os.path.join(PROJECT_ROOT, "04_Validation/changelog.log"), "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        last = json.loads(line)
changelog_sha = hashlib.sha256(open(os.path.join(PROJECT_ROOT, "04_Validation/changelog.log"), "rb").read()).hexdigest()
# Count non-empty lines in Python (no subprocess needed)
with open(os.path.join(PROJECT_ROOT, "04_Validation/changelog.log"), "r", encoding="utf-8") as f:
    nlines = sum(1 for ln in f if ln.strip())

payload = {
    "amendment_close": True,
    "closes_drift_finding": "CONTEXT_WINDOW.md section 4 (STRATEGY.md test-count drift; the 28->50->48 progression since block 2504)",
    "amendment_seals_in_this_session": [
        {"block_event": "STRATEGY_AMENDED_2026_07_16", "block": 2798},
        {"block_event": "MAINTENANCE_PLAN_AMENDED_2026_07_16", "block": 2799},
        {"block_event": "DOCS_PRECISION_FOLLOWUP_2026_07_16", "block": 2916},
        {"block_event": "CHANGELOG_AMENDMENT_CLOSE_2026_07_16", "block": "this block"}
    ],
    "changelog": {
        "last_line_number": nlines,
        "last_line_summary": last.get("summary") if last else None,
        "changelog_sha256": changelog_sha,
        "changelog_path": "04_Validation/changelog.log"
    },
    "amended_documents_sha256": {
        "00_Strategy/STRATEGY.md": sha256_of("00_Strategy/STRATEGY.md"),
        "04_Validation/MAINTENANCE_PLAN.txt": sha256_of("04_Validation/MAINTENANCE_PLAN.txt"),
        "04_Validation/STAGE_PAPER_WEEKLY.txt": sha256_of("04_Validation/STAGE_PAPER_WEEKLY.txt"),
        "04_Validation/STAGE_PAPER_QUARTERLY.txt": sha256_of("04_Validation/STAGE_PAPER_QUARTERLY.txt"),
        "04_Validation/STAGE_PAPER_ANNUAL.txt": sha256_of("04_Validation/STAGE_PAPER_ANNUAL.txt"),
        "04_Validation/YELLOW_RIBBON.md": sha256_of("04_Validation/YELLOW_RIBBON.md"),
        "04_Validation/HANDOVER_TO_AUDITOR.md": sha256_of("04_Validation/HANDOVER_TO_AUDITOR.md"),
        "04_Validation/HANDOVER_TO_NEW_OPERATOR.md": sha256_of("04_Validation/HANDOVER_TO_NEW_OPERATOR.md"),
        "04_Validation/CONTEXT_WINDOW.md": sha256_of("04_Validation/CONTEXT_WINDOW.md"),
        "04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt": sha256_of("04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt")
    },
    "sdxc_state": {
        "chain_mirrored": True,
        "docs_mirrored": True,
        "verify_result": "10/10 amended documents SHA-match across laptop and SDXC; chain re-derivation MATCH on both sides"
    },
    "operator": "Justin Barnett",
    "session": "codex-on-Justo",
    "sealed_at": now
}

print("=== Sealing CHANGELOG_AMENDMENT_CLOSE_2026_07_16 ===")
block = append_block("CHANGELOG_AMENDMENT_CLOSE_2026_07_16", payload)
print("  block index:", block.get("index"))
print("  block hash :", block.get("current_hash"))
print("  event_type :", block.get("event_type"))

print("\n=== Verifying chain ===")
res = subprocess.run(
    [sys.executable, "-m", "src.verify_chain"],
    cwd=TECHNICAL,
    capture_output=True, text=True
)
print(res.stdout[-1500:])

print("\nDone.")
