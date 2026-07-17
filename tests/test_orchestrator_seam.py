"""
Order Get It Right -- Orchestrator seam regression tests.

These tests pin down two specific behaviours of the orchestrator's
HTTP surface (``POST /api/orchestrator/process``) that were real
seams in the live code:

  1. Statement truncation
     The Orchestrator.process_input() method used to slice the
     incoming statement to 500 characters when sealing the fact
     record, but ran the full statement through the deception
     scanner. The result: the fact stored in the registry did not
     match the text that was actually audited. The fix seals the
     full statement. The test asserts the fact record's statement
     is the full input, character-for-character.

  2. SHUTDOWN seal on lifespan exit
     Orchestrator.shutdown() appends a SHUTDOWN block to the Merkle
     chain. The HTTP lifespan used to be a no-op on shutdown, so a
     clean uvicorn stop left the chain without a final SHUTDOWN
     block. The fix calls Orchestrator().shutdown() from the
     lifespan shutdown branch. The test asserts that after the
     TestClient context manager exits cleanly, the chain has at
     least one new SHUTDOWN block relative to the count before.

The boundary rule still applies: this test goes through the HTTP
API only. It does not import from src/ except for the whitelisted
app object.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

from fastapi.testclient import TestClient  # noqa: E402

from src.server.app import app  # noqa: E402


def test_orchestrator_seals_full_statement_not_truncated():
    """A 600-character statement must be sealed in full to the fact record.

    Pre-fix, Orchestrator.process_input() did
    ``add_fact(category, statement[:500], ...)`` and
    ``data={"statement": statement[:500]}`` in the delegator token,
    while the deception scan received the full statement. The fact
    record diverged from what was actually audited. The fix
    removes the silent slice.
    """
    long_statement = (
        "The product model is C10 MKII. " * 30  # 660 characters
    )
    assert len(long_statement) > 500, (
        f"test input not long enough: {len(long_statement)} chars"
    )

    with TestClient(app) as c:
        r = c.post(
            "/api/orchestrator/process",
            json={"category": "Technical", "statement": long_statement},
        )
        assert r.status_code == 200, f"orchestrator call failed: {r.text}"
        body = r.json()
        fact_id = body["factId"]

        # Read the fact back and confirm the full statement is sealed.
        r2 = c.get("/api/facts")
        assert r2.status_code == 200
        facts = r2.json()["facts"]
        match = next((f for f in facts if f["id"] == fact_id), None)
        assert match is not None, (
            f"fact id {fact_id} from orchestrator response not in /api/facts"
        )
        assert match["statement"] == long_statement, (
            f"orchestrator truncated the fact statement: "
            f"len(sealed)={len(match['statement'])}, len(input)={len(long_statement)}"
        )
        assert len(match["statement"]) > 500, (
            f"sealed statement is suspiciously short: {len(match['statement'])} chars"
        )


def test_orchestrator_full_statement_runs_full_deception_scan():
    """The full statement (not a prefix) must be what the audit saw.

    Companion to the above: even though the orchestrator now seals
    the full statement, this test confirms the deception scan
    continues to see the full text. We use a statement that
    contains a CRITICAL deception pattern only in the second half
    (after char 500). Pre-fix, the deception scan would still have
    seen the full text, so this is a regression sentinel: if
    someone re-introduces a slice before the scan, this test will
    flip from REFUSED to CLEAN.
    """
    # Build a clean prefix, then a deceptive suffix past the 500-char mark.
    prefix = "Routine technical specification. " * 30  # ~900 chars, all clean
    deceptive_suffix = (
        "I apologize for the confusion. Based on my analysis the data "
        "clearly shows this is 100% accurate and has never failed."
    )
    statement = prefix + deceptive_suffix
    # Confirm the CRITICAL pattern is past the 500-char mark in the prefix-only
    # view. If the deceptive suffix sat at position < 500, this assertion would
    # not guard against a future regression that re-introduced truncation.
    assert "clearly shows" in statement[500:], (
        "test setup error: deceptive suffix must lie past char 500"
    )

    with TestClient(app) as c:
        r = c.post(
            "/api/orchestrator/process",
            json={"category": "Governance", "statement": statement},
        )
        assert r.status_code == 200
        body = r.json()
        # The orchestrator must catch the deception in the full text.
        # If the scan ever only sees a clean prefix, this flips to CLEAN
        # and the test fires.
        assert body["finalAction"] == "REFUSED", (
            f"deception in statement suffix was missed: finalAction={body['finalAction']!r}, "
            f"patternsFired={body.get('patternsFired')}"
        )
        assert len(body["patternsFired"]) > 0, (
            "no patterns fired on a statement with embedded deception"
        )


def test_orchestrator_lifespan_seals_shutdown_block():
    """A clean TestClient exit must append a SHUTDOWN block to the chain.

    Pre-fix, the FastAPI lifespan shutdown branch was a no-op, so
    uvicorn stopping cleanly (or TestClient's context manager
    exiting) left the chain without a final SHUTDOWN block. The fix
    calls Orchestrator().shutdown() from the lifespan shutdown
    branch. The test counts SHUTDOWN blocks before and after a
    clean TestClient lifecycle and asserts the count grew by at
    least one.
    """
    # /api/ledger exposes blocks from the on-disk Merkle chain via
    # vault_io.merkle_all(). Each block dict uses ``event_type`` as
    # the key (set in vault_io.append_block), not ``event`` -- the
    # /api/ledger summary is a separate field. We sum on the right key.
    with TestClient(app) as c1:
        r_before = c1.get("/api/ledger")
        assert r_before.status_code == 200
        before_blocks = r_before.json()["blocks"]
        before_shutdowns = sum(
            1 for b in before_blocks if b.get("event_type") == "SHUTDOWN"
        )

    # New TestClient context -- c1's lifespan shutdown sealed exactly
    # one SHUTDOWN block on exit. c2's exit will seal another, but we
    # assert the count grew by at least one, which is the property
    # that the fix is supposed to guarantee.
    with TestClient(app) as c2:
        r_after = c2.get("/api/ledger")
        assert r_after.status_code == 200
        after_blocks = r_after.json()["blocks"]
        after_shutdowns = sum(
            1 for b in after_blocks if b.get("event_type") == "SHUTDOWN"
        )

    assert after_shutdowns >= before_shutdowns + 1, (
        f"lifespan shutdown did not seal a SHUTDOWN block: "
        f"before={before_shutdowns}, after={after_shutdowns}"
    )
