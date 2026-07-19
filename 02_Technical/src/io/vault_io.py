"""
Order Get It Right -- Vault I/O Adapter

The vault is a flat directory of JSON files under 03_Vault. This module
is the ONLY module in 02_Technical allowed to construct paths under
03_Vault.  The 00-99 boundary test enforces this.

Code in 02_Technical may call vault_io functions but may not import
from 03_Vault directly.  The vault_io functions are the legal interface.

All JSON serialisation in this module goes through
``src.utils.canonical.canonical_dumps`` (added 2026-07-16, closes the
canonical-JSON foot-gun identified in
``04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md`` area 3). The
previous inline ``json.dumps(...)`` with no ``default=`` callable is
the HIGH-severity latent crash that this module previously contained.
"""
import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

from config.constants import PROJECT_VAULT_DIR
from src.utils.canonical import canonical_dumps

VAULT_DIR = Path(PROJECT_VAULT_DIR)


def _atomic_write_json(path: Path, data: Any) -> None:
    """Atomically write a JSON file to the vault.

    Uses ``canonical_dumps`` so the on-disk file is byte-identical
    to what the Merkle chain was sealed against. The previous
    ``json.dumps(data, indent=2, sort_keys=True)`` (no default=)
    was the foot-gun; it would have produced a file the chain
    could not re-derive if the data ever contained a ``datetime``,
    ``UUID``, ``Decimal``, ``set``, or any other non-JSON-native
    type.

    Windows note: ``os.replace`` can fail with PermissionError when another
    process (e.g. a live uvicorn server) has the target file open. We retry
    a bounded number of times with exponential backoff, then fall back to a
    non-atomic overwrite so the operator is never stuck. This preserves the
    single-writer invariant under the normal case and degrades gracefully
    under concurrent read-only access.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    payload = canonical_dumps(data) if isinstance(data, (dict, list)) else json.dumps(data, indent=2, sort_keys=True)
    tmp.write_text(payload, encoding="utf-8")

    # Retry loop for Windows file-lock races (live server + pytest concurrent).
    last_err = None
    for attempt, delay in enumerate([0.01, 0.03, 0.07, 0.15, 0.31], start=1):
        try:
            os.replace(tmp, path)
            return
        except PermissionError as e:
            last_err = e
            time.sleep(delay)
        except Exception:
            # Any other exception: clean up tmp and re-raise.
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    # Fallback: try shutil.move (sometimes succeeds where os.replace fails on Windows).
    try:
        shutil.move(str(tmp), str(path))
        return
    except Exception:
        pass

    # Last resort: overwrite in place. This is not atomic but ensures the write lands.
    try:
        path.write_text(payload, encoding="utf-8")
    except Exception as e:
        raise last_err from e
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def _read_json(path: Path, default: Any = None) -> Any:
    """Read a JSON file from the vault. Returns default if missing or invalid."""
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def facts_registry_path() -> Path:
    """Path to the facts registry JSON file in the vault."""
    return VAULT_DIR / "facts_registry.json"


def job_registry_path() -> Path:
    """Path to the job registry JSON file in the vault."""
    return VAULT_DIR / "job_registry.json"


def law_path() -> Path:
    """Path to the law.json file in the vault."""
    return VAULT_DIR / "law.json"


def read_facts_registry() -> Dict[str, Any]:
    """Read the facts registry from the vault."""
    return _read_json(facts_registry_path(), {"merkle_root": "0" * 64, "blocks": []})


def write_facts_registry(data: Dict[str, Any]) -> None:
    """Write the facts registry to the vault."""
    _atomic_write_json(facts_registry_path(), data)


def read_job_registry() -> Dict[str, Any]:
    """Read the job registry from the vault."""
    return _read_json(job_registry_path(), {"operator": "Justin Barnett", "merkleRoot": "0" * 64, "jobCount": 0, "updatedAt": "", "jobs": []})


def write_job_registry(data: Dict[str, Any]) -> None:
    """Write the job registry to the vault."""
    _atomic_write_json(job_registry_path(), data)


def read_law() -> Dict[str, Any]:
    """Read law.json from the vault."""
    return _read_json(law_path(), {})


def write_law(data: Dict[str, Any]) -> None:
    """Write law.json to the vault."""
    _atomic_write_json(law_path(), data)


def append_block(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Append a block to the facts registry. Returns the new block.

    The Merkle hash chain logic is implemented here, NOT in a separate
    vault module, because the strict 00-99 boundary rule says code in
    02_Technical cannot import from 03_Vault. This function IS the
    legal interface to the vault's Merkle chain.

    RE-SEED GUARD (2026-07-19): if the on-disk vault file exists but
    reads back zero blocks, we refuse to write block index 1. This
    prevents a silent re-seed of the chain when the vault file is
    truncated, emptied by a OneDrive sync event, or lost. The operator
    must restore the vault from git HEAD (or a backup) before any new
    block can be appended. See GEM_DOCS_RECONCILIATION_2026-07-19.md §6.
    """
    import hashlib
    from datetime import datetime, timezone

    data = read_facts_registry()
    blocks = data.get("blocks", [])

    # Re-seed guard: the file exists on disk but has no blocks. This means
    # the chain was there before (the file would not exist otherwise) and
    # is now empty/truncated. Refuse to start a fresh chain.
    if not blocks and facts_registry_path().exists():
        raise RuntimeError(
            "VAULT_RESEED_REFUSED: facts_registry.json exists on disk but "
            "contains zero blocks. The canonical chain appears to have been "
            "truncated or emptied (e.g. by a OneDrive sync event or a clean "
            "checkout that left the file empty). Refusing to write block "
            "index 1 to prevent a silent fork of the audit history. "
            "Restore the vault from git HEAD before appending new blocks: "
            "`git checkout HEAD -- 03_Vault/facts_registry.json` then "
            "re-run. See GEM_DOCS_RECONCILIATION_2026-07-19.md section 6."
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    previous_hash = blocks[-1]["current_hash"] if blocks else "0" * 64

    block_payload = {"event": event_type, "payload": payload, "ts": timestamp}
    serialised = _canonical_json(block_payload)
    current_hash = hashlib.sha256((previous_hash + serialised).encode("utf-8")).hexdigest()

    from config.constants import CHAIN_OPERATOR_ID as _OPERATOR
    operator = _OPERATOR
    nizk_seed = _canonical_json(payload) + "|" + operator
    integrity_digest = hashlib.sha256(nizk_seed.encode("utf-8")).hexdigest()

    block = {
        "index": len(blocks) + 1,
        "timestamp": timestamp,
        "event_type": event_type,
        "previous_hash": previous_hash,
        "current_hash": current_hash,
        "payload": payload,
        "integrity_digest": integrity_digest,
    }
    blocks.append(block)

    data["merkle_root"] = current_hash
    data["blocks"] = blocks
    write_facts_registry(data)

    return block


def _canonical_json(payload: Any) -> str:
    """Serialise a payload deterministically.

    Now a thin wrapper around ``src.utils.canonical.canonical_dumps``.
    The previous inline implementation
    (``json.dumps(payload, sort_keys=True, separators=(",", ":"))``
    with no ``default=`` callable) was the foot-gun. This wrapper
    exists so the existing call sites
    (``block_payload = {"event": event_type, "payload": payload, "ts": timestamp}``)
    continue to work without change. The wrapper is byte-identical to
    the previous output for any payload that contained only JSON-native
    types (the historical case) and is the project-wide fix for any
    payload that contains ``datetime``, ``UUID``, ``Decimal``, ``set``,
    or any other non-JSON-native type.
    """
    return canonical_dumps(payload)


def merkle_stats() -> Dict[str, Any]:
    """Return statistics about the current Merkle chain."""
    data = read_facts_registry()
    blocks = data.get("blocks", [])
    event_types: Dict[str, int] = {}
    for block in blocks:
        event_types[block["event_type"]] = event_types.get(block["event_type"], 0) + 1
    return {
        "blockCount": len(blocks),
        "merkleRoot": data.get("merkle_root", "0" * 64),
        "eventTypes": event_types,
        "firstBlock": blocks[0]["timestamp"] if blocks else None,
        "lastBlock": blocks[-1]["timestamp"] if blocks else None,
    }


def merkle_all() -> list:
    """Return every block in the Merkle chain."""
    return read_facts_registry().get("blocks", [])


def job_append(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Append a job event to the job registry. Same Merkle chain logic as facts."""
    import hashlib
    from datetime import datetime, timezone

    data = read_job_registry()
    jobs = data.get("jobs", [])

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    previous_hash = data.get("merkleRoot", "0" * 64)

    block_payload = {"event": event_type, "payload": payload, "ts": timestamp}
    serialised = _canonical_json(block_payload)
    current_hash = hashlib.sha256((previous_hash + serialised).encode("utf-8")).hexdigest()

    block = {
        "timestamp": timestamp,
        "event": event_type,
        "previous_hash": previous_hash,
        "current_hash": current_hash,
        "payload": payload,
    }
    jobs.append(block)

    data["merkleRoot"] = current_hash
    data["jobCount"] = len(jobs)
    data["updatedAt"] = timestamp
    data["jobs"] = jobs
    write_job_registry(data)

    return block
