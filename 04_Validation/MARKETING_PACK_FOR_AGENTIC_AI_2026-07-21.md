# Order Get It Right — Marketing Pack for Agentic AI

## 1. One-line pitch

Order Get It Right is a deterministic, air-gapped business audit-and-valuation engine that reads any business document, detects deception, evaluates economic fairness, and produces a legally-grounded GO / DEFER / TEST FIRST / REJECT verdict — with every decision sealed to a tamper-evident Merkle truth ledger.

## 2. Who it is for

- **Small-business operators** checking supplier claims, warranties, quotes, and compliance documents.
- **Consumer advocates** and community legal centres handling unfair-contract or misleading-conduct disputes.
- **Sole-trader professionals** who need defensible evidence without paying for expert witnesses.
- **Regtech developers** who want a transparent, no-black-box audit component to embed in their own stack.
- **Any operator** who has been burned by an AI assistant that hallucinated project facts, fabricated compliance, or silently changed its story.

## 3. The problem it solves

AI tools today either:
- hide behind a black box ("the model says yes"),
- make up facts about your own files (cloud-displacement, phantom build environments),
- require a live internet connection and a paid API key, or
- produce advice that evaporates when challenged in a tribunal.

Order Get It Right does the opposite. Every number is traceable to a named constant and a documented formula. Every output is sealed to a chain you can verify offline. It runs on your machine, not a vendor's cloud container.

## 4. What it actually does

Drop in any business document — invoice, contract, marketing email, warranty certificate, regulator letter, evidence pack — and the engine runs four deterministic gates in one pass:

1. **Deception Gate** — 55-pattern ontology detects misleading language, facade of competence, false certainty, scope creep, phantom environments, and more. Includes structural R1-R6 co-text gates so honest text is not misclassified.
2. **BBFB Gate** — LAW (multiplicative veto), GRACE (quadratic penalty), FRUIT (four-pillar weighted value score: cost, performance, reliability, compliance).
3. **Optionality Gate** — deception-adjusted compound binomial lattice; surfaced as a stylised optionality index, never misrepresented as a business valuation.
4. **Decision Gate** — produces GO / DEFER / TEST FIRST / REJECT with a reason string and a sealed chain entry.

It also drafts:
- Section 56 ACL demand letters,
- Section 177 expert-certificate style affidavits,
- Markdown / DOCX / PDF audit reports.

## 5. Key differentiators

| Feature | Why it matters |
|---|---|
| **100% deterministic** | Same input + same config = same verdict on any host. No randomness, no temperature slider. |
| **Air-gapped** | No network call needed. Runs on Python stdlib. No API key, no vendor lock-in. |
| **Tamper-evident ledger** | Every action sealed to a SHA-256 Merkle chain. Third parties can run `verify_chain` to confirm integrity. |
| **Legally grounded** | Built-in references to Makita v Sprowles [2001] NSWCA 305 and ACCC v Valve [2016] FCA 196/1553. |
| **No black-box AI** | Every pattern, formula, and weight is inspectable in source and methodology docs. |
| **Two delivery shapes** | Python install or Tauri desktop binary. Same engine underneath. |
| **Ollama-immune** | Optional chat shell can use Ollama, but the engine itself never depends on it. Ollama timeouts cannot break the audit. |

## 6. How to talk about it (sample copy)

**Short social post:**
> Tired of AI that lies about your own files? Order Get It Right reads business documents, runs a deterministic deception-and-value audit, and seals every verdict to a tamper-evident chain — no cloud, no API key, no black box.

**Longer landing-page paragraph:**
> Order Get It Right is a local business-truth engine for operators who need more than a chatbot's guess. It ingests contracts, warranties, quotes, and evidence packs; applies a deterministic four-gate audit model (deception detection, economic fairness, optionality, and decision); and produces a defensible GO / DEFER / TEST FIRST / REJECT verdict. Every output is recorded on a SHA-256 Merkle chain that can be re-verified offline, giving you an audit trail that stands up to scrutiny.

**For legal-adjacent audiences:**
> Order Get It Right is not legal advice software — it is an evidence-organisation and audit-truth tool. It helps you structure documents, detect misleading claims, quantify economic gaps, and record your reasoning in a tamper-evident ledger so you or your adviser can present a coherent, defensible case.

## 7. Technical trust signals

- Open, inspectable Python source under `02_Technical/src/`.
- Every constant named and centralised in `config/constants.py`.
- 256 pytest regression tests, including boundary enforcement, canonical JSON hardening, host-dependent deployment, and legal precedent assertions.
- Governance and rejection docs formalise why non-deterministic alternatives (S-QoL/SWB/ALDVMM, cloud-only builds) were rejected.
- Git + Merkle chain dual trust anchors: code changes are committed; audit decisions are sealed.

## 8. Call to action options

- **Download the Tauri desktop binary** and audit your first document offline.
- **Clone the Python source** and run `pytest tests/` to verify the engine before you trust it.
- **Book a demo** for your community legal centre, small-business association, or compliance team.
- **Request a case study** showing how the Selby evidence pack and Makita/Valve precedents produce a sealed, defensible output.

## 9. What NOT to claim

- Do not claim it replaces a lawyer. It is an audit-truth and evidence-organisation tool.
- Do not claim it predicts the future. The optionality lattice is a stylised index, not a valuation.
- Do not claim it uses generative AI to decide. Decisions come from deterministic rules, not an LLM.
- Do not claim it needs Ollama. Ollama is optional; the engine runs without it.

## 10. Operator / maintainer note

This is a living artefact, not a frozen product. It is maintained by a single operator on a daily/weekly/monthly rhythm, with every change committed to Git and sealed to the Merkle chain. The build is operational, maintained, and auditable — not "finished" and abandoned.

---

**Drop this pack into any marketing agentic AI as a single briefing document.** It contains the pitch, audience, problem, features, sample copy, trust signals, CTAs, and guardrails.
