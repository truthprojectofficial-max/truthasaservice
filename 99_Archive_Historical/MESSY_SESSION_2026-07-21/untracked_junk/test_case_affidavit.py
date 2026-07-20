"""
Order Get It Right -- case-specific affidavit test.

Verifies the case-specific s.177 affidavit surface exposed via the HTTP API:
  - GET  /api/affidavit/case/{case_id}/preview  (dry-run, no disk write)
  - POST /api/affidavit/case/{case_id}          (compile + archive)

The case affidavit keeps the full Merkle trail as compact '[SPINE]' entries
while rendering the full factual payload only for the case block(s). The
on-disk vault is read-only here -- the chain stays intact.

Boundary: these tests go through the HTTP API only (the 00-99 boundary test
forbids tests importing from src/ except ``from src.server.app import app``).
The temp-vault redirect is done via monkeypatch on the config module the
endpoints read at call time (``from src.config import VAULT_DIR``), and on
``vault_io`` reached through the app module (already imported by app.py).
"""
import json
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.server.app import app  # noqa: E402  (allowed boundary exception)

client = TestClient(app)
app_module = sys.modules["src.server.app"]
vault_io = app_module.vault_io  # reached via the app, not a direct src import
config_module = sys.modules["src.config"]


def _seed_temp_vault(tmp_path: Path) -> Path:
    """Seed a temp vault with one case block + two unrelated blocks.

    Returns the ledger path. The real production vault is never touched
    because the caller monkeypatches ``config_module.VAULT_DIR`` (which the
    endpoints read via ``from src.config import VAULT_DIR``) and
    ``vault_io.facts_registry_path`` (which append_block uses).
    """
    ledger = tmp_path / "facts_registry.json"
    config_module.VAULT_DIR = tmp_path
    vault_io.facts_registry_path = lambda: ledger
    vault_io.append_block("SYSTEM_EVENT", {"note": "genesis"})
    vault_io.append_block("SYSTEM_EVENT", {"note": "unrelated-1", "big": "x" * 5000})
    vault_io.append_block("AUDIT_CYCLE_COMPLETE", {
        "case": "SELBY-001",
        "finalAction": "REJECT",
        "reason": "Major Failure",
        "payload_blob": "y" * 5000,
    })
    vault_io.append_block("SYSTEM_EVENT", {"note": "unrelated-2", "big": "z" * 5000})
    return ledger


def _read_ledger(ledger: Path) -> dict:
    """Read the live (snapshot + journal) ledger via vault_io so the test
    sees journal-appended blocks too (the snapshot file alone is not updated
    on every append since the 2026-07-20 O(1) journal change). ``vault_io`` is
    already reached via the app module (line 30), so this does not cross the
    00-99 boundary. ``ledger`` is kept as the argument for parity with the
    pre-journal signature; we read the live view, which equals ``ledger``."""
    return vault_io.read_facts_registry()


@pytest.fixture()
def seeded_vault(tmp_path, monkeypatch):
    """Seed a temp vault and point both the API and vault_io at it.

    Restores the real vault paths on teardown so no test state leaks into
    the production chain or into other tests in the suite.
    """
    orig_vault_dir = config_module.VAULT_DIR
    orig_registry_path = vault_io.facts_registry_path
    ledger = _seed_temp_vault(tmp_path)
    yield ledger
    config_module.VAULT_DIR = orig_vault_dir
    vault_io.facts_registry_path = orig_registry_path


def test_case_affidavit_preview_is_focused_and_keeps_trail(seeded_vault):
    """Preview returns a focused exhibit: case payload present, unrelated
    payloads absent, and the full trail as compact [SPINE] entries."""
    ledger = seeded_vault
    r = client.get("/api/affidavit/case/SELBY-001/preview")
    assert r.status_code == 200, f"preview failed: {r.text}"
    body = r.json()
    assert body["preview"] is True
    assert body["wroteToDisk"] is False
    case = body["affidavit"]

    # 1. The case block's factual payload appears; unrelated payloads do not.
    assert "Major Failure" in case, "case block payload missing from case affidavit"
    assert "unrelated-1" not in case, "unrelated payload leaked into case affidavit"
    assert "unrelated-2" not in case, "unrelated payload leaked into case affidavit"

    # 2. The trail must be present: one spine entry per non-case block.
    spine_lines = [ln for ln in case.splitlines() if ln.startswith("[SPINE]")]
    assert len(spine_lines) == 3, (
        f"expected 3 spine entry lines, got {len(spine_lines)}"
    )

    # 3. Standard header + jurisdictional anchors present.
    assert "AFFIDAVIT OF DETERMINISTIC SYSTEM TRUTH" in case
    assert "Section 177" in case
    assert "CASE-SPECIFIC EXHIBIT" in case
    assert "Case blocks     : 1 of 4 total" in case
    # The case block's hash must appear (full factual rendering).
    blocks = _read_ledger(ledger)["blocks"]
    case_block = [b for b in blocks if b["payload"].get("case") == "SELBY-001"][0]
    assert case_block["current_hash"] in case, "case block hash missing from affidavit"


def test_case_affidavit_preview_does_not_mutate_chain(seeded_vault):
    """Two preview calls must not change the on-disk Merkle chain."""
    ledger = seeded_vault
    before = _read_ledger(ledger)
    before_count = len(before["blocks"])
    before_root = before["merkle_root"]

    r1 = client.get("/api/affidavit/case/SELBY-001/preview")
    r2 = client.get("/api/affidavit/case/SELBY-001/preview")
    assert r1.status_code == 200
    assert r2.status_code == 200

    after = _read_ledger(ledger)
    assert len(after["blocks"]) == before_count, "preview mutated block count"
    assert after["merkle_root"] == before_root, "preview mutated Merkle root"


def test_case_affidavit_unknown_case_returns_error_without_raising(seeded_vault):
    """An unknown case id must return a clear error, not a 500/raise."""
    r = client.get("/api/affidavit/case/DOES-NOT-EXIST/preview")
    # The generator returns an "ERROR:" string rather than raising, so the
    # endpoint still returns 200 with the error in the affidavit body.
    assert r.status_code == 200, f"unknown-case preview failed: {r.text}"
    body = r.json()
    assert body["affidavit"].startswith("ERROR:")
    assert "DOES-NOT-EXIST" in body["affidavit"]


def test_case_affidavit_post_archives_outside_chain(seeded_vault):
    """POST compiles, writes the exhibit outside the chain, and does not
    mutate the chain's block count or Merkle root."""
    ledger = seeded_vault
    before = _read_ledger(ledger)
    before_count = len(before["blocks"])
    before_root = before["merkle_root"]

    r = client.post("/api/affidavit/case/SELBY-001")
    assert r.status_code == 200, f"post failed: {r.text}"
    body = r.json()
    assert body["caseId"] == "SELBY-001"

    # An archive path must be returned and the file must exist on disk.
    out_path = body["path"]
    assert isinstance(out_path, str) and len(out_path) > 0, "post returned no path"
    assert os.path.exists(out_path), "case affidavit file not written to disk"
    assert os.path.basename(out_path) == "affidavit_SELBY-001.txt"

    # The exhibit content must carry the case payload and the trail.
    written = Path(out_path).read_text(encoding="utf-8")
    assert "Major Failure" in written, "archived exhibit missing case payload"
    assert "[SPINE]" in written, "archived exhibit missing the Merkle trail"

    # The chain must be untouched: same block count, same Merkle root.
    after = _read_ledger(ledger)
    assert len(after["blocks"]) == before_count, "post mutated block count"
    assert after["merkle_root"] == before_root, "post mutated Merkle root"