# OGIR Legal Handling — What Legals We Need to Handle

> Created 2026-07-24. Internal.
> Sealed to chain: `LEGAL_HANDLING_2026_07_24`

---

## THE LEGAL STACK — what OGIR needs and why

### 1. Business structure (TO DECIDE)

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Sole trader** (current) | $0 (ABN free) | Simple, no paperwork | Personal liability — if sued, Justin's assets are exposed |
| **Sole trader + trading name** | $0 | Can trade as "Order Get It Right" | Same liability |
| **Pty Ltd** | ~$500-900 to set up + $50/yr ASIC review | Limited liability, professional | More paperwork, ASIC lodgements, separate tax return |

**Recommendation:** Start as sole trader (you already have an ABN
or can get one free at abr.gov.au). When you have paying clients,
register a Pty Ltd to cap your liability. Talk to an accountant.

**Action needed:** Register ABN if not done (free, 5 min at
https://www.abr.gov.au). Register "Order Get It Right" as a
business name at https://asic.gov.au ($39 for 3 years or $92 for 5 years).

### 2. Terms of Service (TO WRITE)

You need a Terms of Service that clients agree to when they submit
text for auditing. It must cover:

- [ ] **What OGIR does:** forensic deception-pattern analysis on text. NOT a legal opinion. NOT a court ruling. NOT a guarantee of truth or falsehood.
- [ ] **What OGIR does NOT do:** provide legal advice, replace a lawyer, guarantee accuracy, store client data beyond the retention period, share data with third parties (except as required by law).
- [ ] **The Merkle chain:** every audit is sealed to an append-only chain. The chain is the trust anchor. The client acknowledges the chain is tamper-evident, not tamper-proof.
- [ ] **Privacy:** links to the Privacy Policy (already written at `PRIVACY_POLICY_2026-07-24.md`). NDB scheme compliance.
- [ ] **Liability cap:** OGIR's liability is limited to the fee paid for the audit. Not liable for consequential damages, lost profits, or court outcomes.
- [ ] **Retention:** 7 years (Australian standard for financial/legal records). After that, data is deleted from Supabase; the chain blocks remain (they contain hashes, not the raw text).
- [ ] **Payment:** per-case fees are due before the audit runs. Pro/Enterprise billed monthly.
- [ ] **Disputes:** mediation first (via a nominated mediator), then the courts of South Australia.
- [ ] **Jurisdiction:** Commonwealth of Australia, South Australia.

**Template:** use https://termly.io or https://getterms.io to generate
the base, then customize with the OGIR-specific clauses above.

### 3. Privacy Policy (DONE — review needed)

Already written at `04_Validation/PRIVACY_POLICY_2026-07-24.md`.
Covers 13 APPs + NDB scheme. Needs:
- [ ] Published on the website (copy to `docs/PRIVACY_POLICY.md` for GitHub Pages)
- [ ] Linked from the Tauri app (Help → Privacy Policy)
- [ ] Linked from the Terms of Service
- [ ] Reviewed by a lawyer before public launch

### 4. Engagement Letter (TO WRITE)

For paid audits, you need an engagement letter that the client signs
before you run the audit. It must cover:
- [ ] Scope (what text, what analysis, what deliverables)
- [ ] Fee (flat rate or per-case)
- [ ] Timeline (when the audit will be delivered)
- [ ] Confidentiality (both ways — you won't share their text, they won't share your report)
- [ ] Chain seal (the audit will be sealed to the Merkle chain with a block hash they can verify)
- [ ] Limitation of liability (same as Terms of Service)
- [ ] Termination (either party can terminate, fees for work done are due)

**Template:** see https://www.clio.com/resources/legal-document-templates/

### 5. Affidavit Template (DONE)

The `legal_affidavit_generator.py` already generates affidavits under
ACL Section 56 + Evidence Act 1995. The template includes:
- The operator's name (Justin Barnett)
- The statement audited
- The patterns detected
- The deception score
- The chain block hash
- The date + ISO timestamp

**Needs:**
- [ ] Reviewed by a lawyer — is the affidavit format acceptable in SA courts?
- [ ] The operator's signature (wet ink or digital?)

### 6. ACL Demand Letter (DONE)

The `acl_demand_generator.py` generates ACL Section 56 demand letters.
Already working. Needs:
- [ ] Reviewed by a lawyer — is the demand format current?

### 7. IP Assignment (DONE)

`INTELLECTUAL_PROPERTY_RIGHTS.txt` covers copyright. The MIT license
(now in `LICENSE`) covers open-source licensing. Needs:
- [ ] If a contributor (helper) is hired: they must sign a Contributor
  License Agreement (CLA) assigning their IP to the project. Template
  at https://cla-assistant.io/ or a custom one.

### 8. Insurance (TO DECIDE)

| Type | Cost/yr | What it covers | Needed? |
|------|---------|---------------|---------|
| Professional indemnity | ~$500-1500/yr | If a client sues because the audit was wrong | Yes, once you have paying clients |
| Public liability | ~$300-600/yr | If someone is injured on your premises | No (you work from home, no clients on site) |
| Cyber insurance | ~$300-1000/yr | If the chain/DB is breached | Maybe, once you have client data in Supabase |

**Recommendation:** Get professional indemnity insurance before your
first paying client. Ask an insurance broker in Whyalla or use
https://www.publicliabilityinsurance.com.au/ for quotes.

### 9. Tax (TO SET UP)

- [ ] ABN registered (free at abr.gov.au)
- [ ] Business name registered (if using "Order Get It Right")
- [ ] GST registration (only if turnover > $75,000/yr — not yet)
- [ ] Keep receipts for: cert ($429.99), domain ($10), Ollama ($20/mo), Supabase ($25/mo), insurance
- [ ] Talk to a tax agent (first consultation is often free)

### 10. External Legal Counsel (TO FILL)

You need a lawyer for:
- Reviewing the Terms of Service + engagement letter
- Reviewing the affidavit format for SA courts
- If a client disputes an audit result
- If a data breach triggers NDB notification

**How to find one:**
- Law Society of South Australia: https://www.lawsocietysa.com.au/ (find-a-lawyer)
- Legal Aid SA (free initial consult): https://www.lsa.sa.gov.au
- Community Legal Centre SA: https://www.clcsa.org.au

**Budget:** $200-500 for an initial review of ToS + affidavit template.
Worth it before public launch.

---

## LEGAL CHECKLIST (before public launch)

- [ ] ABN registered (free)
- [ ] Business name registered ($39/3yr at ASIC)
- [ ] Terms of Service written + published on website
- [ ] Privacy Policy published on website (already written, just needs to go live)
- [ ] Engagement letter template written
- [ ] Affidavit template reviewed by a lawyer
- [ ] ACL demand letter reviewed by a lawyer
- [ ] Professional indemnity insurance purchased
- [ ] External legal counsel identified (fill in contacts/legal.json)
- [ ] CLA template ready (if hiring a helper)