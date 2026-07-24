# Terms of Service — Order Get It Right (OGIR)

> **DRAFT — not legally binding until reviewed by a lawyer.**
> Created 2026-07-24. Based on the clauses in LEGAL_HANDLING_2026-07-24.md.
> Sealed to chain: `TERMS_OF_SERVICE_DRAFT_2026_07_24`

---

## 1. What OGIR Is

Order Get It Right (OGIR) is a forensic deception-pattern analysis
tool. It reads text and identifies patterns associated with
deception. It is **NOT** a legal opinion, a court ruling, or a
guarantee of truth or falsehood.

## 2. What OGIR Does

- Analyses submitted text for 55 deception patterns
- Scores the likelihood of deception (0% to 100%)
- Generates a forensic reasoning chain (per-pattern justification)
- Seals every audit to a tamper-evident Merkle chain
- Generates an affidavit under Australian Consumer Law Section 56 + Evidence Act 1995

## 3. What OGIR Does NOT Do

- Does **NOT** provide legal advice — OGIR is a tool, not a lawyer
- Does **NOT** guarantee accuracy — it flags patterns, you decide
- Does **NOT** replace a lawyer — it gives your lawyer better evidence
- Does **NOT** store your data beyond the retention period (7 years)
- Does **NOT** sell or share your data with third parties (except as required by law)

## 4. The Merkle Chain

Every audit is sealed to an append-only SHA-256 hash chain. The
chain is tamper-evident, not tamper-proof. The client acknowledges:
- The chain records what was audited and when
- The chain does not record the raw text (only hashes + metadata)
- The chain can be verified by anyone running `python -m src.verify_chain`
- The chain is the trust anchor — not the operator's word

## 5. Privacy

See our [Privacy Policy](PRIVACY_POLICY.md). OGIR complies with the
Australian Privacy Act 1988 and the Notifiable Data Breaches (NDB)
Scheme. Personal information is handled per the 13 Australian Privacy
Principles.

## 6. Liability

OGIR's liability is limited to the fee paid for the specific audit.
The operator (Justin Barnett) is **NOT** liable for:
- Consequential damages
- Lost profits
- Court outcomes
- Decisions made based on OGIR's output

OGIR is a decision-support tool, not a decision-maker. The operator
is not responsible for how you use the output.

## 7. Retention

Audit data is retained for 7 years (Australian standard for
financial/legal records). After the retention period:
- Supabase rows are deleted
- The Merkle chain blocks remain (they contain hashes, not raw text)
- The client may request deletion earlier (see Privacy Policy, APP 12)

## 8. Payment

- **Per-case audits:** fee is due before the audit runs
- **Pro licenses:** billed annually
- **Enterprise support:** billed monthly
- All prices in AUD unless stated otherwise
- Payment via card or bank transfer

## 9. Disputes

- Mediation first (via a nominated mediator)
- If mediation fails: courts of South Australia
- Jurisdiction: Commonwealth of Australia

## 10. Termination

- Either party may terminate the engagement
- Fees for work already completed are due and non-refundable
- The client may request their data at any time (APP 12 access request)

## 11. Open Source

OGIR's source code is MIT licensed. The Merkle chain runtime is
air-gapped (zero network). The operator cannot alter an audit
result after it is sealed.

## 12. Changes to These Terms

The operator will update these terms within 30 days of any material
change. Changes are sealed to the Merkle chain with event type
`TERMS_OF_SERVICE_AMENDED_<DATE>`.

---

**Operator:** Justin Barnett
**Jurisdiction:** Commonwealth of Australia (ACL + Evidence Act 1995 + Privacy Act 1988)
**Contact:** truth.project.official@gmail.com
**Effective date:** 2026-07-24 (DRAFT — pending legal review)

---

> **This is a DRAFT.** It must be reviewed by a qualified Australian
> lawyer before being published or used in client engagements.
> Budget $200-500 for the legal review (see LEGAL_HANDLING_2026-07-24.md).