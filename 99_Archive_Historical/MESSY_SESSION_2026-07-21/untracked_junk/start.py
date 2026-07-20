#!/usr/bin/env python3
"""
Order Get It Right -- one-click launcher.

HOW TO USE
----------
1. Open a terminal (PowerShell or Command Prompt).
2. Make sure you are in the project root (the folder with this file):
       cd c:\\OrderGetItRight
3. Run:
       .\\start.py
4. Pick a number from the menu and press Enter.

The launcher finds the project root from its own location, so you can also
just double-click start.py (it opens a console and stays open).

Deterministic. No LLM. No network. Every choice runs a real project entry
point via ``python -m <module>`` with the working directory set to
``02_Technical``.
"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


# --- locate the project -------------------------------------------------------
HERE = Path(__file__).resolve().parent
TECH = HERE / "02_Technical"

if not (TECH / "src" / "agents" / "orchestrator.py").exists():
    if (HERE / "src" / "agents" / "orchestrator.py").exists():
        TECH = HERE
    else:
        print("ERROR: could not find 02_Technical/src/agents/orchestrator.py")
        print("       start.py must live in the project root or in 02_Technical.")
        input("\nPress Enter to exit...")
        sys.exit(2)

PY = sys.executable


def _run(args: list) -> int:
    """Run a subprocess in 02_Technical, streaming output to this console."""
    print("\n" + "=" * 72)
    print("  running: " + " ".join(args))
    print("  cwd    : " + str(TECH))
    print("=" * 72 + "\n")
    try:
        return subprocess.call(args, cwd=str(TECH))
    except KeyboardInterrupt:
        print("\n[launcher] interrupted by operator.")
        return 130


# --- the menu ---------------------------------------------------------------
MENU = [
    ("Run a document audit (inbox -> outbox)",
     [PY, "-m", "src.audit_cli", "--inbox", "data/inbox", "--outbox", "data/outbox"],
     "Processes every .txt/.docx/.pdf in 02_Technical/data/inbox and writes\n"
     "    Markdown/PDF/DOCX reports to 02_Technical/data/outbox. Main use."),

    ("Run the end-to-end demo job (sample evidence)",
     [PY, "-m", "src.agents.orchestrator"],
     "Runs the full 4-gate pipeline on a built-in sample (Audio Pro W-Gen)\n"
     "    and prints the JSON verdict. Quick 'is it alive' check."),

    ("Verify the whole audit chain (MATCH / BROKEN)",
     [PY, "-m", "src.verify_chain"],
     "Re-derives the Merkle root from every sealed block and compares it to\n"
     "    the recorded root. ~212 ms for 27,437 blocks. The trust anchor."),

    ("Run HOURLY maintenance health check",
     [PY, "-m", "src.maintenance.scheduler", "--once", "--cadence", "hourly", "--no-seal"],
     "4 routines (~0.3 s): chain integrity, job journal, vault growth,\n"
     "    squeal backlog. No block sealed."),

    ("Run DAILY maintenance health check (seals a block)",
     [PY, "-m", "src.maintenance.scheduler", "--once", "--cadence", "daily"],
     "All 7 routines (~10 s) and seals one maintenance block to the chain."),

    ("Onyx CLI (third-party surface: audit, verify, affidavit, ledger...)",
     [PY, "-m", "src.onyx_cli", "--help"],
     "Prints the Onyx CLI help -- the sub-commands a third party uses:\n"
     "    audit, seal, verify, affidavit, research, hunt, normalize,\n"
     "    compute, compare-to-spec, draft, ledger."),

    ("Monitor agent oversight briefing",
     [PY, "-m", "src.agents.monitor_agent"],
     "MonitorAgent briefing: chain check, hide-pattern scan, unexplained-\n"
     "    verdict cross-check. Read before any legal use."),

    ("Run the test suite (pytest)",
     [PY, "-m", "pytest", "tests", "-q"],
     "Runs all 23 test files. Green = the project still works as specified."),

    ("Install the Windows Task Scheduler (hands-off maintenance)",
     ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
      "-File", str(HERE / "scripts" / "install_scheduler.ps1")],
     "Creates the OGIR-Maintenance-Hourly and OGIR-Maintenance-Daily tasks.\n"
     "    After this the maintenance layer runs itself, no console needed."),

    ("Quit",
     None,
     None),
]


def _banner() -> None:
    print("=" * 72)
    print("   ORDER GET IT RIGHT  --  v1.0.0")
    print("   Deterministic business audit & valuation engine")
    print("   Operator of record: Justin Barnett")
    print("=" * 72)
    print("  No LLM. No network. Tamper-evident chain. Same input -> same verdict.")
    print("-" * 72)
    print("  CHOOSE A TASK:\n")


def main() -> int:
    while True:
        _banner()
        for i, (title, _args, _desc) in enumerate(MENU, start=1):
            print("   %2d. %s" % (i, title))
        print()

        try:
            choice = input("  Enter number (or q to quit): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if choice in ("q", "quit", "exit", ""):
            return 0

        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU)):
            print("  [!] Not a valid choice. Press Enter to try again.")
            input()
            continue

        idx = int(choice) - 1
        title, args, desc = MENU[idx]

        if args is None:  # Quit
            return 0

        print("\n  >> " + title)
        if desc:
            print("     " + desc)
        try:
            input("\n  Press Enter to launch (Ctrl+C to cancel)...")
        except (EOFError, KeyboardInterrupt):
            print("  [cancelled]\n")
            continue

        _run(args)

        print("\n" + "-" * 72)
        try:
            input("  Done. Press Enter to return to the menu (Ctrl+C to quit)...")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[launcher] bye.")
        sys.exit(0)