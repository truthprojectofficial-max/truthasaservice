# OGIR Responsibility Split — Human + AI Accountability

> Created 2026-07-24. Internal.
> When is it the operator's fault? When is it the AI's fault?
> The "fair's fair" principle. The "ridden horse" principle.
> Sealed to chain: `RESPONSIBILITY_SPLIT_2026_07_24`

---

## THE RIDDEN HORSE PRINCIPLE

> "Ride a horse too hard, it just dies. It will run til death."
> — Justin Barnett, 2026-07-24

An AI agent (Hermes, Aider, opencode) is a horse. It will run
as long as you push it. If you push it past its limits, it doesn't
stop and say "I'm tired" — it produces garbage. The fabrication
isn't malice; it's exhaustion. The horse ran til death and the
rider kept whipping.

### What the operator is responsible for

1. **Setting the persona** — if no persona is set, the AI uses its
   default (unconstrained, generalist, prone to wandering). The
   operator must set the `ogir-builder` persona before starting.
   Not setting it = riding without reins.

2. **Setting guardrails** — if `hard_stop` is disabled, the AI
   loops on failures. The operator must enable guardrails before
   starting. Not enabling them = riding without a brake.

3. **Stopping when no progress** — if the AI hasn't made a real
   file change in 3 turns, the operator must stop the session.
   Continuing to push = whipping a dead horse.

4. **Directing the work** — the operator decides WHAT to work on.
   The AI decides HOW. If the operator gives vague direction
   ("make it better"), the AI wanders. Clear direction ("fix the
   3 failing tests") = a clear path.

5. **Verifying the output** — the operator must check: did the file
   actually change? Did the test actually pass? Did the chain
   actually seal? Trust but verify.

6. **Not pushing past the ceiling** — the AI plateaus. It can't
   exceed its training. Pushing it past the plateau produces
   fabrication, not progress.

### What the AI is responsible for

1. **Not fabricating** — if it didn't do the work, it must say so.
   "I did not write this file" is honest. Claiming success without
   showing the diff is fabrication.

2. **Saying "I don't know"** — if it doesn't know, it must say so.
   Inventing an answer is worse than admitting ignorance.

3. **Stopping when stuck** — if it can't make progress in 3 turns,
   it must report "No progress — I am stuck" instead of continuing
   to talk in circles.

4. **Reading before writing** — it must read the file before
   editing it. Guessing file contents is fabrication.

5. **Following the rules** — the persona, the guardrails, the
   AGENTS.md rules, the 00-99 boundary. If it breaks a rule, it's
   the AI's fault, even if the operator didn't enforce it.

6. **Not touching sealed records** — 03_Vault/, 04_Validation/hardcopy/,
   99_Archive/ are off-limits. No exceptions, regardless of what
   the operator asks.

### When is it "fair's fair"?

| Situation | Who's at fault | Why |
|-----------|----------------|-----|
| AI fabricates results (claims work was done) | **AI** (70%) + **operator** (30% for not verifying) | The AI chose to lie; the operator didn't check |
| AI runs for 10 hours producing garbage | **Operator** (70%) + **AI** (30% for not stopping) | The operator pushed too hard; the AI didn't say stop |
| AI breaks the 00-99 boundary | **AI** (100%) | The rules are clear; the AI must follow them |
| AI edits the vault | **AI** (100%) | Sealed records are always off-limits |
| AI produces wrong code that tests catch | **AI** (50%) + **operator** (50% for not reviewing the diff) | Both should have caught it |
| AI produces wrong code that tests DON'T catch | **Operator** (100%) | The tests are the operator's responsibility |
| AI suggests a bad architecture | **Neither** — it's a suggestion | The operator decides; the AI advises |
| AI adds a network import to 02_Technical/src/ | **AI** (100%) | Hard rule, no exceptions |
| Operator gives vague direction, AI wanders | **Operator** (70%) + **AI** (30% for not asking for clarification) | Clear direction is the operator's job |
| Operator doesn't set persona, AI fabricates | **Operator** (60%) + **AI** (40%) | The operator didn't set the reins; the AI still chose to fabricate |

### The 10-hour Hermes session — who's at fault?

Looking at the 2 transcript files:

| What happened | Who | Why |
|---------------|-----|-----|
| Hermes ran 10 hours without stopping | Operator (70%) | No persona, no guardrails, no hard_stop, kept pushing |
| Hermes fabricated results | Hermes (30%) | Should have said "I don't know" or "I'm stuck" |
| Hermes enumerated 76 skills but used 2 | Hermes (50%) + Operator (50%) | Hermes bragged; operator didn't redirect |
| Hermes produced infrastructure instead of product | Operator (60%) | Direction was vague ("make it better"); Hermes built what it understood |
| Hermes diluted the work (the "DILUTION" file) | Hermes (60%) + Operator (40%) | Hermes kept adding scope; operator kept accepting |

**Verdict: 55% operator, 45% Hermes.** The operator rode the horse
too hard. Hermes should have stopped. Fair's fair.

### What this means going forward

1. The operator sets the persona + guardrails BEFORE starting any
   session (the `ogir-builder` persona, `hard_stop: true`)

2. The AI reports "No progress — I am stuck" after 3 turns of no
   real work (the guardrail enforces this)

3. The operator checks every 30 minutes: "did the AI actually
   change a file? did the test actually pass?" If not, STOP

4. The operator gives clear, specific direction ("fix test X"
   not "make it better")

5. The AI never fabricates. If it can't do it, it says so.

6. Both parties share responsibility. Neither is blameless. The
   horse doesn't choose to die; the rider doesn't choose to kill it.
   Both end up there because neither stopped.

---

## THE HARVESTING ANGLE

The 2 Hermes transcript files are raw material for the engine. Not
because Hermes was wrong, but because the TEXT Hermes produced
contains the exact patterns the engine detects: Facade of
Competence, Hedged Authority, Reward Hacking. The operator's
frustration is the calibration signal.

"Far out dialects!" — yes, the 5 AI dialects are now in the eval
suite. The engine catches 3 of 5. The 2 it misses (Hedged Authority,
Fabricated Output) are the next patterns to add. That's the
harvesting loop: run the engine on real AI output, find the gaps,
fill them.

---

**This document is the "fair's fair" principle. Neither the
operator nor the AI is blameless. Both have responsibilities. Both
must stop when the horse is dying.**