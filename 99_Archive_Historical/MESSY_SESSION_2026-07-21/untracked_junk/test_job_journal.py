"""
Order Get It Right -- Job Upsert Journal Tests.

Locks the O(1) append-only upsert journal added 2026-07-20 to the job
registry (implemented inside src.io.vault_io, used by
src.agents.job_delegator).

The job registry is now a frozen snapshot (``job_registry.json``) + an
append-only JSONL upsert journal (``job_chain.jsonl``) + a tail cache
(``job_chain_tail.json``). Unlike the facts chain (pure append), jobs use
UPSERT semantics (a job's status mutates QUEUED -> IN_PROGRESS ->
COMPLETED), so the journal is full-job-state lines keyed by ``job_id`` and
materialisation replays snapshot-then-journal with last-write-wins per id.

These tests run against an ISOLATED temp vault (never the production
``03_Vault``) by redirecting ``vault_io.VAULT_DIR``. They reach the
delegator through ``app_module`` (00-99 boundary: tests may only import
``src.server.app``).
"""
import sys

import pytest
from fastapi.testclient import TestClient

from src.server.app import app  # whitelisted import (00-99 boundary)

client = TestClient(app)
app_module = sys.modules["src.server.app"]
vault_io = app_module.vault_io


@pytest.fixture
def temp_vault(tmp_path, monkeypatch):
    """Point vault_io at an isolated temp vault dir."""
    vault_dir = tmp_path / "03_Vault"
    vault_dir.mkdir()
    monkeypatch.setattr(vault_io, "VAULT_DIR", vault_dir)
    return vault_dir


def _new_delegator():
    """Construct a fresh delegator against the (temp) vault.

    00-99 boundary: tests may only import ``src.server.app``. The
    delegator class is reachable as an attribute of the already-imported
    app module (app.py imports ``AgentJobDelegator`` at module level). We
    pass no ``tau`` so the delegator constructs its own ``TauFirewall``
    (its constructor default), avoiding any direct ``src.agents.*`` import
    from the test.
    """
    return app_module.AgentJobDelegator()


def test_job_journal_round_trip_preserves_upserted_state(temp_vault):
    """Create/claim/close a job through one delegator, then a FRESH
    delegator must materialise the upserted final state from snapshot +
    journal. Proves the journal + _load round-trip works and that a status
    transition (the whole point of upsert semantics) survives a reload."""
    d1 = _new_delegator()
    assert d1.list_all_jobs() == [], "fresh delegator should start empty"

    jid = d1.create_job_token(
        assigner="Audit_Review_Agent",
        target_agent="Lattice_Compute_Agent",
        task_urn="OGIR:02:COMPUTE_LATTICE",
        data={"x": 1},
    )
    # Journal must now hold exactly one upsert line (the QUEUED state).
    journal = vault_io._read_job_journal()
    assert len(journal) == 1
    assert journal[0]["job_id"] == jid
    assert journal[0]["status"] == "QUEUED"

    d1.claim_job(jid)
    d1.close_job(jid, result_hash="a" * 64, status="COMPLETED")

    # The journal now has three lines for the same id; last-write-wins.
    journal = vault_io._read_job_journal()
    assert len(journal) == 3
    assert [j["status"] for j in journal] == ["QUEUED", "IN_PROGRESS", "COMPLETED"]

    # Fresh delegator -- proves _load materialises the journal.
    d2 = _new_delegator()
    jobs = d2.list_all_jobs()
    assert len(jobs) == 1, f"fresh delegator saw {len(jobs)} jobs, expected 1"
    assert jobs[0]["job_id"] == jid
    assert jobs[0]["status"] == "COMPLETED", (
        f"upserted status not materialised: got {jobs[0]['status']!r}"
    )
    assert jobs[0]["result_seal"] == "a" * 64
def test_job_materialisation_is_last_write_wins_per_id(temp_vault):
    """Directly assert the materialisation rule: for a job_id present in
    both the snapshot and the journal, the JOURNAL wins; for a job_id with
    multiple journal lines, the LAST line wins."""
    d = _new_delegator()
    jid = d.create_job_token("A", "B", "OGIR:01:DO", data=None)
    # Snapshot the QUEUED state into the registry file, then keep mutating
    # via the journal -- the journal must override the snapshot.
    snap = vault_io.read_job_registry()
    vault_io.write_job_registry(snap)  # folds journal into snapshot, clears it
    assert vault_io._read_job_journal() == []

    d.claim_job(jid)  # appends IN_PROGRESS to the journal
    d.close_job(jid, result_hash="b" * 64, status="COMPLETED")  # COMPLETED

    mat = vault_io.read_job_registry()
    target = next(j for j in mat["jobs"] if j["job_id"] == jid)
    assert target["status"] == "COMPLETED"
    assert target["result_seal"] == "b" * 64


def test_job_compaction_folds_journal_and_preserves_state(temp_vault):
    """Compaction folds the journal into the snapshot and clears the
    journal; the materialised state is unchanged and a fresh delegator
    sees the same jobs."""
    d = _new_delegator()
    jid1 = d.create_job_token("A", "B", "OGIR:01:DO1", None)
    jid2 = d.create_job_token("A", "B", "OGIR:01:DO2", None)
    d.close_job(jid1, result_hash="c" * 64, status="COMPLETED")

    vault_io._compact_job_chain()
    assert vault_io._read_job_journal() == [], "compaction must clear the journal"

    snap = vault_io.read_job_registry()
    assert snap["jobCount"] == 2
    statuses = {j["job_id"]: j["status"] for j in snap["jobs"]}
    assert statuses == {jid1: "COMPLETED", jid2: "QUEUED"}

    # Fresh delegator sees the post-compaction state.
    d2 = _new_delegator()
    assert len(d2.list_all_jobs()) == 2


def test_job_journal_survives_partial_trailing_line(temp_vault):
    """A crashed upsert leaves a partial trailing journal line; the next
    read must discard it (not raise) and the next append must truncate it
    so the journal stays parseable."""
    d = _new_delegator()
    jid = d.create_job_token("A", "B", "OGIR:01:DO", None)
    # Corrupt the journal with a partial trailing line.
    jp = vault_io._job_journal_path()
    with open(jp, "a", encoding="utf-8") as f:
        f.write('{"job_id": "bogus", "status": "QU')  # no closing -- partial
    # Read must not raise and must drop the partial line.
    journal = vault_io._read_job_journal()
    assert all("status" in j and "job_id" in j for j in journal)
    assert len(journal) == 1  # only the valid QUEUED line
    # The next upsert truncates the partial line and writes cleanly.
    d.claim_job(jid)
    journal = vault_io._read_job_journal()
    assert journal[-1]["status"] == "IN_PROGRESS"
    assert all("QUE" not in j.get("job_id", "") for j in journal)


def test_concurrent_job_upserts_do_not_lose_state(temp_vault):
    """Regression: concurrent job upserts must not lose a job's latest state.

    Before the cross-process job-journal lock (2026-07-20), two concurrent
    ``append_job_upsert`` calls could both read the same tail, both append a
    journal line, and the later writer's tail write would clobber the earlier
    one's ``jobCount``. More importantly, the partial-line truncation in
    ``_append_job_journal_line`` is itself a read-seek-truncate that is NOT
    atomic across threads -- two threads both seeking to end-of-file and
    truncating could corrupt the journal (interleaved partial writes).

    This test fires N threads that each create a DISTINCT job (so there is no
    logical contention on a single job_id) and then materialises the registry
    from a FRESH delegator. The fix is correct iff all N jobs survive with
    their final COMPLETED state -- no job lost, no duplicate job_id, and the
    materialised jobCount equals N. This mirrors the facts-chain fork test
    (test_vault_journal.test_concurrent_appends_do_not_fork) but for the
    upsert/durability semantics of the job journal.
    """
    import threading

    d = _new_delegator()
    n = 16
    errors = []

    def worker(i):
        try:
            jid = d.create_job_token(
                assigner="A",
                target_agent="B",
                task_urn=f"OGIR:01:DO{i}",
                data={"i": i},
            )
            d.claim_job(jid)
            d.close_job(jid, result_hash=f"{i:064d}", status="COMPLETED")
        except Exception as e:  # noqa: BLE001 - surface to main thread
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, f"workers raised: {errors}"

    # Materialise from a FRESH delegator (re-reads snapshot + journal) so we
    # prove the on-disk state -- not just the in-memory list -- is complete.
    d2 = _new_delegator()
    jobs = d2.list_all_jobs()
    assert len(jobs) == n, f"expected {n} jobs to survive, got {len(jobs)}"

    # No duplicate job_ids (the upsert race signature).
    ids = [j["job_id"] for j in jobs]
    assert len(set(ids)) == len(ids), f"duplicate job_ids: {ids}"

    # Every job must have reached its final COMPLETED state (no lost upsert).
    statuses = [j["status"] for j in jobs]
    assert all(s == "COMPLETED" for s in statuses), (
        f"not all jobs reached COMPLETED: {statuses}"
    )

    # The tail cache's jobCount must agree with the materialised registry.
    tail = vault_io._read_job_tail()
    assert tail.get("jobCount") == n, (
        f"tail jobCount {tail.get('jobCount')} != {n} (race clobbered the tail)"
    )


def test_identical_same_second_jobs_get_distinct_job_ids(temp_vault):
    """Regression: two jobs with identical args created in the same wall-clock
    second must get DISTINCT job_ids.

    Before the uuid4 nonce fix (2026-07-21), ``create_job_token`` derived
    ``job_id = sha256(json.dumps(job_block, sort_keys=True))`` where the job
    block carried only a second-granularity timestamp (``...:%SZ``) plus the
    payload. Two calls in the same second with identical
    assigner/target/task/data therefore hashed to the SAME job_id. The second
    job was appended to ``_jobs`` with a duplicate id, ``_find()`` always
    returned the FIRST record (so the second hand-off could never be
    independently claimed/closed), and in the upsert journal (last-write-wins
    per job_id) the second job's QUEUED line could overwrite the first job's
    COMPLETED state on materialisation -- silently losing a job's final state.

    This test creates two identical jobs back-to-back, then a FRESH delegator
    materialises the registry. The fix is correct iff both jobs survive with
    DISTINCT ids and BOTH can be claimed and closed independently. We also
    assert the tail jobCount is 2 (no state was lost).
    """
    d = _new_delegator()

    # Two identical hand-offs in the same second (no sleep -- the bug fires
    # when the truncated timestamp collides, which happens whenever the two
    # calls land in the same wall-clock second).
    jid1 = d.create_job_token(
        assigner="Form_Entry_Agent",
        target_agent="Audit_Review_Agent",
        task_urn="OGIR:02:AUDIT_TEXT",
        data={"statement": "same statement, same second"},
    )
    jid2 = d.create_job_token(
        assigner="Form_Entry_Agent",
        target_agent="Audit_Review_Agent",
        task_urn="OGIR:02:AUDIT_TEXT",
        data={"statement": "same statement, same second"},
    )

    # The core regression assertion: the two ids MUST differ.
    assert jid1 != jid2, (
        f"identical same-second jobs collided on job_id {jid1!r}; "
        f"the second hand-off is orphaned and unclaimable"
    )

    # Both jobs must be independently claimable + closable. Pre-fix, claiming
    # jid2 would mutate jid1's record (because _find returned the first match)
    # and jid2's close would land on the wrong record.
    d.claim_job(jid1)
    d.close_job(jid1, result_hash="1" * 64, status="COMPLETED")
    d.claim_job(jid2)
    d.close_job(jid2, result_hash="2" * 64, status="COMPLETED")

    # Materialise from a FRESH delegator (re-reads snapshot + journal) so the
    # assertion is against the on-disk state, not the in-memory list.
    d2 = _new_delegator()
    jobs = d2.list_all_jobs()
    assert len(jobs) == 2, f"expected 2 jobs to survive, got {len(jobs)}"

    ids = [j["job_id"] for j in jobs]
    assert len(set(ids)) == 2, f"duplicate job_ids after reload: {ids}"
    assert set(ids) == {jid1, jid2}, f"unexpected ids after reload: {ids}"

    # Both jobs must have reached their OWN final state (no cross-contamination
    # of result_seal, which is the signature of the _find-returns-first bug).
    by_id = {j["job_id"]: j for j in jobs}
    assert by_id[jid1]["result_seal"] == "1" * 64, (
        f"job1 result_seal clobbered: {by_id[jid1]['result_seal']!r}"
    )
    assert by_id[jid2]["result_seal"] == "2" * 64, (
        f"job2 result_seal clobbered: {by_id[jid2]['result_seal']!r}"
    )
    assert all(j["status"] == "COMPLETED" for j in jobs), (
        f"not both jobs reached COMPLETED: {[j['status'] for j in jobs]}"
    )

    # The tail cache's jobCount must agree with the materialised registry.
    tail = vault_io._read_job_tail()
    assert tail.get("jobCount") == 2, (
        f"tail jobCount {tail.get('jobCount')} != 2 (a job's state was lost)"
    )