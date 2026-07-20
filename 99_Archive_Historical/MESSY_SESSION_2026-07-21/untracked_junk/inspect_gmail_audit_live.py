"""Inspect a fresh Gmail audit run and print the verdict distribution.

Reads the most recent audit results from the outbox md reports and reports
the deception-probability distribution, the top-10 most-suspicious files,
files with detected patterns, BBFB evaluations, ACL demands, and warnings.

Usage: python 04_Validation/scripts/inspect_gmail_audit_live.py [outbox]
"""
import re
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")
OUTBOX = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "gmail_audit_outbox"


def parse_md(p: Path):
    t = p.read_text(encoding="utf-8", errors="replace")
    def grab(pat):
        m = re.search(pat, t)
        return m.group(1) if m else None
    src = grab(r"Source File\*\*: `([^`]+)`")
    prob = grab(r"Deception Probability \| ([\d.]+)%")
    struct = "TRUE" if "Structural Deception Flag | TRUE" in t else "FALSE"
    pat_section = t.split("Matched Deception Patterns")
    patterns = []
    if len(pat_section) > 1:
        for line in pat_section[1].splitlines():
            m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
            if m and m.group(1).strip() not in ("ID", "---"):
                patterns.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
    bbfb = None
    if "BBFB" in t or "Buy Before" in t or "Buy-Back" in t:
        m = re.search(r"Overall Compliant[:\|]\s*(\w+)", t)
        bbfb = m.group(1) if m else ("evaluated" if "BBFB" in t else None)
    acl = "TRUE" if "ACL Demand" in t and "TRUE" in t.split("ACL Demand")[1][:80] else "FALSE"
    warnings = [l.strip("- ").strip() for l in t.split("## Warnings")[1].splitlines()
                if l.strip().startswith("-")] if "## Warnings" in t else []
    return {
        "filename": src,
        "deceptionProbability": float(prob) / 100.0 if prob else 0.0,
        "structuralDeceptionFlag": struct == "TRUE",
        "patterns": patterns,
        "bbfb": bbfb,
        "acl": acl == "TRUE",
        "warnings": warnings,
    }


def main():
    mds = sorted(OUTBOX.glob("*.md"))
    if not mds:
        print(f"No .md reports in {OUTBOX}")
        return
    results = [parse_md(p) for p in mds]
    results = [r for r in results if r["filename"]]
    print(f"=== GMAIL AUDIT VERDICT INSPECTION (live) ===")
    print(f"reports parsed: {len(results)}\n")

    probs = [r["deceptionProbability"] for r in results]
    buckets = [(0.0, 0.1), (0.1, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.01)]
    labels = ["0-10% (clean)", "10-25% (low)", "25-50% (moderate)", "50-75% (elevated)", "75-100% (high)"]
    print("Deception-probability distribution:")
    for (lo, hi), lab in zip(buckets, labels):
        n = sum(1 for p in probs if lo <= p < hi)
        print(f"  {lab:22} {n:3d}  {'#'*n}")
    print(f"  mean: {sum(probs)/len(probs):.3f}  max: {max(probs):.3f}  min: {min(probs):.3f}\n")

    print("Top 12 most-suspicious files (by deception probability):")
    top = sorted(results, key=lambda r: r["deceptionProbability"], reverse=True)[:12]
    for r in top:
        p = r["deceptionProbability"]
        print(f"  {p*100:5.1f}%  struct={str(r['structuralDeceptionFlag']):5} "
              f"patterns={len(r['patterns']):2}  {(r['filename'] or '')[:65]}")
        for pid, pname, sev in r["patterns"][:3]:
            print(f"           {pid}: {pname[:50]} [{sev}]")
    print()

    flagged = [r for r in results if r["patterns"]]
    print(f"Files with >=1 detected deception pattern: {len(flagged)}")
    all_pids = Counter()
    for r in flagged:
        for pid, pname, sev in r["patterns"]:
            all_pids[pid] += 1
    if all_pids:
        print("Pattern frequency across flagged files:")
        for pid, c in all_pids.most_common():
            print(f"  {c:3d}  {pid}")
    print()

    struct_true = [r for r in results if r["structuralDeceptionFlag"]]
    print(f"Files with STRUCTURAL DECEPTION FLAG = TRUE: {len(struct_true)}")
    for r in struct_true:
        print(f"  {r['deceptionProbability']*100:.1f}%  {r['filename']}")
    print()

    bbfb_files = [r for r in results if r["bbfb"]]
    print(f"BBFB evaluations: {len(bbfb_files)}")
    for r in bbfb_files:
        print(f"  compliant={r['bbfb']}  {r['filename'][:65]}")
    print()

    print(f"ACL demands issued: {sum(1 for r in results if r['acl'])}")
    warn_files = [r for r in results if r["warnings"]]
    print(f"Files with pipeline warnings: {len(warn_files)}")
    for r in warn_files[:8]:
        print(f"  {r['filename'][:55]}: {r['warnings'][:2]}")


if __name__ == "__main__":
    main()