"""Read-only inventory of the Gmail Takeout mboxes in real_world_inbox/.

Counts messages, extracts the date range and top senders, and classifies
senders against a noise list (Gmail block-list + obvious newsletter /
no-reply patterns). Prints a JSON summary the seal script records to the
Merkle chain.

    python 04_Validation/scripts/inventory_gmail_takeout_2026_07_20.py

No network. No LLM. No vault writes. Pure stdlib, read-only.
"""

import os
import re
import json
import hashlib
from collections import Counter
from datetime import datetime

PROJECT_ROOT = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
INBOX = os.path.join(PROJECT_ROOT, "real_world_inbox")
MBOXES = [
    "All mail Including Spam and Trash.mbox",
    "All mail Including Spam and Trash (2).mbox",
]
BLOCK_LIST_PATH = os.path.join(INBOX, "User settings", "Blocked addresses.json")

NOISE_RE = re.compile(
    r"(no-?reply|noreply|newsletter|notification|receipt|donotreply|"
    r"do-not-reply|automated|mailer-daemon|postmaster|updates?@|"
    r"team@|hello@|support@|info@|admin@|system@|alerts?@|"
    r"account-security|accountprotection|email\.independentreserve|"
    r"mail\.independentreserve|vivaldi\.com|canva\.com)",
    re.IGNORECASE,
)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_mbox(path):
    msg_from = msg_date = None
    in_headers = False
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            if line.startswith("From ") and not in_headers:
                if msg_from is not None or msg_date is not None:
                    yield msg_from, msg_date
                in_headers = True
                msg_from = msg_date = None
                continue
            if in_headers:
                if line == "":
                    yield msg_from, msg_date
                    in_headers = False
                    msg_from = msg_date = None
                    continue
                if line.lower().startswith("from:"):
                    msg_from = line[4:].strip()
                elif line.lower().startswith("date:") and msg_date is None:
                    msg_date = line[5:].strip()
    if in_headers and (msg_from is not None or msg_date is not None):
        yield msg_from, msg_date


def extract_email(from_header):
    if not from_header:
        return ""
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        return m.group(1).strip().lower()
    m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", from_header)
    if m:
        return m.group(0).strip().lower()
    return from_header.strip().lower()


def main():
    block_list = []
    if os.path.exists(BLOCK_LIST_PATH):
        block_list = json.load(open(BLOCK_LIST_PATH, "r")).get("addresses", [])
    block_set = {a.lower() for a in block_list}

    results = []
    all_dates = []
    sender_counter = Counter()
    noise_sender_counter = Counter()
    business_sender_counter = Counter()

    for name in MBOXES:
        p = os.path.join(INBOX, name)
        if not os.path.exists(p):
            print(f"  MISSING: {name}")
            continue
        size_mb = round(os.path.getsize(p) / 1048576, 2)
        digest = sha256_of(p)
        count = 0
        for from_h, date_h in parse_mbox(p):
            count += 1
            email = extract_email(from_h)
            sender_counter[email] += 1
            is_noise = email in block_set or bool(NOISE_RE.search(email)) or bool(NOISE_RE.search(from_h or ""))
            if is_noise:
                noise_sender_counter[email] += 1
            else:
                business_sender_counter[email] += 1
            if date_h:
                all_dates.append(date_h)
        results.append({"file": name, "size_mb": size_mb, "sha256": digest, "message_count": count})
        print(f"  {name}: {count} msgs, {size_mb} MB, {digest[:16]}")

    total_msgs = sum(r["message_count"] for r in results)
    total_business = sum(business_sender_counter.values())
    total_noise = sum(noise_sender_counter.values())

    parsed_dates = []
    for d in all_dates:
        try:
            parsed_dates.append(datetime.strptime(d[:31], "%a, %d %b %Y %H:%M:%S %z"))
        except Exception:
            try:
                parsed_dates.append(datetime.strptime(d[:10], "%Y-%m-%d"))
            except Exception:
                pass
    date_min = min(parsed_dates).isoformat() if parsed_dates else None
    date_max = max(parsed_dates).isoformat() if parsed_dates else None

    summary = {
        "inventory_date": "2026-07-20",
        "location": INBOX,
        "mboxes": results,
        "total_messages": total_msgs,
        "total_business_sender_msgs": total_business,
        "total_noise_sender_msgs": total_noise,
        "date_range": {"earliest": date_min, "latest": date_max},
        "block_list_count": len(block_set),
        "top_business_senders": business_sender_counter.most_common(20),
        "top_noise_senders": noise_sender_counter.most_common(10),
        "distinct_senders_total": len(sender_counter),
        "distinct_business_senders": len(business_sender_counter),
    }
    print("\n=== INVENTORY SUMMARY ===")
    print(json.dumps(summary, indent=2, default=str))
    out_path = os.path.join(PROJECT_ROOT, "04_Validation", "gmail_takeout_inventory_2026-07-20.json")
    json.dump(summary, open(out_path, "w"), indent=2, default=str)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()