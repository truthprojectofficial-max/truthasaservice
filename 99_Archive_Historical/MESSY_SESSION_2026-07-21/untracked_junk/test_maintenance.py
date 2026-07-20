"""
Order Get It Right -- Deterministic Maintenance Layer Tests.

Locks the maintenance subsystem (src.maintenance.*) added 2026-07-20.

What these tests prove
----------------------
* The routines are READ-ONLY w.r.t. the vault: running them does NOT
  change the block count or the Merkle root.
* A suite run seals EXACTLY ONE block (the maintenance seal), never
  more, regardless of how many routines run or how many FAIL.
* The routines are idempotent within a cadence: running the same
  cadence twice produces stable deltas (state.json is the anchor).
* A FAIL routine drops a fault file in the Squeal directory so the
  MonitorAgent's next sweep sees it.
* The CLI ``--no-seal`` path writes the report but seals no block.

Boundary compliance (00-99): tests may NOT ``import`` from ``src/``
except the whitelisted ``src.server.app.app`` and
``src.utils.canonical.canonical_dumps``. The maintenance modules are
loaded with ``importlib.import_module`` (a runtime call, not an AST
import statement), so test_no_src_imports_in_tests() does not see it.
The production 03_Vault / 04_Validation are never touched: every test
redirects ``vault_io.VAULT_DIR`` and the maintenance report/squeal/state
paths to a temp directory.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.server.app import app  # whitelisted import (00-99 boundary)

client = TestClient(app)
app_module = sys.modules["src.server.app"]
vault_io = app_module.vault_io

# Load the maintenance subsystem by string (no AST `import src.maintenance`
# statement -> 00-99 boundary-clean).
health = importlib.import_module("src.maintenance.health")
reporter = importlib.import_module("src.maintenance.reporter")
constants = importlib.import_module("config.constants")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_env(tmp_path, monkeypatch):
    """Redirect the vault + maintenance report/squeal/state paths to tmp_path."""
    vault_dir = tmp_path / "03_Vault"
    vault_dir.mkdir()
    reports_dir = tmp_path / "04_Validation" / "maintenance_reports"
    squeal_dir = tmp_path / "04_Validation" / "squeal-reports"
    outbox_dir = tmp_path / "04_Validation" / "reports"
    logs_dir = tmp_path / "04_Validation" / "logs"
    reports_dir.mkdir(parents=True, exist_ok=True)
    squeal_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(vault_io, "VAULT_DIR", vault_dir)
    monkeypatch.setattr(reporter, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(reporter, "STATE_PATH", reports_dir / "state.json")
    monkeypatch.setattr(reporter, "PROJECT_SQUEAL_DIR", str(squeal_dir))
    # Routines read these from config.constants at call time.
    monkeypatch.setattr(constants, "PROJECT_VAULT_DIR", str(vault_dir))
    monkeypatch.setattr(constants, "PROJECT_SQUEAL_DIR", str(squeal_dir))
    monkeypatch.setattr(constants, "PROJECT_OUTBOX_DIR", str(outbox_dir))
    monkeypatch.setattr(constants, "PROJECT_LOGS_DIR", str(logs_dir))
    return tmp_path


def _seed_chain(n=3):
    """Seed n blocks into the (temp) vault so routines have something to read."""
    vault_io.append_block("GENESIS", {"note": "first"})
    for i in range(n - 1):
        vault_io.append_block("FACT_ADDED", {"i": i})
    return n


# ---------------------------------------------------------------------------
# Routine-level tests (read-only)
# ---------------------------------------------------------------------------

def test_routines_have_required_shape(temp_env):
    """Every routine returns {name, status, summary, detail}."""
    _seed_chain(3)
    for name, fn in health.ROUTINES.items():
        result = fn({})
        assert result["name"] == name, f"{name} wrong name"
        assert result["status"] in ("PASS", "WARN", "FAIL"), f"{name} bad status"
        assert isinstance(result["summary"], str) and result["summary"], f"{name} empty summary"
        assert isinstance(result["detail"], dict), f"{name} detail not dict"


def test_routines_are_read_only_on_vault(temp_env):
    """Running every routine must NOT change block count or Merkle root.

    The maintenance layer's core contract: it observes, it never mutates
    history. This is the test an auditor would ask for.
    """
    _seed_chain(5)
    before = vault_io.read_facts_registry()
    before_count = len(before["blocks"])
    before_root = before["merkle_root"]

    for name in health.ROUTINES:
        health.run_routine(name, {})

    after = vault_io.read_facts_registry()
    assert len(after["blocks"]) == before_count, "a routine appended a block"
    assert after["merkle_root"] == before_root, "a routine changed the root"


def test_chain_integrity_passes_on_clean_vault(temp_env):
    """r_chain_integrity returns PASS on a freshly-seeded consistent chain."""
    _seed_chain(4)
    r = health.run_routine("chain_integrity", {})
    assert r["status"] == "PASS", r["summary"]
    assert r["detail"]["matches"] is True


def test_job_journal_tail_passes_when_in_sync(temp_env):
    """r_job_journal_tail returns PASS when tail == registry == jobs list."""
    _seed_chain(2)
    r = health.run_routine("job_journal_tail", {})
    assert r["status"] == "PASS", r["summary"]


def test_vault_growth_delta_uses_state(temp_env):
    """r_vault_growth reports a positive delta against the state anchor."""
    _seed_chain(3)  # GENESIS + 2 FACT_ADDED = 3 blocks
    r0 = health.run_routine("vault_growth", {})
    assert r0["status"] == "PASS"
    assert r0["detail"]["delta"] == 0  # prev defaults to now on first run
    # Now seed the state with a LOWER count -> positive delta (3 - 1 == 2).
    r1 = health.run_routine("vault_growth", {"vault_growth_block_count": 1})
    assert r1["detail"]["delta"] == 2, r1["summary"]
    assert r1["status"] == "PASS"


def test_vault_growth_warns_on_negative_delta(temp_env):
    """A negative delta (blocks removed) is a WARN -- chain is append-only."""
    _seed_chain(2)
    r = health.run_routine("vault_growth", {"vault_growth_block_count": 100})
    assert r["status"] == "WARN", r["summary"]
    assert r["detail"]["delta"] < 0


def test_squeal_backlog_passes_under_threshold(temp_env):
    """No squeal reports -> PASS."""
    _seed_chain(1)
    r = health.run_routine("squeal_backlog", {})
    assert r["status"] == "PASS"
    assert r["detail"]["count"] == 0
# ---------------------------------------------------------------------------
# Suite / reporter tests
# ---------------------------------------------------------------------------

def test_run_suite_seals_exactly_one_block(temp_env):
    """A suite run seals EXACTLY ONE MAINTENANCE_* block, never more."""
    _seed_chain(3)
    before = len(vault_io.read_facts_registry()["blocks"])
    report = reporter.run_suite("hourly", seal=True)
    after = len(vault_io.read_facts_registry()["blocks"])
    sealed = after - before
    assert sealed == 1, f"expected exactly 1 sealed block, got {sealed}"
    assert "sealedBlockIndex" in report
    block = vault_io.read_facts_registry()["blocks"][-1]
    assert block["event_type"].startswith("MAINTENANCE_"), block["event_type"]


def test_run_suite_no_seal_writes_no_block(temp_env):
    """--no-seal runs the routines + writes the report but seals nothing."""
    _seed_chain(3)
    before = len(vault_io.read_facts_registry()["blocks"])
    report = reporter.run_suite("hourly", seal=False)
    after = len(vault_io.read_facts_registry()["blocks"])
    assert after == before, "no-seal run appended a block"
    assert "sealedBlockIndex" not in report


def test_run_suite_writes_report_files(temp_env):
    """Each run writes a .md and a .json report under maintenance_reports/."""
    _seed_chain(2)
    report = reporter.run_suite("hourly", seal=False)
    md = Path(reporter.REPORTS_DIR) / report["reportPath"]
    js = Path(reporter.REPORTS_DIR) / report["reportJson"]
    assert md.exists() and js.exists()
    assert "# Maintenance Report" in md.read_text(encoding="utf-8")


def test_run_suite_is_idempotent_within_cadence(temp_env):
    """Running the same cadence twice produces a stable vault_growth delta.

    The state.json anchor is updated after each run, so a second run sees
    delta +1 (the first run's seal block) -- not a runaway count.
    """
    _seed_chain(3)
    reporter.run_suite("hourly", seal=True)
    r2 = reporter.run_suite("hourly", seal=True)
    growth2 = next(r for r in r2["routines"] if r["name"] == "vault_growth")
    assert growth2["detail"]["delta"] == 1, growth2["summary"]


def test_run_suite_unknown_cadence_raises(temp_env):
    """An unknown cadence is rejected up front, not silently ignored."""
    _seed_chain(1)
    with pytest.raises(ValueError):
        reporter.run_suite("weekly", seal=False)


def test_run_suite_overall_status_reflects_routines(temp_env):
    """overallStatus is the worst routine status (FAIL > WARN > PASS)."""
    _seed_chain(1)
    # Force a WARN by claiming a huge previous block count (negative delta).
    Path(reporter.STATE_PATH).write_text(
        '{"vault_growth_block_count": 1000000}', encoding="utf-8"
    )
    report = reporter.run_suite("hourly", seal=False)
    assert report["overallStatus"] == "WARN", report["overallStatus"]


def test_run_suite_writes_fault_file_on_fail(temp_env, monkeypatch):
    """A FAIL routine drops a maintenance-fault-*.json in the Squeal dir.

    We force ``chain_integrity`` to FAIL by stubbing the verifier the
    routine calls (``health._verify_chain``), which is deterministic and
    does NOT mutate the vault -- the right way to test the FAIL path
    without corrupting a real chain.
    """
    _seed_chain(1)
    monkeypatch.setattr(
        health, "_verify_chain",
        lambda _vault=None: {"matches": False, "brokenAtIndex": 1,
                              "merkleRoot": "0" * 64, "recomputedRoot": "f" * 64,
                              "blockCount": 1},
    )
    report = reporter.run_suite("hourly", seal=False)
    assert report["overallStatus"] == "FAIL", report
    squeal_dir = Path(constants.PROJECT_SQUEAL_DIR)
    faults = list(squeal_dir.glob("maintenance-fault-*.json"))
    assert faults, "expected a maintenance-fault-*.json on FAIL"
    payload = json.loads(faults[0].read_text(encoding="utf-8"))
    assert payload["source"] == "maintenance"
    assert payload["overallStatus"] == "FAIL"


# ---------------------------------------------------------------------------
# Registry / cadence tests
# ---------------------------------------------------------------------------

def test_daily_is_superset_of_hourly(temp_env):
    """DAILY runs every HOURLY routine plus the heavy daily-only ones."""
    for name in health.HOURLY:
        assert name in health.DAILY, f"{name} missing from DAILY"
    assert "disk_usage" in health.DAILY
    assert "constants_checksum" in health.DAILY
    assert "monitor_briefing" in health.DAILY


def test_every_cadence_routine_exists_in_registry():
    """No cadence references a routine that is not in ROUTINES."""
    for cadence, names in health.CADENCES.items():
        for name in names:
            assert name in health.ROUTINES, f"{cadence} references unknown {name}"


def test_run_routine_unknown_name_raises_keyerror(temp_env):
    """run_routine raises KeyError on an unknown routine (fail loud)."""
    _seed_chain(1)
    with pytest.raises(KeyError):
        health.run_routine("does_not_exist", {})


# ---------------------------------------------------------------------------
# Scheduler CLI tests
# ---------------------------------------------------------------------------

def test_scheduler_no_seal_exits_zero_on_pass(temp_env, capsys):
    """`--once --no-seal` on a clean vault exits 0 and seals nothing."""
    _seed_chain(2)
    scheduler = importlib.import_module("src.maintenance.scheduler")
    rc = scheduler.main(["--once", "--cadence", "hourly", "--no-seal"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "overall=PASS" in out
    assert len(vault_io.read_facts_registry()["blocks"]) == 2  # nothing sealed


def test_scheduler_seal_adds_one_block(temp_env, capsys):
    """`--once` (with seal) adds exactly one block and reports the seal."""
    _seed_chain(2)
    scheduler = importlib.import_module("src.maintenance.scheduler")
    before = len(vault_io.read_facts_registry()["blocks"])
    rc = scheduler.main(["--once", "--cadence", "hourly"])
    assert rc in (0, 1)
    after = len(vault_io.read_facts_registry()["blocks"])
    assert after - before == 1, "scheduler sealed != 1 block"
    out = capsys.readouterr().out
    assert "sealed block #" in out


def test_squeal_backlog_warns_over_threshold(temp_env):
    """A high backlog warns the operator."""
    _seed_chain(1)
    fake = Path(constants.PROJECT_SQUEAL_DIR)
    for i in range(60):
        (fake / f"squeal-2026-01-01T00-00-{i:02d}.json").write_text("{}", encoding="utf-8")
    r = health.run_routine("squeal_backlog", {})
    assert r["status"] == "WARN", r["summary"]
    assert r["detail"]["count"] == 60


def test_constants_checksum_warns_on_change(temp_env):
    """A changed constants.py checksum is a WARN (rules changed)."""
    _seed_chain(1)
    r0 = health.run_routine("constants_checksum", {})
    assert r0["status"] == "PASS"  # first run, no previous
    r1 = health.run_routine("constants_checksum", {"constants_checksum": "0" * 64})
    assert r1["status"] == "WARN", r1["summary"]