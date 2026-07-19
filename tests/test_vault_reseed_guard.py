"""VAULT_RESEED_GUARD regression: append_block refuses to start a fresh
chain when the vault file exists on disk but is empty.

Closes the root-cause follow-up from GEM_DOCS_RECONCILIATION_2026-07-19
section 6. On 2026-07-18 the working-tree vault was re-seeded to 383
blocks because a OneDrive sync event or clean checkout left
facts_registry.json present but empty, and append_block silently
wrote block index 1 with previous_hash=0000. This test proves the
guard now refuses that.

Boundary: these tests access vault_io through app_module (the app
module), not via direct `from src.io.vault_io import ...` (the 00-99
boundary test forbids that). The allowed import is
`from src.server.app import app`; we then reach vault_io via
`app_module.vault_io` (the app already imports it).
"""
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.server.app import app

client = TestClient(app)
app_module = sys.modules["src.server.app"]
vault_io = app_module.vault_io


def _write_empty_vault(path: Path) -> None:
    """Write a valid-but-empty vault file (zero blocks, default root)."""
    path.write_text(
        json.dumps({"merkle_root": "0" * 64, "blocks": []}),
        encoding="utf-8",
    )


def _write_populated_vault(path: Path) -> None:
    """Write a vault with one block so the file is non-empty."""
    path.write_text(
        json.dumps({
            "merkle_root": "abc123",
            "blocks": [{
                "index": 1,
                "timestamp": "2026-07-19T00:00:00Z",
                "event_type": "SEED",
                "previous_hash": "0" * 64,
                "current_hash": "abc123",
                "payload": {},
                "integrity_digest": "def456",
            }],
        }),
        encoding="utf-8",
    )


def test_append_block_refuses_reseed_on_empty_existing_vault(tmp_path, monkeypatch):
    """If the vault file exists but has zero blocks, append_block must
    raise RuntimeError instead of silently starting a fresh chain."""
    fake_vault = tmp_path / "facts_registry.json"
    _write_empty_vault(fake_vault)
    monkeypatch.setattr(vault_io, "facts_registry_path", lambda: fake_vault)

    with pytest.raises(RuntimeError, match="VAULT_RESEED_REFUSED"):
        vault_io.append_block("TEST_EVENT", {"probe": "reseed-guard"})


def test_append_block_works_on_populated_vault(tmp_path, monkeypatch):
    """The guard must NOT fire when the vault has real blocks. A normal
    append on a populated chain must still succeed."""
    fake_vault = tmp_path / "facts_registry.json"
    _write_populated_vault(fake_vault)
    monkeypatch.setattr(vault_io, "facts_registry_path", lambda: fake_vault)

    block = vault_io.append_block("TEST_EVENT_AFTER_GUARD", {"probe": "normal-append"})
    assert block["index"] == 2
    assert block["event_type"] == "TEST_EVENT_AFTER_GUARD"


def test_append_block_works_when_vault_file_absent(tmp_path, monkeypatch):
    """When the vault file does not exist at all, append_block must
    still be able to start a fresh chain (the very first run). The guard
    only fires when the file EXISTS but is empty."""
    fake_vault = tmp_path / "does_not_exist.json"
    assert not fake_vault.exists()
    monkeypatch.setattr(vault_io, "facts_registry_path", lambda: fake_vault)

    block = vault_io.append_block("FIRST_RUN_SEED", {"probe": "first-run"})
    assert block["index"] == 1
    assert block["event_type"] == "FIRST_RUN_SEED"