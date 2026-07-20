"""
Order Get It Right -- Vault Append-Only Journal Tests.

Locks the O(1) append journal added 2026-07-20 to the vault's Merkle
chain (implemented inside src.io.vault_io).

The journal splits the facts registry into a frozen snapshot
(``facts_registry.json``) + an append-only JSONL journal
(``facts_chain.jsonl``) + a tail cache (``facts_chain_tail.json``). These
tests verify, against an ISOLATED temp vault (never the production
``03_Vault``), that append/compaction/crash-recovery/reseed-guard all
keep the chain internally consistent: the ``merkle_root`` reported by
``read_facts_registry`` equals the recomputed root of all blocks.

Boundary compliance (00-99): tests may NOT import from ``src.`` directly
except the whitelisted ``from src.server.app import app``. We reach
``vault_io`` through ``app_module.vault_io`` (the app already imports
it), mirroring test_vault_reseed_guard.py. We re-derive the Merkle root
inline using ``app_module.canonical_dumps`` rather than importing
``src.verify_chain``. The production 03_Vault is never touched: every
test redirects ``vault_io.VAULT_DIR`` to a temp directory.
"""
import hashlib
import sys

import pytest
from fastapi.testclient import TestClient

from src.server.app import app  # whitelisted import (00-99 boundary)

client = TestClient(app)
app_module = sys.modules["src.server.app"]
vault_io = app_module.vault_io
canonical_dumps = app_module.canonical_dumps


def _recompute_root(blocks):
    """Re-derive the Merkle root by walking blocks in order, mirroring
    src.verify_chain._recompute_root but inline (tests cannot import it)."""
    previous_hash = "0" * 64
    for block in blocks:
        block_payload = {
            "event": block.get("event_type"),
            "payload": block.get("payload", {}),
            "ts": block.get("timestamp"),
        }
        serialised = canonical_dumps(block_payload)
        expected = hashlib.sha256((previous_hash + serialised).encode("utf-8")).hexdigest()
        if expected != block.get("current_hash"):
            return expected
        previous_hash = expected
    return previous_hash


def _verify(temp_vault):
    """Verify snapshot+journal re-derives to the reported root."""
    data = vault_io.read_facts_registry()
    blocks = data.get("blocks", [])
    recomputed = _recompute_root(blocks)
    claimed = blocks[-1]["current_hash"] if blocks else "0" * 64
    return (recomputed == claimed, len(blocks))


@pytest.fixture
def temp_vault(tmp_path, monkeypatch):
    """Point vault_io at an isolated temp vault dir."""
    vault_dir = tmp_path / "03_Vault"
    vault_dir.mkdir()
    monkeypatch.setattr(vault_io, "VAULT_DIR", vault_dir)
    return vault_dir


def _seed_first_block(vault_dir):
    return vault_io.append_block("GENESIS", {"note": "first"})


def test_append_produces_verifiable_chain(temp_vault):
    """Core invariant: appended blocks re-derive to the reported root."""
    _seed_first_block(temp_vault)
    vault_io.append_block("FACT_ADDED", {"id": "f1", "claim": "a"})
    vault_io.append_block("FACT_ADDED", {"id": "f2", "claim": "b"})
    matches, count = _verify(temp_vault)
    assert matches, f"chain does not verify after 3 appends (count={count})"
    assert count == 3


def test_block_shape_is_identical_to_pre_journal(temp_vault):
    """Block dict shape and hash math unchanged from the pre-journal code."""
    b1 = _seed_first_block(temp_vault)
    assert set(b1.keys()) == {
        "index", "timestamp", "event_type", "previous_hash",
        "current_hash", "payload", "integrity_digest",
    }
    assert b1["index"] == 1
    assert b1["previous_hash"] == "0" * 64
    block_payload = {"event": "GENESIS", "payload": {"note": "first"}, "ts": b1["timestamp"]}
    expected = hashlib.sha256(("0" * 64 + canonical_dumps(block_payload)).encode("utf-8")).hexdigest()
    assert b1["current_hash"] == expected
    b2 = vault_io.append_block("FACT_ADDED", {"id": "f1"})
    assert b2["index"] == 2
    assert b2["previous_hash"] == b1["current_hash"]


def test_compaction_folds_journal_and_chain_still_verifies(temp_vault):
    """Compaction folds journal into snapshot; chain still verifies."""
    _seed_first_block(temp_vault)
    for i in range(5):
        vault_io.append_block("FACT_ADDED", {"i": i})
    vault_io._compact_chain()
    jp = vault_io._chain_journal_path()
    if jp.exists():
        assert jp.read_text(encoding="utf-8").strip() == ""
    snap = vault_io._read_json(vault_io.facts_registry_path(), {"blocks": []})
    assert len(snap["blocks"]) == 6
    matches, count = _verify(temp_vault)
    assert matches, f"post-compaction verify failed (count={count})"
    assert count == 6
    vault_io.append_block("FACT_ADDED", {"i": 99})
    matches2, count2 = _verify(temp_vault)
    assert matches2, f"post-compaction append verify failed (count={count2})"
    assert count2 == 7


def test_compaction_crash_leaves_stale_journal_self_heals(temp_vault):
    """If compaction writes the snapshot but dies before truncating the
    journal, the stale journal (now duplicating the snapshot) must
    self-heal on read: no duplicate blocks, root still verifies, and the
    next append links correctly. This is the crash-safety gap closed
    2026-07-20 (index-based dedup in read_facts_registry / _rebuild_tail /
    _compact_chain)."""
    _seed_first_block(temp_vault)
    for i in range(5):
        vault_io.append_block("FACT_ADDED", {"i": i})
    # Simulate compaction completing the snapshot write but dying BEFORE
    # truncating the journal: fold blocks into snapshot, leave journal intact.
    snapshot = vault_io._read_json(vault_io.facts_registry_path(), {"blocks": []})
    snapshot_blocks = list(snapshot.get("blocks", []))
    snapshot_blocks.extend(vault_io._read_chain_journal())
    root = snapshot_blocks[-1]["current_hash"] if snapshot_blocks else "0" * 64
    vault_io._atomic_write_json(
        vault_io.facts_registry_path(),
        {"merkle_root": root, "blocks": snapshot_blocks},
    )
    # Journal is deliberately NOT truncated -- it still holds blocks 1..6
    # that the snapshot now also holds. This is the post-crash state.
    jp = vault_io._chain_journal_path()
    assert jp.exists() and jp.read_text(encoding="utf-8").strip() != ""

    # The live read MUST NOT double the blocks.
    data = vault_io.read_facts_registry()
    assert len(data["blocks"]) == 6, "stale journal duplicated blocks after crash"
    matches, count = _verify(temp_vault)
    assert matches, f"post-compaction-crash verify failed (count={count})"
    assert count == 6

    # The tail rebuild must also see the dedup'd count, so the next append
    # links to index 7 (not 13) with the correct previous_hash.
    vault_io._chain_tail_path().unlink()  # force a tail rebuild from the stale state
    b7 = vault_io.append_block("FACT_ADDED", {"i": 99})
    assert b7["index"] == 7, f"post-crash append got wrong index {b7['index']}"
    matches2, count2 = _verify(temp_vault)
    assert matches2, f"post-crash append verify failed (count={count2})"
    assert count2 == 7


def test_reseed_guard_fires_on_empty_snapshot(temp_vault):
    """Empty-but-present snapshot with no journal must raise VAULT_RESEED_REFUSED."""
    vault_io._atomic_write_json(
        vault_io.facts_registry_path(),
        {"merkle_root": "0" * 64, "blocks": []},
    )
    with pytest.raises(RuntimeError, match="VAULT_RESEED_REFUSED"):
        vault_io.append_block("GENESIS", {"note": "should be refused"})


def test_partial_journal_line_is_recovered(temp_vault):
    """A partial trailing journal line is discarded; chain still verifies."""
    _seed_first_block(temp_vault)
    vault_io.append_block("FACT_ADDED", {"i": 1})
    jp = vault_io._chain_journal_path()
    with open(jp, "a", encoding="utf-8") as f:
        f.write('{"index":3,"broken":')  # truncated, unparseable
    data = vault_io.read_facts_registry()
    assert len(data["blocks"]) == 2  # partial line discarded
    matches, count = _verify(temp_vault)
    assert matches, f"post-crash verify failed (count={count})"
    assert count == 2
    b3 = vault_io.append_block("FACT_ADDED", {"i": 2})
    assert b3["index"] == 3
    matches2, count2 = _verify(temp_vault)
    assert matches2
    assert count2 == 3


def test_tail_cache_rebuild_when_deleted(temp_vault):
    """Deleting the tail cache must not break appends."""
    _seed_first_block(temp_vault)
    vault_io.append_block("FACT_ADDED", {"i": 1})
    tp = vault_io._chain_tail_path()
    if tp.exists():
        tp.unlink()
    b3 = vault_io.append_block("FACT_ADDED", {"i": 2})
    assert b3["index"] == 3
    matches, count = _verify(temp_vault)
    assert matches
    assert count == 3


def test_many_appends_stay_correct(temp_vault):
    """50 appends; chain verifies with contiguous linkage."""
    _seed_first_block(temp_vault)
    for i in range(50):
        vault_io.append_block("FACT_ADDED", {"i": i})
    matches, count = _verify(temp_vault)
    assert matches, f"50-append verify failed (count={count})"
    assert count == 51
    blocks = vault_io.read_facts_registry()["blocks"]
    for idx, b in enumerate(blocks):
        assert b["index"] == idx + 1
        if idx > 0:
            assert b["previous_hash"] == blocks[idx - 1]["current_hash"]


def test_merkle_stats_and_all_consistent_after_journal(temp_vault):
    """merkle_stats / merkle_all reflect snapshot + journal consistently."""
    _seed_first_block(temp_vault)
    vault_io.append_block("FACT_ADDED", {"i": 1})
    stats = vault_io.merkle_stats()
    all_blocks = vault_io.merkle_all()
    assert stats["blockCount"] == 2 == len(all_blocks)
    assert stats["merkleRoot"] == all_blocks[-1]["current_hash"]
    reg = vault_io.read_facts_registry()
    assert reg["merkle_root"] == all_blocks[-1]["current_hash"]


def test_concurrent_appends_do_not_fork(temp_vault):
    """Regression: concurrent appenders must not fork the Merkle chain.

    Before the cross-process append lock (2026-07-20), two concurrent
    ``append_block`` calls could read the same tail, both compute the same
    ``next_index``, and both append a journal line -- producing two DIFFERENT
    blocks with the same index (a fork) and a divergent Merkle root. This is
    exactly the corruption that broke the production vault at block 25250
    (duplicate indices 25260/25263 plus a truncated fragment line).

    This test seeds one block, then fires N appenders from real OS threads
    (the same in-process concurrency that ``append_block`` must serialise),
    and asserts:
      - exactly N+1 blocks landed (no duplicates, no lost appends),
      - indices are contiguous 1..N+1 with no duplicates,
      - the chain re-derives to a single Merkle root (no fork).
    """
    import threading

    _seed_first_block(temp_vault)
    n = 16
    errors = []

    def appender(i):
        try:
            vault_io.append_block("FACT_ADDED", {"worker": i})
        except Exception as e:  # noqa: BLE001 - surface to main thread
            errors.append(e)

    threads = [threading.Thread(target=appender, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, f"appenders raised: {errors}"

    matches, count = _verify(temp_vault)
    assert matches, f"concurrent-append chain does not verify (count={count})"
    assert count == n + 1, f"expected {n + 1} blocks, got {count}"

    blocks = vault_io.read_facts_registry()["blocks"]
    indices = [b["index"] for b in blocks]
    assert indices == list(range(1, n + 2)), f"non-contiguous/duplicate indices: {indices}"
    # No two blocks may share an index (the fork signature).
    assert len(set(indices)) == len(indices), "duplicate block indices -> fork"