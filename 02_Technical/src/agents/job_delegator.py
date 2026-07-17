"""
Order Get It Right -- Agent Job Delegator (MCP Handshake of Delegation)

Deterministic task hand-off between agents.  Every job is sealed to
the Merkle truth ledger through the vault_io boundary.

URN format: OGIR:<SPACE>:<ACTION>

Spatial map:
  00  STRATEGY       01  METHODOLOGY    02  TECHNICAL
  03  VAULT          04  VALIDATION     99  ARCHIVE
"""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from config.constants import PROJECT_OPERATOR
from src.io import vault_io
from src.agents.tau_firewall import StructuralRefusal, TauFirewall


SPATIAL_MAP: Dict[str, str] = {
    "00": "STRATEGY",
    "01": "METHODOLOGY",
    "02": "TECHNICAL",
    "03": "VAULT",
    "04": "VALIDATION",
    "99": "ARCHIVE",
}

VALID_STATUSES = {"QUEUED", "IN_PROGRESS", "COMPLETED", "REFUSED", "FAILED"}

# Minimal in-process ledger for the job tokens. The actual persistence
# goes through vault_io so the boundary rule is enforceable.
class AgentJobDelegator:
    def __init__(
        self,
        tau: Optional[TauFirewall] = None,
        registry_path: Optional[Path] = None,
        operator: str = PROJECT_OPERATOR,
    ) -> None:
        self.operator = operator
        self.tau = tau if tau is not None else TauFirewall()
        self._lock = RLock()
        self._jobs: List[Dict[str, Any]] = []
        # Persistence goes through vault_io (the only legal interface
        # to 03_Vault from 02_Technical code).
        self._registry_path = (
            Path(registry_path) if registry_path else vault_io.job_registry_path()
        )
        self._load()

    def _load(self) -> None:
        if not self._registry_path.exists():
            return
        try:
            data = json.loads(self._registry_path.read_text(encoding="utf-8"))
            self._jobs = data.get("jobs", [])
        except (json.JSONDecodeError, OSError):
            self._jobs = []

    def _save(self) -> None:
        payload = {
            "operator": self.operator,
            "merkleRoot": vault_io.merkle_stats()["merkleRoot"],
            "jobCount": len(self._jobs),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "jobs": self._jobs,
        }
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._registry_path.with_suffix(self._registry_path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        import os
        os.replace(tmp, self._registry_path)

    @staticmethod
    def _validate_urn(urn: str) -> None:
        parts = urn.split(":")
        if len(parts) < 3 or parts[0] != "OGIR":
            raise ValueError(f"URN must be OGIR:<SPACE>:<ACTION>, got {urn!r}")
        if parts[1] not in SPATIAL_MAP:
            raise ValueError(f"Unknown spatial code {parts[1]!r}; valid: {sorted(SPATIAL_MAP)}")

    def create_job_token(
        self,
        assigner: str,
        target_agent: str,
        task_urn: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a Merkle-linked job token. Returns the deterministic job_id."""
        self._validate_urn(task_urn)
        if not assigner or not target_agent:
            raise ValueError("assigner and target_agent are required")
        data = data or {}
        with self._lock:
            start = time.monotonic()
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            job_block = {
                "assigner": assigner,
                "target": target_agent,
                "task": task_urn,
                "payload": data,
                "timestamp": timestamp,
                "status": "QUEUED",
            }
            token_src = json.dumps(job_block, sort_keys=True, separators=(",", ":")).encode()
            job_id = hashlib.sha256(token_src).hexdigest()
            job_block["job_id"] = job_id
            self._jobs.append(job_block)
            vault_io.append_block("JOB_QUEUED", job_block)
            self._save()
            self.tau.measured((time.monotonic() - start) * 1000.0)
            return job_id

    def list_pending_jobs(self, agent_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                dict(j)
                for j in self._jobs
                if j["target"] == agent_id and j["status"] == "QUEUED"
            ]

    def list_all_jobs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(j) for j in self._jobs]

    def claim_job(self, job_id: str) -> Dict[str, Any]:
        with self._lock:
            start = time.monotonic()
            job = self._find(job_id)
            if job is None:
                raise KeyError(f"unknown job_id {job_id}")
            if job["status"] not in {"QUEUED", "IN_PROGRESS"}:
                raise ValueError(f"job {job_id} is {job['status']!r}; cannot claim")
            job["status"] = "IN_PROGRESS"
            job["claimedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            vault_io.append_block("JOB_CLAIMED", {"job_id": job_id, "target": job["target"]})
            self._save()
            self.tau.measured((time.monotonic() - start) * 1000.0)
            return dict(job)

    def close_job(
        self,
        job_id: str,
        result_hash: str,
        status: str = "COMPLETED",
    ) -> Dict[str, Any]:
        if status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        with self._lock:
            start = time.monotonic()
            job = self._find(job_id)
            if job is None:
                raise KeyError(f"unknown job_id {job_id}")
            job["status"] = status
            job["result_seal"] = result_hash
            job["closedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            vault_io.append_block(f"JOB_{status}", {"job_id": job_id, "result_seal": result_hash})
            self._save()
            self.tau.measured((time.monotonic() - start) * 1000.0)
            return dict(job)

    def refuse_job(self, job_id: str, reason: str) -> Dict[str, Any]:
        reason_hash = hashlib.sha256(reason.encode("utf-8")).hexdigest()
        closed = self.close_job(job_id, result_hash=reason_hash, status="REFUSED")
        closed["refusal_reason"] = reason
        return closed

    def _find(self, job_id: str) -> Optional[Dict[str, Any]]:
        for j in self._jobs:
            if j["job_id"] == job_id:
                return j
        return None

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            by_status: Dict[str, int] = {}
            by_spatial: Dict[str, int] = {}
            for j in self._jobs:
                by_status[j["status"]] = by_status.get(j["status"], 0) + 1
                parts = j["task"].split(":")
                space = parts[1] if len(parts) > 1 else "??"
                by_spatial[space] = by_spatial.get(space, 0) + 1
            return {
                "operator": self.operator,
                "jobCount": len(self._jobs),
                "byStatus": by_status,
                "bySpatial": by_spatial,
                "tau": self.tau.stats(),
                "merkleRoot": vault_io.merkle_stats()["merkleRoot"],
                "registryPath": str(self._registry_path),
            }