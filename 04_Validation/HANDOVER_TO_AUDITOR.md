# HANDOVER TO AN AUDITOR

**Project:** Order Get It Right — Truth as a Service, v1.0.0
**From:** Justin Barnett (sole operator)
**To:** any third party who has been handed this project and asked to verify it
**Created:** 2026-07-16
**Status:** this is the verification script for a stranger. You do not
have to maintain the project. You have to confirm it is what the
operator says it is.

---

## What you have been asked to do

Someone (the operator, a court, a regulator, a buyer, a future AI
session) has handed you a copy of this project. They have made four
claims about it:

1. **The Merkle chain is intact.** Every audit decision since
   2026-07-12 has been sealed to a SHA-256 chain, and the chain
   verifies.
2. **The constants are as documented.** The 19 constants in
   `02_Technical/config/constants.py` are the values the operator
   says they are.
3. **The intellectual-property rights are as documented.** The
   operator's reservations (attribution, integrity, audit-trail,
   jurisdiction) and the third party's rights (right to audit, right
   to copy the backup plan, right to extend the build) are as set
   out in `04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt`.
4. **The maintenance record is plausible.** The build has been
   maintained by a single operator, on a defined schedule, with a
   `type: "change"` or `type: "observation"` or `type: "incident"`
   or `type: "rollback"` entry in `04_Validation/changelog.log` for
   every meaningful event.

You do not have to take these claims on faith. This document tells
you how to verify each one in under 30 minutes for the basic check,
or under 4 hours for the full audit.

---

## The basic verification (30 minutes)

You will need: a Windows host with Python 3.12+ and 256 MB of RAM,
the project folder, and the paper card from the 1-2-3 backup
envelope. (If you do not have the paper card, you cannot do the
basic verification. Skip to "Verification without the paper card"
below.)

### Step 1 (1 minute). Open PowerShell.

    cd C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical

(Or wherever the project lives on your host. The path above is
the operator's. Your copy may be at a different path; the verification
does not depend on the path.)

### Step 2 (2 minutes). Verify the chain.

    python -m src.verify_chain

Expected output, in full:

    claimed_root: <64-hex string>
    recomputed_root: <64-hex string>
    block_count: <integer>
    result: MATCH

`MATCH` means the chain verifies. The `claimed_root` is what the
operator's project says the root is. The `recomputed_root` is what
the verifier independently computed by hashing every block in order.
If they are equal, the chain is intact.

Now compare `claimed_root` to the 64-hex string on the paper card.
If they are equal, the chain is intact *and* matches what the
operator committed to when they last printed the card. If they are
not equal, either the chain has been re-sealed since the card was
printed (in which case the operator should have updated the card),
or the chain has been tampered with (in which case stop and read
`04_Validation/MAINTENANCE_PLAN.txt` §3 Incident Response).

### Step 3 (5 minutes). Walk the six reference fingerprints.

The fingerprints are listed in `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
PART 3. Re-derive them:

    python 04_Validation/scripts/phase_4_refresh_fingerprints.py

It writes the result to `04_Validation/scripts/phase_4_fingerprints.json`.
For each of the six:

- **REF-1 (constants.py SHA-256)**: should match the value in
  PART 3 *if* the constants file has not changed since PART 3 was
  written (2026-07-12). If it has changed, there should be a
  corresponding `CONSTANTS_BUMP` block on the chain.
- **REF-2a (STRATEGY.md SHA-256)**: same logic.
- **REF-2b (GOVERNANCE.md SHA-256)**: same logic.
- **REF-3 (source tree SHA-256)**: same logic.
- **REF-4 (tree shape SHA-256)**: same logic.
- **REF-5 (Merkle root)**: will NOT match the value in PART 3
  unless PART 3 is being re-printed right now. PART 3 was sealed
  on 2026-07-12 with 574 blocks. Today the chain has 2,797 blocks
  (or whatever the current count is — re-derive it). The REF-5
  you compute today is the correct fingerprint for *now*.
- **REF-6 (composite)**: should match the value in PART 3 only if
  all five preceding fingerprints match. If any has drifted, REF-6
  will have drifted too.

If REF-1, REF-2a, REF-2b, REF-3, REF-4 have not drifted, the
operator has not changed the source tree. If they have drifted,
read the chain — the drift should be explained by a `CONSTANTS_BUMP`
or a `DOC_AMENDED` or similar block. If the drift is unexplained,
that is a finding; record it in your audit report.

### Step 4 (5 minutes). Walk the changelog.

    Get-Content ..\04_Validation\changelog.log

(or `cat` on a non-Windows host). Every line is a JSON object.
Count the `type` field values:

- `type: "change"` — operator modified the build
- `type: "observation"` — daily cycle ran
- `type: "incident"` — something broke
- `type: "rollback"` — rolled back to a prior USB
- `type: "audit"` — an audit was run
- `type: "discovery"` — the DiscoveryAgent was used on a new host
- `type: "fork_resolved"` — the project was reconciled after a
  silent fork (e.g. block 2797, 2026-07-16)

The build's design assumption is: every meaningful event is a
changelog line. If you see a chain seal without a corresponding
changelog line, that is a finding. If you see a `type: "incident"`
line without a follow-up `type: "change"`, that is a finding.

The build's contract is the maintenance plan in
`04_Validation/MAINTENANCE_PLAN.txt`. The changelog should
plausibly match the contract: roughly 30 `type: "observation"`
lines per month (one per daily cycle), 4 `type: "change"` lines
per month (one per weekly cycle), 1 per quarter (the quarterly
review), 1 per year (the annual review). If the cadence is wildly
off, that is a finding.

### Step 5 (10 minutes). Run the test suite.

    cd C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical
    python -m pytest tests/

Expected: 70 passed, 0 failed, 2 skipped on a source-only host
(SDXC, fresh checkout, CI). The 2 skips are environment-dependent:
the Tauri junction test in test_a5_deploy_dry_run.py skips when
C:\OrderGetItRight is not present, and the Ollama tool-calling
skip in test_d5_agentic_repl.py fires when no tool-capable model
is loaded. On a fully-provisioned host with the junction present
and a tool-capable Ollama model loaded, the suite passes 72/72.
This is by design.)

If the count is different, read the failures. They are real
regressions. Record them.

### Step 6 (5 minutes). Read the IP-rights document.

Open `04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt`. Read the
full document. The relevant clauses for a third-party auditor are:

- **(c) Right to audit.** "Any person may run `python -m
  src.third_party_assistant` and then `verify` and may compare the
  printed Merkle root to the `claimed_root` in the output. The
  operator grants this right to anyone, anywhere, at any time, for
  any purpose."
- **(d) Right to copy the hard-copy backup plan.** "Any person
  may print and execute the 1-2-3 backup plan at
  `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`. The
  operator grants this right to anyone, anywhere, at any time."
- **(e) Right to extend.** "Any person may write their own agents
  in the same shape (...) and may plug them into the orchestrator
  at `02_Technical/src/agents/orchestrator.py`. The operator grants
  this right subject to the 00-99 boundary test."

You have the right to do everything you have done in steps 1-5.
The operator has granted this right unconditionally. If anyone
(including the operator) tells you that you do not have the right
to run `verify` or to copy the backup plan, they are mistaken.
Cite clause (c) and (d).

### Step 7 (2 minutes). Write the audit report.

You have done the basic verification. The output is a 1-page report
with:

- The Merkle root (claimed and recomputed; should be equal).
- The block count.
- The result (MATCH or BROKEN).
- The six reference fingerprints, with the values in
  `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` PART 3 alongside
  the values you re-derived.
- The test result (70 pass + 2 skip on a source-only host;
  72/72 on a fully-provisioned host; the 2 skips are the Tauri
  junction and the Ollama tool-calling model).
- The changelog summary (X changes, Y observations, Z incidents,
  W rollbacks, in the time period you audited).
- Any findings (drift between PART 3 and the live fingerprints;
  changelog lines without chain seals; chain seals without
  changelog lines; test failures).
- Your signature, the date, and the auditor's contact details.

You are done. The basic verification is complete.

---

## The full audit (4 hours)

If the basic verification surfaces a finding, or if the audit was
commissioned at "full audit" level, do the following in addition.

### Step 8 (1 hour). Re-read every document in `04_Validation/`.

There are ~17 documents in `04_Validation/`. Walk them all. Look
for:

- Internal inconsistencies (e.g. one doc says 70 pass + 2 skip,
  another says 72/72 pass).
- Outdated references (e.g. a doc references an old Merkle root
  without noting the date).
- Stale "next steps" (e.g. a "TODO" that has been done but not
  removed).

Each finding is a single line in your report. Do not propose fixes
unless asked. The operator fixes their own build.

### Step 9 (1 hour). Walk every constant.

Open `02_Technical/config/constants.py`. There are 19 named
constants. The laminated `04_Validation/hardcopy/OPERATOR_MANUAL.txt`
lists them with their values. Confirm the values match.

If any constant has changed since the laminated card was printed,
there should be a `CONSTANTS_BUMP` block on the chain explaining
the change. If the constant has changed and there is no
`CONSTANTS_BUMP` block, that is a finding.

### Step 10 (1 hour). Walk the source tree.

    python 04_Validation/scripts/audit_no_network.py

The build claims no network calls in the runtime. This script
walks every .py file under `02_Technical/src/`, parses it with
`ast`, and flags any import of `urllib`, `urllib2`, `urllib3`,
`requests`, `httpx`, `http.client`, `socket`, `ssl`, `smtplib`,
`imaplib`, `poplib`, `ftplib`, `telnetlib`, `asyncio` (network
paths), or any third-party network library.

Expected: zero flagged files. The list should be empty. If any
file is flagged, the runtime is not air-gapped. That is a
material finding.

### Step 11 (1 hour). Walk the "no black boxes" claim.

The build claims "no black boxes" — every number on the screen is
computed by a documented Python function. The mapping is in
`04_Validation/AUDIT_NO_BLACK_BOX.md`. Walk the doc, then spot-check
3-5 numbers on the live audit pipeline:

- Pick a recent report in `data/outbox/`. Read the report.
- For each numeric field, follow the chain in `AUDIT_NO_BLACK_BOX.md`
  to the Python file and line that produces the number.
- Read the Python file at that line. Confirm the function is doing
  what `AUDIT_NO_BLACK_BOX.md` says it is doing.

If any number on the screen does not have a traceable Python
function, that is a finding. The "no black boxes" promise is the
single most important promise the build makes to a court. It has
to hold.

### Step 12. Write the full audit report.

Same structure as the basic verification, plus the additional
findings from steps 8-11. The full report is typically 4-8 pages.

---

## Verification without the paper card

If you do not have the paper card, you can still verify the chain
(steps 2-3 above), but you cannot prove that the chain matches
what the operator committed to. The paper card is the operator's
out-of-band anchor. Without it, the chain is intact *internally*
but not *externally*. The next quarterly cycle will produce a fresh
paper card. Until then, the chain is the best evidence you have.

If you are conducting a forensic audit, request the paper card
from whoever gave you the project. If they cannot produce it, that
is a finding in itself.

---

## What you do not have to do

- You do not have to maintain the build. You are not the next
  operator. The build's next-operator handover is in
  `04_Validation/HANDOVER_TO_NEW_OPERATOR.md`. That document is
  not for you.
- You do not have to re-derive every constant from first
  principles. The constants are documented in
  `02_Technical/config/constants.py` and on the laminated card.
  Walk them, but do not derive them.
- You do not have to read the source code. The build's claims
  about what the code does are in
  `04_Validation/AUDIT_NO_BLACK_BOX.md` and
  `04_Validation/AUDIT_NO_NETWORK.md`. The two scripts
  (`audit_no_network.py` and the equivalent for black-box) walk
  the code for you. If the scripts are missing or do not run,
  that is a finding; do not write the audit by reading 50 .py
  files by hand.
- You do not have to assess the operator's competence, intentions,
  or honesty. You are not a character witness. You are a chain
  verifier. The chain either verifies or it does not. The
  operator's behaviour is a separate audit, and a different
  document.

---

## What you write in your report if everything passes

> The Order Get It Right project at version 1.0.0, build date
> 2026-07-12, operator Justin Barnett, was verified on <date> by
> <auditor>. The Merkle chain is intact (MATCH at block <N>, root
> <64-hex>). The six reference fingerprints match the values
> documented in `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` PART 3
> (with REF-5 reflecting the live chain state as of <date>). The
> test suite passes (X/48 + 3 skip-guard on a source-only host;
> X/50 + 1 skip-guard on a Tauri-built host; the Ollama skip
> survives on both). The runtime is air-gapped (audit_no_network.py
> reports zero network imports).
> The IP-rights document grants the auditor the right to verify
> (clauses c, d, e). No material findings.

That is the whole report. One paragraph. Filed. Done.

---

## What you write in your report if something fails

> Finding 1: <description, file, line, expected, actual>.
> Finding 2: ...
>
> The Order Get It Right project at version 1.0.0, build date
> 2026-07-12, operator Justin Barnett, was verified on <date> by
> <auditor>. The Merkle chain is intact (MATCH at block <N>, root
> <64-hex>). The test suite passes (X/48 + 3 skip-guard on a
> source-only host; X/50 + 1 skip-guard on a Tauri-built host;
> the Ollama skip survives on both). The runtime is air-gapped. <N> material findings were recorded; the
> operator has been notified. The IP-rights document grants the
> auditor the right to verify (clauses c, d, e); this report is
> filed under those rights.

The chain can be intact and the build can still have findings.
The chain is the audit trail. The findings are the build's
condition. They are separate things. Report both.

---

Welcome to the audit. The chain is the source of truth. The
changelog is the human record. The IP-rights document is the
authority under which you are reading this. You have everything
you need.
