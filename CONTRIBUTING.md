# Contributing to Order Get It Right

> Thank you for considering a contribution. OGIR is a forensic
> deception-detection tool — every contribution must preserve the
> determinism, air-gap, and chain-seal guarantees.

## Read first

1. **`AGENTS.md`** — the contributor guide (rules every agent must follow)
2. **`INDEX.md`** — current project state + must-do checklist
3. **`04_Validation/HANDOVER_LOG.md`** — last agent's sign-off
4. **`LICENSE`** — MIT licensed

## The 6 non-negotiables

1. **Deterministic:** same input + same config = same output. No `random`, no `time.time()`, no `datetime.utcnow()`.
2. **Air-gapped:** no network imports in `02_Technical/src/`. The boundary test enforces this.
3. **Chain-sealed:** every state change calls `vault_io.append_block` before committing.
4. **Canonical JSON:** every `json.dumps` goes through `canonical_dumps` with `sort_keys=True, separators=(",", ":")`.
5. **00-99 boundary:** code in `02_Technical/` cannot import from `03_Vault/` or `04_Validation/`. Tests cannot import from `src/` except `from src.server.app import app`.
6. **Operator identity:** `PROJECT_OPERATOR = "Justin Barnett"`. No anonymous changes.

## How to contribute

### Good first issues

Look for issues labeled `good-first-issue` on GitHub. These are
small, well-scoped tasks suitable for new contributors.

### The seal-test-verify-commit ritual

Every code change follows this exact sequence:

1. **Edit** the source file(s)
2. **Test:** `python -m pytest tests/ -q` → must pass (400+ passed)
3. **Verify:** `$env:PYTHONPATH="02_Technical"; python -m src.verify_chain` → must be MATCH
4. **Seal:** call `vault_io.append_block("EVENT_TYPE", payload)` with files_changed + fix_id
5. **Commit:** `git commit -m "EVENT_TYPE: block NNNNN sealed. <summary>"`
6. **Verify again:** `python -m src.verify_chain` → must still be MATCH

### Code style

- Python 3.12+ syntax (4 spaces, no tabs)
- `snake_case` for functions/variables, `PascalCase` for Pydantic models, `UPPER_SNAKE_CASE` for constants
- Type hints required on every public function
- No comments unless explaining WHY (not WHAT)

### What you can contribute

- New test cases for the evaluation suite (see `tests/test_evaluation_cases_*.py`)
- Bug fixes (include a sealed chain block)
- Documentation improvements
- New deception patterns (requires operator approval — open an issue first)

### What you CANNOT touch

- `03_Vault/` — the Merkle chain. Append-only. Never edit.
- `04_Validation/hardcopy/` — paper trust anchor. Never touch.
- `99_Archive_Historical/` — sealed records. Never touch.
- Adding network imports to `02_Technical/src/` — breaks the air-gap.

## Pull requests

1. Fork the repo
2. Create a feature branch: `git checkout -b fix-description`
3. Make your change following the seal-test-verify-commit ritual
4. Push: `git push origin fix-description`
5. Open a PR with:
   - Chain root before and after
   - New test count
   - Which open item it closes

## Questions?

Open a GitHub Discussion or issue. The operator (Justin Barnett)
responds within 30 days.