"""Verify that the post-amendment docs have the same SHA on the laptop
and on the SDXC. Run after amendments_mirror_to_sdxc.bat.

2026-07-16. Order Get It Right."""

import hashlib
import os
import sys

SRC = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
DST = r"D:\OrderGetItRight"

FILES = [
    "00_Strategy/STRATEGY.md",
    "04_Validation/MAINTENANCE_PLAN.txt",
    "04_Validation/STAGE_PAPER_DAILY.txt",
    "04_Validation/STAGE_PAPER_WEEKLY.txt",
    "04_Validation/STAGE_PAPER_MONTHLY.txt",
    "04_Validation/STAGE_PAPER_QUARTERLY.txt",
    "04_Validation/STAGE_PAPER_ANNUAL.txt",
    "04_Validation/YELLOW_RIBBON.md",
    "04_Validation/HANDOVER_TO_AUDITOR.md",
    "04_Validation/HANDOVER_TO_NEW_OPERATOR.md",
    "04_Validation/CONTEXT_WINDOW.md",
    "04_Validation/scripts/phase_4_fingerprints.json",
]

mismatch = 0
for f in FILES:
    src_path = os.path.join(SRC, f)
    dst_path = os.path.join(DST, f)
    if not os.path.exists(src_path):
        print(f"  MISSING SRC: {f}")
        mismatch += 1
        continue
    if not os.path.exists(dst_path):
        print(f"  MISSING DST: {f}")
        mismatch += 1
        continue
    a = hashlib.sha256(open(src_path, "rb").read()).hexdigest()
    b = hashlib.sha256(open(dst_path, "rb").read()).hexdigest()
    ok = a == b
    if not ok:
        mismatch += 1
    print(f"  {'OK ' if ok else 'XX '} {f} {a}")

print(f"\nResult: {len(FILES) - mismatch}/{len(FILES)} match. Mismatch: {mismatch}.")
sys.exit(0 if mismatch == 0 else 1)
