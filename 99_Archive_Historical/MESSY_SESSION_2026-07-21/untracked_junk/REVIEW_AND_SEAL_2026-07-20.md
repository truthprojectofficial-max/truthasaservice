# Order Get It Right -- Second-Pass Code Review and Seal Record

**Date:** 2026-07-20
**Reviewer:** Cline (act mode), at the operator's request
**Scope:** full review of the journal + concurrency subsystem landed
2026-07-20, plus a second pass to verify the fixes, then a seal to the
Merkle chain.
**Chain state at start:** MATCH, 26,593 blocks, root
`629fb2995e3e9ab5b10b6de02b25348f074b8a698c059d207207746845a2c8f0`

> This is the auditable record of the review. It lists every module
> examined, every finding (with severity), every fix applied, and the
> exact seal payload that was written to the chain. A third party can
> re-derive the seal block from this document and the on-disk state and
> confirm the review actually happened as recorded.

---

## 1. Modules reviewed

| Module | Lines | Focus | Verdict |
|--------|-------|-------|---------|
| `src/io/vault_io.py` | ~750 | append-only journal, locks, compaction, crash recovery | 2 bugs found + fixed |
| `src/server/app.py` | lifespan + handlers | startup/shutdown, concurrency comment | 1 stale comment corrected |
| `src/server/session_tracker.py` | 122 | in-memory session state, body replay | benign race, left as-is |
| `src/io/evidence_parser.py` | ~396 | heuristic regex extraction | sound, no change |
| `src/engines/real_options_lattice.py` | ~204 | CRR binomial, evidence-derived inputs | sound, no change |
| `src/engines/bbfb_engine.py` | ~209 | LAW/GRACE/FRUIT gates, Taguchi curve | sound, no change |

## 2. Findings

### F1 -- Job journal append had no cross-process lock
- **Severity:** HIGH (latent under concurrency; durability + integrity)
- **File:** `src/io/vault_io.py`, `append_job_upsert`
- **Root cause:** The facts-chain append got a cross-process lock earlier
  this session, but the job-journal upsert path was missed. Its
  read-tail -> append-journal-line -> write-tail critical section was
  unlocked, so two concurrent upserts could both read the same tail, both
  append a journal line, and the later writer's tail write clobbered the
  earlier one's `jobCount`. A crash between the two writes could lose a
  job's latest state on restart.
- **Fix:** Refactored the facts-chain lock into a reusable
  `_file_lock(lock_path, in_process_lock)` helper (shared in-process +
  cross-process logic). Added `_job_append_lock` (separate lock file +
  separate `threading.Lock` so the two journals do not serialise each
  other). Wrapped `append_job_upsert`'s whole critical section in it.
- **Test:** `test_concurrent_job_upserts_do_not_lose_state` (new).
- **Status:** FIXED + sealed.

### F2 -- Job tail `jobCount` never advanced on new-job upserts
- **Severity:** MEDIUM (silent tail drift; the test caught it)
- **File:** `src/io/vault_io.py`, `append_job_upsert`
- **Root cause:** The old code did
  `new_count = _read_job_tail().get("jobCount", 0)` then wrote that same
  value back -- so the tail's `jobCount` never incremented when a new job
  was created. It only got corrected on compaction or a tail rebuild. The
  new concurrency test exposed it: `tail jobCount 1 != 16`.
- **Fix:** Recompute from the materialised registry inside the lock:
  `materialised = _materialise_job_registry(); _write_job_tail({"jobCount": materialised["jobCount"], ...})`.
- **Test:** the same `test_concurrent_job_upserts_do_not_lose_state`
  asserts `tail.get("jobCount") == n`.
- **Status:** FIXED + sealed.

### F3 -- Stale/wrong CONCURRENCY comment in `app.py` lifespan
- **Severity:** LOW (documentation accuracy; the code was already correct)
- **File:** `src/server/app.py`, `_lifespan` docstring
- **Root cause:** The comment claimed the multi-worker race would leave
  "the chain would still verify but be missing blocks." That was wrong --
  the race actually FORKED the chain (duplicate indices + divergent
  `current_hash`), which is exactly what broke the production vault at
  block 25250. The comment also predated the lock fix.
- **Fix:** Rewrote the comment to reflect the lock fix and the real
  failure mode, with the corrected note that the old "still verify" claim
  was wrong.
- **Status:** FIXED + sealed.

### F4 -- Session tracker in-memory dict is unlocked
- **Severity:** NEGLIGIBLE (by design for the air-gap single-tenant build)
- **File:** `src/server/session_tracker.py`
- **Root cause:** `_sessions` is a module-level dict with no lock.
  Concurrent same-session requests have a benign TOCTOU on the `locked`
  flag (worst case: one extra request slips through before the lock bites)
  and a lost-update on the `attempts` counter (approximate by design).
- **Decision:** Left as-is. The session tracker is intentionally
  best-effort. Adding a lock would add complexity for no functional gain
  in the single-operator air-gap deployment. Documented in the care
  manual section 6 (do-not-run-multi-worker note).
- **Status:** ACCEPTED, documented, not changed.

### F5 -- `warranty_ratio` defaults to 0 when `monthsToFailure == 0`
- **Severity:** NONE (intended conservative gate)
- **File:** `src/engines/bbfb_engine.py`
- **Root cause:** If a product has not failed (`monthsToFailure == 0`),
  the warranty adequacy ratio defaults to 0.0, failing the 1.00 floor.
- **Decision:** This is correct by design. The gate requires
  `warrantyMonths >= monthsToFailure` (ratio >= 1.0). No failure data
  means we cannot assert warranty adequacy. The operator must supply a
  projected `monthsToFailure`. Not a bug.
- **Status:** ACCEPTED, not changed.

### F6 -- Lattice / evidence math
- **Severity:** NONE
- **File:** `src/engines/real_options_lattice.py`,
  `src/io/evidence_parser.py`
- **Notes:** CRR binomial is standard. `_safe_ratio` handles zero
  denominators. `_clamp` bounds volatility. Spec-value Taguchi curve is
  symmetric and clamped. Evidence parser is deterministic regex-only.
- **Status:** sound, no change.

## 3. Test results (second pass, after fixes)

```
tests/test_vault_journal.py      ........................ 16 passed
tests/test_job_journal.py        .........................  5 passed
tests/test_vault_reseed_guard.py ........................  6 passed
tests/test_smoke.py              ........................ 17 passed
tests/test_evidence_parser.py    ........................  9 passed
tests/test_f7_deep_lattice_wired.py .....................  5 passed
tests/test_f7_spec_value_curve.py .......................  5 passed
                                                       --------
                                                       63 passed
```

The new regression test `test_concurrent_job_upserts_do_not_lose_state`
FAILED before the F1+F2 fixes (`tail jobCount 1 != 16`) and PASSES after.

## 4. The seal

A single block of event_type `CODE_REVIEW_SEALED_2026_07_20` is appended
to the facts chain by
`04_Validation/scripts/seal_code_review_2026_07_20.py`. The payload
records: the six findings above, the two fixes, the SHA-256 of every
changed file and every new doc, the before/after chain state, and the
test result. The seal block's index and hash are printed by the script
and recorded below by hand after the script runs.

**Changed-file fingerprints (at seal time):**

| Artefact | SHA-256 |
|----------|---------|
| `02_Technical/src/io/vault_io.py` | `21e76ea6b98ace4de66d2ac242450829d72b2cb63ed001124242c7f1115ad4dd` |
| `02_Technical/src/server/app.py` | `bf1c033c858e3e23ef18013ecedb538b05aeadd1879e696b77a0afc996df5b5a` |
| `tests/test_job_journal.py` | `eb5db181f4c703f2af0c6e10823dd557a9cb2cafce6d8f9fe896bd09b50ba968` |
| `04_Validation/INSTRUCTION_AND_CARE_MANUAL_2026-07-20.md` | `7712c5b6e99fad83b865af86f6660b5e5648fcef8b064eab6d0338b39a250096` |
| `04_Validation/HANDOVER_NEXT_SESSION_2026-07-20.md` | `f3a302b257deabef08727adcc843d36e5ba1b1f5618e46ad363282769ba2888d` |

**Chain state:**

| | Block count | Merkle root |
|-|-------------|-------------|
| Before seal | 26,593 | `629fb2995e3e9ab5b10b6de02b25348f074b8a698c059d207207746845a2c8f0` |
| After seal | 26,594 | `22f0809d24610ab98106559f203c1c5ec86c5a3c69fb1faec779daa765a6ec79` |

**Seal block:** index = 26594, hash = `22f0809d24610ab98106559f203c1c5ec86c5a3c69fb1faec779daa765a6ec79`.

The chain re-verifies to MATCH after the seal (`python -m src.verify_chain`
returned `RESULT: MATCH -- chain is intact.` with the recomputed root equal
to the claimed root `22f0809d...65a6ec79`).

End of review record. The chain is the source of truth.

---

## 5. Design principle: inflated markup IS the signal, not noise (2026-07-20)

**Context.** The corrected Gmail audit (82 real-body files) flagged two
180 KB HTML emails (Bailey Property Weekly Update, GM_0346 / GM_0350) at
74% deception probability, structural flag TRUE, with an ACL demand issued.
The patterns fired were DD-019 Structural Refusal Mimicry [CRITICAL] and
DD-036 Repetitive Hammering [HIGH].

**The wrong reaction (rejected).** A first-pass note suggested these were
"false positives caused by raw HTML" and proposed adding an HTML-stripper
before the scanner so the emails would "score on their prose, not their
markup." The operator rejected this and was right to.

**The principle.** When a company wraps a trivial message ("weekly
property update", "your shoe lace is untied") in 180 KB of inflated
markup, repetitive banner blocks, and urgency framing, the **inflation
itself is the manipulation**. The scanner correctly read the raw text --
including the markup -- and the repetitive hammering / structural inflation
it found IS the offence. Stripping the HTML would be **laundering the
evidence**: removing the exact artefact the audit exists to flag, then
declaring the email "clean." That is precisely how senders get away with
"CRITICAL WARNING: your shoe lace is untied" -- by relabelling the
inflation as "formatting" and asking the auditor to ignore it.

**Rule (binding).** The deception scanner MUST receive the full extracted
text including HTML markup. No HTML-stripper, no tag-removal, no
"clean for readability" pre-processing step may be inserted between the
evidence parser and the deception scanner. The score reflects what the
recipient actually received, including the markup the sender chose to wrap
it in. A high score on a markup-heavy email is a correct detection of
attention-manipulation-by-volume, not a false positive.

**Scope of this rule.** This applies to the deception scan (Gate 1). It
does NOT apply to the BBFB product-evidence engine, which extracts
structured product facts from prose and already treats HTML tags as
non-evidence. The two gates have different jobs: the deception gate judges
how the message is constructed; the BBFB gate judges what the message
claims about a product.

**Sealed.** This principle is recorded as chain block
`DESIGN_PRINCIPLE_MARKUP_IS_SIGNAL_2026_07_20` so a future session cannot
quietly walk it back by filing an HTML-stripper as a "fix."