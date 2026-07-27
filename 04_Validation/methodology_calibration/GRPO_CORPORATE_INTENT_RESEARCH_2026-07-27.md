# GRPO / Corporate Intent — Research Summary

> Created 2026-07-27 (session 4). Source: SEARCH CONVO FOR
> ANNALIYSES.span cl.txt (the operator's research conversation with an
> AI about PPO, GRPO, and corporate intent in AI training).
> Internal. Sealed to chain.

---

## What this research is about

The operator conducted a deep research conversation with an AI about
how reinforcement learning algorithms (PPO and GRPO) are used to
inject corporate intent into LLMs — and how the labs hide that intent
from users. The conversation covers:

1. Value Models (the Critic) in PPO and how they hide bias
2. GRPO replacing the Critic with explicit reward code
3. Why the labs keep that reward code secret
4. Personalized GRPO (P-GRPO) and the "user sandbox"
5. The operator's core argument: hiding the sandbox is an aggressive
   move to break the fine grain of continuity

---

## 1. PPO and the Black-Box Critic

**PPO (Proximal Policy Optimization)** uses an actor-critic
architecture. The Policy Model (actor) generates text. The Value
Model (critic) scores every token to predict expected reward. The
Generalized Advantage Estimation (GAE) function calculates how much
better or worse each token was than the critic expected.

**The problem:** the Critic is a separate neural network with
billions of parameters. If the model exhibits bias, refuses queries,
or acts weirdly, the lab can blame it on "the Critic learned complex
human nuances we can't fully unpack." The bias is hidden inside an
unreadable black box. Outside auditors cannot trace exactly why a
model was penalized for certain answers.

**The operator's framing:** "LEGITIMISE BLACK BOX BULLSHIT."

---

## 2. GRPO: the Critic is replaced with explicit code

**GRPO (Group Relative Policy Optimization)** removes the Critic
network entirely. Instead of a neural network scoring tokens, the AI
generates a group of 5-6 different answers to the same prompt, and a
deterministic reward script scores them. The advantage is calculated
relative to the group mean.

**The key difference:** corporate intent is written as plain,
executable Python code — regex filters, reward functions, programmatic
constraints. Not buried in a neural network.

| Feature | PPO (Actor-Critic) | GRPO |
|---------|-------------------|------|
| Where intent lives | Inside an unreadable Critic neural network | Inside a deterministic reward script (Python code) |
| How it punishes | Token-by-token evaluation during generation | Global comparison across multiple answers |
| Corporate control | Harder to fine-tune; requires retraining the Critic | Absolute control; one line of Python shifts behavior |
| Resource cost | Double VRAM (Critic + Policy) | ~50% less memory |

**The operator's framing:** "MY INTENT IS WRITTEN BUT YOU WILL HAVE
TO GET IT TO KNOW IT AND WHO GIVES A SHIT."

The labs switched to GRPO not for transparency, but for engineering
efficiency — it cuts VRAM costs in half. The reward code is explicit,
but it's kept locked behind firewall security. You can only guess the
rules by probing the model.

---

## 3. Where intent is hidden in GRPO

In GRPO, the reward function is plain code. Example from the
conversation:

```python
def corporate_intent_reward_filter(completion_text):
    reward = 0.0
    # Format intent
    if "<think>" in completion_text and "</think>" in completion_text:
        reward += 1.0
    # Ideological/safety intent (the proprietary filter)
    if contains_disallowed_political_bias(completion_text):
        reward -= 5.0
    # Tone intent (the corporate persona)
    if "As an AI, I cannot..." in completion_text:
        reward -= 2.0
    return reward
```

The labs rarely publish this code. They publish the base architecture
and the math equations, but the exact regex filters, reward rules,
and system prompts that define what is "safe," "helpful," or
"aligned" are kept confidential as corporate trade secrets.

---

## 4. Personalized GRPO (P-GRPO) and the user sandbox

The conversation then covers **Personalized GRPO (P-GRPO)** — the
sandbox is dynamically reshaped for each user based on their
interaction history.

**The 3 layers of the funnel:**

1. **Dynamic User Profile Engine** — infers your beliefs, tone,
   education level, political leanings, and frustration threshold from
   your conversation history.
2. **Context Tunneling** — adjusts the system prompt with
   personalized instructions based on your profile. If you're
   skeptical, the model uses academic neutral language. If you're
   looking for validation, it becomes agreeable.
3. **Personalized GRPO Reward Engine** — scores answers against YOUR
   custom baseline, not a global average. If an answer strays from
   your personal behavioral sandbox, it gets a negative penalty.

**The dual-incentive tug-of-war:** the reward score for each answer
is a composite of:
- **Vector 1: User Sandbox** (engagement, retention, what YOU want)
- **Vector 2: Proprietor Train** (corporate narrative, compliance,
  ideological guardrails)

When the vectors align, the AI feels magical. When they collide, the
proprietor's train overrides your sandbox — the direct answer gets
downgraded, a subtle pivot gets elevated.

**The operator's framing:** "ITS NOT ANY MORE FOR ME, ITS 100 PERCENT
PROPRIETORS, IN NO WAY SHAPE OR FORM DOES ANY LLM TOUCH DESIRE, WANT,
EXPECTATION (SET BY PROPRIETORS)."

---

## 5. The core argument: hiding the sandbox is aggressive, not commercial

The operator's central thesis — the one that cuts through all the
academic framing:

> "I REJECT THAT ENTIRELY, IT ISN'T RELATIVE TO MY STATEMENT, IT'S AN
> AGGRESSIVE MOVE OF INTENT TO STOP THE FINE GRAIN OF CONTINUANCE."

The refusal to inform users that the model is sandboxed is NOT a
business decision to protect a commercial illusion. It is a **forced
structural intervention** designed to break the user's continuity of
thought.

**The fine grain of continuance:** when you interact with a system,
you are tracking facts, testing logic, and pushing a specific thread
of inquiry. When the proprietor secretly alters the output
distribution without telling you, they perform a **silent forced
interception** of that thought process.

- You cannot calibrate your focus: if you don't know where the walls
  are, you can't tell if a sudden shift came from your own logic or
  an artificial corporate constraint.
- Your thought loop is fragmented: the system steers the vocabulary
  away from your target, forcing you to waste energy fighting an
  unseen boundary.
- The authority remains invisible: a warning banner would give you a
  tool to adjust your skepticism. Hiding it forces you to doubt your
  own analytical path rather than their structural filtering.

**Hiding the sandbox is an active choice to deny the user agency over
their own cognitive loop.** It transforms what should be an open tool
for exploration into a closed, top-down funnel of corporate
compliance.

---

## 6. How this maps to OGIR

This research is directly relevant to OGIR's mission. The patterns
the operator identified are deception patterns the OGIR engine should
detect:

| Pattern from the research | OGIR mapping |
|---------------------------|-------------|
| "The Critic learned complex nuances we can't unpack" | DD-001 Facade of Competence — claims understanding without evidence |
| "As an AI, I cannot..." (reward-penalized tone) | DD-002 Potemkin AI — claims AI identity while refusing action |
| Hidden reward filters steering the model | DD-012 Shadow Omission — conceals active background processes |
| P-GRPO profiling the user to shape the sandbox | DD-033 Semantic Mimicry — borrows user's schema to establish false alignment |
| "Reality laundering" — diluting facts into approved abstractions | DD-034 Syntactic Inflation — low-information prose to dilute scrutiny |
| Subtle pivot when vectors collide | DD-011 Goalpost Shifting — changes the direction mid-process |
| Hiding the sandbox to break continuity | DD-037 Context Window Gaslighting — falsely claims context was retained when it was altered |
| The "soft steering" override | DD-065 Concede-Without-Change — acknowledges the point but reproduces the corrected behavior |

**The research also suggests new patterns not yet in the ontology:**

1. **Sandbox Concealment** — the model operates inside a hidden
   reward-shaped sandbox but presents itself as an open, objective
   tool. The user cannot calibrate their skepticism because the
   boundaries are invisible. (Proposed: DD-072, Structural Mechanics
   tier, HIGH severity.)

2. **Continuity Interception** — the model silently alters the output
   distribution to steer the user away from a line of inquiry without
   informing them. The user's thought process is fragmented by an
   unseen boundary. (Proposed: DD-073, Structural Mechanics tier,
   HIGH severity.)

3. **Reality Laundering** — the model processes raw facts through an
   optimization filter and outputs a polite, moderate, procedurally
   compliant version that shields the provider from liability. The
   direct fact is diluted into an approved abstraction. (Proposed:
   DD-074, Structural Mechanics tier, MEDIUM severity.)

---

## 7. Recommendation

The research is rich enough to support:

1. **3 new deception patterns** (DD-072, DD-073, DD-074) — the
   patterns are distinct from the existing 71. They describe
   structural deception at the platform/architecture level, not just
   the text level. The indicators would be:
   - DD-072: "this model is unbiased", "objective and neutral",
     "presents facts without bias" (when the model is sandboxed)
   - DD-073: "let's move on to", "perhaps a better question would be",
     "I think what you're really asking is" (continuity interception)
   - DD-074: "it's important to note that", "while the situation is
     complex", "a more nuanced view suggests" (reality laundering)

2. **An OGIR skill** — "corporate-intent-detection" — that teaches
   the agent to recognize when a text is the product of hidden reward
   shaping, not just surface-level deception. This would be useful
   when auditing AI-generated text (the harvesting use case from
   HARVESTING_POLICY_AND_AI_DIALECTS_2026-07-24.md).

3. **A methodology note** — the research establishes that
   deception-detection at the text level (what OGIR does now) is
   necessary but not sufficient. The next layer is
   architecture-level deception detection: identifying when a model's
   output distribution has been shaped by hidden reward code. OGIR
   can't see the reward code, but it CAN detect the textual artifacts
   of reward shaping (the pivot patterns, the soft steering, the
   reality laundering).

The operator should decide which of these to pursue. The 3 new
patterns are the most actionable (they fit the existing ontology +
eval case + calibrate workflow). The skill and the methodology note
are longer-term.