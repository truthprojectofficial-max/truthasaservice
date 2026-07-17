"""
Order Get It Right -- 2026-07-16 fork-resolution pre-flight.

Reports the file operations that the FORK_RESOLVED_2026_07_16 plan
intends to perform against Copy B (the canonical working copy at
C:/Users/justo/OneDrive/Documents/My Project/OrderGetItRight/),
sourcing from Copy A (the older copy at
C:/Users/justo/.claude/OrderGetItRight/ which holds the Tauri build
artefacts and the project-root SEAL scripts).

Pure read-only. No copy. No delete. No chain seal. Just a report
of intended operations so the operator can confirm before phase 2
runs.

The intended operations (in order):

  1. Copy 02_Technical/tauri-shell/target/ (entire tree, ~8.5 MB)
     from Copy A to Copy B.
  2. Copy 8 project-root SEAL scripts from Copy A to Copy B:
       A5_SEAL.py
       C1_C5_SEAL.py
       D1_USB_SEAL.py
       D5_SEAL.py
       DEPLOY_HARDENED_SEAL.py
       CANONICAL_JSON_SEAL.py
       MODEL_SWAP_REVERT_SEAL.py
       RESEARCH_QUICK_WINS_SEAL.py
  3. Copy 04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md from
     Copy A to Copy B.
  4. Copy 04_Validation/ogir-build-1.0.0.zip from Copy A to Copy B.
  5. Append a type: "fork_resolved" entry to Copy B's
     04_Validation/changelog.log (changelog only, no chain seal).
  6. Refresh the live Merkle root in Copy B's
     04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt and
     04_Validation/YELLOW_RIBBON.md (text edits, no chain seal).
  7. Re-derive Copy B's Merkle root (read-only, confirm MATCH).
  8. Re-derive the 6 reference fingerprints against Copy B
     (read-only).

The actual copy is in phase_2_copy_from_a_to_b.py.
The changelog append is in phase_3_changelog_append.py.
The text refresh is in phase_4_refresh_fingerprints.py.
The chain seal is in phase_5_seal_fork_resolved.py.

Usage:
    python 04_Validation/scripts/phase_1_preflight.py
"""
import os
from pathlib import Path

COPY_A = Path(r"C:\Users\justo\.claude\OrderGetItRight")
COPY_B = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")

# (relative_path_in_a, relative_path_in_b) pairs. Most are 1:1.
COPY_OPS = [
    # 1. The Tauri build (entire target/ tree)
    (
        "02_Technical/tauri-shell/target",
        "02_Technical/tauri-shell/target",
        "dir",
    ),
    # 2. The 8 project-root SEAL scripts
    ("A5_SEAL.py", "A5_SEAL.py", "file"),
    ("C1_C5_SEAL.py", "C1_C5_SEAL.py", "file"),
    ("D1_USB_SEAL.py", "D1_USB_SEAL.py", "file"),
    ("D5_SEAL.py", "D5_SEAL.py", "file"),
    ("DEPLOY_HARDENED_SEAL.py", "DEPLOY_HARDENED_SEAL.py", "file"),
    ("CANONICAL_JSON_SEAL.py", "CANONICAL_JSON_SEAL.py", "file"),
    ("MODEL_SWAP_REVERT_SEAL.py", "MODEL_SWAP_REVERT_SEAL.py", "file"),
    ("RESEARCH_QUICK_WINS_SEAL.py", "RESEARCH_QUICK_WINS_SEAL.py", "file"),
    # 3. The research-compat doc
    (
        "04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md",
        "04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md",
        "file",
    ),
    # 4. The build zip
    (
        "04_Validation/ogir-build-1.0.0.zip",
        "04_Validation/ogir-build-1.0.0.zip",
        "file",
    ),
]


def fmt_size(n):
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n/1024:.1f} KB"
    if n < 1024 * 1024 * 1024:
        return f"{n/1024/1024:.2f} MB"
    return f"{n/1024/1024/1024:.2f} GB"


def size_of(p):
    if p.is_file():
        return p.stat().st_size
    if p.is_dir():
        total = 0
        for root, _, files in os.walk(p):
            for f in files:
                try:
                    total += (Path(root) / f).stat().st_size
                except OSError:
                    pass
        return total
    return 0


def main():
    print("=" * 72)
    print("FORK RESOLUTION 2026-07-16  --  PRE-FLIGHT REPORT (read-only)")
    print("=" * 72)
    print(f"Copy A (source): {COPY_A}")
    print(f"Copy B (target): {COPY_B}")
    print()

    if not COPY_A.exists():
        print(f"ERROR: Copy A not found: {COPY_A}")
        return 1
    if not COPY_B.exists():
        print(f"ERROR: Copy B not found: {COPY_B}")
        return 1

    print(f"{'OP':>3}  {'KIND':>5}  {'SIZE':>10}  STATUS  RELATIVE PATH")
    print("-" * 72)
    grand_total = 0
    skip = 0
    would = 0
    for i, (rel_a, rel_b, kind) in enumerate(COPY_OPS, 1):
        src = COPY_A / rel_a
        dst = COPY_B / rel_b
        sz = size_of(src) if src.exists() else 0
        if not src.exists():
            status = "SKIP (source missing)"
            skip += 1
        elif dst.exists():
            status = "OVERWRITE DESTINATION"
            would += 1
        else:
            status = "would copy"
            would += 1
        grand_total += sz
        print(
            f"{i:>3}  {kind:>5}  {fmt_size(sz):>10}  {status:<24s}  {rel_b}"
        )
    print("-" * 72)
    print(f"Total bytes to move: {fmt_size(grand_total)} ({grand_total:,})")
    print(f"Operations: {would} would execute, {skip} skipped (source missing)")
    print()
    print("Phase 2 (copy) will refuse to overwrite any existing destination.")
    print("This pre-flight is read-only and changes nothing.")


if __name__ == "__main__":
    raise SystemExit(main())
