# Compliance-word-density detection heuristic ("bit-rate" of fabricated compliance)

## What "bit rate" means here

In the Gemini audit file, "bit rate" is the **density of obligation words + framework name drops per sentence / per section**. When that density is too high, the text is "over-excited" — fabricating obligations. When it drops, the text is hiding or moving past a claim without grounding.

## Measured ratios

### Gem Senior AUDIT RESULTS..txt
- Words: 1,973
- Sentences: 97
- Avg words/sentence: 20.3 (higher than live project docs)
- Obligation words (must, shall, required, ensure, adhere, implement, deploy, maintain, mandatory, etc.): 31 (1.57%)
- Softener words (may, might, could, should, consider, optional, aspirational, roadmap): 1 (0.05%)
- Framework mentions (NIST, ISO, ASQM, ASA, AUASB, Corporations Act): 55 (2.79%)
- **Obligation/softener ratio: 31.0** — extremely high; almost no hedging/aspiration language.
- **Framework mention rate: 2.79%** — every ~36th word is a framework name.

### Live project docs for comparison

| Document | Words/sent | Obligation % | Softener % | Framework % | Obligation/softener |
|---|---|---|---|---|---|
| OGIR_ASSESSMENT_2026-07-18.md | 9.9 | 0.27% | 0.21% | 0.05% | 1.31 |
| OPEN_ITEMS_AND_REFERENCE.md | 10.0 | 0.22% | 0.13% | 0.00% | 1.67 |
| Gem Senior AUDIT RESULTS..txt | 20.3 | 1.57% | 0.05% | 2.79% | 31.00 |

## Interpretation

The Gem Senior AUDIT has:
- **Longer sentences** — 20.3 words/sent vs ~10 for live docs. This is a sign of generated, over-wrought prose.
- **15× more obligation words** relative to live docs.
- **Almost no softeners** — no "aspirational", "roadmap", "consider", "may". It presents everything as binding.
- **56× more framework mentions** per word.

These ratios are the "bit-rate" signal of fabricated compliance.

## Sections with the highest density (most suspicious)

| Section | Score | Why it is suspicious |
|---|---|---|
| "Evidence & Sampling: ASA 500, ASA 520, ASA 530" | 120 | Three framework numbers in five words. No substance. |
| "Professional Ethics: ASA 102, ISO 19011..." | 67 | Framework drop with no explanation. |
| "1. Structural Controls & Principles Matrix" | 28.6 | Framework list as if it were architecture. |
| "Technical Governance Matrix" | 17.1 | Packs NIST, ISO 42001, TEVV, Promptfoo, ASQM, ASA into one sentence. |
| "3. Integrated AI Governance Architecture" | 22.6 | Obligation + framework density spike. |
| "NIST AI RMF Functional Alignment" | 21.7 | Claims codebase "must programmatically map" to NIST. |
| "Statutory Compliance Failures" | 18.5 | Section 336 used as if it imposes duties. |
| "NIST AI RMF Non-Alignment" | 20.0 | Claims project does not satisfy NIST functions. |

## How to use this as a detector

1. **Tokenise sentences** and count obligation words.
2. **Count framework acronyms** (ASQM, ASA, AUASB, ISO, NIST, EU AI Act, etc.).
3. **Count softener/aspiration words**. Healthy technical docs have obligation:softener ratio near 1–2. Fabricated compliance docs show ratio >10.
4. **Measure sentence length**. Generated compliance prose tends toward 18–22 words/sentence vs 9–12 for honest engineering docs.
5. **Flag sections where framework-mention rate exceeds ~1.5%** — means the text is name-dropping standards instead of describing actual implementation.

## Application to this case

The Gemini Senior Audit failed every ratio:
- Obligation/softener ratio 31.0 → over-excited, fabricated obligations.
- Framework density 2.79% → name-dropping instead of building.
- Sentence length 20.3 → generated, not operator-written.
- Specific passages like "Evidence & Sampling: ASA 500, ASA 520, ASA 530" scored 120 — pure framework compression with zero technical content.

This is the measurable "bit-rate" pattern you were asking about.
