"""
Order Get It Right - Facts Registry

In-memory ground-truth store with deterministic timestamps.  All facts
append to the Merkle Truth Ledger (via vault_io) so a verifier can
re-derive the state of the registry at any point in time.

The registry is the bridge between 02_Technical code and the vault
data.  Code in 02_Technical never imports from the vault directly; it
calls vault_io which is the only legal interface to the vault.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from src.types import Fact
from src.io import vault_io

# Module-level state
_next_id = 1
_registry: Dict[int, Dict[str, Any]] = {}
_valid_categories = {"Technical", "Governance", "Forensic"}


def reset_registry() -> None:
    """Reset the in-memory registry. The vault ledger is preserved."""
    global _next_id, _registry
    _next_id = 1
    _registry.clear()


def add_fact(category: str, statement: str, source: str) -> Dict[str, Any]:
    """Add a new fact. Returns the fact dict. PENDING status."""
    global _next_id
    if category not in _valid_categories:
        raise ValueError(
            f"Invalid category {category}. Must be one of: {_valid_categories}"
        )
    for existing in _registry.values():
        if existing["statement"] == statement and existing["source"] == source:
            raise ValueError("Fact already exists for statement and source combination")
    now = datetime.now(timezone.utc).isoformat()
    fact = {
        "id": _next_id,
        "category": category,
        "statement": statement,
        "source": source,
        "verified": False,
        "createdAt": now,
        "updatedAt": now,
    }
    _registry[_next_id] = fact
    _next_id += 1
    # Append to the Merkle truth ledger (through the vault_io boundary)
    vault_io.append_block("FACT_ADDED", fact)
    return fact


def list_facts(
    category: Optional[str] = None,
    verified: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """List facts in the in-memory registry, optionally filtered."""
    results = list(_registry.values())
    if category:
        results = [f for f in results if f["category"] == category]
    if verified is not None:
        results = [f for f in results if f["verified"] == verified]
    results.sort(key=lambda f: (f["createdAt"], f["id"]), reverse=True)
    return results


def get_fact(fact_id: int) -> Optional[Dict[str, Any]]:
    return _registry.get(fact_id)


def verify_fact(fact_id: int) -> Dict[str, Any]:
    """Mark a fact as VERIFIED and seal the state transition to the vault."""
    fact = _registry.get(fact_id)
    if not fact:
        raise ValueError(f"Fact with ID {fact_id} not found")
    now = datetime.now(timezone.utc).isoformat()
    fact["verified"] = True
    fact["updatedAt"] = now
    vault_io.append_block("FACT_VERIFIED", {"id": fact_id})
    return fact


def delete_fact(fact_id: int) -> bool:
    if fact_id in _registry:
        del _registry[fact_id]
        vault_io.append_block("FACT_DELETED", {"id": fact_id})
        return True
    return False


def get_stats() -> Dict[str, Any]:
    """Return in-memory stats and the vault Merkle chain stats."""
    records = list(_registry.values())
    by_category: Dict[str, int] = {}
    for r in records:
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1
    return {
        "total": len(records),
        "verified": sum(1 for r in records if r["verified"]),
        "byCategory": by_category,
        "ledger": vault_io.merkle_stats(),
    }


def ledger() -> Dict[str, Any]:
    """Return the vault Merkle chain stats."""
    return vault_io.merkle_stats()


def ledger_blocks() -> List[Dict[str, Any]]:
    """Return every block in the vault Merkle chain."""
    return vault_io.merkle_all()