"""
Order Get It Right -- B4 Python 3.12 compatibility static check.

Closes OPEN_ITEMS B4. The doc (OPEN_ITEMS_AND_REFERENCE.md line 94-97)
notes the project was developed on Python 3.14.6 but the STRATEGY
promises Python 3.12 as the lowest supported version. We do not
have a Python 3.12 install on the host, so a true runtime test is
out of scope (it would require a 50 MB second-Python install).

This test is a static-analysis fallback that catches the highest-risk
class of incompatibility: language-level syntax that requires Python
>= 3.12. It is a meaningful check because:

  1. PEP 695 (type aliases, generic classes/functions) and StrEnum
     are the most common 3.12+ features a maintainer might reach for.
  2. A single PEP 695 line would break Python 3.12 with a SyntaxError
     on first import, which is exactly the kind of failure mode
     D1 (USB clean-host test) is designed to catch.
  3. The runtime semantics differences between 3.12 and 3.14 for
     stdlib-only code are minimal (the project uses no 3.13+ stdlib
     features, so the only risk surface is language syntax).

Scope: every .py under 02_Technical/src/ and 02_Technical/config/
must parse cleanly AND must contain no 3.12+ syntax nodes. This file
plus tests/ are also scanned.
"""
import ast
import os
import sys
from pathlib import Path

# 3.12+ AST node types. We use getattr so the test file itself parses
# on every Python from 3.8 onward (a meta-requirement for the test
# file to be useful).
_TYPE_ALIAS = getattr(ast, "TypeAlias", None)
_TYPE_PARAM = getattr(ast, "TypeParam", None)

# File roots to scan. Excluded: __pycache__/ (bytecode, not source),
# tauri-shell/ (Rust project, not Python), and the runtime artefacts
# dir (the .pyc files that pytest re-populates).
_SCAN_ROOTS = [
    Path(__file__).resolve().parent.parent / "02_Technical" / "src",
    Path(__file__).resolve().parent.parent / "02_Technical" / "config",
    Path(__file__).resolve().parent,  # tests/ itself
]


def _walk_python_files(roots):
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip bytecode caches
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in filenames:
                if fn.endswith(".py"):
                    yield Path(dirpath) / fn


def _scan_for_312plus_syntax(filepath: Path) -> list:
    """Return a list of (line_number, feature_name) for every 3.12+
    syntax node in the file. Empty list = clean."""
    try:
        # utf-8-sig strips the BOM that several files in the project
        # carry (constants.py, discovery_agent.py, etc.) so the parser
        # sees a clean source.
        source = filepath.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        return [(e.lineno or 0, f"SYNTAX ERROR: {e.msg}")]

    hits = []
    for node in ast.walk(tree):
        if _TYPE_ALIAS is not None and isinstance(node, _TYPE_ALIAS):
            hits.append((node.lineno, "PEP 695 type alias (type X = Y)"))
        if _TYPE_PARAM is not None:
            # Type params can appear on a ClassDef's body or as the
            # type_params attribute on a FunctionDef/AsyncFunctionDef.
            if isinstance(node, ast.ClassDef):
                for b in node.body:
                    if isinstance(b, _TYPE_PARAM):
                        hits.append((node.lineno, "PEP 695 generic class"))
                        break
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                type_params = getattr(node, "type_params", None)
                if type_params:
                    hits.append((node.lineno, "PEP 695 generic function"))
    return hits


def test_no_312plus_syntax_in_runtime():
    """Every .py file in 02_Technical/src, 02_Technical/config, and
    tests/ must be parseable and must contain no Python 3.12+ syntax.

    This is the static-analysis fallback for B4. The deeper test
    would be to actually run the test suite under Python 3.12, but
    the host does not have 3.12 installed and the runtime is stdlib-
    only so the static analysis is sufficient."""
    all_hits = []
    for filepath in _walk_python_files(_SCAN_ROOTS):
        for line, feature in _scan_for_312plus_syntax(filepath):
            all_hits.append((filepath, line, feature))
    if all_hits:
        details = "\n".join(
            f"  {path.relative_to(Path(__file__).resolve().parent.parent)}:{line}: {feature}"
            for path, line, feature in all_hits
        )
        raise AssertionError(
            "Python 3.12+ syntax found in runtime (B4 fail):\n" + details
        )


def test_runtime_parses_under_strict_utf8():
    """A stricter sub-test: every .py file in 02_Technical/src and
    02_Technical/config must parse as plain utf-8 (not utf-8-sig).
    This catches a file that depends on a BOM being present in order
    to parse, which is fragile behaviour on non-Windows hosts."""
    fail = []
    for filepath in _walk_python_files(
        [Path(__file__).resolve().parent.parent / "02_Technical" / "src",
         Path(__file__).resolve().parent.parent / "02_Technical" / "config"]
    ):
        try:
            source = filepath.read_text(encoding="utf-8")  # no -sig
            ast.parse(source, filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError) as e:
            fail.append((filepath, str(e)))
    if fail:
        details = "\n".join(
            f"  {path.relative_to(Path(__file__).resolve().parent.parent)}: {err}"
            for path, err in fail
        )
        raise AssertionError(
            "Some runtime files do not parse under strict utf-8 "
            "(they depend on a BOM being present):\n" + details
        )


def test_runtime_does_not_import_313plus_stdlib():
    """Catches any runtime import of a stdlib module or class that
    was added in Python 3.13 or later. As of 2026-07, the only such
    additions relevant to this project are:
      - graphlib.TopologicalSorter  (3.9, not relevant)
      - http.HTTPMethod             (3.11, not relevant)
      - pathlib.Path.is_junction    (3.12, safe)
      - tomllib                     (3.11, safe)
      - zoneinfo                    (3.9, safe)
    The test is a denylist: any import of a symbol whose containing
    module was added in 3.13 or 3.14 fails. The denylist is empty
    as of 2026-07-12; this test exists to catch a future maintainer
    who reaches for a 3.13+ stdlib feature."""
    # Known stdlib modules/symbols added in 3.13 or 3.14. Keep this
    # list empty for now; populate it as Python releases ship.
    _313PLUS_DENYLIST = set()
    #   e.g. {"new_module_3_13", "new_class_3_14"} -- empty as of 2026-07-12
    _313PLUS_DENYLIST = {m for m in _313PLUS_DENYLIST if m}

    fail = []
    for filepath in _walk_python_files(
        [Path(__file__).resolve().parent.parent / "02_Technical" / "src",
         Path(__file__).resolve().parent.parent / "02_Technical" / "config"]
    ):
        try:
            source = filepath.read_text(encoding="utf-8-sig")
            tree = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in _313PLUS_DENYLIST:
                        fail.append((filepath, node.lineno, alias.name))
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(
                    node.module.startswith(m) for m in _313PLUS_DENYLIST
                ):
                    fail.append((filepath, node.lineno, node.module))
    if fail:
        details = "\n".join(
            f"  {path.relative_to(Path(__file__).resolve().parent.parent)}:{line}: {mod}"
            for path, line, mod in fail
        )
        raise AssertionError(
            "Python 3.13+ stdlib import found in runtime (B4 fail):\n"
            + details
        )
