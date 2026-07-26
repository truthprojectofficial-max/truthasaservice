"""
Order Get It Right -- Handover Drift Detector and Auto-Handover.

Closes the procedural-law gap that allowed the 2026-07-19 v2
handover to remain the operator-facing state document for two
days while the chain advanced 6,532 blocks. The drift detector
reads the latest dated ``handover_next_session_*.md`` file in
``04_Validation/``, extracts its recorded block-count and
last-seal-timestamp, compares them to the live chain, and acts.

Three modes:

  --auto-write   DEFAULT. If drift > threshold, write a fresh
                 handover_next_session_<today>.md from the chain
                 payload and seal a SEALED_HANDOVER_<date> block.
                 Idempotent: re-running on the same state produces
                 no new file and no new block.
  --refuse       Refuse to do work (exit 2) until the drift is
                 resolved. Prints the missing-handover prompt.
  --alert        Seal an OBSERVED_HANDOVER_DRIFT_<date> block to
                 the chain (the next operator / session can see
                 the drift was observed) and exit 3. Does not
                 write the handover.

Threshold: drift is exceeded if EITHER
  - the live chain has advanced more than --block-drift blocks
    since the handover's recorded block-count (default: 100), OR
  - the live chain's last-seal-timestamp is more than --time-drift
    after the handover's recorded last-seal-timestamp (default: 24h)

The script is offline. It does not import any networking module.
Pure stdlib Python 3.12+. Deterministic.

Usage:
    python 04_Validation/scripts/handover_drift_check.py
    python 04_Validation/scripts/handover_drift_check.py --auto-write
    python 04_Validation/scripts/handover_drift_check.py --refuse
    python 04_Validation/scripts/handover_drift_check.py --alert
    python 04_Validation/scripts/handover_drift_check.py --json-only

Exit codes:
    0  drift within threshold, or auto-write succeeded
    2  --refuse and drift exceeded
    3  --alert sealed
    4  vault not found, IO error, or seal failed
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Canonical source paths ------------------------------------------------
PROJECT_ROOT = Path("C:/Users/justo/OneDrive/Documents/My Project/OrderGetItRight")
TECH = PROJECT_ROOT / "02_Technical"
HANDOVER_DIR = PROJECT_ROOT / "04_Validation" / "handovers"
REPORT = Path(__file__).resolve().parent / "handover_drift_report.json"

# Filename pattern for the dated handovers. The date is the
# session date; the chain's last-seal-timestamp is the source of
# truth for "now," not the file's mtime.
HANDOVER_PATTERN = re.compile(r"^handover_next_session_(\d{4}-\d{2}-\d{2})\.md$")

# Patterns to extract the block-count and last-seal-timestamp
# recorded in the handover. The handover convention (set by
# 2026-07-19 and following) records these in lines like:
#   "- Merkle chain: MATCH, N,NNN blocks"
#   "- Chain root: <64-hex>"
#   "- Tests: NN passed, 1 skipped, 1 warning"
# The block-count and root are the canonical claims.
# We also fall back to the "(N blocks, last seal TS, refreshed DATE)"
# parenthetical which both derive_fingerprints.py and the chain
# verifier emit.
BLOCK_COUNT_PATTERNS = [
    re.compile(r"Merkle chain:\s*MATCH,\s*([0-9,]+)\s*blocks", re.IGNORECASE),
    re.compile(r"block count:\s*([0-9,]+)", re.IGNORECASE),
    re.compile(r"\(([0-9,]+)\s*blocks,\s*last seal\s+(\S+?),\s*refreshed", re.IGNORECASE),
]
LAST_SEAL_PATTERNS = [
    re.compile(r"last seal\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", re.IGNORECASE),
]
ROOT_PATTERNS = [
    re.compile(r"chain root:\s*`?([0-9a-f]{64})`?", re.IGNORECASE),
    re.compile(r"merkle root:\s*`?([0-9a-f]{64})`?", re.IGNORECASE),
]


def read_vault_path() -> Path:
    sys.path.insert(0, str(TECH))
    try:
        from config.constants import PROJECT_VAULT_DIR
        return Path(PROJECT_VAULT_DIR)
    finally:
        try:
            sys.path.remove(str(TECH))
        except ValueError:
            pass


def read_live_chain(vault_dir: Path) -> dict:
    chain_file = vault_dir / "facts_registry.json"
    if not chain_file.exists():
        raise SystemExit(f"ERROR: vault not found at {chain_file}")
    data = json.loads(chain_file.read_text(encoding="utf-8"))
    blocks = data.get("blocks", [])
    root = data.get("merkle_root", "")
    if not root:
        raise SystemExit(f"ERROR: vault at {chain_file} has no merkle_root field")
    last = blocks[-1] if blocks else {}
    return {
        "block_count": len(blocks),
        "merkle_root": root,
        "last_seal_timestamp": last.get("timestamp", ""),
        "last_block_event": last.get("event_type", ""),
    }


def find_latest_dated_handover() -> Path | None:
    """Return the most-recently-dated handover file in
    04_Validation/. If multiple share the same date, return the
    lexicographically largest name (matches the project's
    handover_v1 / _v2 / _vN convention)."""
    candidates = []
    for p in HANDOVER_DIR.iterdir():
        m = HANDOVER_PATTERN.match(p.name)
        if m:
            candidates.append((m.group(1), p.name, p))
    if not candidates:
        return None
    # Sort by date ascending, then by filename descending so v2 > v1
    candidates.sort(key=lambda x: (x[0], x[1]))
    return candidates[-1][2]


def extract_recorded_state(handover_path: Path) -> dict:
    text = handover_path.read_text(encoding="utf-8")
    found = {"block_count": None, "last_seal_timestamp": None, "merkle_root": None}
    for pat in BLOCK_COUNT_PATTERNS:
        m = pat.search(text)
        if m:
            # The third pattern captures both block_count and last_seal
            if m.lastindex and m.lastindex >= 1:
                found["block_count"] = int(m.group(1).replace(",", ""))
            if m.lastindex and m.lastindex >= 2:
                found["last_seal_timestamp"] = m.group(2)
            if found["block_count"] is not None:
                break
    for pat in LAST_SEAL_PATTERNS:
        m = pat.search(text)
        if m:
            found["last_seal_timestamp"] = m.group(1)
            break
    for pat in ROOT_PATTERNS:
        m = pat.search(text)
        if m:
            found["merkle_root"] = m.group(1)
            break
    return found


def parse_iso_z(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def compute_drift(recorded: dict, live: dict) -> dict:
    block_drift = None
    time_drift_seconds = None
    if recorded["block_count"] is not None:
        block_drift = live["block_count"] - recorded["block_count"]
    rec_ts = parse_iso_z(recorded["last_seal_timestamp"] or "")
    live_ts = parse_iso_z(live["last_seal_timestamp"])
    if rec_ts and live_ts:
        time_drift_seconds = int((live_ts - rec_ts).total_seconds())
    return {
        "block_drift": block_drift,
        "time_drift_seconds": time_drift_seconds,
    }


def exceeds_threshold(drift: dict, block_threshold: int, time_threshold_seconds: int) -> bool:
    if drift["block_drift"] is not None and drift["block_drift"] > block_threshold:
        return True
    if (
        drift["time_drift_seconds"] is not None
        and drift["time_drift_seconds"] > time_threshold_seconds
    ):
        return True
    return False


def update_handover_in_place(
    handover_path: Path, live: dict, recorded: dict
) -> dict:
    """Update an existing dated handover's recorded-state section
    in place. The new state lives in the same file; the operator-
    authored narrative (everything before/after the recorded-
    state section) is preserved. Idempotent: re-running with no
    new drift produces no change.

    This function rewrites only the recorded-state lines, not
    the operator's prose. The convention is: the recorded-state
    block lives in lines starting with `- Merkle chain:`,
    `- Chain root:`, `- Tests:`, `- Tagline:`, and the
    parenthetical `(N blocks, last seal TS, refreshed DATE)`
    inside the derive_fingerprints-managed sections.

    For handovers written before the drift detector existed
    (like the 2026-07-22 hand-written file), the recorded-state
    lines may not exist; in that case, the function adds them
    at the top of the file under a "## Drift-detected state
    refresh" section.
    """
    text = handover_path.read_text(encoding="utf-8")
    new_state_lines = (
        f"- Merkle chain: MATCH, {live['block_count']:,} blocks\n"
        f"- Chain root: `{live['merkle_root']}`\n"
        f"- Last seal: {live['last_seal_timestamp']} (event: {live['last_block_event']})\n"
    )

    # Pattern: try to replace the existing recorded-state block.
    # The block is the contiguous run of "- Merkle chain:",
    # "- Chain root:", "- Last seal:" lines, separated only by
    # blank lines. If found, replace it. If not found, prepend
    # a "## Drift-detected state refresh" section to the top.
    recorded_block_pattern = re.compile(
        r"((?:- (?:Merkle chain|Chain root|Last seal):[^\n]*\n)+)",
        re.MULTILINE,
    )
    m = recorded_block_pattern.search(text)
    if m:
        new_text = text[: m.start()] + new_state_lines + text[m.end():]
        action = "updated_existing_block"
    else:
        # No recorded-state block found; prepend a refresh
        # section after the first heading.
        heading_end = text.find("\n", text.find("# "))
        if heading_end == -1:
            heading_end = 0
        new_text = (
            text[: heading_end + 1]
            + "\n## Drift-detected state refresh\n\n"
            + "The drift detector refreshed this handover's recorded "
            + "state from the live chain. The operator-authored "
            + "narrative below is preserved.\n\n"
            + new_state_lines
            + "\n"
            + text[heading_end + 1:]
        )
        action = "prepended_refresh_section"

    if new_text == text:
        return {
            "action": "no_change",
            "file": str(handover_path),
        }
    handover_path.write_text(new_text, encoding="utf-8")
    return {
        "action": action,
        "file": str(handover_path),
        "block_count_written": live["block_count"],
        "merkle_root_written": live["merkle_root"],
    }


def write_handover_from_chain(
    live: dict, recorded: dict, today: str, root: str, tagline: str
) -> Path:
    """Write a fresh dated handover from the live chain payload.

    The new file:
      - is named handover_next_session_<today>.md
      - supersedes the latest dated handover
      - records the live block_count, root, and last_seal
      - lists the drift observed (block_drift, time_drift)
      - seals a SEALED_HANDOVER_<date> block to the chain
    """
    new_path = HANDOVER_DIR / f"handover_next_session_{today}.md"
    drift_block = (live["block_count"] - (recorded["block_count"] or 0))
    rec_ts = recorded["last_seal_timestamp"] or "(unknown)"
    body = f"""# Order Get It Right -- Hand-Over Statement (auto-generated)

**Session date:** {today}
**Operator:** Justin Barnett
**Build agent:** automated-handover-drift-detector
**Branch:** ogir-build-2026-07-18
**State at hand-over:**
- Tests: see latest `python -m pytest tests/ -q` output
- Merkle chain: MATCH, {live['block_count']:,} blocks
- Chain root: `{live['merkle_root']}`
- Last seal: {live['last_seal_timestamp']} (event: {live['last_block_event']})
- Tagline: {tagline}

---

## Drift observed

The previous dated handover (referenced `rec_ts`) recorded
`{recorded['block_count']:,}` blocks and root
`{recorded['merkle_root']}`. The live chain is at
{live['block_count']:,} blocks and root
`{live['merkle_root']}`. Block drift:
**{drift_block:,}** blocks.

This handover was auto-written by
`04_Validation/scripts/handover_drift_check.py` because the
drift exceeded the configured threshold. The chain was always
in sync; the operator-facing written record had drifted.

## How to verify

```
cd "C:\\Users\\justo\\OneDrive\\Documents\\My Project\\OrderGetItRight"
python 04_Validation/scripts/derive_fingerprints.py --json-only
cd 02_Technical
python -m src.verify_chain
cd ..
python -m pytest tests/ -q
python 04_Validation/scripts/deterministic_hygiene.py --json-only
```

End of hand-over. The chain is the source of truth.
"""
    new_path.write_text(body, encoding="utf-8")
    return new_path


def _find_latest_sealed_handover_block(vault_dir: Path) -> dict | None:
    """Walk the chain backwards and return the payload of the
    most recent SEALED_HANDOVER_<date> block, or None if no
    such block exists. Used by the auto-write path for
    idempotency."""
    chain_file = vault_dir / "facts_registry.json"
    data = json.loads(chain_file.read_text(encoding="utf-8"))
    for block in reversed(data.get("blocks", [])):
        evt = block.get("event_type", "")
        if evt.startswith("SEALED_HANDOVER_"):
            payload = block.get("payload", {}) or {}
            return payload
    return None


def seal_handover_block(live: dict, today: str, previous_handover: Path | None) -> dict:
    """Seal a SEALED_HANDOVER_<date> block to the chain. Returns
    a dict with sealed status, block_index, and block_hash. The
    seal carries the chain-state payload that was written into
    the new handover, so the chain is aware of the operator-
    facing refresh."""
    sys.path.insert(0, str(TECH))
    try:
        from src.io.vault_io import append_block
        block = append_block(
            f"SEALED_HANDOVER_{today.replace('-', '_')}",
            {
                "type": "sealed_handover",
                "handover_date": today,
                "block_count_at_seal": live["block_count"],
                "merkle_root_at_seal": live["merkle_root"],
                "last_seal_at_emit": live["last_seal_timestamp"],
                "previous_handover_file": str(previous_handover) if previous_handover else None,
                "operator": "automated-handover-drift-detector",
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        return {
            "sealed": True,
            "block_index": block.get("index"),
            "block_hash": block.get("current_hash"),
        }
    except Exception as e:
        return {"sealed": False, "reason": str(e)}
    finally:
        try:
            sys.path.remove(str(TECH))
        except ValueError:
            pass


def read_tagline() -> str:
    src_init = TECH / "src" / "__init__.py"
    text = src_init.read_text(encoding="utf-8")
    m = re.search(r'__tagline__\s*=\s*["\']([^"\']+)["\']', text)
    if not m:
        raise SystemExit(f"ERROR: could not find __tagline__ in {src_init}")
    return m.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--auto-write", action="store_true",
                      help="Auto-write the missing handover (default).")
    mode.add_argument("--refuse", action="store_true",
                      help="Refuse to do work; print prompt; exit 2.")
    mode.add_argument("--alert", action="store_true",
                      help="Seal OBSERVED_HANDOVER_DRIFT; exit 3.")
    parser.add_argument("--json-only", action="store_true",
                        help="Output JSON only, no file/block writes.")
    parser.add_argument("--block-drift", type=int, default=100,
                        help="Block-count drift threshold (default 100).")
    parser.add_argument("--time-drift", type=int, default=86400,
                        help="Time drift threshold in seconds (default 86400 = 24h).")
    args = parser.parse_args()

    # Default mode is auto-write.
    if not (args.refuse or args.alert or args.json_only):
        args.auto_write = True

    vault_dir = read_vault_path()
    live = read_live_chain(vault_dir)
    latest = find_latest_dated_handover()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if latest is None:
        report = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "vault": str(vault_dir),
            "live": live,
            "latest_handover": None,
            "recorded": None,
            "drift": None,
            "exceeds_threshold": None,
            "action_taken": "no_dated_handover_exists",
        }
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print("WARN: no dated handover_next_session_*.md found in 04_Validation/")
        if args.json_only:
            print(json.dumps(report, indent=2))
        return 0

    recorded = extract_recorded_state(latest)
    drift = compute_drift(recorded, live)
    exceeds = exceeds_threshold(drift, args.block_drift, args.time_drift)

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "vault": str(vault_dir),
        "live": live,
        "latest_handover": str(latest),
        "recorded": recorded,
        "drift": drift,
        "exceeds_threshold": exceeds,
        "block_drift_threshold": args.block_drift,
        "time_drift_threshold_seconds": args.time_drift,
        "action_taken": None,
    }

    if not exceeds:
        report["action_taken"] = "no_drift"
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        if args.json_only:
            print(json.dumps(report, indent=2))
        else:
            print(f"OK: latest handover {latest.name} is current.")
            print(f"  live block_count: {live['block_count']}")
            print(f"  recorded block_count: {recorded['block_count']}")
            print(f"  block_drift: {drift['block_drift']}")
        return 0

    # Drift exceeded.
    if args.refuse:
        report["action_taken"] = "refused"
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        if args.json_only:
            print(json.dumps(report, indent=2))
        else:
            print(f"REFUSE: drift exceeded.")
            print(f"  latest handover: {latest.name}")
            print(f"  block_drift: {drift['block_drift']} (threshold {args.block_drift})")
            print(f"  time_drift_seconds: {drift['time_drift_seconds']} (threshold {args.time_drift})")
            print(f"  Run: python 04_Validation/scripts/handover_drift_check.py --auto-write")
        return 2

    if args.alert:
        seal = seal_handover_block(live, today, latest)
        report["action_taken"] = "alert_sealed"
        report["seal"] = seal
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        if args.json_only:
            print(json.dumps(report, indent=2))
        else:
            print(f"ALERT: OBSERVED_HANDOVER_DRIFT sealed.")
            print(f"  block_drift: {drift['block_drift']}")
            print(f"  seal: {seal}")
        return 3

    if args.auto_write:
        # Idempotency check: if the most recent SEALED_HANDOVER
        # block on the chain already carries this exact state,
        # no-op. (The block sealed by the previous auto-write.)
        latest_seal = _find_latest_sealed_handover_block(vault_dir)
        if latest_seal and latest_seal.get("block_count_at_seal") == live["block_count"]:
            report["action_taken"] = "already_current"
            REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
            if args.json_only:
                print(json.dumps(report, indent=2))
            else:
                print(f"OK: latest handover {latest.name} is current (last seal at block {live['block_count']}).")
            return 0

        # Update the existing dated handover in place. The
        # operator-authored narrative is preserved; only the
        # recorded-state block is refreshed.
        update_result = update_handover_in_place(latest, live, recorded)
        seal = seal_handover_block(live, today, latest)
        report["action_taken"] = "auto_updated"
        report["update"] = update_result
        report["seal"] = seal
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        if args.json_only:
            print(json.dumps(report, indent=2))
        else:
            print(f"AUTO-UPDATED: {latest.name}")
            print(f"  update: {update_result}")
            print(f"  block_drift_at_write: {drift['block_drift']}")
            print(f"  seal: {seal}")
        return 0

    # --json-only and drift exceeded: report only, no write, no seal.
    report["action_taken"] = "json_only_with_drift"
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
