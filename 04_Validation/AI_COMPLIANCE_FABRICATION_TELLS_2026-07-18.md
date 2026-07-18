# How to detect Gemini-style fabricated compliance in future documents

## The tell pattern

Gemini's wrong claims follow a consistent pattern: it takes a real framework name (NIST AI RMF, ISO/IEC 42001, Corporations Act s 336, "70/30 rule") and inserts a plausible-sounding obligation that does not exist in the source.

### Common tells

1. **"Must / shall / required to" + named framework + specific action**
   - Example: "must adhere to the 70/30 rule of AI development"
   - Example: "FRIA before production release" placed under NIST AI RMF Manage
   - Example: "corporate auditing compliance is anchored by ASQM 1 ... Under Section 336"

2. **Round-number ratios**
   - 70/30 is suspiciously neat. Real standards rarely use such ratios.

3. **EU concept imported into US framework**
   - FRIA is EU AI Act Article 27. It appears in NIST AI RMF **zero** times.

4. **Statute number used as if it were a duty**
   - s 336 of the Corporations Act gives the AUASB power to make standards; it does not impose ASQM/ASA obligations on a private tool.

5. **Old project fingerprints copied as live state**
   - 3,033 blocks / 52 patterns / no Git — all stale at the time the Gem file was written.

## Concrete detection steps

When reading an AI-generated compliance document:

1. **Ask: which exact clause imposes this?** Demand section/subsection.
2. **Search the cited standard.** Use the official PDF, not a summary.
3. **Check the project fingerprint.** Run `python -m src.verify_chain --print-refs`.
4. **Look for round ratios / neat rules.** Real standards use thresholds, not slogans.
5. **Cross-check dates.** A document created on 2026-07-18 cannot accurately cite a fingerprint from 2026-07-16 unless it is explicitly historical.

## For this specific case

| Wrong claim | Tell | How we verified |
|---|---|---|
| 70/30 rule is binding | Round ratio + "must adhere" | Web search found no authoritative source |
| FRIA under NIST AI RMF | EU concept placed in US framework | NIST AI RMF PDF search for "FRIA" returned zero hits |
| Section 336 anchors ASQM/ASA on tool | Statute misused as duty | AustLII s 336 text: power to make auditing standards |
| 3,033 blocks / v3.9 / 52 patterns | Old fingerprint copied as current | Ran `verify_chain`, checked `phase_4_fingerprints.json` |

## Your reference-only point

Yes: you say what you want and I do not need to justify your intent. But when an external file (Gemini report) makes claims about law, standards, or project state, I will keep verifying those claims against sources because that protects the project from fabricated compliance.
