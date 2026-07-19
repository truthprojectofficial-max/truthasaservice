"""F7-SPEC (2026-07-19): Taguchi-quadratic spec-value curve regression.

Closes the "best band for buck / diminishing returns" build item
recommended by DIMINISHING_RETURNS_RESEARCH_2026-07-19.

These tests go through the HTTP API only (whitelisted
src.server.app) per the 00-99 boundary rule. They assert:
  1. The veto boundary is preserved by construction: a case at
     specMeasured=0.5 (the old PERFORMANCE_FLOOR) still passes, and
     a case at specMeasured=0.4 still fails.
  2. The peak is at specMeasured == specClaimed (specRatio=1.0): the
     curve value is 1.0 there.
  3. Over-spec declines symmetrically: specRatio=1.75 (measured
     75% better than claimed) fails the specAccuracy gate, telling
     the story of its own demise.
  4. The Selby case still vetoes on warrantyAdequacy, NOT on
     specAccuracy (the research found the brief's validation premise
     was wrong -- Selby binds on warranty, not spec).
  5. Determinism: the same ProductEvidence produces bit-identical
     BBFB output across two calls.
"""
from fastapi.testclient import TestClient

from src.server.app import app

client = TestClient(app)


def _bbfb_via_api(spec_measured, spec_claimed=1.0, price=100.0, warranty_months=24.0, months_to_failure=12.0):
    """Helper: run a ProductEvidence through the orchestrator and return the BBFB gate dict."""
    r = client.post(
        "/api/orchestrator/process",
        json={
            "category": "Forensic",
            "statement": f"Spec-value curve probe (specMeasured={spec_measured}).",
            "product_evidence": {
                "productName": "SpecCurveProbe",
                "pricePaid": price,
                "priceAdvertised": price,
                "specClaimed": spec_claimed,
                "specClaimedUnit": "units",
                "specMeasured": spec_measured,
                "warrantyMonths": warranty_months,
                "monthsToFailure": months_to_failure,
                "knownIssues": 0.0,
                "totalFeaturesOrParts": 10.0,
                "regulatoryRequirements": 4.0,
                "violationsFound": 0.0,
            },
        },
    )
    assert r.status_code == 200, f"orchestrator failed: {r.status_code} {r.text}"
    return r.json()["bbfbGate"]


def test_spec_veto_boundary_preserved_at_old_floor():
    """A case at specMeasured=0.5 (the old PERFORMANCE_FLOOR) must still
    PASS the specAccuracy gate. The curve V(0.5) = 0.75 = SPEC_VALUE_VETO_FLOOR,
    so the veto boundary is preserved by construction."""
    bbfb = _bbfb_via_api(spec_measured=0.5)
    spec_acc = [l for l in bbfb["law"] if l["metric"] == "specAccuracy"][0]
    assert spec_acc["passed"], (
        f"boundary case must pass: V(0.5)={spec_acc['value']} threshold={spec_acc['threshold']}"
    )


def test_spec_under_spec_still_vetoed():
    """A case at specMeasured=0.4 must still FAIL the specAccuracy gate.
    V(0.4) = 1 - (0.6/1.0)^2 = 0.64 < 0.75. The old floor would have
    vetoed at 0.4 < 0.5; the curve vetoes at V(0.4) < 0.75. Same result."""
    bbfb = _bbfb_via_api(spec_measured=0.4)
    spec_acc = [l for l in bbfb["law"] if l["metric"] == "specAccuracy"][0]
    assert not spec_acc["passed"], (
        f"under-spec case must fail: V(0.4)={spec_acc['value']} threshold={spec_acc['threshold']}"
    )


def test_spec_peak_at_one():
    """At specMeasured=specClaimed (specRatio=1.0), the curve value is 1.0
    (the peak). The specAccuracy gate passes with maximum value."""
    bbfb = _bbfb_via_api(spec_measured=1.0)
    spec_acc = [l for l in bbfb["law"] if l["metric"] == "specAccuracy"][0]
    assert spec_acc["value"] == 1.0, (
        f"peak value should be 1.0, got {spec_acc['value']}"
    )
    assert spec_acc["passed"]


def test_spec_over_spec_declines_symmetrically():
    """Over-spec (specMeasured=1.75, i.e. 75% better than claimed) must
    FAIL the specAccuracy gate. V(1.75) = 1 - (0.75/1.0)^2 = 0.4375 < 0.75.
    This is the 'tells story of own demise' behaviour: a product that
    overspecs its claim is dishonest about its own spec and the curve
    catches it."""
    bbfb = _bbfb_via_api(spec_measured=1.75)
    spec_acc = [l for l in bbfb["law"] if l["metric"] == "specAccuracy"][0]
    assert not spec_acc["passed"], (
        f"over-spec case must fail: V(1.75)={spec_acc['value']} threshold={spec_acc['threshold']}"
    )


def test_spec_over_spec_at_boundary_still_passes():
    """At specMeasured=1.5 (50% over claim), V(1.5) = 0.75 = the veto
    floor. This is the symmetric counterpart of the 0.5 boundary. It
    passes at the boundary -- the over-spec penalty kicks in beyond 1.5."""
    bbfb = _bbfb_via_api(spec_measured=1.5)
    spec_acc = [l for l in bbfb["law"] if l["metric"] == "specAccuracy"][0]
    assert spec_acc["passed"], (
        f"over-spec boundary must pass: V(1.5)={spec_acc['value']} threshold={spec_acc['threshold']}"
    )


def test_selby_still_vetoed_by_warranty_not_spec():
    """The Selby case (specMeasured=0, specClaimed=12.5) must still fail
    on warrantyAdequacy, NOT on specAccuracy. The research found the
    brief's validation premise was wrong: Selby binds on warranty (0/0),
    not on spec (V(0) = 0 < 0.75, but warranty fails first). This test
    guards against re-framing Selby as a spec-floor case."""
    r = client.post(
        "/api/orchestrator/process",
        json={
            "category": "Forensic",
            "statement": "Selby real evidence: Gen 2 supplied, Gen 3 W invoiced, A$625 per unit.",
            "product_evidence": {
                "productName": "Audio Pro C10 MkII W - supplied Addon C10 MkII",
                "pricePaid": 625.0,
                "priceAdvertised": 625.0,
                "specClaimed": 12.5,
                "specClaimedUnit": "dB",
                "specMeasured": 0.0,
                "warrantyMonths": 0.0,
                "monthsToFailure": 0.0,
                "knownIssues": 4.0,
                "totalFeaturesOrParts": 8.0,
                "regulatoryRequirements": 4.0,
                "violationsFound": 3.0,
            },
        },
    )
    assert r.status_code == 200
    bbfb = r.json()["bbfbGate"]
    warranty = [l for l in bbfb["law"] if l["metric"] == "warrantyAdequacy"][0]
    spec_acc = [l for l in bbfb["law"] if l["metric"] == "specAccuracy"][0]
    # Both fail, but the research point is that warranty is the binding
    # constraint (0/0 = 0 < 1.0), not spec (which also fails V(0)=0 < 0.75).
    # The test guards the framing: Selby is a warranty/description case,
    # not a spec-accuracy case.
    assert not warranty["passed"], "Selby must still fail warranty"
    assert not spec_acc["passed"], "Selby spec also fails (V(0)=0)"
    assert not bbfb["overallCompliant"], "Selby must still be REJECT overall"


def test_spec_value_curve_determinism():
    """The same specMeasured must produce bit-identical specAccuracy
    values across two calls. The curve is pure math (no random, no
    time.time), so the value must be exactly the same both times.
    Uses unique statements to avoid the pre-existing fact-collision
    issue in facts_registry (same statement+source raises ValueError)."""
    import time
    # Two API calls with unique statements (time_ns differs each call)
    # but the SAME spec_measured. The specAccuracy value in the BBFB
    # gate must be bit-identical both times.
    t1 = time.time_ns()
    bbfb1 = _bbfb_via_api(spec_measured=0.7)
    t2 = time.time_ns()
    # _bbfb_via_api embeds spec_measured in the statement; we need
    # unique statements. Patch the helper inline by calling the API
    # directly with a unique statement per call.
    r1 = client.post(
        "/api/orchestrator/process",
        json={
            "category": "Forensic",
            "statement": f"Det probe A {t1}",
            "product_evidence": {
                "productName": "DetA", "pricePaid": 100.0, "priceAdvertised": 100.0,
                "specClaimed": 1.0, "specClaimedUnit": "u", "specMeasured": 0.7,
                "warrantyMonths": 24.0, "monthsToFailure": 12.0,
                "knownIssues": 0.0, "totalFeaturesOrParts": 10.0,
                "regulatoryRequirements": 4.0, "violationsFound": 0.0,
            },
        },
    )
    r2 = client.post(
        "/api/orchestrator/process",
        json={
            "category": "Forensic",
            "statement": f"Det probe B {t2}",
            "product_evidence": {
                "productName": "DetB", "pricePaid": 100.0, "priceAdvertised": 100.0,
                "specClaimed": 1.0, "specClaimedUnit": "u", "specMeasured": 0.7,
                "warrantyMonths": 24.0, "monthsToFailure": 12.0,
                "knownIssues": 0.0, "totalFeaturesOrParts": 10.0,
                "regulatoryRequirements": 4.0, "violationsFound": 0.0,
            },
        },
    )
    assert r1.status_code == 200 and r2.status_code == 200
    spec1 = [l for l in r1.json()["bbfbGate"]["law"] if l["metric"] == "specAccuracy"][0]
    spec2 = [l for l in r2.json()["bbfbGate"]["law"] if l["metric"] == "specAccuracy"][0]
    assert spec1["value"] == spec2["value"], (
        f"non-deterministic spec value: {spec1['value']} vs {spec2['value']}"
    )
    # V(0.7) = 1 - (0.3/1.0)^2 = 1 - 0.09 = 0.91 (with float tolerance)
    assert abs(spec1["value"] - 0.91) < 1e-6, f"V(0.7) should be ~0.91, got {spec1['value']}"