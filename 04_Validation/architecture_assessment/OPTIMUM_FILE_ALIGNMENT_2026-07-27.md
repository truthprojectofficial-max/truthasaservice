# Optimum File Alignment — OGIR vs the AI's Recommendations

> Date: 2026-07-27
> Author: opencode build agent (ollama/glm-5.2:cloud)
> Source: `TO HAVE AN OPTIMUM AGENT USEING OLL.txt` (the operator's prompt +
>   an AI's response) reviewed against the SECOND_OPINION_PROMPT 7 questions.
> Status: Sealed to chain. No code changed.

## Purpose

The last session (5b, HARD GATE) flagged that the prior agent deflected from
this exact task. This document performs the alignment the operator asked for:
take the AI's 13 recommendations from the optimum file, map each one against
OGIR's actual flows, and report what is covered, what is missing, what is
genuinely new, and what was over-prescribed.

OGIR is NOT a concept paper. As of this session it is a 41,077-block Merkle
chain, 411 passing tests, 71 deception patterns, a live Supabase backend (8
tables, 23 RLS policies), a deployed Cloudflare Worker, a Tauri v2 desktop
binary, 25 opencode skills, 3 MCP servers, and a pure-stdlib Python runtime.
The AI did not know this; its response was written as if OGIR were greenfield.

## The 7 questions (answered directly)

### 1. What did the AI get RIGHT?

Three things, all already built:

- **Deterministic deception detection is the strongest idea.** Correct.
  OGIR already ships this: 71 patterns (DD-001-DD-071) across 3 tiers
  (dialects + structural mechanics + linguistic markers + AI-dialect
  DD-070/071), with a 138-case calibration at 100% accuracy, 0 FP, 0 FN.
  The AI's "DD001 source missing -> reject" example is literally DD-001
  through DD-030 already in the ontology.
- **Truth Ledger / SHA-256 Merkle tree.** Correct concept. OGIR has it:
  a 41,077-block append-only SHA-256 chain with a re-derivable root, a
  NIZK proof per block, and a hard-copy paper anchor refreshed quarterly.
  Every state change is sealed via `vault_io.append_block`.
- **Separation of governance from execution.** Correct. OGIR enforces this
  with the 00-99 spatial boundary (`tests/test_00_99_boundary.py`):
  Strategy / Methodology / Technical / Vault / Validation are isolated,
  and code in 02_Technical cannot import from 03_Vault or 04_Validation.

### 2. What did the AI get WRONG — recommended building things OGIR already has?

Eight of its 13 sections are redundant. Point by point:

| AI recommendation | OGIR status | Verdict |
|---|---|---|
| §1 OpenCode-GLM as Head Agent / planner / router | The Orchestrator (`src/agents/orchestrator.py`) IS the single runtime entry point and dispatcher via AgentJobDelegator (MCP hand-off, URN `OGIR:<SPACE>:<ACTION>`). | Already built. |
| §2 Ollama local execution | Runtime is pure stdlib Python, zero network. Ollama is used ONLY for the optional operator REPL, NOT in the audit path. The AI conflated the operator CLI with the engine. | Misframed. |
| §3 Multi-agent specialist pipeline | Already shipped: Form_Entry -> Audit_Review -> Lattice_Compute -> Ledger_Seal, + Affidavit on demand. 10 deterministic no-LLM agents under `src/agents/`. | Already built. |
| §4 Symbolic deception rules (expand to 50-100) | 71 patterns, not 50-100, by deliberate design (calibration discipline, not pattern count). Adding patterns requires a sealed ONTOLOGY_BUMP + calibration rerun. | Already built; the AI's "expand to 100" is over-prescription. |
| §5 Truth Ledger (SHA-256 Merkle) | 41,077-block chain, re-derivable root, NIZK proof per block. | Already built. |
| §6 Four-gate -> seven-gate pipeline | OGIR uses a deliberate 4-gate pipeline: Deception ontology + Shannon entropy -> BBFB (LAW/GRACE/FRUIT/CVS) -> Optionality Lattice (F7-reframed as a deception-adjusted optionality index, NOT a valuation) -> Decision gate. The AI's 7-gate "Input/Planning/Execution/Evidence/Output/Legal/Human" is generic advice that would add latency without adding determinism. | Already built; the AI's expansion is not justified. |
| §7 Supabase with 16 suggested tables | Supabase is LIVE with 8 tables (customers, orders, order_files, scans, affidavits, cases, documents, document_requests) + 23 RLS policies + SSL. The AI's 16-table list includes `agents`, `models`, `tasks`, `runs`, `prompts`, `embeddings`, `memory`, `policies`, `audit_events`, `validation_results` — most of which duplicate what the Merkle chain already records (the chain IS the audit_events/runs/truth_ledger). | Over-prescribed; would duplicate the chain. |
| §8 MCP with 19 servers | OGIR streamlined 8 -> 3 MCP servers (sequential-thinking, github, supabase-disabled) after finding 5 were redundant with built-in tools. The AI's 19-server list (Docker, Playwright, Browser, OCR, Email, Calendar, Vector DB...) would violate the air-gap and add surface area for leaks. | Over-prescribed; contradicts the air-gap. |
| §10 Skills as YAML files | OGIR has 25 skills as `.md` files in `.opencode/skills/`, loaded into the build agent's context. YAML was not chosen because skills are prose instructions, not data configs. | Already built; format choice differs by design. |

### 3. What did the AI MISS — things OGIR has that the AI didn't know about?

- **The 4-gate pipeline is not 4 generic gates.** It is Deception ontology
  (71 patterns) + Shannon entropy -> BBFB engine (LAW multiplicative veto +
  GRACE quadratic penalty + FRUIT weighted product + CVS) -> Optionality
  Lattice (F7-reframed as a deception-adjusted optionality index, explicitly
  NOT a business valuation) -> Decision gate. The AI's "strengthen to 7
  gates" misses that the 4 gates are each mathematically specified.
- **Tau extraction ceiling (0.10).** `TauFirewall` enforces a 10% extraction
  ceiling on heavy operations and issues STRUCTURAL_REFUSAL on hit. The AI
  never mentioned a complexity firewall.
- **Traffic light indicator** (R/G/Y + directional + machine eval
  CLEAN/REVIEW/REFUSED) in engine + UI. The AI's output had no
  machine-actionable verdict.
- **Pre-push closing-procedure gate.** A git hook runs chain verification +
  the full test suite (~300s) before any push AND requires a SIGN_OFF block
  in the last 20 chain blocks. The AI never considered release integrity.
- **S-QoL (5-dimension worth statement)** and **BBFB deception/product-failure
  correlation** — domain engines the AI had no concept of.
- **Canonical JSON hardening.** Every `json.dumps` MUST pass through
  `_canonical_default` (sort_keys, compact separators, no `default=str`).
  The AI never raised determinism of serialization.
- **Operator identity constant** enforced by boundary test — no other
  identity can claim to operate the build without forking the source.
- **25 skills + 11 operator corrections** baked into a priority-check gate
  at session start and sign-off.

### 4. Did the AI over-prescribe?

Yes, severely. Two clear cases:

1. **19 MCP servers** when 3 is the right number. OGIR deliberately
   streamlined 8 -> 3 after finding 5 redundant with built-in tools. The
   AI's list (Docker, Playwright, Browser, OCR, Email, Calendar, Vector DB)
   would break the air-gap and add leak surface. The right answer is the
   minimum that does the job, not the maximum that sounds comprehensive.
2. **16 Supabase tables** when 8 is live and sufficient. The AI's
   `agents/models/tasks/runs/prompts/embeddings/memory/policies/audit_events/
   validation_results` mostly duplicate what the Merkle chain already
   witnesses. Adding them would create a second source of truth and a
   desync risk (the chain is the trust anchor; Supabase is the
   customer-facing store, not the audit witness).

The pattern: the AI treated "more components" as "better architecture."
For a deterministic air-gapped audit engine, the opposite is true — every
added component is a new attack/leak/desync surface.

### 5. What is the ONE most useful takeaway OGIR doesn't already have?

**A model capability registry.** The AI listed it under "Missing Components"
and it is the single item OGIR does not have and would benefit from.

What it would be: a small, sealed, deterministic table mapping each
available model (local + cloud) to its capabilities relevant to OGIR's
operator-facing work: code review quality, long-context reasoning,
tool-calling reliability, determinism of output, air-gap compatibility,
and cost. Today the operator picks the model for a job ad-hoc
(glm-5.2 for build, minimax-m3 for research, qwen2.5-coder for drafting,
DeepSeek-R1 local for review). A registry would make that explicit and
sealable, and would let the `launch-model-for-task` skill pull from a
single source of truth instead of the skill's prose.

Everything else in the AI's "Missing Components" list (agent state
machine, prompt versioning, retry policies, secret management, sandboxed
execution, regression testing, disaster recovery, security model) is
either already present or explicitly out of scope for the air-gapped
runtime. The model capability registry is the one genuinely new, useful,
non-redundant item.

### 6. Was the AI's framing ("concept paper, not a software spec") correct?

No. It was the single biggest error. The AI was given a high-level
architecture vision and correctly observed that the *prompt itself* reads
like a concept paper — that part is fair. But it then concluded the
*project* is a concept paper and spent 400 lines advising the operator to
build things that are already built and tested. The correct framing would
have been: "This prompt describes a system; does that system exist? If it
does, here is what's already covered and what's missing." The AI never
asked whether the system existed, so it prescribed a greenfield build to
someone who already has a 41,077-block chain and 411 passing tests.

This is exactly the failure mode OGIR's engine is designed to detect:
responding to a frame that was never established by the operator, and
filling it with confident-sounding content that misses the actual state.

### 7. Rate the AI's response (1-10) for usefulness to someone who already has a working system.

**3/10.**

Justification:
- It correctly identified the two strongest ideas (deterministic detection,
  Merkle truth ledger) — but OGIR already has both, so the identification
  is confirmation, not new value.
- It got the head-agent / multi-agent / Supabase / MCP / skills
  architecture directionally right — but prescribed building them from
  scratch when they already exist, at a larger scale than OGIR chose
  deliberately.
- It missed every OGIR-specific component that makes the engine
  defensible (Tau firewall, 4-gate math, traffic light, canonical JSON,
  pre-push gate, S-QoL, BBFB correlation, operator identity enforcement).
- The single genuinely useful new item (model capability registry) was
  buried in a "Missing Components" list of 16 items, 15 of which are
  redundant or out of scope.
- The framing error (treating a built system as a concept paper) would
  have wasted weeks if the operator had followed it literally.

It gets a 3 rather than a 1 because it did not hallucinate, did not
fabricate citations, and did correctly name the two load-bearing ideas.
But for someone who already has the system, ~90% of the response is
redundant work.

## Alignment against OGIR flows (summary table)

| OGIR flow | Optimum file covers it? | Note |
|---|---|---|
| Verify chain (session start) | No | The AI never considered session integrity. |
| 4-gate audit pipeline | Partially | Mentioned "gates" but generic, not the OGIR math. |
| Deception ontology (71 patterns) | Yes (concept) | But prescribed 50-100; OGIR chose 71 by calibration. |
| Merkle truth ledger | Yes | Already built. |
| BBFB engine | No | Never mentioned. |
| Optionality Lattice (F7) | No | Never mentioned. |
| Tau extraction ceiling | No | Never mentioned. |
| Traffic light verdict | No | Never mentioned. |
| Canonical JSON determinism | No | Never mentioned. |
| Pre-push closing gate | No | Never mentioned. |
| Supabase backend | Yes (over-prescribed) | 8 live tables vs 16 suggested. |
| Cloudflare Worker | No | Never mentioned. |
| Tauri desktop binary | No | Never mentioned. |
| Skills (25) | Yes (format differs) | OGIR uses .md, AI suggested .yaml. |
| MCP (3) | Yes (over-prescribed) | AI suggested 19. |
| Aider sandbox | No | Never mentioned. |
| Operator identity enforcement | No | Never mentioned. |
| Session sign-on/off ritual | No | Never considered session integrity. |

**Bottom line:** the optimum file describes a subset of OGIR at a higher
component count and lower mathematical specificity. Of its 13 sections,
8 are already built, 2 are over-prescribed, 2 are out of scope for the
air-gap, and 1 (model capability registry) is genuinely new and worth
building. The AI's response would be useful to a greenfield operator; to
the operator of an existing 41,077-block engine it is mostly redundant.

## Recommended next action (operator decision)

Build the **model capability registry** as a sealed JSON file under
`02_Technical/config/` (e.g. `model_capabilities.json`) plus a small
loader, wired into the `launch-model-for-task` skill. This is the one
non-redundant, air-gap-safe, determinism-preserving takeaway. It is a
CONSTANTS_BUMP-adjacent change (adds a config artifact, not a numeric
threshold) and would be sealed as `MODEL_CAPABILITY_REGISTRY_ADDED`.
No other item from the optimum file warrants new work.