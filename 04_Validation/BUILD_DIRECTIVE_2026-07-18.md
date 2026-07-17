

---

## 1. The task

Fix the 11 code-fixable findings from `04_Validation/OGIR_ASSESSMENT_2026-07-18.md`. Each fix is a sealed unit: edit -> test -> verify_chain -> seal block -> git commit. The 6 larger findings (F7, F8, F9, F10, F11-adopt-Git) are out of scope for this run -- they need operator decisions or hardware.

Process each fix in the order below. After EACH fix:
1. Run `python -m pytest tests/ -q` -- must stay at `86 passed, 1 skipped` (or improve). No regressions.
2. Run `python -m src.verify_chain` -- must stay `MATCH`.
3. Seal a block to the chain recording the fix (see sealing protocol in section 3).
4. `git add -A && git commit -m "<event_type>: <one-line summary>"`.

If a fix breaks tests or the chain, `git reset --hard HEAD~1` to revert, seal a `FIX_REVERTED` block with the reason, and move on. Do not get stuck on any single fix.

---

## 2. The fixes (in priority order)

### FIX 1 -- F12: Propagate canonical_dumps to two chain verifiers
**Files:**
- `02_Technical/src/agents/ledger_seal_agent.py` line ~45
- `02_Technical/src/agents/monitor_agent.py` line ~81

**Change:** Both use `json.dumps(sort_keys=True, separators=(",", ":"))` to serialise block payloads for re-hashing. Replace with `canonical_dumps` from `src.utils.canonical`. Add the import. This makes them consistent with `vault_io._canonical_json` and `verify_chain._canonical_json` (the C14 fix).

**Why:** Without this, the two verifiers will `TypeError` if a block payload ever contains a `datetime`/`UUID`/`Decimal`/`set`/-0.0/NFD string, and will silently hash differently from the canonical verifier on the same chain. Latent bug.

**Verification:** `python -m pytest tests/ -q` (must stay 86/1). Manual check: `python -c "from src.agents.ledger_seal_agent import LedgerSealAgent; print(LedgerSealAgent().verify_root()['matches'])"` must print `True`.

**Seal event_type:** `CANONICAL_JSON_PROPAGATED_2026_07_18`

### FIX 2 -- F13: Fix monitor_agent "unexplained_verdicts" stub
**File:** `02_Technical/src/agents/monitor_agent.py` lines ~244-247

**Change:** The current loop appends EVERY `SUPPRESSED` block as "unexplained" without checking for a matching `REFUSAL` block. Implement the actual cross-check: for each `SUPPRESSED` block, scan the chain for a `REFUSAL` block whose `payload.fact_id` (or `payload.job_id`) matches the SUPPRESSED block's reference, within a window of +-10 blocks. If a matching REFUSAL exists, the SUPPRESSED block is "explained" -- do not append it. Only append genuinely unexplained SUPPRESSED blocks.

**Why:** As-is, the operator's Incident Briefing always lists every SUPPRESSED block as unexplained, which is misleading. The comment claims a check that the code doesn't perform.

**Verification:** `python -m pytest tests/ -q`. Add a regression test `tests/test_monitor_unexplained.py` that builds a fake chain with one SUPPRESSED + matching REFUSAL, runs `MonitorAgent.run_briefing(seal_to_chain=False)`, and asserts `unexplained_verdicts` is empty. (This test file can import `src.agents.monitor_agent` -- wait, no, the boundary test forbids that. Use the HTTP surface instead: `POST /api/monitor/briefing` if it exists, or extend the existing monitor test via TestClient. If no HTTP surface exists for monitor, skip the regression test and just assert via subprocess that the module imports cleanly. Document the test-gap decision in the seal.)

**Seal event_type:** `MONITOR_UNEXPLAINED_FIXED_2026_07_18`

### FIX 3 -- F6: Rename nizk_proof -> integrity_digest
**Files:**
- `02_Technical/src/io/vault_io.py` (the field name in `append_block`, ~line 126)
- `02_Technical/src/verify_chain.py` (if it references the field)
- `02_Technical/src/engines/legal_affidavit_generator.py` (the affidavit formatter -- update the label text)
- `02_Technical/src/agents/affidavit_agent.py` (if it references the field)
- Any test that asserts the field name

**Change:** Rename the field `nizk_proof` -> `integrity_digest` everywhere it appears in the runtime and tests. Update the affidavit label text from "NIZK proof" to "integrity digest (SHA-256 of canonical payload + operator identity constant; placeholder for future Schnorr implementation)".

**Why:** The field is a SHA-256 digest, not a zero-knowledge proof. Calling it "NIZK proof" in a legal affidavit is misleading. MATHEMATICS.md already documents it as a placeholder; the code should match.

**Migration concern:** The on-disk chain has 7,156 blocks with `nizk_proof` as the field name. Renaming the field in the code means new blocks use `integrity_digest` but old blocks still have `nizk_proof`. The verifier must handle BOTH field names (read `nizk_proof` for old blocks, `integrity_digest` for new). Do NOT rewrite the chain history. Add a backward-compat read: `block.get("integrity_digest") or block.get("nizk_proof")`.

**Verification:** `python -m pytest tests/ -q` must stay 86/1. `python -m src.verify_chain` must stay MATCH (proves the backward-compat read works against the existing 7,156 blocks).

**Seal event_type:** `NIZK_RENAMED_2026_07_18` -- this is a `CONSTANTS_BUMP`-class change per AGENTS.md; record old name, new name, reason, test result in the payload.

### FIX 4 -- F14: Amend the determinism headline
**File:** `02_Technical/config/constants.py` lines 5-6 (the module docstring)

**Change:** The current docstring says "every magic number is named here" and implies bit-for-bit identity. Update the module docstring to state honestly: "Same input + same config = same verdict, same scores, same decision -- on any host. The sealed chain carries ISO-8601 timestamps and is tamper-evident, not byte-reproducible across runs."

**Also update** `00_Strategy/STRATEGY.md` non-negotiable #1 to match (the "Absolute Determinism" section).

**Why:** The headline overstates what the chain delivers. The project's own tests acknowledge this by stripping timestamps before determinism comparisons. Honest and still strong.

**Verification:** `python -m pytest tests/ -q` (no test asserts the docstring text, so tests won't break). `python -m src.verify_chain` stays MATCH.

**Seal event_type:** `DETERMINISM_HEADLINE_AMENDED_2026_07_18`

### FIX 5 -- F1 + F3: Docs reconciliation
**Files:**
- `AGENTS.md` -- change "19 named constants" to "41 named constants (19 numeric decision thresholds + metadata/paths/version strings)"
- `01_Methodology/MATHEMATICS.md` section 4 -- change "52 Patterns" to "54 Patterns" and "52-pattern" to "54-pattern"
- `README.md` layout section -- replace the stale `document_engine/`, `middleware/`, `services/` directory listings with the actual layout: `src/agents/`, `src/engines/`, `src/io/`, `src/server/`, `src/utils/`, `config/`, `tools/`, `web/`, `tauri-shell/`

**Why:** Three docs disagree with the live tree. The "no black boxes" promise requires docs that match code.

**Verification:** `python -m pytest tests/ -q`. No test asserts these doc strings, but the boundary test must still pass (it doesn't read these docs).

**Seal event_type:** `DOCS_RECONCILED_FINAL_2026_07_18`

### FIX 6 -- F4: Add KNOWN_CHAIN_ARTEFACTS.md
**New file:** `04_Validation/KNOWN_CHAIN_ARTEFACTS.md`

**Content:** List the permanent data-quality artefacts in the chain that cannot be removed (append-only):
- Blocks #1 and #4 both carry `id: 1` with statement "Order Get It Right enforces the agent chain via the job delegator." -- duplicate seed facts from the A3 foot-gun era. New duplicates are blocked by `facts_registry.add_fact` dedup-check on `(statement, source)`.
- Block #2 carries statement "All deception detections use the deterministic 52-pattern ontology v3.8." -- stale; live version is "3.9 (54 patterns)". Sealed before the A2 v3.8/v3.9 fix.
- The chain verifies as MATCH despite these artefacts. They are historical record, not live bugs.

**Why:** The chain is append-only; the explanation is the fix. The next operator/auditor needs this in one place.

**Verification:** `python -m pytest tests/ -q` (the new file is in 04_Validation, doesn't affect tests). `python -m src.verify_chain` stays MATCH.

**Seal event_type:** `KNOWN_ARTEFACTS_DOCUMENTED_2026_07_18`

### FIX 7 -- F5: Gate test-suite changelog writes
**File:** The test that writes "Test incident from pytest" entries to `04_Validation/changelog.log`. Find it with `grep -rl "Test incident from pytest" tests/`.

**Change:** Gate the changelog write behind an environment variable `OGIR_TEST_WRITE_CHANGELOG=1`. Default: do not write to the live changelog. If the env var is not set, write to a temp file (`tempfile.NamedTemporaryFile`) instead, or skip the write and assert the wiring via a mock.

**Why:** The changelog is the human-facing counterpart to the Merkle ledger. Dozens of synthetic "Test incident from pytest" entries on every pytest run corrupt the signal.

**Verification:** `python -m pytest tests/ -q` -- the test that previously wrote to the changelog must still pass (it should assert the wiring via the mock or temp file). Confirm `04_Validation/changelog.log` has NO new "Test incident from pytest" entries after the run.

**Seal event_type:** `CHANGELOG_POLLUTION_GATED_2026_07_18`

### FIX 8 -- F15 cluster: Cleanup seal
**Multiple small fixes in one seal:**

8a. `02_Technical/src/io/vault_io.py` ~line 126: replace hardcoded `"Justin Barnett"` with `from config.constants import PROJECT_OPERATOR` and use `PROJECT_OPERATOR`. The NIZK/integrity_digest seed must use the constant, not a string literal.

8b. `02_Technical/tauri-shell/src/commands.rs`: delete the `ping` function (it's defined but not registered in `invoke_handler!` in `lib.rs`, so it's unreachable dead code). Also remove it from any test if referenced.

8c. `02_Technical/src/agents/inventory_agent.py` ~lines 349-354: remove the dead branch in `_classify` where both arms of `if size <= STREAM_HASH_THRESHOLD: ... else: ...` call `_safe_stream_hash` identically. Collapse to a single call.

8d. `02_Technical/src/engines/real_options_lattice.py` ~line 79: replace the hardcoded sigma2 upper clamp `0.90` with `REAL_OPTIONS_SIGMA_MAX` (import from `config.constants`).

8e. `02_Technical/config/constants.py` line 8: remove the unused `import os`.

8f. `02_Technical/src/engines/squeal_protocol.py`: the `write_squeal_report` function is never called from the audit path (dead code). Either wire it (call it from `deception_scanner.trigger_squeal_protocol` when probability > 0.75, replacing the in-memory `SQUEAL_LOG` list) OR delete it. Conservative choice: wire it. Replace the in-memory `SQUEAL_LOG.append` in `deception_scanner.trigger_squeal_protocol` with a call to `squeal_protocol.write_squeal_report`. Keep the in-memory list as a secondary record if the disk write fails (try/except).

**Verification:** `python -m pytest tests/ -q` must stay 86/1 (or improve if the squeal wiring adds coverage). `python -m src.verify_chain` stays MATCH. For 8b (Tauri), the build won't be re-run in this directive -- just confirm `cargo check` passes in `02_Technical/tauri-shell/` if cargo is available; if not, skip the cargo check and note it in the seal.

**Seal event_type:** `CLEANUP_SEAL_2026_07_18` -- payload lists all 6 sub-fixes (8a-8f) with file:line and before/after.

### FIX 9 -- F17: Fix hardcoded Python path in test
**File:** `tests/test_normalize_regression.py`

**Change:** Replace `PYTHON_EXE = C:\Users\justo\OneDrive\Documents\to the spoils go\Python314\python.exe` with `PYTHON_EXE = sys.executable` (add `import sys` if not present). This makes the test host-agnostic.

**Why:** The test will break on any host other than Justin's. Prerequisite for F9 (second-PC clean-host test).

**Verification:** `python -m pytest tests/test_normalize_regression.py -v` must pass. `python -m pytest tests/ -q` must stay 86/1.

**Seal event_type:** `TEST_PORTABILITY_FIXED_2026_07_18`

### FIX 10 -- F16: Document the single-worker assumption
**Files:**
- `02_Technical/src/server/app.py` -- add a comment at the top of the lifespan handler: "Single uvicorn worker assumed. `vault_io.append_block` is not concurrency-safe across workers (read-modify-write without a process-wide lock). Do not run with `--workers N` where N > 1 without adding a lock."
- `deploy/deploy.ps1` -- add a comment in the server-start section: "Run uvicorn with default single worker. Multi-worker requires a process-wide lock around `vault_io.append_block` (currently absent)."
- `02_Technical/DEPLOYMENT.md` -- add a "Concurrency" section noting the single-worker assumption.

**Why:** The air-gap single-tenant model makes multi-worker unlikely, but the assumption is currently undocumented. Documentation is the proportionate fix.

**Verification:** `python -m pytest tests/ -q`. No functional change.

**Seal event_type:** `CONCURRENCY_ASSUMPTION_DOCUMENTED_2026_07_18`

### FIX 11 -- F2: Cleanup .bak-pre-* files and empty dirs
**Action:**
- Delete all `.bak-pre-*` files under the project:
  ```bash
  find "/c/Users/justo/OneDrive/Documents/My Project/OrderGetItRight" -name ".bak-pre-*" -type f -delete
  ```
  (These are in `02_Technical/src/server/app.py.bak-pre-*`, `02_Technical/src/agents/inventory_agent.py.bak-pre-*`, `02_Technical/src/third_party_assistant.py.bak-pre-*`, `tests/test_smoke.py.bak-pre-*`, `00_Strategy/STRATEGY.md.bak-pre-docfix`.)
- Delete the empty `docs/` directory if empty.
- Delete the empty `02_Technical/03_Vault/` directory if empty (the live vault is at project-root `03_Vault/`).
- Add `.bak-pre-*` to `.gitignore` to prevent future accumulation.

**Why:** 10+ backup files and empty dirs are tree noise. The `.gitignore` already excludes `__pycache__/` etc.; add `.bak-pre-*` for the same reason.

**Verification:** `python -m pytest tests/ -q` (the boundary test excludes `.bak-pre-*` from REF-4, so deletion is safe). `python -m src.verify_chain` stays MATCH. Re-derive REF-4 (tree shape) and note the change in the seal payload.

**Seal event_type:** `TREE_CLEANED_2026_07_18`

---

## 3. Sealing protocol (after EACH fix)

Every fix seals a block to the Merkle chain via the project's own convention. From a Python one-liner or a small script:

```python
import sys
sys.path.insert(0, "02_Technical")
from src.io.vault_io import append_block
block = append_block("<EVENT_TYPE>", {
    "fix_id": "Fxx",
    "files_changed": ["path:line", ...],
    "before": "short description",
    "after": "short description",
    "test_result": "86 passed, 1 skipped, 1 warning",
    "chain_status": "MATCH",
    "bin_id": "codex-on-Justo",
    "operator": "Justin Barnett",
    "timestamp": "2026-07-18T...",
})
print(f"Block {block['index']}, root {block['current_hash']}")
```

The block payload MUST be canonical-JSON-native (dicts of str/int/float/bool/list). No `datetime` objects -- use ISO-8601 strings. The `append_block` call handles canonicalisation internally.

After sealing, the chain root changes. The next `python -m src.verify_chain` must show MATCH with the new root.

---

## 4. Completion criteria

The run is complete when:
1. All 11 fixes are applied (or explicitly sealed as BLOCKED with a reason).
2. `python -m pytest tests/ -q` shows `86 passed, 1 skipped, 1 warning` (or better -- if a fix added a regression test, the count goes up).
3. `python -m src.verify_chain` shows MATCH.
4. The Merkle chain has 11 new blocks (one per fix), each with the correct `event_type`.
5. Git has 11 new commits (one per fix), each with the event_type as the commit subject.
6. A final `COMPLETION_SEAL_2026_07_18` block is appended summarising the run: fixes applied, fixes blocked (if any), final test count, final chain root, final block count.

Print the final summary to stdout:
```
=== OGIR BUILD DIRECTIVE COMPLETE ===
Fixes applied: 11/11 (or N/11 with M blocked)
Final test count: XX passed, 1 skipped
Final chain root: <new root>
Final block count: 7156 + 11 = 7167 (or adjusted)
Git commits: 11
```

---

## 5. What NOT to do

- **Do NOT inline API keys, credentials, or secrets into any prompt, log, commit message, sealed payload, or test file.** Source from disk via env vars (section 0.1).
- **Do NOT ask the operator for input.** This is auto-go. Make conservative decisions and document them in the seal.
- **Do NOT rewrite or edit existing chain blocks.** The chain is append-only. Old blocks stay as-is (the `nizk_proof` -> `integrity_digest` rename uses backward-compat reads, not history rewrites).
- **Do NOT push to any Git remote.** This is a local-only workspace.
- **Do NOT attempt F7 (lattice inputs), F8 (ontology validation expansion), F9 (second-PC test), F10 (code signing), or F11 (Git adoption decision).** These need operator decisions or hardware. They are out of scope.
- **Do NOT skip the verification ritual.** Every fix gets pytest + verify_chain. No exceptions.
- **Do NOT use `--yolo` mode.** Use `--full-auto` (sandboxed but auto-approves file changes in workspace). `--yolo` is no-sandbox and too dangerous for a project with a 7,156-block chain.
- **Do NOT fall back to a different Ollama model without sealing a `MODEL_FALLBACK` block** explaining why qwen3:8b failed and what you fell back to. Prefer to stop and seal `BLOCKED` instead.

---

## 6. If something breaks

If a fix breaks tests and you cannot recover within 2 attempts:
1. `git reset --hard HEAD~1` to revert the fix.
2. Seal a `FIX_REVERTED_2026_07_18` block with `fix_id`, `reason`, `test_failure_output`.
3. Move to the next fix. Do not get stuck.

If the chain ever shows BROKEN (not MATCH):
1. Stop immediately. Do not apply any more fixes.
2. `git reset --hard` to the last commit where the chain was MATCH.
3. Seal a `CHAIN_BROKEN_RECOVERY_2026_07_18` block with the last known good root.
4. End the run with a summary noting the chain break and recovery.

---

## 7. Launch command

Once the directive is written, the operator (or a launcher script) runs Codex with:

```bash
cd "/c/Users/justo/OneDrive/Documents/My Project/OrderGetItRight"
codex exec --full-auto --pty "$(cat 04_Validation/BUILD_DIRECTIVE_2026-07-18.md)"
```

Or, for a background long-running task (recommended -- this will take a while):

```bash
codex exec --full-auto --pty "$(cat 04_Validation/BUILD_DIRECTIVE_2026-07-18.md)" 2>&1 | tee 04_Validation/logs/codex_build_2026-07-18.log
```

The directive is self-contained. Codex reads it, executes sections 0 through 4, and exits with the completion summary.

---

End of directive.