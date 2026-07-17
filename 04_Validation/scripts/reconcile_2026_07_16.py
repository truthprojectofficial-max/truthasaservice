"""
Order Get It Right -- 2026-07-16 chain/changelog reconciliation classifier.

Pure read-only script. Walks every block in the Merkle vault, classifies it
by event_type and timestamp, identifies the gap between the last sealed
changelog entry and the current chain tip, and emits a JSON report to
04_Validation/scripts/reconcile_2026_07_16_report.json.

The report is consumed by RECONCILIATION_2026-07-16.md (the human-readable
paper) and by any later auditor who wants to verify the reconciliation
without re-running the classification.

Usage:
    python 04_Validation/scripts/reconcile_2026_07_16.py

No seal. No chain mutation. Read-only against facts_registry.json.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VAULT = PROJECT_ROOT / "02_Technical" / "03_Vault" / "facts_registry.json"
REPORT = Path(__file__).resolve().parent / "reconcile_2026_07_16_report.json"

# The last human-readable entry in 04_Validation/changelog.log is the
# B1_B3_B4 close at 2026-07-12T05:00:00Z, block 2270. That is the
# operator's documented cut-off. Anything after it is "the gap."
GAP_CUTOFF_ISO = "2026-07-12T05:00:00Z"


def classify_block(b):
    """Return (event_type, job_kind, is_named_closure, ts_dt)."""
    et = b.get("event_type", "?")
    payload = b.get("payload", {}) or {}
    if not isinstance(payload, dict):
        payload = {}

    job_kind = None
    if et in ("JOB_QUEUED", "JOB_CLAIMED", "JOB_COMPLETED", "JOB_REFUSED"):
        job_kind = (
            payload.get("job_kind")
            or payload.get("kind")
            or payload.get("job_type")
            or payload.get("type")
            or "unspecified"
        )

    is_named_closure = et.startswith("OPEN_ITEMS_") and et.endswith("_CLOSED")

    ts = b.get("timestamp", "")
    try:
        ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        ts_dt = None

    return et, job_kind, is_named_closure, ts_dt


def main():
    if not VAULT.exists():
        raise SystemExit(f"Vault not found: {VAULT}")

    data = json.loads(VAULT.read_text(encoding="utf-8"))
    blocks = data.get("blocks", [])
    merkle_root = data.get("merkle_root", "")

    print(f"Vault: {VAULT}")
    print(f"Total blocks: {len(blocks)}")
    print(f"Merkle root: {merkle_root}")
    print()

    # Whole-chain classification
    whole_type = Counter(b.get("event_type", "?") for b in blocks)

    # Find the gap
    gap_cutoff_dt = datetime.fromisoformat(GAP_CUTOFF_ISO.replace("Z", "+00:00"))
    in_gap = []
    pre_gap = []
    for b in blocks:
        et, _, _, ts_dt = classify_block(b)
        if ts_dt and ts_dt > gap_cutoff_dt:
            in_gap.append(b)
        else:
            pre_gap.append(b)

    gap_count = len(in_gap)
    gap_type = Counter(b.get("event_type", "?") for b in in_gap)

    # Job kind classification within the gap
    gap_job_kind = Counter()
    for b in in_gap:
        et, jk, _, _ = classify_block(b)
        if jk is not None:
            gap_job_kind[jk] += 1

    # Named closures within the gap
    named_closures = []
    for b in in_gap:
        et, _, is_named, _ = classify_block(b)
        if is_named:
            named_closures.append({
                "index": b["index"],
                "timestamp": b["timestamp"],
                "event_type": et,
                "current_hash": b.get("current_hash", ""),
                "previous_hash": b.get("previous_hash", ""),
                "summary_keys": sorted((b.get("payload") or {}).keys()),
            })

    # Group JOB_QUEUED + JOB_CLAIMED + JOB_COMPLETED by their natural
    # triplet (index 1, 2, 3 against the same job_id) where possible.
    # We can't always pair them; report the raw counts instead.
    # Also: find AUDIT_CYCLE_COMPLETE blocks in the gap, and the JOB_REFUSED
    # vs REFUSAL distinction.
    audit_cycles = [b for b in in_gap if b.get("event_type") == "AUDIT_CYCLE_COMPLETE"]
    refusals = [b for b in in_gap if b.get("event_type") == "REFUSAL"]
    job_refusals = [b for b in in_gap if b.get("event_type") == "JOB_REFUSED"]

    # The first and last block in the gap (timestamps + index)
    first_gap = in_gap[0] if in_gap else None
    last_gap = in_gap[-1] if in_gap else None

    # The last block in the pre-gap (the "boundary" the gap starts after)
    last_pre = pre_gap[-1] if pre_gap else None

    # Build the report
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "vault_path": str(VAULT),
        "merkle_root": merkle_root,
        "block_count_total": len(blocks),
        "gap_cutoff_iso": GAP_CUTOFF_ISO,
        "gap_block_count": gap_count,
        "gap_first_block": (
            {
                "index": first_gap["index"],
                "timestamp": first_gap["timestamp"],
                "event_type": first_gap["event_type"],
            }
            if first_gap else None
        ),
        "gap_last_block": (
            {
                "index": last_gap["index"],
                "timestamp": last_gap["timestamp"],
                "event_type": last_gap["event_type"],
            }
            if last_gap else None
        ),
        "pre_gap_boundary_block": (
            {
                "index": last_pre["index"],
                "timestamp": last_pre["timestamp"],
                "event_type": last_pre["event_type"],
            }
            if last_pre else None
        ),
        "whole_chain_event_types": dict(whole_type.most_common()),
        "gap_event_types": dict(gap_type.most_common()),
        "gap_job_kinds": dict(gap_job_kind.most_common()),
        "gap_named_closures": named_closures,
        "gap_audit_cycle_count": len(audit_cycles),
        "gap_refusal_count": len(refusals),
        "gap_job_refusal_count": len(job_refusals),
        "gap_assistant_started_count": sum(
            1 for b in in_gap if b.get("event_type") == "ASSISTANT_STARTED"
        ),
        "gap_fact_added_count": sum(
            1 for b in in_gap if b.get("event_type") == "FACT_ADDED"
        ),
    }

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    # Human print
    print("=" * 72)
    print("CHAIN / CHANGELOG RECONCILIATION -- 2026-07-16")
    print("=" * 72)
    print(f"Vault: {VAULT.name}")
    print(f"Total blocks: {len(blocks)}")
    print(f"Merkle root: {merkle_root}")
    print()
    print(f"Gap cut-off (last changelog entry): {GAP_CUTOFF_ISO}")
    print(f"Pre-gap boundary block:  #{last_pre['index']}  {last_pre['timestamp']}  {last_pre['event_type']}"
          if last_pre else "(none)")
    print(f"Gap blocks:              {gap_count}")
    print(f"Gap first block:         #{first_gap['index']}  {first_gap['timestamp']}  {first_gap['event_type']}"
          if first_gap else "(none)")
    print(f"Gap last block:          #{last_gap['index']}  {last_gap['timestamp']}  {last_gap['event_type']}"
          if last_gap else "(none)")
    print()
    print("Gap event types:")
    for k, v in gap_type.most_common():
        print(f"  {v:5d}  {k}")
    print()
    if gap_job_kind:
        print("Gap JOB_* job_kinds:")
        for k, v in gap_job_kind.most_common():
            print(f"  {v:5d}  {k}")
        print()
    if named_closures:
        print("Named OPEN_ITEMS_*_CLOSED in gap:")
        for nc in named_closures:
            print(f"  block {nc['index']}  {nc['timestamp']}  {nc['event_type']}")
            print(f"    summary_keys: {nc['summary_keys']}")
        print()
    print(f"Report written: {REPORT}")


if __name__ == "__main__":
    main()
