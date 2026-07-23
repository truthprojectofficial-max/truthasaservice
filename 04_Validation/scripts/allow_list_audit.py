"""
Order Get It Right -- Allow-List Audit Script
==============================================

Lists the 5 entries in the canonical allow-list (sealed 2026-07-23 in
commit c80150d) with per-file usage counts: how many calls to each
allow-listed module appear in each file. This complements the
closed-set test (tests/test_allow_list_closed.py) by answering
"are the existing entries earning their keep?".

Usage:
    python 04_Validation/scripts/allow_list_audit.py
    python 04_Validation/scripts/allow_list_audit.py --json-only
    python 04_Validation/scripts/allow_list_audit.py --help

Exit codes:
    0 = all 5 entries have at least 1 call (live state)
    2 = at least 1 entry has 0 calls (operator warning:
        the entry is allow-listed but never used; consider
        removing it via a sealed ALLOW_LIST_AMENDED_2026_07_XX event)
    1 = error (file not found, allow-list not importable, etc.)

The allow-list itself is in 04_Validation/scripts/audit_no_network.py
under the constant `ALLOW_LIST`. This script reads that constant; it
does not duplicate it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path


# Compute the path of the audit_no_network.py module and the project root.
# We use the file's own location so the script can be run from anywhere.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from audit_no_network import ALLOW_LIST  # type: ignore
except ImportError as e:
    print(f"FATAL: cannot import ALLOW_LIST from audit_no_network.py: {e}",
          file=sys.stderr)
    sys.exit(1)


PROJECT_ROOT = SCRIPT_DIR.parent.parent  # OrderGetItRight/


def count_module_uses(file_path: Path, module_names: list[str]) -> dict[str, int]:
    """Count occurrences of each module in the file.

    For each module name, count:
      - import statements: `import module_name` and `from module_name ...`
      - attribute access: `module_name.foo(...)` (the most common usage pattern)

    The total `calls` for a module is the sum of these counts.
    """
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {m: -1 for m in module_names}

    counts: dict[str, int] = {}
    for module in module_names:
        # Strip dots so a fully-qualified module name matches the import
        # statement `import x.y` and the attribute access `x.y.foo(...)`.
        # We do a simple count of substring occurrences; this is heuristic,
        # not perfect, but is sufficient for the governance purpose.
        n = text.count(module)
        counts[module] = n
    return counts


def last_modified_iso(path: Path) -> str:
    """Return the file's last-modified time in ISO-8601 UTC."""
    if not path.exists():
        return "MISSING"
    mtime = path.stat().st_mtime
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))


def render_table(rows: list[dict]) -> str:
    """Render the audit result as a fixed-width text table."""
    headers = ["PATH", "MODULES", "CALL_COUNT", "LAST_MODIFIED"]
    widths = [60, 25, 11, 21]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    out = [sep]
    out.append("| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |")
    out.append(sep)
    for r in rows:
        out.append("| " + " | ".join(str(r[h]).ljust(w)
                                      for h, w in zip(headers, widths)) + " |")
    out.append(sep)
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--json-only", action="store_true",
                        help="emit JSON only, no human-readable table")
    args = parser.parse_args()

    if not ALLOW_LIST:
        print("FATAL: ALLOW_LIST is empty in audit_no_network.py",
              file=sys.stderr)
        return 1

    rows: list[dict] = []
    total_calls = 0
    unused_entries: list[str] = []

    # ALLOW_LIST shape (verified 2026-07-23): dict[str, set[str]] mapping
    # the relative path to a set of allow-listed module names.
    if not isinstance(ALLOW_LIST, dict):
        print(f"FATAL: ALLOW_LIST is {type(ALLOW_LIST).__name__}, expected dict",
              file=sys.stderr)
        return 1

    for rel_path, modules in ALLOW_LIST.items():
        modules = list(modules) if modules else []
        if not rel_path or not modules:
            print(f"WARN: malformed allow-list entry: {rel_path!r}: {modules!r}",
                  file=sys.stderr)
            continue

        file_path = PROJECT_ROOT / rel_path
        if not file_path.exists():
            print(f"WARN: allow-list path does not exist: {rel_path}",
                  file=sys.stderr)
            counts = {m: 0 for m in modules}
            call_count = 0
        else:
            counts = count_module_uses(file_path, modules)
            call_count = sum(c for c in counts.values() if c >= 0)

        if call_count == 0:
            unused_entries.append(rel_path)

        total_calls += call_count
        rows.append({
            "PATH": rel_path,
            "MODULES": ",".join(modules),
            "CALL_COUNT": str(call_count),
            "LAST_MODIFIED": last_modified_iso(file_path),
        })

    if args.json_only:
        out = {
            "allow_list_size": len(ALLOW_LIST),
            "total_calls": total_calls,
            "unused_entries": unused_entries,
            "rows": rows,
            "verdict": "OK" if not unused_entries else "WARN_UNUSED",
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Allow-list audit (closed-set policy sealed 2026-07-23 c80150d)")
        print(f"Entries: {len(ALLOW_LIST)} | Total calls: {total_calls}")
        print()
        print(render_table(rows))
        print()
        if unused_entries:
            print(f"WARN: {len(unused_entries)} allow-list entries have 0 calls:")
            for p in unused_entries:
                print(f"  - {p}")
            print()
            print("These entries are allow-listed but never used. Consider")
            print("removing them via a sealed ALLOW_LIST_AMENDED_2026_07_XX event")
            print("after the test_allow_list_closed.py check passes for the")
            print("reduced set.")
        else:
            print("OK: all 5 allow-list entries have at least 1 call.")

    if unused_entries:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
