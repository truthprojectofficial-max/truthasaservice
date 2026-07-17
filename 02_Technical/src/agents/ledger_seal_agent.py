"""
Ledger_Seal_Agent -- the audit log + Merkle chain reviewer.
"""
import hashlib
import json
from typing import Any, Dict, List

from src.utils.canonical import canonical_dumps

from src.io import vault_io
from config.constants import PROJECT_OPERATOR


class LedgerSealAgent:
    """The third-party audit log + Merkle chain reviewer. Deterministic."""

    def __init__(self) -> None:
        self.operator = PROJECT_OPERATOR

    def seal_fact(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return vault_io.append_block(event_type, payload)

    def read_ledger(self) -> List[Dict[str, Any]]:
        return vault_io.merkle_all()

    def stats(self) -> Dict[str, Any]:
        return vault_io.merkle_stats()

    def verify_root(self) -> Dict[str, Any]:
        blocks = vault_io.merkle_all()
        stats = vault_io.merkle_stats()
        if not blocks:
            return {
                "claimed_root": stats["merkleRoot"],
                "recomputed_root": "0" * 64,
                "matches": stats["merkleRoot"] == "0" * 64,
                "block_count": 0,
                "broken_at": None,
            }
        previous_hash = "0" * 64
        for block in blocks:
            payload = {
                "event": block["event_type"],
                "payload": block["payload"],
                "ts": block["timestamp"],
            }
            serialised = canonical_dumps(payload)
            computed = hashlib.sha256((previous_hash + serialised).encode("utf-8")).hexdigest()
            if computed != block["current_hash"]:
                return {
                    "claimed_root": stats["merkleRoot"],
                    "recomputed_root": computed,
                    "matches": False,
                    "block_count": len(blocks),
                    "broken_at": block["index"],
                }
            previous_hash = block["current_hash"]
        return {
            "claimed_root": stats["merkleRoot"],
            "recomputed_root": previous_hash,
            "matches": previous_hash == stats["merkleRoot"],
            "block_count": len(blocks),
            "broken_at": None,
        }
