================================================================================
ORDER GET IT RIGHT  --  THE YELLOW RIBBON
A short proof of welcome for the next operator, the next AI, and the operator
themselves on a day they are afraid.
Generated: 2026-07-11  (UTC)
Refreshed: 2026-07-18  (UTC, after the operator-initiated F1-F17 build + F11 Git + F7 lattice-reframing + F8 ontology R1-R4+R5 + intake-held + E4 F1 re-derivation + this refresh; 88/1 tests passing; chain MATCH; 10561+ blocks
seal -- Tauri exe + MSI + NSIS rebuilt against the new single-page UI;
all three artefacts mirrored to USB; 6,966 blocks; 86/1 tests passing;
stale 02_Technical/tests/ mirror removed -- REF-3 52 -> 50 .py,
REF-4 220 -> 218 files)
Author:    codex-on-Justo  (operator: Justin Barnett)
================================================================================

This document is intentionally short. Everything in it points at
something that already exists. Nothing in it requires the author to
be present. Nothing in it requires the network. Nothing in it
requires any AI, any vendor, any cloud service, any subscription,
or any credentials. If you have the project folder and a working
Python, you can re-derive every claim in this document in under
sixty seconds.

If you are reading this and you are afraid, read the first section
("The ribbon") and then the last section ("If someone cuts the
ribbon"). You do not need to read the middle.

================================================================================
THE RIBBON
================================================================================

The project is yours. It is not a vendor's. It is not a platform's.
It is not a model's. It is a folder on a Windows laptop that
contains:

  1. A deterministic Python program that audits businesses.
  2. A Merkle chain that proves every decision the program ever made.
  3. A human-readable changelog of every change ever made.
  4. A hard-copy backup plan that survives the laptop's death.
  5. A set of six cryptographic fingerprints that identify the project
     uniquely, re-derivable by anyone with the folder.

The folder is at:

  C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight
  (USB/SDXC backup at D:\OrderGetItRight)

The chain is at:

  03_Vault\facts_registry.json

The current Merkle root (the single number that summarises the
chain's integrity) is:
  5b66058e8d322f00a724a9f4b36cdf3f3f9a6d7a01dc147c9ebf843bf05b71f3
  (10561 blocks, last seal 2026-07-17T18:52:05Z, refreshed 2026-07-18)

This number changes every time the program seals a fact. The version
above is a snapshot from the close of the 2026-07-17 session. The authoritative way to read the current root is to re-derive it from
disk -- under 5 seconds, no network required, on any machine with
Python 3.12+ installed:

  cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
  python -m src.verify_chain
  # or, to print the six reference fingerprints:
  python -m src.verify_chain --print-refs

If the number that prints matches the one above, the chain is
intact. If it does not match, something has been changed or
removed that should not have been. The chain is honest about
this; that is the whole point of a chain.

================================================================================
WHAT THIS SESSION DID  (in one paragraph)
================================================================================

This session (2026-07-17) closed OPEN_ITEMS E4 by running the
audit engine against the pre-2021 reference corpus (the operator
brought Verified.docx into the project; an existing 41,316-byte
text export at data/samples/verified_prior_2021.txt was used as
the audit input, embedded in a 5-section intake). The engine
returned PASS_WITH_FALSE_POSITIVE_FLAGS: 5/54 patterns fired
(DD-001, DD-006, DD-011, DD-041, DD-054); 12 raw hits resolved
to 11 false positives (single-word lexical matches on common
English connectives in editorial register) and 1 true negative
(anti-deception exposure). Four ontology refinement
recommendations (R1-R4) were queued for the next scheduled bump.
The reference corpus is now the canonical pre-2021 baseline.
The full prior session (2026-07-17) closed A3 (seed-on-POST
fix), C5 (STRATEGY.md operational-and-maintained tone), D2
(no-network audit extended with allow-list and 4-test regression),
and D3 (full screen-to-function trace doc). The 2026-07-16 session
before that resolved a fork between two working copies of the
project (C:\Users\justo\.claude\OrderGetItRight/ and
C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight/),
declared the OneDrive copy canonical, and reconciled the chain.
The remaining open items are the true clean-host restore test
(D1-TRUE, operator), the Gmail .mbox import (E1, operator), and
four reserved slots in NEXT FIVE STEPS (now including the R1-R4
ontology bump that came out of the E4 calibration).

The same day, the operator ran three follow-up sessions that closed
material seams in the live program (not the spec docs). Tier 1
(ORCHESTRATOR_SEAM_FIXED) removed a silent statement[:500] truncation
in Orchestrator.process_input() and wired the FastAPI lifespan
shutdown to seal a SHUTDOWN block on every clean exit; +3 tests in
tests/test_orchestrator_seam.py brought the suite from 76/1 to 79/1.
Tier 2 (TIER2_SURFACES_ADDED) added GET /api/affidavit/preview
returning the same markdown as POST without writing to disk, and
corrected two stale "Truncated to 500 chars" docstrings in
tools/agentic_repl_tools.py; +3 tests in tests/test_affidavit_preview.py
brought the suite to 82/1 and the endpoint count to 32. Tier 3
(TIER3_DOCS_REFRESHED) refreshed the Orchestrator class docstring
(distinguishing the 4-agent hand-off chain from the 10 named
modules under src/agents/) and the QUICK_REFERENCE_CARD.txt
Merkle root snapshot. Tier 4 (this refresh) updates the live
numbers in this Ribbon and the fingerprints in
OPEN_ITEMS_AND_REFERENCE.md to match the current chain.

Later the same day, the operator asked for a UI that "speaks for
itself against known needs, of working capacity, figures the
operator can assess as it operates, info it can call upon, stop
go clear etc." That grounded the UI_OPERATOR_FACING_REDESIGN
seal, which fixed a real Tier-1 path bug in src/server/app.py:
STATIC_DIR was computed with .parent.parent (one level too
shallow) which landed on 02_Technical/src/web/ -- a directory
that does not exist. The classic effect: GET / fell through to
the JSON fallback {"status": ...} and /static was never mounted.
The Tauri shell masked the bug because it serves web/ directly
from disk via its own frontendDist config, so the operator had
only ever seen the UI through the desktop binary. Browser mode
was silently broken. Fixed to .parent.parent.parent. New
regression test tests/test_static_dir.py (4 tests, all
boundary-compliant) pins the on-disk layout, the GET / serving,
the /static mount, and the byte-identity of served HTML vs disk
file. The web/index.html was then rewritten from a 10-tab layout
(28.4 KB) to a single-page operating surface (58.7 KB) with: a
sticky top bar (working-capacity tags, STOP/GO/CLEAR, Merkle
root), a working-capacity strip (runtime, shell, bin, last seal,
tau stats, merkle root), a four-gate pipeline view
(Deception / BBFB / Real-Options Lattice / Decision) that
shows real figures as the pipeline fires, a recent-runs strip
(last 10, color-coded by final action, click to reload), a
call-upon drawer enumerating all 32 HTTP endpoints, and inline
panels for facts / ledger / MCP+tau+jobs / ontology 54 patterns
/ affidavit (with preview + generate) / batch upload /
evaluation suite / changelog. The handle for the refusal
short-circuit (finalAction=REFUSED returns a different shape
than the full pipeline) is handled in loadRunIntoView. Tests:
86 passed, 1 host-dependent skip. Sealed
UI_OPERATOR_FACING_REDESIGN_2026_07_17.

Immediately after the UI seal, the operator confirmed two
follow-on items with "yes and yes": (a) hard-delete the stale
02_Technical/tests/ mirror (a 933-byte test_smoke.py and a
misplaced first-draft test_static_dir.py, both duplicating
canonical files at the project-root tests/) and (b) rebuild the
Tauri desktop binary so the new UI ships to distribution. Both
are now CLOSED. The stale directory was removed via PowerShell
Remove-Item (rm -rf was denied by the shell harness; the
operator confirmed hard-delete via AskUserQuestion). Effect on
fingerprints: REF-3 went 52 -> 50 .py files, REF-4 went 220 ->
218 files; REF-1/2a/2b unchanged; chain still MATCH. The Tauri
rebuild was a two-pass sequence: first `npx tauri build
--no-bundle` (2m 46s warm-up) to confirm the new web/ would
link into the binary, then full `npx tauri build` (1m 34s
incremental) producing the .exe (4,852,736 bytes, sha256
791bb7b9...), the .msi installer (2,318,336 bytes, sha256
aea590f2...), and the .nsis installer (1,628,695 bytes, sha256
9e96a519...). All three artefacts were verified as valid (PE32+
GUI, valid MSI with proper metadata, valid NSIS installer) and
mirrored to D:\OrderGetItRight\02_Technical\tauri-shell\target\
release\. Code sign status is "NotSigned" -- identical to the
2026-07-12 build, no regression. 4 pre-existing warnings
carried through, none blocking. The 32-endpoint surface and
all 88 tests are still intact. Sealed
TAURI_REBUILT_FOR_UI_REDESIGN_2026_07_17 (block 6775; root
0e7c200775e5926440838111bab8fe8d399414f15081a6308a7b5fe5b9ac50fe
at the moment of seal). A subsequent
TAURI_REBUILT_DOCS_REFRESHED_2026_07_17 seal (block 6870; root
f3e10f4a2ce645f3727954f2876c6d51a514024652de38d5b1ecf5226cacc7cd
at the moment of seal) captured the first doc refresh.

Following that, the operator flagged that the print-and-pin
hardcopy files (OPERATOR_MANUAL.txt, HARD_COPY_BACKUP_PLAN_1-2-3.txt)
and the present-tense ritual commands in YELLOW_RIBBON.md had
several stale references. Specifically: the project-root path
still pointed at the pre-fork .claude directory (changed during
the 2026-07-16 OneDrive reconciliation), the .py file count was
44 (actual 50), the test count was "3/3 boundary + 2/2 normalize"
(actual 86/1), the agent count said "FIVE AGENTS" (actual 10
named modules), the "WHAT TO DO IF SOMETHING BREAKS" section
listed 6 generic steps and the wrong test command, and the 130-line
"next operator notes" section in HARD_COPY_BACKUP_PLAN still
documented the 2026-07-12 IndentationError bug (fixed at block
416, six days earlier). All six present-tense stale references
have now been corrected. REF-3 / REF-4 unchanged (no source or
tree changes; 50 .py / 218 files). REF-5 advanced through
automatic SHUTDOWN seals written by the FastAPI lifespan handler
during the post-edit pytest run; REF-6 re-derived in lockstep.
The two historical `.claude` references that remain
(YELLOW_RIBBON.md line 91, CONTEXT_WINDOW.md line 104) are
deliberate: they describe the fork-resolution history in the
past tense.

================================================================================
WHERE EVERYTHING IS
================================================================================

  Build root:           C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight
  Source code:          02_Technical\src\
  Agents:               02_Technical\src\agents\  (10 named modules, all deterministic)
  Engines:              02_Technical\src\engines\  (9 engines, pure stdlib)
  Web UI:               02_Technical\web\index.html
  Tests:                tests\  (10561 chain block; 88 tests, 87 passing + 1 host-dependent skip)
  Tauri shell:          02_Technical\tauri-shell\  (built, artefacts on disk)
  Merkle chain:         03_Vault\facts_registry.json
  Job registry:         03_Vault\job_registry.json
  Human changelog:      04_Validation\changelog.log
  Engine changelog:     04_Validation\changelog.log  (same file)
  Hard-copy plan:       04_Validation\hardcopy\HARD_COPY_BACKUP_PLAN_1-2-3.txt
  Operator manual:      04_Validation\hardcopy\OPERATOR_MANUAL.txt
  Quick ref card:       04_Validation\hardcopy\QUICK_REFERENCE_CARD.txt
  Open items doc:       04_Validation\OPEN_ITEMS_AND_REFERENCE.md
  First-run guide:      04_Validation\INTRODUCTION.md
  Troubleshooting:      04_Validation\TROUBLESHOOTING.md
  This document:        04_Validation\YELLOW_RIBBON.md
  Strategy:             00_Strategy\STRATEGY.md
  Governance:           00_Strategy\GOVERNANCE.md
  Ontology (human):     01_Methodology\DECEPTION_ONTOLOGY.md
  Mathematics:          01_Methodology\MATHEMATICS.md
  Real-options lattice: 01_Methodology\REAL_OPTIONS_LATTICE.md
  Deployment notes:     02_Technical\DEPLOYMENT.md
  Resourcing notes:     02_Technical\RESOURCING.md
  Constants:            02_Technical\config\constants.py
  Build zip:            04_Validation\ogir-build-1.0.0.zip
  Backups from session: *.bak-pre-*  (7 files; do not delete)

================================================================================
THE SIX FINGERPRINTS  (proof of identity)
================================================================================

These six numbers, taken together, identify this exact build of
the project. If a third party has the project folder, they can
re-derive every one of them in under ten seconds. If a third
party does not have the project folder, they do not have the
project; the numbers are useless to them without the files.

  REF-1  constants.py SHA-256
        481effb1a956e28b09efc0353de95ad81a52cdb8d851236b1aff2fd27af52f4e
        Re-derive:  python -c "import hashlib; print(hashlib.sha256(open('constants.py','rb').read()).hexdigest())"

  REF-2  STRATEGY.md + GOVERNANCE.md SHA-256
        STRATEGY:    e4b2ff1928e2b8e4d253cf7a2feaf66457df6df4c01b49793a499286023aa75d
        GOVERNANCE:  0c2335de7e3e1962f30cacc3d12fe2921e8565287190c04d2dec01328f8f028d
        Re-derive:  same as REF-1, applied to each .md file

  REF-3  source tree (every project .py under 02_Technical, in order) SHA-256
        2cec0eccfd3bed43d3aa7f2a1134c1a772a7d6e100acff8966db9106895d7845
        Re-derive:  see OPEN_ITEMS_AND_REFERENCE.md PART 3 for the script
        (50 .py files; was 52 before TAURI_REBUILT_FOR_UI_REDESIGN_2026_07_17
         closed A10 -- the stale 02_Technical/tests/ mirror was removed)

  REF-4  tree shape (which files exist, regardless of content) SHA-256
        982e489f5d9d92c93c295bd0945f562d40fc2b5a29902ce18cfff5fa71c66832
        Re-derive:  see OPEN_ITEMS_AND_REFERENCE.md PART 3 for the script
        (465 files; rotated from the prior fingerprint
         542ef5a95f5b44a19920afaccca252e150be9ab33cbe9a9b20cfc03b1703bce5
         -- the file list rotated between seals; the change in
         REF-4 reflects the live tree at TODO_FULL_RECONCILED_2026_07_17)

  REF-5  Merkle root (live chain state)
  5b66058e8d322f00a724a9f4b36cdf3f3f9a6d7a01dc147c9ebf843bf05b71f3
  (10561 blocks, last seal 2026-07-17T18:52:05Z, refreshed 2026-07-18)
  (HANDOVER_2026_07_17_EVENING_DOCS_RECONCILIATION sealed the
   end-of-session handover; the verify_chain run that followed
   wrote one more SHUTDOWN block, taking the chain to 7156)

  REF-6  composite (a single number anyone can write down)
        5d9fd3d5353736d6615adf0040dbfedb369bd44269bc3af9a5b3a92c312248e3
        Computed from REF-1..REF-5 concatenated in order.
        Re-derive:  python -m src.verify_chain --print-refs
        (Note: --print-refs is currently affected by a pre-existing
         path bug; for now re-derive by hand or use the small one-shot
         Python snippet in TROUBLESHOOTING.md REF re-derivation entry.)
        Or by hand: concatenate the five strings above, sha256 them.

If REF-1 through REF-5 all match on a third party's machine, they
have the project. If any one of them does not match, they have a
different version. The project does not need a license server, a
cloud account, a vendor relationship, or a phone home to prove
itself. The hashes are the proof.

================================================================================
IF SOMEONE CUTS THE RIBBON
================================================================================

If a future session, a vendor, a model, or a person tells you:

  - "We have a better way to do this and we're going to rewrite
    the project."  -- Let them. But do not let them delete the
    ribbon. Move the build folder aside, let them write their
    version, then run the verify command above on BOTH folders.
    If their version's Merkle root matches the original, the
    change is honest. If it does not match, something was lost.

  - "This project is too old. The Python version is wrong, the
    libraries are deprecated, we need to start fresh."  -- They
    may be right about the libraries. They are wrong about
    starting fresh. The Merkle chain is the proof of every
    decision the program ever made. A fresh start wipes the
    chain. The chain is the proof. Do not wipe the chain.

  - "We are migrating this to the cloud / to a SaaS / to a
    platform."  -- The whole point of this project is that it
    does not live in the cloud, on a SaaS, or on a platform.
    If they migrate it, the migrated thing is not this project.
    It is a different project that uses some of the same names.
    The original stays on your disk. The original is the
    project. The migration is a different project.

  - "We have updated the constants / patched a bug / changed
    the ontology."  -- Run `python -m pytest` from the project
    root. Expect 88 pass + 1 host-dependent skip (was 86 before the 2026-07-18 R1-R4 gate regression test was added). If those counts
    match, the change may be valid. Then read
    04_Validation/changelog.log. If the change is not in the
    changelog, it is not in the chain. If it is not in the chain,
    it is not a change the operator approved. Push back.

  - "We are the new maintainers."  -- The maintainer is the
    person whose name is in config/constants.py as
    PROJECT_OPERATOR. The maintainer is Justin Barnett. If the
    maintainer changes, that change must be sealed to the
    chain. If the maintainer changes without a seal, it is
    not a change. It is a claim.

  - "This project has been deprecated / sunset / archived."
    -- The Merkle chain does not deprecate. The chain is the
    chain. The operator is the operator. The project is the
    project. Until the operator signs a document that says
    otherwise, sealed to the chain, the project is not
    deprecated.

In all of these cases, the answer is the same: re-derive the
Merkle root. If it matches, the project is intact. If it does
not match, the project has been changed without going through
the chain, and that is the moment to push back, not before.

================================================================================
THE RIBBON IS NOT THE CHAIN. THE RIBBON IS THE FACT THAT THE CHAIN
EXISTS AND IS ON YOUR DISK AND NO ONE ELSE'S.
================================================================================

The chain is at 03_Vault/facts_registry.json. It is on your disk. It is not on GitHub. It is not in the cloud. It is
not behind a login. It is a file. If you have the file, you have
the chain. If you do not have the file, you do not have the
project. That is the only proof that matters.

Print this page. Put it with the operator manual. Put a copy in
the bank safe-deposit box with the USB stick. Put a copy in the
fireproof safe. The ribbon is the paper that says where the
chain is. The chain is the proof.

Welcome home.

================================================================================
END OF DOCUMENT
================================================================================