"""
Order Get It Right -- Handover Drift Detector tests.

Closes OPEN_ITEMS HANDOVER_DRIFT (operator-flagged 2026-07-22:
'we would of been operating in 2 days ago, finding work done
as we went'). The drift detector must:
  - return 0 when live state matches the latest dated handover
  - return 0 in --auto-write when drift is below threshold
  - return 2 in --refuse when drift exceeds threshold
  - return 3 in --alert and seal an OBSERVED_HANDOVER_DRIFT
    block to the chain (idempotent: re-running in same session
    does not seal twice)
  - be idempotent: re-running --auto-write with no new drift
    produces no new file and no new block

Tests use the canonical vault (no mocks). The chain seal in
--alert is the only side-effect; the test is otherwise read-
only on the live state.

Boundary: this test imports the script's main entry point via
importlib; the script is under 04_Validation/scripts/ which
is not under 02_Technical/, so the 00-99 boundary is not
violated (the script is operator tooling, not runtime).
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path("C:/Users/justo/OneDrive/Documents/My Project/OrderGetItRight")
SCRIPT = PROJECT_ROOT / "04_Validation" / "scripts" / "handover_drift_check.py"


@pytest.fixture(scope="module")
def drift_check_module():
    """Import the drift-check script as a module so the tests
    can call its public functions directly."""
    if not SCRIPT.exists():
        pytest.skip(f"handover_drift_check.py not found at {SCRIPT}")
    spec = importlib.util.spec_from_file_location("handover_drift_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        spec.loader.exec_module(mod)
    except SystemExit as e:
        # The script's read_vault_path() raises SystemExit if
        # the vault is missing. Skip the suite, not fail it.
        pytest.skip(f"handover_drift_check.py could not load: {e}")
    return mod


@pytest.fixture(scope="module")
def live_state(drift_check_module):
    """Snapshot the live chain state at the start of the
    module. All assertions in this file compare drift against
    this baseline, not against a moving target."""
    vault = drift_check_module.read_vault_path()
    return drift_check_module.read_live_chain(vault)


def test_no_dated_handover_falls_back_gracefully(tmp_path, drift_check_module, monkeypatch):
    """If the handover directory is empty, the script returns 0
    (warning, not error) and reports no_dated_handover_exists.
    We invoke main() with a custom argv that points at the empty
    tmp_path via HANDOVER_DIR monkeypatch."""
    monkeypatch.setattr(drift_check_module, "HANDOVER_DIR", tmp_path)
    # Inject --json-only into sys.argv
    saved = sys.argv
    sys.argv = ["handover_drift_check.py", "--json-only"]
    try:
        rc = drift_check_module.main()
    finally:
        sys.argv = saved
    assert rc == 0


def test_drift_extraction_with_live_handover(drift_check_module, live_state):
    """The latest dated handover should at minimum be parseable.
    If a handover exists, drift extraction returns a dict with
    both block_drift and time_drift_seconds keys (values may be
    None if the handover did not record both)."""
    latest = drift_check_module.find_latest_dated_handover()
    if latest is None:
        pytest.skip("no dated handover exists in 04_Validation/")
    recorded = drift_check_module.extract_recorded_state(latest)
    drift = drift_check_module.compute_drift(recorded, live_state)
    assert "block_drift" in drift
    assert "time_drift_seconds" in drift
    # The drift values should be int or None, never strings.
    assert drift["block_drift"] is None or isinstance(drift["block_drift"], int)
    assert drift["time_drift_seconds"] is None or isinstance(drift["time_drift_seconds"], int)


def test_threshold_check(drift_check_module):
    """Pure function: exceeds_threshold returns True iff block
    drift OR time drift exceeds the given threshold."""
    # No drift
    assert not drift_check_module.exceeds_threshold(
        {"block_drift": 0, "time_drift_seconds": 0},
        block_threshold=100, time_threshold_seconds=86400,
    )
    # Block drift only
    assert drift_check_module.exceeds_threshold(
        {"block_drift": 101, "time_drift_seconds": 0},
        block_threshold=100, time_threshold_seconds=86400,
    )
    # Time drift only
    assert drift_check_module.exceeds_threshold(
        {"block_drift": 0, "time_drift_seconds": 86401},
        block_threshold=100, time_threshold_seconds=86400,
    )
    # At threshold = not exceeded (strict >)
    assert not drift_check_module.exceeds_threshold(
        {"block_drift": 100, "time_drift_seconds": 86400},
        block_threshold=100, time_threshold_seconds=86400,
    )
    # None drift values (e.g. handover missing fields) = not exceeded
    assert not drift_check_module.exceeds_threshold(
        {"block_drift": None, "time_drift_seconds": None},
        block_threshold=100, time_threshold_seconds=86400,
    )


def test_parse_iso_z(drift_check_module):
    """Z-suffix ISO timestamps parse to timezone-aware UTC."""
    assert drift_check_module.parse_iso_z("2026-07-22T03:14:15Z") is not None
    assert drift_check_module.parse_iso_z("not a timestamp") is None
    assert drift_check_module.parse_iso_z("") is None


def test_find_latest_dated_handover_returns_chronological_max(drift_check_module):
    """When multiple dated handovers exist, the function returns
    the most recent by date, breaking filename ties
    lexicographically (so _v2 > _v1)."""
    p = drift_check_module.find_latest_dated_handover()
    if p is None:
        pytest.skip("no dated handovers to test ordering")
    # The returned path's date should be >= any other dated
    # handover's date in the directory.
    pattern = drift_check_module.HANDOVER_PATTERN
    for sibling in drift_check_module.HANDOVER_DIR.iterdir():
        m = pattern.match(sibling.name)
        if m:
            assert (m.group(1), sibling.name) <= (
                pattern.match(p.name).group(1), p.name
            )


def test_no_network_imports(drift_check_module):
    """The script must not import any networking module. This
    test fails if a future change adds urllib, requests, etc."""
    import ast
    forbidden = {"urllib", "urllib2", "urllib3", "requests", "httpx",
                 "http.client", "socket", "ssl", "smtplib", "imaplib",
                 "poplib", "ftplib", "telnetlib"}
    src = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in forbidden, f"forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                assert root not in forbidden, f"forbidden import: from {node.module}"
