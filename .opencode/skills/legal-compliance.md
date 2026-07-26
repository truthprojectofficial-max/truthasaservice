---
description: "Use when changing legal-output code or making marketing claims. Jurisdiction: Commonwealth of Australia / SA. Statutes: ACL, Evidence Act 1995, Privacy Act 1988. The engine is a Verified Processor, NOT a lawyer/court/ASIC/ISO cert. Over-claiming what the engine proves is a legal risk."
---

# Legal Compliance Skill

## What the engine IS

A **Verified Processor** — a deterministic, air-gapped forensic
analysis tool. It processes text and produces a DeceptionReport with
a tamper-evident Merkle-chain seal.

## What the engine is NOT

- NOT a lawyer
- NOT a court
- NOT ASIC
- NOT an ISO certification body
- NOT a substitute for professional legal advice

Over-claiming any of these is a legal risk. The accreditation brief
(`ACCREDITATION_AND_VERIFICATION_BRIEF_2026-07-21.md`) explicitly lists
what NOT to claim.

## Jurisdiction

**Commonwealth of Australia / South Australia**

## Key statutes

| Statute | What it covers |
|---------|---------------|
| Competition and Consumer Act 2010 Schedule 2 (ACL) | ss 18 (misleading conduct), 29 (false representations), 54 (goods match description), 55 (acceptable quality), 56 (fit for purpose), 236 (damages), 246M (non-party consumer remedies) |
| Evidence Act 1995 (NSW) s 177 | Expert certificate |
| Evidence Act 1995 (Cth) s 79 | Opinion evidence |
| Corporations Act 2001 (Cth) | Corporate conduct |
| Privacy Act 1988 (Cth) | 13 APPs + NDB scheme |

## Case law already embedded

- **Makita v Sprowles [2001] NSWCA 305** — expert evidence standard
- **ACCC v Valve [2016] FCA 196** — misleading conduct

## Privacy and NDB

- **Privacy Act 1988 (Cth)** + 13 Australian Privacy Principles (APPs)
  + Notifiable Data Breaches (NDB) scheme.
- **Retention:** 7 years (Australian standard for financial/legal records).
- **Pseudonymise** inputs. Documents not sent to cloud. No outbound
  network during audit.
- **NDB response plan** exists (`NDB_RESPONSE_PLAN_2026-07-24.md`).
- **Privacy policy** written, needs lawyer review + publishing
  (`PRIVACY_POLICY_2026-07-24.md`).

### Do NOT harvest personal data

- Names, emails, phone numbers from client docs are NOT harvested
  into the eval suite. The harvesting loop (see `ontology-and-
  calibration` skill) only takes deception patterns, not PII.

### Suspicious citations (verify before citing)

- OAIC "millisecond collection" claim — SUSPICIOUS, verify first.
- 2026 Unfair Trading Practices Bill — SUSPICIOUS, verify first.
- Do not cite these in marketing or legal docs until verified.

## Engagement discipline (for paid audits)

- **Engagement letter** required: scope, fee, timeline,
  confidentiality, chain seal reference, liability cap, termination.
- **Terms of Service:** what OGIR does/doesn't, Merkle chain is
  tamper-evident NOT tamper-proof, liability capped to fee paid,
  7-year retention, SA jurisdiction.
- **ACL demand letter + s.177 affidavit** templates exist, need
  lawyer review.
- **CLA template** for future helpers.
- **Professional indemnity insurance** before first paying client.

## The rule

The engine is a Verified Processor. It is not a lawyer, a court, or a
certification body. Over-claiming what it can prove is a legal risk.
The jurisdiction is Australia. The statutes are listed above. Legal
docs (engagement letters, ToS, affidavits) need lawyer review before
use. Personal data is never harvested. Suspicious citations are
verified before they enter marketing or legal text.