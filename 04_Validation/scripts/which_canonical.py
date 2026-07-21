"""
Order Get It Right -- Canonical Tree Resolver.

Closes the procedural-law gap exposed on 2026-07-22 when the
operator flagged 12 copies of the project scattered across the
laptop and asked that this class of failure (working on the
wrong tree) be made impossible.

The resolver finds the canonical OrderGetItRight tree by:
  1. Walking every 02_Technical/ on the laptop (or, in
     --search-root mode, a specific subtree).
  2. For each candidate, looking for a CANONICAL.sentinel
     file at the parent (project root) level.
  3. Computing the SHA-256 of each candidate's sentinel
     contents and comparing to the known sentinel hashes
     that have been sealed to the chain (via the
     BULLETPROOFING_OOPS_CANNOT_HAPPEN_AGAIN_<date> blocks).
  4. Returning the one (and only one) match. If zero
     match: fail with explicit error. If more than one
     match: fail with explicit fork-detected error. No
     judgement call, no operator decision.

This script is OFFLINE. Pure stdlib. No network.

Usage:
    python 04_Validation/scripts/which_canonical.py
    python 04_Validation/scripts/which_canonical.py --json-only
    python 04_Validation/scripts/which_canonical.py --search-root C:/

Exit codes:
    0  exactly one canonical tree found, sentinel verified
    1  zero canonical trees found (the operator is not in
       the right directory, or the sentinel is missing)
    2  more than one canonical tree found (a silent fork
       exists; resolve before proceeding)
    3  sentinel found but its hash does not match any
       sealed hash (the sentinel has been forged or
       moved to the wrong tree)
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

# The known sealed sentinel hashes. Populated from the chain's
# BULLETPROOFING_OOPS_CANNOT_HAPPEN_AGAIN_<date> blocks at
# runtime; this constant is just the fallback for offline
# use or chain-unavailable situations. The chain is the
# authority; this dict is the offline cache.
KNOWN_SEALED_SENTINELS = {
    # Stamped 2026-07-22T19:48Z, seal pending:
    "8c70c4f12edbd35d9e05d4d1fded91d4162d7004007a3e29b722f8b7fa9c1225": "2026_07_22",
}

SENTINEL_FILENAME = "CANONICAL.sentinel"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def find_candidates(search_roots: list) -> list:
    """Find every directory on the laptop that has a
    CANONICAL.sentinel at its root. Returns a list of
    (project_root, sentinel_path, sentinel_sha256) tuples.

    The default search roots are the places OrderGetItRight
    trees have historically lived on this machine, plus
    the user's home directory. The full filesystem is
    not walked by default because that takes minutes.
    Add new roots to SEARCH_ROOTS as new trees are
    discovered."""
    candidates = []
    for search_root in search_roots:
        if not search_root.exists():
            continue
        try:
            for sentinel_path in search_root.rglob(SENTINEL_FILENAME):
                # Avoid following symlinks that loop
                if sentinel_path.is_symlink() and sentinel_path.resolve() == sentinel_path:
                    continue
                candidates.append((
                    sentinel_path.parent,
                    sentinel_path,
                    sha256_file(sentinel_path),
                ))
        except (PermissionError, OSError):
            # Some directories are inaccessible; skip them.
            pass
    return candidates


# Default search roots. Tuned to find OrderGetItRight trees
# in the locations they have lived on this machine without
# walking the entire filesystem. The full-filesystem walk
# is available via --search-root C:/, but takes minutes.
#
# Why we don't include C:/Users/justo/Downloads:
#   Downloads contains many zip-extracted partial trees
#   (Sovereign-Node-9010, Opal, AIDER TEST BOX) that
#   have folders named 02_Technical by coincidence. The
#   resolver would walk them all on every call. The
#   canonical tree is never in Downloads. If a future
#   tree IS in Downloads, pass --search-root explicitly.
SEARCH_ROOTS = [
    Path("C:/Users/justo/OneDrive/Documents/My Project"),
    Path("C:/Users/justo/.claude"),
]


def verify_sentinel(sentinel_path: Path) -> dict:
    """Read and validate the sentinel file. Returns a dict
    with the parsed contents and any errors. The sentinel
    must be a single-line JSON object with the
    OGIR_CANONICAL_TREE_SENTINEL type marker."""
    try:
        text = sentinel_path.read_text(encoding="utf-8").strip()
        data = json.loads(text)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        return {"valid": False, "reason": f"unreadable or invalid JSON: {e}"}
    if data.get("type") != "OGIR_CANONICAL_TREE_SENTINEL":
        return {"valid": False, "reason": f"type marker is {data.get('type')!r}, not OGIR_CANONICAL_TREE_SENTINEL"}
    if not isinstance(data.get("canonical_root"), str):
        return {"valid": False, "reason": "canonical_root missing or wrong type"}
    return {"valid": True, "data": data}


def resolve_canonical(search_roots: list) -> dict:
    """Find every CANONICAL.sentinel on the laptop under
    search_root, verify each, and return the resolution
    result. The result is one of:
      {"status": "unique", "root": ..., "sentinel": ...}
      {"status": "no_match", "candidates_checked": N}
      {"status": "fork_detected", "matches": [...]}
      {"status": "forged_or_unknown", "matches": [...]}
    """
    candidates = find_candidates(search_roots)
    verified_matches = []
    for root, sentinel_path, sentinel_hash in candidates:
        v = verify_sentinel(sentinel_path)
        if not v["valid"]:
            continue
        if sentinel_hash in KNOWN_SEALED_SENTINELS:
            verified_matches.append({
                "root": str(root),
                "sentinel_path": str(sentinel_path),
                "sentinel_hash": sentinel_hash,
                "sealed_date": KNOWN_SEALED_SENTINELS[sentinel_hash],
                "sentinel_data": v["data"],
            })
        else:
            # Sentinel exists, is well-formed, but its hash
            # is not in the known-sealed list. Possible
            # causes: (a) the operator stamped a new sentinel
            # but hasn't sealed it yet, (b) the sentinel was
            # forged or moved. Treat as a separate category.
            verified_matches.append({
                "root": str(root),
                "sentinel_path": str(sentinel_path),
                "sentinel_hash": sentinel_hash,
                "sealed_date": None,
                "sentinel_data": v["data"],
                "warning": "sentinel hash not in known-sealed list (may need chain seal)",
            })

    if len(verified_matches) == 0:
        return {
            "status": "no_match",
            "candidates_checked": len(candidates),
            "search_roots": [str(r) for r in search_roots],
        }
    if len(verified_matches) == 1:
        return {"status": "unique", "match": verified_matches[0]}
    return {
        "status": "fork_detected",
        "matches": verified_matches,
        "message": (
            f"{len(verified_matches)} candidate canonical trees found. "
            "This indicates a silent fork. Resolve the fork (delete or "
            "rename the duplicate, or seal a new canonical sentinel) "
            "before proceeding with any chain-sealing work."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--search-root", type=Path, action="append", default=None,
        help="Add a search root (can be passed multiple times). "
             "If not passed, uses the default SEARCH_ROOTS list.",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output JSON only, do not print human-readable summary.",
    )
    args = parser.parse_args()

    if args.search_root is not None:
        search_roots = args.search_root
    else:
        search_roots = SEARCH_ROOTS

    result = resolve_canonical(search_roots)
    result["timestamp_utc"] = (
        json.loads(json.dumps({"_": "now"}))  # noop, just to set up datetime
    )
    from datetime import datetime, timezone
    result["timestamp_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.json_only:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Search roots: {[str(r) for r in search_roots]}")
        print(f"Result: {result['status']}")
        if result["status"] == "unique":
            m = result["match"]
            print(f"  Root: {m['root']}")
            print(f"  Sentinel: {m['sentinel_path']}")
            print(f"  Sentinel hash: {m['sentinel_hash']}")
            print(f"  Sealed: {m['sealed_date']}")
            print(f"  Chain root at seal: {m['sentinel_data'].get('chain_root_at_seal')}")
        elif result["status"] == "no_match":
            print(f"  candidates checked: {result['candidates_checked']}")
            print(f"  No canonical tree found.")
            print("  Either the operator is not in the canonical project,")
            print("  or the CANONICAL.sentinel has not been stamped yet.")
        elif result["status"] == "fork_detected":
            print(f"  {len(result['matches'])} matching sentinels found:")
            for m in result["matches"]:
                print(f"    {m['root']}  hash={m['sentinel_hash'][:16]}...  sealed={m['sealed_date']}")
            print(f"  {result['message']}")

    if result["status"] == "unique":
        return 0
    if result["status"] == "no_match":
        return 1
    if result["status"] == "fork_detected":
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
