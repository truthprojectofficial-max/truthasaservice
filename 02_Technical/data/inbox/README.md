# data/inbox/  --  Audit Intake Folder

This folder is the batch intake for the Order Get It Right audit CLI.

The CLI is invoked as:

    python -m src.audit_cli --inbox data/inbox --outbox data/outbox \
                            --formats md,pdf,docx

It reads every `.txt`, `.docx`, and `.pdf` file in this folder, runs
each one through the audit pipeline (Form_Entry -> Audit_Review ->
Lattice_Compute -> Ledger_Seal -> Affidavit), and writes a Markdown
/PDF/DOCX report per file into `data/outbox/`. See SPECS.txt I-03
and MAINTENANCE_PLAN.txt section 2.3 (Monthly Cycle step 2).

This folder is the **only** interface between external evidence and
the audit engine. The engine does not read the network, the
registry, the inbox folder under `to the spoils go`, or anywhere
else. If an evidence file is not in this folder, the engine will
not see it.

## What goes in here

- `.txt` files, UTF-8, plain text, any line length.
- `.docx` files, Microsoft Word 2007+ (Office Open XML).
- `.pdf` files, PDF 1.4+.

Each file is one audit case. The CLI walks them in lexicographic
order. A case consists of five sections, in any order, marked with
the headers below. Sections may be empty; the engine records the
empty section as a fact and continues.

### Section headers (plain text)

    [CLAIMANT]      name, role, contact (free text)
    [CLAIM]         the claim being audited (one paragraph)
    [EVIDENCE]      exhibit list, dates, sources, what the claimant
                    is relying on
    [REQUESTED]     the verdict the claimant wants (e.g. "SUSTAINED",
                    "REFUND", "DAMAGES $X")
    [JURISDICTION]  the legal basis being invoked (e.g. "ACL s 18",
                    "Evidence Act 1995 (NSW) s 177", "contract law")

Any text outside the five sections is treated as supporting
narrative and is preserved verbatim in the audit report.

## What does NOT go in here

- Executables, scripts, .zip, .tar, .gz. (No code ever runs from
  this folder.)
- Photos, scans, audio, video. (Out of scope for the textual
  pipeline.)
- Real personally identifying information. (Use a pseudonym or
  `REDACTED-*` placeholder.)
- Anything that the operator does not want sealed to the chain. The
  chain grows by one block per file ingested.

## The seed files

The four `SEED_*.txt` files in this folder are synthetic intakes
shipped with the build so the CLI has something to chew on. They
are not real evidence. They are templates:

    SEED_001_sample_audit_intake.txt   -- the canonical 5-section
                                          template, with notes
    SEED_002_warranty_claim.txt        -- a consumer warranty case
                                          (audio product specs vs.
                                          measured performance)
    SEED_003_prior_2021_reference.txt  -- a reference corpus pointer
                                          to data/samples/
                                          verified_prior_2021.txt
    SEED_004_drive_inventory_pointer.txt  -- a self-audit pointer
                                             to data/outbox/
                                             DRIVE_INVENTORY_*

Delete the seeds before any real audit run. The CLI will warn
("SEED_* file present, this is a synthetic case") but will still
process them.

## Folder history

- 2026-07-12: folder created during initial build.
- (gap)     : folder went missing between 2026-07-12 and 2026-07-16
              (fork resolution; see RECONCILIATION_2026-07-16.md
              and block 2797 in the Merkle chain).
- 2026-07-16: folder recreated. Seeds written. CLI re-runnable with
              the default `--inbox data/inbox` argument.
