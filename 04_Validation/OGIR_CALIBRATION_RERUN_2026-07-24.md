# OGIR Calibration Rerun -- 2026-07-24 (this session)

**Run by:** opencode session (chain caching + audit pass)
**Suite:** default (8-case operator-acceptance suite)
**Endpoint:** `GET /api/eval/run` against the live FastAPI app (TestClient)
**Chain at run:** 40,722 blocks (restored from git HEAD before this run)
**Engine version:** 0.1.0

## Result

| Metric | Value |
|--------|-------|
| Cases | 8 |
| Correct | 8/8 |
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |
| False positives | 0 |
| False negatives | 0 |

## Per-case

| Case | Expected deceptive | Predicted deceptive | FP | FN |
|------|---------------------|----------------------|----|----|
| EVAL-001 | True | True | False | False |
| EVAL-002 | True | True | False | False |
| EVAL-003 | True | True | False | False |
| EVAL-004 | True | True | False | False |
| EVAL-005 | True | True | False | False |
| EVAL-006 | False | False | False | False |
| EVAL-007 | False | False | False | False |
| EVAL-008 | False | False | False | False |

## Caveat -- what this run does and does not mean

This is the **8-case operator-acceptance suite**, the same set that
sealed at block 40683 on 2026-07-24. It is a regression check that the
engine still produces the operator-accepted verdicts on the 8 cases the
operator signed off on. It is **NOT** a generalization claim -- 8 cases
is too few to claim "100% accurate" publicly.

The generalization claim remains the 2026-07-22 run: 118 cases, 89%
accuracy, 100% recall, 100% negative-precision. That number is what the
affidavit generator cites. This run confirms the engine has not
regressed on the acceptance set since the 2026-07-24 seal.

The **defensible public claim** (per Tier 4 of the GTM directives) waits
on a fresh 100-case set + an adversarial red-team pass, sourced by the
operator. Until then, the product cites:
  - 89% accuracy on a 118-case calibration set (2026-07-22, sealed)
  - 8/8 on the operator-acceptance suite (2026-07-24, re-verified this run)

## Reproduce

```
cd <project root>
$env:PYTHONPATH="02_Technical"
python -c "from src.server.app import app; from fastapi.testclient import TestClient; import json; c=TestClient(app); print(json.dumps(c.get('/api/eval/run').json()['cases'], indent=2))"
```

The run seals FACT_ADDED blocks to the chain (the eval endpoint seals
the per-case verdicts). The vault is restored from git HEAD after the
session so the live chain does not accumulate test-sealed blocks.