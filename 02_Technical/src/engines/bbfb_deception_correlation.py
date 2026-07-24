"""
BBFB-Deception Correlation Detector

When BBFB catches a bad product (non-compliant) AND the deception
engine flags the description as deceptive, the two signals compound:
the deception was concealing the product failure. This is worse than
either signal alone.

The correlation produces a "fine-grain decision marker" — a
compound score that's more sensitive than either engine alone
when the signals are close to a threshold.

For example:
- BBFB score = 0.78 (just below compliance threshold 0.80)
- Deception probability = 0.45 (just below review threshold 0.50)
- Either alone: borderline. Both together: the deception was hiding
  the borderline failure — compound risk = HIGH.

This module computes the compound signal WITHOUT changing the
existing BBFB constants or thresholds. It only reads them and
produces a new compound assessment. The existing gates are untouched.
"""
from __future__ import annotations
from typing import Any, Dict, Optional


def compute_correlation(
    bbfb_compliant: bool,
    fruit_score: float,
    grace_risk: str,
    law_failures: int,
    deception_probability: float,
    deception_severity: str,
) -> Dict[str, Any]:
    """Compute the BBFB-deception compound correlation.

    This does NOT change any existing thresholds. It produces a
    new compound assessment that is more sensitive when both
    signals are borderline.

    Args:
        bbfb_compliant: did the BBFB gate pass?
        fruit_score: FRUIT composite value score (0.0-1.0)
        grace_risk: LOW/MEDIUM/HIGH/CRITICAL
        law_failures: count of LAW gates that failed
        deception_probability: 0.0-1.0
        deception_severity: highest deception severity (NONE/LOW/MEDIUM/HIGH/CRITICAL)

    Returns:
        {
            "compound_risk": str,        # LOW/MEDIUM/HIGH/CRITICAL
            "correlation": str,          # "concealment" / "independent" / "no_risk"
            "correlation_strength": float, # 0.0-1.0
            "compound_score": float,     # 0.0-1.0 (higher = worse)
            "fine_grain_marker": str,    # human-readable compound assessment
            "decision_boost": float,     # adjustment to apply to the final decision
        }
    """
    # Normalise the inputs to 0.0-1.0 risk scores
    bbfb_risk = 0.0
    if not bbfb_compliant:
        bbfb_risk = 0.5  # base non-compliance
    bbfb_risk += law_failures * 0.1  # each LAW failure adds 10%
    bbfb_risk = min(1.0, bbfb_risk)

    # FRUIT inverted: low score = high risk
    fruit_risk = max(0.0, 1.0 - fruit_score)

    # GRACE risk to numeric
    grace_map = {"LOW": 0.1, "MEDIUM": 0.3, "HIGH": 0.6, "CRITICAL": 0.9}
    grace_risk_val = grace_map.get(grace_risk, 0.3)

    # Deception risk IS the deception probability
    deception_risk = deception_probability

    # Compound score: weighted average
    # The weighting prioritises the compound signal:
    # when both bbfb_risk and deception_risk are high, the compound
    # is higher than either alone (synergistic, not just additive)
    base_risk = (bbfb_risk * 0.35) + (fruit_risk * 0.15) + (grace_risk_val * 0.15) + (deception_risk * 0.35)

    # Synergy bonus: when both BBFB and deception are above 0.3,
    # add a compound bonus (the concealment effect)
    synergy = 0.0
    if bbfb_risk > 0.3 and deception_risk > 0.3:
        # The concealment effect: deception was hiding the product failure
        synergy = min(0.2, (bbfb_risk - 0.3) * (deception_risk - 0.3) * 0.5)

    compound_score = min(1.0, base_risk + synergy)

    # Correlation type
    if bbfb_risk > 0.3 and deception_risk > 0.3:
        correlation = "concealment"
        correlation_strength = min(1.0, (bbfb_risk + deception_risk) / 2 + synergy)
    elif bbfb_risk > 0.3 or deception_risk > 0.3:
        correlation = "independent"
        correlation_strength = max(bbfb_risk, deception_risk)
    else:
        correlation = "no_risk"
        correlation_strength = 0.0

    # Compound risk level
    if compound_score >= 0.75:
        compound_risk = "CRITICAL"
    elif compound_score >= 0.5:
        compound_risk = "HIGH"
    elif compound_score >= 0.25:
        compound_risk = "MEDIUM"
    else:
        compound_risk = "LOW"

    # Fine-grain marker (human-readable)
    if correlation == "concealment":
        fine_grain = (
            f"Concealment detected: the product fails BBFB (risk {bbfb_risk:.0%}) "
            f"AND the description is deceptive (risk {deception_risk:.0%}). "
            f"The deception appears to be concealing the product failure. "
            f"Compound risk: {compound_risk} ({compound_score:.0%})."
        )
    elif correlation == "independent":
        if bbfb_risk > deception_risk:
            fine_grain = (
                f"Product risk: BBFB non-compliant (risk {bbfb_risk:.0%}) "
                f"but description is relatively clean (deception {deception_risk:.0%}). "
                f"The product is bad but honestly described."
            )
        else:
            fine_grain = (
                f"Deception risk: description is deceptive (risk {deception_risk:.0%}) "
                f"but product meets BBFB thresholds (risk {bbfb_risk:.0%}). "
                f"The product may be acceptable but the description is hiding something."
            )
    else:
        fine_grain = (
            f"Low compound risk: product meets BBFB thresholds (risk {bbfb_risk:.0%}) "
            f"and description is clean (deception {deception_risk:.0%}). "
            f"No concealment detected."
        )

    # Decision boost: a small adjustment to the final decision
    # This does NOT replace the existing decision — it nudges it
    # when the compound signal is borderline
    # Positive boost = push toward REFUSED
    # Negative boost = push toward GO
    # Zero = no change
    if compound_risk == "CRITICAL":
        decision_boost = 0.15  # strong nudge toward REFUSED
    elif compound_risk == "HIGH":
        decision_boost = 0.10  # moderate nudge toward REVIEW_REQUIRED
    elif compound_risk == "MEDIUM":
        decision_boost = 0.05  # slight nudge toward review
    else:
        decision_boost = 0.0

    return {
        "compound_risk": compound_risk,
        "correlation": correlation,
        "correlation_strength": round(correlation_strength, 4),
        "compound_score": round(compound_score, 4),
        "fine_grain_marker": fine_grain,
        "decision_boost": decision_boost,
        "bbfb_risk": round(bbfb_risk, 4),
        "deception_risk": round(deception_risk, 4),
        "synergy_bonus": round(synergy, 4),
    }