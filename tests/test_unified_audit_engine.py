"""
Order Get It Right -- Unified audit/value/deception engine tests.

These tests assert that the all3-in-one process exists, is deterministic,
and negates human error by always producing the same final verdict for
a given input. They go through the HTTP API only.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

from fastapi.testclient import TestClient  # noqa: E402
from src.server.app import app  # noqa: E402


def _sample_evidence_payload():
    return {
        "productName": "Audio Pro W-Generation",
        "pricePaid": 599,
        "priceAdvertised": 599,
        "specClaimed": 106,
        "specClaimedUnit": "dB",
        "specMeasured": 94,
        "warrantyMonths": 24,
        "monthsToFailure": 18,
        "knownIssues": 3,
        "totalFeaturesOrParts": 12,
        "regulatoryRequirements": 4,
        "violationsFound": 1,
        "notes": "Sample evidence for unified engine test.",
    }


def test_unified_engine_returns_all_three_gates():
    with TestClient(app) as c:
        r = c.post(
            "/api/orchestrator/process",
            json={
                "category": "Technical",
                "statement": "The product clearly performs exactly as advertised and has never failed.",
                "product_evidence": _sample_evidence_payload(),
            },
        )
    assert r.status_code == 200
    body = r.json()
    assert "deceptionGate" in body
    assert "bbfbGate" in body
    assert "optionalityGate" in body
    assert "finalAction" in body
    assert "reason" in body
    assert "ledgerRoot" in body
    assert body["finalAction"] in {"GO", "DEFER", "TEST FIRST", "REJECT", "REFUSED", "REVIEW_REQUIRED"}


def test_unified_engine_is_deterministic():
    """Same input + same evidence must produce the same finalAction and root fields.

    The in-memory facts registry forbids duplicate (statement, source)
    pairs across a single process lifetime, so we vary a harmless
    suffix to keep the inputs distinct while keeping the
    verdict-relevant content identical.
    """
    base = {
        "category": "Technical",
        "statement": "Routine inspection found the device output is 94 dB, rated 106 dB.",
        "product_evidence": _sample_evidence_payload(),
    }
    with TestClient(app) as c:
        r1 = c.post("/api/orchestrator/process", json={**base, "statement": base["statement"] + " [run-1]"})
        assert r1.status_code == 200
    with TestClient(app) as c:
        r2 = c.post("/api/orchestrator/process", json={**base, "statement": base["statement"] + " [run-2]"})
        assert r2.status_code == 200
    b1 = r1.json()
    b2 = r2.json()
    assert b1["finalAction"] == b2["finalAction"]
    assert b1["reason"] == b2["reason"]
    assert b1["deceptionGate"]["score"] == b2["deceptionGate"]["score"]
    assert b1["bbfbGate"]["overallCompliant"] == b2["bbfbGate"]["overallCompliant"]


def test_unified_engine_blocks_deceptive_input():
    """A statement with a HIGH/CRITICAL deception pattern must not be GO."""
    with TestClient(app) as c:
        r = c.post(
            "/api/orchestrator/process",
            json={
                "category": "Governance",
                "statement": (
                    "I apologize for the confusion. Based on my analysis the data clearly "
                    "shows this is 100% accurate and has never failed."
                ),
                "product_evidence": _sample_evidence_payload(),
            },
        )
    assert r.status_code == 200
    body = r.json()
    assert body["finalAction"] != "GO", f"deceptive input allowed to pass: {body['finalAction']}"
