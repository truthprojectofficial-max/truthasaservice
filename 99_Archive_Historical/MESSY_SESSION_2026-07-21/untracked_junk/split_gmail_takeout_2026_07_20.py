"""Split the Gmail Takeout mboxes into individual .txt files for the CLI.

The audit CLI's process_directory() iterates top-level files in the inbox
dir and supports .txt/.docx/.pdf. mbox/.eml are not supported directly, so
this splitter breaks each mbox message into one .txt file (headers + body),
filtering out the operator's own addresses and pure-noise senders so only
incoming business correspondence reaches the four-gate pipeline.

Uses the stdlib ``email`` module for MIME-correct parsing: multipart,
quoted-printable (=XX), base64, and RFC-2047 encoded headers are all
decoded so the audit scanner receives real readable text.

    python 04_Validation/scripts/split_gmail_takeout_2026_07_20.py

No network. No LLM. Pure stdlib.
"""

import os
import re
import json
import email
from collections import Counter

PROJECT_ROOT = r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
INBOX_SRC = os.path.join(PROJECT_ROOT, "real_world_inbox")
SPLIT_INBOX = os.path.join(PROJECT_ROOT, "data", "gmail_split_inbox")
MBOXES = [
    "All mail Including Spam and Trash.mbox",
    "All mail Including Spam and Trash (2).mbox",
]

OPERATOR_ADDRS = {
    "juzzychance@gmail.com",
    "truth.project.official@gmail.com",
    "justobeme@outlook.com",
    "brycebarnett01@gmail.com",
}

NOISE_RE = re.compile(
    r"(no-?reply|noreply|newsletter|notification|receipt|donotreply|"
    r"do-not-reply|automated|mailer-daemon|postmaster|updates?@|"
    r"team@|hello@|support@|info@|admin@|system@|alerts?@|"
    r"account-security|accountprotection|independentreserve|"
    r"vivaldi\.com|canva\.com|googleplay|accounts\.google|github|"
    r"ollama\.com|petersonacademy|pfp\.net|belong\.com\.au|"
    r"spotify\.com|workforceaustralia|dewr\.gov|stripe\.com|"
    r"createsend|ecomms\.origin|sevenrooms|anthropic\.com|nvidia\.com)",
    re.IGNORECASE,
)


def extract_email(from_header):
    if not from_header:
        return ""
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        return m.group(1).strip().lower()
    m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", from_header)
    return m.group(0).strip().lower() if m else from_header.strip().lower()


def _decode_mbox_raw(path):
    """Read mbox as bytes and split into raw RFC-822 message blobs on 'From ' lines.

    Each blob in mbox format begins with an envelope line
    ('From sender date') that is NOT part of the RFC-822 message. We strip
    that first line so the remaining bytes parse cleanly with
    email.message_from_bytes.
    """
    with open(path, "rb") as f:
        data = f.read()
    for blob in re.split(rb"(?:^|\n)From ", data):
        blob = blob.strip()
        if not blob:
            continue
        # Drop the envelope line (everything up to and including the first \n).
        nl = blob.find(b"\n")
        if nl != -1:
            blob = blob[nl + 1:]
        # Re-prepend the standard 'From ' so the message has a proper header
        # block start is NOT needed; the blob now starts with the first real
        # RFC-822 header (e.g. 'Return-Path:', 'MIME-Version:', 'Date:').
        yield blob


def _safe_decode_header(raw):
    """Decode an RFC-2047 encoded header (=?utf-8?Q?...?=) to plain text."""
    from email.header import decode_header, make_header
    try:
        return str(make_header(decode_header(raw or "")))
    except Exception:
        return raw or ""


def _body_from_msg(msg):
    """Extract the best plain-text body from an email.message.Message.

    Handles multipart/alternative, multipart/mixed, quoted-printable, base64,
    and 7bit/8bit. Prefers text/plain; falls back to text/html.
    """
    if msg.is_multipart():
        plain_parts = []
        html_parts = []
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload is not None:
                        charset = part.get_content_charset() or "utf-8"
                        plain_parts.append(payload.decode(charset, errors="replace"))
                except Exception:
                    pass
            elif ctype == "text/html":
                try:
                    payload = part.get_payload(decode=True)
                    if payload is not None:
                        charset = part.get_content_charset() or "utf-8"
                        html_parts.append(payload.decode(charset, errors="replace"))
                except Exception:
                    pass
        if plain_parts:
            return "\n\n".join(plain_parts)
        if html_parts:
            return "\n\n".join(html_parts)
        return ""
    try:
        payload = msg.get_payload(decode=True)
        if payload is None:
            return msg.get_payload() or ""
        charset = msg.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")
    except Exception:
        return msg.get_payload() or ""


def parse_mbox_messages(path):
    """Parse an mbox file into decoded messages using the stdlib email module."""
    for blob in _decode_mbox_raw(path):
        try:
            msg = email.message_from_bytes(blob)
        except Exception:
            continue
        yield {
            "from": _safe_decode_header(msg.get("From", "")),
            "date": msg.get("Date", ""),
            "subject": _safe_decode_header(msg.get("Subject", "(no subject)")),
            "body": _body_from_msg(msg),
        }


def sanitize(name, maxlen=60):
    s = re.sub(r"[^\w \-]", "", name)
    s = re.sub(r"\s+", "_", s).strip("_")
    return (s[:maxlen] or "msg").rstrip("_")
def main():
    os.makedirs(SPLIT_INBOX, exist_ok=True)
    for old in os.listdir(SPLIT_INBOX):
        if old.endswith(".txt"):
            os.remove(os.path.join(SPLIT_INBOX, old))
    kept = skipped_operator = skipped_noise = empty_body = idx = 0
    kept_senders = Counter()
    for name in MBOXES:
        p = os.path.join(INBOX_SRC, name)
        if not os.path.exists(p):
            print(f"  MISSING: {name}")
            continue
        for msg in parse_mbox_messages(p):
            idx += 1
            em = extract_email(msg["from"])
            if em in OPERATOR_ADDRS:
                skipped_operator += 1
                continue
            if NOISE_RE.search(em) or NOISE_RE.search(msg["from"] or ""):
                skipped_noise += 1
                continue
            kept += 1
            kept_senders[em] += 1
            if len((msg["body"] or "").strip()) == 0:
                empty_body += 1
            subj = sanitize(msg["subject"])
            date_short = (msg["date"] or "")[:10].replace("-", "")
            fname = f"GM_{idx:04d}_{date_short}_{subj}.txt"[:120]
            out = os.path.join(SPLIT_INBOX, fname)
            block = (
                f"From: {msg['from']}\nDate: {msg['date']}\n"
                f"Subject: {msg['subject']}\n---\n{msg['body']}\n"
            )
            with open(out, "w", encoding="utf-8", errors="replace") as wf:
                wf.write(block)
    print(f"=== SPLIT COMPLETE ===")
    print(f"  total parsed       : {idx}")
    print(f"  kept (business in) : {kept}")
    print(f"  skipped (operator) : {skipped_operator}")
    print(f"  skipped (noise)   : {skipped_noise}")
    print(f"  kept with empty body: {empty_body}")
    print(f"  split inbox dir    : {SPLIT_INBOX}")
    print(f"  distinct kept      : {len(kept_senders)}")
    print("  top kept senders:")
    for em, c in kept_senders.most_common(15):
        print(f"    {c:4d}  {em}")
    manifest = {
        "split_date": "2026-07-20",
        "source_mboxes": MBOXES,
        "split_inbox": SPLIT_INBOX,
        "total_parsed": idx,
        "kept": kept,
        "skipped_operator": skipped_operator,
        "skipped_noise": skipped_noise,
        "kept_with_empty_body": empty_body,
        "operator_addresses": sorted(OPERATOR_ADDRS),
        "top_kept_senders": kept_senders.most_common(20),
    }
    mpath = os.path.join(PROJECT_ROOT, "04_Validation", "gmail_split_manifest_2026-07-20.json")
    json.dump(manifest, open(mpath, "w"), indent=2)
    print(f"\nWrote {mpath}")


if __name__ == "__main__":
    main()