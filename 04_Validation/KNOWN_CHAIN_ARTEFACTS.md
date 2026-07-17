# Known Chain Artefacts -- 2026-07-18

The Merkle truth ledger at `03_Vault/facts_registry.json` is **append-only by
design**. Every block ever sealed remains in the chain forever. The chain
verifies as MATCH against its current root despite the artefacts below;
they are **historical record, not live bugs**. The explanation is the fix:
this document records every permanent data-quality artefact so the next
operator or auditor sees the answer in one place.

## Artefact 1: Duplicate `id: 1` seed fact (blocks #1 and #4)

**Symptom.** The first five blocks of the chain contain a duplicate seed
fact with `id: 1`:

- Block #1 (`timestamp: 2026-07-11T17:15:10Z`): `id: 1`, statement
  "Order Get It Right enforces the agent chain via the job delegator."
- Block #2: `id: 2`, statement "All deception detections use the
  deterministic 52-pattern ontology v3.8."
- Block #3: `id: 3`, statement "BBFB engine uses LAW/GRACE/FRUIT
  decomposition..."
- Block #4 (`timestamp: 2026-07-11T17:15:11Z`): `id: 1`, **same statement
  as block #1**.

**Cause.** This was the residual of the "startup reset foot-gun" tracked
under `OPEN_ITEMS_AND_REFERENCE.md` item **A3**. A fresh process would
load the on-disk chain, find an empty in-memory registry, and re-seed the
seed facts. Because the previous process had not yet flushed, the re-seed
appended rather than dedup'd, producing two `id: 1` blocks one second apart.
The bug was not in the seal logic (each block was sealed correctly and
verifies individually); it was in the seed-on-startup vs seed-on-POST race
window.

**Fix (already sealed).** OPEN_ITEMS A3 was closed in the seal
`A3_CLOSED_2026_07_17` (block 5246):

- `_seed_facts_once()` was guarded with `if list_facts(): return` so a
  non-empty in-memory registry short-circuits the seed.
- The `POST /api/facts` handler was rewired to call `_ensure_seeded()`
  before adding any operator fact, so a fresh process cannot reach a
  POST with an empty registry.
- `facts_registry.add_fact` enforces a `(statement, source)` dedup-check
  that raises `ValueError` on a duplicate, so the API path is now
  dup-proof.

**Residue.** Blocks #1 and #4 remain in the chain. They are historical
record. They do not break the chain -- the Merkle hash links them
correctly. Any third party who reads the chain head and sees `id: 1`
twice is looking at the residue of a closed bug, not a live regression.

## Artefact 2: Stale "52-pattern ontology v3.8" seed fact (block #2)

**Symptom.** Block #2 carries the statement "All deception detections use
the deterministic 52-pattern ontology v3.8." The live
`DECEPTION_ONTOLOGY_VERSION` constant in
`02_Technical/config/constants.py` is `"3.9 (54 patterns)"`.

**Cause.** Block #2 was sealed on 2026-07-11, before the v3.8 -> v3.9
bump and the 52 -> 54 pattern addition. The chain is append-only; the
old seed fact cannot be edited.

**Fix (already sealed).** `OPEN_ITEMS A2` ("v3.8/v3.9 hardcoded strings")
was closed in `OPEN_ITEMS_A2_V3_9_BUMP_2026_07_15`. All live code reads
the current constant. The MATHEMATICS.md section 4 was also updated from
"52 Patterns" to "54 Patterns" in the `DOCS_RECONCILED_FINAL_2026_07_18`
seal of this build (F1+F3 in `OGIR_ASSESSMENT_2026-07-18.md`).

**Residue.** Block #2 remains. The live runtime never reads the block's
statement field for ontology version (the constant is the source of
truth). The block is a historical snapshot of the operator's claim on
2026-07-11; the operator's claim today is the v3.9 / 54-pattern version.

## Why these are not live bugs

1. The chain **verifies as MATCH** (re-derives the same Merkle root from
   disk). Re-running `python -m src.verify_chain` prints
   `RESULT: MATCH -- chain is intact.`
2. The `facts_registry.add_fact` dedup check raises `ValueError` on any
   new duplicate; the live API is dup-proof.
3. The `DECEPTION_ONTOLOGY_VERSION` constant is the runtime's source of
   truth; the block #2 statement is a historical claim, never read by
   any code path.
4. The A3 fix's regression test (`tests/test_orchestrator_seam.py` plus
   the A3 force-clean-baseline test added in the
   `A3_CLOSED_2026_07_17` seal) exercises the fresh-process path and
   asserts no new duplicates can be created.

## How to add to this file

If a future seal produces a new permanent artefact (for example, a
historical block with a known-stale statement that cannot be edited
without breaking the chain), add a new section "Artefact N" with the
same shape: Symptom, Cause, Fix (with seal reference), Residue.

The chain is the source of truth. This file is the index of
explanations for the human reader.

---

End of KNOWN_CHAIN_ARTEFACTS.md -- 2026-07-18.