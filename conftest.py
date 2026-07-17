"""
Order Get It Right -- pytest configuration

This conftest exists at the project root so that pytest (run from any
directory) finds the tests/ folder and the 02_Technical/ source tree
without the operator having to think about paths.

The single rule this file encodes: tests/ may reach into the FastAPI app
object via the HTTP test client. That is the one and only legitimate
src.* import the test suite makes. The boundary test
tests/test_00_99_boundary.py whitelists this exact import.

No other fixtures, hooks, or configuration live here. The build must
not grow this file beyond what is needed to make pytest discover the
tests and nothing else.
"""
import sys
from pathlib import Path

# Make 02_Technical importable so tests/ can mount the FastAPI app
# for the HTTP boundary tests. The boundary test enforces that this
# is the only src.* import any test file makes.
_TECHNICAL = Path(__file__).resolve().parent / "02_Technical"
if str(_TECHNICAL) not in sys.path:
    sys.path.insert(0, str(_TECHNICAL))
