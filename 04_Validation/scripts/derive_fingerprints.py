"""
Order Get It Right -- Reference Fingerprint Deriver and Doc Refresher.

Re-derives the six reference fingerprints against the live project
and refreshes the two operator-facing documents (YELLOW_RIBBON.md,
QUICK_REFERENCE_CARD.txt) so their present-tense claims match the
chain.

The six fingerprints (per OPEN_ITEMS_AND_REFERENCE.md PART 3):

  REF-1  02_Technical/config/constants.py        SHA-256
  REF-2a 00_Strategy/STRATEGY.md                 SHA-256
  REF-2b 00_Strategy/GOVERNANCE.md               SHA-256
  REF-3  source tree SHA-256 (every .py under the canonical
         02_Technical source-tree scope, in deterministic order,
         sha of concatenated per-file hashes)
  REF-4  tree shape SHA-256 (sorted relative paths joined by '\\n',
         excluding generated artefacts)
  REF-5  Merkle root (live chain state, from facts_registry.json)
  REF-6  composite (sha256 of REF-1..REF-5 concatenated)

Vault path is read from the canonical source (config.constants.
PROJECT_VAULT_DIR) so the script never carries a stale hardcoded
path. The tagline (line 2 of QUICK_REFERENCE_CARD, the project line
of YELLOW_RIBBON) is read from src/__init__.py (the canonical
source) so the doc refresh never carries a stale "Truth as a
Service" / "Verified Processor" string.

The chain's last-block timestamp is read from facts_registry.json
(not from any hardcoded literal) so the doc refresh never lies
about when the last seal happened.

Supersedes phase_4_refresh_fingerprints.py (2026-07-16 fork-
resolution script), which had three bugs:
  1. Hardcoded vault path `02_Technical/03_Vault/` (real vault
     is at `03_Vault/` at the project root).
  2. Hardcoded "2026-07-15T21:25:44Z" timestamp literal in the
     doc-refresh strings, which would lie if the chain was at any
     other state.
  3. Did not update the tagline (YELLOW_RIBBON header still said
     "Truth as a Service" after the 2026-07-21 rebrand).

The original phase_4_refresh_fingerprints.py is retained as a
historical artefact and a reference for the 2026-07-16 fork-
resolution sequence. Do not run it; it is a fossil.

Usage:
    python 04_Validation/scripts/derive_fingerprints.py
    python 04_Validation/scripts/derive_fingerprints.py --json-only
    python 04_Validation/scripts/derive_fingerprints.py --no-doc-refresh

Exit codes:
    0  fingerprints derived, docs refreshed (or --no-doc-refresh)
    1  vault not found or merkle_root missing
    2  IO error
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Canonical source paths ------------------------------------------------
# These are read once at module load. If the project layout changes,
# update the constants, not the script.

PROJECT_ROOT = Path("C:/Users/justo/OneDrive/Documents/My Project/OrderGetItRight")
TECH = PROJECT_ROOT / "02_Technical"
CONSTANTS = TECH / "config" / "constants.py"
STRATEGY = PROJECT_ROOT / "00_Strategy" / "STRATEGY.md"
GOVERNANCE = PROJECT_ROOT / "00_Strategy" / "GOVERNANCE.md"
SRC_INIT = TECH / "src" / "__init__.py"
YELLOW_RIBBON = PROJECT_ROOT / "04_Validation" / "YELLOW_RIBBON.md"
QUICK_REF_CARD = PROJECT_ROOT / "04_Validation" / "hardcopy" / "QUICK_REFERENCE_CARD.txt"
REPORT = Path(__file__).resolve().parent / "phase_4_fingerprints.json"

# Source-tree scope for REF-3: matches OPEN_ITEMS_AND_REFERENCE.md
# PART 3. Excludes the vendored CPython bundle under
# tauri-shell/resources/python/.
SRC_DIRS = [
    TECH / "config",
    TECH / "src",
    TECH / "tauri-shell" / "src",
    TECH / "tools",
    TECH / "web",
]

# Exclusions for REF-4: caches, build outputs, vendored bundles,
# archives.
EXCLUDE_PARTS = (
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "target",
    "resources",
    ".git",
    "99_Archive",
    "99_Archive_Historical",
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def read_vault_path() -> Path:
    """Read the canonical vault path from config.constants.PROJECT_VAULT_DIR.

    Imports the constants module via sys.path injection so the
    script picks up the same canonical value the runtime uses,
    even if the constant changes from a literal to an expression
    in the future.
    """
    sys.path.insert(0, str(TECH))
    try:
        from config.constants import PROJECT_VAULT_DIR
        return Path(PROJECT_VAULT_DIR)
    finally:
        # Don't leave our sys.path modification in place for any
        # subsequent imports in the same process.
        try:
            sys.path.remove(str(TECH))
        except ValueError:
            pass


def read_tagline() -> str:
    """Read the canonical tagline from 02_Technical/src/__init__.py.

    Format: `__tagline__ = "Verified Processor"`.
    """
    text = SRC_INIT.read_text(encoding="utf-8")
    m = re.search(r'__tagline__\s*=\s*["\']([^"\']+)["\']', text)
    if not m:
        raise SystemExit(f"ERROR: could not find __tagline__ in {SRC_INIT}")
    return m.group(1)


def derive_ref1() -> str:
    return sha256_file(CONSTANTS)


def derive_ref2a() -> str:
    return sha256_file(STRATEGY)


def derive_ref2b() -> str:
    return sha256_file(GOVERNANCE)


def derive_ref3() -> tuple:
    py_files = sorted(
        p for d in SRC_DIRS if d.exists() for p in d.rglob("*.py")
        if "__pycache__" not in p.parts and ".pytest_cache" not in p.parts
    )
    h = hashlib.sha256()
    for p in py_files:
        h.update(sha256_file(p).encode())
    return h.hexdigest(), len(py_files)


def derive_ref4() -> tuple:
    all_files = sorted(
        str(p.relative_to(PROJECT_ROOT)).replace("\\", "/")
        for p in PROJECT_ROOT.rglob("*")
        if p.is_file() and not any(x in p.parts for x in EXCLUDE_PARTS)
    )
    h = hashlib.sha256()
    for f in all_files:
        h.update((f + "\n").encode())
    return h.hexdigest(), len(all_files)


def derive_ref5(vault_path: Path) -> tuple:
    """vault_path is the vault directory. The chain file is
    facts_registry.json inside it. If vault_path is a file (some
    legacy code paths pass the file directly), accept that too."""
    if vault_path.is_dir():
        chain_file = vault_path / "facts_registry.json"
    elif vault_path.is_file():
        chain_file = vault_path
    else:
        raise SystemExit(f"ERROR: vault path {vault_path} is neither file nor directory")
    data = json.loads(chain_file.read_text(encoding="utf-8"))
    blocks = data.get("blocks", [])
    root = data.get("merkle_root", "")
    if not root:
        raise SystemExit(f"ERROR: vault at {chain_file} has no merkle_root field")
    last = blocks[-1] if blocks else {}
    return root, last.get("current_hash", ""), len(blocks), last.get("timestamp", "")


def derive_ref6(ref1: str, ref2a: str, ref2b: str, ref3: str, ref4: str, ref5: str) -> str:
    return hashlib.sha256(
        (ref1 + ref2a + ref2b + ref3 + ref4 + ref5).encode()
    ).hexdigest()


def refresh_yellow_ribbon(
    root: str,
    block_count: int,
    last_ts: str,
    ref1: str,
    ref2a: str,
    ref2b: str,
    ref3: str,
    ref4: str,
    ref6: str,
    tagline: str,
) -> dict:
    """Refresh YELLOW_RIBBON.md in place. Idempotent."""
    before_sha = sha256_file(YELLOW_RIBBON)
    text = YELLOW_RIBBON.read_text(encoding="utf-8")

    # 1. Tagline in the header line (line 2). Pattern: "v1.0.0  |  <tagline>  |  Operator:".
    # If tagline changed, the script updates the middle segment.
    text = re.sub(
        r"(v\d+\.\d+\.\d+\s+\|\s+)([^|]+?)(\s+\|\s+Operator:)",
        rf"\g<1>{tagline}\g<3>",
        text,
        count=1,
    )

    # 2. The Merkle root in "THE RIBBON" section.
    # Pattern: a 64-hex line followed by a parenthesised "(N blocks, last seal ..., refreshed ...)".
    new_root_line = (
        f"  {root}\n"
        f"  ({block_count} blocks, last seal {last_ts}, refreshed {datetime.now(timezone.utc).strftime('%Y-%m-%d')})\n"
    )
    root_pattern = re.compile(
        r"^\s+[0-9a-f]{64}\n\s+\([^)]+\)\n", re.MULTILINE
    )
    new_text, n_root = root_pattern.subn(new_root_line, text)
    text = new_text

    # 3. The six fingerprints block. Replace each REF-N value line.
    # Pattern: "REF-N  label..." followed by the 64-hex on the next line.
    text = re.sub(
        r"(REF-1\s+constants.py\s+SHA-256\s*\n\s+)[0-9a-f]{64}",
        rf"\g<1>{ref1}", text,
    )
    text = re.sub(
        r"(REF-2a\s+STRATEGY\.md SHA-256\s*\n\s+STRATEGY:\s+)[0-9a-f]{64}",
        rf"\g<1>{ref2a}", text,
    )
    text = re.sub(
        r"(GOVERNANCE:\s+)[0-9a-f]{64}",
        rf"\g<1>{ref2b}", text,
    )
    text = re.sub(
        r"(REF-3\s+source tree[^\n]*\n\s+)[0-9a-f]{64}",
        rf"\g<1>{ref3}", text,
    )
    text = re.sub(
        r"(REF-4\s+tree shape[^\n]*\n\s+)[0-9a-f]{64}",
        rf"\g<1>{ref4}", text,
    )
    text = re.sub(
        r"(REF-6\s+composite[^\n]*\n\s+)[0-9a-f]{64}",
        rf"\g<1>{ref6}", text,
    )

    after_sha = ""
    changed = text != YELLOW_RIBBON.read_text(encoding="utf-8")
    if changed:
        YELLOW_RIBBON.write_text(text, encoding="utf-8")
        after_sha = sha256_file(YELLOW_RIBBON)
    return {
        "file": str(YELLOW_RIBBON),
        "sha_before": before_sha,
        "sha_after": after_sha or before_sha,
        "root_lines_replaced": n_root,
        "tagline_set_to": tagline,
        "changed": changed,
    }


def refresh_quick_reference_card(
    root: str, block_count: int, last_ts: str, tagline: str
) -> dict:
    before_sha = sha256_file(QUICK_REF_CARD)
    text = QUICK_REF_CARD.read_text(encoding="utf-8")

    # 1. Tagline in line 2.
    text = re.sub(
        r"(v\d+\.\d+\.\d+\s+\|\s+)([^|]+?)(\s+\|\s+Operator:)",
        rf"\g<1>{tagline}\g<3>",
        text,
        count=1,
    )

    # 2. The "Live snapshot" block. The card has:
    #      "  Live snapshot (as of YYYY-MM-DD, NNNNN blocks):\n"
    #      "    <root>\n"
    # The date and block count are written into the heading, the
    # root into the indented line. Pattern: a 64-hex line that
    # follows a "Live snapshot" heading.
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    new_snapshot_block = (
        f"  Live snapshot (as of {date_str}, {block_count} blocks):\n"
        f"    {root}\n"
    )
    snapshot_pattern = re.compile(
        r"^\s*Live snapshot \(as of[^\n]*\):\n\s+[0-9a-f]{64}\n",
        re.MULTILINE,
    )
    text, n_replaced = snapshot_pattern.subn(new_snapshot_block, text)

    after_sha = ""
    changed = text != QUICK_REF_CARD.read_text(encoding="utf-8")
    if changed:
        QUICK_REF_CARD.write_text(text, encoding="utf-8")
        after_sha = sha256_file(QUICK_REF_CARD)
    return {
        "file": str(QUICK_REF_CARD),
        "sha_before": before_sha,
        "sha_after": after_sha or before_sha,
        "snapshot_blocks_replaced": n_replaced,
        "tagline_set_to": tagline,
        "changed": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output JSON only; do not refresh any docs.",
    )
    parser.add_argument(
        "--no-doc-refresh", action="store_true",
        help="Derive fingerprints but do not refresh YELLOW_RIBBON.md or QUICK_REFERENCE_CARD.txt.",
    )
    args = parser.parse_args()

    # 1. Read the canonical sources.
    try:
        vault_path = read_vault_path()
    except Exception as e:
        print(f"ERROR reading vault path: {e}", file=sys.stderr)
        return 1
    if not vault_path.exists():
        print(f"ERROR: vault not found at canonical path: {vault_path}", file=sys.stderr)
        return 1
    # If the constant pointed at a file, accept that. If it pointed
    # at a directory, check facts_registry.json lives inside.
    if vault_path.is_dir() and not (vault_path / "facts_registry.json").exists():
        print(
            f"ERROR: vault dir {vault_path} does not contain facts_registry.json",
            file=sys.stderr,
        )
        return 1

    try:
        tagline = read_tagline()
    except Exception as e:
        print(f"ERROR reading tagline: {e}", file=sys.stderr)
        return 1

    # 2. Derive the six fingerprints.
    ref1 = derive_ref1()
    ref2a = derive_ref2a()
    ref2b = derive_ref2b()
    ref3, ref3_n = derive_ref3()
    ref4, ref4_n = derive_ref4()
    ref5, ref5_last, ref5_n, ref5_last_ts = derive_ref5(vault_path)
    ref6 = derive_ref6(ref1, ref2a, ref2b, ref3, ref4, ref5)

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tagline": tagline,
        "vault_path": str(vault_path),
        "ref1_constants_sha256": ref1,
        "ref2a_strategy_sha256": ref2a,
        "ref2b_governance_sha256": ref2b,
        "ref3_source_tree_sha256": ref3,
        "ref3_file_count": ref3_n,
        "ref4_tree_shape_sha256": ref4,
        "ref4_file_count": ref4_n,
        "ref5_merkle_root": ref5,
        "ref5_last_block_hash": ref5_last,
        "ref5_block_count": ref5_n,
        "ref5_last_block_timestamp": ref5_last_ts,
        "ref6_composite_sha256": ref6,
        "doc_refreshes": {},
    }

    # 3. Refresh the docs.
    if not args.json_only and not args.no_doc_refresh:
        report["doc_refreshes"]["YELLOW_RIBBON.md"] = refresh_yellow_ribbon(
            ref5, ref5_n, ref5_last_ts, ref1, ref2a, ref2b, ref3, ref4, ref6, tagline,
        )
        report["doc_refreshes"]["QUICK_REFERENCE_CARD.txt"] = refresh_quick_reference_card(
            ref5, ref5_n, ref5_last_ts, tagline,
        )

    # 4. Write the JSON report.
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    # 5. Print to stdout.
    print(f"REF-1  constants.py       : {ref1}")
    print(f"REF-2a STRATEGY.md        : {ref2a}")
    print(f"REF-2b GOVERNANCE.md      : {ref2b}")
    print(f"REF-3  source tree ({ref3_n} files): {ref3}")
    print(f"REF-4  tree shape  ({ref4_n} files): {ref4}")
    print(f"REF-5  Merkle root        : {ref5}")
    print(f"       (last block hash   : {ref5_last})")
    print(f"       (block count       : {ref5_n})")
    print(f"       (last block ts     : {ref5_last_ts})")
    print(f"REF-6  composite          : {ref6}")
    print(f"tagline (from src/__init__.py): {tagline}")
    if report["doc_refreshes"]:
        for name, r in report["doc_refreshes"].items():
            status = "REFRESHED" if r.get("changed") else "no change"
            print(f"  {name}: {status}")
    print(f"\nReport: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
