# Order Get It Right -- Hand-Over Statement

**Session date:** 2026-07-20
**Operator:** Justin Barnett
**Build agent:** Cline (act mode)
**State at hand-over:**
- Chain: MATCH, 26,593 blocks at start; one `CODE_REVIEW_SEALED_2026_07_20`
  block appended this session -- seal block index 26594, hash
  `22f0809d24610ab98106559f203c1c5ec86c5a3c69fb1faec779daa765a6ec79`.
  Chain re-verifies to MATCH after the seal.
- Chain root at start: `629fb2995e3e9ab5b10b6de02b25348f074b8a698c059d207207746845a2c8f0`
- Chain root after seal: `22f0809d24610ab98106559f203c1c5ec86c5a3c69fb1faec779daa765a6ec79`
- Tests (fast suite): 63 passed across vault, job journal, reseed guard,
  smoke, evidence parser, lattice.
- New regression test: `tests/test_job_journal.py::test_concurrent_job_upserts_do_not_lose_state`

---

## 1. What was done in this session

A two-pass code review followed by fixes and a seal. No new features; this
was a hardening and documentation pass.

1. **First pass (review).** Reviewed the concurrency-critical and
   logic-heavy modules: `vault_io.py` (facts chain + job journal),
   `server/app.py` (lifespan/handlers), `session_tracker.py`,
   `evidence_parser.py`, `real_options_lattice.py`, `bbfb_engine.py`.

2. **Second pass (fix).** Two real bugs found and fixed in the job-journal
   append path:
   - **Bug 1 (concurrency):** `append_job_upsert` had no lock around its
     read-modify-write critical section -- the same race that forked the
     facts chain at block 25250. Fixed by refactoring the facts-chain lock
     into a reusable `_file_lock` helper and adding a `_job_append_lock`
     that wraps the whole upsert.
   - **Bug 2 (durability):** `append_job_upsert` propagated the stale tail
     `jobCount` instead of recomputing it, so the tail never advanced on a
     new-job upsert. The new concurrency regression test caught it
     (`tail jobCount 1 != 16`). Fixed by recomputing from
     `_materialise_job_registry()` inside the lock.

3. **Comment correction.** The `_lifespan` CONCURRENCY comment in
   `app.py` claimed the multi-worker race would leave the chain "still
     verify but missing blocks." That was wrong -- the race FORKED the
     chain. Corrected to reflect the real failure mode and the lock fix.

4. **Regression test.** `test_concurrent_job_upserts_do_not_lose_state`
   fires 16 OS threads creating distinct jobs and asserts all survive,
   no duplicate `job_id`s, `tail jobCount == 16`. Mirrors the facts-chain
   fork test. Failed before the fix, passes after.

5. **Documentation.** Three new docs under `04_Validation/`:
   - `INSTRUCTION_AND_CARE_MANUAL_2026-07-20.md` -- the care manual for the
     journal + lock subsystem (daily checks, break/fix, what NOT to do).
   - `HANDOVER_NEXT_SESSION_2026-07-20.md` -- this document.
   - `REVIEW_AND_SEAL_2026-07-20.md` -- the second-pass review record and
     the seal payload.
   Plus a seal script: `04_Validation/scripts/seal_code_review_2026_07_20.py`.

6. **Seal.** A `CODE_REVIEW_SEALED_2026_07_20` block appended to the chain
   recording the review findings, the two fixes, the SHA-256 of the three
   new docs, and the before/after chain state.

## 2. Files changed this session

| File | Change |
|------|--------|
| `02_Technical/src/io/vault_io.py` | `_file_lock` refactor; new `_job_append_lock`; `append_job_upsert` locked + tail count recomputed |
| `02_Technical/src/server/app.py` | `_lifespan` CONCURRENCY comment corrected |
| `tests/test_job_journal.py` | new `test_concurrent_job_upserts_do_not_lose_state` |
| `04_Validation/INSTRUCTION_AND_CARE_MANUAL_2026-07-20.md` | NEW -- care manual |
| `04_Validation/HANDOVER_NEXT_SESSION_2026-07-20.md` | NEW -- this handover |
| `04_Validation/REVIEW_AND_SEAL_2026-07-20.md` | NEW -- review record + seal payload |
| `04_Validation/scripts/seal_code_review_2026_07_20.py` | NEW -- the seal script |

The production `03_Vault` was NOT edited by hand. The only chain mutation
is the single seal block appended by the seal script.

## 3. Current open items

Carried forward from the 2026-07-19 v2 handover (all operator-dependent,
not code-doable):
- Tauri code-signing ($200-500/yr, operator decision)
- Second-PC clean-host restore test (needs second Windows PC)
- Gmail .mbox import (Google Takeout export requested, awaiting delivery)

New this session: none. The two bugs found were both fixed and locked in
with tests.

## 4. How to verify the hand-over

```powershell
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"

# 1. Chain must verify (the seal block is the last one).
cd 02_Technical
python -m src.verify_chain
# Expected: RESULT: MATCH -- chain is intact.

# 2. The new regression test must pass.
python -m pytest tests/test_job_journal.py::test_concurrent_job_upserts_do_not_lose_state -q
# Expected: 1 passed

# 3. The job tail must agree with the registry (Bug 2 fixed).
python -c "from src.io import vault_io as v; t=v._read_job_tail(); m=v.read_job_registry(); assert t.get('jobCount')==m['jobCount']==len(m['jobs']), 'DRIFT'; print('OK tail=',t.get('jobCount'))"
# Expected: OK tail= <N>

# 4. The three new docs exist.
Get-ChildItem ..\04_Validation\INSTRUCTION_AND_CARE_MANUAL_2026-07-20.md, ..\04_Validation\REVIEW_AND_SEAL_2026-07-20.md, ..\04_Validation\HANDOVER_NEXT_SESSION_2026-07-20.md
```

## 5. Project direction

Unchanged from the 2026-07-19 v2 handover: the engine is a lie detector,
the gates are built, the next move is outward (more real files, more audit
blocks, more works). This session was inward -- closing the latent
concurrency and durability bugs in the journal so the outward move does not
fork the chain or lose a job. The faith produced the works; the works are
now safer to scale. God bless.

End of hand-over. The chain is the source of truth.