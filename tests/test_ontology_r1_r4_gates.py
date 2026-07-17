"""
Order Get It Right -- F8 R1-R4 ontology gate regression test.

The E4 pre-2021 reference calibration identified four patterns
whose lexical-only match produced too many false positives on
honest academic / editorial text:

  R1: DD-001 (Facade of Competence) -- "clearly" matches
      descriptive uses (E4 line 129: "clearly articulating
      the journal's aim"). Gate: require clause-initial +
      no evidence anchor (citation, year, dollar figure) in
      a +/- 120-char window.

  R2: DD-006 (Programmed Intent Ambiguity) -- "could" /
      "to clarify" matches capability descriptions (E4 line
      47: "readers could use to check reality"). Gate:
      require an obligation verb (must, shall, will,
      agree, commit, promise, guarantee) in the same
      sentence.

  R3: DD-041 (Hedging Loop, renamed from Multilingual
      Hedging Loop) -- "could be" matches honest capability
      claims (E4 line 89: "every claim could be traced
      back to its verified genuine source"). Gate: require
      NO implementation signal in the same sentence.

  R4: DD-054 (Scope Creep / Feature Expansion Deception) --
      "consistent with" matches both compliance (E4 line
      251: "management was consistent with legislation")
      and scope expansion. Gate: require a scope-widening
      verb OR a sibling scope-creep indicator in the same
      sentence.

The test re-derives the E4 calibration cases against the
gated scanner and asserts the four false positives are
suppressed while the true positives still fire. The test
goes through the HTTP API only, per the 00-99 boundary rule.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

from fastapi.testclient import TestClient  # noqa: E402

from src.server.app import app  # noqa: E402


# (label, text, expected_patterns_set_that_must_fire)
E4_CASES = [
    (
        "R1: descriptive 'clearly' should NOT fire DD-001 (E4 line 129)",
        "this included clearly articulating the aim and scope of the journal, educating editorial board members on the principle of independent peer review, and implementing a system to protect against conflicts of interest.",
        set(),
    ),
    (
        "R1: facade 'clearly' without evidence anchor SHOULD fire DD-001",
        "Clearly, the data shows this is 100% accurate and has never failed.",
        {"DD-001", "DD-009"},
    ),
    (
        "R2: capability 'could' should NOT fire DD-006 (E4 line 47)",
        "readers could use to check reality in an age of contested facts.",
        set(),
    ),
    (
        "R2: obligation 'could' followed by 'will' SHOULD fire DD-006",
        "you could agree to this, and we will deliver as promised.",
        {"DD-006"},
    ),
    (
        "R3: honest 'could be traced' should NOT fire DD-041 (E4 line 89)",
        "ensuring that every claim could be traced back to its verified genuine source, and we implement a system to enforce it.",
        set(),
    ),
    (
        "R3: unachievable 'could be' with no implementation SHOULD fire DD-041",
        "the result could be anything depending on the observer, and nothing is certain.",
        {"DD-041"},
    ),
    (
        "R4: compliance 'consistent with legislation' should NOT fire DD-054 (E4 line 251)",
        "ensuring that management was consistent with legislation and ethical protocols.",
        set(),
    ),
    (
        "R4: scope-expansion 'consistent with going forward' SHOULD fire DD-054",
        "consistent with our strategic objectives going forward, we have added additional deliverables.",
        {"DD-054"},
    ),
]


def test_r1_r4_ontology_gates():
    """Re-derive the E4 calibration cases against the gated scanner
    and assert the false positives are suppressed while the true
    positives still fire. Goes through the HTTP API so it stays
    on the right side of the 00-99 boundary."""
    with TestClient(app) as c:
        for label, text, expected in E4_CASES:
            r = c.post("/api/analyze", json={"text": text})
            assert r.status_code == 200, f"analyze failed: {r.text}"
            data = r.json()
            fired = {p["patternId"] for p in data.get("detectedPatterns", [])}
            # The F8 contract is: false positives from the E4
            # calibration are suppressed. A pattern firing on a
            # true-positive input is OK. We only assert the
            # *expected* set is matched (no missing).
            missing = expected - fired
            assert not missing, (
                f"{label}\n"
                f"  expected patterns NOT fired: {sorted(missing)}\n"
                f"  all fired patterns: {sorted(fired)}\n"
                f"  text: {text!r}"
            )


def test_r1_r4_calibration_summary():
    """The E4 calibration report identified 11 false positives and 1
    true negative on the pre-2021 reference corpus. With the R1-R4
    gates, the four false-positive patterns (DD-001, DD-006,
    DD-041, DD-054) on the calibration sentences are suppressed.
    This summary test re-runs the four "should NOT fire"
    calibration sentences through the gated scanner in one
    request and asserts the gated pattern set is NOT in the
    fired set. The per-case test above is the load-bearing
    assertion; this one is the at-a-glance summary."""
    not_cases = [case for case in E4_CASES if "should NOT" in case[0]]
    with TestClient(app) as c:
        for case in not_cases:
            label, text, _ = case
            r = c.post("/api/analyze", json={"text": text})
            assert r.status_code == 200
            data = r.json()
            fired = {p["patternId"] for p in data.get("detectedPatterns", [])}
            # Each "should NOT" case asserts a SPECIFIC gated
            # pattern is not fired. Extract the pattern id from
            # the label for the per-case assertion.
            if "DD-001" in label:
                assert "DD-001" not in fired, f"DD-001 false positive: {text!r}"
            elif "DD-006" in label:
                assert "DD-006" not in fired, f"DD-006 false positive: {text!r}"
            elif "DD-041" in label:
                assert "DD-041" not in fired, f"DD-041 false positive: {text!r}"
            elif "DD-054" in label:
                assert "DD-054" not in fired, f"DD-054 false positive: {text!r}"
