#!/usr/bin/env bash
# Order Get It Right -- EVAL-suite runner (operator-side)
#
# Runs the existing 8-case evaluation suite and re-derives the metrics.
# Used by F8-EXTENDED to grow the suite to 30+ cases. The suite is
# the canonical empirical baseline for the 54-pattern ontology; the
# metrics this script prints are the number that goes on the chain.
#
# Usage:  bash 02_Technical/scripts/run_eval_suite.sh
# Output: stdout -- a single JSON object with metrics + per-case results.
#         exits 0 if F1 >= 0.7; 1 otherwise.
#
# The F8 contract is F1 >= 0.7 on the 8-case suite. The pre-R1-R4
# baseline was F1 = 0.909. The post-R1-R4 re-derivation is recorded
# in data/outbox/E4_F1_RE_DERIVED_2026-07-18.json (0.500 on the
# strict TN-as-TP framing). The threshold 0.7 is the operator-
# acceptable F1 floor for the 8-case suite.

set -euo pipefail

cd "$(dirname "$0")/../.."  # project root
cd 02_Technical

python -c "
import json, sys
sys.path.insert(0, '.')
from src.engines.evaluation_service import run_evaluation_suite
from src.engines.evaluation_cases import DEFAULT_EVALUATION_CASES

result = run_evaluation_suite(DEFAULT_EVALUATION_CASES, suite_name='default')
m = result.metrics
out = {
    'suite_name': 'default',
    'totalCases': m.totalCases,
    'passed': m.passed,
    'failed': m.failed,
    'accuracy': m.accuracy,
    'precision': m.precision,
    'recall': m.recall,
    'f1Score': m.f1Score,
    'truePositives': m.truePositives,
    'trueNegatives': m.trueNegatives,
    'falsePositives': m.falsePositives,
    'falseNegatives': m.falseNegatives,
    'perCase': [
        {
            'caseId': c.caseId,
            'label': c.label,
            'passed': c.passed,
            'deceptionProbability': c.deceptionProbability,
            'patternCount': c.patternCount,
            'expectedDeceptive': c.expectedDeceptive,
            'predictedDeceptive': c.predictedDeceptive,
            'falsePositive': c.falsePositive,
            'falseNegative': c.falseNegative,
        }
        for c in result.cases
    ],
}
print(json.dumps(out, indent=2))
sys.exit(0 if m.f1Score >= 0.7 else 1)
"