# Privacy Policy — Order Get It Right (OGIR)

**Effective date:** 2026-07-24
**Operator:** Justin Barnett
**Application:** Order Get It Right (OGIR) — Forensic Lie-Detector
**Version:** 1.0.0 (Tauri v2 desktop app)

## 1. Open and Transparent Management (APP 1)

OGIR is operated by a single individual (Justin Barnett, the Operator) as a
forensic deception-detection tool. The Operator maintains a dynamic
Privacy Policy at this file path and commits every change to the
public Merkle chain in `03_Vault/facts_registry.json` so the policy
itself is auditable.

The data we collect, why we collect it, and how long we keep it, are
listed in the sections below. The Operator will update this policy
within 30 days of any material change to data handling.

## 2. Anonymity and Pseudonymity (APP 2)

OGIR is a **local desktop application**. It runs as a Tauri v2 app
on the user's machine. The user can:

- Use the application **fully offline** without any account registration
- Run the lie-detector on text **without identifying themselves**
- Reject the optional Google Drive integration (Section 6) and use
  the app purely as a local CLI / file-scan tool
- Sign in to the optional Supabase sync (Section 5) with a pseudonym
  email; the Operator does not require legal-name verification

No account registration is required to use the lie-detector for its
core purpose (deception-pattern analysis on user-supplied text).

## 3. Collection of Solicited Personal Information (APP 3)

OGIR collects only the data the user explicitly provides:

| What | Why | How long |
|------|-----|----------|
| Text submitted to the audit panel | To run the lie-detector | Not stored on any server; only in the user's local SQLite cache (TTL 30 days) |
| Optional Google Drive file (if user picks) | To scan a specific file the user chose via Google Picker | Not stored; streamed, scanned, discarded |
| Optional Supabase sync (if user signs in) | To back up audit history across devices | Until the user deletes the account |
| Crash logs (if user opts in) | To debug the Tauri runtime | 90 days |

We do **not** collect:
- Browsing history outside the app
- Location data (no GPS, no IP geolocation)
- Biometric data
- Sensitive categories (race, religion, health, etc.)

## 4. Handling of Personal Information (APP 3 — APP 7 — APP 9)

If the user signs in to Supabase sync, the data is:

- Encrypted in transit (TLS 1.3, Cloudflare R2 egress is zero-fee)
- Encrypted at rest (AES-256, Supabase Pro tier default)
- Subject to Row-Level Security (RLS): users can only read their own audits

If the user does **not** sign in, OGIR is fully local. The Operator
never sees the text. The Tauri runtime never sends the text anywhere.

The Operator handles all APPs 3-7 and 9 as follows:
- **APP 3 (Collection):** Only solicited data; see Section 3.
- **APP 4 (Unsolicited):** If received, the Operator destroys the data within 30 days.
- **APP 5 (Notification):** If unsolicited data is received, the Operator notifies the individual.
- **APP 6 (Use):** Data is used only for the purposes stated in APP 3.
- **APP 7 (Direct marketing):** OGIR does not engage in direct marketing.
- **APP 9 (Other uses):** All other uses are with the individual's consent.

## 5. Cross-Border Disclosure (APP 8)

OGIR uses these services (all with explicit user consent):

- **Supabase** (Postgres + auth) — US/EU regions per user choice
- **Cloudflare R2** (binary updates only, not user data) — global edge
- **Google Picker** (drive.file scope only) — user-selected files

No data is transferred to jurisdictions with insufficient privacy
protection. The Operator will publish the regional choices in the
OGIR_PROJECT_STATE document.

## 6. APP 9 — Adoption, Use, Disclosure

OGIR uses the data only for the purposes stated in APP 3. The
Operator does not sell user data. The Operator does not use the
data for direct marketing. The Operator does not share the data
with third parties except:

- Cloudflare (for binary updates)
- Supabase (for optional cloud sync, only if user signs in)
- Google (for optional Drive picker, only if user signs in)

## 7. APP 10 — Quality of Personal Information

OGIR takes reasonable steps to ensure the data it holds is accurate,
up-to-date, and complete. Users can edit or delete their audit
history at any time. The Operator can be contacted via the
project repository for data corrections.

This section also covers **APP 10** (quality of personal information).

## 8. APP 11 — Security of Personal Information

OGIR is built on a **zero-network** foundation:

- The runtime tree (`02_Technical/src/`) has **zero network imports**
  (verified by `04_Validation/scripts/audit_no_network.py`,
  106 .py files CLEAN, 0 FAIL, zero network modules anywhere).
- The audit tool chain is a hard-fail: any urllib / socket / http.client
  import anywhere in the build fails the test suite.
- The Operator follows D1-TRUE compliance (00-99 spatial mandate,
  ISO date mandate, ACL Section 56).
- The chain is a Merkle witness: every audit run is recorded in
  `03_Vault/facts_registry.json` with a SHA-256 hash chain.

**Encryption:** TLS 1.3 in transit, AES-256 at rest (Supabase default).

**De-identification:** When the user deletes an audit, the row is
hard-deleted from Supabase. When the user uninstalls OGIR, the local
SQLite cache is wiped (TTL = 30 days, but the user can `rm -rf`
the cache dir for instant wipe).

## 9. APP 12 — Access and Correction

Users can:
- Export their audit history (JSON) at any time
- Delete individual audits or the entire account
- Request a copy of all data the Operator holds (manual process,
  30-day response time)
- Correct any data the Operator holds

This section also covers **APP 12** (access and correction).

## 10. APP 13 — Complaints

If the user has a complaint, the Operator can be reached via the
project repository. The Operator will respond within 30 days.

For complaints that cannot be resolved, the user can contact the
**Office of the Australian Information Commissioner (OAIC)** at
https://www.oaic.gov.au/.

---

## NDB Scheme (Notifiable Data Breaches)

Per the **Privacy Act 1988 (Cth)** and the **Notifiable Data
Breaches (NDB) Scheme**:

If the Operator becomes aware of a data breach that is **objectively
likely to cause serious harm** to any individual, the Operator will:

1. **Assess the breach within 30 days** of becoming aware
2. **Notify the OAIC** if the assessment confirms serious harm
3. **Notify all affected individuals** with:
   - The identity and contact details of the Operator
   - A description of the data breach
   - The kinds of information concerned
   - Recommended steps the individual should take

The full NDB Response Plan is at `04_Validation/NDB_RESPONSE_PLAN_2026-07-24.md`.

---

## Changes to this Policy

| Date | Change | Sealed |
|------|--------|--------|
| 2026-07-24 | Initial policy (Tauri v2 desktop, Supabase Pro, Cloudflare R2, Google Picker drive.file) | This document |

---

**This policy is committed to the OGIR Merkle chain.** Any update
must be a sealed event of the form `PRIVACY_POLICY_AMENDED_<DATE>`
with documented justification in the commit message.
