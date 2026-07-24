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
    SPEC_BEST_BAND_X_STAR,
    SPEC_VALUE_WIDTH_W,
    SPEC_VALUE_VETO_FLOOR,
)

BBFB_CONFIG = {
    "CVS_THRESHOLD": CVS_THRESHOLD,
    "LAW_PASS_VALUE": 1,
    "LAW_FAIL_VALUE": 0,
    "GRACE_QUADRATIC_COEFFICIENT": GRACE_QUADRATIC_COEFFICIENT,
    "FRUIT_DEFAULT_WEIGHTS": FRUIT_WEIGHTS,
    "SPEC_BEST_BAND_X_STAR": SPEC_BEST_BAND_X_STAR,
    "SPEC_VALUE_WIDTH_W": SPEC_VALUE_WIDTH_W,
    "SPEC_VALUE_VETO_FLOOR": SPEC_VALUE_VETO_FLOOR,
}


def _safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    if not denominator:
        return default
    return numerator / denominator


def spec_value_curve(x: float) -> float:
    """F7-SPEC (2026-07-19): symmetric Taguchi-quadratic spec-value curve.

    Replaces the hard specAccuracy floor (>= PERFORMANCE_FLOOR) with a
    concave value function that peaks at x* = SPEC_BEST_BAND_X_STAR
    (spec measured == spec claimed) and declines quadratically on
    BOTH sides. This implements the "best band for buck" / diminishing-
    returns behaviour the operator asked for.

    Form (symmetric Taguchi loss -> value):
        V(x) = 1 - ((x - x*) / w)^2, clamped to [0, 1]

    - Peak at x* = 1.0: the product does exactly what it claims. Value = 1.0.
    - Under-spec (x < 1.0): value declines quadratically. At x=0.5, V=0.75.
    - Over-spec (x > 1.0): value ALSO declines. A product that overspecs
      its claim tells the story of its own demise -- it will fail other
      BBFB criteria (price fairness: you overpaid; compliance: the claim
      was inaccurate). The symmetric curve makes that visible in the
      spec dimension too.
    - Veto boundary preserved by construction: V_min = V(PERFORMANCE_FLOOR)
      = V(0.5) = 1 - (0.5/1.0)^2 = 0.75 = SPEC_VALUE_VETO_FLOOR. So any
      case that was vetoed at spec_ratio < 0.5 under the old hard floor is
      still vetoed under the curve, because V(x) < 0.75 iff x < 0.5
      (for the under-spec side) or x > 1.5 (for the over-spec side).

    Deterministic: pure math, no random, no optimisation. Same input =
    same output on any host (PYTHONHASHSEED=0).

    See DIMINISHING_RETURNS_RESEARCH_2026-07-19 (in the validation
    folder) for the methodology, primary-source citations
    (Taguchi 1986), and the derivation of V_min from PERFORMANCE_FLOOR.
    """
    raw = 1.0 - ((x - SPEC_BEST_BAND_X_STAR) / SPEC_VALUE_WIDTH_W) ** 2
    return max(0.0, min(1.0, raw))


def calculate_bbfb(evidence: ProductEvidence) -> BBFBResult:
    """Run the full BBFB pipeline on a ProductEvidence payload.

    Fields not provided (0 or empty) are SKIPPED, not treated as
    perfect. A gate whose input is 0/0 gets "NOT_PROVIDED" status
    instead of pass or fail. The FRUIT pillar for that dimension
    is excluded from the composite, and its weight is redistributed
    to the other pillars. This prevents a user who only provides
    price + spec + warranty from getting a "perfect compliance"
    score on issues and violations they didn't report.
    """
    price_ratio = _safe_ratio(evidence.pricePaid, evidence.priceAdvertised, 0.0)
    spec_ratio = _safe_ratio(evidence.specMeasured, evidence.specClaimed, 0.0)
    warranty_ratio = _safe_ratio(evidence.warrantyMonths, evidence.monthsToFailure, 0.0)
    issue_ratio = _safe_ratio(evidence.knownIssues, evidence.totalFeaturesOrParts, 0.0)
    violation_ratio = _safe_ratio(evidence.violationsFound, evidence.regulatoryRequirements, 0.0)

    # Track which fields were actually provided (non-zero denominator)
    has_price = evidence.priceAdvertised > 0
    has_spec = evidence.specClaimed > 0
    has_warranty = evidence.monthsToFailure > 0
    has_issues = evidence.totalFeaturesOrParts > 0
    has_compliance = evidence.regulatoryRequirements > 0

    input_evidence = [
        {
            "metric": "priceRatio",
            "numerator": evidence.pricePaid,
            "denominator": evidence.priceAdvertised,
            "computedRatio": price_ratio,
            "provided": has_price,
        },
        {
            "metric": "specRatio",
            "numerator": evidence.specMeasured,
            "denominator": evidence.specClaimed,
            "computedRatio": spec_ratio,
            "provided": has_spec,
        },
        {
            "metric": "warrantyRatio",
            "numerator": evidence.warrantyMonths,
            "denominator": evidence.monthsToFailure,
            "computedRatio": warranty_ratio,
            "provided": has_warranty,
        },
        {
            "metric": "issueRatio",
            "numerator": evidence.knownIssues,
            "denominator": evidence.totalFeaturesOrParts,
            "computedRatio": issue_ratio,
            "provided": has_issues,
        },
        {
            "metric": "violationRatio",
            "numerator": evidence.violationsFound,
            "denominator": evidence.regulatoryRequirements,
            "computedRatio": violation_ratio,
            "provided": has_compliance,
        },
    ]

    # LAW Gate
    # F7-SPEC (2026-07-19): specAccuracy now uses the Taguchi-quadratic
    # spec_value_curve instead of the raw spec_ratio. The threshold is
    # SPEC_VALUE_VETO_FLOOR (= V(PERFORMANCE_FLOOR) = 0.75), so the veto
    # boundary is preserved by construction. efficiencyAdequacy still
    # uses the raw spec_ratio with EFFICIENCY_FLOOR -- it measures
    # execution efficiency, not spec accuracy.
    spec_value = spec_value_curve(spec_ratio)
    law_inputs: List[LAWGateInput] = [
        LAWGateInput(metric="priceFairness", value=price_ratio, threshold=1.0),
        LAWGateInput(metric="specAccuracy", value=spec_value, threshold=SPEC_VALUE_VETO_FLOOR),
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
    # F7-SPEC (2026-07-19): perf_score now uses spec_value_curve(spec_ratio)
    # instead of the raw spec_ratio. The curve is the honest spec value --
    # using raw ratio after curving the LAW gate would be inconsistent.
    #
    # Each pillar now carries TWO values:
    #   - "value": the actual score (0.0-1.0)
    #   - "floor": the minimum acceptable score for this pillar
    #   - "margin": value - floor (how far above the minimum)
    #   - "status": "ABOVE_FLOOR" / "AT_FLOOR" / "BELOW_FLOOR" / "NOT_PROVIDED"
    # This gives the operator a scale: not just "performance is 0.184"
    # but "performance is 0.184, floor is 0.150, margin is 0.034 — barely above."
    weights = FRUIT_WEIGHTS
    cost_score = max(0.0, 1.0 - abs(1.0 - price_ratio))
    perf_score = spec_value
    reliability_score = min(warranty_ratio, 1.0)
    compliance_score = 1.0 - violation_ratio

    # Floor values: the minimum acceptable score for each pillar
    # These are derived from the LAW gate thresholds — the floor IS
    # the point where the LAW gate would veto. Below the floor = veto.
    cost_floor = 0.0  # price fairness has no hard floor (it's a ratio)
    perf_floor = SPEC_VALUE_VETO_FLOOR  # 0.75 — the Taguchi veto boundary
    reliability_floor = WARRANTY_FLOOR  # 1.0 — warranty must cover the failure
    compliance_floor = 1.0 - VIOLATION_RATIO_FLOOR  # 0.95 — at most 5% violations

    def _pillar(name, score, floor, weight, provided=True):
        margin = round(score - floor, 6)
        if not provided:
            status = "NOT_PROVIDED"
        elif score < floor:
            status = "BELOW_FLOOR"
        elif margin < 0.01:
            status = "AT_FLOOR"
        else:
            status = "ABOVE_FLOOR"
        return {
            "name": name,
            "value": round(score, 6),
            "floor": round(floor, 6),
            "margin": margin,
            "status": status,
            "weight": weight,
            "weighted": round(score * weight, 6),
        }

    weighted_scores = [
        _pillar("cost", cost_score, cost_floor, weights["cost"], has_price),
        _pillar("performance", perf_score, perf_floor, weights["performance"], has_spec),
        _pillar("reliability", reliability_score, reliability_floor, weights["reliability"], has_warranty),
        _pillar("compliance", compliance_score, compliance_floor, weights["compliance"], has_compliance),
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
