# OGIR Assessment Notes -- 2026-07-18

**Reviewer:** Hermes Agent (cloud model glm-5.2:cloud) on behalf of operator Justin Barnett.
**Mode:** Read-only review. No source files modified. Two deliverables produced:
- `04_Validation/OGIR_ARCHITECTURE_DIAGRAM.html` (dark-themed SVG architecture diagram)
- `04_Validation/OGIR_ASSESSMENT_2026-07-18.md` (full assessment, ~34 KB)

This note is the short-form pointer for the record. The long-form assessment is
the canonical document.

## Context

Previous attempt (logged in `Windows PowerShell 5.1.txt`) failed: local Ollama
models (qwen3.5:9b, llama3.1:8b, gemma4:12b) hit `finish_reason='length'` truncation
repeatedly and could not complete the analysis. The current run uses a cloud
model with a larger output budget. No Ollama model was in the audit path -- the
project's no-LLM-in-the-audit-loop rule was not violated.

## What was reviewed

- `AGENTS.md`, `README.md`, `pyproject.toml`, `conftest.py`, `.gitignore`
- `00_Strategy/STRATEGY.md`, `00_Strategy/GOVERNANCE.md`
- `01_Methodology/MATHEMATICS.md`, `DECEPTION_ONTOLOGY.md`, `REAL_OPTIONS_LATTICE.md`
- `02_Technical/config/constants.py`
- `02_Technical/requirements.txt`
- `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` (read in full)
- `04_Validation/changelog.log` (head + tail)
- `03_Vault/facts_registry.json` (head + tail -- the live Merkle chain)
- Project tree structure (full file listing under 02_Technical, tests/, deploy/,
  launchers/, docs/, 04_Validation/)
- A background subagent was dispatched to digest the full Python source tree
  (agents, engines, io, server, utils, tauri-shell, tests). Its digest is
  appended to the conversation separately and should be cross-checked against
  the long-form assessment before any decision is sealed.

## Headline findings (priority order)

1. **F8 -- Ontology validation thin.** 54 patterns validated against only 8 EVAL
   cases. F1=0.909 after v3.9 bump; EVAL-002 and EVAL-007 still fail. The
   deception ontology is the heart of the audit verdict.
2. **F7 -- Lattice inputs hard-coded.** S0=55.0, K1=18.0, K2=10.0 are the same
   for every audit. The lattice is a deception-adjusted optionality index,
   not a business valuation. Legal output language should not imply otherwise.
3. **F6 -- "NIZK proof" is a placeholder.** It is a SHA-256 digest, not a Schnorr
   signature. MATHEMATICS.md is honest; downstream affidavit language is not.
   Rename `nizk_proof` -> `integrity_digest` in the next CONSTANTS_BUMP.
4. **F4 -- Duplicate id:1 blocks baked into the chain.** Blocks #1 and #4 both
   carry `id: 1` with the same statement. The A3 foot-gun fix prevents new
   duplicates; it cannot remove the old ones. The chain still verifies. Add a
   `KNOWN_CHAIN_ARTEFACTS.md` note so the next operator/auditor sees the
   explanation in one place.
5. **F1 -- Documentation drift.** Constants count ("19" vs 35), ontology version
   (MATHEMATICS.md still says "52 patterns" vs 54), test counts (70/2, 73/0,
   86/1, 48/3 all appear), README layout (lists `document_engine/`,
   `middleware/`, `services/` that don't exist). A single
   `DOCS_RECONCILED_FINAL` seal would fix the remainder.
6. **F5 -- Changelog pollution.** Dozens of synthetic "Test incident from pytest"
   entries in `04_Validation/changelog.log`. Gate the test writes behind
   `OGIR_TEST_WRITE_CHANGELOG=1` or redirect to a temp file.
7. **F9 -- Single-operator.** `PROJECT_OPERATOR = "Justin Barnett"` is
   boundary-enforced. Bus factor is one. Run D1-true-clean-host on a second PC
   with a trusted third party acting as the next operator.
8. **F2 -- `.bak-pre-*` and stale dirs.** 10+ backup files, empty `docs/`,
   empty `02_Technical/03_Vault/`. Add `.bak-pre-*` to `.gitignore` or
   hard-delete.
9. **F10 -- Tauri binary unsigned.** Fine for personal use; blocker for
   distribution.
10. **F11 -- No Git.** By design (chain is version control). Consider adopting
    Git in parallel for diff/branch/remote-backup ergonomics.

## What the project does well

- 00-99 spatial hierarchy with AST-enforced boundary test
- Canonical JSON rule, correctly applied and tested
- No-network claim verified by `audit_no_network.py` and pinned by
  `tests/test_audit_no_network.py`
- 6 reference fingerprints (REF-1..REF-6) -- clever third-party verification
- Maintenance rhythm (daily/weekly/monthly/quarterly/annual via 5 STAGE_PAPER_*.txt)
- Handover docs for two distinct audiences (auditor, new operator)
- 928-line TROUBLESHOOTING.md with SYMPTOM/ROOT CAUSE/FIX/ESCALATE structure
- Honest OPEN_ITEMS list, sealed to the chain

## Reference fingerprints (live state)

| Fingerprint | Value |
|-------------|-------|
| REF-1 constants.py | 7654ddf6fffd79c618d1899b6703121d99b742e8d37793e2ea1a023bb70bedea |
| REF-2a STRATEGY.md | e4b2ff1928e2b8e4d253cf7a2feaf66457df6df4c01b49793a499286023aa75d |
| REF-2b GOVERNANCE.md | 0c2335de7e3e1962f30cacc3d12fe2921e8565287190c04d2dec01328f8f028d |
| REF-3 source tree | 7962bf6116445f46296ac97f43ffaf01ce8ca68e111cfc3f565d4c7a5b659087 |
| REF-4 tree shape | b85f4cb7c7c4bbcd202cdde014219d5d6820137f0bb714a519e5403e7915e0af |
| REF-5 Merkle root | 0fe4872733fb402bbe8dc14e6543a702f901118e6130549304de156bf48ac7c7 |
| REF-6 composite | ec72d1f273f9c6e52385bd39dffe41a2a52d7d47fe267dca40a9188a1a34cda6 |
| Block count | 7,156 |
| First / last block | 2026-07-11T17:15:10Z / 2026-07-17T14:14:00Z (approx) |

Re-derive: `cd 02_Technical && python -m src.verify_chain` (add `--print-refs`
for all six fingerprints).

## Next-operator one-liner

Read `OGIR_ASSESSMENT_2026-07-18.md` for the full report. The two deliverables
this session produced are in `04_Validation/` (the diagram and the assessment);
they are not sealed to the chain (review-only artefacts). If the operator
decides to act on a finding, the action and its seal are the operator's call.

---

End of notes.