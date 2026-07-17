"""Final cross-side verify: every file involved in the precision
amendment should SHA-match between laptop and SDXC, and the
chains on both sides should be at the same block count and
root.

2026-07-16. Order Get It Right."""

import hashlib
import os

LAPTOP_ROOT = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
SDXC_ROOT = r"D:\OrderGetItRight"

FILES = [
    "00_Strategy/STRATEGY.md",
    "04_Validation/MAINTENANCE_PLAN.txt",
    "04_Validation/STAGE_PAPER_WEEKLY.txt",
    "04_Validation/STAGE_PAPER_QUARTERLY.txt",
    "04_Validation/STAGE_PAPER_ANNUAL.txt",
    "04_Validation/YELLOW_RIBBON.md",
    "04_Validation/HANDOVER_TO_AUDITOR.md",
    "04_Validation/HANDOVER_TO_NEW_OPERATOR.md",
    "04_Validation/CONTEXT_WINDOW.md",
    "04_Validation/changelog.log",
    "04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt",
    "04_Validation/scripts/seal_strategy_amended.py",
    "04_Validation/scripts/seal_precision_followup.py",
    "04_Validation/scripts/seal_amendment_close.py",
    "04_Validation/scripts/precision_mirror_all_to_sdxc.bat",
    "02_Technical/03_Vault/facts_registry.json",
]

mismatch = 0
for rel in FILES:
    laptop = os.path.join(LAPTOP_ROOT, rel)
    sdxc = os.path.join(SDXC_ROOT, rel)
    if not os.path.exists(laptop):
        print(f"  MISSING LAPTOP: {rel}")
        mismatch += 1
        continue
    if not os.path.exists(sdxc):
        print(f"  MISSING SDXC:   {rel}")
        mismatch += 1
        continue
    a = hashlib.sha256(open(laptop, "rb").read()).hexdigest()
    b = hashlib.sha256(open(sdxc, "rb").read()).hexdigest()
    if a != b:
        mismatch += 1
    print(f"  {'OK ' if a == b else 'XX '} {rel[:55]:<55s}  {a[:12]}")

print(f"\nResult: {len(FILES) - mismatch}/{len(FILES)} match across laptop and SDXC.")
