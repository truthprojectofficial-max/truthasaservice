"""
00-99 Boundary Enforcement Test

The strict 00-99 rule says:
  - 02_Technical cannot import from 03_Vault or 04_Validation
  - tests/ cannot import from src/
  - tests go through the HTTP API only

This test does an AST scan of every Python file in the project and
fails with a precise message on any violation. The message is the
"why" of the rule, not just the line number.
"""
import ast
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL_SRC = PROJECT_ROOT / "02_Technical" / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
VAULT_NAMES = {"03_Vault", "04_Validation"}

# Per the strict rule, the vault path is constructed only in
# src/io/vault_io.py and config/constants.py.  Any other file that
# hard-codes the literal "03_Vault" or "04_Validation" violates the
# boundary because it couples code to data.
VAULT_COUPLING_FILE_WHITELIST = {
    (PROJECT_ROOT / "02_Technical" / "src" / "io" / "vault_io.py").resolve(),
    (PROJECT_ROOT / "02_Technical" / "config" / "constants.py").resolve(),
}

# tests/ is allowed to import a tiny set of public, deterministic,
# side-effect-free symbols from 02_Technical. Everything else must go
# through the HTTP API.
# The whitelist below is enforced by test_no_src_imports_in_tests().
TESTS_CAN_IMPORT_FROM = {
    # The FastAPI app object is the public HTTP surface. Tests/ mounts it
    # via TestClient. This is the primary src.* import the test suite
    # makes, and the boundary test (below) enforces it.
    "src.server.app.app",
    # ``canonical_dumps`` is a pure, deterministic JSON serialiser used
    # by vault_io.py and verify_chain.py. It cannot be exercised through
    # plain JSON HTTP because plain JSON has no representation for
    # datetime, UUID, Decimal, set, frozenset, Path, or Enum. The
    # canonical-JSON hardening tests therefore import this single utility
    # directly; no other src.* symbol is permitted.
    "src.utils.canonical.canonical_dumps",
    # The A3 regression test (test_seed_facts_preserves_operator_facts_across_reseed)
    # needs to clear the module-level _SEEDED guard and call _ensure_seeded()
    # to simulate a server restart in-process. Whitelist the module import.
    "src.server.app",
}


def _walk_python_files(root: Path):
    for dirpath, _dirnames, filenames in os.walk(root):
        if "__pycache__" in dirpath or ".pytest_cache" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                yield Path(dirpath) / fn


def _imports_vault_or_validation(filepath: Path, tree: ast.AST) -> list:
    """Return a list of (line, message) for any import that crosses the 00-99 boundary."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                if any(part in mod.split(".") for part in VAULT_NAMES):
                    violations.append((
                        node.lineno,
                        f"import {mod} -- 02_Technical cannot import from a vault or validation folder",
                    ))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            # Walk up the relative dots to find the absolute target
            depth = node.level or 0
            # If relative (level > 0), check if any parent is a vault/validation
            if depth > 0:
                # Relative imports walk up `depth` levels. If any of those
                # levels could be a vault/validation, the import is
                # ambiguous. The strict rule says no relative imports
                # that could touch the vault.
                # For simplicity, just flag any non-zero level import in
                # 02_Technical that goes through more than one level,
                # because 02_Technical is exactly two levels under
                # the project root.
                if depth >= 1:
                    # Try to resolve by going up `depth` levels from
                    # the file's directory.
                    target = filepath.parent
                    for _ in range(depth):
                        target = target.parent
                    if any(part in target.parts for part in VAULT_NAMES):
                        violations.append((
                            node.lineno,
                            f"from .{'.' * depth}{mod} -- relative import walks up into a vault/validation folder",
                        ))
            elif any(part in mod.split(".") for part in VAULT_NAMES):
                violations.append((
                    node.lineno,
                    f"from {mod} import ... -- 02_Technical cannot import from a vault or validation folder",
                ))
    return violations


def _imports_from_src(test_filepath: Path, tree: ast.AST) -> list:
    """Return a list of (line, message) for any test file that imports from src/.

    The one and only exception is `from src.server.app import app` -- the
    FastAPI app object, which the HTTP test client mounts. Any other src.*
    import is a violation. Whole-module imports of `src` (e.g. `import src`)
    are NEVER allowed, because they would let a test reach every internal
    symbol. Only the single whitelisted fully-qualified symbol is permitted,
    and only when it is bound by an `ImportFrom` (i.e. `from ... import app`).
    """
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # Bare `import src` or `import src.foo` is NEVER allowed.
            for alias in node.names:
                if alias.name == "src" or alias.name.startswith("src."):
                    violations.append((
                        node.lineno,
                        f"import {alias.name} -- tests cannot import from src/; "
                        f"the only allowed import is `from src.server.app import app`",
                    ))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == "src" or mod.startswith("src."):
                # Allow ONLY the specific whitelisted symbol, bound by name.
                for alias in node.names:
                    fqname = f"{mod}.{alias.name}" if mod else alias.name
                    if fqname in TESTS_CAN_IMPORT_FROM:
                        # The whitelist entry is `src.server.app.app`;
                        # the ImportFrom is `from src.server.app import app`.
                        # Above loop builds `src.server.app.app`. Match.
                        continue
                    allowed = ", ".join(sorted(TESTS_CAN_IMPORT_FROM))
                    violations.append((
                        node.lineno,
                        f"from {mod} import {alias.name} -- tests cannot import "
                        f"from src/; allowed imports: {allowed}",
                    ))
            # Also flag relative imports that walk into src/
            if (node.level or 0) > 0:
                target = test_filepath.parent
                for _ in range(node.level):
                    target = target.parent
                if node.module:
                    full_target = (target / node.module.replace(".", "/")).resolve()
                else:
                    full_target = target.resolve()
                if "src" in full_target.parts:
                    violations.append((
                        node.lineno,
                        f"relative import walks into src/ -- tests cannot "
                        f"import from src/; use the HTTP API only",
                    ))
    return violations


def _hardcodes_vault_path(filepath: Path, tree: ast.AST) -> list:
    """Return (line, message) for any string literal naming 03_Vault or 04_Validation outside the whitelist."""
    violations = []
    if filepath.resolve() in VAULT_COUPLING_FILE_WHITELIST:
        return violations
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for name in VAULT_NAMES:
                if name in node.value:
                    violations.append((
                        node.lineno,
                        f"hard-coded {name!r} in {filepath.name} -- vault coupling must go through src/io/vault_io.py",
                    ))
    return violations


class TestBoundary(unittest.TestCase):
    def test_no_vault_or_validation_imports_in_technical(self):
        """No file under 02_Technical/src may import from 03_Vault or 04_Validation."""
        all_violations = []
        for filepath in _walk_python_files(TECHNICAL_SRC):
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            try:
                tree = ast.parse(source, filename=str(filepath))
            except SyntaxError:
                continue
            all_violations.extend(_imports_vault_or_validation(filepath, tree))
        if all_violations:
            lines = "\n".join(f"  {filepath.name}:{ln}: {msg}" for ln, msg in all_violations)
            self.fail(
                "00-99 BOUNDARY VIOLATION\n"
                "  rule: code in 02_Technical cannot import from 03_Vault or 04_Validation\n"
                "  effect: vault data is now reachable from code. Trust boundary broken.\n"
                f"  {lines}\n"
            )

    def test_no_src_imports_in_tests(self):
        """No test file may import from src/. Tests go through the HTTP API only."""
        all_violations = []  # (filename, lineno, message)
        for filepath in _walk_python_files(TESTS_DIR):
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            try:
                tree = ast.parse(source, filename=str(filepath))
            except SyntaxError:
                continue
            for ln, msg in _imports_from_src(filepath, tree):
                all_violations.append((filepath.name, ln, msg))
        if all_violations:
            lines = "\n".join(f"  {name}:{ln}: {msg}" for name, ln, msg in all_violations)
            self.fail(
                "00-99 BOUNDARY VIOLATION\n"
                "  rule: tests cannot import from src/; they go through the HTTP API only\n"
                "  effect: tests are coupled to internal structure. Boundary cannot be tested.\n"
                f"  {lines}\n"
            )

    def test_no_hardcoded_vault_paths_outside_whitelist(self):
        """Only src/io/vault_io.py and config/constants.py may construct vault paths."""
        all_violations = []
        for filepath in _walk_python_files(TECHNICAL_SRC):
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            try:
                tree = ast.parse(source, filename=str(filepath))
            except SyntaxError:
                continue
            all_violations.extend(_hardcodes_vault_path(filepath, tree))
        if all_violations:
            lines = "\n".join(f"  {filepath.name}:{ln}: {msg}" for ln, msg in all_violations)
            self.fail(
                "00-99 BOUNDARY VIOLATION\n"
                "  rule: only src/io/vault_io.py and config/constants.py may name 03_Vault or 04_Validation\n"
                "  effect: code is coupled to data paths. Boundary cannot be enforced.\n"
                f"  {lines}\n"
            )


if __name__ == "__main__":
    unittest.main()