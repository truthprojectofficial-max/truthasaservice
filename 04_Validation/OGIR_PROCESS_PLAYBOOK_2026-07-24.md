# OGIR Process — How This Business Actually Works

> Created 2026-07-24. Internal. The operator's playbook.
> Every step from client contact to sealed delivery to recall.
> Sealed to chain: `OGIR_PROCESS_PLAYBOOK_2026_07_24`

---

## THE 8-STAGE FLOW

```
1. Intake → 2. Triage → 3. Seal → 4. Audit → 5. Affidavit → 6. Review → 7. Deliver → 8. Archive
```

### Stage 1: Intake

**What happens:** Client contacts operator (email, phone, portal).
Client submits text/document to be audited. Operator creates a case.

**Who:** Client submits. Operator receives.

**Inputs:**
- Client name + contact
- Document to audit (text, PDF, email, contract)
- Category (Technical, Governance, Forensic)
- Optional: product evidence (price, spec, warranty)

**Output:** Case card in the "Inbox" column of the trial board.

**Chain:** `CASE_CREATED` block sealed with client name + case ID.

---

### Stage 2: Triage

**What happens:** Operator reviews scope. Conflict check (has the
operator audited this client/party before?). Accept or reject.

**Who:** Operator (Auditor role).

**Checklist:**
- [ ] Is this within OGIR's scope? (deception detection on text)
- [ ] Conflict of interest? (prior relationship with the party?)
- [ ] Engagement letter needed? (yes for paid work, no for pro bono)
- [ ] Category correct? (Technical, Governance, Forensic)

**Output:** Case moves to "Sealed" (accepted) or "Rejected" (with reason).

**Chain:** `CASE_TRIAGED` block sealed with decision + reason.

---

### Stage 3: Seal

**What happens:** Engagement locked. Fact created in the chain.
The audit is now a sealed event — it cannot be silently altered.

**Who:** Operator (Auditor role).

**What:**
1. POST to `/api/facts` with category + statement + source
2. Fact gets an ID + is sealed to the chain
3. Case moves to "Audit Running"

**Chain:** `FACT_ADDED` block (automatic via the API).

---

### Stage 4: Audit

**What happens:** The 4-gate pipeline runs on the submitted text.

**The 4 gates:**
1. **Deception** — 55-pattern scanner + Shannon entropy
2. **BBFB** — LAW multiplicative veto + GRACE quadratic penalty + FRUIT weighted product
3. **Optionality** — deception-adjusted optionality index (NOT a valuation — F7)
4. **Decision** — GO / REVIEW_REQUIRED / REFUSED / REJECT

**Who:** The engine (automated). Operator monitors.

**What the client sees:** The "What flagged" read-out — each fired
pattern as a card with:
- Pattern ID + name (DD-001 Clarity Shield)
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Confidence percentage
- Which indicators matched

**What the client can do:** Submit an explanation ("the warranty
terms were in a separate attachment"). This is sealed as their
statement to the chain. It does NOT change the verdict — it
appends their context.

**Chain:** `AUDIT_CYCLE_COMPLETE` block with deception score + verdict.

---

### Stage 5: Affidavit

**What happens:** Legal affidavit generated from the pipeline output.

**Who:** Operator (Auditor role) generates. Operator reviews.

**What:**
1. POST to `/api/affidavit` or use the CLI
2. Affidavit text generated (ACL Section 56 + Evidence Act 1995)
3. Operator reviews for accuracy
4. Case moves to "Client Review"

**Chain:** `AFFIDAVIT_GENERATED` block.

---

### Stage 6: Client Review

**What happens:** Client sees the flagged patterns + the affidavit
draft. Client can:
- Accept the findings
- Submit an explanation (sealed to chain, doesn't change verdict)
- Dispute (triggers a re-audit with the explanation as context)

**Who:** Client reviews. Operator waits.

**Chain:** `CLIENT_REVIEW_STARTED` block. If explanation submitted,
`FACT_ADDED` with source `client_explanation`.

---

### Stage 7: Deliver

**What happens:** Final report + affidavit delivered to client.
The delivery itself is sealed.

**Who:** Operator delivers.

**Delivery method:**
- Email (PDF attachment)
- Portal download (if Supabase wired)
- Paper (printed, signed, mailed)
- USB (for high-security clients)

**Chain:** `CASE_DELIVERED` block with delivery method + hash of delivered content.

**Supabase:** A row in `document_requests` is created automatically
(recall tracking). The `documents` table stores the content +
content_hash + chain_block_hash for future retrieval.

---

### Stage 8: Archive

**What happens:** Case moves to cold storage. Indexed for recall.
Merkle proof retained. Retention period starts (per Privacy Act).

**Who:** Operator (DPO role) archives.

**Retention:** 7 years (Australian standard for financial/legal records).

**Recall:** When someone requests a copy (APP 12 access request):
1. Search `documents` table by keyword (`search_documents('invoice warranty')`)
2. Retrieve the document + its chain block hash
3. Verify: `python -m src.verify_chain` confirms the block is in the chain
4. Deliver: the document + the Merkle proof (block hash + chain root)
5. Seal: `DOCUMENT_RETRIEVED` block recording who requested what

**Chain:** `CASE_ARCHIVED` block.

---

## THE OPERATOR'S DAILY RITUAL

### Morning (5 min)
```
1. Verify the chain
   $env:PYTHONPATH="02_Technical"; python -m src.verify_chain
   # MUST be MATCH

2. Read the bark log
   cat 04_Validation/scripts/last_seal.log | Select-Object -Last 5

3. Check the trial board (Trello or Supabase cases table)
   # Any new cases in Inbox? Any in Client Review waiting on you?
```

### Per-case (15-30 min)
```
1. Triage the intake → accept or reject
2. Run the pipeline (POST to /api/orchestrator/process or use the Tauri app)
3. Review the flagged patterns
4. Generate the affidavit
5. Deliver to client
6. Seal the delivery
```

### Weekly (30 min)
```
1. Run tests: python -m pytest tests/ -q
2. Supabase backup: supabase db dump --data-only -f backup.sql
3. Check Cloudflare Worker health: curl https://update.ordergetitright.com/health
4. Check for unexpected Supabase signups
5. Git push to GitHub
```

### Monthly (15 min)
```
1. Check Supabase usage (DB size, MAU)
2. Check Cloudflare analytics (requests, bandwidth)
3. Check GitHub Actions (any failures?)
4. Review the tick list for any overdue items
5. Verify chain still MATCH
```

---

## THE BUSINESS MODEL

| Tier | Price | What you get |
|------|-------|-------------|
| **Free (open source)** | $0 | Local CLI, 55-pattern scanner, Merkle chain, self-verify |
| **Pro (signed desktop)** | $49/yr | Signed Tauri binary, auto-updater, Drive import, Supabase sync |
| **Per-case (API)** | $25/case | Run an audit via API, get sealed affidavit + Merkle proof |
| **Enterprise (support)** | $500/mo | Priority support, custom ontology, on-site training, SLA |

Revenue: the engine is free and verifiable. The signed binary is
convenience. Per-case API is try-before-you-buy. Enterprise support
is where the real money is.

---

## THE BILLING CYCLE

| Service | Cost | Frequency | Auto? |
|---------|------|-----------|-------|
| Cloudflare domain | ~$10/yr | Annual | No (manual renewal) |
| Cloudflare Workers | $0 (free tier) | — | — |
| Supabase Free | $0 | — | — |
| Supabase Pro | $25/mo USD | Monthly | Yes (card auto-charge) |
| Ollama Cloud Pro | $20/mo | Monthly | Yes (card auto-charge) |
| GitHub | $0 (public repo) | — | — |
| SignMyCode/Certera | $429.99/yr | Annual | No (manual renewal) |
| Apple Developer | $99/yr | Annual | No (not enrolled) |

**Monthly burn (current):** ~$20/mo (Ollama) + $0 (everything else on free tier)
**Monthly burn (after Pro upgrade):** ~$45/mo ($20 Ollama + $25 Supabase)
**Annual burn:** ~$540/yr current, ~$970/yr after upgrades

---

## THE CONTACTS (who does what)

See `contacts/` directory. 9 roles, all filled by Justin initially:

1. **Operator/Owner** — Justin (legal liability, signing authority)
2. **Auditor** — Justin (runs the pipeline, seals blocks)
3. **Technical Contact** — Justin (infrastructure, build)
4. **DPO** — Justin (privacy/access requests, retention)
5. **Legal Contact** — TO FILL (external counsel)
6. **Client Contact** — per case (client side)
7. **Supplier/Vendor** — Cloudflare, Supabase, Google, GitHub, SignMyCode, Ollama
8. **Emergency** — Justin (primary), TO FILL (backup)
9. **Witness/Notary** — TO FILL (optional, paper trust anchor)

---

**This document is the operator's playbook. Read it. Follow it. Seal everything.**