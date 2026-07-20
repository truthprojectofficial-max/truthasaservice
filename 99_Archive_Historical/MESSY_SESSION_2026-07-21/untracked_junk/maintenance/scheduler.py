"""
src.maintenance.scheduler -- CLI driver for the deterministic maintenance layer.

Usage
-----
::

    # run the daily set right now and seal one block
    python -m src.maintenance.scheduler --once --cadence daily

    # run the hourly set every 3600 s forever (for a console window, or
    # background it; on Windows prefer Task Scheduler firing --once hourly)
    python -m src.maintenance.scheduler --loop --interval 3600 --cadence hourly

    # dry run -- run the routines, write the report, but do NOT seal a block
    python -m src.maintenance.scheduler --once --cadence daily --no-seal

Deterministic. No LLM. No network. The only write per run is one sealed
maintenance block (unless --no-seal) + the report files under the
maintenance reports directory (see ``config.constants``).
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import List

from src.maintenance import health, reporter


def _run_once(cadence: str, seal: bool) -> int:
    report = reporter.run_suite(cadence, seal=seal)
    print(f"[maintenance] cadence={cadence} overall={report['overallStatus']} "
          f"routines={report['routineCount']}")
    for r in report["routines"]:
        print(f"  {r['status']:4} {r['name']:22} {r['summary']}")
    if "sealedBlockIndex" in report:
        print(f"[maintenance] sealed block #{report['sealedBlockIndex']} "
              f"hash {report['sealedBlockHash'][:16]}...")
    return 0 if report["overallStatus"] != "FAIL" else 1


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.maintenance.scheduler",
        description="Deterministic maintenance: chain verify, journal check, "
                    "vault growth, disk usage, squeal backlog, monitor sweep.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true",
                      help="run one cadence and exit")
    mode.add_argument("--loop", action="store_true",
                      help="run a cadence, sleep --interval seconds, repeat")
    parser.add_argument("--cadence", choices=list(health.CADENCES),
                        default="hourly", help="which routine set to run (hourly/daily)")
    parser.add_argument("--interval", type=int, default=3600,
                        help="seconds between runs in --loop mode (default 3600)")
    parser.add_argument("--no-seal", action="store_true",
                        help="run routines + write report, but do NOT seal a block")
    args = parser.parse_args(argv)

    seal = not args.no_seal
    if args.once:
        return _run_once(args.cadence, seal)

    # --loop
    print(f"[maintenance] loop mode: cadence={args.cadence} interval={args.interval}s")
    while True:
        try:
            _run_once(args.cadence, seal)
        except KeyboardInterrupt:
            print("[maintenance] loop interrupted by operator; exiting.")
            return 0
        except Exception as exc:  # noqa: BLE001 -- a single run failure must not kill the loop
            print(f"[maintenance] run failed: {exc}", file=sys.stderr)
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())