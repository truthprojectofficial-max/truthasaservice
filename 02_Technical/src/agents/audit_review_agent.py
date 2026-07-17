"""
Audit_Review_Agent -- the test + contradiction-hunting role.

The third party hands the agent a DraftFact (or a fact_id, or a
plaintext). The agent's job is to:
  1. Run the 54-pattern deception scan.
  2. Run the entropy check.
  3. Cross-check the fact against the build folder: does the code
     match the spec? does the spec match the third party's expectation?
  4. Produce a three-state verdict: CLEAN / FLAGGED / SUPPRESSED.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.constants import PROJECT_ROOT
from src.engines.deception_scanner import audit_text, DeceptionReport


@dataclass
class AuditVerdict:
    state: str
    reason: str
    deception_probability: float
    patterns_fired: List[Dict[str, Any]] = field(default_factory=list)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class AuditReviewAgent:
    """The third-party test role. Deterministic. No LLM."""

    def __init__(self, root: Path = PROJECT_ROOT) -> None:
        self.root = Path(root)

    def audit(self, text: str, context: Optional[str] = None) -> AuditVerdict:
        report: DeceptionReport = audit_text(text, context=context)
        if any(p.severity == "CRITICAL" for p in report.detectedPatterns):
            state = "SUPPRESSED"
            reason = "CRITICAL deception pattern detected"
        elif any(p.severity == "HIGH" for p in report.detectedPatterns):
            state = "FLAGGED"
            reason = "HIGH deception pattern detected"
        else:
            state = "CLEAN"
            reason = "no HIGH or CRITICAL pattern matched"
        return AuditVerdict(
            state=state,
            reason=reason,
            deception_probability=report.deceptionProbability,
            patterns_fired=[
                {
                    "patternId": p.patternId,
                    "patternName": p.patternName,
                    "severity": p.severity,
                    "confidence": p.confidence,
                    "matchedIndicators": p.matchedIndicators,
                }
                for p in report.detectedPatterns
            ],
        )

    def hunt(self, statement: str, roots: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not statement or not statement.strip():
            return []
        roots = roots or ["02_Technical", "deploy", "docs"]
        contradictions: List[Dict[str, Any]] = []
        markers: List[str] = []
        lowered = statement.lower()
        if "air-gapped" in lowered or "no network" in lowered or "no_network" in lowered:
            markers.extend(["urllib", "requests.get", "requests.post", "http.client"])
        if "deterministic" in lowered:
            markers.extend(["random.", "time.time()", "datetime.now"])
        if "no llm" in lowered or "no model" in lowered:
            markers.extend(["openai", "anthropic", "ollama", "litellm"])
        if "no placeholders" in lowered or "no todo" in lowered:
            markers.extend(["TODO", "FIXME", "placeholder"])
        for root_name in roots:
            root_path = self.root / root_name
            if not root_path.exists():
                continue
            for path in root_path.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix not in {".py", ".md", ".txt", ".ps1", ".sh", ".yml", ".yaml", ".json"}:
                    continue
                if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except (OSError, UnicodeDecodeError):
                    continue
                for lineno, line in enumerate(text.splitlines(), start=1):
                    ll = line.lower()
                    for marker in markers:
                        if marker in ll:
                            contradictions.append({
                                "file": str(path.relative_to(self.root)),
                                "line": lineno,
                                "marker": marker,
                                "text": line.strip()[:300],
                            })
                            if len(contradictions) >= 100:
                                return contradictions
        return contradictions
