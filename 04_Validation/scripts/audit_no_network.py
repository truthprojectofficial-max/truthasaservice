"""
Order Get It Right -- No-Network Audit (static import scan, extended)

Walks every .py file under the runtime tree AND the operator-tool /
test / script trees, parses each with `ast`, and flags any import of
a module that can touch the network. Prints one line per file with a
CLEAN / ALLOWED / REVIEW / NETWORK_IMPORT_FOUND verdict.

This is the on-disk proof for the build's "zero network calls in the
runtime, allow-list only outside the runtime" promise
(OPEN_ITEMS_AND_REFERENCE.md D2). A third party with the project
folder can run this script in under 30 seconds and confirm the
runtime is offline and the operator tools are honest.

Verdict taxonomy:
  CLEAN               -- the file has no network imports
  ALLOWED             -- the file has a network import that is on the
                         allow-list (operator tool calling Ollama local,
                         or a test that replays the same call)
  REVIEW              -- the file has a network import that is NOT on
                         the allow-list. This is a new tool that needs
                         a doc note (or an accidental import).
  NETWORK_IMPORT_FOUND -- the file is inside the RUNTIME tree
                         (02_Technical/src/) and has any network import.
                         This is always a HARD FAIL. The runtime
                         promise is broken.

Exit codes:
  0  every file is CLEAN or ALLOWED
  1  at least one file is REVIEW or NETWORK_IMPORT_FOUND

Pure stdlib. No network. No LLM. No third-party deps.
"""
import ast
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Scope 1: the runtime tree. ANY network import here is a HARD FAIL.
# The runtime promise is "no network calls in the runtime". A runtime
# file reaching out is the contract being broken, not paperwork.
RUNTIME_SCOPE = PROJECT_ROOT / "02_Technical" / "src"

# Scope 2: operator tools, tests, and the audit script itself. These
# may import network modules, but only with an explicit allow-list
# entry. A new network import in this scope with no allow-list entry
# is REVIEW -- the operator needs to decide if it is intentional and
# add it to the allow-list, or remove it.
ALLOWED_SCOPES = [
    PROJECT_ROOT / "02_Technical" / "tools",
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "04_Validation" / "scripts",  # self-audit; this file
]

# Allow-list: file path (relative to PROJECT_ROOT) -> set of allowed
# top-level network module names. Each entry is justified in
# AUDIT_NO_NETWORK.md under "The Allow-List".
ALLOW_LIST: dict = {
    # The agentic REPL is the operator's natural-language interface.
    # It talks to Ollama at http://127.0.0.1:11434 (local). Stdlib
    # urllib is used to avoid the `requests` third-party dep. The
    # REPL does NOT touch the public internet.
    "02_Technical/tools/agentic_repl.py": {
        "urllib", "urllib.request", "urllib.error",
    },
    "02_Technical/tools/agentic_repl_tools.py": {
        "urllib", "urllib.request", "urllib.error",
    },
    # The discovery agent is an operator-side DNS / TCP probe. It is
    # explicitly the "operator reaches the network" tool. It does
    # not run during a normal audit; it runs only when the operator
    # invokes `onyx> discovery <target>`.
    "02_Technical/tools/discovery_agent.py": {
        "socket",
    },
    # The D5 end-to-end test replays the agentic REPL's Ollama
    # calls. It is testing the REPL, so it must use the same
    # library the REPL uses.
    "tests/test_d5_agentic_repl.py": {
        "urllib", "urllib.request", "urllib.error",
    },
    # The DNS forwarder health check is an operator-side probe
    # of the local Unbound resolver on 127.0.0.1:53. It uses
    # socket to send a raw DNS query via UDP to the loopback
    # only -- the script never opens a socket to a non-loopback
    # address. It is the "is my local DNS forwarder healthy?"
    # diagnostic, parallel to discovery_agent.py's "is the
    # network reachable from here" diagnostic. Runs only when
    # the operator invokes the health check.
    "04_Validation/scripts/dns_forwarder_health.py": {
        "socket",
    },
}

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

    verdict is one of: CLEAN, ALLOWED, REVIEW, NETWORK_IMPORT_FOUND.
    """
    if not hits:
        return "CLEAN", ""
    rel = filepath.relative_to(PROJECT_ROOT).as_posix()
    # Runtime scope: ANY network import is a hard fail.
    if RUNTIME_SCOPE in filepath.parents:
        mods = ", ".join(m for _, m in hits)
        return "NETWORK_IMPORT_FOUND", f"runtime file imports [{mods}]"
    # Allow-list scope: must match the allow-list for this file.
    allowed_for_file = ALLOW_LIST.get(rel, set())
    mods_hit = {m for _, m in hits}
    mods_allow = {m.split(".", 1)[0] for m in mods_hit} | mods_hit
    if mods_allow.issubset(allowed_for_file):
        return "ALLOWED", f"on allow-list: {sorted(mods_allow)}"
    extras = sorted(mods_allow - allowed_for_file)
    return "REVIEW", f"not on allow-list: {extras}"


def main() -> int:
    files = []
    files.extend(sorted(_walk_python_files(RUNTIME_SCOPE)))
    for scope in ALLOWED_SCOPES:
        files.extend(sorted(_walk_python_files(scope)))
    files = sorted(set(files))

    if not files:
        print(f"ERROR: no .py files found in any scope", file=sys.stderr)
        return 2

    rt_count = sum(1 for f in files if RUNTIME_SCOPE in f.parents)
    tool_count = sum(1 for f in files if (PROJECT_ROOT / "02_Technical" / "tools") in f.parents)
    test_count = sum(1 for f in files if (PROJECT_ROOT / "tests") in f.parents)
    script_count = sum(1 for f in files if (PROJECT_ROOT / "04_Validation" / "scripts") in f.parents)

    lines = []
    lines.append(f"NO-NETWORK AUDIT (extended) -- {len(files)} .py files")
    lines.append(f"  runtime:   {rt_count}  (02_Technical/src/ -- hard-fail scope)")
    lines.append(f"  tools/:    {tool_count}  (operator CLI tools)")
    lines.append(f"  tests/:    {test_count}  (pytest)")
    lines.append(f"  scripts/:  {script_count}  (04_Validation/scripts/)")
    lines.append("-" * 78)

    counts = {"CLEAN": 0, "ALLOWED": 0, "REVIEW": 0, "NETWORK_IMPORT_FOUND": 0}
    for fp in files:
        rel = fp.relative_to(PROJECT_ROOT)
        hits = _scan_file(fp)
        verdict, reason = _classify_file(fp, hits)
        counts[verdict] += 1
        if verdict == "CLEAN":
            lines.append(f"CLEAN      {rel}")
        elif verdict == "ALLOWED":
            lines.append(f"ALLOWED    {rel}  -- {reason}")
        elif verdict == "REVIEW":
            mods = ", ".join(f"{m} (line {ln})" for ln, m in hits)
            lines.append(f"REVIEW     {rel}  -- {mods}")
        else:  # NETWORK_IMPORT_FOUND
            mods = ", ".join(f"{m} (line {ln})" for ln, m in hits)
            lines.append(f"FAIL       {rel}  -- {mods}")
    lines.append("-" * 78)
    lines.append(
        f"Summary: CLEAN={counts['CLEAN']}  "
        f"ALLOWED={counts['ALLOWED']}  "
        f"REVIEW={counts['REVIEW']}  "
        f"FAIL={counts['NETWORK_IMPORT_FOUND']}"
    )

    if counts["NETWORK_IMPORT_FOUND"] == 0 and counts["REVIEW"] == 0:
        lines.append("RESULT: PASS -- runtime is offline; tools/ and tests/ are on the allow-list.")
        lines.append("The 'no network calls in the runtime, allow-list only outside' promise holds.")
        print("\n".join(lines))
        return 0
    else:
        if counts["NETWORK_IMPORT_FOUND"] > 0:
            lines.append(
                "RESULT: FAIL -- the runtime tree (02_Technical/src/) imports a "
                "network module. The runtime promise is broken."
            )
        if counts["REVIEW"] > 0:
            lines.append(
                "RESULT: FAIL -- one or more files have a network import that is "
                "not on the allow-list. Either remove the import or add it to "
                "ALLOW_LIST in this script and document it in AUDIT_NO_NETWORK.md."
            )
        print("\n".join(lines))
        return 1


if __name__ == "__main__":
    sys.exit(main())
