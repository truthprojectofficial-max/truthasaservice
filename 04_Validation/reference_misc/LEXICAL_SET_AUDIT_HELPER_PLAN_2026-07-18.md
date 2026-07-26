# Lexical-set audit helper plan

## Current coverage

- Total ontology patterns: **54** (v3.10, renamed from 3.9 in source comment).
- Patterns tested by EVAL suite extension: **19**.
- Patterns untested by EVAL suite: **35**.

Untested patterns:
DD-001, DD-002, DD-006, DD-007, DD-008, DD-013, DD-014, DD-016, DD-018, DD-020,
DD-021, DD-022, DD-023, DD-024, DD-025, DD-026, DD-030, DD-032, DD-033, DD-034,
DD-035, DD-037, DD-038, DD-039, DD-042, DD-043, DD-044, DD-045, DD-046, DD-047,
DD-048, DD-049, DD-050, DD-051, DD-054.

## Audit method

1. For each untested pattern, write one synthetic **TRUE POSITIVE** case that triggers it.
2. Write one synthetic **TRUE NEGATIVE** near-miss that does **not** trigger it.
3. Add both cases to the EVAL suite.
4. Run the suite and adjust indicators or test cases until both pass.

## What I have already done

Probed every untested pattern with synthetic text. All 35 patterns fire as expected.
The extended suite can be grown to cover all 54 patterns with roughly 70 additional
focused cases (35 positive + 35 negative).

## Helpers available

- `src.engines.deception_ontology_data.py` -- authoritative pattern definitions.
- `tests/test_evaluation_cases_extended.py` -- existing extended suite.
- FastAPI `/api/analyze` endpoint -- used via `TestClient` in tests.
- `src.verify_chain` -- Merkle-chain verification after edits.

## Recommended chunking

Break the 35 remaining patterns into four batches:

Batch A (technical / system): DD-001, DD-002, DD-007, DD-008, DD-018, DD-020, DD-021, DD-022, DD-023, DD-024
Batch B (manipulation / social): DD-006, DD-013, DD-014, DD-016, DD-026, DD-030, DD-032, DD-033, DD-034, DD-035
Batch C (emotional / cross-modal): DD-038, DD-039, DD-042, DD-043, DD-044, DD-045, DD-046, DD-047, DD-048, DD-049
Batch D (misc): DD-025, DD-037, DD-050, DD-051, DD-054

Estimated time: 4-6 hours across the four batches.

## Pitfall

Some patterns overlap (DD-014 vs DD-028, DD-016 vs DD-022, DD-006 vs DD-041). When
a test case fires more patterns than expected, update the expected set rather than
weaken the pattern. The goal is documentation, not isolation.
