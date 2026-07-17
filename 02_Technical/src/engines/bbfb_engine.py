"""
BBFB / CIDI Governance Engine

Barnett Binary Faith-Basis engine. LAW / GRACE / FRUIT gates with the
mandated quadratic penalty and weighted composite value score.
"""
from datetime import datetime, timezone
from typing import List

from src.types import (
    ProductEvidence,
    BBFBResult,
    LAWGateInput,
    LAWGateResult,
    GRACERiskResult,
    FRUITResult,
)
from config.constants import (
    PERFORMANCE_FLOOR,
    EFFICIENCY_FLOOR,
    WARRANTY_FLOOR,
    ISSUE_DENSITY_FLOOR,
    VIOLATION_RATIO_FLOOR,
    GRACE_QUADRATIC_COEFFICIENT,
    GRACE_CRITICAL_THRESHOLD,
    FRUIT_WEIGHTS,
    CVS_THRESHOLD,
)

BBFB_CONFIG = {
    "CVS_THRESHOLD": CVS_THRESHOLD,
    "LAW_PASS_VALUE": 1,
    "LAW_FAIL_VALUE": 0,
    "GRACE_QUADRATIC_COEFFICIENT": GRACE_QUADRATIC_COEFFICIENT,
    "FRUIT_DEFAULT_WEIGHTS": FRUIT_WEIGHTS,
}


def _safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    if not denominator:
        return default
    return numerator / denominator


def calculate_bbfb(evidence: ProductEvidence) -> BBFBResult:
    """Run the full BBFB pipeline on a ProductEvidence payload."""
    price_ratio = _safe_ratio(evidence.pricePaid, evidence.priceAdvertised, 0.0)
    spec_ratio = _safe_ratio(evidence.specMeasured, evidence.specClaimed, 0.0)
    warranty_ratio = _safe_ratio(evidence.warrantyMonths, evidence.monthsToFailure, 0.0)
    issue_ratio = _safe_ratio(evidence.knownIssues, evidence.totalFeaturesOrParts, 0.0)
    violation_ratio = _safe_ratio(evidence.violationsFound, evidence.regulatoryRequirements, 0.0)

    input_evidence = [
        {
            "metric": "priceRatio",
            "numerator": evidence.pricePaid,
            "denominator": evidence.priceAdvertised,
            "computedRatio": price_ratio,
        },
        {
            "metric": "specRatio",
            "numerator": evidence.specMeasured,
            "denominator": evidence.specClaimed,
            "computedRatio": spec_ratio,
        },
        {
            "metric": "warrantyRatio",
            "numerator": evidence.warrantyMonths,
            "denominator": evidence.monthsToFailure,
            "computedRatio": warranty_ratio,
        },
        {
            "metric": "issueRatio",
            "numerator": evidence.knownIssues,
            "denominator": evidence.totalFeaturesOrParts,
            "computedRatio": issue_ratio,
        },
        {
            "metric": "violationRatio",
            "numerator": evidence.violationsFound,
            "denominator": evidence.regulatoryRequirements,
            "computedRatio": violation_ratio,
        },
    ]

    # LAW Gate
    law_inputs: List[LAWGateInput] = [
        LAWGateInput(metric="priceFairness", value=price_ratio, threshold=1.0),
        LAWGateInput(metric="specAccuracy", value=spec_ratio, threshold=PERFORMANCE_FLOOR),
        LAWGateInput(metric="efficiencyAdequacy", value=spec_ratio, threshold=EFFICIENCY_FLOOR),
        LAWGateInput(metric="warrantyAdequacy", value=warranty_ratio, threshold=WARRANTY_FLOOR),
        LAWGateInput(
            metric="issueDensity",
            value=1.0 - issue_ratio,
            threshold=1.0 - ISSUE_DENSITY_FLOOR,
        ),
        LAWGateInput(
            metric="complianceClean",
            value=1.0 - violation_ratio,
            threshold=1.0 - VIOLATION_RATIO_FLOOR,
        ),
    ]
    law_results: List[LAWGateResult] = []
    law_pass = True
    for inp in law_inputs:
        passed = inp.value >= inp.threshold
        law_results.append(
            LAWGateResult(metric=inp.metric, value=inp.value, threshold=inp.threshold, passed=passed)
        )
        if not passed:
            law_pass = False

    # GRACE quadratic penalty
    p_fail = max(0.0, 1.0 - price_ratio) if price_ratio < 1.0 else 0.0
    d_tech = issue_ratio
    g_comp = violation_ratio
    raw_penalty = GRACE_QUADRATIC_COEFFICIENT * (p_fail ** 2 + d_tech ** 2 + g_comp ** 2)
    normalised_penalty = min(raw_penalty, 1.0)
    risk_level = (
        "CRITICAL" if normalised_penalty > GRACE_CRITICAL_THRESHOLD
        else "HIGH" if normalised_penalty > 0.5
        else "MEDIUM" if normalised_penalty > 0.25
        else "LOW"
    )

    # FRUIT weighted product
    weights = FRUIT_WEIGHTS
    cost_score = max(0.0, 1.0 - abs(1.0 - price_ratio))
    perf_score = spec_ratio
    reliability_score = min(warranty_ratio, 1.0)
    compliance_score = 1.0 - violation_ratio
    weighted_scores = [
        {"name": "cost", "weighted": round(cost_score * weights["cost"], 6)},
        {"name": "performance", "weighted": round(perf_score * weights["performance"], 6)},
        {"name": "reliability", "weighted": round(reliability_score * weights["reliability"], 6)},
        {"name": "compliance", "weighted": round(compliance_score * weights["compliance"], 6)},
    ]
    composite_value_score = round(sum(ws["weighted"] for ws in weighted_scores), 6)
    compliant = composite_value_score >= CVS_THRESHOLD and law_pass

    return BBFBResult(
        inputEvidence=input_evidence,
        law=law_results,
        grace=GRACERiskResult(
            rawPenalty=round(raw_penalty, 4),
            normalizedPenalty=round(normalised_penalty, 4),
            riskLevel=risk_level,
        ),
        fruit=FRUITResult(
            compositeValueScore=composite_value_score,
            weightedScores=weighted_scores,
            compliant=compliant,
            threshold=CVS_THRESHOLD,
        ),
        overallCompliant=compliant,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
