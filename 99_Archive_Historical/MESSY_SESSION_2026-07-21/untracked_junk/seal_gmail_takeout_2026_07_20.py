"""Seal GMAIL_TAKEOUT_INVENTORIED_2026_07_20 to the Merkle chain.

Records the read-only inventory of the Gmail Takeout mboxes: file
SHA-256s, message counts, date range, top senders, noise classification,
and the block-list. The inventory JSON is read from
04_Validation/gmail_takeout_inventory_2026-07-20.json.

Run from the project root:

    python 04_Validation/scripts/seal_gmail_takeout_2026_07_20.py

No network. No LLM. The chain is the source of truth.
"""

import sys
import os
import json
import subprocess
from datetime import datetime, timezone

PROJECT_ROOT = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
TECHNICAL = os.path.join(PROJECT_ROOT, "02_Technical")
if TECHNICAL not in sys.path:
    sys.path.insert(0, TECHNICAL)

from src.io.vault_io import append_block, merkle_stats

INV_PATH = os.path.join(PROJECT_ROOT, "04_Validation", "gmail_takeout_inventory_2026-07-20.json")


def main():
    with open(INV_PATH, "r") as f:
        inv = json.load(f)

    before = merkle_stats()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "event": "gmail_takeout_inventoried",
        "inventory_date": inv["inventory_date"],
        "operator": "Justin Barnett",
        "location": inv["location"],
        "mboxes": inv["mboxes"],
        "total_messages": inv["total_messages"],
        "total_business_sender_msgs": inv["total_business_sender_msgs"],
        "total_noise_sender_msgs": inv["total_noise_sender_msgs"],
        "date_range": inv["date_range"],
        "block_list_count": inv["block_list_count"],
        "distinct_senders_total": inv["distinct_senders_total"],
        "distinct_business_senders": inv["distinct_business_senders"],
        "top_business_senders": inv["top_business_senders"],
        "top_noise_senders": inv["top_noise_senders"],
        "chain_state_before": {
            "block_count": before["blockCount"],
            "merkle_root": before["merkleRoot"],
        },
        "sealed_at": now,
        "note": (
            "Read-only inventory of two Gmail Takeout mbox exports moved "
            "into the project real_world_inbox. No gates run; no ingestion. "
            "This seals the arrival and classification of 1,069 messages. "
            "Next step: split + filter, then run the four-gate pipeline."
        ),
    }

    print("=== Sealing GMAIL_TAKEOUT_INVENTORIED_2026_07_20 ===")
    print("  before block count :", before["blockCount"])
    print("  before merkle root :", before["merkleRoot"])
    block = append_block("GMAIL_TAKEOUT_INVENTORIED_2026_07_20", payload)
    print("  seal block index   :", block.get("index"))
    print("  seal block hash    :", block.get("current_hash"))

    print("\n=== Verifying chain after seal ===")
    res = subprocess.run(
        [sys.executable, "-m", "src.verify_chain"],
        cwd=TECHNICAL,
        capture_output=True,
        text=True,
    )
    print(res.stdout[-1000:])

    after = merkle_stats()
    print("\n=== After state ===")
    print("  after block count  :", after["blockCount"])
    print("  after merkle root  :", after["merkleRoot"])
    print("\nDone. The Gmail Takeout arrival is sealed to the chain.")


if __name__ == "__main__":
    main()