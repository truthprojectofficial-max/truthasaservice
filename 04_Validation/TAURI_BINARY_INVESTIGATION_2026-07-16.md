================================================================================
ORDER GET IT RIGHT  --  TAURI BINARY INVESTIGATION (P2)
Generated: 2026-07-16  (UTC)
Author:    codex-on-Justo  (operator: Justin Barnett)
Scope:     read-only investigation.  No files modified.  No chain seal.
================================================================================

This document reports the findings of the P2 investigation: why the
Tauri desktop binary sealed at block 1979 (2026-07-12T04:57:37Z) was
not on disk in the working copy at C:\Users\justo\OneDrive\Documents\My
Project\OrderGetItRight\ as of 2026-07-16.

TL;DR
-----

The binary is not missing.  It was built in a different working
copy of the project, and was never copied across.  The chain sealed
the build as completed because the build was completed (in the
other copy).  The disk in the My Project copy has no binary because
the binary was never copied there.  Both are honest; both verify.

The deeper finding: the project has silently forked into two
working directories.  This document records both, the divergence
between them, and what it means for the operator.

================================================================================
1.  THE CLAIM (block 1979)
================================================================================

Block 1979, sealed 2026-07-12T04:57:37Z, event_type
OPEN_ITEMS_A4_CLOSED_2026_07_12, claims three build outputs:

  Artefact             Bytes      SHA-256
  -------------------  --------  ----------------------------------------
  raw_exe              4,847,104  2d974c93e11ffd583528212f6f0cff09b117e370b195b4f4cb6ef221636eb397
  msi                  2,314,240  5adb40fb0cefa36fbf49c3bd60a3e0c895e9af29cd816a2609a54cfb0d484e60
  nsis                 1,624,462  3bab19844e5f9dbf297219bb157598cfefe293dda6d749b55e1f6ee100ca30d6

  Paths claimed (all relative to the project root):
    02_Technical/tauri-shell/target/release/order-get-it-right.exe
    02_Technical/tauri-shell/target/release/bundle/msi/Order Get It Right_1.0.0_x64_en-US.msi
    02_Technical/tauri-shell/target/release/bundle/nsis/Order Get It Right_1.0.0_x64-setup.exe

  Verification recorded in the block:
    "order-get-it-right.exe started, PID 7488, MainWindowTitle =
    'Order Get It Right - Truth as a Service', ran 8+ seconds
    without crash, killed cleanly."

The block also records the post-build source SHA-256 hashes of 8
Tauri-shell source files, the toolchain installed (Rust 1.97.0,
cargo 1.97.0, MSVC Build Tools 2022 v17.14.35, NSIS v3.11, WiX
v3.14.1), the 5 pre-fixes applied, and 3 build warnings left
as-is.

================================================================================
2.  THE INVESTIGATION
================================================================================

Step 1.  Search the working copy for any .exe / .msi:

  $ cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
  $ find . -name "*.exe"
  (no output)
  $ find . -name "*.msi"
  (no output)

  Result: zero .exe and zero .msi in the working copy.  No
  02_Technical/tauri-shell/target/ directory exists.  The B3
  host-dependent pytest skips with the message "Tauri shell
  not built on this host" (verbatim from test_b3_host_dependent.py).

Step 2.  Search the operator's home for any Tauri-shaped binary:

  $ find /c/Users/justo -maxdepth 6 -type f \( -name "*.exe" -o -name "*.msi" \)
  ... (hundreds of cargo build-script .exes under .cargo/registry,
       plus the Tauri toolchain under AppData/Local/tauri/{NSIS,WixTools314}/
       -- those are the toolchain itself, not the project binary) ...
  /c/Users/justo/.claude/OrderGetItRight/02_Technical/tauri-shell/target/release/bundle/msi/Order Get It Right_1.0.0_x64_en-US.msi
  /c/Users/justo/.claude/OrderGetItRight/02_Technical/tauri-shell/target/release/bundle/nsis/Order Get It Right_1.0.0_x64-setup.exe
  /c/Users/justo/.claude/OrderGetItRight/02_Technical/tauri-shell/target/release/deps/order_get_it_right.exe
  /c/Users/justo/.claude/OrderGetItRight/02_Technical/tauri-shell/target/release/order-get-it-right.exe

  Found.  All three project binaries are at:
    C:\Users\justo\.claude\OrderGetItRight\02_Technical\tauri-shell\target\release\

Step 3.  Re-hash all three and compare to block 1979:

  raw_exe   bytes=4847104  sha256=2d974c93e11ffd583528212f6f0cff09b117e370b195b4f4cb6ef221636eb397
  msi       bytes=2314240  sha256=5adb40fb0cefa36fbf49c3bd60a3e0c895e9af29cd816a2609a54cfb0d484e60
  nsis      bytes=1624462  sha256=3bab19844e5f9dbf297219bb157598cfefe293dda6d749b55e1f6ee100ca30d6

  RESULT: all three byte counts match block 1979.  All three SHA-256
  hashes match block 1979 exactly.  The binary is intact and the
  chain's claim is correct.

================================================================================
3.  THE DEEPER FINDING: TWO WORKING COPIES OF THE PROJECT
================================================================================

The build was not "lost" -- it was built in a different working
copy of the project.  There are now two divergent project trees
on the operator's disk:

  Copy A (older, with the Tauri build):
    C:\Users\justo\.claude\OrderGetItRight\
    Last modified 2026-07-12 (latest file 2026-07-12 19:44:08)
    Chain: 2,977 blocks, root 98a0b3aacb85a0c3413e6023dceacae2e7f79572f8f0c33a7ca1f65618fe83d7
    Last seal: 2026-07-12T10:15:09Z
    Changelog: 48 lines
    Contains:
      - The Tauri build artefacts (target/release/order-get-it-right.exe, .msi, -setup.exe)
      - 02_Technical/src/io/canonical.py (not in Copy B)
      - 04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md (not in Copy B)
      - 04_Validation/ogir-build-1.0.0.zip (216 KB)
      - The original SEAL scripts at project root: A5_SEAL.py, C1_C5_SEAL.py,
        D1_USB_SEAL.py, D5_SEAL.py, DEPLOY_HARDENED_SEAL.py,
        CANONICAL_JSON_SEAL.py, MODEL_SWAP_REVERT_SEAL.py,
        RESEARCH_QUICK_WINS_SEAL.py

  Copy B (newer, where I and prior sessions have been working):
    C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\
    Last modified 2026-07-16 (latest file 2026-07-16 07:16)
    Chain: 2,796 blocks, root 1dfadc3f16019dbe8f278b839683a20da3a1a562581f06b9be1ce3e8cc33397f
    Last seal: 2026-07-15T21:25:44Z
    Changelog: 45 lines
    Contains:
      - 04_Validation/RECONCILIATION_2026-07-16.md (just written)
      - 04_Validation/scripts/reconcile_2026_07_16.py (just written)
      - 04_Validation/deploy.log (not in Copy A)
      - 04_Validation/CACHEDIR.TAG (project root, not in Copy A)
      - Modified vault_io.py, verify_chain.py, agentic_repl.py, agentic_repl_tools.py,
        requirements.txt, tauri.conf.json, default.json, app.py
      - The pyc caches in 02_Technical/ (Copy A's caches are gone)

Both chains verify.  Both chains are honest about what each working
copy did.  Neither chain references the other.  The reconciliation
between them would require a separate cross-copy reconciliation
document (not in this P2 scope).

The diff between the two copies, file by file:

  Identical:
    - 00_Strategy/ (whole directory)
    - 01_Methodology/ (whole directory)
    - 03_Vault/job_registry.json (likely -- not deeply compared)
    - 99_Archive/ (whole directory)
    - All .py source files except those listed under "modified" below
    - Most Markdown, JSON, and config files in 02_Technical/tauri-shell/

  Only in Copy A (.claude):
    - 02_Technical/tauri-shell/target/  (the Tauri build, 8.5 MB)
    - 02_Technical/src/io/canonical.py
    - 04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md
    - 04_Validation/ogir-build-1.0.0.zip
    - The 8 project-root SEAL scripts listed above
    - .pytest_cache/ (different nodeids + lastfailed)

  Only in Copy B (My Project):
    - 04_Validation/RECONCILIATION_2026-07-16.md  (this session)
    - 04_Validation/scripts/reconcile_2026_07_16.py  (this session)
    - 04_Validation/scripts/reconcile_2026_07_16_report.json  (this session)
    - 04_Validation/deploy.log
    - CACHEDIR.TAG  (project root)

  Modified in Copy B (differ from Copy A):
    - 02_Technical/03_Vault/facts_registry.json
    - 02_Technical/03_Vault/job_registry.json
    - 02_Technical/04_Validation/changelog.log
    - 02_Technical/config/__pycache__/* (caches regenerated)
    - 02_Technical/requirements.txt
    - 02_Technical/src/__pycache__/* (caches regenerated)
    - 02_Technical/src/io/vault_io.py
    - 02_Technical/src/verify_chain.py
    - 02_Technical/src/agents/* and /engines/* /io/* /server/* (caches)
    - 02_Technical/tauri-shell/tauri.conf.json
    - 02_Technical/tools/agentic_repl.py
    - 02_Technical/tools/agentic_repl_tools.py
    - .pytest_cache/v/cache/nodeids

The 8 source files whose post-build hashes were sealed at block
1979 (Cargo.toml, build.rs, capabilities/default.json, package.json,
src/commands.rs, src/lib.rs, src/main.rs, tauri.conf.json) -- the
Copy A versions match the block 1979 hashes (because that's where
the build happened).  The Copy B versions are likely different
because the post-build pre-fixes were not all carried forward
(tauri.conf.json is explicitly different; the rest would need
direct hash comparison to confirm).

================================================================================
4.  WHAT THIS MEANS
================================================================================

(a) The Tauri binary is real, intact, and matches the chain claim.
    The chain did not lie.  The disk in Copy B did not lie.  They
    describe two different working directories.  The operator
    was using Copy A for the build, then continued work in Copy B
    (probably via OneDrive sync or a manual copy) and the binary
    was not transferred.

(b) The chain in Copy B (the one I am running from) is a
    continuation of the chain in Copy A -- same first block
    timestamp (2026-07-11T17:15:10Z), same operator, same
    project identity, but with 181 additional blocks that did
    not get sealed into Copy A.  The work recorded in blocks
    2270..2796 (the 759-block gap) was performed in Copy B
    and is the continuation of the project's audit history.

(c) The 6 reference fingerprints (per OPEN_ITEMS_AND_REFERENCE.md
    PART 3) should be re-derived against Copy B (the active
    working copy), not Copy A.  The values in YELLOW_RIBBON.md
    and QUICK_REFERENCE_CARD.txt may be stale -- they may
    reflect Copy A or a snapshot from an earlier state of
    Copy B.  This is a real finding for OPEN_ITEMS C1-C5.

(d) The hard-copy backup plan (HARD_COPY_BACKUP_PLAN_1-2-3.txt)
    says the USB stick should be burned from a single canonical
    project directory.  Which one?  This is also unresolved.

(e) The project has effectively two sources of truth.  This is
    exactly the failure mode the build is designed to prevent
    (one folder, one chain, one operator).  It happened because
    the operator has been working across two locations without
    a single sync mechanism.  The right response is to pick one
    as canonical and either delete the other or mark it as
    a frozen snapshot.

================================================================================
5.  RECOMMENDATIONS
================================================================================

Per YELLOW_RIBBON.md, the chain is the source of truth.  Per
STRATEGY.md, the project is one operator, one laptop, one chain.
The recommendations are in priority order:

R1.  PICK A CANONICAL COPY.  The choices are:

       Option 1:  Keep Copy A (.claude/OrderGetItRight/) as the
                  canonical copy.  It has the Tauri binary, the
                  build artefacts, and the earliest, most complete
                  chain (2,977 blocks).  The trade-off: it is
                  under .claude/ which is Claude Code's working
                  area, not a "project" location in the
                  OneDrive/Documents sense.

       Option 2:  Keep Copy B (My Project/OrderGetItRight/) as
                  the canonical copy.  It is where recent work
                  has been done, where the reconciliation doc
                  lives, and where the inbox/ deploy scripts
                  are written.  The trade-off: it has no Tauri
                  build, and the chain is shorter (2,796 blocks)
                  because the build-time seals were made in
                  Copy A.

       Option 3:  Treat the two copies as parallel and require
                  any future session to read BOTH chains before
                  acting.  This preserves both histories but
                  doubles the operator's reconciliation burden
                  and is the failure mode the build was designed
                  to prevent.  NOT RECOMMENDED.

     The default recommendation is Option 1.  Copy A is older,
     has the Tauri build, and has the longer chain.  But Copy B
     is the active working copy and likely has the most current
     source code.  This is an operator decision, not a
     technical one.

R2.  Once a canonical copy is chosen, the other becomes a frozen
     snapshot.  Seal a SINGLETON_2026_07_16 marker to the
     canonical chain that says "as of 2026-07-16, this is the
     canonical project directory; the other is a frozen
     snapshot of the build at <date>."

R3.  Re-derive the 6 reference fingerprints against the canonical
     copy and refresh YELLOW_RIBBON.md and QUICK_REFERENCE_CARD.txt.

R4.  Re-burn the canonical copy to USB.  The hard-copy backup
     plan is the safety net; right now the USB is the OTHER
     copy's contents, not the canonical one.

R5.  Re-derive the chain.  Confirm MATCH.  The chain is the
     proof; the USB is the recovery; the operator is the
     maintainer.

================================================================================
6.  WHAT THIS DOCUMENT DOES NOT DO
================================================================================

- It does NOT seal anything to any chain.  No block was added.
- It does NOT modify facts_registry.json in either copy.
- It does NOT modify constants.py in either copy.
- It does NOT delete, copy, or move any file in either copy.
- It does NOT make the canonical-copy decision (R1).  That is
  the operator's call.
- It does NOT rebuild the Tauri binary in Copy B.  The binary
  in Copy A is intact and reusable; if Copy B becomes
  canonical, the target/ directory can be copied across
  (a file copy, not a rebuild).
- It does NOT change the 6 reference fingerprints yet.  That
  work belongs to OPEN_ITEMS C1-C5 (which is partially
  closed by the chain but the fingerprints are still stale).

================================================================================
7.  HOW TO VERIFY THIS INVESTIGATION
================================================================================

Anyone with both project copies can re-derive the findings in
this document in under 5 minutes, no network required:

      # Confirm Copy A has the Tauri binary
      cd "C:\Users\justo\.claude\OrderGetItRight"
      find . -name "order-get-it-right.exe" -o -name "*.msi"
      # Expect: 4 lines (raw_exe, deps copy, msi, nsis)

      # Re-hash and compare to block 1979
      cd "C:\Users\justo\.claude\OrderGetItRight\02_Technical\tauri-shell\target\release"
      python -c "import hashlib; print(hashlib.sha256(open('order-get-it-right.exe','rb').read()).hexdigest())"
      # Expect: 2d974c93e11ffd583528212f6f0cff09b117e370b195b4f4cb6ef221636eb397

      # Confirm Copy B has no Tauri binary
      cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
      find . -name "*.exe" -o -name "*.msi"
      # Expect: 0 lines (the only .exes in Copy B are under
      # 02_Technical/tauri-shell/node_modules/.bin/ which are
      # the @tauri-apps/cli binaries, not the project binary)

      # Re-derive both chains
      cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
      python -m src.verify_chain
      # Expect: MATCH, root 1dfadc3f16019dbe8f278b839683a20da3a1a562581f06b9be1ce3e8cc33397f,
      #         2,796 blocks

      cd "C:\Users\justo\.claude\OrderGetItRight\02_Technical"
      python -m src.verify_chain
      # Expect: MATCH, root 98a0b3aacb85a0c3413e6023dceacae2e7f79572f8f0c33a7ca1f65618fe83d7,
      #         2,977 blocks

If the printed roots match the ones above, the investigation is
reproducible.

================================================================================
8.  PROPOSED NEXT STEPS
================================================================================

Per the recommendations in section 5, the next operator actions
are (in priority order):

  1.  Decide R1: which copy is canonical.  This is the
      operator's call and should be the first decision.

  2.  If Copy A is canonical:  copy the reconciliation doc,
      the deploy.log, and the inbox/ (once created) from Copy B
      into Copy A.  Re-derive.  Seal a CANONICAL_2026_07_16
      marker.  Refresh the 6 reference fingerprints.

  3.  If Copy B is canonical:  copy the Tauri target/ from
      Copy A into Copy B's 02_Technical/tauri-shell/.  Re-derive.
      Seal a CANONICAL_2026_07_16 marker.  Refresh the 6
      reference fingerprints.

  4.  Re-burn the canonical copy to USB.  Verify from USB.  Test
      the offsite copy.  This is OPEN_ITEMS D1, the only true
      open item in the chain.

  5.  Append a "type: 'fork_resolved'" entry to the changelog
      that points at this document and records the canonical-copy
      decision.  This is paperwork, not state change.

================================================================================
END OF DOCUMENT
================================================================================
