"""
Affidavit_Agent -- the overseer role.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from config.constants import (
    PROJECT_OPERATOR,
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_JURISDICTION,
    DECEPTION_ONTOLOGY_VERSION,
    TAU_EXTRACTION_CEILING,
    PERFORMANCE_FLOOR,
    EFFICIENCY_FLOOR,
    GRACE_QUADRATIC_COEFFICIENT,
    REAL_OPTIONS_S0,
    REAL_OPTIONS_K1,
    REAL_OPTIONS_K2,
    REAL_OPTIONS_T1,
    REAL_OPTIONS_T2,
    SHANNON_ANOMALY_THRESHOLD,
    PROJECT_ROOT,
)
from src.io import vault_io


class AffidavitAgent:
    """The third-party overseer. The 'old to new' reviewer."""

    def __init__(self, root: Path = None) -> None:
        self.root = root or PROJECT_ROOT
        self.operator = PROJECT_OPERATOR

    def compile_affidavit(self) -> str:
        blocks = vault_io.merkle_all()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines = [
            "=" * 80,
            "AFFIDAVIT OF DETERMINISTIC SYSTEM TRUTH",
            "=" * 80,
            f"SYSTEM: {PROJECT_NAME} v{PROJECT_VERSION}",
            f"OPERATOR: {self.operator}",
            f"DATE: {now}",
            f"ONTOLOGY: {DECEPTION_ONTOLOGY_VERSION}",
            f"TAU CEILING: {TAU_EXTRACTION_CEILING}",
            f"JURISDICTION: {PROJECT_JURISDICTION}",
            "=" * 80,
            "",
            f"I, {self.operator}, declare that the following evidence",
            "blocks were generated within a deterministic, no-black-box",
            "environment. The Merkle chain is sealed to SHA-256.",
            "",
            f"Block count: {len(blocks)}",
            f"Current root: {vault_io.merkle_stats()['merkleRoot']}",
            "",
            "--- BEGIN CHRONOLOGICAL EVIDENCE LOG ---",
        ]
        for block in blocks:
            lines.append("")
            lines.append(f"BLOCK #{block['index']} -- {block['event_type']}")
            lines.append(f"  timestamp: {block['timestamp']}")
            lines.append(f"  hash:      {block['current_hash']}")
            lines.append(f"  previous:  {block['previous_hash']}")
            lines.append(f"  payload:   {json.dumps(block['payload'], sort_keys=True)[:200]}")
            lines.append("-" * 80)
        lines.append("")
        lines.append("--- END OF EVIDENCE LOG ---")
        lines.append("")
        lines.append("SIGNED: ____________________________________")
        lines.append(f"        {self.operator}")
        lines.append(f"        {PROJECT_NAME} Operator")
        lines.append(f"        Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
        return "\n".join(lines)

    def compare_to_spec(self) -> List[Dict[str, Any]]:
        disagreements: List[Dict[str, Any]] = []
        spec_values = {
            "tau_extraction_ceiling": TAU_EXTRACTION_CEILING,
            "performance_floor": PERFORMANCE_FLOOR,
            "efficiency_floor": EFFICIENCY_FLOOR,
            "grace_quadratic_coefficient": GRACE_QUADRATIC_COEFFICIENT,
            "real_options_s0": REAL_OPTIONS_S0,
            "real_options_k1": REAL_OPTIONS_K1,
            "real_options_k2": REAL_OPTIONS_K2,
            "shannon_anomaly_threshold": SHANNON_ANOMALY_THRESHOLD,
        }
        for path in (self.root / "02_Technical" / "src").rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                for name, value in spec_values.items():
                    if isinstance(value, float):
                        pattern = f"= {value:.1f}"
                    else:
                        pattern = f"= {value}"
                    if pattern in line and "from config" not in line and "import" not in line:
                        disagreements.append({
                            "file": str(path.relative_to(self.root)),
                            "line": lineno,
                            "spec_constant": name,
                            "spec_value": value,
                            "text": line.strip()[:200],
                        })
        return disagreements
