"""
Command-line entry point for batch document auditing.

Usage:
    python -m src.audit_cli --inbox inbox --outbox outbox --formats md,pdf,docx
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.io.pipeline import process_directory, clear_eject, request_eject


def _parse_formats(value: str):
    parts = [p.strip().lower() for p in value.split(",")]
    out = []
    for p in parts:
        if not p.startswith("."):
            p = "." + p
        out.append(p)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="value-audit",
        description="Order Get It Right -- deterministic document audit pipeline.",
    )
    parser.add_argument(
        "--inbox", default="inbox", help="Directory containing .txt/.docx/.pdf files to audit."
    )
    parser.add_argument(
        "--outbox", default="outbox", help="Directory where reports will be written."
    )
    parser.add_argument(
        "--formats",
        default="md,pdf,docx",
        help="Comma-separated output formats: md,pdf,docx.",
    )
    parser.add_argument(
        "--eject",
        action="store_true",
        help="Set the eject flag before running (stops after first file).",
    )
    args = parser.parse_args(argv)

    inbox = Path(args.inbox).resolve()
    outbox = Path(args.outbox).resolve()
    formats = _parse_formats(args.formats)

    clear_eject()
    if args.eject:
        request_eject()

    print("Order Get It Right -- Batch Document Audit")
    print(f"Inbox : {inbox}")
    print(f"Outbox: {outbox}")
    print(f"Formats: {', '.join(formats)}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("-" * 60)

    results = process_directory(inbox, outbox, formats)

    success = sum(1 for r in results if r.status == "success")
    errors = sum(1 for r in results if r.status == "error")
    ejected = sum(1 for r in results if r.status == "ejected")
    warnings = sum(1 for r in results if r.status == "warning")

    for r in results:
        print(f"[{r.status.upper():8}] {r.input_path.name}")
        if r.error:
            print(f"  -> {r.error}")
        for op in r.output_paths:
            print(f"  -> {op}")

    print("-" * 60)
    print(
        f"Done. Success: {success} | Errors: {errors} | "
        f"Warnings: {warnings} | Ejected: {ejected}"
    )
    print(f"Finished: {datetime.now(timezone.utc).isoformat()}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
