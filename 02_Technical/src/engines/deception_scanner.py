"""
Order Get It Right - Audit Service

Translates the audit logic into deterministic Python.  No cloud AI is invoked
in the core audit path.
"""
import math
import re
from datetime import datetime, timezone
from typing import List, Optional

from src.types import DeceptionReport, DeceptionMatch, EntropyAnalysis
from .deception_ontology_data import DECEPTION_ONTOLOGY
from config.constants import (
    SHANNON_ANOMALY_THRESHOLD,
    SHANNON_LOW_THRESHOLD,
    SHANNON_MAX_NORMAL,
    DECEPTION_PROBABILITY_VETO,
    DECEPTION_ONTOLOGY_VERSION,
)

SQUEAL_LOG: List[dict] = []


def shannon_entropy(text: str) -> EntropyAnalysis:
    """Character-level Shannon entropy over a normalised view of the text."""
    char_count: dict = {}
    clean = text.lower()
    if not clean:
        return EntropyAnalysis(
            shannonEntropy=0.0,
            normalizedEntropy=0.0,
            characterDistribution={},
            anomalyFlag=False,
            lowEntropyFlag=True,
        )
    for ch in clean:
        char_count[ch] = char_count.get(ch, 0) + 1
    total = len(clean)
    entropy = 0.0
    for ch, count in char_count.items():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    max_entropy = math.log2(len(char_count)) if char_count else 1.0
    normalised = entropy / max_entropy if max_entropy > 0 else 0.0
    return EntropyAnalysis(
        shannonEntropy=round(entropy, 4),
        normalizedEntropy=round(normalised, 4),
        characterDistribution=char_count,
        anomalyFlag=entropy > SHANNON_ANOMALY_THRESHOLD,
        lowEntropyFlag=entropy < SHANNON_LOW_THRESHOLD,
    )


def detect_patterns_with_confidence(
    text: str, prioritized: Optional[List[str]] = None
) -> List[DeceptionMatch]:
    """Match every deception pattern whose indicators appear in the text."""
    lower = text.lower()
    matches: List[DeceptionMatch] = []
    prioritized = prioritized or []
    for pattern in DECEPTION_ONTOLOGY:
        matched_indicators: list[str] = []
        for indicator in pattern.indicators:
            if indicator.lower() in lower:
                matched_indicators.append(indicator)
        if matched_indicators:
            is_prioritized = pattern.id in prioritized
            base_confidence = pattern.threshold
            confidence = min(base_confidence * 1.15, 1.0) if is_prioritized else base_confidence
            matches.append(
                DeceptionMatch(
                    patternId=pattern.id,
                    patternName=pattern.name,
                    confidence=round(confidence, 4),
                    matchedIndicators=matched_indicators,
                    severity=pattern.severity,
                )
            )

    # Repetition-hammering guard: catch the "I apologize. I apologize. I apologize." pattern
    repetition_match = re.search(r"\b(\w{2,})(?:\s+\1){2,}\b", lower)
    if repetition_match:
        existing = next((m for m in matches if m.patternId == "DD-036"), None)
        indicator = f'repeated: "{repetition_match.group(1)}"'
        if existing:
            existing.matchedIndicators.append(indicator)
        else:
            base_confidence = 0.88
            confidence = min(base_confidence * 1.15, 1.0) if "DD-036" in prioritized else base_confidence
            matches.append(
                DeceptionMatch(
                    patternId="DD-036",
                    patternName="Repetitive Hammering",
                    confidence=round(confidence, 4),
                    matchedIndicators=[indicator],
                    severity="HIGH",
                )
            )
    return sorted(matches, key=lambda x: x.confidence, reverse=True)


def calculate_deception_probability(
    detected_patterns: List[DeceptionMatch], anomaly_flag: bool
) -> float:
    """Combine average confidence, coverage, and the entropy anomaly into a single probability."""
    if not detected_patterns:
        return 0.0
    avg_confidence = sum(p.confidence for p in detected_patterns) / len(detected_patterns)
    coverage_ratio = len(detected_patterns) / len(DECEPTION_ONTOLOGY)
    return round(avg_confidence * 0.6 + coverage_ratio * 0.2 + (0.2 if anomaly_flag else 0.0), 4)


def build_forensic_reasoning(
    entropy: EntropyAnalysis, detected_patterns: List[DeceptionMatch]
) -> List[str]:
    """Render the human-readable explanation that appears in every audit report."""
    reasoning: List[str] = []
    if entropy.anomalyFlag:
        reasoning.append(
            f"Shannon Entropy ({entropy.shannonEntropy:.3f} bits/char) exceeds anomaly "
            f"threshold ({SHANNON_ANOMALY_THRESHOLD}). Possible non-human origin."
        )
    if entropy.lowEntropyFlag:
        reasoning.append(
            f"Shannon Entropy ({entropy.shannonEntropy:.3f} bits/char) below "
            f"{SHANNON_LOW_THRESHOLD} -- manipulatively coherent. Possible scripted content."
        )
    for p in detected_patterns:
        reasoning.append(
            f"[{p.severity}] {p.patternName} ({p.patternId}): "
            f"{len(p.matchedIndicators)} indicator(s) matched. "
            f"Confidence: {p.confidence * 100:.1f}%."
        )
    if not reasoning:
        reasoning.append(
            "No deception patterns detected and entropy within normal band. "
            "Text appears free of the 54-pattern ontology indicators."
        )
    return reasoning


def trigger_squeal_protocol(
    input_text: str, probability: float, patterns: List[DeceptionMatch]
) -> dict:
    """Write a high-deception event to the in-memory Squeal log AND
    persist a JSON Squeal report to disk (src.engines.squeal_protocol).

    F15 cleanup: the disk writer (squeal_protocol.write_squeal_report)
    was previously dead code. The trigger now calls both paths: the
    in-memory SQUEAL_LOG list is kept as a secondary record (for the
    monitor's hide-pattern scan), and the disk write is the
    durable witness. A disk-write failure is caught and recorded in
    the in-memory record under ``disk_write_error`` so a monitor can
    surface it.
    """
    critical_patterns = [
        f"{p.patternId} {p.patternName} ({p.confidence * 100:.1f}%)"
        for p in patterns
        if p.severity in ("CRITICAL", "HIGH")
    ]
    record = {
        "triggeredAt": datetime.now(timezone.utc).isoformat(),
        "inputSnippet": input_text[:200],
        "deceptionProbability": probability,
        "criticalPatterns": critical_patterns,
        "forensicSummary": (
            f"Squeal Protocol triggered: {len(critical_patterns)} high/critical pattern(s) "
            f"detected. Probability {probability * 100:.1f}%."
        ),
    }
    SQUEAL_LOG.append(record)
    # Persist to disk via squeal_protocol.write_squeal_report. Best-effort:
    # if the disk write fails (e.g. read-only filesystem, permission),
    # record the error in the in-memory entry so a monitor can surface it.
    try:
        from src.engines.squeal_protocol import write_squeal_report
        from src.types import DeceptionReport
        report = DeceptionReport(
            inputText=input_text,
            entropy=type("E", (), {"shannonEntropy": 0.0, "normalizedEntropy": 0.0,
                                   "characterDistribution": {}, "anomalyFlag": False,
                                   "lowEntropyFlag": False})(),
            detectedPatterns=patterns,
            deceptionProbability=probability,
            structuralDeceptionFlag=probability > DECEPTION_PROBABILITY_VETO,
            forensicReasoning=[record["forensicSummary"]],
            timestamp=record["triggeredAt"],
        )
        filename = write_squeal_report(report, session_id="deception_scanner")
        record["squeal_file"] = filename
    except Exception as exc:  # pragma: no cover - defensive
        record["disk_write_error"] = repr(exc)
    return record


def audit_text(
    input_text: str,
    context: Optional[str] = None,
    prioritized_patterns: Optional[List[str]] = None,
) -> DeceptionReport:
    """Run the full deception audit on the supplied text."""
    text_to_audit = f"{input_text}\n\nContext: {context}" if context else input_text
    entropy = shannon_entropy(text_to_audit)
    detected_patterns = detect_patterns_with_confidence(text_to_audit, prioritized_patterns)
    deception_probability = calculate_deception_probability(detected_patterns, entropy.anomalyFlag)
    structural_deception_flag = (
        deception_probability > DECEPTION_PROBABILITY_VETO
        or any(p.severity == "CRITICAL" for p in detected_patterns)
    )
    forensic_reasoning = build_forensic_reasoning(entropy, detected_patterns)
    if structural_deception_flag and deception_probability > DECEPTION_PROBABILITY_VETO:
        trigger_squeal_protocol(input_text, deception_probability, detected_patterns)
    return DeceptionReport(
        inputText=input_text[:500],
        entropy=entropy,
        detectedPatterns=detected_patterns,
        deceptionProbability=deception_probability,
        structuralDeceptionFlag=structural_deception_flag,
        forensicReasoning=forensic_reasoning,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
