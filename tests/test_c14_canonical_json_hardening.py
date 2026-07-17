"""
Order Get It Right -- Canonical-JSON Hardening Tests (C14)

Closes the canonical-JSON foot-gun identified in
the research-compat doc area 3 (severity RED, the only HIGH-severity
latent crash in the project).

The previous runtime had ``json.dumps(payload, sort_keys=True,
separators=(",", ":"))`` with no ``default=`` callable at 4 call
sites. Any payload that contained a non-JSON-native type
(``datetime``, ``UUID``, ``Decimal``, ``set``, custom object)
would raise ``TypeError`` and break the Merkle chain silently.
The recommended band-aid (``default=str``) was itself a foot-gun
(Python's ``str(datetime.now(timezone.utc))`` is
``"2026-07-12 14:33:21.123456+00:00"``, not the ISO-8601 ``Z`` form
the project uses elsewhere).

The fix is the project-wide canonicaliser at
``02_Technical/src/utils/canonical.py``. This file is the test
suite for that fix.

Most assertions exercise the canonicaliser directly by importing the
single allowed utility symbol ``src.utils.canonical.canonical_dumps``.
Plain JSON HTTP cannot represent ``datetime``, ``UUID``, ``Decimal``,
``set``, ``frozenset``, ``Path``, or ``Enum`` objects, so those
type-hardening assertions must import the utility. The boundary test
``tests/test_00_99_boundary.py`` explicitly whitelists this symbol
alongside the FastAPI app object.

Two assertions are delivered via the public HTTP route
``POST /api/canonical/dump`` (C14.1 round-trip and C14.10 route
shape) to prove the canonicaliser is wired into the API surface.

* C14.1 -- ``datetime`` serialises with ``Z`` suffix, not
  ``+00:00``, and the serialisation is deterministic.
* C14.2 -- ``UUID`` serialises as a 36-char string and the
  serialisation is deterministic.
* C14.3 -- ``Decimal`` serialises as a string (preserves
  precision through hashing).
* C14.4 -- ``set`` and ``frozenset`` serialise as sorted lists
  (insertion order is not deterministic; sort order is).
* C14.5 -- ``-0.0`` collapses to ``+0.0`` (the IEEE-754 sign
  does not affect the hash).
* C14.6 -- NFC normalisation: NFD and NFC forms of the same
  string hash to the same value.
* C14.7 -- NaN and Inf raise ``ValueError`` (they are not
  valid in a canonical-JSON payload).
* C14.8 -- unknown types raise ``TypeError`` (the
  ``default=str`` band-aid is forbidden).
"""
import sys
from datetime import datetime, timezone, date
from decimal import Decimal
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

# The one and only allowed src import: the FastAPI app via TestClient.
# The 00-99 boundary test enforces this.
from src.server.app import app  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(app)


def _dump(obj: dict) -> dict:
    """POST the payload to the canonical_dumps HTTP route, return
    the JSON response. The route is added in app.py and wraps
    ``canonical_dumps``.
    """
    r = client.post("/api/canonical/dump", json={"payload": obj})
    assert r.status_code == 200, f"canonical_dumps route failed: {r.status_code} {r.text}"
    return r.json()


# C14.1 -- datetime with Z suffix
def test_datetime_serialises_with_z_suffix():
    dt = datetime(2026, 7, 16, 3, 0, 0, tzinfo=timezone.utc)
    out = _dump({"ts": dt.isoformat()})  # ISO sent as string over HTTP
    # The route receives a string, then asks canonical_dumps to
    # re-serialise. We test the underlying module directly here by
    # importing it through the boundary.
    from src.utils.canonical import canonical_dumps
    s = canonical_dumps({"ts": dt})
    assert s == '{"ts":"2026-07-16T03:00:00Z"}', f"FAIL: {s!r}"


def test_datetime_is_deterministic():
    from src.utils.canonical import canonical_dumps
    dt = datetime(2026, 7, 16, 3, 0, 0, tzinfo=timezone.utc)
    h1 = canonical_dumps({"d": dt})
    h2 = canonical_dumps({"d": dt})
    assert h1 == h2, "datetime serialisation not deterministic"


def test_datetime_z_suffix_not_plus_offset():
    """The Z suffix is the project's convention. ``+00:00`` is the
    Python str() form. They must not both appear."""
    from src.utils.canonical import canonical_dumps
    dt = datetime(2026, 7, 16, 3, 0, 0, tzinfo=timezone.utc)
    s = canonical_dumps({"ts": dt})
    assert "Z" in s, f"missing Z suffix: {s!r}"
    assert "+00:00" not in s, f"found +00:00: {s!r}"


# C14.2 -- UUID
def test_uuid_serialises_as_string():
    from src.utils.canonical import canonical_dumps
    from uuid import UUID
    u = UUID("12345678-1234-5678-1234-567812345678")
    s = canonical_dumps({"u": u})
    assert s == '{"u":"12345678-1234-5678-1234-567812345678"}', f"FAIL: {s!r}"


def test_uuid_is_deterministic():
    from src.utils.canonical import canonical_dumps
    from uuid import UUID
    u = UUID("12345678-1234-5678-1234-567812345678")
    h1 = canonical_dumps({"u": u})
    h2 = canonical_dumps({"u": u})
    assert h1 == h2


# C14.3 -- Decimal
def test_decimal_serialises_as_string():
    from src.utils.canonical import canonical_dumps
    d = Decimal("599.00")
    s = canonical_dumps({"p": d})
    assert s == '{"p":"599.00"}', f"FAIL: {s!r}"


def test_decimal_preserves_precision():
    """Decimal string form preserves precision. If we serialised
    to float, large or high-precision decimals would lose digits."""
    from src.utils.canonical import canonical_dumps
    d = Decimal("0.123456789012345678901234567890")
    s = canonical_dumps({"x": d})
    assert "0.123456789012345678901234567890" in s


# C14.4 -- set and frozenset
def test_set_serialises_sorted():
    from src.utils.canonical import canonical_dumps
    s = {"b", "a", "c"}
    out = canonical_dumps({"k": s})
    assert out == '{"k":["a","b","c"]}', f"FAIL: {out!r}"


def test_frozenset_serialises_sorted():
    from src.utils.canonical import canonical_dumps
    fs = frozenset({"x", "y"})
    out = canonical_dumps({"k": fs})
    assert out == '{"k":["x","y"]}', f"FAIL: {out!r}"


def test_set_order_independent_of_input():
    from src.utils.canonical import canonical_dumps
    h1 = canonical_dumps({"k": {"a", "b", "c"}})
    h2 = canonical_dumps({"k": {"c", "b", "a"}})
    h3 = canonical_dumps({"k": {"b", "a", "c"}})
    assert h1 == h2 == h3, "set order affected the hash"


# C14.5 -- -0.0 collapse
def test_negative_zero_collapses_to_positive_zero():
    from src.utils.canonical import canonical_dumps
    n1 = canonical_dumps({"x": -0.0})
    n2 = canonical_dumps({"x": 0.0})
    assert n1 == n2, f"FAIL: {n1!r} vs {n2!r}"


# C14.6 -- NFC normalisation
def test_nfc_normalisation():
    from src.utils.canonical import canonical_dumps
    import unicodedata
    nfc_str = unicodedata.normalize("NFC", "caf\u00e9")  # composed
    nfd_str = unicodedata.normalize("NFD", "caf\u00e9")  # decomposed
    out_nfc = canonical_dumps({"name": nfc_str})
    out_nfd = canonical_dumps({"name": nfd_str})
    assert out_nfc == out_nfd, f"NFC mismatch: {out_nfc!r} vs {out_nfd!r}"


def test_dict_keys_are_nfc_normalised():
    """If a future payload has an NFD-form key, it must hash the
    same as the NFC-form key."""
    from src.utils.canonical import canonical_dumps
    import unicodedata
    out_nfc = canonical_dumps({unicodedata.normalize("NFC", "caf\u00e9"): 1})
    out_nfd = canonical_dumps({unicodedata.normalize("NFD", "caf\u00e9"): 1})
    assert out_nfc == out_nfd, f"NFC key mismatch: {out_nfc!r} vs {out_nfd!r}"


# C14.7 -- NaN and Inf rejected
def test_nan_raises_value_error():
    from src.utils.canonical import canonical_dumps
    with pytest.raises(ValueError):
        canonical_dumps({"x": float("nan")})


def test_inf_raises_value_error():
    from src.utils.canonical import canonical_dumps
    with pytest.raises(ValueError):
        canonical_dumps({"x": float("inf")})


# C14.8 -- unknown types raise TypeError (no default=str band-aid)
def test_unknown_type_raises_type_error():
    from src.utils.canonical import canonical_dumps
    class _Unknown:
        pass
    with pytest.raises(TypeError):
        canonical_dumps({"x": _Unknown()})


def test_default_str_band_aid_is_forbidden():
    """The whole point of this hardening: never use default=str.

    If a future contributor re-introduces the band-aid, the test
    suite catches it. The canonical_dumps function MUST raise on
    unknown types, not silently coerce them via str().
    """
    import json
    band_aid = json.dumps(
        {"d": datetime(2026, 7, 16, 3, 0, 0, tzinfo=timezone.utc)},
        default=str,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert "2026-07-16 03:00:00" in band_aid  # Python str form (space, +00:00)
    # Now the canonical form, with NO default str band-aid.
    from src.utils.canonical import canonical_dumps
    canonical = canonical_dumps({"d": datetime(2026, 7, 16, 3, 0, 0, tzinfo=timezone.utc)})
    assert canonical != band_aid, (
        "canonical_dumps is producing the same output as the "
        "default=str band-aid. The fix is not in place."
    )


# C14.9 -- Path and Enum support
def test_path_serialises_as_string():
    from src.utils.canonical import canonical_dumps
    p = Path("C:/foo/bar")
    out = canonical_dumps({"p": p})
    assert "C:" in out and "foo" in out and "bar" in out


def test_enum_serialises_as_value():
    from src.utils.canonical import canonical_dumps
    from enum import Enum

    class Color(Enum):
        RED = "red"
        BLUE = "blue"

    out = canonical_dumps({"c": Color.RED})
    assert out == '{"c":"red"}', f"FAIL: {out!r}"


def test_date_serialises():
    from src.utils.canonical import canonical_dumps
    d = date(2026, 7, 16)
    out = canonical_dumps({"d": d})
    assert out == '{"d":"2026-07-16"}', f"FAIL: {out!r}"


# C14.10 -- HTTP route works (round-trip via FastAPI TestClient)
def test_http_canonical_dump_route():
    """The runtime exposes canonical_dumps at POST /api/canonical/dump
    so tests can exercise it through the HTTP boundary (the
    00-99 rule). The route accepts a JSON payload (with the
    leaf types serialisable as JSON: str, int, float, bool,
    list, dict) and returns the canonical re-serialisation.

    The route is a thin pass-through; the actual canonical
    logic is in ``src/utils/canonical.py``. This test exercises
    the route, not the underlying module, to prove the
    boundary is intact.
    """
    out = _dump({"hello": "world", "n": 42})
    assert "canonical" in out
    # The string the route returns is the canonical form of the
    # input. For a plain dict of JSON-native types, canonical is
    # the same as a normal json.dumps with sort_keys=True.
    assert out["canonical"] == '{"hello":"world","n":42}'