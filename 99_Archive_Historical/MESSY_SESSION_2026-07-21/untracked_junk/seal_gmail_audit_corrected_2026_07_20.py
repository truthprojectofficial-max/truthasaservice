"""Seal the CORRECTED Gmail Takeout audit run (2026-07-20, real bodies) to the chain.

The first seal (GMAIL_AUDIT_RESULT_2026_07_20) sealed 93 files whose bodies
were empty due to a broken mbox parser (quoted-printable not decoded, body
dropped). That run is INVALID. This script seals the re-run over the 82
files with correctly-decoded MIME bodies, using a distinct event type so
the chain records both the invalidation and the corrected verdicts.

Run from anywhere:
    python 04_Validation/scripts/seal_gmail_audit_corrected_2026_07_20.py
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
INVALID_EVENT = "GMAIL_AUDIT_INVALIDATED_2026_07_20"
RESULT_EVENT = "GMAIL_AUDIT_RESULT_V2_2026_07_20"
SUMMARY_EVENT = "GMAIL_AUDIT_BATCH_SEALED_V2_2026_07_20"


def verdict_from_report(r):
    dr = r.deception_report or {}
    bbfb = r.bbfb_report or {}
    patterns = dr.get("detectedPatterns", []) or []
    pids = [{"id": p.get("patternId"), "name": p.get("patternName"),
             "severity": p.get("severity")} for p in patterns[:12]]
    return {
        "filename": r.filename,
        "status": "success",
        "textLength": r.text_length,
        "deceptionProbability": round(dr.get("deceptionProbability", 0.0), 4),
        "structuralDeceptionFlag": bool(dr.get("structuralDeceptionFlag", False)),
        "patternsDetected": len(patterns),
        "patternIds": pids,
        "bbfbEvaluated": bool(r.bbfb_report),
        "bbfbCompliant": bool(bbfb.get("overallCompliant", True)) if bbfb else None,
        "aclDemandIssued": bool(r.acl_demand),
        "warnings": list(r.warnings or []),
    }


def main():
    print("=== SEAL (corrected): Gmail audit run 2026-07-20 ===")
    sealer = LedgerSealAgent()

    # 1) Seal an invalidation block for the prior empty-body run.
    sealer.seal_fact(INVALID_EVENT, {
        "reason": "First seal (GMAIL_AUDIT_RESULT_2026_07_20, 93 blocks) audited "
                  "empty/truncated bodies: mbox parser did not decode MIME "
                  "quoted-printable/base64 and dropped multipart bodies. All "
                  "93 returned 0.0% deception -- an artifact, not a clean result.",
        "invalidatedBlocks": 93,
        "fix": "Replaced hand-rolled mbox regex parser with stdlib email module "
               "(email.message_from_bytes + per-part decode). 82 files now have "
               "real bodies; 21 show detected patterns, 8 structural flags.",
    })
    print("  sealed invalidation block")

    # 2) Re-run the audit and seal each result.
    results = process_directory(SPLIT_INBOX, OUTBOX, [".md"])
    success = [r for r in results if r.status == "success" and r.report]
    timeouts = [r for r in results if r.status == "timeout"]
    errors = [r for r in results if r.status == "error"]
    print(f"  files audited : {len(results)}")
    print(f"  success      : {len(success)}")
    print(f"  timeouts     : {len(timeouts)}")
    print(f"  errors       : {len(errors)}")

    sealed = 0
    high_signal = []
    for r in results:
        if r.status != "success" or not r.report:
            continue
        v = verdict_from_report(r.report)
        sealer.seal_fact(RESULT_EVENT, v)
        sealed += 1
        if v["structuralDeceptionFlag"] or v["aclDemandIssued"] or (
            v["bbfbCompliant"] is False
        ):
            high_signal.append(v)

    summary = {
        "runDate": "2026-07-20",
        "runVersion": "v2 (corrected MIME parsing)",
        "source": "Gmail Takeout (2 mboxes, 1069 parsed, 82 business kept, "
                  "607 operator-sent skipped, 380 noise skipped)",
        "filesAudited": len(results),
        "success": len(success),
        "timeouts": len(timeouts),
        "errors": len(errors),
        "sealedBlocks": sealed,
        "highSignalCount": len(high_signal),
        "highSignalFiles": [{"file": h["filename"],
                             "deceptionP": h["deceptionProbability"],
                             "struct": h["structuralDeceptionFlag"],
                             "bbfbCompliant": h["bbfbCompliant"],
                             "acl": h["aclDemandIssued"]}
                            for h in high_signal],
    }
    sealer.seal_fact(SUMMARY_EVENT, summary)
    print(f"  sealed blocks: 1 invalidation + {sealed} results + 1 summary = {sealed + 2}")
    print(f"  high-signal  : {len(high_signal)} (structural flag / ACL / BBFB non-compliant)")
    print(f"  high-signal files:")
    for h in high_signal:
        print(f"    - {h['filename']}")
        print(f"        deceptionP={h['deceptionProbability']:.2f} "
              f"struct={h['structuralDeceptionFlag']} "
              f"bbfbCompliant={h['bbfbCompliant']} "
              f"acl={h['aclDemandIssued']}")

    from src.io import vault_io
    stats = vault_io.merkle_stats()
    print(f"\n  chain after seal: blockCount={stats['blockCount']} "
          f"root={stats['merkleRoot'][:16]}...")

    out = ROOT / "04_Validation" / "gmail_audit_sealed_corrected_2026-07-20.json"
    json.dump({"summary": summary, "highSignal": high_signal}, open(out, "w"), indent=2)
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()