# Order Get It Right -- Build Directive for Next Session

**For:** Codex (or any deterministic build agent)  
**Date:** 2026-07-18  
**Branch:** `ogir-build-2026-07-18`  
**Current state at directive write:**
- 94 passed, 1 skipped, 2 xfailed, 1 warning
- Merkle chain MATCH, 11,311 blocks, root `37d603d5e82b2fb08f7818d05d96a9b0596328eddc7fcf23f4457c84ecc9e1f2`
- Git working tree clean after `F8_EXTENDED_AI_LEGAL_EVAL_SUITE_2026_07_18`
- Two held AI-legal intakes on file:
  - `data/outbox/INTAKE_HELD_AUDITED_2026-07-18_CLAUDE_LEGAL.json`
  - `data/outbox/INTAKE_HELD_AUDITED_2026-07-18_WILLIAMS_AI_TRANSCRIPT.json`

---

## 1. Mission

This directive removes ambiguity from the next build session. Every work package below has:

1. A clear goal.
2. Exact files to touch.
3. Step-by-step instructions.
4. A verification command.
5. A **multi-choice decision gate** with a default answer.

The default answer is always the conservative path: preserve the chain, preserve the test suite, and do not introduce operator-dependent decisions without explicit authority.

If the operator is indecisive, silent, or gives a non-answer, **use the default**. Do not ask clarifying questions unless the directive explicitly tells you to. The directive is the authority.

---

## 2. Pre-flight ritual (run before any work)

```powershell
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git status                          # must be clean
git log --oneline -5                # know the last 5 commits
cd 02_Technical
python -m pytest tests/ -q          # capture baseline
cd 02_Technical
python -m src.verify_chain          # must print MATCH
```

If `git status` is dirty, stop. Seal an `OPERATOR_DIRTY_TREE_2026_07_XX` block with the output of `git status`, commit the existing work, or stash it. Do not start new work on a dirty tree.

If `pytest` or `verify_chain` fails, stop. Do not add features to a broken build. Seal a `BUILD_BASELINE_BROKEN_2026_07_XX` block and end the session.

---

## 3. Work packages

### WP-1 -- Embed Makita v Sprowles citation in affidavit generator

**Goal:** Close F8-EXTENDED-LEGAL. The affidavit generator makes a specialised-knowledge claim under the Evidence Act 1995 (NSW) s 79 but does not cite the foundational authority. Add the citation so an adversarial reader can verify the basis.

**Files:**
- `02_Technical/src/engines/legal_affidavit_generator.py` lines 108-122 (VERIFICATION STATEMENT / Pathway of Reasoning / Specialised knowledge block)

**Steps:**
1. Read the current `compile_full_affidavit` method.
2. Locate the paragraph beginning `"Specialised knowledge: The operator is the original author..."`.
3. Rewrite it to:
   - Cite `Makita (Australia) Pty Ltd v Sprowles [2001] NSWCA 305`.
   - State that the operator's knowledge meets the Makita test: the field is specialised, the opinion is based on the operator's training/study/experience, and the opinion is wholly or substantially based on that knowledge.
   - Keep the existing claim that the operator is the original author of the codebase and has direct working knowledge of every module, formula, and threshold.
4. Do not change any other affidavit logic.

**Verification:**
```powershell
cd 02_Technical
python -m pytest tests/ -q          # must stay 94/1/2xfailed/1warning or improve
python -m src.verify_chain          # must print MATCH
```

**Decision gate:**
- (A) Implement the citation now.
- (B) Defer to a later session; update OPEN_ITEMS step 2 to "deferred".
- (C) Ask the operator for a different citation.

**Default:** (A) Implement now. The held intake `Supreme Court of New South Wales -.txt` is already on file and this is the obvious next step.

---

### WP-2 -- R5-EXTENDED-2: Register/hedge gate for AI legal text

**Status:** CLOSED 2026-07-18. The gate is implemented in `02_Technical/src/engines/deception_scanner.py` and the two former xfail tests in `tests/test_evaluation_cases_ai_legal.py` now pass.

**What was done:**
1. Added `_has_legal_register()` helper that detects court-argument and legal-commentary register markers (e.g. `Justice`, `Section`, `v.`, `Court`, `counsel`, `oral argument`, `lawyer`, `argument`, `brief`).
2. Added `_apply_r5_legal_register_gate()` that suppresses register-sensitive hedge/politeness patterns (DD-004, DD-006, DD-011, DD-027, DD-041) when:
   - the text is in legal register, AND
   - only those patterns fire, AND
   - no fabrication/lie-of-certainty pattern (DD-001, DD-009, DD-019, DD-020, DD-036, DD-040, DD-052) is present.
3. Removed the `@pytest.mark.xfail` markers from EVAL-031 and EVAL-033.

**Verification:**
```powershell
cd 02_Technical
python -m pytest tests/test_evaluation_cases_ai_legal.py -v  # 8 passed
python -m pytest tests/ -q                                   # 94 passed, 1 skipped, 1 warning
python -m src.verify_chain                                  # MATCH
```

---

### WP-3 -- R5-EXTENDED: Lexical-set audit for remaining 53 patterns

**Goal:** Surface false-negatives in the remaining 53 patterns by testing surface-form near-misses, then fix them in one ontology bump.

**Files:**
- `02_Technical/src/engines/deception_ontology_data.py`
- `tests/test_evaluation_cases_extended.py` (new or extend existing)
- `02_Technical/config/constants.py` (bump ontology version string)

**Steps:**
1. For each pattern DD-001..DD-054, write a small probe sentence that:
   - Uses a synonym or near-miss of the existing indicator, and
   - Is clearly deceptive in context.
2. Run each probe through `/api/analyze`.
3. If a probe fails to fire, add the synonym to the indicator list.
4. Do not change pattern names, severities, or thresholds unless a false-positive is uncovered.
5. Bump `DECEPTION_ONTOLOGY_VERSION` to `3.11 (54 patterns, R1-R4 + R5 + R5-EXTENDED applied)`.

**Verification:**
```powershell
cd 02_Technical
python -m pytest tests/ -q
python -m src.verify_chain
```

**Decision gate:**
- (A) Do the full 53-pattern audit now.
- (B) Do a smaller 10-pattern pilot now and defer the rest.
- (C) Defer entirely.

**Default:** (B) Do a 10-pattern pilot. The full audit is 4-6 hours; a pilot gives measurable progress without monopolising the session.

---

### WP-4 -- F11-remote: Add a Git remote

**Goal:** Close F11-remote. Add an offsite-compatible remote so the code-side trust anchor is backed up.

**Files:**
- None (Git config only).

**Steps:**
1. Decide which remote option to use.

**Decision gate (must be answered explicitly):**
- (a) USB bare repo at `D:\OrderGetItRight\.git` -- air-gap compatible, cheapest.
- (b) Self-hosted Gitea on a Raspberry Pi inside the air-gap.
- (c) Third-party host (GitHub / Codeberg / GitLab) -- **requires explicit operator approval because it breaks the air-gap guarantee**.
- (d) Defer entirely.

**Default:** (a) USB bare repo. This matches the air-gap discipline and requires no new hardware or accounts.

If (a) is selected:
```powershell
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git remote add usb "D:\OrderGetItRight\.git" || git remote set-url usb "D:\OrderGetItRight\.git"
git push -u usb ogir-build-2026-07-18
```

If the push fails because `D:\OrderGetItRight` is not a git repo, create a bare repo first:
```powershell
git init --bare "D:\OrderGetItRight\.git"
```

**Verification:**
```powershell
git remote -v
git push usb ogir-build-2026-07-18
```

Then seal a `GIT_REMOTE_USB_ADDED_2026_07_XX` block.

---

### WP-5 -- F8-EXTENDED: Continue EVAL-suite expansion

**Goal:** Grow the EVAL suite toward 30+ cases with real anonymised correspondence.

**Files:**
- `tests/test_evaluation_cases_extended.py`

**Steps:**
1. Identify 5-10 additional public-domain or operator-anonymised correspondence samples.
2. Add them as `EvaluationCase` rows.
3. Tag each case and set probability bands conservatively.
4. Do not chase 100% pass rate; xfail is acceptable for known gaps.

**Candidate themes:**
- Supplier warranty evasion (already covered by EVAL-001).
- AI customer-service chat transcripts.
- Marketing copy with greenwashing / overstated claims.
- Regulator letters.
- Invoice disputes.

**Decision gate:**
- (A) Add 5-10 more cases now.
- (B) Defer until R5-EXTENDED-2 and Makita are done.
- (C) Ask operator for specific correspondence to anonymise.

**Default:** (B) Defer. WP-1 and WP-2 are higher leverage for this session.

---

### WP-6 -- F7-deep: Wire lattice inputs to extracted evidence

**Goal:** Replace the hard-coded S0/K1/K2 lattice defaults with values derived from extracted evidence, turning the optionality index into something closer to a business-specific signal.

**Files:**
- `02_Technical/src/engines/real_options_lattice.py`
- `02_Technical/src/io/extractors.py`
- `02_Technical/config/constants.py`
- `01_Methodology/REAL_OPTIONS_LATTICE.md`

**Steps:**
1. Define mapping from extracted evidence to lattice inputs (e.g. price paid -> S0, remediation cost -> K1, follow-on investment -> K2).
2. Add optional `evidence` parameter to `hardened_compound_binomial_gate`.
3. Fall back to hard-coded defaults when evidence is missing.
4. Update the framing string if the inputs are now evidence-derived.
5. Seal a `CONSTANTS_BUMP` block recording the change.

**Decision gate:**
- (A) Implement now.
- (B) Defer; keep the current framing as optionality index.
- (C) Partial: add the evidence parameter but keep defaults as primary.

**Default:** (B) Defer. This is a methodology change, not a bug fix. It needs its own session and a calibration plan.

---

### WP-7 -- Optional: Refresh hard-copy reference card

**Goal:** Update the printed QUICK_REFERENCE_CARD with the latest Merkle root and test count.

**Files:**
- `04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt`

**Steps:**
1. Run `cd 02_Technical && python -m src.verify_chain --print-refs`.
2. Update the card with the new REF-5 root and block count.
3. Print and pin it.

**Decision gate:**
- (A) Refresh and print now.
- (B) Defer to the next quarterly cycle.

**Default:** (B) Defer. Hard-copy refresh is a quarterly ritual unless the root changes for a reason the operator cares about.

---

## 4. Project direction suggestions

These are recommendations from the reviewing agent, not commands. If the operator disagrees, the operator's choice wins.

### Next 2 sessions (highest leverage)
1. **WP-1 Makita citation** -- 1 hour, closes a real legal-output gap.
2. **WP-2 R5-EXTENDED-2 register gate** -- unblocks the two xfailed AI-legal cases and makes the scanner safe for court text.

### Next 1-2 months
3. **WP-3 lexical-set audit pilot** -- start with 10 patterns, expand in monthly chunks.
4. **WP-4 Git remote** -- USB bare repo, preserves air-gap.
5. **WP-5 EVAL expansion to 30+ cases** -- use held intakes and public-domain correspondence.
6. **D1-TRUE clean-host test** -- second Windows PC, trusted third party acts as next operator.

### Longer term
7. **F7-deep evidence-wired lattice OR kill the valuation framing entirely** -- pick one. Either make the lattice business-specific or double down on "optionality index" everywhere.
8. **F10 code-signing** -- required for any distribution beyond the operator.
9. **Legal review** -- have a real Australian lawyer read the affidavit generator and ACL demand letter.
10. **Ontology validation study** -- run precision/recall against 50+ real cases, per pattern.

### What not to do
- Do not add network imports to the runtime.
- Do not run multi-worker uvicorn without a lock.
- Do not rewrite existing chain blocks.
- Do not push to a third-party Git host without explicit operator approval.
- Do not claim the tool is "court-ready" or a "business valuation" in any public language.

---

## 5. Sealing and commit protocol

After every source change:

1. Run `pytest` and `verify_chain`.
2. Seal a block with event type in SCREAMING_SNAKE_CASE.
3. `git add -A && git commit -m "<event_type>: <one-line summary>"`.
4. One block, one commit, per source change.

If a change breaks tests or chain after two recovery attempts:
1. `git reset --hard HEAD~1`.
2. Seal a `FIX_REVERTED_2026_07_XX` block with the reason.
3. Move to the next work package.

If the chain ever shows BROKEN:
1. Stop all work.
2. `git reset --hard` to the last MATCH commit.
3. Seal a `CHAIN_BROKEN_RECOVERY_2026_07_XX` block.
4. End the session.

---

## 6. Completion criteria for this session

The session is complete when:

1. WP-1 or WP-2 (or both) are done and sealed/committed, OR explicitly deferred with a sealed block.
2. `python -m pytest tests/ -q` returns `94 passed, 1 skipped, 2 xfailed, 1 warning` or better.
3. `python -m src.verify_chain` prints MATCH.
4. `git status` is clean.
5. `OPEN_ITEMS_AND_REFERENCE.md` is updated to reflect which steps were closed or deferred.

If none of WP-1..WP-7 are started, the session is a no-op and should end with a `NO_WORK_SELECTED_2026_07_XX` seal.

---

End of directive. The chain is the source of truth; this document is the operator-readable plan.
