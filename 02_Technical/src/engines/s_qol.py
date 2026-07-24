"""
Systemic Quality of Life (S-QoL) Interpretation Layer

Translates OGIR's raw mathematical outputs (FRUIT composite value
score, deception probability, GRACE risk) into human-interpretable
verdicts using the S-QoL framework from the BBFB Audits PDF.

The 5 S-QoL dimensions:
1. Systemic Vitality — is the system alive and running? (from GRACE risk)
2. Structural Integrity — is it structurally sound? (from LAW gate pass/fail)
3. Transactional Execution — does it do what it says? (from FRUIT + deception)
4. Operational Morbidity — how often does it fail? (from GRACE penalty)
5. Systemic Vulnerability — how exposed is it? (from deception + violations)

Each dimension maps to a 5-level scale:
  Excellent / Good / Marginal / Poor / Critical

This is the MAPS (MApping onto Preference-based measures) adaptation:
a deterministic, auditable translation from raw math to human value.
Same inputs = same S-QoL levels on any host.

Based on: Unifying Human Value in BBFB Audits.pdf (16 pages)
and: CPA Australia business-evaluation-guide.pdf (33 pages)
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


def _level_from_score(score: float) -> str:
    """Map a 0.0-1.0 score to a 5-level S-QoL verdict."""
    if score >= 0.85:
        return "Excellent"
    elif score >= 0.70:
        return "Good"
    elif score >= 0.50:
        return "Marginal"
    elif score >= 0.30:
        return "Poor"
    else:
        return "Critical"


def _level_from_risk(risk: str) -> str:
    """Map a GRACE risk level to S-QoL."""
    mapping = {
        "LOW": "Excellent",
        "MEDIUM": "Good",
        "HIGH": "Marginal",
        "CRITICAL": "Critical",
    }
    return mapping.get(risk, "Marginal")


def compute_s_qol(
    fruit_score: float,
    law_pass: bool,
    grace_risk_level: str,
    grace_penalty: float,
    deception_probability: float,
    violation_ratio: float,
    detected_patterns: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Compute the 5-dimension S-QoL assessment.

    Args:
        fruit_score: FRUIT composite value score (0.0-1.0)
        law_pass: did the LAW gate pass?
        grace_risk_level: LOW/MEDIUM/HIGH/CRITICAL
        grace_penalty: normalised GRACE penalty (0.0-1.0)
        deception_probability: 0.0-1.0 from deception engine
        violation_ratio: violations / requirements
        detected_patterns: for severity weighting

    Returns:
        {
            "dimensions": {
                "systemic_vitality": {"score": float, "level": str, "meaning": str},
                "structural_integrity": {"score": float, "level": str, "meaning": str},
                "transactional_execution": {"score": float, "level": str, "meaning": str},
                "operational_morbidity": {"score": float, "level": str, "meaning": str},
                "systemic_vulnerability": {"score": float, "level": str, "meaning": str},
            },
            "overall_s_qol": {"score": float, "level": str, "meaning": str},
            "worth_statement": str,  # human-readable worth assessment
        }
    """
    # Dimension 1: Systemic Vitality (from GRACE risk)
    vitality_score = max(0.0, 1.0 - grace_penalty)
    vitality_level = _level_from_score(vitality_score)
    vitality_meaning = "The system is alive and running with low failure risk." if vitality_level in ("Excellent", "Good") else "The system has elevated failure risk."

    # Dimension 2: Structural Integrity (from LAW gate)
    integrity_score = 1.0 if law_pass else 0.0
    integrity_level = "Excellent" if law_pass else "Critical"
    integrity_meaning = "All structural gates passed." if law_pass else "One or more structural gates failed — the product does not meet minimum thresholds."

    # Dimension 3: Transactional Execution (from FRUIT + deception)
    # This is the deception-adjusted dimension: if the description is
    # deceptive, you can't trust that it does what it says
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

    from config.constants import SPEC_VALUE_VETO_FLOOR
    margin_above_floor = max(0.0, fruit_score - SPEC_VALUE_VETO_FLOOR)
    deception_discount = margin_above_floor * deception_probability * severity_weight
    transactional_score = max(0.0, fruit_score - deception_discount)
    transactional_level = _level_from_score(transactional_score)

    if deception_probability > 0.7:
        transactional_meaning = "The product description is highly deceptive — you cannot trust that it does what it claims."
    elif deception_probability > 0.3:
        transactional_meaning = "The product description contains deception markers — trust the claims with caution."
    else:
        transactional_meaning = "The product description is clean — the claims appear trustworthy."

    # Dimension 4: Operational Morbidity (from GRACE penalty directly)
    morbidity_score = max(0.0, 1.0 - grace_penalty)
    morbidity_level = _level_from_score(morbidity_score)
    morbidity_meaning = "Low failure rate expected." if morbidity_level in ("Excellent", "Good") else "Elevated failure rate — product may fail prematurely."

    # Dimension 5: Systemic Vulnerability (from deception + violations)
    vulnerability_raw = (deception_probability * 0.6) + (violation_ratio * 0.4)
    vulnerability_score = max(0.0, 1.0 - vulnerability_raw)
    vulnerability_level = _level_from_score(vulnerability_score)

    if vulnerability_level in ("Poor", "Critical"):
        vulnerability_meaning = "High exposure — deception and/or compliance violations make this product risky."
    else:
        vulnerability_meaning = "Low exposure — the product is transparent and compliant."

    # Overall S-QoL (weighted average of all 5 dimensions)
    # Weights from MCDA methodology (health economics adaptation):
    # Transactional Execution and Structural Integrity weigh most
    weights = {
        "vitality": 0.15,
        "integrity": 0.25,
        "transactional": 0.30,
        "morbidity": 0.15,
        "vulnerability": 0.15,
    }
    overall_score = (
        vitality_score * weights["vitality"]
        + integrity_score * weights["integrity"]
        + transactional_score * weights["transactional"]
        + morbidity_score * weights["morbidity"]
        + vulnerability_score * weights["vulnerability"]
    )
    overall_level = _level_from_score(overall_score)

    # Worth statement (human-readable)
    worth_statements = {
        "Excellent": "This product delivers what it claims with low risk. High value — proceed with confidence.",
        "Good": "This product mostly delivers what it claims. Acceptable value — proceed with normal oversight.",
        "Marginal": "This product falls short in measurable ways. Review required — proceed only after verifying the gaps.",
        "Poor": "This product significantly under-delivers. High risk of economic harm — do not proceed without operator override.",
        "Critical": "This product fails to deliver. Economic harm is likely — structural refusal recommended.",
    }
    worth_statement = worth_statements[overall_level]

    # Add deception note if relevant
    if deception_probability > 0.3:
        worth_statement += f" Deception risk: {deception_probability*100:.0f}% — the product description contains markers of deception."

    return {
        "dimensions": {
            "systemic_vitality": {
                "score": round(vitality_score, 4),
                "level": vitality_level,
                "meaning": vitality_meaning,
            },
            "structural_integrity": {
                "score": round(integrity_score, 4),
                "level": integrity_level,
                "meaning": integrity_meaning,
            },
            "transactional_execution": {
                "score": round(transactional_score, 4),
                "level": transactional_level,
                "meaning": transactional_meaning,
                "deception_adjusted": deception_probability > 0.0,
                "deception_discount": round(deception_discount, 4),
            },
            "operational_morbidity": {
                "score": round(morbidity_score, 4),
                "level": morbidity_level,
                "meaning": morbidity_meaning,
            },
            "systemic_vulnerability": {
                "score": round(vulnerability_score, 4),
                "level": vulnerability_level,
                "meaning": vulnerability_meaning,
            },
        },
        "overall_s_qol": {
            "score": round(overall_score, 4),
            "level": overall_level,
            "meaning": worth_statement,
        },
        "worth_statement": worth_statement,
        "framework": "S-QoL (Systemic Quality of Life) — MAPS adaptation. 5 dimensions, MCDA-weighted. Deterministic: same inputs = same S-QoL on any host.",
    }