"""Seal the Gmail Takeout audit run (2026-07-20) to the Merkle chain.

Re-runs the deterministic audit pipeline over the 93 split-inbox files
in-process (no md parsing), extracts the four-gate verdict for each,
and appends one ledger block per file plus a batch-summary block.

No network, no LLM. Each block is an immutable fact:
    event_type = GMAIL_AUDIT_RESULT_2026_07_20
    payload    = {filename, status, deceptionProbability, structuralFlag,
                 bbfbCompliant, aclDemandIssued, patternsCount, warnings}

Run from 02_Technical:
    python 04_Validation/scripts/seal_gmail_audit_2026_07_20.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")
TECH = ROOT / "02_Technical"
sys.path.insert(0, str(TECH))

from src.io.pipeline import process_directory
from src.agents.ledger_seal_agent import LedgerSealAgent


SPLIT_INBOX = ROOT / "data" / "gmail_split_inbox"
OUTBOX = ROOT / "data" / "gmail_audit_outbox"
EVENT = "GMAIL_AUDIT_RESULT_2026_07_20"
SUMMARY_EVENT = "GMAIL_AUDIT_BATCH_SEALED_2026_07_20"


def verdict_from_report(r):
    dr = r.deception_report or {}
    bbfb = r.bbfb_report or {}
    patterns = dr.get("detectedPatterns", []) or []
    return {
        "filename": r.filename,
        "status": "success",
        "textLength": r.text_length,
        "deceptionProbability": round(dr.get("deceptionProbability", 0.0), 4),
        "structuralDeceptionFlag": bool(dr.get("structuralDeceptionFlag", False)),
        "patternsDetected": len(patterns),
        "patternIds": [p.get("patternId") for p in patterns[:8]],
        "bbfbEvaluated": bool(r.bbfb_report),
        "bbfbCompliant": bool(bbfb.get("overallCompliant", True)) if bbfb else None,
        "aclDemandIssued": bool(r.acl_demand),
        "warnings": list(r.warnings or []),
    }


def main():
    print("=== SEAL: Gmail audit run 2026-07-20 ===")
    results = process_directory(SPLIT_INBOX, OUTBOX, [".md"])
    success = [r for r in results if r.status == "success" and r.report]
    timeouts = [r for r in results if r.status == "timeout"]
    errors = [r for r in results if r.status == "error"]
    print(f"  files audited : {len(results)}")
    print(f"  success      : {len(success)}")
    print(f"  timeouts     : {len(timeouts)}")
    print(f"  errors       : {len(errors)}")

    sealer = LedgerSealAgent()
    sealed = 0
    high_signal = []
    for r in results:
        if r.status != "success" or not r.report:
            continue
        v = verdict_from_report(r.report)
        sealer.seal_fact(EVENT, v)
        sealed += 1
        if v["structuralDeceptionFlag"] or v["aclDemandIssued"] or (
            v["bbfbCompliant"] is False
        ):
            high_signal.append(v)

    summary = {
        "runDate": "2026-07-20",
        "source": "Gmail Takeout (2 mboxes, 1069 parsed, 93 business kept)",
        "filesAudited": len(results),
        "success": len(success),
        "timeouts": len(timeouts),
        "errors": len(errors),
        "sealedBlocks": sealed,
        "highSignalCount": len(high_signal),
        "highSignalFiles": [h["filename"] for h in high_signal],
    }
    sealer.seal_fact(SUMMARY_EVENT, summary)
    print(f"  sealed blocks: {sealed} results + 1 summary = {sealed + 1}")
    print(f"  high-signal  : {len(high_signal)} (structural flag / ACL / BBFB non-compliant)")
    print(f"  high-signal files:")
    for h in high_signal:
        print(f"    - {h['filename']}")
        print(f"        deceptionP={h['deceptionProbability']:.2f} "
              f"struct={h['structuralDeceptionFlag']} "
              f"bbfbCompliant={h['bbfbCompliant']} "
              f"acl={h['aclDemandIssued']} patterns={h['patternIds'][:3]}")

    # verify the chain after sealing
    from src.io import vault_io
    stats = vault_io.merkle_stats()
    print(f"\n  chain after seal: blockCount={stats['blockCount']} "
          f"root={stats['merkleRoot'][:16]}...")

    out = ROOT / "04_Validation" / "gmail_audit_sealed_2026-07-20.json"
    json.dump({"summary": summary, "highSignal": high_signal}, open(out, "w"), indent=2)
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()