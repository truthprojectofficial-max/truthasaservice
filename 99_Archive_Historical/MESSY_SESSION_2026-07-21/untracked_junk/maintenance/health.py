"""
src.maintenance.health -- the individual deterministic routines.

Each routine is a function ``r_<name>(state) -> RoutineResult`` where:

* ``state`` is the previous-run state dict (for delta routines) or
  ``{}`` on first run / when no state exists.
* ``RoutineResult`` is a plain dict::

      {
        "name": "chain_integrity",
        "status": "PASS" | "WARN" | "FAIL",
        "summary": "<one line for the operator>",
        "detail":  { ... structured finding ... },
      }

Every routine is pure w.r.t. the vault: it only READS. It may compute
hashes, count files, and compare to ``state`` -- it never writes to the
vault, never edits a block, never mutates a verdict. Writing is the
job of ``reporter`` (the seal block + the report file) and ``faults``
(a fault file in the Squeal dir on FAIL).
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List

from src.io import vault_io
from src.verify_chain import verify as _verify_chain

RoutineResult = Dict[str, Any]


# ---------------------------------------------------------------------------
# Routines
# ---------------------------------------------------------------------------

def r_chain_integrity(_state: Dict[str, Any]) -> RoutineResult:
    """Re-derive the Merkle root from disk and compare to the registry."""
    try:
        result = _verify_chain(None)  # default vault
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "chain_integrity",
            "status": "FAIL",
            "summary": f"verify_chain raised: {exc}",
            "detail": {"error": repr(exc)},
        }
    ok = bool(result.get("matches"))
    broken = result.get("brokenAtIndex")
    return {
        "name": "chain_integrity",
        "status": "PASS" if ok else "FAIL",
        "summary": "chain intact (MATCH)" if ok else f"BROKEN at block {broken}",
        "detail": {
            "matches": ok,
            "blockCount": result.get("blockCount"),
            "merkleRoot": result.get("merkleRoot"),
            "firstBlock": result.get("firstBlock"),
            "lastBlock": result.get("lastBlock"),
            "brokenAt": broken,
        },
    }


def r_job_journal_tail(state: Dict[str, Any]) -> RoutineResult:
    """Confirm the job-journal tail agrees with the materialised registry."""
    try:
        tail = vault_io._read_job_tail()
        reg = vault_io.read_job_registry()
        tail_count = int(tail.get("jobCount", -1))
        reg_count = int(reg.get("jobCount", -2))
        jobs_len = len(reg.get("jobs", []))
        ok = tail_count == reg_count == jobs_len
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "job_journal_tail",
            "status": "FAIL",
            "summary": f"job-tail check raised: {exc}",
            "detail": {"error": repr(exc)},
        }
    return {
        "name": "job_journal_tail",
        "status": "PASS" if ok else "FAIL",
        "summary": (
            f"OK tail={tail_count} registry={reg_count} jobs={jobs_len}"
            if ok
            else f"DRIFT tail={tail_count} registry={reg_count} jobs={jobs_len}"
        ),
        "detail": {
            "tailJobCount": tail_count,
            "registryJobCount": reg_count,
            "jobsListLength": jobs_len,
        },
    }


def r_vault_growth(state: Dict[str, Any]) -> RoutineResult:
    """Block-count delta since the last maintenance run."""
    try:
        stats = vault_io.merkle_stats()
        now_count = int(stats.get("blockCount", 0))
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "vault_growth",
            "status": "FAIL",
            "summary": f"vault_growth raised: {exc}",
            "detail": {"error": repr(exc)},
        }
    prev = int(state.get("vault_growth_block_count", now_count))
    delta = now_count - prev
    status = "PASS" if delta >= 0 else "WARN"
    return {
        "name": "vault_growth",
        "status": status,
        "summary": f"block count {now_count} (delta {delta:+d} since last run)",
        "detail": {"blockCount": now_count, "previousBlockCount": prev, "delta": delta},
    }


def r_disk_usage(_state: Dict[str, Any]) -> RoutineResult:
    """Bytes used by the vault, outbox, logs, and squeal directories."""
    from config.constants import (
        PROJECT_VAULT_DIR, PROJECT_OUTBOX_DIR, PROJECT_LOGS_DIR, PROJECT_SQUEAL_DIR,
    )
    targets = {
        "vault": Path(PROJECT_VAULT_DIR), "outbox": Path(PROJECT_OUTBOX_DIR),
        "logs": Path(PROJECT_LOGS_DIR), "squeal": Path(PROJECT_SQUEAL_DIR),
    }
    usage = {label: (_dir_size(p) if p.exists() else 0) for label, p in targets.items()}
    total = sum(usage.values())
    return {
        "name": "disk_usage",
        "status": "PASS",
        "summary": (
            f"vault {usage['vault']/1_048_576:.1f} MB, "
            f"outbox {usage['outbox']/1_048_576:.1f} MB, "
            f"logs {usage['logs']/1_048_576:.1f} MB, "
            f"squeal {usage['squeal']/1_048_576:.1f} MB"
        ),
        "detail": {"bytes": usage, "totalBytes": total},
    }


def r_squeal_backlog(state: Dict[str, Any]) -> RoutineResult:
    """Count un-acknowledged Squeal reports. WARN above a threshold."""
    from config.constants import PROJECT_SQUEAL_DIR
    squeal_dir = Path(PROJECT_SQUEAL_DIR)
    count = 0
    if squeal_dir.exists():
        count = sum(
            1 for p in squeal_dir.iterdir()
            if p.is_file() and p.name.startswith("squeal-") and p.name.endswith(".json")
        )
    threshold = int(state.get("squeal_backlog_threshold", 50))
    status = "PASS" if count <= threshold else "WARN"
    return {
        "name": "squeal_backlog",
        "status": status,
        "summary": f"{count} squeal report(s) on disk (threshold {threshold})",
        "detail": {"count": count, "threshold": threshold},
    }


def r_constants_checksum(state: Dict[str, Any]) -> RoutineResult:
    """SHA-256 of constants.py. WARN if it changed since last run."""
    from config.constants import PROJECT_ROOT
    p = Path(PROJECT_ROOT) / "02_Technical" / "config" / "constants.py"
    try:
        digest = _hash_file(p)
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "constants_checksum",
            "status": "FAIL",
            "summary": f"constants.py unreadable: {exc}",
            "detail": {"error": repr(exc)},
        }
    prev = state.get("constants_checksum")
    status = "PASS"
    if prev is not None and prev != digest:
        status = "WARN"
    note = "" if (prev is None or prev == digest) else f" (changed from {prev[:12]})"
    return {
        "name": "constants_checksum",
        "status": status,
        "summary": f"constants.py {digest[:12]}{note}",
        "detail": {"sha256": digest, "previous": prev},
    }


def r_monitor_briefing(_state: Dict[str, Any]) -> RoutineResult:
    """Run the MonitorAgent oversight sweep (NOT sealed by it).

    Surfaces the MonitorAgent's headline finding. The briefing uses
    snake_case keys (``chain_integrity`` is the string ``"OK"`` or
    ``"BROKEN (...)"``; ``hide_pattern_hits`` is a dict of role->list).
    """
    from src.agents.monitor_agent import MonitorAgent
    try:
        briefing = MonitorAgent().run_briefing(seal_to_chain=False)
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "monitor_briefing",
            "status": "FAIL",
            "summary": f"MonitorAgent raised: {exc}",
            "detail": {"error": repr(exc)},
        }
    chain_str = str(briefing.get("chain_integrity", "OK"))
    chain_ok = chain_str == "OK"
    hide_hits = briefing.get("hide_pattern_hits", {})
    total_hits = int(briefing.get("hide_pattern_hits_total", 0))
    squeal_count = briefing.get("squeal_file_count")
    if not chain_ok:
        status = "FAIL"
    elif total_hits:
        status = "WARN"
    else:
        status = "PASS"
    return {
        "name": "monitor_briefing",
        "status": status,
        "summary": (
            f"monitor: chain {'OK' if chain_ok else 'BROKEN'}, "
            f"{total_hits} hide-pattern hit(s), {squeal_count} squeal file(s)"
        ),
        "detail": {
            "chainIntegrity": chain_str,
            "chainRootObserved": briefing.get("chain_root_observed"),
            "chainRootRecomputed": briefing.get("chain_root_recomputed"),
            "hidePatternHits": hide_hits,
            "hidePatternHitsTotal": total_hits,
            "squealCount": squeal_count,
            "blockCount": briefing.get("block_count"),
        },
    }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

HOURLY: List[str] = [
    "chain_integrity", "job_journal_tail", "vault_growth", "squeal_backlog",
]
DAILY: List[str] = [
    "chain_integrity", "job_journal_tail", "vault_growth", "disk_usage",
    "squeal_backlog", "constants_checksum", "monitor_briefing",
]
CADENCES: Dict[str, List[str]] = {"hourly": HOURLY, "daily": DAILY}

ROUTINES: Dict[str, Any] = {
    "chain_integrity": r_chain_integrity,
    "job_journal_tail": r_job_journal_tail,
    "vault_growth": r_vault_growth,
    "disk_usage": r_disk_usage,
    "squeal_backlog": r_squeal_backlog,
    "constants_checksum": r_constants_checksum,
    "monitor_briefing": r_monitor_briefing,
}


def run_routine(name: str, state: Dict[str, Any]) -> RoutineResult:
    """Run one routine by name. Raises KeyError on unknown name."""
    return ROUTINES[name](state)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dir_size(p: Path) -> int:
    total = 0
    for dirpath, _dirs, files in os.walk(p):
        if "__pycache__" in dirpath or ".pytest_cache" in dirpath:
            continue
        for fn in files:
            try:
                total += (Path(dirpath) / fn).stat().st_size
            except OSError:
                pass
    return total


def _hash_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()