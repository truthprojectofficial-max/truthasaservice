"""
OGIR Operator Todo Auto-Generator

Reads the sealed blocks from the current session + the open items from
the last handover log block, and generates a draft OPERATOR_TODO file.

This is out-of-runtime tooling (lives in 04_Validation/scripts/). It
reads the vault JSON directly (it is not in 02_Technical, so the
boundary does not apply). It does NOT seal to the chain.

Usage:
    python 04_Validation/scripts/generate_operator_todo.py

Output:
    Prints a draft todo to stdout. The agent reviews it, edits it,
    and writes the final file to 04_Validation/operator_completions/.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Resolve paths relative to the project root (parent of 04_Validation)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
VAULT_FILE = PROJECT_ROOT / "03_Vault" / "facts_registry.json"
HANDOVER_FILE = (
    PROJECT_ROOT
    / "04_Validation"
    / "handovers"
    / "HANDOVER_LOG.md"
)


def _load_blocks() -> List[Dict[str, Any]]:
    """Load all blocks from the vault."""
    if not VAULT_FILE.exists():
        print(f"ERROR: vault not found at {VAULT_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(VAULT_FILE, "r", encoding="utf-8") as f:
        registry = json.load(f)
    return registry.get("blocks", [])


def _find_session_blocks(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find the SIGN_ON and SIGN_OFF blocks for the current session.

    Returns a dict with:
        sign_on_index: int
        sign_off_index: int or None
        session_blocks: list of blocks between sign_on and sign_off (or end)
    """
    sign_on_index = None
    sign_off_index = None

    # Walk backwards to find the last SIGN_ON
    for i in range(len(blocks) - 1, -1, -1):
        et = blocks[i].get("event_type", "")
        if "SIGN_ON" in et and "OPENCODE" in et:
            sign_on_index = i
            break

    if sign_on_index is None:
        return {
            "sign_on_index": -1,
            "sign_off_index": None,
            "session_blocks": [],
        }

    # Walk forward from SIGN_ON to find SIGN_OFF
    for i in range(sign_on_index + 1, len(blocks)):
        et = blocks[i].get("event_type", "")
        if "SIGN_OFF" in et and "OPENCODE" in et:
            sign_off_index = i
            break

    end = sign_off_index if sign_off_index is not None else len(blocks)
    session_blocks = blocks[sign_on_index:end]

    return {
        "sign_on_index": sign_on_index,
        "sign_off_index": sign_off_index,
        "session_blocks": session_blocks,
    }


def _summarize_blocks(session_blocks: List[Dict[str, Any]]) -> List[str]:
    """Summarize the event types sealed in this session."""
    summaries = []
    for block in session_blocks:
        et = block.get("event_type", "UNKNOWN")
        idx = block.get("index", "?")
        summaries.append(f"- Block {idx}: {et}")
    return summaries


def _extract_open_items_from_handover() -> List[str]:
    """Extract the 'What's open (operator action only)' items from the
    last handover block in HANDOVER_LOG.md.
    """
    if not HANDOVER_FILE.exists():
        return ["(handover log not found)"]

    content = HANDOVER_FILE.read_text(encoding="utf-8")

    # Find the last session block
    sessions = re.split(r"\n## Session:", content)
    if len(sessions) < 2:
        return ["(no session blocks found in handover)"]

    last_session = sessions[-1]

    # Extract "What's open (operator action only)" section
    match = re.search(
        r"### What's open \(operator action only\):(.+?)(?:###|$)",
        last_session,
        re.DOTALL,
    )
    if not match:
        return ["(no open items section found)"]

    items_text = match.group(1).strip()
    items = [
        line.strip().lstrip("- ").strip()
        for line in items_text.split("\n")
        if line.strip().startswith("-")
    ]
    return items if items else ["(no items listed)"]


def _generate_todo() -> str:
    """Generate the draft operator todo."""
    blocks = _load_blocks()
    session = _find_session_blocks(blocks)
    session_blocks = session["session_blocks"]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    chain_count = len(blocks)

    # Summarize what was sealed
    sealed_summary = _summarize_blocks(session_blocks)
    blocks_sealed = len(session_blocks)

    # Extract open items
    open_items = _extract_open_items_from_handover()

    # Build the draft
    lines = []
    lines.append("# OPERATOR TODO — What you need to do, in order")
    lines.append("")
    lines.append(
        f"> Auto-generated draft {now} from {blocks_sealed} sealed blocks. "
        f"Chain at {chain_count}. The agent reviews and finalizes this."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## What was sealed this session")
    lines.append("")
    for s in sealed_summary:
        lines.append(s)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Open items (operator action only)")
    lines.append("")
    for item in open_items:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## What the next agent should do")
    lines.append("")
    lines.append(
        "- Sign on (verify chain, read handover, read INDEX, run tests, "
        "seal SIGN_ON)."
    )
    lines.append(
        "- Read this file for the prioritized list. Do NOT jump to "
        "project work without checking priorities first."
    )
    lines.append(
        "- Check 04_Validation/operator_completions/OPERATOR_TODO for "
        "the full prioritized list."
    )
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(_generate_todo())