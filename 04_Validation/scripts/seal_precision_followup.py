"""Seal DOCS_PRECISION_FOLLOWUP_2026_07_16 to add the laptop/SDXC
test-count distinction. The earlier STRATEGY_AMENDED_2026_07_16
and MAINTENANCE_PLAN_AMENDED_2026_07_16 (blocks 2798, 2799) said
"48 pass + 3 skip-guard" without naming the host. This seal
records the precision: 50 pass + 1 skip-guard on the laptop
(Tauri shell built); 48 pass + 3 skip-guard on a source-only
host (SDXC, fresh checkout, CI). The Ollama skip-guard survives
on every host.

2026-07-16. Order Get It Right."""

import sys
import os
import json
import hashlib
import importlib
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

payload = {
    "amendment_type": "docs_precision_followup",
    "amendment_chain": [
        "STRATEGY_AMENDED_2026_07_16 (block 2798) -- initial drift fix",
        "MAINTENANCE_PLAN_AMENDED_2026_07_16 (block 2799) -- initial drift fix",
        "DOCS_PRECISION_FOLLOWUP_2026_07_16 (this block) -- host-specific test count"
    ],
    "precision_added": {
        "laptop_test_count": "50 passed, 0 failed, 1 skipped (Ollama tool-calling only)",
        "sdxc_or_source_only_test_count": "48 passed, 0 failed, 3 skipped (2 Tauri-build + 1 Ollama)",
        "determinant": "whether the Tauri shell has been built (presence of 02_Technical/tauri-shell/target/release/order-get-it-right.exe)",
        "ollama_skip_survives_on_every_host": True
    },
    "live_evidence": {
        "laptop_tauri_binary": {
            "path": r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical\tauri-shell\target\release\order-get-it-right.exe",
            "exists": True,
            "bytes": 4847104,
            "mtime_utc": "2026-07-12 14:21"
        },
        "sdxc_tauri_binary": {
            "path": r"D:\OrderGetItRight\02_Technical\tauri-shell\target\release\order-get-it-right.exe",
            "exists": False,
            "expected_after_building": "npx tauri build in D:\\OrderGetItRight\\02_Technical\\tauri-shell"
        },
        "laptop_pytest_v_run": "50 passed, 1 skipped in 9.13s",
        "sdxc_pytest_v_run": "48 passed, 3 skipped in 16.73s"
    },
    "amended_files": {
        "00_Strategy/STRATEGY.md": {
            "new_sha256": sha256_of("00_Strategy/STRATEGY.md"),
            "old_sha256_at_initial_amend": "b9850dd7655adfbf78cf07f7d1a6e2958a310c3d6b73b4d2d7a3be67787f10e3"
        },
        "04_Validation/MAINTENANCE_PLAN.txt": {
            "new_sha256": sha256_of("04_Validation/MAINTENANCE_PLAN.txt"),
            "old_sha256_at_initial_amend": "0f93b6fbef5740eeedc7780344a46e4498d2a127365b386df2c19b503e7c4931"
        },
        "04_Validation/STAGE_PAPER_WEEKLY.txt": sha256_of("04_Validation/STAGE_PAPER_WEEKLY.txt"),
        "04_Validation/STAGE_PAPER_QUARTERLY.txt": sha256_of("04_Validation/STAGE_PAPER_QUARTERLY.txt"),
        "04_Validation/STAGE_PAPER_ANNUAL.txt": sha256_of("04_Validation/STAGE_PAPER_ANNUAL.txt"),
        "04_Validation/YELLOW_RIBBON.md": sha256_of("04_Validation/YELLOW_RIBBON.md"),
        "04_Validation/HANDOVER_TO_AUDITOR.md": sha256_of("04_Validation/HANDOVER_TO_AUDITOR.md"),
        "04_Validation/HANDOVER_TO_NEW_OPERATOR.md": sha256_of("04_Validation/HANDOVER_TO_NEW_OPERATOR.md"),
        "04_Validation/CONTEXT_WINDOW.md": sha256_of("04_Validation/CONTEXT_WINDOW.md")
    },
    "operator": "Justin Barnett",
    "session": "codex-on-Justo",
    "amended_at": now
}

print("=== Sealing DOCS_PRECISION_FOLLOWUP_2026_07_16 ===")
block = append_block("DOCS_PRECISION_FOLLOWUP_2026_07_16", payload)
print("  block index:", block.get("index"))
print("  block hash :", block.get("current_hash"))
print("  event_type :", block.get("event_type"))

print("\n=== Verifying chain ===")
import subprocess
res = subprocess.run(
    [sys.executable, "-m", "src.verify_chain"],
    cwd=TECHNICAL,
    capture_output=True, text=True
)
print(res.stdout[-1500:])

print("\nDone.")
