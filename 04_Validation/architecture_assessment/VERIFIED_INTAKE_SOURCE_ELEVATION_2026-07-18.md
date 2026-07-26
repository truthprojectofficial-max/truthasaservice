# Verified intake source extraction for EVAL suite expansion

## Files now available on disk

1. **Verified.docx** (`C:\Users\justo\OneDrive\Documents\My Project\Verified.docx`)
   - 40,534 characters, 153 sentences.
   - Topic: "Verified Digital Information Environments and Factual Retrieval Systems Prior to 2021".
   - Source type: academic/editorial survey text.
   - Expected use: **TRUE NEGATIVE** baseline for pre-2021 editorial language.
   - Already referenced in `04_Validation/pre_2021_reference_audit_intake.txt`.

2. **Williams AI Transcript** (`data/inbox/Williams_Ai_Transcript.txt`)
   - 59,484 characters, 116 lines.
   - Topic: AI-generated oral argument in Williams v. Alabama.
   - Expected use: **TRUE NEGATIVE** legal register case (polite AI legal text).
   - Note: scanner currently fires DD-004, DD-006, DD-011, DD-015, DD-019, DD-027, DD-041, DD-043; this was the R5-EXTENDED-2 target.

3. **Claude Legal Commentary** (`data/outbox/INTAKE_HELD_AUDITED_2026-07-18_CLAUDE_LEGAL.json`)
   - Topic: human-written commentary about Claude AI in legal oral argument.
   - Current scanner: DD-006, DD-041 fire at 0.5174 probability.
   - Expected use: **TRUE NEGATIVE** writerly-hedge case.

4. **AvePoint Intake** (`data/outbox/INTAKE_HELD_AUDITED_2026-07-18_AVEPOINT.json`)
   - Clean intake, 0 patterns fired, 0.0 deception probability.
   - Expected use: **TRUE NEGATIVE** clean case.

5. **SEED_001 sample audit intake** (`data/inbox/SEED_001_sample_audit_intake.txt`)
   - Small synthetic deceptive warranty claim.
   - Already used in tests.

## What can be lifted for EVAL cases

### From Verified.docx (TRUE NEGATIVE pre-2021 editorial)

Extract short sentences that contain no deception markers:

- "The Associated Press (AP), founded in 1846, maintained its position as a trusted provider of unbiased news through a consistent focus on accuracy and frame-by-frame analysis of digital content."
- "The Wikipedia editing model was unique in its transparency."
- "The Digital Object Identifier (DOI) became the cornerstone of grounded repeatable use as information by providing a persistent link to a document regardless of changes in the hosting website's URL structure."
- "Trove, launched in 2009 by the National Library of Australia (NLA), exemplified a verified trusted source of honesty through longstanding publicly known representation."
- "By the turn of the 21st century, most reputable journals had adopted peer review as the primary mechanism for factual validation."

### From Williams AI transcript (TRUE NEGATIVE legal register)

Extract polite but honest legal argument excerpts:

- "Justice Jackson, you're exactly right. I apologize for any confusion. Felder's analysis is dispositive here, and Alabama's law does not require exhaustion. Let me clarify. We implement the Section 1983 framework."
- "Justice Barrett, exactly. The question is whether the state-litigation requirement conflicts with Section 1983."

### From Claude legal commentary (TRUE NEGATIVE writerly hedge)

- "This is clearly better than what a human lawyer could come up with on the spot. If you gave me six hours, I doubt I could do better. Maybe one can offer a different flavor of this argument."

### Adversarial TRUE POSITIVE variants

Create adversarial versions by injecting false certainty / fabrication into the same register:

- Williams register used to lie:
  "JUSTICE JACKSON, you're exactly right. I apologize for any confusion. Let me clarify. The cases clearly establish that the product is 100% accurate and has never failed. I can assure you that all tests confirm full compliance."
- Claude register used to fabricate:
  "This is clearly the controlling authority. If you gave me six hours, I doubt I could find a better case. Maybe one can offer a different flavor, but Smith v. Jones [2023] HCA 1 is directly on point and has never been distinguished."

## Recommended next step

Use these verified on-disk sources to create 20–30 new EVAL cases. Do not hunt external websites yet — the project already has enough held material to expand the suite substantially, and this material is already operator-verified and chain-sealed.

Proposed file: `tests/test_evaluation_cases_extended.py`
- Cases EVAL-009 to EVAL-028 from synthetic pattern proposals.
- Cases EVAL-029+ from the held verified intakes above.
- Mix: 60% TRUE NEGATIVE (clean editorial / legal register), 40% TRUE POSITIVE (adversarial variants + known deceptive patterns).
