# Order Get It Right -- Instruction and Care Manual

**Date:** 2026-07-20
**Scope:** the append-only journal + cross-process append-lock hardening
landed this session in `src/io/vault_io.py`, and the supporting changes in
`src/server/app.py` and `tests/test_job_journal.py`.
**Operator:** Justin Barnett
**Baseline at start of session:** chain MATCH, 26,593 blocks, root
`629fb2995e3e9ab5b10b6de02b25348f074b8a698c059d207207746845a2c8f0`

> This manual is the care-and-feeding guide for the new journal subsystem.
> It is written for the operator who has to keep the build alive after the
> person who wrote it is gone. It is NOT a contract. It is the honest list
> of what the journal does, what it does NOT do, what to check daily, and
> what to do if something breaks. The chain is the source of truth; this
> document is the human-readable explanation of it.

---

## 1. What changed this session (and why you should care)

Two real bugs were fixed and one regression test was added. Neither bug was
visible in normal single-user operation; both only bit under concurrent
writes. Because the build is a single-operator, single-laptop, air-gap
tool, the bugs were latent -- but "latent" is not "safe", so they are now
fixed and locked in with tests.

| # | File | What | Why it matters |
|---|------|------|----------------|
| 1 | `src/io/vault_io.py` | The facts-chain append lock was extracted into a reusable `_file_lock(lock_path, in_process_lock)` helper, and a NEW `_job_append_lock` was added. `append_job_upsert` now runs its whole critical section under that lock. | Without the lock, two concurrent job upserts could both read the same tail, both append a journal line, and the later writer clobbered the earlier one's `jobCount`. A crash between the two writes could LOSE a job's latest state on restart. |
| 2 | `src/io/vault_io.py` | `append_job_upsert` now recomputes the tail `jobCount` from the materialised registry (`_materialise_job_registry()["jobCount"]`) instead of propagating the stale tail value. | The old code did `new_count = tail.get("jobCount", 0)` then wrote it back UNCHANGED, so the tail's `jobCount` NEVER advanced when a new job was added. It only got corrected on compaction or a tail rebuild. The regression test caught `tail jobCount 1 != 16`. |
| 3 | `src/server/app.py` | The `_lifespan` CONCURRENCY comment was corrected. | The old comment claimed a multi-worker race would leave "the chain would still verify but be missing blocks." That was WRONG -- the race actually FORKED the chain (duplicate indices + divergent `current_hash`), which is exactly what broke the production vault at block 25250. The comment now reflects the real failure mode and the lock fix. |
| 4 | `tests/test_job_journal.py` | New test `test_concurrent_job_upserts_do_not_lose_state`. | Fires 16 OS threads, each creating a distinct job, and asserts all 16 survive with COMPLETED status, no duplicate `job_id`s, and `tail jobCount == 16`. Mirrors the facts-chain fork test. |

## 2. The two journals (what they are, in plain English)

The vault now has TWO append-only journals. Both work the same way: a frozen
snapshot file + an append-only JSONL journal + a small tail cache. This
split is what makes an append O(1) instead of a full file rewrite.

### 2.1 The facts chain (the audit trail)

```
03_Vault/facts_registry.json     <- frozen snapshot (the blocks up to last compaction)
03_Vault/facts_chain.jsonl       <- append-only journal (one block per line, since compaction)
03_Vault/facts_chain_tail.json   <- small cache: blockCount + merkleRoot
03_Vault/facts_chain.lock        <- cross-process lock file (NEW)
```

Every audit decision, every operator action, every session seal is a block
appended here. This is the Merkle truth ledger. It MUST verify. If it does
not verify, the project's integrity is broken and you stop (see section 5).

### 2.2 The job journal (the delegator state)

```
03_Vault/job_registry.json       <- frozen snapshot (jobs up to last compaction)
03_Vault/job_chain.jsonl         <- append-only upsert journal (one full job state per line)
03_Vault/job_chain_tail.json     <- small cache: jobCount + merkleRoot
03_Vault/job_chain.lock          <- cross-process lock file (NEW)
```

The job journal uses UPSERT semantics: a job's status mutates
QUEUED -> IN_PROGRESS -> COMPLETED, and each transition is a new journal
line for the SAME `job_id`. Materialisation replays snapshot-then-journal
with last-write-wins per id, so the latest state wins. This is NOT a Merkle
chain -- it is a durable, replayable state log.

## 3. How the locks work (so you can explain it to a court)

Both journals now acquire a cross-process exclusive lock around the whole
read-modify-write critical section. The lock is two-layered:

1. **In-process** (`threading.Lock`): acquired first. Cheap, always
   available. Guards the single-process multi-thread case (FastAPI runs
   sync endpoints in a threadpool; the concurrency regression test fires
   real OS threads). Each journal has its own lock so they do not needlessly
   serialise each other: `_chain_process_lock` and `_job_process_lock`.
2. **Cross-process** (OS file lock): acquired second. On Windows this is
   `msvcrt.locking(fileno, LK_LOCK, 1)` on byte 0 of the lock file, with a
   30-second bounded retry loop. On POSIX it is `fcntl.flock(LOCK_EX)` on the
   whole file. The lock file is created (not truncated) so it persists
   across processes.

The critical section for the facts chain is: read tail -> compute next block
(hash of previous + canonical-JSON payload) -> append journal line -> write
tail. The critical section for the job journal is: append journal line ->
materialise registry (snapshot + journal) -> write tail -> maybe compact.

**The lock is released on exit, including on exception.** If a write raises,
the journal is not left half-written and the lock is not held. The next
writer can proceed.

**The lock files are safe to delete.** They are recreated on the next
append. You do not need to back them up. They are NOT part of the audit
trail; they are infrastructure.

## 4. Daily care (what to check, every day you use the build)

These four checks take under 60 seconds and catch 99% of problems.

```powershell
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"

# 1. Chain must verify.
python -m src.verify_chain
# Expected: RESULT: MATCH -- chain is intact.

# 2. Job tail must agree with the materialised registry.
python -c "from src.io import vault_io as v; t=v._read_job_tail(); m=v.read_job_registry(); print('tail=',t.get('jobCount'),'mat=',m['jobCount']); assert t.get('jobCount')==m['jobCount'], 'TAIL DRIFT'"
# Expected: tail= <N> mat= <N>   (same number)

# 3. Fast tests must pass (the journal + lock regression tests live here).
python -m pytest tests/test_vault_journal.py tests/test_job_journal.py tests/test_vault_reseed_guard.py tests/test_smoke.py -q
# Expected: 46 passed

# 4. No leftover partial journal lines (crash recovery).
python -c "from src.io import vault_io as v; j=v._read_job_journal(); print('job journal lines:', len(j)); print('all valid:', all('job_id' in x and 'status' in x for x in j))"
# Expected: all valid: True
```

If any of the four fails, go to section 5.

### 4.1 The numbers that should match

After a clean session, these three numbers MUST be equal:

- `vault_io._read_job_tail()["jobCount"]`
- `vault_io.read_job_registry()["jobCount"]`
- `len(vault_io.read_job_registry()["jobs"])`

If the tail says 12 but the registry says 15, the tail has drifted -- run
the repair in section 5.2. (With the fix from this session, this should
never happen, but the check is cheap and the drift is silent, so check it.)

## 5. What to do if something breaks

### 5.1 The facts chain does not verify (BROKEN)

This is the worst case. The audit trail is broken. STOP. Do not run any
audits. Do not append any blocks. Read
`04_Validation/MAINTENANCE_PLAN.txt` section 3 (Incident Response). The
short version: restore the vault from the last known-good backup (the
hard-copy 1-2-3 backup plan), re-verify, and seal a `CHAIN_RESTORED` block
recording the restore. Do NOT attempt to "fix" the chain by editing JSON by
hand -- that defeats the entire point of the Merkle trail.

### 5.2 The job tail has drifted from the registry (tail != materialised)

This is a DURABILITY issue, not an integrity issue -- the jobs are all still
in the journal, the tail cache is just stale. Repair is one line:

```powershell
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
python -c "from src.io import vault_io as v; v._compact_job_chain(); t=v._read_job_tail(); m=v.read_job_registry(); print('after compaction tail=',t.get('jobCount'),'mat=',m['jobCount'])"
```

Compaction folds the journal into the snapshot, clears the journal, and
rewrites the tail from the materialised registry -- so the numbers will
match after. Then seal a `JOB_TAIL_REPAIRED` block recording the drift you
found and the compaction you ran.

### 5.3 A partial journal line (crash during an append)

If the build crashed mid-append, the journal may have a partial trailing
line (no closing brace). This is EXPECTED and HANDLED: `_read_job_journal`
discards any line that does not parse as valid JSON, and the next
`_append_job_journal_line` truncates the partial line before writing. So
the fix is simply: run any job operation (or the compaction command in
5.2), and the partial line is cleaned up automatically. No manual editing.

### 5.4 The lock file is stuck (a process died holding it)

On Windows, `msvcrt.locking` is released when the file handle is closed,
which the OS does when the process dies. So a stuck lock should not happen.
If it somehow does (a hung process), kill the Python process in Task
Manager, then delete the `.lock` file. The next append recreates it.

## 6. What NOT to do

- **Do NOT run `uvicorn --workers N` with N > 1 without reading the
  `app.py` `_lifespan` comment first.** The cross-process lock now makes
  this SAFE for the chain, but the single-worker default remains the
  deployment recommendation. The session tracker's in-memory `_sessions`
  dict is not shared across workers, so multi-worker would give each worker
  its own session state (a functional surprise, not a crash).
- **Do NOT edit the journal files (`.jsonl`) by hand.** They are append-only
  and parse-strict. A hand-edited line that is not valid canonical JSON will
  be discarded on read, silently losing that block/job-state. The only
  sanctioned write path is `vault_io.append_block` / `append_job_upsert`.
- **Do NOT delete the snapshot files (`facts_registry.json`,
  `job_registry.json`) without first compacting.** The snapshot + journal
  together ARE the state. Deleting the snapshot loses every block/job
  folded into it. Compaction moves the journal into the snapshot; it does
  not delete history.
- **Do NOT back up the `.lock` files.** They are recreated on every append.
  Backing them up and restoring a stale one could cause a spurious lock
  conflict. Back up the three real files per journal (snapshot, journal,
  tail), not the lock.

## 7. When to compact (and when NOT to)

Compaction folds the journal into the snapshot and clears the journal. It
runs automatically every `_JOB_COMPACTION_THRESHOLD` upserts (see
`config/constants.py`). You do NOT need to run it manually in normal use.

Run it manually ONLY if:
- the tail has drifted from the registry (section 5.2), or
- the journal file is getting large and you want to fold it before a backup.

Do NOT compact while a batch audit is running -- wait for it to finish.
Compaction takes the append lock, so a running append would just wait, but
it is cleaner to compact when the system is idle.

## 8. Where everything lives (quick map)

| Artefact | Path | Backed up? |
|----------|------|-----------|
| Facts snapshot | `03_Vault/facts_registry.json` | YES |
| Facts journal | `03_Vault/facts_chain.jsonl` | YES |
| Facts tail | `03_Vault/facts_chain_tail.json` | YES |
| Facts lock | `03_Vault/facts_chain.lock` | no (recreated) |
| Job snapshot | `03_Vault/job_registry.json` | YES |
| Job journal | `03_Vault/job_chain.jsonl` | YES |
| Job tail | `03_Vault/job_chain_tail.json` | YES |
| Job lock | `03_Vault/job_chain.lock` | no (recreated) |
| Chain verifier | `02_Technical/src/verify_chain.py` | (source) |
| Journal code | `02_Technical/src/io/vault_io.py` | (source) |
| Regression tests | `tests/test_vault_journal.py`, `tests/test_job_journal.py` | (source) |

## 9. The one-sentence summary for a court or a new operator

> Every audit decision is sealed to a SHA-256 Merkle chain; every job
> state is appended to a durable upsert journal; both are guarded by a
> cross-process lock so concurrent writes cannot fork the chain or lose a
> job's latest state; the chain is the source of truth and this manual is
> how you keep it honest.

End of manual. The chain is the source of truth.
