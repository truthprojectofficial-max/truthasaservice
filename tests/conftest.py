"""Project-wide pytest configuration.

TEMP-VAULT FIXTURE (added 2026-07-24, closes the chain-pollution finding
from SESSION_LOG_2026-07-24.md section 1B):

Every test that seals a block (directly or via the FastAPI TestClient)
seals to a THROWAWAY vault in a per-test temp directory, NOT to the
live trust anchor at 03_Vault/facts_registry.json. The live chain is
read-only during tests.

Why: the session log documented that tests were appending JOB_QUEUED /
JOB_DELEGATED / TEST_LOOP_SEALED blocks to the real 40k+ block chain.
After a test session the vault had hundreds of pollution blocks and
the chain lineage broke at block 41,919. The workaround was
`git checkout HEAD -- 03_Vault/facts_registry.json` after every test
run. This fixture is the real fix: tests never touch the live vault.

Ethos alignment (AGENTS.md): "the chain is the source of truth for
*what the engine decided*". Test fixtures are not engine decisions.
Sealing them to the real chain was the opposite of the ethos -- it
polluted the witness with non-decisions. The temp vault is the
throwaway witness; the real vault is the trust anchor.

Security: the temp vault is a pytest tmp_path -- no secrets, no real
operator decisions. The real vault at 03_Vault/ is never opened for
writing by tests. Attack surface goes down.

Traceability: test seals land in the temp witness, attributed to the
same CHAIN_OPERATOR_ID ("OGIR-OPERATOR") used in production. The
chain-integrity mechanism (seal + verify) is still exercised
end-to-end on every test that calls append_block / the orchestrator.
The 40k-block real chain is verified separately by the manual/CI
command `python -m src.verify_chain` (which reads the real vault,
not the temp one).

Reversibility: delete this file and the test harness reverts to the
prior behaviour. One `git checkout` undoes it.

The BARK_LOG_PATH (04_Validation/scripts/last_seal.log) is left
pointing at the real project root. Test bark lines are cosmetic noise
in a secondary, append-only witness -- they do not affect the trust
anchor (the chain). Redirecting the bark log would require modifying
multiple bark tests for no security benefit.
"""
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

# Boundary-clean import: only src.server.app is whitelisted by the
# 00-99 boundary test (tests/test_00_99_boundary.py). We reach
# vault_io THROUGH the app module, the same pattern used by
# test_vault_reseed_guard.py:27-28.
from src.server import app as app_module  # noqa: E402
vault_io = app_module.vault_io  # noqa: E402


@pytest.fixture(autouse=True)
def _temp_vault(tmp_path, monkeypatch):
    """Redirect the Merkle chain to a per-test temp directory.

    Every test gets a fresh temp vault with one genesis block. The
    re-seed guard does not fire because the file is created by the
    genesis seal (it does not pre-exist as an empty file). All seals
    during the test land in the temp vault. When the test finishes,
    monkeypatch restores the real paths and tmp_path is discarded.

    Subprocess tests (e.g. test_post_seal_bark.py) inherit the
    OGIR_TEST_VAULT_DIR env var so their wrapper scripts can redirect
    vault_io before calling append_block.
    """
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    facts_path = vault_dir / "facts_registry.json"
    job_path = vault_dir / "job_registry.json"
    law_path = vault_dir / "law.json"

    monkeypatch.setattr(vault_io, "VAULT_DIR", vault_dir)
    monkeypatch.setattr(vault_io, "facts_registry_path", lambda: facts_path)
    monkeypatch.setattr(vault_io, "job_registry_path", lambda: job_path)
    monkeypatch.setattr(vault_io, "law_path", lambda: law_path)
    monkeypatch.setenv("OGIR_TEST_VAULT_DIR", str(vault_dir))

    # Seed a genesis block so the re-seed guard does not fire on the
    # first real test seal. The file does not pre-exist, so the guard
    # (which only fires when the file EXISTS but has zero blocks) is
    # bypassed. append_block creates block index 1.
    vault_io.append_block("TEST_VAULT_GENESIS", {
        "fix_id": "conftest",
        "files_changed": ["tests/conftest.py: temp-vault fixture"],
        "bin_id": "pytest-fixture",
        "note": "Throwaway genesis block for test isolation. Not a real decision.",
    })

    yield