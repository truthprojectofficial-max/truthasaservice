"""
Real-Options Lattice

Two-stage compound binomial lattice. Cox-Ross-Rubinstein. Fully
deterministic, no random number generator.

FRAMING (F7, added 2026-07-18):
The lattice outputs a **deception-adjusted optionality index**, NOT a
business valuation. The S0, K1, K2 inputs are hard-coded defaults
(REAL_OPTIONS_S0=55.0, REAL_OPTIONS_K1=18.0, REAL_OPTIONS_K2=10.0 in
config/constants.py). They do NOT derive from the audited business's
actual financial statements. The output value is therefore a stylised
compound option under a stylised volatility regime, useful for ranking
candidates and for the deception-aware learning-delta story, but
defensibly *not* a number to file as the value of the business. The
orchestrator output and any legal output that quotes the lattice MUST
include the LATTICE_FRAMING string from constants. See
01_Methodology/REAL_OPTIONS_LATTICE.md "Framing" section for the
operator-facing explanation.
"""
import math
from datetime import datetime, timezone

from src.types import RealOptionsValuation
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
    """
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
