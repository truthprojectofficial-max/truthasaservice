"""
Order Get It Right -- Affidavit preview / dry-run test.

Companion to tests/test_orchestrator_seam.py. Closes the Tier-2
surface gap: /api/affidavit has both a write-on-POST path and a
preview-on-GET path. The preview must:
  1. Return the same markdown content as POST (compile is
     deterministic; both endpoints call the same generator method).
  2. Mark itself as a preview (wroteToDisk: false) so an operator
     reading the response can tell at a glance which path it went
     through.
  3. NOT include a ``path`` key pointing at an archive file --
     because the preview did not write one.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

from fastapi.testclient import TestClient  # noqa: E402

from src.server.app import app  # noqa: E402


def test_affidavit_preview_returns_deterministic_markdown():
    """GET /api/affidavit/preview must return valid, complete markdown.

    The preview endpoint is a dry-run for the POST /api/affidavit
    endpoint. It compiles the same affidavit the POST would write
    to disk, but returns it in the response body without touching
    the filesystem. The markdown must start with the standard
    affidavit header so an operator can confirm at a glance that
    the document is well-formed.
    """
    with TestClient(app) as c:
        r = c.get("/api/affidavit/preview")
        assert r.status_code == 200, f"preview endpoint failed: {r.text}"
        body = r.json()

        # The response must mark itself as a preview.
        assert body.get("preview") is True, (
            f"preview endpoint did not self-identify as a preview: {body.keys()}"
        )
        assert body.get("wroteToDisk") is False, (
            f"preview endpoint reports wroteToDisk=True: {body}"
        )

        # A preview must NOT return a 'path' pointing at an archive
        # file, because no archive was written. The POST endpoint
        # is the one that returns a path.
        assert "path" not in body or body.get("path") in (None, ""), (
            f"preview endpoint returned a 'path' key (it should not have written "
            f"anything to disk): {body.get('path')!r}"
        )

        # The affidavit markdown must be present and well-formed.
        md = body.get("affidavit", "")
        assert isinstance(md, str) and len(md) > 0, (
            f"preview returned empty or non-string affidavit: {type(md).__name__}"
        )
        assert "AFFIDAVIT OF DETERMINISTIC SYSTEM TRUTH" in md, (
            f"preview markdown missing standard header; first 200 chars: {md[:200]!r}"
        )
        # Section 177 reference must be present (jurisdictional claim).
        assert "Section 177" in md, "preview missing Section 177 reference"
        # The chain anchor must be present (the affidavit is a witness
        # of the Merkle root, so the document is meaningless without it).
        assert "SYSTEM IDENTIFIER" in md, "preview missing system identifier"


def test_affidavit_preview_matches_post_output():
    """The preview and the POST must return the same markdown.

    Both endpoints call the same compile_full_affidavit() method on
    the same generator; the only difference is the side effect of
    writing the result to disk. The markdown content must be the
    same modulo the per-call timestamp in the header -- which is a
    property of the runtime, not the compile. The chain, the
    blocks, the NIZK proofs, and the operator identity are all
    deterministic, so the bodies below the timestamp line must be
    byte-identical.
    """
    def _strip_header_timestamp(md: str) -> str:
        """Remove the DATE OF AFFIDAVIT line so two calls that landed
        a second apart can still be compared."""
        lines = md.splitlines()
        return "\n".join(
            line for line in lines if not line.startswith("DATE OF AFFIDAVIT:")
        )

    with TestClient(app) as c:
        # Preview first.
        r_preview = c.get("/api/affidavit/preview")
        assert r_preview.status_code == 200
        preview_body = r_preview.json()
        preview_md = preview_body["affidavit"]

        # Then the actual archive.
        r_post = c.post("/api/affidavit")
        assert r_post.status_code == 200
        post_body = r_post.json()
        post_md = post_body["affidavit"]

        # Strip the per-call timestamp from both bodies and compare.
        # Everything else (the chain, the blocks, the operator
        # identity, the system identifier, the protocol compliance
        # line) must be identical.
        assert _strip_header_timestamp(preview_md) == _strip_header_timestamp(post_md), (
            "preview and POST produced different affidavit content "
            "(excluding the per-call timestamp in the header)"
        )
        # POST must include a real path; preview must not.
        assert isinstance(post_body.get("path"), str) and len(post_body["path"]) > 0, (
            f"POST did not return a path: {post_body}"
        )


def test_affidavit_preview_does_not_mutate_chain():
    """Two preview calls must not change the on-disk Merkle chain.

    Preview is a read-only operation: it compiles the affidavit
    markdown from the existing chain and returns it without
    writing anywhere. The chain block count before and after
    must be identical. This is the test that catches a regression
    where someone wires the preview endpoint to also seal a
    block (it would be a real bug -- a dry-run must not write).
    """
    with TestClient(app) as c:
        # Read the chain length before the preview.
        r_before = c.get("/api/ledger")
        assert r_before.status_code == 200
        before_count = len(r_before.json()["blocks"])
        before_stats = r_before.json()["stats"]["ledger"]
        before_root = before_stats["merkleRoot"]

        # Hit the preview twice.
        r1 = c.get("/api/affidavit/preview")
        r2 = c.get("/api/affidavit/preview")
        assert r1.status_code == 200
        assert r2.status_code == 200

        # Read the chain length after. Must be unchanged.
        r_after = c.get("/api/ledger")
        assert r_after.status_code == 200
        after_count = len(r_after.json()["blocks"])
        after_stats = r_after.json()["stats"]["ledger"]
        after_root = after_stats["merkleRoot"]

        assert after_count == before_count, (
            f"preview mutated the chain: before={before_count}, after={after_count}"
        )
        assert after_root == before_root, (
            f"preview mutated the Merkle root: before={before_root}, after={after_root}"
        )
