"""
Regression tests for static-dir serving in src/server/app.py.

Background: STATIC_DIR was originally computed as
    Path(__file__).parent.parent / "web"
which resolves to 02_Technical/src/web/ -- a directory that does not
exist (the real web folder is 02_Technical/web/). The off-by-one
silently broke browser-mode UI serving: GET / fell through to the
JSON fallback {"status": ...}, and /static was never mounted. The
Tauri shell still worked because it serves the web directory
directly from disk via its own frontendDist config.

These tests pin the observable, HTTP-level behaviour -- the served
HTML at / and /static/index.html -- without importing the internal
STATIC_DIR symbol (which the 00-99 boundary test does not whitelist).
The invariant is: whatever path the runtime uses, it must land on
the 02_Technical/web/ folder. The TestClient gives us the same
end-to-end check a real browser would see.

Sealed: UI_OPERATOR_FACING_REDESIGN_2026_07_17
"""
from pathlib import Path

from fastapi.testclient import TestClient

# Only the FastAPI app object is allowed by the 00-99 boundary test.
# The path constants live behind the HTTP surface and are tested
# through the served bytes, not through introspection.
from src.server.app import app  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = PROJECT_ROOT / "02_Technical" / "web"
INDEX_FILE = WEB_DIR / "index.html"


def test_web_folder_is_in_the_expected_place():
    """Sanity check the on-disk layout. If this ever fires, the
    layout has shifted and the HTTP-level tests below need a
    matching path update."""
    assert WEB_DIR.exists(), f"web folder missing: {WEB_DIR}"
    assert INDEX_FILE.exists(), f"index.html missing: {INDEX_FILE}"


def test_root_serves_index_html():
    """GET / must return text/html containing the <title>, not the
    JSON fallback that the operator used to see when STATIC_DIR was
    wrong (then 02_Technical/src/web/ did not exist and the
    `if index.exists()` guard in app.py returned False)."""
    with TestClient(app) as client:
        r = client.get("/")
    assert r.status_code == 200, f"GET / returned {r.status_code}"
    ct = r.headers.get("content-type", "")
    assert "text/html" in ct, f"GET / content-type was {ct!r}, expected text/html"
    body = r.text
    assert "<title>" in body, "GET / body has no <title> -- looks like the JSON fallback"
    assert "Order Get It Right" in body, "GET / body missing the project name"


def test_static_mount_serves_index_html():
    """GET /static/index.html must also resolve and serve the file.
    This exercises the StaticFiles mount, which only fires when
    STATIC_DIR.exists() is True at import time -- the silent failure
    mode of the old path bug."""
    with TestClient(app) as client:
        r = client.get("/static/index.html")
    assert r.status_code == 200, f"GET /static/index.html returned {r.status_code}"
    assert "<title>" in r.text


def test_served_html_matches_disk_file():
    """The HTML served by GET / must be byte-identical to the file
    on disk. This catches a future regression where the wrong folder
    is mounted (e.g. a stale or partial copy) and still returns 200
    with HTML, but the wrong bytes."""
    with TestClient(app) as client:
        r = client.get("/")
    on_disk = INDEX_FILE.read_bytes().decode("utf-8")
    assert r.text == on_disk, "GET / body differs from 02_Technical/web/index.html on disk"
