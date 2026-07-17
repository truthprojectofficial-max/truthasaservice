"""
Order Get It Right -- Canonical-JSON Helpers

The runtime serialises every fact, every payload, and every audit-block
body with ``json.dumps(..., sort_keys=True, separators=(",", ":"))``.
The default ``json.dumps`` raises ``TypeError`` on any non-JSON-native
type: ``datetime``, ``UUID``, ``Decimal``, ``Enum``, ``Path``, ``set``,
``frozenset``, ``datetime.time``, ``datetime.date``.

Earlier sessions used the band-aid ``default=str``. That is itself a
foot-gun: Python's ``str(datetime.now(timezone.utc))`` returns
``"2026-07-12 14:33:21.123456+00:00"`` (space separator, no ``Z``
suffix). The rest of the project uses the ISO-8601 ``Z`` form. A
REPL-built payload that contained a ``datetime`` would hash
differently from a vault-built payload, breaking the Merkle root.

The fix is the project-wide canonicaliser below: one callable,
``canonical_dumps(obj)``, used by every ``json.dumps`` call in
``vault_io.py`` and ``verify_chain.py``. The callable handles every
type the runtime may ever encounter, raises ``TypeError`` on
anything else, and never silently corrupts a hash.

Two additional concerns the canonicaliser handles:

* **NFC normalisation** -- every string value and every key is
  passed through ``unicodedata.normalize("NFC", s)``. Without this,
  a payload that contains ``"cafe\u0301"`` (NFD) would hash
  differently from the same payload written as ``"caf\u00e9"`` (NFC).
  Realistic on macOS HFS+, iOS ``String`` bridging, and many web
  sources. See https://tools.ietf.org/html/rfc8785#section-3.1.

* **``-0.0`` collapse** -- IEEE-754 distinguishes ``+0.0`` from
  ``-0.0``. Two systems doing the same arithmetic can hit different
  signs of zero on different platforms. The canonicaliser collapses
  ``-0.0`` to ``+0.0`` so the hash is stable across hosts.

* **NaN / Inf rejection** -- ``json.dumps`` emits these as bare
  tokens (non-standard JSON). We set ``allow_nan=False`` so the
  runtime raises ``ValueError`` (Python 3.14) on a payload that
  contains them. The honest error is better than a silent hash
  corruption.

The recipe is in ``the validation directory/RESEARCH_COMPATIBILITY_2026-07-12.md``
area 3 (severity RED, the only HIGH-severity latent crash in the
project). This module is the project's instruction manual realised
in code.

This module lives at ``02_Technical/src/utils/canonical.py`` and is
imported by ``vault_io.py`` and ``verify_chain.py``. It is runtime
code; it must not import from ``the vault directory`` or ``the validation directory``
(the 00-99 boundary test enforces this).
"""
from __future__ import annotations

import json
import math
import unicodedata
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID


def _normalise(obj: Any) -> Any:
    """Recursively walk ``obj`` and return a JSON-stable representation.

    * Dict keys are sorted and NFC-normalised.
    * String values are NFC-normalised.
    * ``set`` and ``frozenset`` are sorted into lists (insertion
      order is not deterministic; sort order is).
    * ``-0.0`` is collapsed to ``+0.0``.

    This walker is the project-wide fix for the canonical-JSON
    foot-gun identified in
    ``the validation directory/RESEARCH_COMPATIBILITY_2026-07-12.md`` area 3.
    """
    if isinstance(obj, dict):
        out: dict = {}
        for k, v in obj.items():
            nk = unicodedata.normalize("NFC", k) if isinstance(k, str) else k
            out[nk] = _normalise(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [_normalise(v) for v in obj]
    if isinstance(obj, (set, frozenset)):
        members = sorted(obj, key=lambda m: _sort_key(m))
        return [_normalise(m) for m in members]
    if isinstance(obj, float):
        if obj == 0.0:
            return 0.0
        return obj
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    return obj


def _json_default(obj: Any) -> Any:
    """The ``default=`` callable for ``json.dumps``.

    Raised by ``json.dumps`` for any type the runtime has not been
    taught to serialise. The intentional failure mode is the
    opposite of the ``default=str`` band-aid: explicit failure,
    not silent corruption. If a future contributor adds a new
    type to a payload, they must extend this callable and the
    test in ``tests/test_c14_canonical_json_hardening.py``.
    """
    if isinstance(obj, datetime):
        s = obj.isoformat()
        if s.endswith("+00:00"):
            s = s[:-6] + "Z"
        return s
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(
        f"Object of type {type(obj).__name__} is not JSON-serialisable "
        f"by Order Get It Right's canonicaliser. Add a handler to "
        f"src.utils.canonical._json_default and a test to "
        f"tests/test_c14_canonical_json_hardening.py."
    )


def _sort_key(obj: Any) -> str:
    """String form of ``obj`` for use as a sort key in
    ``_normalise``. Uses the canonical-JSON form so two sets with
    the same members in different orders hash the same.
    """
    return json.dumps(
        _normalise(obj),
        default=_json_default,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_dumps(obj: Any) -> str:
    """The one entry point for every ``json.dumps`` call in the runtime.

    Walks ``obj`` through ``_normalise`` (NFC keys, NFC values,
    set sort, -0.0 collapse), then serialises with the strict
    ``default=`` callable and ``allow_nan=False``. The result is
    byte-identical on any host, on any Python version, for any
    of the leaf types the project uses. NaN and Inf raise
    ``ValueError`` rather than being emitted as non-standard bare
    tokens.

    If you find yourself writing ``json.dumps`` anywhere in
    ``02_Technical/src/``, import this function instead. The
    00-99 boundary test does not currently enforce this, but the
    code-review discipline is: if the file you are editing is
    inside ``02_Technical/src/`` and you reach for ``json.dumps``,
    you should be using ``canonical_dumps``.
    """
    return json.dumps(
        _normalise(obj),
        default=_json_default,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
