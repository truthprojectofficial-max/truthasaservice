# OGIR Business Model Research + Trial Board Flow + Recall Indexing + Contacts

> Created 2026-07-24. Internal planning doc.
> Sealed to chain: `BUSINESS_MODEL_AND_WORKFLOW_RESEARCH_2026_07_24`

---

## PART 1: Business Models to Study

### Companies that sell forensic/audit/compliance tools

| Company | URL | Model | Free tier | Paid tier | OGIR takeaway |
|---------|-----|-------|-----------|-----------|---------------|
| **SafetyCulture (iAuditor)** | https://safetyculture.com | Freemium audit SaaS, per-user/mo | Limited audits, basic templates | $/user/mo, unlimited audits, analytics | **Closest AU analog.** Free engine + paid analytics/certification |
| **Nuix** | https://www.nuix.com/pricing | Per-GB + per-seat | None (demo-gated) | Per-GB processed, per-investigator seat | Per-audit-case pricing model |
| **Verafin** | https://verafin.com | Enterprise SaaS, sales-led | None | Per-institution annual contract | API risk-score tier = per-decision billing |
| **Chainlink** | https://chain.link | Free docs + paid production | Full docs, sandbox free | Per-call in LINK token | Free verification, paid production use |
| **Logikull** | https://www.logikull.com | Freemium e-discovery | Capped documents | Per-case monthly | Free trial → per-case billing |
| **ComplianceQuarter** | https://compliancequarter.com.au | Per-module SaaS | None | Per-module/mo | AU compliance market reference |

### Recommended OGIR business model

**Open core + per-case + support contracts:**

| Tier | Price | What you get |
|------|-------|-------------|
| **Free (open source)** | $0 | Local CLI engine, 55-pattern scanner, Merkle chain, self-verify. MIT licensed. Run it yourself, verify it yourself. |
| **Pro (signed desktop)** | $49/yr | Signed Tauri binary (no SmartScreen warning), auto-updater, Google Drive import, Supabase sync. For operators who want the polished tool, not the build-from-source path. |
| **Per-case (API/affidavit)** | $25/case | Run an audit via the API, get a sealed affidavit + Merkle proof. For one-off use without installing anything. |
| **Enterprise (support contract)** | $500/mo | Priority support, custom ontology tuning, on-site training, SLA, custom integrations. For firms doing >20 audits/mo. |

**Revenue logic:** The engine is free and verifiable (trust model preserved). The signed binary is convenience. Per-case API is the "try before you buy" path. Enterprise support is where the real money is — same as Red Hat.

### Sites to study paperwork/policy/product flows

| # | Site | What to study | URL |
|---|------|-------------|-----|
| 1 | Termly | Privacy/terms/EULA/disclaimer policy generators | https://termly.io/resources/templates/ |
| 2 | Clio | Legal intake forms, engagement letters, case management templates | https://www.clio.com/resources/legal-document-templates/ |
| 3 | monday.com | Audit-firm kanban boards, client onboarding workflows | https://monday.com/templates |
| 4 | Trello | Law-firm, consulting flow boards | https://trello.com/templates |
| 5 | ClickUp | Consulting/audit client-onboarding templates | https://clickup.com/templates |
| 6 | iubenda | Privacy/cookie policy generator (EU) | https://www.iubenda.com/ |
| 7 | GetTerms.io | One-click privacy + terms generator | https://getterms.io/ |
| 8 | Termageddon | Auto-updating privacy policies | https://termageddon.com/ |
| 9 | Process Street | SOP/checklist/compliance process templates | https://www.process.st/checklists/ |
| 10 | SafetyCulture | AU audit/checklist templates (closest analog) | https://safetyculture.com/ |

---

## PART 2: Trial Board Flow (intake → delivery → archive)

### Suggested OGIR kanban columns

```
Inbox → Triage → Sealed → Audit Running → Affidavit Draft → Client Review → Delivered → Archive
```

| Column | What happens | Who | Trigger to next |
|--------|-------------|-----|-----------------|
| **Inbox** | Client submits text/file via intake form or email | Client | Operator triages |
| **Triage** | Operator reviews scope, conflict check, accepts or rejects | Operator (Auditor role) | Engagement letter signed → Sealed |
| **Sealed** | Engagement locked, chain block sealed, fact created | Operator (Auditor) | Run pipeline → Audit Running |
| **Audit Running** | 4-gate pipeline executes: Deception → BBFB → Optionality → Decision | Engine (automated) | Pipeline completes → Affidavit Draft |
| **Affidavit Draft** | Legal affidavit generated from pipeline output | Operator (Auditor) | Operator reviews → Client Review |
| **Client Review** | Client sees the flagged-patterns read-out, can submit explanation | Client | Client approves or disputes → Delivered |
| **Delivered** | Final report + affidavit sealed to chain, delivered to client | Operator (Auditor) | Retention period elapses → Archive |
| **Archive** | Cold storage, indexed for recall, Merkle proof retained | Operator (DPO role) | Retrieval request → Recall flow |

### How to implement (simplest path)

**Option A — Trello board (free, visual):**
- Create board "OGIR Cases"
- 8 columns as above
- Each case = a card
- Labels: GO / REVIEW_REQUIRED / REFUSED / REJECT
- Power-up: Custom Fields for fact_id, chain_block, client_name

**Option B — Supabase table (already wired):**
- Add a `cases` table: `id, client_id, status, fact_id, chain_block, created_at, sealed_at, delivered_at, archived_at`
- Status enum: `inbox, triage, sealed, running, draft, review, delivered, archived`
- RLS: client can only see their own cases
- Every status change seals a `CASE_STATUS_CHANGED` block

**Option C — OGIR UI (built into the Tauri app):**
- Add a "Cases" tab to the Tauri UI
- Reads from the Supabase `cases` table
- Shows the kanban columns as cards
- Operator drags cards between columns
- Each drag seals a chain block

---

## PART 3: Recall / Indexing System

### The problem

When someone (client, court, regulator) requests a copy of an audit
OGIR did, you need to find it and retrieve it. The chain has 40,860+
blocks. You can't scroll through them manually.

### Recommended approach — Postgres FTS + Merkle proof

**Indexing:** Every audit that runs through the pipeline creates:
1. A chain block (sealed, immutable) — already exists
2. A Supabase `scans` row (already exists: `id, customer_id, result, created_at`)
3. An affidavit (if generated) — stored as text in the `affidavits` table

**Add a `documents` table for the recall index:**
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id UUID REFERENCES scans(id),
  client_id UUID REFERENCES customers(id),
  document_type TEXT NOT NULL,  -- 'audit_report', 'affidavit', 'evidence', 'explanation'
  content_text TEXT,            -- the full text for search
  content_hash TEXT NOT NULL,   -- SHA-256 of the content
  chain_block_index INT,        -- the Merkle chain block that sealed this
  chain_block_hash TEXT,        -- the block's current_hash
  created_at TIMESTAMPTZ DEFAULT now(),
  searchable tsvector GENERATED ALWAYS AS (to_tsvector('english', content_text)) STORED
);
CREATE INDEX documents_search_idx ON documents USING GIN(searchable);
```

**Retrieval workflow:**
1. Requester contacts operator (email, phone, portal)
2. Operator searches: `SELECT * FROM documents WHERE searchable @@ to_tsquery('invoice warranty') AND client_id = $1`
3. Operator retrieves the document + its chain block hash
4. Operator verifies: `python -m src.verify_chain` confirms the block is in the chain
5. Operator delivers: the document + the Merkle proof (block hash + chain root)
6. Operator seals a `DOCUMENT_RETRIEVED` block recording who requested what

**Tracking table:**
```sql
CREATE TABLE document_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  requester_name TEXT NOT NULL,
  requester_contact TEXT NOT NULL,
  document_id UUID REFERENCES documents(id),
  request_reason TEXT,
  delivered_at TIMESTAMPTZ,
  delivery_hash TEXT,  -- hash of what was delivered
  created_at TIMESTAMPTZ DEFAULT now()
);
```

Every retrieval is itself an auditable event, sealed to the chain.

### Australian Privacy Act s12 (access requests)

Under APP 12, any individual can request access to personal
information OGIR holds about them. The operator must:
1. Respond within a "reasonable period" (30 days is the benchmark)
2. Provide a copy of the information
3. May charge a reasonable access fee
4. May refuse only on specific grounds (unreasonable, unlawful,
   commercial-sensitive)

The `document_requests` table above is the tracking mechanism for
compliance with APP 12.

---

## PART 4: Contacts + Roles Registry

### Roles (all filled by the operator initially, separated in the chain for audit clarity)

| Role | Responsibility | Why define it even if solo |
|------|---------------|---------------------------|
| **Operator / Owner** | Business entity, legal liability, signing authority | Legal anchor |
| **Auditor** | Runs the 4-gate pipeline, seals blocks | Separates "who audited" from "who owns" |
| **Technical Contact** | Runtime, build, Tauri shell, infrastructure | Incident/breach response point |
| **Data Protection Officer (DPO)** | Handles s12/APP12 access requests, retention, privacy | Required by Privacy Act 1988 |
| **Legal Contact** | External counsel for affidavits, disputes | Can't self-represent on own disputes |
| **Client Contact** | Per-engagement primary contact (client side) | Distinct from operator |
| **Supplier / Vendor** | Cloudflare, Supabase, Google, SignMyCode, Ollama | Supply-chain mapping |
| **Emergency Contact** | Breach notification, chain-compromise response | IR plan requirement |
| **Witness / Notary** (optional) | Hardcopy Merkle-root card witness | Paper trust anchor integrity |

### Current contacts (operator fills in)

```
OPERATOR / OWNER:
  Name:     Justin Barnett
  Email:    truth.project.official@gmail.com
  Phone:    0480569941
  Address:  20 Loveday St, Whyalla Norrie SA 5608
  Role:     Operator, Auditor, Technical Contact, DPO

LEGAL CONTACT:
  Name:     [TO FILL — external counsel]
  Email:    [TO FILL]
  Phone:    [TO FILL]
  Jurisdiction: Commonwealth of Australia

SUPPLIER / VENDOR CONTACTS:
  Cloudflare:     https://dash.cloudflare.com (account: truth.project.official)
  Supabase:       https://qqbrpqdbxhypkvvsjble.supabase.co
  Google OAuth:   console.cloud.google.com (project: ordergetitright)
  SignMyCode:     support@signmycode.com (Customer ID: #1015571)
  Ollama:         https://ollama.com/settings
  GitHub:         github.com/truthprojectofficial-max/truthasaservice

EMERGENCY CONTACT:
  Name:     Justin Barnett
  Phone:    0480569941
  Role:     Breach notification, chain-compromise response
  Backup:   [TO FILL — second person if operator unavailable]

WITNESS / NOTARY:
  Name:     [TO FILL — optional, for hardcopy Merkle root card]
```

### How to store this

Create a `contacts/` directory at the project root:
```
contacts/
  operator.json       # Justin's details (sealed to chain)
  roles.json          # role → incumbent mapping
  vendors.json        # all supplier contacts
  legal.json          # external counsel (when filled)
  emergency.json      # IR contacts
  clients/
    <client_id>.json  # per-engagement client contacts (created per case)
```

Each contact file sealed to the chain on create/update with
`event_type: CONTACT_REGISTERED` or `CONTACT_UPDATED`. This keeps
the "who knew what and when" trail that a forensic product must
demonstrate.

---

## NEXT STEPS

1. **Study the 10 sites** listed in Part 1 for paperwork/policy templates
2. **Pick a trial board** — Trello (free, visual) or Supabase table (already wired)
3. **Add the `documents` + `document_requests` tables** to the Supabase schema (I can write the SQL migration)
4. **Fill in the contacts** — legal contact, emergency backup, witness/notary
5. **Create the `contacts/` directory** — I can scaffold this now if you want

---

**This document is internal planning. Not for clients.**