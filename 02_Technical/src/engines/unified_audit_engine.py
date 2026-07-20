"""
Order Get It Right -- Unified audit / value / deception engine.

This module wraps the existing engines into one negating-human-error
process. It is a thin deterministic facade around:

  - src.engines.deception_scanner
  - src.engines.bbfb_engine
  - src.engines.real_options_lattice
  - src.agents.orchestrator (for job-token hand-offs and chain sealing)

The orchestrator already runs all three gates, but this module provides
an explicit "all3 in one" entry point that operators and the README can
point to. It is stateless and deterministic.
"""
from typing import Any, Dict, Optional

from src.types import ProductEvidence
from src.agents.orchestrator import Orchestrator


def process(
    statement: str,
    product_evidence: Optional[ProductEvidence] = None,
    category: str = "Technical",
) -> Dict[str, Any]:
    """Run the unified audit/value/deception engine on a single input.

    The orchestrator performs the actual work and seals an AUDIT_CYCLE
    block to the Merkle chain. This facade just makes the unified entry
    point explicit and self-documenting.

    Returns a dict with keys:
      - deceptionGate
      - bbfbGate
      - optionalityGate
      - finalAction
      - reason
      - ledgerRoot
      - timestamp
      - factId
    """
    core = Orchestrator()
    return core.process_input(
        category=category,
        statement=statement,
        product_evidence=product_evidence,
    )
