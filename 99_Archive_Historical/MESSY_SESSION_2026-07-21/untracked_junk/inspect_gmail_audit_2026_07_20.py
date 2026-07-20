"""Inspect the sealed Gmail audit verdicts (2026-07-20).

Reads the 93 sealed result blocks from the chain and reports the deception-
probability distribution, the top-10 most-suspicious files, any files with
detected patterns, and a per-file verdict table.
"""
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")
TECH = ROOT / "02_Technical"
sys.path.insert(0, str(TECH))

from src.io import vault_io

EVENT = "GMAIL_AUDIT_RESULT_2026_07_20"

def main():
    blocks = vault_io.merkle_all()
    results = [b for b in blocks if b.get("event_type") == EVENT]
    print(f"=== GMAIL AUDIT VERDICT INSPECTION ===")
    print(f"sealed result blocks: {len(results)}\n")

    probs = [b["payload"]["deceptionProbability"] for b in results]
    probs_sorted = sorted(probs, reverse=True)
    print("Deception-probability distribution:")
    buckets = [(0.0, 0.1), (0.1, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.01)]
    labels = ["0-10% (clean)", "10-25% (low)", "25-50% (moderate)", "50-75% (elevated)", "75-100% (high)"]
    for (lo, hi), lab in zip(buckets, labels):
        n = sum(1 for p in probs if lo <= p < hi)
        bar = "#" * n
        print(f"  {lab:22} {n:3d}  {bar}")
    print(f"  mean deception probability: {sum(probs)/len(probs):.3f}")
    print(f"  max: {max(probs):.3f}  min: {min(probs):.3f}\n")

    print("Top 10 most-suspicious files (by deception probability):")
    top = sorted(results, key=lambda b: b["payload"]["deceptionProbability"], reverse=True)[:10]
    for b in top:
        p = b["payload"]
        print(f"  {p['deceptionProbability']*100:5.1f}%  struct={str(p['structuralDeceptionFlag']):5} "
              f"patterns={p['patternsDetected']:2}  {p['filename'][:70]}")
        if p["patternIds"]:
            print(f"           patterns: {', '.join(p['patternIds'])}")
    print()

    flagged = [b for b in results if b["payload"]["patternsDetected"] > 0]
    print(f"Files with >=1 detected deception pattern: {len(flagged)}")
    all_pids = Counter()
    for b in flagged:
        for pid in b["payload"]["patternIds"]:
            all_pids[pid] += 1
    if all_pids:
        print("Pattern frequency across flagged files:")
        for pid, c in all_pids.most_common():
            print(f"  {c:3d}  {pid}")

    bbfb_files = [b for b in results if b["payload"]["bbfbEvaluated"]]
    print(f"\nFiles where BBFB engine evaluated product evidence: {len(bbfb_files)}")
    for b in bbfb_files[:15]:
        p = b["payload"]
        print(f"  compliant={str(p['bbfbCompliant']):5}  {p['filename'][:70]}")

    print(f"\nACL demands issued: {sum(1 for b in results if b['payload']['aclDemandIssued'])}")
    warnings = [b for b in results if b["payload"]["warnings"]]
    print(f"Files with pipeline warnings: {len(warnings)}")
    for b in warnings[:10]:
        print(f"  {b['payload']['filename'][:60]}: {b['payload']['warnings']}")

if __name__ == "__main__":
    main()