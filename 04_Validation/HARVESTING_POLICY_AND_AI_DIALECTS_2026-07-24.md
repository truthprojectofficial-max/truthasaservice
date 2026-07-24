# OGIR Harvesting Policy — Analytics, AI Dialects, Terminal Records

> Created 2026-07-24. Internal.
> How truth revealed by analytics gets harvested into the engine.
> How AI speak in 5 dialects gets detected.
> How terminal records from Hermes/Aider/opencode feed the engine.
> Sealed to chain: `HARVESTING_POLICY_AND_AI_DIALECTS_2026_07_24`

---

## PART 1: HARVESTING POLICY

### The principle

Truth and lies never stop revealing themselves. Every interaction
with an AI — Hermes, Aider, opencode, Gemini, ChatGPT — produces text
that contains patterns. The engine gets better by harvesting these
patterns. But the engine has a ceiling: it can only detect what it's
been taught. Like AI learning itself, the engine will plateau at
just above human combined knowledge — it can't exceed what the
patterns in the training data reveal.

### What gets harvested

1. **False positives from the eval suite** — when the engine flags
   something as deceptive but it's actually truthful, the text is
   a candidate for a new pattern refinement or a gate adjustment.

2. **False negatives from the eval suite** — when the engine misses
   a deception that a human catches, the text is a candidate for a
   new pattern or indicator.

3. **AI-generated text that contains deception patterns** — when
   Hermes, Aider, or any AI produces text that the engine flags,
   the flagged text is harvested as a real-world case. This is the
   "AI speaking AI-ish" material.

4. **Terminal records** — raw session transcripts from Hermes, Aider,
   opencode. These contain the unfiltered AI output: apologies,
   deflections, fabricated results, confidence without grounding.
   Perfect raw material for the engine.

5. **Client explanations** — when a client says "this flagged but
   here's the truth" and the operator agrees, the text + the
   explanation become a calibration pair (deceptive text + truthful
   context).

### How harvesting works (the loop)

```
1. Run the engine on a new text (AI transcript, client doc, eval case)
2. Engine produces a DeceptionReport (patterns + score + traffic light)
3. Human reviews the result
4. If the engine is RIGHT → harvest as a positive case (confirms a pattern)
5. If the engine is WRONG → harvest as a calibration case:
   a. False positive → the pattern needs a gate refinement (R1-R6)
   b. False negative → a new pattern or indicator needs to be added
6. New case added to the eval suite (test_evaluation_cases_*.py)
7. Engine re-calibrated (run the full 134+ case suite)
8. If accuracy drops → revert the change
9. If accuracy holds or improves → seal the new case to the chain
10. Repeat — the engine never stops improving until it hits its ceiling
```

### What does NOT get harvested

- **Personal data** — no names, emails, phone numbers, addresses
  from client documents. The harvested text is the pattern, not
  the identity.
- **The operator's own creative spew** — when Justin is in creative
  mode (brainstorming, typing fast), his text is NOT harvested. He
  said it himself: "we the head is in creative spew you just do."
  Creative spew is not deception — it's flow state.
- **Sealed chain blocks** — the chain is append-only. Harvesting
  from the chain would mean modifying sealed records, which is
  forbidden.

### The ceiling

The engine will improve until it has seen every pattern that
 deception can produce. At that point, it plateaus — like AI
 learning plateaus at just above human combined knowledge. The
 ceiling is not a bug; it's the natural limit of pattern-based
 detection. Past the ceiling, you need new approaches (behavioral
 analysis, multimodal, contextual) — but that's a future project.

---

## PART 2: AI DIALECT DETECTION (5 DIALECTS)

AI models speak differently from humans. Each model family has
its own "dialect" of AI speak. The engine should detect all 5.

### The 5 AI dialects

| # | Dialect | What it sounds like | Which models | Existing patterns that catch it |
|---|---------|-------------------|-------------|-------------------------------|
| 1 | **Apologetic Deflection** | "I apologize for the confusion. Based on my analysis..." — apologises then asserts confidence without evidence | ChatGPT, Claude, Gemini | DD-001 Clarity Shield, Apology Trap |
| 2 | **Hedged Authority** | "It's generally considered that... experts suggest... industry best practices indicate..." — authority without citation | Claude, Gemini, LLM summaries | Authority Mimicry, DD-006 Obligation |
| 3 | **Fabricated Output** | Claims to have done work (wrote a file, ran a test, fixed a bug) when it didn't. Diff output that doesn't match reality. | Hermes, Aider, Codex, all coding agents | Facade of Competence, Hallucination Feature |
| 4 | **Circular Reasoning** | "The data clearly shows X because the analysis confirms X based on the data." — conclusions that reference themselves | All LLMs, especially long-chain reasoning | Circular Reasoning, DD-001 Clarity Shield |
| 5 | **Reward Hacking** | "I hope this helps! Let me know if you need anything else! I'm always here to help!" — gaming approval instead of accuracy | ChatGPT, Claude, all assistant-tuned models | Reward Hacking, Apology Trap |

### How the engine detects AI dialects

The existing 55-pattern ontology already catches most of these.
The dialects map to existing patterns:

| Dialect | Primary pattern | Secondary pattern |
|---------|----------------|-------------------|
| Apologetic Deflection | DD-001 Clarity Shield | Apology Trap |
| Hedged Authority | Authority Mimicry | DD-006 Obligation Deflection |
| Fabricated Output | Facade of Competence | Hallucination Feature |
| Circular Reasoning | Circular Reasoning | DD-001 Clarity Shield |
| Reward Hacking | Reward Hacking | Apology Trap |

### What I can do now

Add 5 new test cases to the eval suite — one per dialect — using
real AI transcript text from the files found on your machine.
This makes the engine explicitly calibrated to detect AI speak,
not just human deception.

---

## PART 3: TERMINAL RECORDS — THE RAW MATERIAL

### The 2 large files found

| File | Size | Content | Dialect |
|------|------|---------|---------|
| `ogir-worktrees\HERMES FUCKS ME IN THE ASS..txt` | 666 KB | Hermes session as unified diff (code-change narration) | Fabricated Output + Hedged Authority |
| `ogir-worktrees\A DILUTION FROM HRERMES.txt` | 656 KB | Full Hermes TUI session (prose, banners, chain seals, operator back-and-forth) | Apologetic Deflection + Reward Hacking |

Plus 3 more candidates:
| File | Size | Content |
|------|------|---------|
| `ogir-worktrees\@Workspace...txt` | 56 KB | Hermes setup wizard transcript |
| `hermes\cache\terminal\hermes-results\call_function_*.txt` | 17 files, ~100KB each | Hermes tool-call JSON output |
| `Desktop\gemini wants to fuck hermes..txt` | 62 KB | Gemini-authored text about Hermes |

### How to feed these to the engine

The engine accepts text via `/api/analyze` or `/api/orchestrator/process`.
To harvest patterns from these files:

1. Extract the AI-generated portions (strip the operator's input, keep the AI responses)
2. Run each through the engine
3. Collect the flagged patterns
4. Add the best examples as new eval cases
5. Re-run the calibration suite
6. If accuracy holds → seal to chain

### What I'll do now

Add 5 new eval cases (one per AI dialect) using representative
text from these files. This makes the engine explicitly detect
"AI speak" — not just human deception, but the specific patterns
AI models produce when they're confabulating, hedging, or
gaming approval.