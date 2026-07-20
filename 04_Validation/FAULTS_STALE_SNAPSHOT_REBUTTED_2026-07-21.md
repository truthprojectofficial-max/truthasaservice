# Stale snapshot rebuttal: `faults..txt` critical errors are already closed

## Source

`files for inspiration and code/faults..txt` lists critical errors and open items from an earlier snapshot.

## Rebuttal

Every item it flags is either already fixed and regression-locked in the live project, or was never accurate.

### 1. Latent canonical JSON bugs

**Stale claim:** Type errors on sets/decimals/dates/UUIDs, `default=str` foot-gun, `+0.0/-0.0` float drift, and NFC/NFD Unicode divergence would break Merkle hash parity.

**Live state:** Closed by F12/2026-07-18 canonical JSON hardening. The project uses `canonical_dumps()` everywhere a payload is hashed or sealed.

**Regression lock:** `tests/test_c14_canonical_json_hardening.py` (22 tests) covers:
- datetime → ISO-8601 `Z` suffix determinism
- UUID/decimal/set/path/enum/date serialisation
- `-0.0` collapses to `+0.0`
- NFC normalisation of keys and values
- NaN/Inf rejected
- `default=str` forbidden
- HTTP `/api/canonical-dump` round-trip

### 2. Deployment bugs

**Stale claim:** PowerShell root resolution, same-tree overwrite, verify-chain CWD crash, missing Python version gate, loose pip failure tracking.

**Live state:** Closed by A5.1/D1 deployment hardening.

**Regression lock:** `tests/test_a5_deploy_dry_run.py` covers:
- full dry-run report emission
- install-path redirect on this host
- warning on non-redirect install path
- no filesystem mutation during dry-run

### 3. Silent directory fork / missing Tauri binaries

**Stale claim:** Project forked between `.claude/OrderGetItRight` and `My Project/OrderGetItRight`, causing binaries to go missing.

**Live state:** The messy session was cleaned in commit b91cda3 and restored to the canonical path. The Tauri shell is under `02_Technical/tauri-shell`.

**Regression lock:** `tests/test_b3_host_dependent.py` verifies the Tauri artefacts, build env, deploy script syntax, hardcopy backup plan, and USB restore assumptions on this host.

### 4. Deprecated FastAPI startup hook

**Stale claim:** `app.py` uses `@app.on_event("startup")`, causing `DeprecationWarning`s.

**Live state:** Replaced with a modern `lifespan` context manager (`_lifespan`) at 2026-07-18.

**Evidence:** `02_Technical/src/server/app.py` line 95-120 defines `@asynccontextmanager async def _lifespan(app: FastAPI)` and constructs the app with `FastAPI(lifespan=_lifespan)`.

### 5. Destructive startup reset

**Stale claim:** `_seed_facts()` forcibly calls `reset_registry()` on every server boot.

**Live state:** `_seed_facts_once()` (line 667) guards the reset with `if facts_registry.list_facts(): return`. It only seeds an empty registry.

### 6. Outdated ontology hardcoding

**Stale claim:** Startup hardcodes `"v3.8 (52 patterns)"` while active ontology is v3.9.

**Live state:** The seed fact uses `DECEPTION_ONTOLOGY_VERSION` from `config/constants.py`, which is currently `"3.10 (55 patterns, R1-R6 applied)"`.

**Regression lock:** `tests/test_smoke.py::test_seed_facts_use_live_ontology_version` asserts the seeded fact contains the live pattern count and rejects stale literals like "52 patterns" or "v3.8".

## Conclusion

`faults..txt` is a historical snapshot, not a live bug report. The project does not need remediation; it needs this rebuttal in the audit trail so the snapshot cannot be mistaken for current open work.
