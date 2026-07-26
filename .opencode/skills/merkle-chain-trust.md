---
description: "Use when making any trust claim or touching the vault. The Merkle chain is the audit-side trust anchor (append-only, re-derivable). Git is the code-side trust anchor (mutable). Both required. The chain wins if they disagree. 6 reference fingerprints identify the project."
---

# Merkle Chain and Trust Anchors Skill

The project has two trust anchors, in parallel since 2026-07-18 (F11).
They are not interchangeable.

## The two trust anchors

| Anchor | What it witnesses | Mutability | Verification |
|--------|-----------------|-----------|-------------|
| Merkle chain (`03_Vault/facts_registry.json`) | Every audit decision (what the engine decided) | Append-only | `python -m src.verify_chain` → MATCH |
| Git (`ogir-build-2026-07-18` branch) | Every source change (what the operator committed) | Mutable | `git log` / `git status` |

### The rule on disagreement

**The chain wins.** If `verify_chain` says BROKEN, restore the vault,
not the code. The chain is the source of truth for *what the engine
decided*; Git is the source of truth for *what the operator committed*.

## The Merkle chain

- **File:** `03_Vault/facts_registry.json`
- **Structure:** Each block contains: index, timestamp, event_type,
  payload, previous_hash, block_hash. The `block_hash` is a SHA-256
  of the canonical JSON of the block (including `previous_hash`).
- **Root:** The final block's `block_hash` is the Merkle root. Any
  change to a past block invalidates every block after it.
- **Verification:** `python -m src.verify_chain` recomputes the root
  from every block and compares to the claimed root. MATCH = intact.
- **Block count:** 40,000+ (grows with every state change).
- **The single interface:** `02_Technical/src/io/vault_io.py`. No code
  reads or writes the vault directly.

## The 6 reference fingerprints

`python -m src.verify_chain --print-refs` prints 6 reference
fingerprints (REF-1 through REF-6) that identify the project. These
are stable across hosts (same input + same config = same output). They
are the project's cryptographic identity.

## The paper card (last-resort recovery)

`04_Validation/hardcopy/` contains a paper card with the Merkle root
printed on it. This is the last-resort recovery anchor — if both git
and the USB mirror are corrupt, the paper card has the known-good root.
Refresh on every quarterly cycle (re-burn the backup, reprint the card).

## The 1-2-3 backup

1. Laptop (working copy)
2. USB / SDXC mirror (`D:\OrderGetItRight.git`)
3. Offsite (the paper card + the USB stored offsite)

`robocopy /MIR /XD __pycache__ .pytest_cache target node_modules` for
the USB mirror. Re-burn quarterly.

## The NIZK proof

Every chain seal includes a NIZK (non-interactive zero-knowledge) proof:
a SHA-256 of the canonical JSON payload plus the operator identity
constant (`PROJECT_OPERATOR = "Justin Barnett"`). The boundary test
enforces no other identity can claim to operate the build.

## The rule

The chain IS the product's proof. It is append-only, re-derivable, and
tamper-evident. Git is the code management layer. Both are required
for a defensible record. If they disagree, the chain wins. The paper
card is the last resort.