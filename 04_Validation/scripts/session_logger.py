"""
OGIR Live Session Logger

Writes a durable, timestamped log of every agent action as it happens,
so the session record does NOT depend on the terminal scrollback buffer
(which truncates). The terminal is a display device; this file is the
record.

WHY THIS EXISTS:
  The 2026-07-27 session-3 transcript was captured as ``# Todos.txt``
  (106 KB, 1902 lines) — a raw paste of the terminal scrollback. It was
  truncated by the terminal buffer limit and had gaps where opencode
  collapsed long outputs ("Click to expand"). The operator had to copy
  as he went. This script replaces that pattern: the agent appends to a
  file as it works, so the full record is on disk at session end.

USAGE (by the agent, via bash):
  The agent calls this script with a subcommand:

  # Start a session (creates the file, writes the header)
  python 04_Validation/scripts/session_logger.py start \\
      --agent opencode --model "ollama/glm-5.2:cloud" \\
      --chain-blocks 41027 --tests-passed 408

  # Log an action (append a timestamped entry)
  python 04_Validation/scripts/session_logger.py action \\
      --type webfetch --summary "Fetched firecrawl.dev homepage" \\
      --detail "Saved raw to 04_Validation/logs/fetched/firecrawl-dev-2026-07-27.md"

  # Log a correction (operator corrected the agent)
  python 04_Validation/scripts/session_logger.py correction \\
      --summary "Stop-when-done: agent tried to sign off with items remaining" \\
      --detail "Operator said: WHAT PUSH? MORE WORK FOR SURE"

  # Log a decision (agent made a choice)
  python 04_Validation/scripts/session_logger.py decision \\
      --summary "Implemented DD-070 + DD-071 with R6/R7 gates" \\
      --detail "Chose 400-char forward window for R7 evidence gate"

  # Log a missed-task (agent recognized a missed task from a prior session)
  python 04_Validation/scripts/session_logger.py missed \\
      --summary "Firecrawl data fetched but not persisted in session 3" \\
      --detail "Context lost on session end; had to re-fetch in session 4"

  # End a session (writes the footer)
  python 04_Validation/scripts/session_logger.py end \\
      --blocks-sealed 11 --tests-passed 408 --pushed

OUTPUT:
  04_Validation/logs/sessions/session-<YYYY-MM-DD>-<HHMMSS>.md
  One file per session. Markdown. Append-only.

CONTRACT:
  - Out-of-runtime (lives in 04_Validation/scripts/). No boundary issue.
  - Does NOT seal to the chain. The chain is the trust anchor; this log
    is the operational record for the operator's review.
  - Pure stdlib. No network. Deterministic timestamps (UTC).
  - Append-only: never overwrites a prior session's log.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Resolve paths relative to the project root (parent of 04_Validation)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "04_Validation" / "logs" / "sessions"

# A single session log file, set by `start` and reused by subsequent
# commands in the same session. Stored in an env var so subcommands
# pick it up across separate process invocations.
_SESSION_FILE_ENV = "OGIR_SESSION_LOG_FILE"


def _utc_now() -> str:
    """Deterministic UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _utc_time_for_filename() -> str:
    return datetime.now(timezone.utc).strftime("%H%M%S")


def _get_session_file() -> Path:
    """Get the current session log file from the env var."""
    path_str = os.environ.get(_SESSION_FILE_ENV, "")
    if not path_str:
        # Fallback: find the most recent session log created today.
        if LOG_DIR.exists():
            today_logs = sorted(
                LOG_DIR.glob(f"session-{_utc_date()}-*.md"),
                reverse=True,
            )
            if today_logs:
                return today_logs[0]
        # No session started — create one on the fly.
        return _start_file()
    p = Path(path_str)
    if not p.exists():
        # The env var is stale; start a new file.
        return _start_file()
    return p


def _start_file() -> Path:
    """Create a new session log file and return its path."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"session-{_utc_date()}-{_utc_time_for_filename()}.md"
    path = LOG_DIR / filename
    # Set the env var so subsequent commands in this shell find it.
    os.environ[_SESSION_FILE_ENV] = str(path)
    return path


def cmd_start(args: argparse.Namespace) -> int:
    path = _start_file()
    ts = _utc_now()
    lines = [
        f"# OGIR Session Log — {ts}",
        "",
        f"- **Agent:** {args.agent}",
        f"- **Model:** {args.model}",
        f"- **Session start:** {ts}",
        f"- **Chain blocks at start:** {args.chain_blocks}",
        f"- **Tests passed at start:** {args.tests_passed}",
        "",
        "---",
        "",
        "## Actions",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(str(path))
    # Echo the env var assignment so the operator/agent can capture it
    # if running in a fresh shell each time.
    print(f"set { _SESSION_FILE_ENV }={path}")
    return 0


def _append_entry(
    entry_type: str,
    summary: str,
    detail: Optional[str] = None,
) -> int:
    path = _get_session_file()
    ts = _utc_now()
    block = ["", f"### [{ts}] {entry_type.upper()}", "", f"**{summary}**"]
    if detail:
        block.append("")
        block.append(detail)
    block.append("")
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(block) + "\n")
    print(f"logged {entry_type} -> {path.name}")
    return 0


def cmd_action(args: argparse.Namespace) -> int:
    return _append_entry(
        f"action: {args.type}", args.summary, args.detail
    )


def cmd_correction(args: argparse.Namespace) -> int:
    return _append_entry("correction", args.summary, args.detail)


def cmd_decision(args: argparse.Namespace) -> int:
    return _append_entry("decision", args.summary, args.detail)


def cmd_missed(args: argparse.Namespace) -> int:
    return _append_entry("missed-task", args.summary, args.detail)


def cmd_end(args: argparse.Namespace) -> int:
    path = _get_session_file()
    ts = _utc_now()
    lines = [
        "",
        "---",
        "",
        "## Session end",
        "",
        f"- **Session end:** {ts}",
        f"- **Blocks sealed:** {args.blocks_sealed}",
        f"- **Tests passed:** {args.tests_passed}",
        f"- **Pushed to origin:** {args.pushed}",
        "",
    ]
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"session ended -> {path.name}")
    # Clear the env var so the next `start` creates a fresh file.
    os.environ.pop(_SESSION_FILE_ENV, None)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OGIR live session logger. Appends a durable, "
        "timestamped record of agent actions to a file so the session "
        "does not depend on the terminal scrollback buffer."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Start a new session log")
    p_start.add_argument("--agent", required=True, help="Agent name")
    p_start.add_argument("--model", required=True, help="Model id")
    p_start.add_argument(
        "--chain-blocks", type=int, default=0, help="Chain block count"
    )
    p_start.add_argument(
        "--tests-passed", type=int, default=0, help="Tests passed count"
    )
    p_start.set_defaults(func=cmd_start)

    p_action = sub.add_parser("action", help="Log an agent action")
    p_action.add_argument(
        "--type", required=True, help="Action type (webfetch, edit, seal, etc.)"
    )
    p_action.add_argument("--summary", required=True, help="One-line summary")
    p_action.add_argument("--detail", default=None, help="Optional detail")
    p_action.set_defaults(func=cmd_action)

    p_corr = sub.add_parser("correction", help="Log an operator correction")
    p_corr.add_argument("--summary", required=True, help="One-line summary")
    p_corr.add_argument("--detail", default=None, help="Optional detail")
    p_corr.set_defaults(func=cmd_correction)

    p_dec = sub.add_parser("decision", help="Log an agent decision")
    p_dec.add_argument("--summary", required=True, help="One-line summary")
    p_dec.add_argument("--detail", default=None, help="Optional detail")
    p_dec.set_defaults(func=cmd_decision)

    p_missed = sub.add_parser("missed", help="Log a recognized missed task")
    p_missed.add_argument("--summary", required=True, help="One-line summary")
    p_missed.add_argument("--detail", default=None, help="Optional detail")
    p_missed.set_defaults(func=cmd_missed)

    p_end = sub.add_parser("end", help="End the session log")
    p_end.add_argument(
        "--blocks-sealed", type=int, default=0, help="Blocks sealed this session"
    )
    p_end.add_argument(
        "--tests-passed", type=int, default=0, help="Tests passed at end"
    )
    p_end.add_argument(
        "--pushed",
        action="store_true",
        default=False,
        help="Whether the session was pushed to origin",
    )
    p_end.set_defaults(func=cmd_end)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())