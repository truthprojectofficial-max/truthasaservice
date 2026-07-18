"""Tests for /api/parse/evidence.

The evidence parser must turn plain product text into the numeric fields the
BBFB and Real-Options Lattice engines consume, without the operator doing
unit conversion or hand-extraction.

These tests use the public HTTP API only -- no src/ imports per 00-99 boundary.
"""
import pytest
from fastapi.testclient import TestClient

from src.server.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _parse(client: TestClient, text: str) -> dict:
    resp = client.post("/api/parse/evidence", json={"text": text})
    assert resp.status_code == 200, resp.text
    return resp.json()["parsed"]


def test_parse_speaker_example_full(client):
    """The Audio Pro speaker text the operator pasted should parse cleanly."""
    text = (
        "Audio Pro W-Gen Speaker. Price: $599. The product is advertised with a maximum output of 106 dB. "
        "Our independent measurement showed 94 dB. Warranty is 24 months. The unit failed after 18 months. "
        "Three customers have reported issues. The device has 12 components. "
        "Four regulatory requirements apply, one violation found."
    )
    parsed = _parse(client, text)
    assert parsed["product_name"] == "Audio Pro W-Gen Speaker"
    assert parsed["price_paid"] == 599.0
    assert parsed["spec_claimed"] == 106.0
    assert parsed["spec_claimed_unit"] == "db"
    assert parsed["spec_measured"] == 94.0
    assert parsed["warranty_months"] == 24.0
    assert parsed["months_to_failure"] == 18.0
    assert parsed["known_issues"] == 3
    assert parsed["total_features_or_parts"] == 12
    assert parsed["regulatory_requirements"] == 4
    assert parsed["violations_found"] == 1
    assert parsed["confidence"] == "high"


def test_parse_minimal_text_no_numbers(client):
    """Text without enough numeric product indicators returns None."""
    resp = client.post("/api/parse/evidence", json={"text": "Hello world"})
    assert resp.status_code == 200
    assert resp.json()["parsed"] is None

    resp = client.post("/api/parse/evidence", json={"text": "x" * 39})
    assert resp.status_code == 200
    assert resp.json()["parsed"] is None


def test_parse_written_numbers_and_clauses(client):
    """Written-out numbers and comma-separated clauses must not cross-pollinate."""
    text = (
        "Model: Acme Router. Listed at $199. It promises a range of 50 m. "
        "We measured 38 m. Two year warranty. It died after ten months. "
        "Five users reported problems. It has eight ports. "
        "Three safety standards apply, two breaches confirmed."
    )
    parsed = _parse(client, text)
    assert parsed["product_name"] == "Acme Router"
    assert parsed["price_paid"] == 199.0
    assert parsed["spec_claimed"] == 50.0
    assert parsed["spec_measured"] == 38.0
    assert parsed["warranty_months"] == 24.0  # 2 years
    assert parsed["months_to_failure"] == 10.0
    assert parsed["known_issues"] == 5
    assert parsed["total_features_or_parts"] == 8
    assert parsed["regulatory_requirements"] == 3
    assert parsed["violations_found"] == 2


def test_parse_falls_back_to_first_line_name(client):
    """If no explicit label, use the leading words of the first line."""
    text = "SuperWidget 3000. Price $49. Warranty 12 months. Failed after 3 months."
    parsed = _parse(client, text)
    assert parsed["product_name"] == "SuperWidget 3000"
    assert parsed["warranty_months"] == 12.0
    assert parsed["months_to_failure"] == 3.0


def test_parse_no_product_triggers_returns_none(client):
    """Random text without price/warranty/spec/model/device/product returns None."""
    parsed = _parse(client, "The quick brown fox jumps over the lazy dog. " * 5)
    assert parsed is None


def test_parse_single_spec_hit_uses_same_value(client):
    """A single spec measurement sets both claimed and measured to the same value."""
    text = "Device X. Price $100. Measured 75 dB. Warranty 6 months."
    parsed = _parse(client, text)
    assert parsed["spec_claimed"] == 75.0
    assert parsed["spec_measured"] == 75.0
    assert parsed["spec_claimed_unit"] == "db"
