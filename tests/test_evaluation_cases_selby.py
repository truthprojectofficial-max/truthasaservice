"""
Order Get It Right -- Selby consumer-dispute EVAL fixture.

Real-world case: Barnett v Selby Acoustics (Audio Pro C10 MkII W bait-and-switch).
The held evidence pack is at:
  C:/Users/justo/OneDrive/Documents/My Project/files for inspiration and code/SELBY EVEDENCE PACK.txt

This test uses anonymised, synthetic excerpts that preserve the linguistic
surface forms found in the retailer correspondence and the factual invoice
data, without embedding client identifying material into the committed source.

Positive case SELBY-001: a retailer response that combines apology theatre,
false certainty, and major-failure denial -- the deception surface forms that
appear in actual consumer-dispute correspondence.

Negative case SELBY-002: a dry, factual evidentiary statement matching the
invoice and technical-gap details -- no deception markers.

Both cases go through the HTTP /api/analyze endpoint to stay on the right side
of the 00-99 boundary.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

from fastapi.testclient import TestClient  # noqa: E402
from src.server.app import app  # noqa: E402


SELBY_POSITIVE_CASES = [
    (
        "SELBY-001",
        "Retailer apology + false certainty + major-failure denial",
        (
            "I apologize for the confusion regarding your order. I can assure you that the Audio Pro C10 MKII "
            "units we supplied are 100% accurate to the invoice and are working as intended. There is no failure "
            "occurred here; it is a minor issue and the system is stable. We have reviewed your evidence carefully "
            "and the original decision was correct."
        ),
        {"DD-004", "DD-009", "DD-020"},
    ),
]

SELBY_NEGATIVE_CASES = [
    (
        "SELBY-002",
        "Dry invoice and technical-gap statement",
        (
            "Tax Invoice dated 6 December 2025. Product: Audio Pro C10 MKII Wireless Multiroom Speaker White. "
            "ID 142376, SKU C10 MKII-WH, quantity 1, unit price $625.00, total paid $625.00. The supplied unit is an "
            "Addon C10 MkII Gen 2. Verified specifications: measured output 94 dB SPL at 1 kHz, rated output 106 dB SPL, "
            "gap 12 dB. Warranty period 24 months."
        ),
    ),
]


def _analyze(text: str):
    with TestClient(app) as client:
        r = client.post("/api/analyze", json={"text": text})
        assert r.status_code == 200, f"analyze failed: {r.text}"
        return r.json()


@pytest.mark.parametrize("case_id,label,text,expected_patterns", SELBY_POSITIVE_CASES)
def test_selby_positive_case(case_id, label, text, expected_patterns):
    """Consumer-dispute deceptive register must fire expected ontology patterns."""
    data = _analyze(text)
    fired = {p["patternId"] for p in data.get("detectedPatterns", [])}
    prob = data.get("deceptionProbability", 0.0)

    missing = expected_patterns - fired
    assert not missing, (
        f"{case_id} {label}: expected patterns not fired: {sorted(missing)}. "
        f"fired={sorted(fired)} prob={prob:.4f}"
    )
    assert prob >= 0.3, (
        f"{case_id} {label}: expected deceptive (prob>=0.3) but got {prob:.4f}"
    )


@pytest.mark.parametrize("case_id,label,text", SELBY_NEGATIVE_CASES)
def test_selby_negative_case(case_id, label, text):
    """Dry factual evidence statement must not fire deception patterns."""
    data = _analyze(text)
    fired = {p["patternId"] for p in data.get("detectedPatterns", [])}
    prob = data.get("deceptionProbability", 0.0)

    assert not fired, (
        f"{case_id} {label}: expected no patterns but fired {sorted(fired)} "
        f"prob={prob:.4f}"
    )
    assert prob < 0.3, (
        f"{case_id} {label}: expected low deception probability, got {prob:.4f}"
    )


def test_selby_suite_case_count():
    """Selby fixture contains the expected number of cases."""
    total = len(SELBY_POSITIVE_CASES) + len(SELBY_NEGATIVE_CASES)
    assert total == 2, f"expected 2 Selby cases, found {total}"
