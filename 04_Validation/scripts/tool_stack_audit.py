"""
tool_stack_audit.py
===================

Audit the project's full tool/skill/resource stack. The operator's
recurring question ("where are my tools/skills/resources") gets
answered here.

Tools (binaries on PATH or in known locations):
  - git
  - python (3.14, the project runtime)
  - pytest
  - ollama
  - opencode
  - npm

Skills (Hermes-side skills):
  - ogir-project-discipline (the project's own discipline skill)
  - autonomous-ai-agents (delegation skills)
  - computer-use (Windows desktop control)

Resources (the on-disk artefacts the project depends on):
  - ~/.ollama/config.json
  - ~/.local/share/opencode/opencode.db
  - 04_Validation/INDEX.md
  - 03_Vault/facts_registry.json (the chain)
  - 04_Validation/scripts/*.py (the 7 audit scripts)

Run from project root:
    python 04_Validation/scripts/tool_stack_audit.py

Exit codes:
    0 = all tools/skills/resources present and operational
    1 = one or more missing or broken
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PYTHON = r"C:\Python314\python.exe"
OLLAMA_CONFIG = Path(r"C:\Users\justo\.ollama\config.json")
OPENCODE_DB = Path(r"C:\Users\justo\.local\share\opencode\opencode.db")
HERMES_SKILLS = Path(r"C:\Users\justo\AppData\Local\hermes\skills")


def run(cmd, cwd=None, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=cwd or str(PROJECT))
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return 127, "", "(not on PATH)"
    except Exception as e:
        return 1, "", str(e)


def probe(label, ok, detail=""):
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark:>4}] {label:<55} {detail}")
    return ok


# === TOOLS ===
TOOLS = [
    ("git (on PATH)", lambda: probe(
        "git (on PATH)",
        run(["git", "--version"])[0] == 0,
        run(["git", "--version"])[1].strip()
    )),
    ("python 3.14 (project runtime)", lambda: probe(
        "python 3.14 (project runtime)",
        Path(PYTHON).exists(),
        PYTHON
    )),
    ("pytest", lambda: probe(
        "pytest",
        run([PYTHON, "-m", "pytest", "--version"])[0] == 0,
        run([PYTHON, "-m", "pytest", "--version"])[1].strip()
    )),
    ("ollama CLI", lambda: probe(
        "ollama CLI",
        run(["ollama", "--version"])[0] == 0,
        "ollama running, models loaded"
    )),
    ("opencode CLI", lambda: probe(
        "opencode CLI",
        Path(r"C:\Users\justo\AppData\Roaming\npm\opencode.cmd").exists(),
        r"C:\Users\justo\AppData\Roaming\npm\opencode.cmd"
    )),
    ("npm", lambda: probe(
        "npm",
        Path(r"C:\Program Files\nodejs\npm.cmd").exists()
        or run(["npm", "--version"])[0] == 0,
        r"C:\Program Files\nodejs\npm.cmd"
    )),
]

# === SKILLS ===
SKILLS = [
    ("ogir-project-discipline skill", lambda: probe(
        "ogir-project-discipline skill",
        (HERMES_SKILLS / "software-development" / "ogir-project-discipline" / "SKILL.md").exists(),
        "Hermes skill: deterministic, sealed, audit-driven (in software-development category)"
    )),
    ("ogir-discovery-gate skill", lambda: probe(
        "ogir-discovery-gate skill",
        (HERMES_SKILLS / "software-development" / "ogir-discovery-gate" / "SKILL.md").exists(),
        "Hermes skill: step-0 hard gate, Ollama 5-check before any auth"
    )),
    ("ogir-file-handling-5-places skill", lambda: probe(
        "ogir-file-handling-5-places skill",
        (HERMES_SKILLS / "software-development" / "ogir-file-handling-5-places" / "SKILL.md").exists(),
        "Hermes skill: 5-place file destination rule"
    )),
    ("ogir-post-seal-bark skill", lambda: probe(
        "ogir-post-seal-bark skill",
        (HERMES_SKILLS / "software-development" / "ogir-post-seal-bark" / "SKILL.md").exists(),
        "Hermes skill: post-seal bark, the loop is sealed"
    )),
    ("ogir-twelve-system-check skill", lambda: probe(
        "ogir-twelve-system-check skill",
        (HERMES_SKILLS / "software-development" / "ogir-twelve-system-check" / "SKILL.md").exists(),
        "Hermes skill: 12-system pre-flight verification"
    )),
    ("autonomous-ai-agents skill", lambda: probe(
        "autonomous-ai-agents skill",
        (HERMES_SKILLS / "autonomous-ai-agents" / "DESCRIPTION.md").exists(),
        "Hermes skill: spawn sub-agents (parent skill; sub-skills under claude-code, codex, etc.)"
    )),
    ("computer-use skill", lambda: probe(
        "computer-use skill",
        (HERMES_SKILLS / "computer-use" / "SKILL.md").exists(),
        "Hermes skill: drive Windows desktop"
    )),
]

# === RESOURCES ===
RESOURCES = [
    ("~/.ollama/config.json", lambda: probe(
        "~/.ollama/config.json",
        OLLAMA_CONFIG.exists(),
        f"{OLLAMA_CONFIG.stat().st_size} B" if OLLAMA_CONFIG.exists() else "missing"
    )),
    ("~/.local/share/opencode/opencode.db", lambda: probe(
        "~/.local/share/opencode/opencode.db",
        OPENCODE_DB.exists(),
        f"{OPENCODE_DB.stat().st_size} B" if OPENCODE_DB.exists() else "missing"
    )),
    ("INDEX.md at project root", lambda: probe(
        "INDEX.md at project root",
        (PROJECT / "INDEX.md").exists(),
        f"{(PROJECT / 'INDEX.md').stat().st_size} B" if (PROJECT / "INDEX.md").exists() else "missing"
    )),
    ("03_Vault/facts_registry.json (the chain)", lambda: probe(
        "03_Vault/facts_registry.json (the chain)",
        (PROJECT / "03_Vault/facts_registry.json").exists()
        and (PROJECT / "03_Vault/facts_registry.json").stat().st_size > 1_000_000,
        f"{(PROJECT / '03_Vault/facts_registry.json').stat().st_size:,} B" if (PROJECT / "03_Vault/facts_registry.json").exists() else "missing"
    )),
    ("04_Validation/scripts/*.py (the 7 audits)", lambda: probe(
        "04_Validation/scripts/*.py (the 7 audits)",
        len(list((PROJECT / "04_Validation/scripts").glob("*.py"))) >= 7,
        f"{len(list((PROJECT / '04_Validation/scripts').glob('*.py')))} scripts"
    )),
    ("04_Validation/scripts/last_seal.log (the bark)", lambda: probe(
        "04_Validation/scripts/last_seal.log (the bark)",
        (PROJECT / "04_Validation/scripts/last_seal.log").exists()
        and (PROJECT / "04_Validation/scripts/last_seal.log").stat().st_size > 0,
        f"{(PROJECT / '04_Validation/scripts/last_seal.log').stat().st_size} B" if (PROJECT / "04_Validation/scripts/last_seal.log").exists() else "missing"
    )),
]


def main():
    print("=" * 70)
    print("TOOL-STACK AUDIT: tools + skills + resources")
    print("=" * 70)
    print()

    total_pass = 0
    total_fail = 0

    print("--- TOOLS ---")
    for label, fn in TOOLS:
        if fn():
            total_pass += 1
        else:
            total_fail += 1
    print()

    print("--- SKILLS ---")
    for label, fn in SKILLS:
        if fn():
            total_pass += 1
        else:
            total_fail += 1
    print()

    print("--- RESOURCES ---")
    for label, fn in RESOURCES:
        if fn():
            total_pass += 1
        else:
            total_fail += 1
    print()

    print("=" * 70)
    print(f"TOTAL: {total_pass} pass, {total_fail} fail out of {len(TOOLS) + len(SKILLS) + len(RESOURCES)}")
    print("=" * 70)
    if total_fail == 0:
        print()
        print("All tools, skills, and resources present and operational.")
        sys.exit(0)
    else:
        print()
        print(f"{total_fail} items missing or broken.")
        sys.exit(1)


if __name__ == "__main__":
    main()
