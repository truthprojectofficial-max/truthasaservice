"""
Order Get It Right -- 2026-07-16 fork-resolution phase 3.

Appends a single type: "fork_resolved" entry to Copy B's
04_Validation/changelog.log. The entry records:

  - that the project had silently forked into two working copies
    (C:/Users/justo/.claude/OrderGetItRight and
    C:/Users/justo/OneDrive/Documents/My Project/OrderGetItRight)
  - that Copy B (the My Project copy) is the canonical working copy
  - that the 3 Tauri artefacts and 5 SEAL/doc files were copied
    from Copy A to Copy B
  - that the 3 Tauri artefacts were re-hashed against block 1979
    and matched byte-for-byte
  - that this changelog entry points at
    04_Validation/RECONCILIATION_2026-07-16.md and
    04_Validation/TAURI_BINARY_INVESTIGATION_2026-07-16.md

This is paperwork. It does NOT seal a new Merkle block (that is
phase 5). It only adds a row to the human changelog so the
record of the fork resolution is on disk next to the chain
record.

Reversible: the last line of changelog.log can be removed with
a single edit. The script also prints the SHA-256 of the file
before and after the append, so a third party can confirm only
the one line was added.

Usage:
    python 04_Validation/scripts/phase_3_changelog_append.py
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")
CHANGELOG = PROJECT_ROOT / "04_Validation" / "changelog.log"
REPORT = Path(__file__).resolve().parent / "phase_3_changelog_report.json"

# The line to append. The fields match the existing changelog
# format (one JSON object per line, ISO 8601 timestamp, binId,
# type, summary, details).
ENTRY = {
    "binId": "codex-on-Justo",
    "timestamp": "2026-07-16T07:30:00Z",
    "type": "fork_resolved",
    "summary": "Two working copies of the project reconciled. Copy B (My Project/OrderGetItRight/) is canonical. Tauri build + 5 SEAL/doc files copied from Copy A (.claude/OrderGetItRight/) to Copy B; 3 Tauri artefacts re-hashed against block 1979 and matched byte-for-byte.",
    "details": (
        "The build had silently forked into two working directories: "
        "C:/Users/justo/.claude/OrderGetItRight/ (older, with the Tauri build, "
        "chain root 98a0b3aacb85a0c3413e6023dceacae2e7f79572f8f0c33a7ca1f65618fe83d7, "
        "2,977 blocks) and "
        "C:/Users/justo/OneDrive/Documents/My Project/OrderGetItRight/ "
        "(newer, chain root 1dfadc3f16019dbe8f278b839683a20da3a1a562581f06b9be1ce3e8cc33397f, "
        "2,796 blocks). Both chains verified. The Tauri binary sealed at block 1979 "
        "existed in Copy A but not Copy B -- it was not deleted, it was in a different "
        "working copy. 8 files (8,864,089 bytes) copied from Copy A to Copy B: 3 Tauri "
        "final artefacts (raw_exe 2d974c93, msi 5adb40fb, nsis 3bab1984 -- all matched "
        "block 1979 byte-for-byte after copy) and 5 SEAL/doc files (D1_USB_SEAL.py, "
        "CANONICAL_JSON_SEAL.py, MODEL_SWAP_REVERT_SEAL.py, "
        "RESEARCH_QUICK_WINS_SEAL.py, 04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md). "
        "Phase scripts at 04_Validation/scripts/phase_1_preflight.py, "
        "phase_2_copy_from_a_to_b.py, phase_3_changelog_append.py. "
        "Full reconciliation in 04_Validation/RECONCILIATION_2026-07-16.md and "
        "04_Validation/TAURI_BINARY_INVESTIGATION_2026-07-16.md. "
        "No chain seal -- that is phase 5."
    ),
    "see_also": [
        "04_Validation/RECONCILIATION_2026-07-16.md",
        "04_Validation/TAURI_BINARY_INVESTIGATION_2026-07-16.md",
        "04_Validation/scripts/phase_1_preflight.py",
        "04_Validation/scripts/phase_2_copy_from_a_to_b.py",
        "04_Validation/scripts/phase_2_copy_report.json",
    ],
}


def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if not CHANGELOG.exists():
        print(f"ERROR: changelog not found: {CHANGELOG}", file=sys.stderr)
        return 1

    # Pre-append: hash and line count
    sha_before = sha256_file(CHANGELOG)
    lines_before = sum(1 for _ in CHANGELOG.open("r", encoding="utf-8"))
    last_line_before = ""
    with CHANGELOG.open("r", encoding="utf-8") as f:
        for line in f:
            last_line_before = line.rstrip("\n")

    print("=" * 72)
    print("FORK RESOLUTION 2026-07-16  --  PHASE 3: CHANGELOG APPEND")
    print("=" * 72)
    print(f"Changelog: {CHANGELOG}")
    print(f"SHA-256 before: {sha_before}")
    print(f"Lines before:   {lines_before}")
    print(f"Last line:      {last_line_before[:100]}{'...' if len(last_line_before) > 100 else ''}")
    print()

    # Append
    line_to_append = json.dumps(ENTRY, separators=(",", ":")) + "\n"
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(line_to_append)

    # Post-append: hash and line count
    sha_after = sha256_file(CHANGELOG)
    lines_after = sum(1 for _ in CHANGELOG.open("r", encoding="utf-8"))
    last_line_after = ""
    with CHANGELOG.open("r", encoding="utf-8") as f:
        for line in f:
            last_line_after = line.rstrip("\n")

    print(f"SHA-256 after:  {sha_after}")
    print(f"Lines after:    {lines_after}")
    print(f"Last line:      {last_line_after[:100]}{'...' if len(last_line_after) > 100 else ''}")
    print()

    if lines_after != lines_before + 1:
        print(f"ERROR: line count did not grow by exactly 1 "
              f"({lines_before} -> {lines_after})", file=sys.stderr)
        return 2

    if last_line_after != line_to_append.rstrip("\n"):
        print("ERROR: last line does not match the entry we tried to append",
              file=sys.stderr)
        return 3

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "changelog_path": str(CHANGELOG),
        "sha256_before": sha_before,
        "sha256_after": sha_after,
        "lines_before": lines_before,
        "lines_after": lines_after,
        "entry_appended": ENTRY,
        "last_line_appended": last_line_after,
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Appended 1 line ({len(line_to_append)} bytes).")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
