"""
Order Get It Right -- Traffic Light Indicator

Converts the deception probability (0.0-1.0) into a directional
traffic light with R/G/Y bands, a percentage, and a directional
indicator (toward or away from deception).

The bands use the existing constants:
  DECEPTION_PROBABILITY_LOW  = 0.30  (below = GREEN)
  DECEPTION_PROBABILITY_VETO = 0.75  (above = RED)
  Between 0.30 and 0.75 = YELLOW (AMBER)

The directional indicator shows whether the score is trending
toward or away from deception based on the severity mix of the
detected patterns (CRITICAL patterns push toward RED, LOW patterns
push toward GREEN).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


# Band boundaries (from config/constants.py, mirrored here to avoid
# import cycles in the UI layer)
GREEN_CEILING = 0.30    # <= 0.30 = GREEN (low deception likelihood)
RED_FLOOR = 0.75         # >= 0.75 = RED (high deception likelihood)
# 0.30 < score < 0.75 = YELLOW (amber, review required)


def traffic_light(
    deception_probability: float,
    detected_patterns: Optional[List[Dict[str, Any]]] = None,
    verdict: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert a deception probability into a traffic light indicator.

    Returns:
        {
            "light": "GREEN" | "YELLOW" | "RED",
            "percentage": float,          # 0-100
            "direction": "toward" | "away" | "neutral",
            "direction_label": str,       # human-readable
            "band": str,                  # "0-30% low" | "30-75% review" | "75-100% high"
            "machine_eval": str,          # "CLEAN" | "REVIEW_REQUIRED" | "REFUSED"
            "advice": str,                # what the operator should do
            "severity_mix": Dict[str, int], # count by severity
        }
    """
    score = max(0.0, min(1.0, deception_probability))
    pct = round(score * 100, 1)

    # Determine the light
    if verdict == "SUPPRESSED":
        light = "RED"
    elif score >= RED_FLOOR:
        light = "RED"
    elif score <= GREEN_CEILING:
        light = "GREEN"
    else:
        light = "YELLOW"

    # Severity mix (for directional indicator)
    severity_mix: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    if detected_patterns:
        for p in detected_patterns:
            sev = p.get("severity", "LOW").upper()
            if sev in severity_mix:
                severity_mix[sev] += 1

    # Directional indicator: toward or away from deception
    # If more HIGH/CRITICAL patterns than LOW, trending TOWARD deception
    high_critical = severity_mix["CRITICAL"] + severity_mix["HIGH"]
    low_medium = severity_mix["MEDIUM"] + severity_mix["LOW"]
    if high_critical > low_medium:
        direction = "toward"
        direction_label = "trending toward deception"
    elif low_medium > high_critical and score < GREEN_CEILING:
        direction = "away"
        direction_label = "trending away from deception"
    else:
        direction = "neutral"
        direction_label = "mixed signals — no clear trend"

    # Machine evaluation (the decision the engine makes)
    if light == "RED":
        machine_eval = "REFUSED"
        advice = "High deception likelihood. Structural refusal recommended. Do not proceed without operator override."
    elif light == "YELLOW":
        machine_eval = "REVIEW_REQUIRED"
        advice = "Moderate deception likelihood. Human review required before proceeding. Client may submit an explanation."
    else:
        machine_eval = "CLEAN"
        advice = "Low deception likelihood. Within acceptable bounds. Proceed with normal process."

    # Band label
    if score <= GREEN_CEILING:
        band = f"0-{int(GREEN_CEILING * 100)}% low"
    elif score >= RED_FLOOR:
        band = f"{int(RED_FLOOR * 100)}-100% high"
    else:
        band = f"{int(GREEN_CEILING * 100)}-{int(RED_FLOOR * 100)}% review"

    return {
        "light": light,
        "percentage": pct,
        "direction": direction,
        "direction_label": direction_label,
        "band": band,
        "machine_eval": machine_eval,
        "advice": advice,
        "severity_mix": severity_mix,
    }