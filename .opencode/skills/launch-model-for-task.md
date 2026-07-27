---
description: "Use when the operator needs a second model for reasoning, code review, critique, or any task the build agent should not do alone. Covers the full launch-point-review workflow for all Ollama launch surfaces. The agent writes the prompt; the operator launches the model, points it at the file, copies the answer back. Never in the project tree."
---

# Launch Model for Task Skill

The operator has 8 Ollama launch surfaces. Each can run any model. The
build agent (opencode/glm-5.2:cloud) is the only one that seals to the
chain, commits, or edits the project. The others are read-only on the
project — they receive a prompt, do work, return an answer.

## The 8 launch surfaces

| Launch | Command | Where to run it | What it is | Seals? |
|--------|---------|-----------------|------------|--------|
| opencode | `ollama launch opencode` | Project root (the repo) | Build agent — the only one that seals/commits | YES |
| codex | `ollama launch codex` | Anywhere EXCEPT the project tree | Code review, code drafting, critique | NO |
| hermes | `ollama launch hermes` | `C:\Users\justo\AppData\Local\hermes\` | Long research, browser, email adapter | NO |
| claude | `ollama launch claude` | Anywhere EXCEPT the project tree | Reasoning, analysis, writing | NO |
| copilot | `ollama launch copilot` | Anywhere EXCEPT the project tree | Quick tasks, code suggestions | NO |
| pi | `ollama launch pi` | Anywhere | Quick reasoning, sanity checks | NO |
| droid | `ollama launch droid` | Anywhere EXCEPT the project tree | Automation, scripting | NO |
| openclaw | `ollama launch openclaw` | Anywhere EXCEPT the project tree | Legal analysis, document review | NO |

## The CATCH: where to launch

**Some launches MUST be run from a specific directory.** This is the
part that trips people up. Get it wrong and the model either can't find
its config or touches the project tree.

| If the launch needs... | Run it from... | Why |
|------------------------|----------------|-----|
| Project access (build agent) | `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight` | opencode reads `.opencode/` config from the cwd |
| Hermes gateway | `C:\Users\justo\AppData\Local\hermes\` | Hermes config.yaml lives there |
| Code review / critique | `C:\AIDERTESTBOX\` (the sandbox) | Prevents the model from touching the live project |
| Anything else | Anywhere — but NOT the project root | If you launch in the project root, the model can see and edit project files. Don't. |

**The rule:** if it's not the build agent, launch it somewhere that is
NOT the project root. The Aider sandbox (`C:\AIDERTESTBOX`) is the
designated safe location for code review and drafting. For reasoning /
critique / analysis, launch anywhere — desktop, temp folder, wherever.

## The workflow

```
1. Operator asks for a second opinion / review / critique
2. Build agent writes a COMPLETE, self-contained prompt
   (context + question + constraints + format + what not to do)
3. Build agent saves the prompt to a file outside the project:
   C:\AIDERTESTBOX\review_prompt.txt (or Desktop, or anywhere)
4. Operator launches the right model:
   ollama launch codex  (for code review)
   ollama launch claude (for reasoning/critique)
   ollama launch hermes  (for research with browser)
   ollama launch pi      (for quick sanity check)
   ollama launch droid   (for automation/scripting)
   ollama launch openclaw (for legal analysis)
5. Operator sets the model to glm-5.2:cloud (or the best model for the task)
6. Operator points the launched model at the prompt file (reads it)
7. The model outputs its review/answer to the terminal
8. Operator copies the output to a file (e.g. My Project folder — NOT the project tree)
9. Operator tells the build agent where the output file is
10. Build agent reads the output file, evaluates it, decides what to act on
11. Build agent seals + commits (if acting on it). The external model
    never touches the project, never seals, never commits.
```

## Which model for which task

| Task | Best model | Launch | Why |
|------|-----------|--------|-----|
| Code review | `glm-5.2:cloud` | `ollama launch codex` | Code specialist surface, writes in-file |
| Deep reasoning / strategy | `glm-5.2:cloud` | `ollama launch claude` | Reasoning surface, long-form analysis |
| Architecture critique | `glm-5.2:cloud` | `ollama launch claude` | Same — reasoning surface |
| Quick sanity check | `glm-5.2:cloud` | `ollama launch pi` | Fast, lightweight |
| Research with browser | `minimax-m3:cloud` | `ollama launch hermes` | Hermes has browser, email, tool calling |
| Math/formula verification | `glm-5.2:cloud` | `ollama launch codex` | Code surface handles math notation |
| Legal analysis | `glm-5.2:cloud` | `ollama launch openclaw` | Legal document surface |
| Automation/scripting | `glm-5.2:cloud` | `ollama launch droid` | Automation surface |
| Flaw finding | `glm-5.2:cloud` | `ollama launch claude` | Reasoning surface, catches more |

**Default model:** `glm-5.2:cloud` for everything except Hermes research
(which uses `minimax-m3:cloud`). The operator can change the model on
any launch with `/model` inside the tool. The model doesn't have to
match the launch surface — you can run glm-5.2 inside codex, claude,
pi, or any of them. The launch surface determines the UI/tools; the
model determines the reasoning.

## What the prompt file must contain

When the build agent writes a prompt for an external model, the file
must be complete and self-contained (the external model has zero
context):

1. **Context** — what OGIR is (one paragraph), current state, what
   decision is being made
2. **The question** — exactly what to analyze/critique/review
3. **Constraints** — determinism, no network, 00-99 boundary, canonical
   JSON, chain seal rules (if relevant to the review)
4. **Format** — how to format the answer (bullet points, numbered list,
   code diff, yes/no with reasoning, etc.)
5. **What NOT to do** — do not write code into the project, do not seal,
   do not commit, do not assume context not provided

Save the prompt to: `C:\AIDERTESTBOX\review_prompt.txt` (or Desktop)

## Code reviews (mandatory)

Before sealing any non-trivial code change (new function, new test,
engine modification, config change), the build agent MUST:

1. Write a code review prompt with the full diff + conventions
2. Save it to `C:\AIDERTESTBOX\review_prompt.txt`
3. Tell the operator: "Launch codex, point at C:\AIDERTESTBOX\review_prompt.txt, copy the answer back."
4. Wait for the answer
5. Do not seal until the review comes back CLEAN or every issue is addressed

## The operator's only actions

The operator does 3 things:
1. **Launch** the model (`ollama launch codex` / `claude` / `pi` / etc.)
2. **Point** it at the prompt file
3. **Copy** the answer back

The build agent does everything else: writes the prompt, reads the
answer, evaluates it, decides, seals, commits.

## What never happens

- The external model never touches the project tree
- The external model never seals to the chain
- The external model never commits to git
- The external model never edits project source
- The build agent never blindly trusts the external model's answer —
  it evaluates it against project constraints first

## Practice run

To test this workflow:
1. Build agent writes a small test prompt (e.g., "Review this function
   for bugs: [simple function]")
2. Save to `C:\AIDERTESTBOX\practice_prompt.txt`
3. Operator launches `ollama launch codex`, sets model to glm-5.2:cloud
4. Points codex at the practice prompt file
5. Codex writes its review in the file
6. Operator copies the review back
7. Build agent reads it and confirms the workflow works

If the practice run succeeds, the workflow is gold. If it fails, the
catch is usually the launch location — check the table above.