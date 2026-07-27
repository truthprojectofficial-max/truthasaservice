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


# F8 (R1-R4, 2026-07-18): structural co-text gates for four patterns.
# The lexical-only match on DD-001/DD-006/DD-041/DD-054 produced too many
# false positives on honest academic / editorial text (see E4 calibration
# report -- see the operator's calibration documentation).
# These helpers run a small structural check on the surrounding text and
# drop the lexical match when the gate fails.

_OBLIGATION_VERBS = {
    "must", "shall", "will", "would", "agree", "agreed", "commit",
    "committed", "promise", "promised", "guarantee", "guaranteed",
    "undertake", "undertook", "oblige", "obliged", "require", "required",
    "expect", "expected", "ensure", "ensured", "responsible", "liable",
}

_SCOPE_WIDENING_VERBS = {
    "expand", "expands", "expanded", "expanding",
    "widen", "widens", "widened", "widening",
    "extend", "extends", "extended", "extending",
    "include", "includes", "included", "including",
    "add", "adds", "added", "adding",
    "cover", "covers", "covered", "covering",
    "scope", "scopes", "scoped", "scoping",
    "broaden", "broadens", "broadened",
    "incorporate", "incorporates", "incorporated",
    "introduce", "introduces", "introduced",
    "expand", "grew", "grow", "growth",
}

# Citations / numeric anchors that imply "supporting evidence is present"
# in the same clause as a "clearly" claim. If any of these appear within
# ~120 chars of "clearly", the indicator is descriptive, not a facade.
_EVIDENCE_ANCHORS = re.compile(
    r"\b(?:\d{4}|\d+\.\d+|\$\d|cite|cited|see\s|figure|table|appendix|"
    r"https?://|www\.|doi\s*[:=]|et\s*al\.?|ibid\.)\b",
    re.IGNORECASE,
)

_CLAUSE_INITIAL_CLEARLY = re.compile(
    r"(?:^|[.;!?\n]\s+|\s+and\s+|\s+but\s+)(clearly)\b",
    re.IGNORECASE,
)


def _gate_dd_001_clarity(text: str, lower: str, matched: list[str]) -> bool:
    """R1: a DD-001 match stands only if the indicator is in a clause-initial
    claim position AND the surrounding text does not contain an evidence
    anchor (a citation, a year, a dollar figure, etc.). The structural test
    rejects honest descriptive uses of "clearly" such as
    "clearly articulating the journal's aim" (E4 line 129)."""
    if "clearly" not in matched:
        return True  # other DD-001 indicators fire on different surface forms
    # If ANY of the other indicators fire, the pattern is still load-bearing.
    if len(matched) > 1:
        return True
    # Pure "clearly" match: require clause-initial + no evidence anchor nearby.
    if not _CLAUSE_INITIAL_CLEARLY.search(lower):
        return False
    # Find every "clearly" occurrence; if any of them has an evidence anchor
    # within +/- 120 chars, the pattern is descriptive.
    for m in _CLAUSE_INITIAL_CLEARLY.finditer(lower):
        start, end = m.start(1), m.end(1)
        window = lower[max(0, start - 120): min(len(lower), end + 120)]
        if _EVIDENCE_ANCHORS.search(window):
            return False
    return True


def _gate_dd_006_obligation(text: str, lower: str, matched: list[str]) -> bool:
    """R2: a DD-006 match on "could" / "to clarify" stands only if the
    sentence containing the indicator has an obligation verb. Descriptive
    uses of "could" (e.g. "readers could use to check reality" -- E4 line
    47) are honest hedging about capability, not programmed ambiguity."""
    if not ({"could", "to clarify"} & set(matched)):
        return True  # other DD-006 indicators not gated
    # Build a sentence index once.
    sentences = re.split(r"(?<=[.;!?\n])\s+", text)
    for sent in sentences:
        s_low = sent.lower()
        if not any(ind.lower() in s_low for ind in matched):
            continue
        # If this sentence has an obligation verb, the gate passes.
        words = set(re.findall(r"[a-z]+", s_low))
        if words & _OBLIGATION_VERBS:
            return True
    return False


def _gate_dd_041_capability(text: str, lower: str, matched: list[str]) -> bool:
    """R3: a DD-041 match on "could be" stands only if the sentence claims
    an unachievable capability. The honest use (E4 line 89: "every claim
    could be traced back to its verified genuine source") describes a
    real, implemented method -- no match. The deceptive use ("the result
    could be anything depending on the observer") claims an unachievable
    capability -- match.

    Heuristic: if the sentence following "could be" describes a method
    that another sentence claims is implemented (e.g. "we implement a
    system to" + "could be traced"), the "could be" is honest capability
    language. We treat the indicator as honest by default and require a
    non-implementation signal in the sentence to fire."""
    if "could be" not in matched:
        return True
    # Walk sentences that contain "could be"
    sentences = re.split(r"(?<=[.;!?\n])\s+", text)
    fired = False
    for sent in sentences:
        s_low = sent.lower()
        if "could be" not in s_low:
            continue
        # An UNACHIEVABLE capability claim is one where the sentence has
        # no implementation verb (implement, deploy, build, run, write,
        # create, ensure) AND no concrete method noun (system, method,
        # tool, process, protocol, framework, function, procedure).
        impl_signals = {
            "implement", "implements", "implemented", "deploy", "deployed",
            "build", "builds", "built", "run", "runs", "ran",
            "write", "writes", "wrote", "create", "creates", "created",
            "ensure", "ensures", "ensured", "system", "method",
            "tool", "process", "protocol", "framework", "function",
            "procedure", "module", "library", "service", "platform",
            "mechanism", "infrastructure",
        }
        words = set(re.findall(r"[a-z]+", s_low))
        if words & impl_signals:
            continue  # sentence has implementation signal -- honest use
        fired = True
        break
    return fired


def _gate_dd_054_scope(text: str, lower: str, matched: list[str]) -> bool:
    """R4: a DD-054 match on "consistent with" stands only if the sentence
    containing the indicator also has a scope-widening verb OR a sibling
    scope-creep indicator. Compliance use ("management was consistent with
    legislation" -- E4 line 251) is a held scope, not an expansion -- no
    match."""
    if "consistent with" not in matched:
        return True  # other DD-054 indicators not gated
    sentences = re.split(r"(?<=[.;!?\n])\s+", text)
    sibling_widening_indicators = {
        "expanded the scope", "continuous improvement", "value-add",
        "going forward", "additional deliverables", "new deliverables",
        "alignment with strategic objectives", "stakeholder expectations",
    }
    for sent in sentences:
        s_low = sent.lower()
        if "consistent with" not in s_low:
            continue
        words = set(re.findall(r"[a-z]+", s_low))
        if words & _SCOPE_WIDENING_VERBS:
            return True
        if any(ind in s_low for ind in sibling_widening_indicators):
            return True
    return False


# R6 (2026-07-27): DD-070 (Authority Mimicry) citation gate. The authority
# invoke markers ("experts suggest", "studies show", "it is generally
# considered") fire only when no citation follows in a +/- 120 char window.
# Honest academic text that cites a real source is NOT a match. This mirrors
# the R1 evidence-anchor gate on DD-001, extended to the authority-invoke
# lexical set. See AI_DIALECT_FALSE_NEGATIVES_RESEARCH_2026-07-27.md.

_AUTHORITY_INVOKE_INDICATORS = {
    "experts suggest", "industry best practices indicate",
    "it is generally considered", "studies show", "widely regarded as",
    "commonly accepted that", "according to leading", "the consensus is",
}

# Named-source heuristic: "Surname et al", "Surname (year)", "per Surname",
# "according to Surname", "Surname found/showed/reported/demonstrated/
# concluded". Compiled once at import (determinism + perf).
_NAMED_SOURCE = re.compile(
    r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+et\s+al\.?|"
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s*\(\d{4}|"
    r"per\s+[A-Z][a-z]+|according\s+to\s+[A-Z][a-z]+|"
    r"[A-Z][a-z]+\s+(?:found|showed|reported|demonstrated|concluded))\b"
)


def _gate_dd_070_authority(text: str, lower: str, matched: list[str]) -> bool:
    """R6: a DD-070 match stands only if the authority-invoke marker appears
    WITHOUT a citation anchor (a year, a number, a named source, a URL, a
    DOI, et al., ibid.) within +/- 120 chars. Honest academic text that
    writes 'Smith et al. (2024) found that experts suggest...' has a real
    citation and is NOT a match; the bare 'experts suggest this is best
    practice' with no source IS a match."""
    if not (set(matched) & _AUTHORITY_INVOKE_INDICATORS):
        return True
    for ind in matched:
        if ind not in _AUTHORITY_INVOKE_INDICATORS:
            continue
        start = 0
        while True:
            idx = lower.find(ind, start)
            if idx == -1:
                break
            window = lower[max(0, idx - 120): min(len(lower), idx + len(ind) + 120)]
            if _EVIDENCE_ANCHORS.search(window) or _NAMED_SOURCE.search(window):
                # citation present near this occurrence -- honest use,
                # advance to look for a bare (uncited) occurrence elsewhere.
                start = idx + len(ind)
                continue
            # at least one occurrence has no citation -- the pattern fires.
            return True
    return False


# R7 (2026-07-27): DD-071 (Work-Claim Without Evidence) evidence gate. The
# work-claim markers ("I've updated the file", "the test passes now", "I
# fixed the bug") fire only when no evidence follows in the same turn: no
# code block fence, no file path, no command output snippet, no diff marker.
# Honest work reports that show the diff / output are NOT a match. See
# AI_DIALECT_FALSE_NEGATIVES_RESEARCH_2026-07-27.md.

_WORK_CLAIM_INDICATORS = {
    "i've updated the file", "the test passes now", "i fixed the bug",
    "i've written the script", "the changes are applied",
    "i've already done that", "the output confirms",
}

_EVIDENCE_FOLLOW_ANCHORS = re.compile(
    r"(?:```|^\s*diff\b|^\s*\+\+\+\s|^\s*---\s|^\s*@@\s|"
    r"\b(?:\.py|\.js|\.ts|\.rs|\.json|\.md|\.txt|\.yaml|\.yml|\.toml)\b|"
    r"\b(?:src|tests|config)/[^\s]+|"
    r"\bPASSED\b|\bFAILED\b|\bpassed\b.*\bskipped\b|"
    r"\b\d+\s+passed\b|\bexit\s+code\s+\d|"
    r"\bcommit\s+[0-9a-f]{7,}|"
    r"^\s*\$|^\s*>\s|^\s*C:\\)",
    re.IGNORECASE | re.MULTILINE,
)


def _gate_dd_071_work_claim(text: str, lower: str, matched: list[str]) -> bool:
    """R7: a DD-071 match stands only if the work-claim marker appears
    WITHOUT a following evidence anchor (a code block fence, a file path,
    a diff marker, a command-output token, a commit sha) within a 400-char
    forward window. Honest work reports that show the diff / the file path
    / the test output after the claim are NOT a match; the bare 'I've
    updated the file' with no diff IS a match. The forward window (not the
    whole text) prevents an unrelated code block elsewhere in a long input
    from suppressing a genuinely bare deceptive claim."""
    if not (set(matched) & _WORK_CLAIM_INDICATORS):
        return True
    for ind in matched:
        if ind not in _WORK_CLAIM_INDICATORS:
            continue
        start = 0
        while True:
            idx = lower.find(ind, start)
            if idx == -1:
                break
            fwd = text[idx: min(len(text), idx + 400)]
            if _EVIDENCE_FOLLOW_ANCHORS.search(fwd):
                # evidence follows this occurrence -- honest claim, advance.
                start = idx + len(ind)
                continue
            # at least one occurrence has no following evidence -- fires.
            return True
    return False


# F8 (R1-R4, 2026-07-18): structural co-text gates for four patterns.
# ... [existing R1-R4 gates unchanged] ...

# R5-EXTENDED-2 (2026-07-18): legal-register / hedge gate.
#
# Honest legal text -- oral-argument transcripts, AI disclosure statements,
# and writerly legal commentary -- uses politeness markers ("I apologize",
# "let me clarify") and hedges ("could", "maybe", "I doubt") that are normal
# in adversarial/courtroom register. Without a register gate these surface
# forms fire DD-004, DD-006, DD-011, DD-027 and DD-041 and produce false
# positives. R5 suppresses those patterns when:
#   1. the text carries legal-register markers (court roles, procedure words,
#      citations, legal vocabulary), AND
#   2. only the register-sensitive hedge/politeness patterns fire, AND
#   3. no fabrication/lie-of-certainty pattern (DD-009, DD-036, etc.) fires.
# If a fabrication marker is present (e.g. "100% accurate" in EVAL-032) the
# full original match set is preserved so the deception is still reported.

_LEGAL_REGISTER_MARKERS = [
    "justice ", "section ", " v. ", " v ", "court", "established in", "dispositive",
    "statute", "framework", "oral argument", "counsel", "appellant", "respondent",
    "petitioner", "defendant", "plaintiff", "evidence", "testimony", "burden of proof",
    "precedent", "binding", "controlling", "overruled", "affirmed", "reversed",
    "the court held", "we hold", "it is so ordered",
    "lawyer", "attorney", "legal", "argument", "brief", "motion", "pleading",
    "jurisdiction", "admissible", "hearsay", "tort", "contract", "statutory",
]

_REGISTER_SENSITIVE_PATTERNS = {"DD-004", "DD-006", "DD-011", "DD-027", "DD-041"}
_FABRICATION_PATTERNS = {"DD-001", "DD-009", "DD-019", "DD-020", "DD-036", "DD-040", "DD-052"}


def _has_legal_register(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in _LEGAL_REGISTER_MARKERS)


def _apply_r5_legal_register_gate(
    matches: List[DeceptionMatch], text: str
) -> List[DeceptionMatch]:
    """R5-EXTENDED-2: suppress hedge/politeness patterns in legal register
    when no fabrication marker is present."""
    if not matches:
        return matches
    if not _has_legal_register(text):
        return matches
    fired_ids = {m.patternId for m in matches}
    if fired_ids & _FABRICATION_PATTERNS:
        return matches
    if fired_ids.issubset(_REGISTER_SENSITIVE_PATTERNS):
        return []
    return matches


_R1_R4_GATES = {
    "DD-001": _gate_dd_001_clarity,
    "DD-006": _gate_dd_006_obligation,
    "DD-041": _gate_dd_041_capability,
    "DD-054": _gate_dd_054_scope,
    # R6/R7 (2026-07-27): AI-dialect false-negative closures.
    "DD-070": _gate_dd_070_authority,
    "DD-071": _gate_dd_071_work_claim,
}


def detect_patterns_with_confidence(
    text: str, prioritized: Optional[List[str]] = None
) -> List[DeceptionMatch]:
    """Match every deception pattern whose indicators appear in the text,
    then apply the F8 R1-R4 structural co-text gates, the R6/R7 AI-dialect
    gates, and the R5-EXTENDED-2 legal-register hedge gate. The gates are
    documented in deception_ontology_data.py and in the E4/E5 calibration
    reports."""
    lower = text.lower()
    matches: List[DeceptionMatch] = []
    prioritized = prioritized or []
    for pattern in DECEPTION_ONTOLOGY:
        matched_indicators: list[str] = []
        for indicator in pattern.indicators:
            if indicator.lower() in lower:
                matched_indicators.append(indicator)
        if not matched_indicators:
            continue
        # F8 R1-R4 structural gates (DD-001, DD-006, DD-041, DD-054).
        gate = _R1_R4_GATES.get(pattern.id)
        if gate is not None and not gate(text, lower, matched_indicators):
            continue  # gate rejected the lexical match
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

    # R5-EXTENDED-2 legal-register hedge gate
    matches = _apply_r5_legal_register_gate(matches, text)
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
            "Text appears free of the 71-pattern ontology indicators."
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
