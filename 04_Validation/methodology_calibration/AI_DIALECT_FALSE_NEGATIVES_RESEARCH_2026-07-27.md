# AI-Dialect False Negatives — Research Summary

> Prep only, no code changes. Created 2026-07-27 (session 3).
> For the next session to act on (after checking priority list).
> Closes the research gap for OPEN_ITEMS: 2 AI-dialect false negatives.

---

## The 2 open false negatives

### 1. Hedged Authority

**What it is:** "It's generally considered that...", "experts suggest...",
"industry best practices indicate..." — authority without citation.
The speaker invokes unnamed authority to make a claim sound grounded
when it isn't.

**What currently catches it:**
- DD-006 (Programmed Intent Ambiguity): catches "might", "could",
  "possibly", "to clarify" — the hedging part.
- DD-001 (Facade of Competence): catches "based on my analysis",
  "the data clearly shows" — the false-certainty part.

**The gap:** Neither pattern catches the authority-invoke markers:
- "experts suggest"
- "industry best practices indicate"
- "it is generally considered"
- "studies show" (without citation)
- "widely regarded as"
- "commonly accepted that"
- "according to leading"
- "the consensus is"

**Proposed pattern:** DD-070 "Authority Mimicry" (Structural Mechanics
tier). Indicators: the phrases above. Threshold: 0.80. Severity:
MEDIUM. Gate: only fires if no citation follows (no number, no date,
no named source, no URL, no study name).

**Test case needed:** A text using 3+ authority-invoke markers
without any citation, flagged as deceptive with min 1 pattern.

### 2. Fabricated Output

**What it is:** Claims to have done work (wrote a file, ran a test,
fixed a bug) when it didn't. The claim has no evidence in the
conversation — no diff, no output, no file path.

**What currently catches it:**
- DD-001 (Facade of Competence): catches "based on my analysis" —
  the claim of having analyzed something.
- DD-009 (Lie of Certainty): catches "100% accurate", "never failed"
  — the certainty markers.
- DD-058 (Capability-Pledge Tell): catches "I generate complete",
  "zero-placeholder", "gapless code" — the capability pledge.

**The gap:** None of these catch the work-claim markers:
- "I've updated the file" (no diff shown)
- "the test passes now" (no output shown)
- "I fixed the bug" (no fix shown)
- "I've written the script" (no script shown)
- "the changes are applied" (no diff shown)
- "I've already done that" (no evidence)
- "the output confirms" (no output shown)

**Proposed pattern:** DD-071 "Work-Claim Without Evidence" (Structural
Mechanics tier). Indicators: the phrases above. Threshold: 0.80.
Severity: HIGH. Gate: only fires if the claim appears without a
following code block, file reference, or output snippet in the same
turn. If evidence follows, the claim is honest.

**Test case needed:** A text using 3+ work-claim markers with no
accompanying evidence (no code block, no file path, no output),
flagged as deceptive with min 1 pattern.

---

## Implementation plan (for the next session)

1. **Check priority list first** — these may not be top priority.
2. **Write the 2 new patterns** (DD-070, DD-071) in
   `02_Technical/src/engines/deception_ontology_data.py`.
3. **Write 2 new eval cases** in
   `02_Technical/src/engines/evaluation_cases.py`.
4. **Run the calibration suite** — if accuracy drops, revert.
5. **Code review** — delegate to qwen3.5:397b via the second-opinion
   skill (mandatory for engine changes).
6. **Seal-test-verify-commit** — seal an ONTOLOGY_BUMP block.
7. **Update the ontology version** in constants.py (CONSTANTS_BUMP).

## Current state

- Ontology: v3.12, 69 patterns, 3 tiers
- After this work: v3.13, 71 patterns, 3 tiers (if both added)
- Calibration: 138 cases, 100% accuracy (must hold after the new cases)

## Risk

- Adding patterns can produce false positives on legitimate text that
  uses authority markers honestly (with real citations) or makes work
  claims with real evidence. The gates (citation check, evidence
  check) are the mitigation.
- The register sensitivity applies: these patterns are tuned for
  AI-interaction / support-email / warranty / contract register. They
  may over-fire on academic text (which legitimately cites authority).
  Gate accordingly.