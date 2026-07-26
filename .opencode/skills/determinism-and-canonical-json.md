---
description: "Use when writing any code that touches JSON, time, or randomness. Same input + same config = same output on any host. No random, no time.time(), no datetime.utcnow(). Every json.dumps MUST pass through _canonical_default. Never write default=str."
---

# Determinism and Canonical JSON Skill

The determinism promise: same input + same config = same output, on
any host. This is a non-negotiable. The chain is tamper-evident (not
byte-reproducible across runs) — both guarantees coexist.

## Forbidden in runtime code

| Forbidden | Why | Use instead |
|-----------|-----|------------|
| `import random` | Non-deterministic | Deterministic algorithms |
| `time.time()` | Non-deterministic | `datetime.now(timezone.utc)` |
| `datetime.utcnow()` | Deprecated + non-deterministic | `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")` |
| `uuid.uuid4()` | Non-deterministic | Deterministic ID from content hash |
| `os.urandom()` | Non-deterministic | Not needed in audit path |

## The canonical timestamp

Every timestamp in the chain and in audit output uses:
```python
from datetime import datetime, timezone
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
```

Format: `YYYY-MM-DDTHH:MM:SSZ` (ISO 8601, UTC, no microseconds).

## Canonical JSON

Every `json.dumps` in the runtime MUST pass through `_canonical_default`
(see `02_Technical/src/utils/canonical.py`):

```python
from src.utils.canonical import _canonical_default
import json

json.dumps(payload, default=_canonical_default, sort_keys=True, separators=(",", ":"))
```

### Why

- `sort_keys=True` — key order does not affect the hash.
- `separators=(",", ":")` — no whitespace, compact output.
- `_canonical_default` — handles types stdlib `json` can't serialize
  (Path, datetime, Decimal, sets) in a deterministic way.

### The band-aid that breaks determinism

```python
# WRONG — never do this
json.dumps(payload, default=str)
```

`default=str` calls `str()` on any unserializable object. `str()`
is NOT deterministic across Python versions, platforms, or even runs
(`str(Path("a/b"))` differs on Windows vs Linux). A `default=str`
band-aid silently breaks the determinism promise. The canonical-JSON
hardening test catches it.

## What the chain guarantees vs what determinism guarantees

| Property | Chain | Determinism |
|----------|-------|-------------|
| Same input → same output | No (append-only) | YES |
| Tamper-evident | YES | No |
| Byte-reproducible across runs | No | YES (for the engine decision) |

The chain is tamper-evident: any change to a past block invalidates the
Merkle root. Determinism is byte-reproducible: the same input through
the same engine produces the same verdict. Both are required.

## The rule

No randomness. No wall-clock time in the audit path. Every JSON
serialization is canonical. A `default=str` is a bug, not a shortcut.
The determinism promise is the product — break it and the trust
anchor is meaningless.