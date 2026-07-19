"""
Real-Options Lattice

Two-stage compound binomial lattice. Cox-Ross-Rubinstein. Fully
deterministic, no random number generator.

FRAMING (F7, added 2026-07-18; F7-deep, added 2026-07-19):
The lattice outputs a **deception-adjusted optionality index**, NOT a
business valuation. When ProductEvidence is supplied (F7-deep), the
S0/K1/K2 and sigma1/sigma2 inputs are derived from the evidence fields:
  - S0   = pricePaid (capital at stake / recoverable amount)
  - K1   = pricePaid * REAL_OPTIONS_STRIKING_RATIO (stage-1 break-even)
  - K2   = pricePaid * 0.5 (stage-2 escalation threshold)
  - sigma1 = 0.3 * (1 + specGap)  (merit uncertainty from spec shortfall)
  - sigma2 = 0.2 * (1 + complianceGap) (escalation uncertainty from
              regulatory violations)
When no evidence is supplied, the hardcoded defaults
(REAL_OPTIONS_S0=55.0, REAL_OPTIONS_K1=18.0, REAL_OPTIONS_K2=10.0 in
config/constants.py) are used as stylised fallbacks. The orchestrator
output and any legal output that quotes the lattice MUST include the
LATTICE_FRAMING string from constants. See
01_Methodology/REAL_OPTIONS_LATTICE.md "Framing" section for the
operator-facing explanation.
"""
import math
from datetime import datetime, timezone
from typing import Optional

from src.types import ProductEvidence, RealOptionsValuation
from config.constants import (
    REAL_OPTIONS_S0,
    REAL_OPTIONS_K1,
    REAL_OPTIONS_K2,
    REAL_OPTIONS_T1,
    REAL_OPTIONS_T2,
    REAL_OPTIONS_R,
    REAL_OPTIONS_SIGMA1,
    REAL_OPTIONS_SIGMA2,
    REAL_OPTIONS_N1,
    REAL_OPTIONS_N2,
    REAL_OPTIONS_LEARNING_DELTA,
    REAL_OPTIONS_STRIKING_RATIO,
    REAL_OPTIONS_SIGMA_MIN,
    REAL_OPTIONS_SIGMA_MAX,
)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division, matching BBFB engine's _safe_ratio semantics."""
    if denominator == 0:
        return default
    return numerator / denominator


def derive_lattice_inputs_from_evidence(evidence: ProductEvidence) -> dict:
    """
    F7-deep (2026-07-19): derive S0, K1, K2, sigma1, sigma2 from the
    actual ProductEvidence fields instead of the hardcoded stylised
    defaults.

    Mapping rationale:
      - S0 (underlying asset value): pricePaid -- the capital at stake
        and the recoverable amount. For a consumer dispute, this is the
        refund the claimant seeks.
      - K1 (stage-1 strike): pricePaid * STRIKING_RATIO -- the break-even
        threshold for pursuing the claim. The option is in the money if
        the expected recovery exceeds 85% of what was paid.
      - K2 (stage-2 strike): pricePaid * 0.5 -- the escalation cost for
        stage 2 (tribunal/court filing). Lower than K1 because the
        marginal cost of escalating is less than the initial pursuit cost.
      - sigma1 (stage-1 volatility): derived from the spec gap
        (1 - specRatio). A total spec failure doubles the base volatility.
      - sigma2 (stage-2 volatility): derived from the compliance gap
        (1 - complianceRatio). High regulatory violations increase
        escalation uncertainty.

    Returns a dict with keys s0, k1, k2, sigma1, sigma2. All values are
    clamped to the SIGMA_MIN/SIGMA_MAX range for the volatility inputs.
    Falls back to hardcoded defaults if pricePaid <= 0 (no meaningful
    capital at stake).
    """
    if evidence.pricePaid <= 0:
        return {
            "s0": REAL_OPTIONS_S0,
            "k1": REAL_OPTIONS_K1,
            "k2": REAL_OPTIONS_K2,
            "sigma1": REAL_OPTIONS_SIGMA1,
            "sigma2": REAL_OPTIONS_SIGMA2,
        }

    s0 = float(evidence.pricePaid)
    k1 = s0 * REAL_OPTIONS_STRIKING_RATIO
    k2 = s0 * 0.5

    spec_ratio = _safe_ratio(evidence.specMeasured, evidence.specClaimed, 0.0)
    spec_gap = 1.0 - spec_ratio
    sigma1 = _clamp(0.3 * (1.0 + spec_gap), REAL_OPTIONS_SIGMA_MIN, REAL_OPTIONS_SIGMA_MAX)

    compliance_ratio = 1.0 - _safe_ratio(
        evidence.violationsFound, evidence.regulatoryRequirements, 0.0
    )
    compliance_gap = 1.0 - compliance_ratio
    sigma2 = _clamp(0.2 * (1.0 + compliance_gap), REAL_OPTIONS_SIGMA_MIN, REAL_OPTIONS_SIGMA_MAX)

    return {
        "s0": s0,
        "k1": k1,
        "k2": k2,
        "sigma1": sigma1,
        "sigma2": sigma2,
    }


def _binomial_lattice(S0: float, K: float, T: float, r: float, sigma: float, n: int) -> float:
    """Back-induction Cox-Ross-Rubinstein binomial lattice for a European call."""
    dt = T / n
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    p = (math.exp(r * dt) - d) / (u - d)
    # Terminal payoffs
    values = [max(S0 * (u ** (n - i)) * (d ** i) - K, 0.0) for i in range(n + 1)]
    # Back-induction
    for step in range(n, 0, -1):
        values = [
            math.exp(-r * dt) * (p * values[i] + (1 - p) * values[i + 1])
            for i in range(len(values) - 1)
        ]
    return values[0]


def hardened_compound_binomial_gate(
    deception_score: float,
    entropy: float,
    evidence: Optional[ProductEvidence] = None,
    s0: float = REAL_OPTIONS_S0,
    k1: float = REAL_OPTIONS_K1,
    k2: float = REAL_OPTIONS_K2,
    t1: float = REAL_OPTIONS_T1,
    t2: float = REAL_OPTIONS_T2,
    r: float = REAL_OPTIONS_R,
    sigma1: float = REAL_OPTIONS_SIGMA1,
    sigma2: float = REAL_OPTIONS_SIGMA2,
    n1: int = REAL_OPTIONS_N1,
    n2: int = REAL_OPTIONS_N2,
) -> RealOptionsValuation:
    """
    Hardened deterministic compound real-options gate.

    Adjusts volatility deterministically from the deception score and the
    Shannon entropy of the input.  All formulas are public, no random
    numbers are used.

    F7-deep (2026-07-19): when ``evidence`` (a ProductEvidence) is supplied,
    S0/K1/K2/sigma1/sigma2 are derived from the evidence fields via
    ``derive_lattice_inputs_from_evidence``. When ``evidence`` is None,
    the hardcoded defaults (or caller-supplied overrides) are used.
    """
    if evidence is not None:
        derived = derive_lattice_inputs_from_evidence(evidence)
        s0 = derived["s0"]
        k1 = derived["k1"]
        k2 = derived["k2"]
        sigma1 = derived["sigma1"]
        sigma2 = derived["sigma2"]

    adjusted_sigma1 = _clamp(
        sigma1 * (1 + deception_score * 0.35),
        REAL_OPTIONS_SIGMA_MIN,
        REAL_OPTIONS_SIGMA_MAX,
    )
    adjusted_sigma2 = _clamp(
        sigma2 * (1 + entropy / 9.0),
        REAL_OPTIONS_SIGMA_MIN,
        REAL_OPTIONS_SIGMA_MAX,
    )

    v1 = _binomial_lattice(s0, k1, t1, r, adjusted_sigma1, n1)

    # Learning delta: high deception reduces what is learned between stages
    learning_delta = REAL_OPTIONS_LEARNING_DELTA * (1 - 0.6 * deception_score)
    s0_2 = v1 + learning_delta
    v2 = _binomial_lattice(s0_2, k2, t2, r, adjusted_sigma2, n2)

    total = v1 + v2
    threshold = (k1 + k2) * REAL_OPTIONS_STRIKING_RATIO
    decision = "GO" if total > threshold else "DEFER"

    from config.constants import LATTICE_FRAMING
    return RealOptionsValuation(
        stage1Value=round(v1, 4),
        stage2Value=round(v2, 4),
        totalValue=round(total, 4),
        threshold=round(threshold, 4),
        decision=decision,
        adjustedVolatilityStage1=round(adjusted_sigma1, 4),
        adjustedVolatilityStage2=round(adjusted_sigma2, 4),
        learningDelta=round(learning_delta, 4),
        timestamp=datetime.now(timezone.utc).isoformat(),
        framing=LATTICE_FRAMING,
    )
