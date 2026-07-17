"""
Evaluation Service

Runs curated evaluation suites through the deception pipeline.  Computes
precision, recall, F1, and per-case verdicts.
"""
import uuid
from datetime import datetime, timezone
from typing import List

from src.types import (
    EvaluationCase,
    EvaluationCaseResult,
    EvaluationMetrics,
    EvaluationRunResult,
)
from .deception_scanner import audit_text

DECEPTIVE_THRESHOLD = 0.3


def run_evaluation_case(eval_case: EvaluationCase) -> EvaluationCaseResult:
    """Run a single evaluation case through the audit pipeline."""
    report = audit_text(eval_case.input)
    predicted_deceptive = report.deceptionProbability >= DECEPTIVE_THRESHOLD
    pattern_count = len(report.detectedPatterns)
    passed = True

    if predicted_deceptive != eval_case.expectedDeceptive:
        passed = False
    if pattern_count < eval_case.expectedMinPatterns:
        passed = False
    if (
        eval_case.expectedMinDeceptionProbability is not None
        and report.deceptionProbability < eval_case.expectedMinDeceptionProbability
    ):
        passed = False
    if (
        eval_case.expectedMaxDeceptionProbability is not None
        and report.deceptionProbability > eval_case.expectedMaxDeceptionProbability
    ):
        passed = False

    return EvaluationCaseResult(
        caseId=eval_case.id,
        label=eval_case.label,
        passed=passed,
        deceptionProbability=report.deceptionProbability,
        patternCount=pattern_count,
        expectedDeceptive=eval_case.expectedDeceptive,
        predictedDeceptive=predicted_deceptive,
        falsePositive=predicted_deceptive and not eval_case.expectedDeceptive,
        falseNegative=not predicted_deceptive and eval_case.expectedDeceptive,
        tags=eval_case.tags,
    )


def run_evaluation_suite(
    cases: List[EvaluationCase], suite_name: str = "default"
) -> EvaluationRunResult:
    """Run the entire evaluation suite and return the aggregated metrics."""
    results = [run_evaluation_case(c) for c in cases]
    tp = sum(1 for r in results if r.expectedDeceptive and r.predictedDeceptive)
    tn = sum(1 for r in results if not r.expectedDeceptive and not r.predictedDeceptive)
    fp = sum(1 for r in results if r.falsePositive)
    fn = sum(1 for r in results if r.falseNegative)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    metrics = EvaluationMetrics(
        totalCases=len(results),
        passed=sum(1 for r in results if r.passed),
        failed=sum(1 for r in results if not r.passed),
        accuracy=(tp + tn) / len(results) if results else 0.0,
        truePositives=tp,
        trueNegatives=tn,
        falsePositives=fp,
        falseNegatives=fn,
        precision=precision,
        recall=recall,
        f1Score=f1,
    )
    return EvaluationRunResult(
        runId=str(uuid.uuid4()),
        suiteName=suite_name,
        metrics=metrics,
        cases=results,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
