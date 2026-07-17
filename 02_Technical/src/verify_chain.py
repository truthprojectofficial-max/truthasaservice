"""
Order Get It Right -- Standalone Chain Verifier

Re-derives the Merkle root of the facts registry from the on-disk
blocks and compares it to the `merkle_root` field recorded in the
registry. Prints MATCH or BROKEN with diagnostics.

This is the third-party handoff for OPEN_ITEMS_AND_REFERENCE.md D4
("build a 'verify from USB' script"). The hard-copy backup plan
promises a third party can verify the chain in under 30 seconds. This
script is that promise realised.

Usage:
    python -m src.verify_chain
    python -m src.verify_chain --vault <path-to-vault-directory>
    python -m src.verify_chain --print-refs

Exit codes:
    0  chain is intact (MATCH)
    1  chain is broken (BROKEN)
    2  usage / IO error

The script is offline. It does not import any networking module. It
reads JSON files from the vault directory and computes SHA-256 hashes.
A third party can copy the project folder to a USB stick, run this
script on a host with no network, and confirm the chain is intact.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.io import vault_io
from src.utils.canonical import canonical_dumps


def _canonical_json(payload: Any) -> str:
    """Serialise a payload deterministically.

    Now a thin wrapper around ``src.utils.canonical.canonical_dumps``
    (added 2026-07-16, closes the canonical-JSON foot-gun identified
    in ``the research-compat doc (area 3, canonical-JSON foot-gun)`` area 3).

    The previous inline implementation
    (``json.dumps(payload, sort_keys=True, separators=(",", ":"))``
    with no ``default=`` callable) was the HIGH-severity latent
    crash. This wrapper is byte-identical to the previous output
    for any payload that contained only JSON-native types (the
    historical case) and is the project-wide fix for any payload
    that contains ``datetime``, ``UUID``, ``Decimal``, ``set``, or
    any other non-JSON-native type.
    """
    return canonical_dumps(payload)


def _recompute_root(blocks: List[Dict[str, Any]]) -> Tuple[str, Optional[int]]:
    """Re-derive the Merkle root by walking the block list in order.

    Returns (root, first_broken_index). first_broken_index is None on
    success or the index of the first block whose current_hash does
    not match its computed value.
    """
    previous_hash = "0" * 64
    for block in blocks:
        ts = block.get("timestamp")
        event_type = block.get("event_type")
        payload = block.get("payload", {})
        block_payload = {"event": event_type, "payload": payload, "ts": ts}
        serialised = _canonical_json(block_payload)
        expected = hashlib.sha256((previous_hash + serialised).encode("utf-8")).hexdigest()
        if expected != block.get("current_hash"):
            return expected, block.get("index")
        previous_hash = expected
    return previous_hash, None


def _load_registry(vault_path: Path) -> Dict[str, Any]:
    """Load facts_registry.json from the vault, or return an empty
    registry if the file does not exist yet.
    """
    registry_file = vault_path / "facts_registry.json"
    if not registry_file.exists():
        return {"merkle_root": "0" * 64, "blocks": []}
    try:
        with open(registry_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: could not read {registry_file}: {exc}", file=sys.stderr)
        sys.exit(2)


def verify(vault_path: Optional[Path] = None) -> Dict[str, Any]:
    """Verify the chain. Returns a dict with the result fields.

    The dict shape:
      {
        "matches": bool,
        "merkleRoot": str (64-hex),
        "recomputedRoot": str (64-hex),
        "blockCount": int,
        "firstBlock": str | None,
        "lastBlock": str | None,
        "brokenAtIndex": int | None,
        "brokenAtRoot": str | None,
        "vaultPath": str,
      }
    """
    if vault_path is None:
        vault_path = Path(vault_io.VAULT_DIR)
    vault_path = Path(vault_path).resolve()

    registry = _load_registry(vault_path)
    blocks = registry.get("blocks", [])
    claimed_root = registry.get("merkle_root", "0" * 64)
    recomputed_root, broken_at = _recompute_root(blocks)
    matches = (claimed_root == recomputed_root) and (broken_at is None)
    return {
        "matches": matches,
        "merkleRoot": claimed_root,
        "recomputedRoot": recomputed_root,
        "blockCount": len(blocks),
        "firstBlock": blocks[0]["timestamp"] if blocks else None,
        "lastBlock": blocks[-1]["timestamp"] if blocks else None,
        "brokenAtIndex": broken_at,
        "brokenAtRoot": recomputed_root if broken_at is not None else None,
        "vaultPath": str(vault_path),
    }


def _print_result(result: Dict[str, Any]) -> None:
    print("=" * 78)
    print("ORDER GET IT RIGHT -- CHAIN VERIFICATION")
    print("=" * 78)
    print(f"Vault path       : {result['vaultPath']}")
    print(f"Block count      : {result['blockCount']}")
    print(f"First block      : {result['firstBlock']}")
    print(f"Last block       : {result['lastBlock']}")
    print(f"Claimed root     : {result['merkleRoot']}")
    print(f"Recomputed root  : {result['recomputedRoot']}")
    if result["matches"]:
        print("-" * 78)
        print("RESULT: MATCH -- chain is intact.")
        print("Every block in the vault re-derives to the same Merkle root that")
        print("is recorded in the registry. The audit history is unchanged.")
    else:
        print("-" * 78)
        print("RESULT: BROKEN -- chain does not re-derive.")
        print(f"First broken block index: {result['brokenAtIndex']}")
        print("Possible causes:")
        print("  - A block was edited or removed without re-sealing.")
        print("  - A block was added without following the previous_hash rule.")
        print("  - The on-disk JSON was corrupted (disk failure, partial write).")
        print("Do not trust any verdict derived from this chain. Roll back to the")
        print("last known-good backup (the hard-copy backup plan covers this).")
    print("=" * 78)


def _hash_file(path: Path) -> str:
    """SHA-256 of a single file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_source_tree(root: Path) -> str:
    """Composite SHA-256 over every .py under root (sorted, excluding __pycache__)."""
    files: List[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if "__pycache__" in dirpath or ".pytest_cache" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                files.append(Path(dirpath) / fn)
    files.sort()
    h = hashlib.sha256()
    for f in files:
        h.update(f.read_bytes())
    return h.hexdigest()


def _print_refs(project_root: Path, result: Dict[str, Any]) -> None:
    """Print the six project reference fingerprints."""
    print("=" * 78)
    print("ORDER GET IT RIGHT -- SIX REFERENCE FINGERPRINTS")
    print("=" * 78)
    constants = project_root / "02_Technical" / "config" / "constants.py"
    strategy = project_root / "00_Strategy" / "STRATEGY.md"
    governance = project_root / "00_Strategy" / "GOVERNANCE.md"
    src = project_root / "02_Technical"
    print(f"REF-1  constants.py SHA-256       : {_hash_file(constants)}")
    print(f"REF-2a STRATEGY.md SHA-256        : {_hash_file(strategy)}")
    print(f"REF-2b GOVERNANCE.md SHA-256      : {_hash_file(governance)}")
    print(f"REF-3  source tree SHA-256        : {_hash_source_tree(src)}")
    # REF-4 (tree shape) is computed by find + sha256sum of the path list.
    # Skipped here to keep the script single-file; documented in OPEN_ITEMS.
    print(f"REF-5  Merkle root (live)         : {result['merkleRoot']}")
    print(f"       Block count                : {result['blockCount']}")
    print(f"       First block                : {result['firstBlock']}")
    print(f"       Last block                 : {result['lastBlock']}")
    print("=" * 78)
    print("REF-6 (composite) is sha256 of the concatenation of REF-1..REF-5.")
    print("Re-derive by hand: concatenate the five strings above and sha256 them.")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.verify_chain",
        description="Verify the Order Get It Right Merkle chain from disk.",
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=None,
        help="Path to the vault directory (default: the project's vault).",
    )
    parser.add_argument(
        "--print-refs",
        action="store_true",
        help="Also print the six project reference fingerprints.",
    )
    args = parser.parse_args()

    vault_path = Path(args.vault) if args.vault else None
    try:
        result = verify(vault_path)
    except Exception as exc:
        print(f"ERROR: verification failed: {exc}", file=sys.stderr)
        return 2

    _print_result(result)

    if args.print_refs:
        # The project root is the parent of 02_Technical, which is the
        # parent of the vault. Resolved to avoid symlink confusion.
        project_root = Path(vault_io.PROJECT_VAULT_DIR).resolve().parent.parent
        _print_refs(project_root, result)

    return 0 if result["matches"] else 1


if __name__ == "__main__":
    sys.exit(main())
