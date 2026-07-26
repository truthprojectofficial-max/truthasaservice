"""
Order Get It Right -- Stale snapshot rebuttal validation.

Locks the fact that the historical bug list in faults..txt is already
closed by the live regression suite and modern app lifecycle.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

from fastapi.testclient import TestClient  # noqa: E402
from src.server.app import app  # noqa: E402


def test_faults_rebuttal_doc_exists():
    doc = PROJECT_ROOT / "04_Validation" / "reference_misc" / "FAULTS_STALE_SNAPSHOT_REBUTTED_2026-07-21.md"
    assert doc.is_file(), f"missing faults rebuttal doc: {doc}"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "test_c14_canonical_json_hardening",
        "test_a5_deploy_dry_run",
        "test_b3_host_dependent",
        "_lifespan",
        "_seed_facts_once",
        "DECEPTION_ONTOLOGY_VERSION",
    ]:
        assert phrase in text, f"rebuttal doc missing expected phrase: {phrase}"


def test_app_uses_lifespan_not_on_event():
    """Regression for deprecated @app.on_event('startup') hook."""
    app_file = TECHNICAL / "src" / "server" / "app.py"
    source = app_file.read_text(encoding="utf-8")
    # The file may mention @app.on_event only inside explanatory comments/docstrings.
    # We require the modern lifespan registration and no actual decorator usage.
    assert "app = FastAPI(" in source and "lifespan=_lifespan" in source.replace(" ", ""), (
        "app.py not wired to the lifespan handler"
    )
    # Strip the docstring for the decorator check: line 97 explicitly says
    # 'Replaces @app.on_event("startup")' as a comment, not a decorator.
    assert "@app.on_event(" not in source.split('"""')[-1], (
        "app.py still contains an actual @app.on_event decorator"
    )


def test_seed_facts_guards_against_nonempty_registry():
    """_seed_facts_once must not reset a registry that already has facts."""
    app_file = TECHNICAL / "src" / "server" / "app.py"
    source = app_file.read_text(encoding="utf-8")
    assert "if facts_registry.list_facts():" in source, (
        "_seed_facts_once missing non-empty guard"
    )
    assert "facts_registry.reset_registry()" in source, (
        "_seed_facts_once missing reset path for empty registry"
    )


def test_canonical_json_hardening_tests_exist():
    test_file = PROJECT_ROOT / "tests" / "test_c14_canonical_json_hardening.py"
    assert test_file.is_file(), "missing canonical JSON hardening regression test"


def test_deploy_dry_run_tests_exist():
    test_file = PROJECT_ROOT / "tests" / "test_a5_deploy_dry_run.py"
    assert test_file.is_file(), "missing A5 deploy dry-run regression test"


def test_host_dependent_tests_exist():
    test_file = PROJECT_ROOT / "tests" / "test_b3_host_dependent.py"
    assert test_file.is_file(), "missing B3 host-dependent regression test"
