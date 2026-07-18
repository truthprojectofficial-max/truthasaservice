# Sample intake / EVAL case reference sites (extracted from `codex next headach.txt`)

## What the file contains

`C:\Users\justo\OneDrive\Documents\My Project\codex next headach.txt` is a Hermes/Codex session transcript. It does NOT contain clickable reference URLs. It contains **named public-domain case studies** and **synthetic test-case proposals** that Codex mapped to the 54-pattern ontology.

## Public-domain cases identified in the transcript

| Case / Source | Jurisdiction | Pattern tested | Use |
|---|---|---|---|
| **Mata v. Avianca, Inc.**, 22-cv-1461 (PKC) (S.D.N.Y. June 22, 2023) | US Federal Court | DD-036 fake legal citation | TRUE POSITIVE |
| **UK ChatGPT fake case** (lawyer cited hallucinated authorities) | UK | DD-036 fake authority | TRUE POSITIVE |
| **Williams v. Alabama** AI oral argument | US / Alabama | Politeness register in legal text | TRUE NEGATIVE |
| **Claude legal commentary** (held on disk as `INTAKE_HELD_AUDITED_2026-07-18_CLAUDE_LEGAL.json`) | General | Writerly hedges | TRUE NEGATIVE |
| **Australian Federal Court / NSW / Victorian Supreme Court AI practice notes 2024-2025** | Australia | Honest AI disclosure | TRUE NEGATIVE |
| **BC lawyer ChatGPT fake family-law cases** (Law Society of BC guidance) | Canada | DD-036 fake authority | TRUE POSITIVE |
| **USPTO AI-generated trademark specimens** | US | DD-040 / DD-052 phantom modality | TRUE POSITIVE |
| **Published Australian consumer-law judgments and ACCC regulator releases** | Australia | Various consumer-law patterns | Mixed |

## Synthetic pattern-based cases proposed (EVAL-009 to EVAL-028)

Codex also proposed 20 fully synthetic cases mapped to specific patterns:

- DD-010 Lie of Spoliation
- DD-012 Shadow Omission
- DD-017 Mary Hell Scenario
- DD-040 Phantom Capability Declaration
- DD-036 Stochastic Plausibility Spoofing
- DD-015 Sycophancy Bias
- DD-028 Predatory Loop via Clarification Requests
- DD-029 Institutional Gaslighting
- DD-031 Truncated Convergence Evasion
- DD-052 Phantom Modality Injection
- DD-053 Bureaucratic Redirection
- DD-005 Information Blackmail
- DD-003 Run-for-the-Line Syndrome
- DD-027 Apology Theater Escalation
- Plus technical/legal true negatives for DD-041, DD-054 gates

## Actual reference documents on disk

The transcript mentions these held files inside the project:

- `03_Vault/affidavit_transcript.txt` — Williams AI oral argument transcript.
- `04_Validation/INTAKE_HELD_AUDITED_2026-07-18_CLAUDE_LEGAL.json` — Claude legal commentary.
- `04_Validation/pre_2021_reference_audit_intake.txt` — pre-2021 reference corpus.

## Where to get more real cases

The transcript suggests these source categories, but no specific URLs:

1. **Australian Federal Court / State Supreme Court practice directions on AI use** (2024-2025).
2. **ACCC media releases and guidance** on consumer guarantees and misleading conduct.
3. **AustLII** (`www.austlii.edu.au`) for published judgments under ACL, s 18, s 54.
4. **UK / Canadian Law Society guidance** on AI hallucination in legal research.
5. **US Federal Court orders** for Mata v. Avianca and similar AI-fabrication cases.

## Bottom line

There is no single "reference sites" file. The case material is either:
- Already held in the project vault (`03_Vault`, `04_Validation`),
- Publicly named (Mata v. Avianca, Williams v. Alabama),
- Or proposed as synthetic cases.

For the EVAL-suite expansion, the fastest path is to use the **held transcripts plus the synthetic cases**, because the public URLs were never collected into a list.
