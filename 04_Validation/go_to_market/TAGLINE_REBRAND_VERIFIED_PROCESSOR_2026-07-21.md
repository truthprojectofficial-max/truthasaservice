# Tagline rebrand: Verified Processor

## Decision

The project tagline is changed from "Truth as a Service" to "Verified Processor."

## Why

"Truth as a Service" over-promises. It implies the engine *is* truth or can deliver truth on demand. That is legally and epistemically dangerous:

- It invites misrepresentation claims.
- It suggests infallibility.
- It conflicts with the project's own mandate that the engine is a deterministic tool, not an oracle.

"Verified Processor" is more accurate:

- **Verified** = every output is traceable to named constants, documented formulas, and a sealed Merkle chain that third parties can re-derive.
- **Processor** = it processes inputs; it does not *become* the truth. The operator remains responsible for the inputs and for legal judgment.

## What changed

| File | Before | After |
|---|---|---|
| `02_Technical/config/constants.py` | `PROJECT_TAGLINE = "Truth as a Service"` | `PROJECT_TAGLINE = "Verified Processor"` |
| `02_Technical/src/__init__.py` | `__tagline__ = "Truth as a Service"` | `__tagline__ = "Verified Processor"` |
| `02_Technical/web/index.html` | title and version-line showed "Truth as a Service" | shows "Verified Processor" |
| `README.md` | heading "Truth as a Service" | heading "Verified Processor" |
| `04_Validation/MARKETING_PACK_FOR_AGENTIC_AI_2026-07-21.md` | used "business-truth engine" and "audit-truth tool" | reframed as "Verified Processor" |
| `04_Validation/ACCREDITATION_AND_VERIFICATION_BRIEF_2026-07-21.md` | "block-build of truth" and "truth machine" | reframed as "Verified Processor" and "auditable processing tool" |

## What did NOT change

- Historical records: `04_Validation/changelog.log`, hardcopy documents, and archive files keep the old tagline as a matter of truthful record.
- The Tauri shell config (`tauri.conf.json`, `Cargo.toml`) still contains the old tagline until the next binary rebuild. This is acceptable because the binary is not the live runtime.
- The sealed Merkle chain is append-only; old blocks are unchanged.

## Operator/marketing rule

- Do not use "truth machine", "Truth as a Service", or similar absolute claims in new marketing, legal, or product copy.
- Use "Verified Processor" or describe the engine as a deterministic audit/valuation tool that seals decisions to a chain.
- Every external claim must be verifiable from the source tree, the constants file, or the chain.

## Test lock

`tests/test_tagline_rebrand.py` asserts:
- `config/constants.py` and `src/__init__.py` use "Verified Processor".
- `web/index.html` uses "Verified Processor".
- No *new* source file contains the legacy tagline (historical logs/archives are whitelisted).

## Sealed

Block recorded under event `TAGLINE_REBRAND_VERIFIED_PROCESSOR_2026_07_21`.
