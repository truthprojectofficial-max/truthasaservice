"""
Squeal Protocol

Writes high-deception events to disk as JSON audit trail.  Triggered
automatically when audit_text() detects structural deception.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from src.config import SQUEAL_DIR
from src.types import DeceptionReport


def write_squeal_report(
    report: DeceptionReport,
    session_id: str,
    trigger: str = "Structural_Deception_Flag",
) -> str:
    ts = report.timestamp.replace(":", "-").replace(".", "-")
    safe_session_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in session_id)
    filename = f"squeal-{ts}-{safe_session_id}.json"
    filepath = SQUEAL_DIR / filename
    critical_patterns = [
        f"{p.patternId} {p.patternName} ({p.confidence * 100:.1f}%)"
        for p in report.detectedPatterns
        if p.severity in ("CRITICAL", "HIGH")
    ]
    payload = {
        "timestamp": report.timestamp,
        "sessionId": session_id,
        "trigger": trigger,
        "inputText": report.inputText,
        "deceptionProbability": report.deceptionProbability,
        "structuralDeceptionFlag": report.structuralDeceptionFlag,
        "criticalPatterns": critical_patterns,
        "forensicReasoning": report.forensicReasoning,
        "recommendation": (
            "ESCALATE_TO_LEGAL"
            if any(p.severity == "CRITICAL" for p in report.detectedPatterns)
            else "MONITOR_CLOSELY"
        ),
    }
    filepath.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return filename


def list_squeal_reports() -> List[str]:
    if not SQUEAL_DIR.exists():
        return []
    return sorted(
        f.name for f in SQUEAL_DIR.iterdir() if f.name.startswith("squeal-") and f.name.endswith(".json")
    )


def read_squeal_report(filename: str) -> dict:
    safe_name = Path(filename).name
    filepath = SQUEAL_DIR / safe_name
    if not filepath.exists():
        raise FileNotFoundError(filename)
    return json.loads(filepath.read_text(encoding="utf-8"))
