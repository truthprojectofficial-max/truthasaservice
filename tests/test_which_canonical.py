"""
Order Get It Right -- Canonical Tree Resolver tests.

Closes the procedural-law gap exposed 2026-07-22 when the
operator flagged 12 copies of the project scattered across
the laptop. The resolver must:
  - find the canonical tree deterministically (sentinel +
    sealed hash + path match)
  - reject when invoked from a non-canonical directory
  - reject when zero sentinels exist
  - reject when more than one sentinel exists (silent fork)
"""
import hashlib
import json
from pathlib import Path

import pytest


def test_sentinel_format_is_stable():
    """The sentinel file is a single-line JSON object with
    the OGIR_CANONICAL_TREE_SENTINEL type marker. The schema
    is what the resolver parses; if it changes, the resolver
    breaks."""
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("wcp",
        Path(__file__).parent.parent / "04_Validation" / "scripts" / "which_canonical.py")
    wcp = module_from_spec(spec)
    spec.loader.exec_module(wcp)
    sentinel_path = Path("CANONICAL.sentinel")
    assert sentinel_path.exists(), "CANONICAL.sentinel must exist at project root"
    text = sentinel_path.read_text(encoding="utf-8").strip()
    data = json.loads(text)
    assert data["type"] == "OGIR_CANONICAL_TREE_SENTINEL"
    assert data["version"] == 1
    assert "canonical_root" in data
    assert "constants_sha256" in data
    assert "chain_root_at_seal" in data
    assert "block_count_at_seal" in data
    assert len(data["constants_sha256"]) == 64


def test_sentinel_hash_matches_canonical_root():
    """The sentinel's canonical_root must point to the
    directory containing the sentinel (modulo path
    normalization)."""
    sentinel_path = Path("CANONICAL.sentinel")
    data = json.loads(sentinel_path.read_text(encoding="utf-8"))
    sentinel_parent = str(sentinel_path.parent.resolve()).replace("\\", "/").lower()
    canon_root = data["canonical_root"].replace("\\", "/").lower()
    assert sentinel_parent in canon_root or canon_root in sentinel_parent, (
        f"sentinel canonical_root {canon_root!r} does not match its location {sentinel_parent!r}"
    )


def test_constants_sha256_is_actually_constants():
    """The sentinel's constants_sha256 must be the SHA-256
    of the canonical config/constants.py file. If it ever
    differs, the sentinel was forged or the constants were
    changed without re-stamping."""
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("wcp",
        Path(__file__).parent.parent / "04_Validation" / "scripts" / "which_canonical.py")
    wcp = module_from_spec(spec)
    spec.loader.exec_module(wcp)
    sentinel_path = Path("CANONICAL.sentinel")
    data = json.loads(sentinel_path.read_text(encoding="utf-8"))
    constants_path = Path("02_Technical") / "config" / "constants.py"
    actual_hash = hashlib.sha256(constants_path.read_bytes()).hexdigest()
    assert data["constants_sha256"] == actual_hash, (
        f"sentinel constants_sha256 is stale: {data['constants_sha256']!r} "
        f"vs actual {actual_hash!r}. Re-stamp the sentinel."
    )


def test_resolver_finds_exactly_one():
    """The resolver, run with the default search roots, must
    find exactly one canonical tree. The canonical is the
    project root containing this test file."""
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("wcp",
        Path(__file__).parent.parent / "04_Validation" / "scripts" / "which_canonical.py")
    wcp = module_from_spec(spec)
    spec.loader.exec_module(wcp)
    result = wcp.resolve_canonical(wcp.SEARCH_ROOTS)
    assert result["status"] == "unique", f"expected unique, got {result}"
    root = result["match"]["root"]
    sentinel_path = Path("CANONICAL.sentinel")
    expected_root = str(sentinel_path.parent.resolve()).lower()
    assert root.lower() == expected_root, (
        f"resolver found {root!r} but expected {expected_root!r}"
    )


def test_no_network_imports():
    """The resolver must be offline (no network imports).
    Same law as the rest of the audit path."""
    import subprocess
    proc = subprocess.run(
        ["python", "04_Validation/scripts/audit_no_network.py",
         "04_Validation/scripts/which_canonical.py"],
        capture_output=True, text=True,
        cwd=Path(__file__).parent.parent,
    )
    # The audit_no_network.py script returns 0 on pass.
    assert proc.returncode == 0, (
        f"which_canonical.py has network imports: {proc.stdout} {proc.stderr}"
    )
