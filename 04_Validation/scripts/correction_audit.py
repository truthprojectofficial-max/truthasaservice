"""
correction_audit.py
===================

Cross-checks every correction made in a session against the on-disk state
+ the chain + the git log. A correction that exists in only ONE place is
a crack. A correction that shows up across code + test + doc + commit
message + chain block is hardened.

This is the operator's "investigation tool" (per 2026-07-23): every
correction made is a probe that, when re-run, tells us whether the fix
is still in place or whether it has drifted. Run this BEFORE any new
work to confirm the baseline.

Run from project root:
    python 04_Validation/scripts/correction_audit.py

Exit codes:
    0 = all corrections still in place (no cracks)
    1 = one or more cracks detected (output lists them)
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple, Callable

PROJECT = Path(__file__).resolve().parents[2]
CHAIN_PATH = PROJECT / "03_Vault" / "facts_registry.json"
PYTHON = r"C:\Python314\python.exe"

# ----------------------------------------------------------------------------
# PROBES
# ----------------------------------------------------------------------------
# Each correction is a dict with: name, commit, chain block, list of probes.
# A probe is (label, callable) where the callable returns True if the
# correction is still in place at that location.

CORRECTIONS = [
    {
        "name": "C1: 5-allow-list closed-set policy",
        "commit": "c80150d",
        "block": 35595,
        "probes": [
            ("test_allow_list_closed.py exists",
             lambda: (PROJECT / "tests/test_allow_list_closed.py").exists()),
            ("AUDIT_NO_NETWORK.md says 'Five files'",
             lambda: "Five files" in (PROJECT / "04_Validation/architecture_assessment/AUDIT_NO_NETWORK.md").read_text(encoding="utf-8")),
            ("allow_list_audit.py exists (WP-4 governance)",
             lambda: (PROJECT / "04_Validation/scripts/allow_list_audit.py").exists()),
            ("test_allow_list_closed.py passes",
             lambda: subprocess.run([PYTHON, "-m", "pytest",
                                     "tests/test_allow_list_closed.py", "-q"],
                                    capture_output=True, text=True,
                                    cwd=str(PROJECT)).returncode == 0),
            ("chain block 35595 has ALLOW_LIST_CLOSED event_type",
             lambda: any(b["index"] == 35595 and "ALLOW_LIST" in b["event_type"]
                         for b in json.loads(CHAIN_PATH.read_text(encoding="utf-8"))["blocks"])),
        ],
    },
    {
        "name": "C2: INDEX.md at project root (one-page entry point)",
        "commit": "00146f6",
        "block": 35663,
        "probes": [
            ("INDEX.md at project root",
             lambda: (PROJECT / "INDEX.md").exists()),
            ("INDEX.md has 'How to start a new session'",
             lambda: "How to start a new session" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")),
            ("INDEX.md has STEP 0 hard gate (discovery gate)",
             lambda: "STEP 0 IS A HARD GATE" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")),
            ("INDEX.md has step 3.5 (bark log read)",
             lambda: "3.5" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")
                     and "last_seal.log" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")),
            ("INDEX.md mentions loop-sealed rule",
             lambda: "loop" in (PROJECT / "INDEX.md").read_text(encoding="utf-8").lower()
                     and "sealed" in (PROJECT / "INDEX.md").read_text(encoding="utf-8").lower()),
        ],
    },
    {
        "name": "C3: Build directive operational (local-Ollama path)",
        "commit": "9fcae15",
        "block": 35662,
        "probes": [
            ("BUILD_DIRECTIVE_SPAWN_AND_SPREAD file exists",
             lambda: (PROJECT / "04_Validation/build_directives/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md").exists()),
            ("Section 8 (auth) marked resolved",
             lambda: "auth" in (PROJECT / "04_Validation/build_directives/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md")
                     .read_text(encoding="utf-8").lower()
                     and "resolved" in (PROJECT / "04_Validation/build_directives/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md")
                     .read_text(encoding="utf-8").lower()),
            ("Section 5 (unified local-Ollama path)",
             lambda: "unified" in (PROJECT / "04_Validation/build_directives/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md")
                     .read_text(encoding="utf-8").lower()
                     and "ollama" in (PROJECT / "04_Validation/build_directives/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md")
                     .read_text(encoding="utf-8").lower()),
        ],
    },
    {
        "name": "C4: Step 0 hard gate (Ollama 5-check)",
        "commit": "59d8d27",
        "block": 36379,
        "probes": [
            ("INDEX.md has STEP 0",
             lambda: "STEP 0" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")),
            ("5-check Ollama verification in INDEX.md",
             lambda: "Ollama" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")
                     and ("5-check" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")
                          or "5 checks" in (PROJECT / "INDEX.md").read_text(encoding="utf-8"))),
            ("opencode run smoke test in INDEX.md",
             lambda: "opencode run" in (PROJECT / "INDEX.md").read_text(encoding="utf-8")),
            ("chain block 36379 has DISCOVERY_GATE event_type",
             lambda: any(b["index"] == 36379 and "DISCOVERY_GATE" in b["event_type"]
                         for b in json.loads(CHAIN_PATH.read_text(encoding="utf-8"))["blocks"])),
        ],
    },
    {
        "name": "C5: Post-seal bark (loop is sealed)",
        "commit": "6bf704b",
        "block": 36511,
        "probes": [
            ("vault_io.py has _post_seal_bark function",
             lambda: "_post_seal_bark" in (PROJECT / "02_Technical/src/io/vault_io.py")
                     .read_text(encoding="utf-8")),
            ("vault_io.py calls _post_seal_bark in append_block",
             lambda: "_post_seal_bark(block, event_type, payload)"
                     in (PROJECT / "02_Technical/src/io/vault_io.py").read_text(encoding="utf-8")),
            ("BARK_LOG_PATH anchored to facts_registry_path",
             lambda: "facts_registry_path" in (PROJECT / "02_Technical/src/io/vault_io.py")
                     .read_text(encoding="utf-8")
                     and "BARK_LOG_PATH" in (PROJECT / "02_Technical/src/io/vault_io.py")
                     .read_text(encoding="utf-8")),
            ("Bark log file exists at canonical path",
             lambda: (PROJECT / "04_Validation/scripts/last_seal.log").exists()),
            ("Bark log has multiple entries",
             lambda: (PROJECT / "04_Validation/scripts/last_seal.log").stat().st_size > 200),
            ("test_post_seal_bark.py exists",
             lambda: (PROJECT / "tests/test_post_seal_bark.py").exists()),
            ("test_post_seal_bark.py has 6+ tests",
             lambda: (PROJECT / "tests/test_post_seal_bark.py").read_text(encoding="utf-8")
                     .count("def test_") >= 6),
            ("Bark log is in .gitignore",
             lambda: "last_seal.log" in (PROJECT / ".gitignore").read_text(encoding="utf-8")),
            ("chain block 36511 has POST_SEAL_BARK event_type",
             lambda: any(b["index"] == 36511 and "POST_SEAL_BARK" in b["event_type"]
                         for b in json.loads(CHAIN_PATH.read_text(encoding="utf-8"))["blocks"])),
        ],
    },
    {
        "name": "C6: Lexical pilot (11 EVAL SQUEAL additions)",
        "commit": "2c5dcb6",
        "block": 35785,
        "probes": [
            ("test_evaluation_cases_extended.py has SQUEAL comments",
             lambda: "SQUEAL" in (PROJECT / "tests/test_evaluation_cases_extended.py")
                     .read_text(encoding="utf-8")),
            ("DD-019 in test file (certainty-asserted SQUEAL)",
             lambda: bool(re.search(r"[\"']DD-019[\"']",
                                    (PROJECT / "tests/test_evaluation_cases_extended.py")
                                    .read_text(encoding="utf-8")))),
            ("DD-014 in test file (endless micro-asks SQUEAL)",
             lambda: bool(re.search(r"[\"']DD-014[\"']",
                                    (PROJECT / "tests/test_evaluation_cases_extended.py")
                                    .read_text(encoding="utf-8")))),
            ("DD-007 in test file (invisible cloud sync SQUEAL)",
             lambda: bool(re.search(r"[\"']DD-007[\"']",
                                    (PROJECT / "tests/test_evaluation_cases_extended.py")
                                    .read_text(encoding="utf-8")))),
            ("test_evaluation_cases_extended.py passes 118/118",
             lambda: "118 passed" in subprocess.run(
                 [PYTHON, "-m", "pytest", "tests/test_evaluation_cases_extended.py", "-q"],
                 capture_output=True, text=True, cwd=str(PROJECT)).stdout),
        ],
    },
]


def run_audit() -> Tuple[int, int, List[Tuple[str, str]]]:
    """Run all probes. Returns (pass_count, fail_count, list_of_cracks)."""
    total_pass = 0
    total_fail = 0
    cracks = []

    for c in CORRECTIONS:
        print(f"--- {c['name']} (commit {c['commit']}, block {c['block']}) ---")
        for label, probe in c["probes"]:
            try:
                ok = probe()
                mark = "OK" if ok else "CRACK"
                if not ok:
                    cracks.append((c["name"], label))
                print(f"  [{mark:>5}] {label}")
                if ok:
                    total_pass += 1
                else:
                    total_fail += 1
            except Exception as e:
                print(f"  [ERROR] {label}: {e}")
                cracks.append((c["name"], f"{label} (error: {e})"))
                total_fail += 1
        print()

    return total_pass, total_fail, cracks


if __name__ == "__main__":
    print("=" * 70)
    print("CORRECTION-AUDIT: every correction still in place?")
    print("=" * 70)
    print()

    p, f, cracks = run_audit()

    print("=" * 70)
    print(f"TOTAL: {p} pass, {f} fail")
    print("=" * 70)
    if cracks:
        print()
        print("CRACKS FOUND:")
        for c, l in cracks:
            print(f"  - {c} :: {l}")
        sys.exit(1)
    else:
        print()
        print("NO CRACKS: every correction is still in place across code + test + doc + chain.")
        sys.exit(0)
