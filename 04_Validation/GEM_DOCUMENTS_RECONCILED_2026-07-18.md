# Reconciliation of Gemini Gem Configuration Documents against Live Project State

**Project:** Order Get It Right (OGIR)  
**Live project path:** `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`  
**Documents reconciled:**
- `C:\Users\justo\OneDrive\Documents\My Project\Gemini Gem Knowledge Base Configuration.txt`
- `C:\Users\justo\OneDrive\Documents\My Project\Gem Senior AUDIT RESULTS..txt`
**Reconciled by:** Hermes Agent on behalf of operator Justin Barnett  
**Date:** 2026-07-18 (UTC)  
**Live state at reconciliation:**
- Git branch: `ogir-build-2026-07-18`
- Merkle chain: 11,313 blocks, root re-derived at runtime
- Last commit: `8951d0a HANDOVER_NEXT_SESSION_2026_07_18`
- Tests (last hand-over): 94 passed, 1 skipped, 2 xfailed, 1 warning

---

## 1. What these two documents are

Both files are **draft specifications for custom Gemini assistants ("Gems")** intended to operate as RAG pre-processors or audit reviewers for the OrderGetItRight project. They are **not** live system documentation and they are **not** current audit reports. They contain useful architectural frameworks but also stale numbers, aspirational architecture, and legal framing that overstates the project's compliance status.

This document reconciles their claims against the live project state so they can be corrected before being used as source material for any Gem, NotebookLM source, or external communication.

---

## 2. Factual corrections

| Claim in Gem documents | Live state | Correction |
|---|---|---|
| "3,033 blocks, root 26501872d1a9d419..." (Configuration doc) | 11,313 blocks; root changes with each seal | The 3,033 figure is from an earlier snapshot. Live root must be re-derived with `python -m src.verify_chain`. |
| "Merkle ledger that holds exactly 3,033 blocks" | 11,313 blocks as of 2026-07-18 | Update all block-count references. The chain is append-only; exact counts are per-snapshot. |
| "validation-vault-share" Azure Files Storage Share | Not implemented | This is an architecture roadmap item, not live. Current storage is local JSON `03_Vault/facts_registry.json`. |
| Migration to SQLite / better-sqlite3 | Not implemented | Still using `facts_registry.json`. SQLite migration is a scaling proposal, not code. |
| "No Git" / "There is no `.git/`" | Git adopted in parallel on 2026-07-18 (F11) | `.git/` exists on branch `ogir-build-2026-07-18`. Remove this claim. |
| "7,156 blocks" (Assessment doc reference) | 11,313 blocks as of 2026-07-18 | The 7,156 figure was correct at the time of `OGIR_ASSESSMENT_2026-07-18.md` drafting but is now stale. |
| "52-pattern deception ontology" | 54-pattern ontology v3.10 | Updated in live code and docs. Configuration doc says v3.9 (54 patterns) which is partially correct; Assessment doc's "52" is stale. |
| "8 EVAL cases" | 15+ after AI-legal case additions in 2026-07-18 | Update EVAL-suite count. Still short of the 30+ target. |
| "NIZK proof" | Renamed to `integrity_digest` in live code (F6) | Update terminology. The field is a SHA-256 digest, not a zero-knowledge proof. |
| "Real-options valuation" / "business valuation" | Reframed as "deception-adjusted optionality index" (F7) | Update language. The lattice uses hard-coded inputs and does not value the audited business. |
| Tauri binary signed | Unsigned (F10, acknowledged) | Remove any implication of signed binaries. Code-signing is a future operator decision. |
| "Facts registry loaded entirely into memory" | Still true | Correct. Flag as current scaling limitation. |
| "Zero-AI Spatial Architecture Mandate" 00-99 hierarchy | Correctly matches live project | Keep. The 00-99 hierarchy is real and enforced by `tests/test_00_99_boundary.py`. |

---

## 3. Legal and compliance framing corrections

The Gem Senior audit document makes several claims about statutory compliance that need tempering:

### 3.1 Section 336 of the Corporations Act 2001

**Document claim:** "Under Section 336 of the Corporations Act 2001, corporate auditing compliance is anchored by ASQM 1 and ASQM 2..."  
**Correction:** Section 336 of the Corporations Act deals with the appointment, removal, and remuneration of auditors of proprietary companies. It does not impose ASQM/ASA requirements on a personal software tool. ASQM/ASA apply to registered company auditors conducting statutory audits under the Corporations Act. OGIR is a personal audit-assistance tool, not a registered audit firm. The document conflates **statutory audit firm obligations** with **software engineering governance**. The frameworks are useful analogies; they are not legally binding on this project.

### 3.2 "Cannot be audited in full, nor certified as complying"

**Document claim:** The project cannot be audited because it lacks ASQM mechanisms, ASA 500 evidence, ISO 19011 reproducibility, ISO/IEC 42001 PDCA, NIST AI RMF alignment, etc.  
**Correction:** This is partially true as engineering criticism but misleading as legal conclusion. The project:
- Is not required to be ISO/IEC 42001 certified.
- Is not required to be NIST AI RMF aligned.
- Is not conducting statutory audits under the Corporations Act.

What the project **is** trying to do: produce transparent, deterministic, defensible audit assistance. The relevant standards for that goal are **evidence law** (Evidence Act 1995, expert evidence rules like *Makita (Australia) Pty Ltd v Sprowles* [2001] NSWCA 305) and **consumer law** (ACL). The corporate auditing standards are useful structural references but should not be presented as mandatory gates.

### 3.3 "70/30 rule of AI development"

**Document claim:** "The 70/30 rule of AI development, ensuring that while the technical model automates roughly 30% of repetitive data tasks, human oversight retains 70% of critical reasoning..."  
**Correction:** This is not a recognised standard or rule in AI governance literature. It appears to be a heuristic invented in the document. Do not present it as an industry standard. Human-in-the-loop oversight is a real concept (NIST AI RMF Manage function), but the 70/30 split is arbitrary.

### 3.4 "Fundamental Rights Impact Assessments (FRIA)"

**Document claim:** Required before production release under NIST AI RMF Manage.  
**Correction:** FRIA is an EU AI Act concept, not a NIST AI RMF concept. NIST AI RMF uses "risk response" and "human-in-the-loop" framing. FRIA should not be attributed to NIST.

---

## 4. Useful elements to keep from the documents

### 4.1 00-99 Spatial Hierarchy Rule (Configuration doc)

This correctly describes the live project structure:
- `00_Strategy/` -- governance
- `01_Methodology/` -- human-readable math, no code
- `02_Technical/` -- executable code
- `03_Vault/` -- durable data / Merkle chain
- `04_Validation/` -- logs, reports, legal outputs

Keep and use this framing.

### 4.2 ISO 19011 principles mapping

The seven ISO 19011 principles (Integrity, Fair Presentation, Due Professional Care, Confidentiality, Independence, Evidence-based Approach, Risk-based Approach) are a sensible design vocabulary for OGIR. They can be used as **aspirational design principles**, not as certification requirements.

### 4.3 NIST AI RMF functional alignment

The four core functions (Govern, Map, Measure, Manage) are a reasonable way to structure an AI governance story for the project. Use them descriptively, not as compliance assertions.

### 4.4 Deception Ontology v3.9 / v3.10

The 54-pattern ontology, Shannon entropy formula, and Levenshtein/n-gram bypass detection are correctly described in the Configuration doc and match the live project. Keep this material.

### 4.5 RAG pre-processing workflow

The configuration doc's advice about converting sources to Markdown, fragmenting large files, and verifying indexing is sound and should be retained.

---

## 5. Recommendations for revising the Gem documents

### 5.1 For `Gemini Gem Knowledge Base Configuration.txt`

1. Update block count from 3,033 to "11,313 as of 2026-07-18; re-derive with `python -m src.verify_chain`".
2. Update ontology version to v3.10 (54 patterns).
3. Mark SQLite/Azure Files migration as **roadmap**, not current architecture.
4. Update the knowledge-base file list to include live files:
   - `04_Validation/OGIR_ASSESSMENT_2026-07-18.md`
   - `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
   - `04_Validation/HANDOVER_NEXT_SESSION_2026-07-18.md`
   - `04_Validation/BUILD_DIRECTIVE_NEXT_SESSION.md`
   - Remove or flag references to `reconciliation_2026-07-16.md` cloud sync claim unless it can be verified.
5. Add a "Live state caveat" rule: the Gem must not quote exact block counts, roots, or test baselines without re-deriving them at runtime.

### 5.2 For `Gem Senior AUDIT RESULTS..txt`

1. Replace "Section 336 of the Corporations Act 2001" with a correct statement: "The project aims to support audit-like reasoning; it is not a registered audit firm and is not subject to ASQM/ASA statutory requirements. These standards are used as engineering reference frameworks."
2. Remove or reframe the "cannot be audited/certified" conclusion. Use language like: "The project is not ready for statutory audit-firm certification and would require the following engineering controls before any compliance-oriented review..."
3. Remove the "70/30 rule" or present it explicitly as the operator's own heuristic, not an industry standard.
4. Correct FRIA attribution: attribute to EU AI Act, not NIST AI RMF.
5. Update the remediation roadmap to match live project state:
   - F6 (NIZK rename) is already done.
   - F7 lattice reframing is already done; deep wiring remains open.
   - F12-F17 code fixes are already done.
   - F8 ontology R1-R4 + R5 are done; R5-EXTENDED-2 and 30+ EVAL cases remain.
   - F9, F10, F11-remote remain genuinely open.
6. Cite `OGIR_ASSESSMENT_2026-07-18.md` as the authoritative current assessment.

---

## 6. What is genuinely still open in the live project

From `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` and `HANDOVER_NEXT_SESSION_2026-07-18.md`:

1. **R5-EXTENDED-2 register/hedge gate** -- HIGH priority; 2 xfailed tests in `tests/test_evaluation_cases_ai_legal.py`.
2. **Embed Makita v Sprowles citation** in `legal_affidavit_generator.py` -- MEDIUM priority.
3. **Lexical-set audit for remaining 53 patterns** -- LOW-MEDIUM priority.
4. **Add Git remote** (USB bare repo default) -- MEDIUM priority.
5. **Expand EVAL suite to 30+ real cases** -- MEDIUM priority; partially done with AI-legal cases.
6. **Wire lattice inputs to extracted evidence** (F7-deep) -- LOW priority; deferred.
7. **Refresh hard-copy reference card** -- LOW priority.
8. **Tauri code-signing** -- operator decision.
9. **Second-PC clean-host restore test** -- MEDIUM priority; needs hardware.
10. **Gmail .mbox import** -- LOW priority; needs operator export.

---

## 7. Conclusion

The two Gem documents are valuable as draft assistant specifications but **must not be used as authoritative project documentation without this reconciliation**. The live project has progressed significantly beyond the state they describe. Use this reconciliation as a correction sheet when editing them, and always prefer the live `04_Validation/` documents as the source of truth.

The most important single correction: stop presenting the project as failing statutory audit-firm certification requirements. It is a personal audit-assistance tool with strong internal governance. Its real next engineering priorities are the R5-EXTENDED-2 register gate and the Makita citation, not broad compliance certification.

---



---

## A. Verification of legal and standard claims

The statements in this reconciliation about statutes and standards were checked against primary or authoritative sources before sealing:

### A.1 Corporations Act 2001 (Cth) section 336

Primary source checked: *Corporations Act 2001* (Cth) s 336 via the Internet Archive's capture of AustLII (2026-01-10).

Verified text: "CORPORATIONS ACT 2001 - SECT 336 Auditing standards. AUASB's power to make auditing standards (1) The AUASB may, by legislative instrument, make auditing standards for the purposes of this Act or the ASIC Act."

Finding: Section 336 concerns the **Australian Auditing and Assurance Standards Board's power to make auditing standards**. It does **not** govern the appointment, removal, or remuneration of auditors, and it does **not** impose ASQM/ASA requirements on a personal software tool. The Gem Senior document's statement that "Under Section 336 of the Corporations Act 2001, corporate auditing compliance is anchored by ASQM 1 and ASQM 2" misstates the section's content and its legal effect on a non-audit-firm software project.

### A.2 NIST AI Risk Management Framework functions

Primary source checked: NIST, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1 (January 2023), extracted via jina.ai from `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`.

Verified functions: GOVERN, MAP, MEASURE, MANAGE (sections 5.1-5.4).

Finding: The four functions are correctly named in the Gem documents. However, the AI RMF does **not** use the term "Fundamental Rights Impact Assessment" (FRIA). A search of the PDF returned zero occurrences of "FRIA" or "Fundamental Rights Impact Assessment." FRIA is an **EU AI Act** concept (Article 27), not a NIST RMF concept.

### A.3 EU AI Act Article 27 -- Fundamental Rights Impact Assessment

Primary source checked: Regulation (EU) 2024/1689 (Artificial Intelligence Act), OJ L 2024/1689, extracted from `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689`.

Verified text: "Article 27 Fundamental rights impact assessment for high-risk AI systems. Prior to deploying a high-risk AI system ... deployers ... shall perform an assessment of the impact on fundamental rights that the use of such system may produce."

Finding: FRIA is correctly described as an EU AI Act requirement for high-risk AI system deployers. The Gem Senior document incorrectly attributes FRIA to the NIST AI RMF Manage function.

### A.4 Makita (Australia) Pty Ltd v Sprowles [2001] NSWCA 305

Primary source checked: Case transcript held locally at `C:\Users\justo\OneDrive\Documents\My Project\Supreme Court of New South Wales -.txt` (AustLII extract, 157,727 bytes).

Verified citation and principle: The case is [2001] NSWCA 305 (14 September 2001), per Priestley, Powell and Heydon JJA. At paragraph 85, Heydon JA summarised the requirements for expert opinion evidence under the *Evidence Act 1995* (NSW) s 79: the witness must demonstrate a field of specialised knowledge, an identified aspect of that field, training/study/experience making them an expert, and the opinion must be wholly or substantially based on that expert knowledge and applied to identified facts.

Finding: The case is the correct authority for the specialised-knowledge foundation required under s 79. It is the precedent the project's affidavit generator implicitly relies on when asserting that the operator has "direct, working knowledge of every module, formula, and threshold."

### A.5 The "70/30 rule of AI development"

No authoritative industry standard, regulatory guidance, or academic source was found establishing a "70/30 rule" as a recognised AI governance principle. It appears to be a heuristic invented in the Gem Senior document. The NIST AI RMF and EU AI Act refer to human oversight and human-in-the-loop measures, but neither prescribes a fixed 70/30 split between human reasoning and automated processing.

---

End of reconciliation.
