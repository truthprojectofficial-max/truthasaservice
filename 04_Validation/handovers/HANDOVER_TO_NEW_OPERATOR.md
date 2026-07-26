# HANDOVER TO A NEW OPERATOR

**Project:** Order Get It Right — Truth as a Service, v1.0.0
**From:** Justin Barnett (sole operator, 2026-07-12 to 2026-07-16)
**To:** the next operator
**Created:** 2026-07-16
**Status:** this is not a contract. It is a one-page orientation so you
do not have to re-discover what the project is, where it lives, and
what you have to do to keep it alive.

---

## What you have inherited

A deterministic business audit and valuation program. It runs on one
laptop, with no network and no LLM in the audit path. Every audit
decision is sealed to a SHA-256 Merkle chain. Every operator action is
written to a JSONL changelog. The chain is the audit trail. The
changelog is the human-readable counterpart.

The project's identity, in one sentence, is the one at the top of
`04_Validation/OPEN_ITEMS_AND_REFERENCE.md` PART 4:

> Order Get It Right -- Truth as a Service.
> A deterministic business audit and valuation program.
> Version 1.0.0. Operator: <your name now, not mine>.
> Jurisdiction: Commonwealth of Australia.
> Operates from `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`.
> No network. No LLM in the audit loop. Every decision sealed to a
> Merkle chain at `02_Technical/03_Vault/facts_registry.json`.

The first thing you do is replace `<your name now, not mine>` with
your own. The boundary test (`tests/test_00_99_boundary.py`) enforces
that no other identity can claim to operate the build without a
sealed change. So you will need to seal a `OPERATOR_HANDOVER` block
to the chain. That is in step 4 below.

---

## What you do, in order

### Step 1 (15 minutes). Read the project from above.

Read these five files, in this order. Do not skim. Read.

1. `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` — the canonical
   "what is this project, what is open, what is closed, what are the
   six fingerprints" document. PART 3 has the six fingerprints.
2. `04_Validation/MAINTENANCE_PLAN.txt` — the contract. Five
   cycles (daily/weekly/monthly/quarterly/annual), the rhythm,
   the cost, the incident response procedure.
3. `04_Validation/STAGE_PAPER_DAILY.txt` — the 9 steps of the
   daily cycle, as a checklist.
4. `04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt` — the
   operator's reservations (attribution, integrity, audit-trail,
   jurisdiction) and the third party's rights (right to audit, right
   to copy the backup plan, right to extend the build with new
   agents under the 00-99 boundary).
5. `04_Validation/hardcopy/OPERATOR_MANUAL.txt` — the laminated
   one-pager with the daily-use commands, the constants, the five
   agents, the four gates, and the "what to do if something breaks"
   flow.

### Step 2 (15 minutes). Verify the chain is intact.

Open PowerShell.

    cd C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical
    python -m src.verify_chain

Expected: `MATCH: <64-hex Merkle root>`. The 64-hex string is on the
paper card in the 1-2-3 backup envelope. If they do not match, **stop**
and read `04_Validation/MAINTENANCE_PLAN.txt` §3 (Incident Response).
The chain is the source of truth. If it is broken, the rest does not
matter.

### Step 3 (15 minutes). Re-derive the six reference fingerprints.

The fingerprints are in `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
PART 3. Re-derive them with the script:

    python 04_Validation/scripts/phase_4_refresh_fingerprints.py

It writes the result to `04_Validation/scripts/phase_4_fingerprints.json`.
Compare each fingerprint to the value in PART 3. **The REF-5 (Merkle
root) will not match the one in PART 3** — that is expected, because
PART 3 was sealed on 2026-07-12. The REF-5 you compute today will be
the root *after* the last seal on disk. That is the correct
fingerprint for *now*.

The other five (REF-1, REF-2a, REF-2b, REF-3, REF-4) should match
unless you have changed the source tree. If they do not match, you
have drifted from the previous operator. That is not necessarily
wrong — it just means the project has changed. Re-seal with the new
fingerprints so the next operator inherits the new ones, not the old
ones.

### Step 4 (15 minutes). Seal the handover.

    python -m src.third_party_assistant
    onyx> seal OPERATOR_HANDOVER_2026-07-16
              {"from": "Justin Barnett",
               "to": "<your name>",
               "to_email": "<your email>",
               "to_contact": "<your phone>",
               "merkle_root_at_handover": "<root from step 2>",
               "fingerprints_at_handover": {
                 "ref1_constants_sha256": "<from step 3>",
                 "ref2a_strategy_sha256": "<from step 3>",
                 "ref2b_governance_sha256": "<from step 3>",
                 "ref3_source_tree_sha256": "<from step 3>",
                 "ref4_tree_shape_sha256": "<from step 3>",
                 "ref5_merkle_root": "<from step 3>",
                 "ref6_composite_sha256": "<from step 3>"
               },
               "six_non_negotiables_accepted": true,
               "jurisdiction_accepted": "Commonwealth of Australia",
               "first_action_as_operator": "Daily cycle (step 5)"}
    onyx> verify

This seals the handover to the chain. The previous operator's name
remains in the constants file until you choose to change it (which
requires a `CONSTANTS_BUMP` seal of its own). For now, both names
co-exist: the project was built by Justin Barnett, the new operator
is `<your name>`, and the chain records the transition.

### Step 5 (15 minutes). Run the daily cycle.

You have now read the project, verified the chain, re-derived the
fingerprints, sealed the handover, and you are about to do the
*first cycle of the new era*. Follow `STAGE_PAPER_DAILY.txt`
exactly. 9 steps. 15 minutes. Confirm the chain at the end. Append
the type: "observation" entry to `04_Validation/changelog.log`. Done.

Welcome to the project.

---

## What you do tomorrow, and the day after

- **Every day** (15 min): `STAGE_PAPER_DAILY.txt`. This is the
  non-negotiable floor. If you do nothing else, do this.
- **Every week** (2 hr): `STAGE_PAPER_WEEKLY.txt`. This is where
  the audit work happens.
- **Every month** (4 hr): `STAGE_PAPER_MONTHLY.txt`. The full
  evaluation suite, the smoke tests, the constants walk.
- **Every quarter** (8 hr): `STAGE_PAPER_QUARTERLY.txt`. The 1-2-3
  backup refresh. The offsite test. The most important step is the
  USB burn + verify from USB.
- **Every year** (16 hr): `STAGE_PAPER_ANNUAL.txt`. The full
  document re-read. The version bump. The annual review seal.

If you do all five, you are spending 6 hours/day on daily, 8
hours/month on weekly, 4 hours/month on monthly, 8 hours/quarter
on quarterly, 16 hours/year on annual. Roughly 5-6 hours/week on
maintenance. That is the design budget.

---

## What you do NOT change, ever, without a sealed CONSTANTS_BUMP

The constants in `02_Technical/config/constants.py`. The full list
is on the laminated OPERATOR_MANUAL.txt. The four that matter most:

- `TAU_EXTRACTION_CEILING = 0.10` — the firewall. The operator
  cannot extract more than 10% of the audited value in fees. This
  is the structural enforcement of "we do not game the audit to
  inflate our own bill."
- `DECEPTION_ONTOLOGY_VERSION = "3.9 (54 patterns)"` — the version
  of the 54-pattern ontology. Bumping to 3.10 (or v4.0) requires
  adding patterns, re-sealing the ontology, and updating every doc
  that cites the version.
- `PROJECT_OPERATOR` — your name now. The boundary test will fail
  if this changes without a `CONSTANTS_BUMP` block on the chain.
- `PROJECT_JURISDICTION` — Commonwealth of Australia. Changing
  jurisdiction is a fork in the project. Do not do it as a
  constants bump. Call a project review.

If you change any of these, the procedure is:

1. Edit the constant in `constants.py`.
2. Run the full pytest suite. Expected: 70 pass + 2 skip-guard on
   a source-only host (Tauri junction not present; Ollama tool-
   calling model not loaded). On a fully-provisioned host with
   the junction present and a tool-capable Ollama model loaded,
   the suite passes 72/72.
3. Run the chain re-derivation. Expected: MATCH.
4. Seal a `CONSTANTS_BUMP` block to the chain with the old value,
   the new value, the reason, and the test result.
5. Update the paper card in the 1-2-3 backup envelope.
6. Append a type: "change" entry to `changelog.log`.
7. Re-burn the USB stick in the next quarterly cycle (or sooner,
   if the change is material).

---

## What you do if the previous operator has died

The hard-copy backup plan in `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`
section 3 ("NEXT-OPERATOR NOTES") is the relevant doc. The
short version:

1. Find the bank safe deposit box (or whichever offsite location
   the previous operator used). The box contains: one USB stick,
   one paper card with the Merkle root, one A4 sheet listing the
   Python interpreter path and the single command to run, and a
   sealed envelope with the passphrase.
2. Open the envelope. Read the passphrase.
3. Boot the USB stick on a Windows host with Python 3.12+ and
   256 MB of RAM. (Any Windows host with that profile will do.
   The MSI Prestige 16 is not required.)
4. Run `python -m src.verify_chain`. Confirm the root matches the
   paper card.
5. Read this handover document, then go to step 1 above.

If the chain matches, you are now the operator. Run the daily
cycle today. Welcome to the project. If the chain does not match,
the USB is corrupt or has been tampered with. Re-burn from the
operator's primary laptop (if it survives) or from a recent cloud
backup of the project tree (the operator may have one; the
project itself does not require one).

---

## What you do not have to do

- You do not have to re-read every project file. The five files
  in step 1 above are the orientation. Everything else is reference.
- You do not have to re-derive the SHA-256 chain from scratch. The
  chain is on disk. Re-deriving means running `verify` and
  comparing to the paper card.
- You do not have to maintain the build for anyone but the people
  who actually send you audits. The build is one operator, one
  laptop, one chain. It is not a SaaS. It is not multi-tenant.
  It is your job to do the audits that come in, and to keep the
  chain honest.
- You do not have to keep me (the previous operator) in the loop.
  The chain records who sealed what, when. If a future operator
  (or a court) needs to ask me something, they can find me via
  the contact details in the chain (the `OPERATOR_HANDOVER_2026-07-16`
  block I sealed, plus the original `B1_PROJECT_OPERATOR` block
  from 2026-07-12).

---

## What you do if you have a question I did not anticipate

Read `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` PART 1. It is
the honest list of what the build does not do, what was deferred,
and what the previous operator was still thinking about. PART 2 has
the five next steps. PART 3 has the six fingerprints. PART 4 has
the one-sentence identity. If your question is not answered by
PARTs 1-4, it is a new question. The chain is the place to ask it
— append a type: "observation" entry to `changelog.log` with the
question, and seal it.

Welcome.
