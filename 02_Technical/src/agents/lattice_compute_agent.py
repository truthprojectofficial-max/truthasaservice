"""
Lattice_Compute_Agent -- the real-world business test role.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from src.engines.bbfb_engine import calculate_bbfb
from src.engines.real_options_lattice import hardened_compound_binomial_gate
from src.types import ProductEvidence


@dataclass
class BusinessVerdict:
    # F7 (2026-07-18): renamed valuation_decision/valuation_total to
    # optionality_decision/optionality_total to enforce the framing --
    # the lattice output is an optionality index, not a business
    # valuation. The optionality_framing field surfaces the constant.
    bbfb_compliant: bool
    bbfb_cvs: float
    bbfb_grace_risk: str
    optionality_decision: str
    optionality_total: float
    optionality_framing: str
    summary: str
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class LatticeComputeAgent:
    """The third-party real-world test role. Deterministic. No LLM."""

    def compute_bbfb(self, evidence: ProductEvidence) -> BusinessVerdict:
        bbfb = calculate_bbfb(evidence)
        lattice = hardened_compound_binomial_gate(deception_score=0.0, entropy=0.0)
        if bbfb.overallCompliant:
            summary = "Business claim is compliant with the BBFB engine."
        else:
            summary = f"Business claim is non-compliant. GRACE risk: {bbfb.grace.riskLevel}."
        return BusinessVerdict(
            bbfb_compliant=bbfb.overallCompliant,
            bbfb_cvs=bbfb.fruit.compositeValueScore,
            bbfb_grace_risk=bbfb.grace.riskLevel,
            optionality_decision=lattice.decision,
            optionality_total=lattice.totalValue,
            optionality_framing=lattice.framing,
            summary=summary,
        )
