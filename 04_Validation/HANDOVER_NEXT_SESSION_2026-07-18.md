# Order Get It Right -- Hand-Over Statement

**Session date:** 2026-07-18
**Operator:** Justin Barnett
**Build agent:** codex-on-Justo
**Branch:** ogir-build-2026-07-18
**State at hand-over:**
- Tests: 94 passed, 1 skipped, 2 xfailed, 1 warning
- Merkle chain: MATCH, 11,312 blocks
- Chain root: `c9fbbff7c45202b26d0befb4f5abb1409e393ff44d5330ecdbc2c25628244cf8`
- Git: clean working tree, last commit `1b313f5`

---

## 1. What was done in this session

1. Full assessment of the project: legitimacy, real-world application, market, work so far, remaining work, structure, and framing.
2. Added 7 documented AI-legal case studies to the EVAL suite in:
   - `tests/test_evaluation_cases_ai_legal.py`
   - Cases: Mata v. Avianca (fabricated citation), UK ChatGPT fake case, Williams v. Alabama AI oral argument honest register, Williams register used as deception cover, Claude legal commentary, Australian AI disclosure, Canadian fake family-law citation.
3. Wrote a self-contained build directive for the next session in:
   - `04_Validation/BUILD_DIRECTIVE_NEXT_SESSION.md`
4. Sealed both changes to the Merkle chain and committed them to Git.

---

## 2. Current open items

From `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` and the new directive:

| # | Item | Severity | Effort | State |
|---|------|----------|--------|-------|
| 1 | Embed Makita v Sprowles citation in affidavit generator | MEDIUM | 1 hour | OPEN |
| 2 | R5-EXTENDED-2 register/hedge gate for AI legal text | HIGH | 2-4 hours | CLOSED 2026-07-18; gate implemented and xfail markers removed |
| 3 | Lexical-set audit for remaining 53 patterns | LOW-MEDIUM | 4-6 hours | OPEN; pilot recommended |
| 4 | Add Git remote (USB bare repo default) | MEDIUM | 30 min | OPEN |
| 5 | Expand EVAL suite to 30+ real cases | MEDIUM | 1-2 days | OPEN; partial progress with AI-legal cases |
| 6 | Wire lattice inputs to extracted evidence (F7-deep) | LOW | 1-2 days | OPEN; defer recommended |
| 7 | Refresh hard-copy reference card | LOW | 15 min | OPEN; defer to quarterly cycle |
| 8 | Tauri code-signing | LOW | $200-500/yr | OPEN; operator decision |
| 9 | Second-PC clean-host restore test (D1-TRUE) | MEDIUM | 2-4 hours | OPEN; needs second Windows PC |
| 10 | Gmail .mbox import (E1) | LOW | 1-2 hours | OPEN; operator must export |

---

## 3. What the next operator should do first

Pick one of these two high-leverage items:

1. **Embed Makita citation in `legal_affidavit_generator.py`.**
   - File: `02_Technical/src/engines/legal_affidavit_generator.py`, lines 108-122.
   - Held intake: `C:\Users\justo\OneDrive\Documents\Supreme Court of New South Wales -.txt`
   - Citation: `Makita (Australia) Pty Ltd v Sprowles [2001] NSWCA 305`.
   - Seal: `F8_EXTENDED_LEGAL_MAKITA_CITED_2026_07_XX`.

2. **Implement R5-EXTENDED-2 register/hedge gate.**
   - File: `02_Technical/src/engines/deception_scanner.py`.
   - Targets: the two xfailed cases in `tests/test_evaluation_cases_ai_legal.py`.
   - Goal: suppress DD-004 / DD-011 / DD-027 / DD-041 on court-argument register and writerly hedges, without breaking the adversarial cover-lie case EVAL-032.
   - Seal: `R5_EXTENDED_2_REGISTER_GATE_2026_07_XX`.

The build directive `04_Validation/BUILD_DIRECTIVE_NEXT_SESSION.md` contains exact steps, decision gates, and defaults for both.

---

## 4. How to verify the hand-over

```powershell
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git status                              # should be clean
git log --oneline -3                    # should show the two session commits
cd 02_Technical
python -m pytest tests/ -q              # expect 94 passed, 1 skipped, 2 xfailed, 1 warning
python -m src.verify_chain              # expect MATCH
```

If anything fails, see `04_Validation/TROUBLESHOOTING.md`.

---

## 5. Files changed or created in this session

- `tests/test_evaluation_cases_ai_legal.py` (new)
- `04_Validation/BUILD_DIRECTIVE_NEXT_SESSION.md` (new)
- `03_Vault/facts_registry.json` (auto-sealed SHUTDOWN blocks during test runs)
- `03_Vault/job_registry.json` (auto-updated)
- `03_Vault/affidavit_transcript.txt` (auto-regenerated during tests)

---

## 6. Project direction statement

Order Get It Right is a maintained, auditable personal audit tool, not a finished commercial product. The next 2 sessions should focus on:

1. Legal defensibility: Makita citation + per-pattern validation.
2. Scanner safety: R5-EXTENDED-2 register gate so AI-legal text is not misclassified.
3. Empirical base: expand EVAL suite toward 30+ cases.

Longer term: decide whether to wire real financials to the optionality lattice or keep it explicitly framed as an optionality index; code-sign the Tauri binary before any public distribution; have a real Australian lawyer review the affidavit and ACL demand letter.

---

## 7. Contact and identity

- Operator: Justin Barnett
- Canonical source: `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`
- USB/SDXC backup: `D:\OrderGetItRight`
- Jurisdiction: Commonwealth of Australia / ACL / Evidence Act 1995 (NSW)
- Version: 1.0.0, ontology 3.10 (54 patterns)

End of hand-over. The chain is the source of truth; this document is the operator-readable companion.
