"""
Order Get It Right -- Ollama isolation validation.

Locks the contract that Ollama is an optional operator convenience,
not a runtime dependency. The deterministic engine must work without it.
"""
import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
TOOLS_DIR = TECHNICAL / "tools"
RUNTIME_DIRS = [
    TECHNICAL / "src" / "engines",
    TECHNICAL / "src" / "server",
    TECHNICAL / "src" / "agents",
    TECHNICAL / "src" / "io",
    TECHNICAL / "src" / "utils",
]


def _imports_ollama(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                if "ollama" in name.lower():
                    return True
    for token in ["ollama", "Ollama", "OLLAMA_HOST", "OLLAMA_URL"]:
        if token in source:
            return True
    return False


def test_runtime_has_no_ollama_dependency():
    for directory in RUNTIME_DIRS:
        for py_file in directory.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            # audit_review_agent.py legitimately contains "ollama" as a
            # keyword marker in third-party assistant detection.
            if py_file.name == "audit_review_agent.py":
                assert "ollama" in source.lower(), (
                    "audit_review_agent.py lost its third-party marker"
                )
                continue
            assert not _imports_ollama(source), (
                f"runtime file depends on Ollama: {py_file}"
            )


def test_ollama_code_isolated_to_tools():
    ollama_tool_files = list(TOOLS_DIR.rglob("*ollama*")) + list(TOOLS_DIR.rglob("*agentic_repl*"))
    assert len(ollama_tool_files) > 0, "agentic REPL files missing from tools/"


def test_ollama_disaster_note_exists():
    doc = PROJECT_ROOT / "04_Validation" / "session_logs" / "OLLAMA_TIMEOUT_DISASTER_NOTE_2026-07-21.md"
    assert doc.is_file(), f"missing Ollama disaster note: {doc}"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "timeout warnings",
        "ClineCLI",
        "optional operator convenience",
        "engine must never require Ollama",
    ]:
        assert phrase in text, f"disaster note missing phrase: {phrase}"


def test_d5_test_is_skip_guarded():
    d5_test = PROJECT_ROOT / "tests" / "test_d5_agentic_repl.py"
    assert d5_test.is_file(), "missing D5 agentic REPL test"
    source = d5_test.read_text(encoding="utf-8")
    assert "pytest.skip" in source or "@pytest.mark.skipif" in source, (
        "D5 test does not skip when Ollama/FastAPI is unavailable"
    )
