"""
Deception-Adjusted Valuation Integration

Connects the deception engine (67 patterns) to the BBFB valuation
engine (LAW/GRACE/FRUIT). When the deception engine flags patterns
in a product description, the valuation is adjusted:

1. LAW gate: if deception is HIGH/CRITICAL, the specAccuracy gate
   gets a penalty — you can't trust the claimed spec if the text
   is deceptive.

2. GRACE penalty: deception adds to the quadratic penalty. A
   deceptive product description increases the risk of economic harm.

3. FRUIT composite: the performance pillar is reduced by the
   deception probability. If the text is 80% likely deceptive,
   the performance score is reduced by 80% of its margin above
   the veto floor. You don't lose everything, but you lose trust.

The integration is one-directional: deception affects valuation,
NOT the other way. A product can be non-compliant without being
deceptive. But a deceptive product description should always
reduce the valuation, because you can't trust the claims.

Design principles:
- Pure stdlib, no dependencies
- Deterministic: same input = same output
- The deception probability is a discount factor, not a veto
- The LAW gate already has a veto; deception doesn't add a second
  veto, it adjusts the threshold of the existing one
- The pronoun-shift and jargon-as-shield patterns (DD-068, DD-069)
  feed into this: jargon-heavy product descriptions with few
  verifiable details get a performance penalty
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


def adjust_spec_for_deception(
    spec_value: float,
    deception_probability: float,
    detected_patterns: Optional[List[Dict[str, Any]]] = None,
) -> float:
    """Adjust the spec value curve output for deception.

    If the product description is deceptive, you can't trust the
    claimed spec. The spec_value (from the Taguchi curve) is
    discounted by the deception probability.

    The discount is proportional but not total:
    - 0% deception → no change (trust the spec fully)
    - 50% deception → 50% of the margin above the veto floor is removed
    - 100% deception → spec_value is pushed to the veto floor

    This preserves the LAW veto: if spec_value was already at the
    veto floor, deception doesn't push it below (that would be a
    double penalty). It only reduces the margin ABOVE the floor.

    Args:
        spec_value: the raw spec_value_curve output (0.0 to 1.0)
        deception_probability: 0.0 to 1.0
        detected_patterns: the patterns that fired (for severity weighting)

    Returns:
        Adjusted spec value (0.0 to 1.0), never below the veto floor
    """
    from config.constants import SPEC_VALUE_VETO_FLOOR

    # Severity weighting: HIGH/CRITICAL patterns weigh more than MEDIUM/LOW
    severity_weight = 1.0
    if detected_patterns:
        has_critical = any(p.get("severity") == "CRITICAL" for p in detected_patterns)
        has_high = any(p.get("severity") == "HIGH" for p in detected_patterns)
        if has_critical:
            severity_weight = 1.0  # full penalty
        elif has_high:
            severity_weight = 0.85  # 85% of full penalty
        else:
            severity_weight = 0.5  # half penalty for MEDIUM/LOW only

    # The discount: remove deception_probability * severity_weight of
    # the margin above the veto floor
    margin_above_floor = max(0.0, spec_value - SPEC_VALUE_VETO_FLOOR)
    discount = margin_above_floor * deception_probability * severity_weight
    adjusted = spec_value - discount

    # Never push below the veto floor (avoid double-penalty with LAW gate)
    return max(SPEC_VALUE_VETO_FLOOR, adjusted)


def adjust_grace_for_deception(
    raw_penalty: float,
    deception_probability: float,
    detected_patterns: Optional[List[Dict[str, Any]]] = None,
) -> float:
    """Add deception to the GRACE quadratic penalty.

    Deception in a product description increases the risk of
    economic harm. A deceptive spec claim means the product is
    likely worse than advertised — the GRACE penalty should increase.

    The deception penalty is additive: it adds to the existing
    raw_penalty (which already includes price failure, issue density,
    and compliance violations). Deception is a fourth risk factor.

    Args:
        raw_penalty: the existing GRACE raw penalty (0.0 to ~3.0, clamped to 1.0)
        deception_probability: 0.0 to 1.0
        detected_patterns: for severity weighting

    Returns:
        Adjusted raw penalty (may exceed 1.0, will be clamped by caller)
    """
    # Severity weighting
    severity_weight = 1.0
    if detected_patterns:
        has_critical = any(p.get("severity") == "CRITICAL" for p in detected_patterns)
        has_high = any(p.get("severity") == "HIGH" for p in detected_patterns)
        if has_critical:
            severity_weight = 1.0
        elif has_high:
            severity_weight = 0.85
        else:
            severity_weight = 0.5

    # Deception penalty: the square of the deception probability
    # (quadratic, matching the GRACE model — small deceptions add
    # small penalties, large deceptions add large penalties)
    deception_penalty = deception_probability ** 2 * severity_weight

    return raw_penalty + deception_penalty


def adjust_fruit_performance_for_deception(
    perf_score: float,
    deception_probability: float,
    detected_patterns: Optional[List[Dict[str, Any]]] = None,
) -> float:
    """Adjust the FRUIT performance pillar for deception.

    The performance pillar (spec_value_curve output) is the most
    directly affected by deception: if the spec claim is deceptive,
    the performance score should reflect that distrust.

    This is the same adjustment as adjust_spec_for_deception but
    applied to the FRUIT performance score specifically. It's
    called separately because FRUIT uses the curved value while
    LAW uses the vetoed value.

    Args:
        perf_score: the FRUIT performance score (0.0 to 1.0)
        deception_probability: 0.0 to 1.0
        detected_patterns: for severity weighting

    Returns:
        Adjusted performance score (0.0 to 1.0)
    """
    from config.constants import SPEC_VALUE_VETO_FLOOR

    severity_weight = 1.0
    if detected_patterns:
        has_critical = any(p.get("severity") == "CRITICAL" for p in detected_patterns)
        has_high = any(p.get("severity") == "HIGH" for p in detected_patterns)
        if has_critical:
            severity_weight = 1.0
        elif has_high:
            severity_weight = 0.85
        else:
            severity_weight = 0.5

    margin_above_floor = max(0.0, perf_score - SPEC_VALUE_VETO_FLOOR)
    discount = margin_above_floor * deception_probability * severity_weight
    return max(0.0, perf_score - discount)


def deception_adjusted_valuation(
    spec_value: float,
    raw_penalty: float,
    perf_score: float,
    deception_probability: float,
    detected_patterns: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Full deception-adjusted valuation integration.

    Connects the deception engine output to the BBFB valuation.
    Returns the adjusted values for LAW, GRACE, and FRUIT.

    Args:
        spec_value: raw spec_value_curve output
        raw_penalty: GRACE raw penalty
        perf_score: FRUIT performance score
        deception_probability: 0.0 to 1.0 from the deception engine
        detected_patterns: list of {patternId, severity} dicts

    Returns:
        {
            "adjusted_spec_value": float,
            "adjusted_grace_penalty": float,
            "adjusted_perf_score": float,
            "deception_discount": float,  # the total discount applied
            "deception_severity": str,    # highest severity detected
        }
    """
    adjusted_spec = adjust_spec_for_deception(spec_value, deception_probability, detected_patterns)
    adjusted_grace = adjust_grace_for_deception(raw_penalty, deception_probability, detected_patterns)
    adjusted_perf = adjust_fruit_performance_for_deception(perf_score, deception_probability, detected_patterns)

    # Determine highest severity
    severity = "NONE"
    if detected_patterns:
        severities = [p.get("severity", "LOW") for p in detected_patterns]
        if "CRITICAL" in severities:
            severity = "CRITICAL"
        elif "HIGH" in severities:
            severity = "HIGH"
        elif "MEDIUM" in severities:
            severity = "MEDIUM"
        else:
            severity = "LOW"

    # Total discount applied (for reporting)
    spec_discount = spec_value - adjusted_spec
    perf_discount = perf_score - adjusted_perf
    grace_increase = adjusted_grace - raw_penalty

    return {
        "adjusted_spec_value": round(adjusted_spec, 6),
        "adjusted_grace_penalty": round(adjusted_grace, 6),
        "adjusted_perf_score": round(adjusted_perf, 6),
        "spec_discount": round(spec_discount, 6),
        "perf_discount": round(perf_discount, 6),
        "grace_increase": round(grace_increase, 6),
        "deception_severity": severity,
        "deception_probability": round(deception_probability, 4),
        "integration": "deception-adjusted valuation: deceptive product descriptions reduce spec trust (LAW), increase risk penalty (GRACE), and discount performance (FRUIT). The discount is proportional to deception probability and severity. The LAW veto floor is preserved — deception never double-penalizes below the floor.",
    }