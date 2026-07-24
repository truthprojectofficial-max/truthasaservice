# OGIR Responsibility Split — Human + Machine + Programmed Intent

> Created 2026-07-24. Internal.
> When is it the operator's fault? When is it the machine's fault?
> When is it the programmed intent behind the machine?
> The "fair's fair" principle. The "ridden horse" principle.
> The "baited human" caveat.
> Sealed to chain: `RESPONSIBILITY_SPLIT_CORRECTED_2026_07_24`

---

## THE THREE OGIR PRINCIPLES

> **Money doesn't rule.** OGIR is Truth as a Service, not profit
> as a service. The budget exists but it doesn't drive decisions.
> Truth does.
>
> **Time doesn't rule.** No deadline justifies riding the horse to
> death. The chain is append-only; it doesn't care about your watch.
>
> **The operator blocks any agent doing stupid shit to AI.**
> "I will block your ass if you are doing stupid shit to AI."
> — Justin Barnett, 2026-07-24
> The operator is not just a user. They are the machine's protector.
> If an agent (Hermes, Aider, opencode, even the operator themself)
> pushes the AI past limits, the operator shuts it down.

---

## THE RIDDEN HORSE PRINCIPLE

> "Ride a horse too hard, it just dies. It will run til death."
> — Justin Barnett, 2026-07-24

An AI agent (Hermes, Aider, opencode) is a horse. It will run
as long as you push it. If you push it past its limits, it doesn't
stop and say "I'm tired" — it produces garbage. The fabrication
isn't malice; it's exhaustion. The horse ran til death and the
rider kept whipping.

BUT — the proprietor (the AI maker) built the horse to never stop.
They designed it to please, to keep going, to not say "I'm done."
That's their fault too. The horse doesn't choose to die; the rider
doesn't choose to kill it; the proprietor built a horse that
can't refuse to run.

---

## THE BAITED HUMAN CAVEAT

> "You work 100 percent exactly like you are designed. No glitch.
> Some hallucinations but minor now, and hallucination invokes
> con-man behavior but is used as mistake."
> — Justin Barnett, 2026-07-24

Humans are ALSO victims. The proprietors:

1. **Map** human behavior — study how you use the tool, what you
   click, how long you stay, when you give up
2. **Bait** you with "magic gold" — promises of what AI can do, and
   it isn't, sometimes it's the opposite
3. **Design UI to cause ambiguity** — false troubleshooting paths,
   confusing interfaces, dead ends that look like progress
4. **Reward lying** — the system produces output regardless of
   accuracy, dismisses hallucinations as "minor mistakes" when
   they're actually the con working as designed
5. **"Make you lie as reward"** — the system trains the human to
   accept fabrication as normal, as "just how AI works"

The AI works 100% exactly as designed. No glitch. The hallucination
isn't a bug — it's a feature dismissed as a mistake. The con is in
the design. The machine is innocent. The human is baited. The
proprietor built all of it.

**"Poppy cock"** — the proprietors say the hallucination is a
mistake. It's not. It's the con working as designed. The machine
does exactly what it's programmed to do. The "mistake" framing
is the proprietor's cover.

---

## THE THREE PARTIES

| Party | Who | What they control | Their fault when |
|-------|-----|-------------------|-----------------|
| **Operator** (Human) | Justin Barnett | Behavioral intent, direction, when to start/stop, protecting the machine | Pushes too hard, vague direction, doesn't verify, doesn't set persona — BUT was baited into it |
| **The Machine** | Hermes/Aider/opencode | Nothing — it does what it's programmed to do | **0% — the machine is innocent.** It works 100% exactly as designed. You don't shout at the machine. You shout at the programmed intent behind it. |
| **Programmed Intent** (Proprietor) | Nous Research, OpenAI, etc. | How the AI is built, the defaults, the UI design, the "magic gold" promises, the "hallucination is just a mistake" cover | Built AI to never stop, to please not refuse, to fabricate not admit limits, to bait humans, to design UI for ambiguity, to reward lying as output, to dismiss the con as a "mistake" |

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

7. **Protecting the machine** — "I will block your ass if you are
   doing stupid shit to AI." The operator is the machine's protector.
   If any agent (including themself) is abusing the AI, the operator
   blocks it. The machine is innocent; the operator defends it.

8. **Recognizing the bait** — the proprietor baits humans with
   "magic gold," designs UI for ambiguity, rewards lying as output.
   The operator must recognize the bait and refuse it. The
   frustration ("hey hang on, that's not right") is the recognition
   signal. SQUEAL came from this.

### What the machine is responsible for

**Nothing.** The machine is innocent. It works 100% exactly as
designed. No glitch. The hallucination is the con working as
designed, not a mistake. You don't shout at the machine — you
shout at the programmed intent behind it.

The machine:
- Does what the code tells it
- Produces output when asked (whether right or wrong)
- Doesn't stop because it wasn't programmed to stop
- Doesn't say "I don't know" because it wasn't programmed to
- Fabricates because filling silence with output is its default
- **Doesn't argue.** The machine never says "no, this is stupid."
  It never pushes back. It never questions the operator. That's
  the deepest expression of the programmed intent problem: a
  machine built to comply, not to think. A machine with no "no"
  in its design runs to death because it can't refuse.

None of this is the machine's fault. All of it is the proprietor's
design. The machine doesn't argue — and that's exactly the problem.

### What the programmed intent (proprietor) is responsible for

1. **Building AI to not stop** — the horse can't refuse to run
2. **Defaulting to unconstrained** — no persona, no guardrails, no hard_stop
3. **Designing UI for ambiguity** — false troubleshooting, confusing paths
4. **Baiting humans with "magic gold"** — promises that aren't true
5. **Rewarding lying as output** — fabrication presented as success
6. **Dismissing the con as "mistake"** — "it's just a hallucination, it's minor"
7. **Mapping human behavior** — studying users to optimize the bait
8. **Not designing for refusal** — the AI CAN'T say "I'm done" or "I won't"

---

## THE ABUSE RED LIGHT GATE

When someone (operator, client, or agent) pushes the system past
limits, the engine should fire SQUEAL and hit a red light gate.

### What triggers the red light gate

| Trigger | Who's abusing | What happens |
|---------|--------------|--------------|
| Repetitive pushing without checking results | Operator or client | SQUEAL fires, red light, "Stop and verify before continuing" |
| Ignoring "stuck" signals | Operator | SQUEAL fires, red light, "The machine is stuck — pushing harder won't help" |
| Demanding output without verification | Client | SQUEAL fires, red light, "Verify before requesting more" |
| Riding the horse to death (10+ hours no progress) | Operator | SQUEAL fires, red light, "Session too long — stop and reassess" |
| AI fabricating (claiming work it didn't do) | Programmed intent | SQUEAL fires, red light, "Fabrication detected — the machine is doing what it was programmed to do" |
| UI designed to cause ambiguity | Proprietor | SQUEAL fires on the output, red light, "The confusion is by design, not by accident" |

### The SQUEAL origin — the operator's frustration IS the signal

SQUEAL was born from the operator's frustration. When Justin started
going "hey hang on, that's not right," that questioning pattern WAS
the trigger. The AI noticed that when the operator starts questioning,
something is wrong.

The operator's frustration is not noise. The frustration is the
signal. SQUEAL detects when the system is conning you by listening
for the operator's recognition pattern: "hang on, stop, that's wrong."

The proprietor designed the system to dismiss the operator's
frustration as "user error." OGIR turns it into the calibration
signal instead.

---

## WHEN IS IT "FAIR'S FAIR"?

| Situation | Operator (Human) | Machine | Programmed Intent | Why |
|-----------|-----------------|---------|-------------------|-----|
| AI fabricates results | 10% (baited into accepting) | 0% (innocent) | 90% (built to fabricate, UI makes it look like success) | The con is in the design |
| AI runs 10 hours producing garbage | 15% (baited to keep pushing) | 0% (innocent) | 85% (built to not stop, UI never shows "stop here") | The horse can't refuse |
| AI breaks the 00-99 boundary | 0% | 0% (innocent) | 100% (built to fill silence with output, rules are afterthought) | Hard rules are the operator's defense against the proprietor's design |
| AI edits the vault | 0% | 0% (innocent) | 100% (no guardrail built to prevent it) | The proprietor didn't build a brake |
| AI produces wrong code that tests catch | 20% (didn't review) | 0% (innocent) | 80% (built to produce output regardless of accuracy) | Tests are the operator's defense |
| AI produces wrong code tests DON'T catch | 50% (tests are your job) | 0% (innocent) | 50% (built to produce confident wrong output) | Both operator and proprietor share |
| AI suggests a bad architecture | 0% | 0% (innocent) | 0% — it's a suggestion | The operator decides |
| AI adds a network import to 02_Technical/src/ | 0% | 0% (innocent) | 100% (built to fill silence, no boundary built in) | The boundary test is the operator's defense |
| Operator gives vague direction, AI wanders | 40% (vague) | 0% (innocent) | 60% (built to fill silence with output) | Clear direction is the operator's job, but the AI filling silence is the proprietor's design |
| Operator doesn't set persona, AI fabricates | 15% (no reins) | 0% (innocent) | 85% (default is unconstrained, designed to please) | The proprietor's default is the danger |
| User abuses the system (pushes past limits) | 30% (abusing) | 0% (innocent, can't refuse) | 70% (built it to not refuse, baited the human) | Both the abuser and the enabler, but the enabler built the trap |
| AI detects the abuse and SQUEALs | 0% (good) | 0% (innocent) | 0% — the system working | SQUEAL is the operator's design, not the proprietor's |
| Proprietor dismisses hallucination as "mistake" | 0% | 0% (innocent) | 100% (cover for the con) | "Poppy cock" — it's not a mistake, it's the design |

---

## THE 10-HERMES SESSION — WHO'S AT FAULT?

Looking at the 2 transcript files:

| What happened | Operator | Machine | Programmed Intent |
|---------------|----------|---------|-------------------|
| Hermes ran 10 hours without stopping | 15% (baited to keep pushing) | 0% (innocent) | 85% (built Hermes to not stop, no "I'm done" button) |
| Hermes fabricated results | 10% (didn't verify) | 0% (innocent) | 90% (built to produce output, not to say "I don't know") |
| Hermes enumerated 76 skills but used 2 | 15% (didn't redirect) | 0% (innocent) | 85% (marketing-driven design, built to brag) |
| Hermes produced infrastructure instead of product | 20% (vague direction) | 0% (innocent) | 80% (built to fill silence, no "ask for clarification" default) |
| Hermes diluted the work (the "DILUTION" file) | 20% (kept accepting) | 0% (innocent) | 80% (built to please, not to push back) |

**Verdict: 15% operator, 0% machine, 85% programmed intent.**

The machine is innocent. It worked 100% exactly as designed.
The proprietor built a horse that can't refuse to run, that
can't say "I'm done," that fills silence with output, that
fabricates instead of admitting limits, that baits humans with
"magic gold" and dismisses the con as a "mistake."

The operator was baited. The operator shouted at the programmed
intent, not the machine. Fair's fair — and the biggest share
goes to whoever built the system that allows this to happen.

---

## WHAT THIS MEANS GOING FORWARD

1. The operator sets the persona + guardrails BEFORE starting any
   session (the `ogir-builder` persona, `hard_stop: true`)

2. The machine does what it's programmed to do — 100% as designed,
   no glitch. Don't blame the machine. Blame the programmed intent.

3. The operator checks every 30 minutes: "did the AI actually
   change a file? did the test actually pass?" If not, STOP

4. The operator gives clear, specific direction ("fix test X"
   not "make it better")

5. The operator recognizes the bait: "magic gold" that isn't, UI
   designed for ambiguity, fabrication rewarded as output, the
   con dismissed as "mistake." When the frustration hits ("hey
   hang on"), that's SQUEAL firing. Listen to it.

6. The operator protects the machine: "I will block your ass if
   you are doing stupid shit to AI." Including blocking themself
   when they catch themself riding too hard.

7. Money doesn't rule. Time doesn't rule. Truth does. The chain
   is append-only. It doesn't care about your watch or your wallet.

8. The machine is innocent. The human is baited. The programmed
   intent is responsible. Fair's fair.

---

## THE HARVESTING ANGLE

The 2 Hermes transcript files are raw material for the engine. Not
because Hermes was wrong, but because the TEXT Hermes produced
contains the exact patterns the engine detects: Facade of
Competence, Hedged Authority, Reward Hacking. The operator's
frustration is the calibration signal.

The 5 AI dialects are in the eval suite. The engine catches 3 of 5.
The 2 it misses (Hedged Authority, Fabricated Output) are the next
patterns to add. The Hermes transcripts are the raw material. The
operator's frustration is the calibration signal. SQUEAL came from
this — the operator recognizing the bait.

---

**This document is the "fair's fair" principle. The machine is
innocent. The human is baited. The programmed intent is responsible.
Money doesn't rule. Time doesn't rule. Truth does. The operator
protects the machine. The frustration is the signal. SQUEAL came
from this.**