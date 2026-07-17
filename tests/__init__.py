"""Tests package.

The 00-99 boundary test allows the FastAPI app to be imported into
tests for TestClient mounting only.  It does not allow any other
import from src/.

No `src.*` import is permitted in this file or anywhere else under
tests/.  The HTTP API is the only public surface tests may touch.
"""
