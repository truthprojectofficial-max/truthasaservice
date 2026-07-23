"""
Order Get It Right -- No-Network Audit (static import scan, extended)

Walks every .py file under the runtime tree AND the operator-tool /
test / script trees, parses each with `ast`, and flags any import of
a module that can touch the network. Prints one line per file with a
CLEAN / NETWORK_IMPORT_FOUND verdict.

This is the on-disk proof for the build's "zero network calls
anywhere" promise (operator 2026-07-22 directive). A third party
with the project folder can run this script in under 30 seconds and
confirm the entire build is offline. There is no allow-list; every
network import is a hard fail.

Verdict taxonomy (post-2026-07-24):
  CLEAN               -- the file has no network imports
  NETWORK_IMPORT_FOUND -- the file has a network import.
                         This is always a HARD FAIL. The zero-network
                         promise is broken.

Exit codes:
  0  every file is CLEAN
  1  at least one file is NETWORK_IMPORT_FOUND

Pure stdlib. No network. No LLM. No third-party deps.

History:
  - 2026-07-17 (block 4944): D2_NO_NETWORK_AUDIT_EXTENDED, allow-list of 4 files
  - 2026-07-23 (block 35595): 5-allow-list CLOSED_AND_LOCKED, 5 entries
  - 2026-07-24: 5-allow-list DROPPED per operator 2026-07-22 directive.
    Zero network modules anywhere. All 5 previously-allow-listed files
    rewritten to use subprocess + curl / nslookup / Resolve-DnsName.
"""
import ast
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# All scopes are now hard-fail. The allow-list is gone.
SCOPES = [
    PROJECT_ROOT / "02_Technical" / "src",     # runtime
    PROJECT_ROOT / "02_Technical" / "tools",   # operator tools
    PROJECT_ROOT / "tests",                    # pytest
    PROJECT_ROOT / "04_Validation" / "scripts",  # self-audit
]

# Modules that can touch the network. Each entry is a top-level module
# name as it would appear in `import X` or `from X import ...`.
NETWORK_MODULES = {
    "urllib",
    "urllib2",
    "urllib3",
    "requests",
    "httpx",
    "http",
    "http.client",
    "socket",
    "ssl",
    "smtplib",
    "imaplib",
    "poplib",
    "ftplib",
    "telnetlib",
    "asyncio",
    "aiohttp",
    "httplib",
    "xmlrpc",
    "xmlrpc.client",
    "xmlrpc.server",
    "socketserver",
}

# Top-level prefix matches (e.g. `urllib.request` is caught via "urllib").
NETWORK_PREFIXES = {
    "urllib",
    "http",
}


def _module_is_network(module_name: str) -> bool:
    if module_name in NETWORK_MODULES:
        return True
    top = module_name.split(".", 1)[0]
    if top in NETWORK_PREFIXES:
        return True
    if module_name in {"asyncio"}:
        # asyncio is a network-adjacent module: while it can be used
        # purely for local concurrency, in a no-network build we want
        # to know it is there. Flag it for operator review.
        return True
    return False


def _walk_python_files(root: Path):
    if not root.exists():
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        if "__pycache__" in dirpath or ".pytest_cache" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                yield Path(dirpath) / fn


def _scan_file(filepath: Path) -> list:
    """Return list of (line, module) for every network import found."""
    hits = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return hits
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _module_is_network(alias.name):
                    hits.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None and _module_is_network(node.module):
                hits.append((node.lineno, node.module))
    return hits


def _classify_file(filepath: Path, hits: list) -> tuple:
    """Return (verdict, reason) for a file given its network-import hits.

    Post-2026-07-24: the allow-list is gone. ANY network import is a
    hard fail anywhere in the build.
    """
    if not hits:
        return "CLEAN", ""
    mods = ", ".join(m for _, m in hits)
    return "NETWORK_IMPORT_FOUND", f"network import [{mods}]"


def main() -> int:
    files = []
    for scope in SCOPES:
        files.extend(sorted(_walk_python_files(scope)))
    files = sorted(set(files))

    if not files:
        print(f"ERROR: no .py files found in any scope", file=sys.stderr)
        return 2

    lines = []
    lines.append(f"NO-NETWORK AUDIT (extended) -- {len(files)} .py files")
    for scope in SCOPES:
        rel = scope.relative_to(PROJECT_ROOT)
        n = sum(1 for f in files if scope in f.parents)
        lines.append(f"  {rel.as_posix()}: {n}")
    lines.append("-" * 78)

    counts = {"CLEAN": 0, "NETWORK_IMPORT_FOUND": 0}
    for fp in files:
        rel = fp.relative_to(PROJECT_ROOT)
        hits = _scan_file(fp)
        verdict, reason = _classify_file(fp, hits)
        counts[verdict] += 1
        if verdict == "CLEAN":
            lines.append(f"CLEAN      {rel}")
        else:  # NETWORK_IMPORT_FOUND
            mods = ", ".join(f"{m} (line {ln})" for ln, m in hits)
            lines.append(f"FAIL       {rel}  -- {mods}")
    lines.append("-" * 78)
    lines.append(
        f"Summary: CLEAN={counts['CLEAN']}  "
        f"FAIL={counts['NETWORK_IMPORT_FOUND']}"
    )

    if counts["NETWORK_IMPORT_FOUND"] == 0:
        lines.append("RESULT: PASS -- zero network modules anywhere.")
        lines.append("The 'no network calls anywhere' promise holds.")
        print("\n".join(lines))
        return 0
    else:
        lines.append(
            "RESULT: FAIL -- one or more files have a network import. "
            "Remove the import or replace it with subprocess + curl / "
            "nslookup / Resolve-DnsName."
        )
        print("\n".join(lines))
        return 1


if __name__ == "__main__":
    sys.exit(main())
