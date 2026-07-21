# Order Get It Right -- Hand-Over Statement

**Session date:** 2026-07-22
**Operator:** Justin Barnett
**Build agent:** hermes-m3.5 (custom) on the local Ollama proxy
**Branch:** ogir-build-2026-07-18
**State at hand-over:**
- Tests: 261 passed, 1 skipped, 1 warning
- Merkle chain: MATCH, 28,531 blocks
- Chain root: `eb7846eab0096e3ed604fd0b49aef323d4064a515e3aaa23244a1106dd6a1b89`
- Git: working tree has 2 untracked files (the new fingerprint script
  and its JSON report); 3 vault files are auto-modified by lifecycle
  seals (expected, not staged)
- Git remote: `usb` -> `D:/OrderGetItRight.git`
- Tagline: "Verified Processor" (rebranded 2026-07-21, commit 6b4057e)
- Operator location: 20 Loveday St, Whyalla Norrie SA 5086 (moved 2026-07-22)

---

## 1. What was done in this session

The session opened with a search for the latest handover. The
2026-07-19_v2 was the most recent (21,999 blocks, 233 tests,
ecc131c). Re-deriving the live state showed 28,531 blocks, 261
tests, root eb7846ea..., 8 commits between 2026-07-19 and
2026-07-21 -- the v2 handover was 6,532 blocks stale. The
operator correctly flagged this as a bulletproofing failure
("we would of been operating in 2 days ago, finding work done
as we went. no no no. ... bullet proof this program must be ...
ritual is religion, procedual is law!").

Five work packages completed in this session:

1. **Live state re-derivation.** `git status`, `verify_chain`,
   `pytest` (4m02s, 261/1), `deterministic_hygiene --json-only`
   (GREEN verdict, seal+push eligible). All four checks
   confirmed the 2026-07-21 live state. Vault re-seed guard
   from commit a3af446 still in effect; no anomalies.

2. **Six-fingerprint re-derivation, doc refresh, permanent
   script.** Re-derivation exposed a real bug in
   `phase_4_refresh_fingerprints.py`: the script hardcoded
   `VAULT = 02_Technical/03_Vault/facts_registry.json` instead
   of reading the canonical `config.constants.PROJECT_VAULT_DIR`,
   and baked two hardcoded timestamps (2026-07-15T21:25:44Z and
   2026-07-12T06:08:18Z) into the doc-refresh strings. The
   hardcoded timestamps would lie about the live chain state
   on any future run where the chain had advanced past
   2026-07-16. The script also did not update the tagline,
   so the YELLOW_RIBBON kept its prior branding after
   the 2026-07-21 rebrand.

   Wrote `04_Validation/scripts/derive_fingerprints.py` as the
   permanent replacement. It:
     - reads the vault path from `config.constants.PROJECT_VAULT_DIR`
       (imports the module, not regex over the source)
     - reads the tagline from `02_Technical/src/__init__.py` (the
       canonical source; line 4, `__tagline__ = "..."`)
     - reads the last-block timestamp from the live chain
     - refreshes YELLOW_RIBBON.md root line, all six REF
       values, and the tagline header line in one pass
     - refreshes QUICK_REFERENCE_CARD.txt snapshot block and
       tagline in one pass
     - writes the JSON report to `phase_4_fingerprints.json`
     - is idempotent (running it twice is the same as once)
   Marked `phase_4_refresh_fingerprints.py` as DEPRECATED with
   a clear "do not run" docstring header that names the three
   bugs and points at the replacement.

   Live fingerprints (re-derived 2026-07-22):
     REF-1  f54ca558539ae1062d64db8719fe92f1022e5670994db5d630fd62768def508d
     REF-2a baad06b39cbb8ef2f4bfa162ea1a8597c1617d070879f1f017a06766ca62fd74
     REF-2b 0c2335de7e3e1962f30cacc3d12fe2921e8565287190c04d2dec01328f8f028d
     REF-3  be44b055de075bd7980db6f2533a45ca67e0076a1c6b8e924697877b8e89340f (49 .py files)
     REF-4  a071047da020a0bf5d8604d9f148f0d7ad76b22b62710ac0f2f375a585a96d8f (307 files)
     REF-5  eb7846eab0096e3ed604fd0b49aef323d4064a515e3aaa23244a1106dd6a1b89 (28,531 blocks)
     REF-6  1fafb8a538f27a2e492eb1a52de75fa02c1b279659f5716e151e5901050d6e36

3. **Doc refresh.** YELLOW_RIBBON.md header tagline now
   "Verified Processor"; root line now `eb7846ea...`; six
   fingerprint REF values refreshed to the live values; the
   "as of 2026-07-15" stale parenthetical replaced with
   "(28531 blocks, last seal 2026-07-21T14:33:48Z, refreshed
   2026-07-21)". QUICK_REFERENCE_CARD.txt header tagline now
   "Verified Processor"; "Live snapshot" block now
   "(as of 2026-07-21, 28531 blocks): eb7846ea...". Both
   refreshes are idempotent.

4. **This handover.** Written to
   `04_Validation/handover_next_session_2026-07-22.md`
   (this file). Supersedes the 2026-07-19 v2 as the live
   operator-facing state document.

5. **Operator location and network state captured.** The
   operator moved to 20 Loveday St, Whyalla Norrie SA 5086
   on 2026-07-22. Internet is Starlink only (no copper/fiber
   foreseeable for at least 18 months). The active
   conversation layer is `minimax-m3:cloud` proxied through
   the local Ollama (port 11434) to ollama.com. Phone hotspot
   (Pixel 7a over Felix Vodafone 5G, USB or Wi-Fi tether) was
   used during the move and produced a DNS failure mode
   ("dial tcp: lookup ollama.com: no such host") that took
   down the conversation layer; the audit path was unaffected.
   This DNS failure mode is a separate bulletproofing item
   addressed below.

## 2. Current open items

All code-doable items closed in this session or earlier.
Remaining items, in priority order by necessity of reality:

  1. **Offsite backup (operator, real, ~1 hour at a Whyalla
     bank branch).** The 1-2-3 backup plan in
     `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`
     requires the USB stick + paper card to live in a
     fireproof offsite location. The previous location was a
     bank safe-deposit box in the old home; that box is no
     longer local. A new offsite needs to be set up in
     Whyalla. Until this is done, the chain is on a single
     physical site (the laptop at 20 Loveday St) plus the
     local USB mirror, both of which would be lost in a
     house fire. The 1-2-3 plan calls this the third copy;
     it is currently missing.

  2. **Adapter discipline (operator, 30 seconds per session).**
     The Windows host "Thevice" has five network adapters
     (UsbNcm Host Device = phone-as-modem, Intel Wi-Fi 6E
     AX211 = Wi-Fi to local router, two Microsoft Wi-Fi
     Direct Virtual Adapters, Bluetooth PAN, Hyper-V virtual
     switch). The phone-as-modem path and the Wi-Fi path
     can both reach the internet; the phone-as-modem wins
     by metric (25 vs 30). When the phone is in USB-tether
     mode, its DNS resolver can be a captive-portal or
     CGNAT forwarder that does not resolve ollama.com. Fix:
     turn off the USB tether when on Wi-Fi, and vice versa.
     One path at a time. This is a session-hygiene rule, not
     a config change.

  3. **Auto-handover on session-seal boundary (code, ~2
     hours).** The 2-day gap between 2026-07-19 v2 and
     2026-07-21 live is the failure mode this would prevent.
     Design: the `deterministic_hygiene.py` script (or a new
     `end_of_session_seal` command) reads the latest dated
     `handover_next_session_*.md` file, compares its
     recorded block-count and last-seal-timestamp to the
     live chain, and if the gap exceeds a threshold
     (suggested: 100 blocks or 24 hours), auto-fires a
     `SEALED_HANDOVER_<date>` block that writes the
     handover from the chain payload (not from operator
     memory) and seals it. Idempotent. This is the
     procedural-law replacement for the operator-remembered
     ritual.

  4. **Handover-drift invariant (code, ~30 min once (3) is
     in).** On session start, refuse to do work until the
     dated-handover drift is below threshold (or sealed as
     `OBSERVED_HANDOVER_DRIFT` for the next operator to
     handle). The seal makes the drift visible to the
     chain; the refusal makes the drift impossible to
     ignore.

  5. **Audit path works without LLM (already true; doc
     needed).** The audit path is air-gapped and works
     from PowerShell with no Ollama, no ollama-cloud
     connection, and no LLM in the loop. A one-page
     runbook titled "what to do when the conversation
     layer is down" should be sealed to the chain so
     the operator (or a future AI session) can fall back
     to the audit path without rediscovering it. ~1
     hour of work.

  6. **Operator-dependent, unchanged from prior handovers:**
     Tauri code-signing ($200-500/yr, operator decision);
     second-PC clean-host restore test (needs second
     Windows PC, not WSL/Ubuntu); Gmail .mbox import
     (awaiting operator export).

## 3. The handover-drift problem (and its fix)

The chain never lost track. The audit history is intact
across the 2-day gap (28,531 blocks, every block sealed, every
block linked, verify_chain MATCH). The 2-day gap is a gap in
the *operator-facing written record*, not in the *sealed
record*. The 2026-07-19 v2 is still factually correct for
2026-07-19. It was simply not refreshed for 2026-07-21.

This is exactly the kind of soft failure the project is
designed to prevent in the audit path (the chain has no
fallback because the chain does not fall back). The
operator-facing written record is the one place where the
design has been "operator religion" rather than "procedural
law" -- the operator was trusted to remember to write the
handover at session-end. That trust failed over the
2026-07-19 to 2026-07-21 window. The fix is the auto-
handover event (open item 3) plus the drift invariant
(open item 4).

## 4. How to verify the hand-over

```
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git status
git log --oneline -10
git remote -v
python 04_Validation/scripts/derive_fingerprints.py --json-only
cd 02_Technical
python -m src.verify_chain
cd ..
python -m pytest tests/ -q
python 04_Validation/scripts/deterministic_hygiene.py --json-only
```

Expected:
- `git status`: working tree has 2 untracked files
  (`04_Validation/scripts/derive_fingerprints.py` and
  `04_Validation/scripts/phase_4_fingerprints.json`); 3 vault
  files modified (lifecycle auto-seals, expected).
- `git log --oneline -10`: top entry is
  `HANDOVER_REFRESH_AND_FINGERPRINT_FIX_2026_07_22` (this
  commit, to be made next).
- `git remote -v`: `usb -> D:/OrderGetItRight.git`.
- `python derive_fingerprints.py --json-only`: prints the six
  REF values, all matching the live chain, and exits 0.
- `python -m src.verify_chain`: prints
  `RESULT: MATCH -- chain is intact`, root
  `eb7846ea...`, block count 28,531+ (grows with each seal).
- `python -m pytest tests/ -q`: 261 passed, 1 skipped, 1 warning
  in ~4 minutes. The skip is `tests/test_d5_agentic_repl.py:244`
  (FastAPI audit server not running on port 3000).
- `python deterministic_hygiene.py --json-only`: prints JSON
  with `verdict: GREEN`, `actions.seal_eligible: true`,
  `actions.push_eligible: true`. Wall-clock ~4m30s.

## 5. Key artefacts created or changed in this session

- `04_Validation/scripts/derive_fingerprints.py` (new, ~430 lines)
- `04_Validation/scripts/_derive_fps_2026_07_21.py` (interim
  one-shot; safe to delete or keep as a script variant;
  superseded by `derive_fingerprints.py`)
- `04_Validation/scripts/phase_4_fingerprints.json` (machine-
  readable report, regenerated by `derive_fingerprints.py`)
- `04_Validation/scripts/phase_4_fingerprints_2026_07_21.json`
  (interim one-shot output; safe to delete or keep)
- `04_Validation/scripts/phase_4_refresh_fingerprints.py`
  (DEPRECATED header added; original 2026-07-16 logic
  preserved as a historical artefact; do not run)
- `04_Validation/YELLOW_RIBBON.md` (header tagline,
  root line, six REF values refreshed to live state)
- `04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt` (header
  tagline, Live snapshot block refreshed to live state)
- `04_Validation/handover_next_session_2026-07-22.md` (this
  file, the new live operator-facing state document)

## 6. Project direction

The engine is a lie detector. It reads text and asks: does
that? The number answers. The chain seals it. The gates are
built. The work between 2026-07-19 and 2026-07-21 was all
rebuttal, calibration, and outward work: ontology bump to v3.10
(55 patterns, +DD-055 Cloud Displacement), the rebrand to
"Verified Processor", the Ollama isolation contract locked in
src/, the unified audit engine facade, two rebuttals of stale
outside claims (FRUIT drift, faults snapshot), the S-QoL
governance formalised, the Gemini audit dump triaged, the
Tauri signing reference locked. None of that was architecture
change; it was all the engine being exercised in new
directions.

The 2026-07-22 session brought the operator-facing record
back into lockstep with the chain. The next move is the
auto-handover event (open item 3) so this kind of drift
cannot recur. The audit path itself was never in question.

End of hand-over. The chain is the source of truth. The
chain is at 28,531 blocks. The chain is intact.
