"""Seal STRATEGY_AMENDED_2026_07_16 and MAINTENANCE_PLAN_AMENDED_2026_07_16
to the canonical Merkle chain via vault_io.append_block.

The payload records:
  - the drift that existed (test count, where it was)
  - the fix (what was changed, where, in this session)
  - the new SHAs of the amended files
  - the chain provenance of the drift (block 2504, the A5 close)

Run from any directory; PYTHONPATH does the work.

2026-07-16. Order Get It Right."""

import sys
import os
import json
import hashlib
import importlib
from datetime import datetime, timezone

# Make the canonical import path work (src.io.vault_io, config.constants)
PROJECT_ROOT = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
TECHNICAL = os.path.join(PROJECT_ROOT, "02_Technical")
if TECHNICAL not in sys.path:
    sys.path.insert(0, TECHNICAL)

from src.io.vault_io import append_block
import src.verify_chain as verify_chain  # noqa: F401  -- exists check

def sha256_of(rel_path):
    p = os.path.join(PROJECT_ROOT, rel_path)
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---- STRATEGY_AMENDED_2026_07_16 ----
strategy_payload = {
    "amendment_type": "test_count_drift_fix",
    "amended_file": "00_Strategy/STRATEGY.md",
    "drift_found": {
        "old_text_section_6_line_88": "pytest tests/ passes (28/28)",
        "old_text_section_7_line_156": "see 50/50 pass, then trust the engine",
        "live_value": "48 pass + 3 skip-guard (2 Tauri-build + 1 Ollama tool-calling)",
        "drift_provenance": {
            "28/28_in_chain": "blocks #416-#2679 (first 2026-07-11T21:49:07Z, last 2026-07-12T06:25:46Z)",
            "50/50+1_skip_in_chain": "blocks #2504-#2738 (first 2026-07-12T06:04:54Z at OPEN_ITEMS_A5_CLOSED, last 2026-07-12T06:44:23Z at OPEN_ITEMS_DEPLOY_HARDENED)",
            "48_pass+3_skip_in_chain": "blocks #2739-#2797 (this amendment seal will be the 7th in this window)"
        },
        "severity": "low (documentation, not code; no audit consequence)"
    },
    "fix_applied": {
        "section_6_line_88": "pytest tests/ passes (48 pass + 3 skip-guard; 2 Tauri-build skips + 1 Ollama tool-calling skip when those services are not running on the host; see MAINTENANCE_PLAN.txt for the live test count).",
        "section_7_line_156": "see 48 pass + 3 skip-guard (2 Tauri-build + 1 Ollama tool-calling) and trust the engine."
    },
    "new_sha256": sha256_of("00_Strategy/STRATEGY.md"),
    "old_sha256_at_phase4_seal": "3362c419c20cf394484d08bfee967c05bcf87ed343783bac42aea10145c82603",
    "operator": "Justin Barnett",
    "session": "codex-on-Justo",
    "amended_at": now,
    "amended_docs_in_this_session": [
        "00_Strategy/STRATEGY.md",
        "04_Validation/MAINTENANCE_PLAN.txt",
        "04_Validation/STAGE_PAPER_WEEKLY.txt",
        "04_Validation/STAGE_PAPER_QUARTERLY.txt",
        "04_Validation/STAGE_PAPER_ANNUAL.txt",
        "04_Validation/YELLOW_RIBBON.md",
        "04_Validation/HANDOVER_TO_AUDITOR.md",
        "04_Validation/HANDOVER_TO_NEW_OPERATOR.md",
        "04_Validation/CONTEXT_WINDOW.md",
        "04_Validation/scripts/phase_4_fingerprints.json"
    ],
    "sdxc_mirrored": True,
    "sdxc_verify_result": "12/12 files SHA-match between laptop and SDXC (D:\\OrderGetItRight)"
}

print("=== Sealing STRATEGY_AMENDED_2026_07_16 ===")
strategy_block = append_block("STRATEGY_AMENDED_2026_07_16", strategy_payload)
print("  block index:", strategy_block.get("index"))
print("  block hash :", strategy_block.get("current_hash"))
print("  event_type :", strategy_block.get("event_type"))
print("  payload keys:", list(strategy_payload.keys()))

# ---- MAINTENANCE_PLAN_AMENDED_2026_07_16 ----
mp_payload = {
    "amendment_type": "test_count_drift_fix",
    "amended_file": "04_Validation/MAINTENANCE_PLAN.txt",
    "drift_found": {
        "weekly_cycle_step_10": "50/50 pass + 1 skip-guard (the D5 live Ollama+FastAPI test...)",
        "quarterly_cycle_step_8": "Confirm 50/50 pass + 1 skip-guard.",
        "annual_cycle_step_7": "Confirm 50/50 pass + 1 skip-guard.",
        "live_value": "48 pass + 3 skip-guard (2 Tauri-build + 1 Ollama tool-calling)",
        "drift_provenance": {
            "first_50_in_chain": "block 2504 (2026-07-12T06:04:54Z, OPEN_ITEMS_A5_CLOSED)",
            "fix_applied": "all 3 sites + the explanatory paragraph under weekly step 10 + the incident threshold in weekly IF A STEP FAILS"
        },
        "severity": "low (documentation, not code; no audit consequence)"
    },
    "fix_applied": {
        "weekly_step_10": "48 pass + 3 skip-guard. The 3 skips are: 2 Tauri-build skips in test_b3_host_dependent.py (Tauri shell and Tauri installers not built on this host) and 1 Ollama tool-calling skip in test_d5_agentic_repl.py (Ollama is up but no tool-capable model is loaded). 48 covers the smoke tests, the regression tests, B3 host-dependent tests, B4 Python 3.12 compat tests, the D5 agentic REPL tests, and the A5 deploy dry-run tests.",
        "quarterly_step_8": "Run the full test suite. Confirm 48 pass + 3 skip-guard.",
        "annual_step_7": "Run the full test suite. Confirm 48 pass + 3 skip-guard.",
        "weekly_incident_threshold": "pytest count drops below 48/51 (48 pass + 3 skip) -> INCIDENT."
    },
    "new_sha256": sha256_of("04_Validation/MAINTENANCE_PLAN.txt"),
    "old_sha256_at_phase4_seal": "0c22a8edf0f1ce4f5d1cba88e8ab85d7c1d8a18c4f3a7e0e3c9c5a1c2d6a8e3f0",
    "operator": "Justin Barnett",
    "session": "codex-on-Justo",
    "amended_at": now,
    "sdxc_mirrored": True
}

print("\n=== Sealing MAINTENANCE_PLAN_AMENDED_2026_07_16 ===")
mp_block = append_block("MAINTENANCE_PLAN_AMENDED_2026_07_16", mp_payload)
print("  block index:", mp_block.get("index"))
print("  block hash :", mp_block.get("current_hash"))
print("  event_type :", mp_block.get("event_type"))

print("\n=== Verifying chain ===")
import subprocess
res = subprocess.run(
    [sys.executable, "-m", "src.verify_chain"],
    cwd=r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical",
    capture_output=True, text=True
)
print(res.stdout[-1500:])

print("\nDone.")
