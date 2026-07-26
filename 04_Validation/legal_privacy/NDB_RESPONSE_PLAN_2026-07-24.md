# NDB Response Plan — Order Get It Right (OGIR)

**Effective date:** 2026-07-24
**Operator:** Justin Barnett
**Application:** Order Get It Right (OGIR)
**Reference:** Privacy Act 1988 (Cth), NDB Scheme, 13 APPs

## Purpose

This document is the **Notifiable Data Breaches (NDB) Response Plan**
for OGIR. It describes what the Operator will do if a data breach
occurs that is **objectively likely to cause serious harm** to any
individual.

This plan satisfies APP 11.2 (security of personal information) and
the NDB Scheme's 30-day assessment requirement.

## 1. What is an "Eligible Data Breach"?

Under the NDB Scheme, a data breach is **eligible** (i.e., must be
reported) if:

1. There is **unauthorized access to, unauthorized disclosure of,
   or loss of** personal information held by the Operator; AND
2. The breach is **likely to result in serious harm** to one or
   more individuals; AND
3. The Operator has **not been able to prevent the likelihood of
   serious harm** through remedial action.

**Serious harm** includes:
- Financial harm (e.g., fraud, identity theft)
- Physical harm (e.g., stalking, violence)
- Psychological harm (e.g., humiliation, distress)
- Reputational harm (e.g., damage to credit record)
- Other forms of harm considered significant by a reasonable person

## 2. The 30-Day Assessment Window

When the Operator **becomes aware of reasonable grounds to suspect**
a data breach, the Operator will:

1. **Day 0** — Become aware of the breach (or suspect one)
2. **Days 1-7** — Conduct preliminary assessment
   - Identify the scope (what data, how many users, what kind)
   - Contain the breach (revoke keys, take systems offline, etc.)
   - Document everything in a sealed chain event
3. **Days 8-21** — Detailed assessment
   - Determine if the breach is "likely to result in serious harm"
   - Identify the individuals affected
   - Identify the OAIC contact and the notification mechanism
4. **Days 22-30** — Decision and notification (if eligible)
   - If **eligible**: prepare and submit the OAIC statement
   - If **not eligible**: document the decision and the reasoning
   - If **uncertain**: treat as eligible and notify

The Operator will **always** complete the assessment within 30 days,
even if the conclusion is "not eligible."

## 3. Notification to OAIC

If the breach is eligible, the Operator will submit a **Statement
to the OAIC** that includes:

1. The **identity and contact details** of the Operator
2. A **description of the data breach**:
   - Date the breach occurred (or the period)
   - Date the Operator became aware
   - Description of the circumstances
   - The kinds of information concerned
3. The **kinds of personal information** involved
4. **Recommended steps** to be taken by individuals to reduce risk
5. **Steps the Operator has taken** (or intends to take) to remedy
6. **Steps the Operator has taken** (or intends to take) to prevent
   future breaches

The OAIC statement is submitted via the OAIC's online portal at
https://www.oaic.gov.au/privacy/notifiable-data-breaches.

## 4. Notification to Affected Individuals

The Operator will also notify **each affected individual** with:

1. The **identity and contact details** of the Operator
2. A **description of the data breach** (same as OAIC statement)
3. The **kinds of personal information** involved
4. **Recommended steps** to reduce risk (e.g., change passwords,
   monitor credit, contact IDCARE)
5. **Other entities** the individual can contact for help (IDCARE,
   OAIC, police)

Notification methods (in order of preference):
- Email to the address on file (if user signed in to Supabase)
- In-app notification (if user has OGIR installed)
- Public statement on the project repository (if individual
  notification is impractical)

## 5. Examples of Breaches and Responses

| Breach | Eligible? | Action |
|--------|-----------|--------|
| Audit log leaked (text only, no user ID) | NO (no PII) | Document, no notification |
| Supabase credentials compromised, full user table dumped | YES (PII + harm) | Notify OAIC + all users within 30 days |
| Tauri crash log leaks local file path | NO (no PII, path is local) | Document, no notification |
| Google Picker scope expanded to full drive without consent | YES (scope creep is a breach) | Notify OAIC + all users, revert scope |
| DNS forwarder log captures queries (e.g., Unbound logs) | NO (no PII) | Document, no notification |
| Chain witness leaked (Merkle chain published inadvertently) | NO (no PII) | Document, no notification |

## 6. Roles and Responsibilities

In a single-operator project, all roles fall to the Operator
(Justin Barnett):

- **Discovery:** Operator (self)
- **Containment:** Operator (immediately)
- **Assessment:** Operator (within 30 days)
- **Notification:** Operator (OAIC + users)
- **Remediation:** Operator
- **Post-mortem:** Operator + sealed chain event

If the Operator is unavailable (illness, accident), the **successor
process** is: the project's `04_Validation/WHY_THIS_FAILED.md` and
`OGIR_PROJECT_STATE_2026-07-24.md` documents describe the system
well enough for a successor to act.

## 7. Documentation Requirements

Every breach response must be documented in the OGIR Merkle chain:

- `NDB_SUSPECTED_<DATE>` — when the Operator becomes aware
- `NDB_ASSESSMENT_STARTED_<DATE>` — when the 30-day window opens
- `NDB_CONTAINED_<DATE>` — when the breach is contained
- `NDB_ASSESSMENT_COMPLETE_<DATE>` — when the assessment concludes
- `NDB_ELIGIBLE_<DATE>` or `NDB_NOT_ELIGIBLE_<DATE>` — the decision
- `NDB_OAIC_NOTIFICATION_<DATE>` — when the OAIC statement is sent
- `NDB_USER_NOTIFICATION_<DATE>` — when users are notified
- `NDB_REMEDIATION_<DATE>` — when fixes are in place
- `NDB_POSTMORTEM_<DATE>` — when the post-mortem is sealed

## 8. Test of the Plan

This plan is a **living document**. The Operator will:

- **Annually** (every 12 months) review and update this plan
- **On any change** to the data handling (e.g., new Supabase
  project, new Cloudflare region, new Tauri version) review and
  update this plan
- **On any incident** (suspected or confirmed) trigger a full
  review

The review is sealed as `NDB_PLAN_REVIEWED_<DATE>`.

## 9. Contact Information

- **Operator:** Justin Barnett
- **Project:** https://github.com/[operator-repo] (the OGIR repo)
- **Email:** [operator's email]
- **OAIC contact:** https://www.oaic.gov.au/privacy/privacy-complaints

## 10. Related Documents

- `04_Validation/PRIVACY_POLICY_2026-07-24.md` — the 13 APPs
- `04_Validation/OGIR_PROJECT_STATE_2026-07-24.md` — the project state
- `04_Validation/WHY_THIS_FAILED.md` — the trial-verdict history
- `.hermes/plans/2026-07-24_ogir-gtm-fix-plan.md` — the 7-work-block GTM plan

---

**This plan is committed to the OGIR Merkle chain.** Any update
must be a sealed event of the form `NDB_RESPONSE_PLAN_AMENDED_<DATE>`.
