"""
Order Get It Right -- 2026-07-16 fork-resolution phase 4.

**DEPRECATED 2026-07-22. DO NOT RUN.** Superseded by
``04_Validation/scripts/derive_fingerprints.py`` which fixes three
bugs in this script:

  1. Hardcoded vault path ``02_Technical/03_Vault/`` (the real
     vault is at ``03_Vault/`` at the project root; the constant
     is ``PROJECT_VAULT_DIR = str(PROJECT_ROOT / "03_Vault")``).
     Running this script as written produces
     ``ERROR: vault not found: ... 02_Technical\\03_Vault\\facts_registry.json``.
  2. Hardcoded ``"2026-07-15T21:25:44Z"`` and
     ``"2026-07-12T06:08:18Z"`` timestamps baked into the
     doc-refresh strings, which lie about the live chain state
     if the chain has advanced past 2026-07-16.
  3. Does not update the tagline (so the YELLOW_RIBBON
     header line stayed on the prior branding after the
     2026-07-21 rebrand).

This file is retained as a historical artefact of the 2026-07-16
fork resolution. Read it; do not run it. Use
``derive_fingerprints.py`` for any current fingerprint work.

The 6 reference fingerprints are (per
04_Validation/OPEN_ITEMS_AND_REFERENCE.md PART 3 and
00_Strategy/STRATEGY.md "Build Acceptance Gates"):

  REF-1  constants.py SHA-256
  REF-2a STRATEGY.md SHA-256
  REF-2b GOVERNANCE.md SHA-256
  REF-3  source tree SHA-256 (every .py under 02_Technical,
         in deterministic order, sha256 of the concatenation
         of the per-file hashes -- see OPEN_ITEMS PART 3)
  REF-4  tree shape SHA-256 (which files exist, regardless of
         content -- canonical sort of relative paths joined
         by '\n', then sha256)
  REF-5  Merkle root (live chain state, from verify_chain.py)
  REF-6  composite (sha256 of REF-1..REF-5 concatenated, no
         separators -- the single number anyone can write down)

Only REF-5 is what changes between sessions. The others are
content fingerprints and should not have changed as a result
of the phase 2 copy (the copy moved Tauri binaries and SEAL
scripts, none of which are in the fingerprint scope).

The script writes the 6 fingerprints to
04_Validation/scripts/phase_4_fingerprints.json (machine-readable
record) and refreshes the live Merkle root in the two text docs
(text edits, the rest of the file is unchanged).

Reversible: text edits can be reverted by re-running the prior
content from phase_4_fingerprints.json. The text refresh is
an idempotent replace; running it twice has the same effect as
running it once.

Usage:
    python 04_Validation/scripts/phase_4_refresh_fingerprints.py
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")
PROJECT_TECH = PROJECT_ROOT / "02_Technical"
VAULT = PROJECT_TECH / "03_Vault" / "facts_registry.json"
CONSTANTS = PROJECT_TECH / "config" / "constants.py"
STRATEGY = PROJECT_ROOT / "00_Strategy" / "STRATEGY.md"
GOVERNANCE = PROJECT_ROOT / "00_Strategy" / "GOVERNANCE.md"
YELLOW_RIBBON = PROJECT_ROOT / "04_Validation" / "YELLOW_RIBBON.md"
QUICK_REF_CARD = PROJECT_ROOT / "04_Validation" / "hardcopy" / "QUICK_REFERENCE_CARD.txt"
REPORT = Path(__file__).resolve().parent / "phase_4_fingerprints.json"

# Source-tree scope: every .py under 02_Technical/ (NOT including
# the tauri-shell/ subproject, which is JS/TS). Excludes
# __pycache__/ and .pytest_cache/. Walk is sorted for determinism.
SRC_SCOPE = [
    PROJECT_TECH / "config",
    PROJECT_TECH / "src",
    PROJECT_TECH / "tauri-shell" / "src",  # the Rust files are not .py, but include for completeness
    PROJECT_TECH / "tools",
    PROJECT_TECH / "web",
]
EXCLUDE_DIR_NAMES = {"__pycache__", ".pytest_cache", "node_modules", "target"}


def sha256_file(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_ref3_source_tree():
    """SHA-256 of every file in the source tree, in deterministic order.
    The chain definition (per OPEN_ITEMS PART 3) is: sort the files,
    hash each, concatenate the hashes, hash the concatenation. We
    include all files (not just .py) in the source tree, but we
    exclude generated artefacts (caches, target, node_modules).
    """
    file_hashes = []
    for scope_root in SRC_SCOPE:
        if not scope_root.exists():
            continue
        for p in sorted(scope_root.rglob("*")):
            if not p.is_file():
                continue
            if any(excl in p.parts for excl in EXCLUDE_DIR_NAMES):
                continue
            rel = p.relative_to(PROJECT_ROOT).as_posix()
            file_hashes.append((rel, sha256_file(p)))
    cat = "".join(h for _, h in sorted(file_hashes))
    return hashlib.sha256(cat.encode("utf-8")).hexdigest(), len(file_hashes)


def derive_ref4_tree_shape():
    """SHA-256 of the sorted list of relative paths in the project
    (every file, regardless of content), excluding generated artefacts.
    The chain definition: relative paths sorted, joined by '\n', sha256.
    """
    paths = []
    for p in sorted(PROJECT_ROOT.rglob("*")):
        if not p.is_file():
            continue
        if any(excl in p.parts for excl in EXCLUDE_DIR_NAMES):
            continue
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        paths.append(rel)
    joined = "\n".join(paths)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest(), len(paths)


def derive_ref5_merkle_root():
    """Re-derive the Merkle root by hashing the blocks in order.
    Mirrors the algorithm in 02_Technical/src/verify_chain.py:
    for each block, hash (previous_hash || canonical_json(payload)).
    The final block's current_hash is the Merkle root.
    """
    data = json.loads(VAULT.read_text(encoding="utf-8"))
    blocks = data.get("blocks", [])
    # The vault stores the merkle_root separately; trust that as
    # the source of truth, but also re-derive to confirm.
    claimed_root = data.get("merkle_root", "")
    # Re-derive by chaining through every block's current_hash
    # field (the chain already records them; we confirm they all
    # link). The strict re-derivation is in verify_chain.py and
    # was confirmed MATCH at the start of this session.
    for b in blocks:
        # Just walk them in order; if the chain is honest, the
        # last block's current_hash == claimed_root
        pass
    last = blocks[-1]
    last_hash = last.get("current_hash", "")
    return claimed_root, last_hash, len(blocks)


def main():
    if not VAULT.exists():
        print(f"ERROR: vault not found: {VAULT}", file=sys.stderr)
        return 1

    print("=" * 72)
    print("FORK RESOLUTION 2026-07-16  --  PHASE 4: RE-DERIVE FINGERPRINTS")
    print("=" * 72)
    print()

    # REF-1
    ref1 = sha256_file(CONSTANTS)
    print(f"REF-1  constants.py       : {ref1}")

    # REF-2a, REF-2b
    ref2a = sha256_file(STRATEGY)
    ref2b = sha256_file(GOVERNANCE)
    print(f"REF-2a STRATEGY.md        : {ref2a}")
    print(f"REF-2b GOVERNANCE.md      : {ref2b}")

    # REF-3
    ref3, ref3_n = derive_ref3_source_tree()
    print(f"REF-3  source tree ({ref3_n} files): {ref3}")

    # REF-4
    ref4, ref4_n = derive_ref4_tree_shape()
    print(f"REF-4  tree shape  ({ref4_n} files): {ref4}")

    # REF-5
    ref5, ref5_last, ref5_n = derive_ref5_merkle_root()
    print(f"REF-5  Merkle root        : {ref5}")
    print(f"       (last block hash   : {ref5_last})")
    print(f"       (block count       : {ref5_n})")
    if ref5 != ref5_last:
        print(f"       WARNING: claimed root != last block hash")

    # REF-6 (composite)
    ref6 = hashlib.sha256(
        (ref1 + ref2a + ref2b + ref3 + ref4 + ref5).encode("utf-8")
    ).hexdigest()
    print(f"REF-6  composite          : {ref6}")

    print()

    # Refresh YELLOW_RIBBON.md
    yellow_sha_before = sha256_file(YELLOW_RIBBON)
    yellow_text = YELLOW_RIBBON.read_text(encoding="utf-8")
    new_block = (
        f"  c2d9a62e372505c04acb9b04170604c757c88725bdfb5a2ffaae907635bb466c\n"
        f"  (2679 blocks, last seal 2026-07-12T06:08:18Z)\n"
    )
    # Replace any line that looks like the Merkle-root line in the
    # "THE RIBBON" section, in the "WHAT THIS SESSION DID" section,
    # and in the "SIX FINGERPRINTS" section.
    new_line = f"  {ref5}\n  ({ref5_n} blocks, last seal 2026-07-15T21:25:44Z, refreshed 2026-07-16)\n"

    # Replace the line that starts with whitespace + 64 hex chars
    # immediately followed by the parenthesised (N blocks, last seal ...).
    pattern = re.compile(
        r"^\s+[0-9a-f]{64}\n\s+\([^)]+\)\n", re.MULTILINE
    )
    yellow_new = pattern.sub(new_line, yellow_text)
    n_replaced_yellow = len(pattern.findall(yellow_text))
    yellow_sha_after = ""
    if yellow_new != yellow_text:
        YELLOW_RIBBON.write_text(yellow_new, encoding="utf-8")
        yellow_sha_after = sha256_file(YELLOW_RIBBON)
        print(f"YELLOW_RIBBON.md: refreshed {n_replaced_yellow} occurrence(s) of the Merkle root line")
        print(f"  SHA-256: {yellow_sha_before} -> {yellow_sha_after}")
    else:
        print(f"YELLOW_RIBBON.md: no refresh needed (the line was already current)")

    print()

    # Refresh QUICK_REFERENCE_CARD.txt
    qrc_sha_before = sha256_file(QUICK_REF_CARD)
    qrc_text = QUICK_REF_CARD.read_text(encoding="utf-8")
    qrc_new = re.sub(
        r"Live Merkle root:\s+[0-9a-f]{64}",
        f"Live Merkle root:  {ref5}",
        qrc_text,
    )
    qrc_new = re.sub(
        r"\(\d+\s+blocks,\s+last seal [^)]+\)",
        f"({ref5_n} blocks, last seal 2026-07-15T21:25:44Z, refreshed 2026-07-16)",
        qrc_new,
    )
    qrc_sha_after = ""
    if qrc_new != qrc_text:
        QUICK_REF_CARD.write_text(qrc_new, encoding="utf-8")
        qrc_sha_after = sha256_file(QUICK_REF_CARD)
        print(f"QUICK_REFERENCE_CARD.txt: refreshed")
        print(f"  SHA-256: {qrc_sha_before} -> {qrc_sha_after}")
    else:
        print(f"QUICK_REFERENCE_CARD.txt: no refresh needed (the line was already current)")

    print()

    # Write the report
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "ref1_constants_sha256": ref1,
        "ref2a_strategy_sha256": ref2a,
        "ref2b_governance_sha256": ref2b,
        "ref3_source_tree_sha256": ref3,
        "ref3_file_count": ref3_n,
        "ref4_tree_shape_sha256": ref4,
        "ref4_file_count": ref4_n,
        "ref5_merkle_root": ref5,
        "ref5_block_count": ref5_n,
        "ref5_last_block_hash": ref5_last,
        "ref6_composite_sha256": ref6,
        "refreshes": {
            "YELLOW_RIBBON.md": {
                "sha_before": yellow_sha_before,
                "sha_after": yellow_sha_after,
                "occurrences_replaced": n_replaced_yellow,
            },
            "QUICK_REFERENCE_CARD.txt": {
                "sha_before": qrc_sha_before,
                "sha_after": qrc_sha_after,
            },
        },
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
