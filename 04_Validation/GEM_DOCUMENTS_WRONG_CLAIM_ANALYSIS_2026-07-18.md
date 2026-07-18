# Gemini Documents Wrong-Claim Analysis

## Source of the wrong data

The two Gemini files (`Gemini Gem Knowledge Base Configuration.txt` and `Gem Senior AUDIT RESULTS..txt`) were created on disk at 2026-07-18 18:09 and 18:10 local time. Their content is based on a stale snapshot of the project from 2026-07-16.

The exact source of the "3,033 blocks" claim is:

- File: `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\04_Validation\scripts\phase_4_fingerprints.json`
- Generated: `2026-07-16T00:32:18.928132+00:00`
- Field: `"ref5_block_count": 3033`
- Field: `"ref5_merkle_root": "26501872d1a9d4196bde427b38fd099e7155de942a2f6bfeebad005b2f98653b"`

This was an accurate fingerprint **when it was generated on 2026-07-16**. The Gemini files copied it verbatim two days later without refreshing the fingerprint.

## When the underlying facts changed

| Claim in Gemini files | When it was true | What changed after | Live state (2026-07-18) |
|---|---|---|---|
| 3,033 blocks, root 26501872d1a9d419... | 2026-07-16 00:32 | Block sealing continued | 12,008 blocks, root changes with every seal |
| 52-pattern ontology v3.8 / v3.9 | Before 2026-07-18 03:58 | `ONTOLOGY_BUMP_R1_R4_2026_07_18` commit | v3.10, 54 patterns, R1-R4 + R5-EXTENDED-2 gates |
| No Git / project not using Git | Before 2026-07-18 02:48 | `GIT_ADOPTED_IN_PARALLEL_2026_07_18` commit | Git branch `ogir-build-2026-07-18` |
| NIZK proof | Early build | Renamed in live code (F6) | `integrity_digest` |
| Real-options valuation | Before F7 reframe | `F7_LATTICE_REFRAMED_2026_07_18` commit | deception-adjusted optionality index |
| SQLite / Azure migration | Never implemented | Still aspirational in roadmap | `facts_registry.json` JSON file |
| Tauri binary signed | Never | Still unsigned (F10) | Unsigned; operator decision pending |

## Why the Gemini files are wrong

The files are not malicious. They are **stale assistant specifications**. They were generated from a 2-day-old fingerprint and from older project documents (`INTELLECTUAL_PROPERTY_RIGHTS.txt`, `SPECS.txt`, `QUICK_REFERENCE_CARD.txt`) that themselves were updated during the 2026-07-18 build session (C2_IP_AUDIT at block 2678 and C1_quick_reference_card refresh).

The Gemini assistant apparently:
1. Read `phase_4_fingerprints.json` (2026-07-16) for block count/root.
2. Read older docs that still said v3.8 / 52 patterns.
3. Did not re-run `python -m src.verify_chain` or `git status` before generating the configuration.
4. Added aspirational roadmap items (SQLite, Azure, ISO 42001 certification) as if they were current architecture.

## Specific factual errors detected

### Gemini Gem Knowledge Base Configuration.txt

1. **"3,033 blocks"** -- stale; actual 12,008.
2. **"52 deception patterns / v3.9"** -- stale; actual 54 patterns v3.10.
3. **"migrating to a local, binary SQLite database"** -- not implemented.
4. **"Azure App Service" / cloud stateless deployment** -- not implemented.
5. **"signed binary"** -- not signed.
6. **"no Git"** -- Git adopted 2026-07-18.

### Gem Senior AUDIT RESULTS..txt

1. **"Section 336 of the Corporations Act 2001 anchors ASQM 1 / ASA compliance"** -- s 336 is the AUASB's power to make standards, not a direct obligation on a personal tool.
2. **"70/30 rule of AI development"** -- not a recognised standard; a heuristic from productivity blogs.
3. **"FRIA before production release" under NIST AI RMF Manage** -- FRIA is EU AI Act Article 27, not NIST.
4. **"ISO/IEC 42001 certification"** -- useful reference, not a self-imposed certification requirement.
5. **"3,033 blocks" / root** -- stale fingerprint.
6. **Implied project is not auditable/compliant** -- partially true as an aspiration assessment, but the framing overstates statutory obligations.

## Recommendation

Treat the Gemini files as **draft assistant specs from a stale snapshot**. Do not use them as project state. The authoritative live state is:

- `03_Vault/facts_registry.json` and `python -m src.verify_chain`
- `04_Validation/OGIR_ASSESSMENT_2026-07-18.md`
- `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
- `04_Validation/HANDOVER_NEXT_SESSION_2026-07-18.md`
- Git branch `ogir-build-2026-07-18`

If you want a refreshed Gemini configuration, regenerate it after running `python -m src.verify_chain --print-refs` and reading the current `OPEN_ITEMS_AND_REFERENCE.md`.
