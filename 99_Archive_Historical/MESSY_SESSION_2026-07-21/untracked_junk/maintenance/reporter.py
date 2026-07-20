"""
src.maintenance.reporter -- run a cadence, write the report, seal the block.

This is the only part of the maintenance layer that WRITES:

1. It runs the cadence's routines (read-only checks) and collects results.
2. It writes a ``.md`` human report and a ``.json`` machine report under
   the maintenance reports directory (see ``config.constants``).
3. It updates a single ``state.json`` (the delta anchor for next run).
4. It seals exactly ONE ``MAINTENANCE_<CADENCE>_<ts>`` block to the chain,
   whose payload is the full report summary. This is the audit trail.
5. On any FAIL routine, it also drops a ``maintenance-fault-*.json`` file
   in the Squeal directory so the MonitorAgent's next sweep sees it.

It never edits a verdict, never deletes a block, never mutates history.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from config.constants import (
    PROJECT_MAINTENANCE_REPORTS_DIR,
    PROJECT_ROOT,
    PROJECT_SQUEAL_DIR,
)
from src.io import vault_io
from src.maintenance import health

REPORTS_DIR = Path(PROJECT_MAINTENANCE_REPORTS_DIR)
STATE_PATH = REPORTS_DIR / "state.json"


def run_suite(cadence: str, seal: bool = True) -> Dict[str, Any]:
    """Run a cadence's routines, write reports, seal one block."""
    if cadence not in health.CADENCES:
        raise ValueError(f"unknown cadence {cadence!r}; choose from {list(health.CADENCES)}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    state = _load_state()

    started = datetime.now(timezone.utc)
    routine_names = health.CADENCES[cadence]
    results: List[Dict[str, Any]] = []
    for name in routine_names:
        try:
            results.append(health.run_routine(name, state))
        except Exception as exc:  # noqa: BLE001
            results.append({
                "name": name, "status": "FAIL",
                "summary": f"routine raised: {exc}",
                "detail": {"error": repr(exc)},
            })

    overall = _overall_status(results)
    finished = datetime.now(timezone.utc)
    report = {
        "cadence": cadence,
        "startedAt": started.isoformat(),
        "finishedAt": finished.isoformat(),
        "overallStatus": overall,
        "routines": results,
        "routineCount": len(results),
    }

    ts = started.strftime("%Y-%m-%dT%H-%M-%SZ")
    md_path = REPORTS_DIR / f"maintenance-{cadence}-{ts}.md"
    json_path = REPORTS_DIR / f"maintenance-{cadence}-{ts}.json"
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    report["reportPath"] = md_path.name
    report["reportJson"] = json_path.name

    _save_state(_derive_state(results))

    if overall == "FAIL":
        _write_fault_file(report)

    if seal:
        event_type = f"MAINTENANCE_{cadence.upper()}_{ts}"
        seal_payload = {
            "cadence": cadence,
            "overallStatus": overall,
            "routineCount": len(results),
            "reportFile": md_path.name,
            "routineStatuses": {r["name"]: r["status"] for r in results},
        }
        block = vault_io.append_block(event_type, seal_payload)
        report["sealedBlockIndex"] = block.get("index")
        report["sealedBlockHash"] = block.get("current_hash")

    return report

# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _overall_status(results: List[Dict[str, Any]]) -> str:
    statuses = [r["status"] for r in results]
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"


def _load_state() -> Dict[str, Any]:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def _save_state(state: Dict[str, Any]) -> None:
    try:
        STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        pass


def _derive_state(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract values the next run needs for delta comparisons."""
    state: Dict[str, Any] = {}
    for r in results:
        d = r.get("detail", {})
        if r["name"] == "vault_growth" and "blockCount" in d:
            state["vault_growth_block_count"] = d["blockCount"]
        if r["name"] == "constants_checksum" and "sha256" in d:
            state["constants_checksum"] = d["sha256"]
    return state


def _write_fault_file(report: Dict[str, Any]) -> None:
    squeal_dir = Path(PROJECT_SQUEAL_DIR)
    squeal_dir.mkdir(parents=True, exist_ok=True)
    ts = report["startedAt"].replace(":", "-").replace(".", "-")
    failed = [r for r in report["routines"] if r["status"] == "FAIL"]
    payload = {
        "timestamp": report["startedAt"],
        "source": "maintenance",
        "cadence": report["cadence"],
        "overallStatus": report["overallStatus"],
        "failedRoutines": [{"name": r["name"], "summary": r["summary"]} for r in failed],
        "recommendation": "ESCALATE_TO_OPERATOR",
    }
    path = squeal_dir / f"maintenance-fault-{ts}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Maintenance Report -- {report['cadence']}")
    lines.append("")
    lines.append(f"- Started:  {report['startedAt']}")
    lines.append(f"- Finished: {report['finishedAt']}")
    lines.append(f"- Overall:  **{report['overallStatus']}**")
    lines.append(f"- Routines: {report['routineCount']}")
    lines.append("")
    lines.append("| Routine | Status | Summary |")
    lines.append("|---|---|---|")
    for r in report["routines"]:
        lines.append(f"| {r['name']} | {r['status']} | {r['summary']} |")
    lines.append("")
    lines.append("## Detail")
    for r in report["routines"]:
        lines.append(f"### {r['name']} -- {r['status']}")
        lines.append(r["summary"])
        lines.append("```json")
        lines.append(json.dumps(r.get("detail", {}), indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")
    return "\n".join(lines) + "\n"