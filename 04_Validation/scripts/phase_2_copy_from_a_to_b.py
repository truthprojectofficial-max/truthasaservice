"""
Order Get It Right -- 2026-07-16 fork-resolution phase 2.

Copies the 3 final Tauri artefacts and 5 new SEAL/doc files from
Copy A (.claude/OrderGetItRight/) to Copy B (My Project/OrderGetItRight/).

The 3 Tauri artefacts are verified SHA-256 against block 1979 AFTER
copy. If any of them does not match the chain's claim, the script
prints a loud warning and refuses to continue. The 5 new files
are copied with shutil.copy2 (preserves metadata). No file is
ever overwritten -- if a destination already exists, the script
prints a warning and skips it.

No chain seal. No changelog edit. Just the copy + a per-file
SHA-256 verification report written to
04_Validation/scripts/phase_2_copy_report.json.

Reversible: every copied file is a single `os.remove` away.

Usage:
    python 04_Validation/scripts/phase_2_copy_from_a_to_b.py
"""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

COPY_A = Path(r"C:\Users\justo\.claude\OrderGetItRight")
COPY_B = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")

# Block 1979 expected SHA-256s, taken verbatim from the chain.
TAURI_EXPECTED_SHA256 = {
    "raw_exe": "2d974c93e11ffd583528212f6f0cff09b117e370b195b4f4cb6ef221636eb397",
    "msi":     "5adb40fb0cefa36fbf49c3bd60a3e0c895e9af29cd816a2609a54cfb0d484e60",
    "nsis":    "3bab19844e5f9dbf297219bb157598cfefe293dda6d749b55e1f6ee100ca30d6",
}

# (src_rel, dst_rel, kind, note, expected_sha256_or_None)
COPY_OPS = [
    # 3 Tauri final artefacts
    (
        "02_Technical/tauri-shell/target/release/order-get-it-right.exe",
        "02_Technical/tauri-shell/target/release/order-get-it-right.exe",
        "raw_exe",
        "Tauri raw exe (4,847,104 bytes per block 1979)",
        TAURI_EXPECTED_SHA256["raw_exe"],
    ),
    (
        "02_Technical/tauri-shell/target/release/bundle/msi/Order Get It Right_1.0.0_x64_en-US.msi",
        "02_Technical/tauri-shell/target/release/bundle/msi/Order Get It Right_1.0.0_x64_en-US.msi",
        "msi",
        "Tauri MSI installer (2,314,240 bytes per block 1979)",
        TAURI_EXPECTED_SHA256["msi"],
    ),
    (
        "02_Technical/tauri-shell/target/release/bundle/nsis/Order Get It Right_1.0.0_x64-setup.exe",
        "02_Technical/tauri-shell/target/release/bundle/nsis/Order Get It Right_1.0.0_x64-setup.exe",
        "nsis",
        "Tauri NSIS installer (1,624,462 bytes per block 1979)",
        TAURI_EXPECTED_SHA256["nsis"],
    ),
    # 5 new SEAL/doc files
    (
        "D1_USB_SEAL.py",
        "D1_USB_SEAL.py",
        "file",
        "SEAL script (D1 USB clean-host)",
        None,
    ),
    (
        "CANONICAL_JSON_SEAL.py",
        "CANONICAL_JSON_SEAL.py",
        "file",
        "SEAL script (canonical JSON enforcement)",
        None,
    ),
    (
        "MODEL_SWAP_REVERT_SEAL.py",
        "MODEL_SWAP_REVERT_SEAL.py",
        "file",
        "SEAL script (model swap revert)",
        None,
    ),
    (
        "RESEARCH_QUICK_WINS_SEAL.py",
        "RESEARCH_QUICK_WINS_SEAL.py",
        "file",
        "SEAL script (research quick wins)",
        None,
    ),
    (
        "04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md",
        "04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md",
        "file",
        "Research-compat doc",
        None,
    ),
]

REPORT = Path(__file__).resolve().parent / "phase_2_copy_report.json"


def sha256_file(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not COPY_A.exists():
        print(f"ERROR: Copy A not found: {COPY_A}", file=sys.stderr)
        return 1
    if not COPY_B.exists():
        print(f"ERROR: Copy B not found: {COPY_B}", file=sys.stderr)
        return 1

    print("=" * 72)
    print("FORK RESOLUTION 2026-07-16  --  PHASE 2: COPY A -> B")
    print("=" * 72)
    print(f"Source (A): {COPY_A}")
    print(f"Target (B): {COPY_B}")
    print()

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "operations": [],
    }
    total_bytes = 0
    copied = 0
    skipped = 0
    failed = 0
    tauri_verified = {"raw_exe": None, "msi": None, "nsis": None}

    for i, (rel_a, rel_b, kind, note, expected_sha) in enumerate(COPY_OPS, 1):
        src = COPY_A / rel_a
        dst = COPY_B / rel_b
        op_record = {
            "op_index": i,
            "src": str(src),
            "dst": str(dst),
            "kind": kind,
            "note": note,
        }

        if not src.exists():
            op_record["result"] = "skipped"
            op_record["reason"] = "source missing"
            skipped += 1
            report["operations"].append(op_record)
            print(f"  [{i:>2}] SKIP  source missing  {rel_b}")
            continue

        if dst.exists():
            op_record["result"] = "skipped"
            op_record["reason"] = "destination exists; refusing to overwrite"
            skipped += 1
            report["operations"].append(op_record)
            print(f"  [{i:>2}] SKIP  destination exists  {rel_b}")
            continue

        # Create parent dirs as needed
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Pre-copy: verify source SHA matches the chain claim (for Tauri files)
        src_sha_pre = sha256_file(src)
        src_size = src.stat().st_size
        op_record["src_bytes"] = src_size
        op_record["src_sha256"] = src_sha_pre

        if expected_sha is not None:
            if src_sha_pre != expected_sha:
                op_record["result"] = "failed"
                op_record["reason"] = (
                    f"source SHA-256 does not match block 1979 claim. "
                    f"want={expected_sha} got={src_sha_pre}"
                )
                failed += 1
                report["operations"].append(op_record)
                print(f"  [{i:>2}] FAIL  source hash mismatch  {rel_b}")
                print(f"        want: {expected_sha}")
                print(f"        got:  {src_sha_pre}")
                continue

        # Do the copy
        try:
            shutil.copy2(src, dst)
        except OSError as e:
            op_record["result"] = "failed"
            op_record["reason"] = f"copy error: {e}"
            failed += 1
            report["operations"].append(op_record)
            print(f"  [{i:>2}] FAIL  copy error: {e}  {rel_b}")
            continue

        # Post-copy: verify the destination has the same SHA
        dst_sha = sha256_file(dst)
        dst_size = dst.stat().st_size
        if dst_sha != src_sha_pre:
            op_record["result"] = "failed"
            op_record["reason"] = (
                f"post-copy SHA mismatch -- corruption. "
                f"src={src_sha_pre} dst={dst_sha}"
            )
            failed += 1
            report["operations"].append(op_record)
            print(f"  [{i:>2}] FAIL  post-copy corruption  {rel_b}")
            # Remove the corrupted file
            try:
                dst.unlink()
            except OSError:
                pass
            continue

        op_record["result"] = "copied"
        op_record["dst_bytes"] = dst_size
        op_record["dst_sha256"] = dst_sha
        copied += 1
        total_bytes += dst_size
        if kind in tauri_verified:
            tauri_verified[kind] = dst_sha
        report["operations"].append(op_record)
        sha_short = dst_sha[:16]
        print(f"  [{i:>2}] OK    {dst_size:>10} bytes  sha={sha_short}  {rel_b}")

    print()
    print("-" * 72)
    print(f"Copied:   {copied} files, {total_bytes:,} bytes total")
    print(f"Skipped:  {skipped} files (source missing or destination exists)")
    print(f"Failed:   {failed} files (pre-copy or post-copy verification failed)")
    print()

    # Tauri verification summary
    print("Tauri block-1979 verification:")
    all_ok = True
    for kind, got in tauri_verified.items():
        want = TAURI_EXPECTED_SHA256[kind]
        if got == want:
            print(f"  {kind:>8}  sha256 MATCH  ({got[:16]}...)")
        else:
            all_ok = False
            print(f"  {kind:>8}  sha256 MISMATCH")
            print(f"    want: {want}")
            print(f"    got:  {got}")
    if all_ok:
        print("  All 3 Tauri artefacts match block 1979 claim byte-for-byte.")
    else:
        print("  WARNING: Tauri artefacts do NOT match block 1979.")
        print("  Phase 2 is incomplete; do NOT proceed to phases 3-6.")

    report["summary"] = {
        "copied": copied,
        "skipped": skipped,
        "failed": failed,
        "total_bytes": total_bytes,
        "all_tauri_match_block_1979": all_ok,
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print()
    print(f"Report written: {REPORT}")
    return 0 if (failed == 0 and all_ok) else 2


if __name__ == "__main__":
    raise SystemExit(main())
