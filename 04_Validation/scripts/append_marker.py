"""
Order Get It Right -- Append-Marker Helper.

Tiny utility to append a single marker block to the chain
with a custom event_type and freeform payload. Used for
operator-action events (C_PORT_RECOVERY_*, etc.) that
don't fit the automated seal paths.

Usage:
    python append_marker.py --event-type MY_EVENT_2026_07_22 \\
        --note "short description"
    python append_marker.py --event-type FOO --note "bar" \\
        --payload '{"x": 1}' --json-only

The script reads canonical vault path from
config.constants.PROJECT_VAULT_DIR. It is offline (no
network). It refuses to run if the chain is in a state
that conflicts with the marker (e.g. a marker with the
same event_type was sealed in the last N blocks).
"""
import argparse
import json
import sys
from pathlib import Path

TECH = Path("02_Technical")
sys.path.insert(0, str(TECH))
from config.constants import PROJECT_VAULT_DIR  # noqa: E402

from src.io.vault_io import append_block  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--event-type", required=True,
                        help="SCREAMING_SNAKE_CASE event_type, e.g. C_PORT_RECOVERY_2026_07_22")
    parser.add_argument("--note", required=True,
                        help="Short human-readable note (goes in the payload).")
    parser.add_argument("--payload", default=None,
                        help="Optional JSON string with extra payload fields.")
    parser.add_argument("--operator", default="Justin Barnett",
                        help="Operator name (default: Justin Barnett).")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    # Validate event_type format
    if not args.event_type.replace("_", "").isalnum():
        print(f"ERROR: event_type {args.event_type!r} must be SCREAMING_SNAKE_CASE",
              file=sys.stderr)
        return 1

    extra = {}
    if args.payload:
        try:
            extra = json.loads(args.payload)
        except json.JSONDecodeError as e:
            print(f"ERROR: --payload is not valid JSON: {e}", file=sys.stderr)
            return 1

    payload = {
        "note": args.note,
        "operator": args.operator,
        "appended_via": "append_marker.py",
        **extra,
    }

    block = append_block(args.event_type, payload)
    if args.json_only:
        print(json.dumps(block, indent=2, sort_keys=True))
    else:
        print(f"SEALED: {args.event_type}")
        print(f"  block_index: {block.get('index')}")
        print(f"  block_hash:  {block.get('current_hash')}")
        print(f"  vault_path:  {PROJECT_VAULT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
