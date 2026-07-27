# OGIR Release Announcement — Social/Dev Community Posts

> Date: 2026-07-27
> Purpose: Ready-to-paste posts for sharing OGIR with the developer
>   community. The operator asked to "put it in social pages for
>   devs/public give away." This file has the copy for each platform.
> Status: Sealed to chain. No code changed.

---

## 1. Reddit post (r/programming, r/Python, r/devops)

**Title:** [Show] I built an air-gapped, deterministic deception-detection engine in pure Python — 71 patterns, Merkle-sealed, court-grade affidavits. 411 tests, MIT, here's the source.

**Body:**

I've been working on a project called Order Get It Right (OGIR) — a forensic lie-detector for business documents. It reads contracts, warranties, supplier emails, product listings, and flags the specific language patterns that signal deception.

The design constraints were brutal and I'd love feedback from people who care about this kind of thing:

- **Deterministic.** Same input + same config = same output, on any host. No `random`, no `time.time()`, no `datetime.utcnow()`. Every `json.dumps` goes through a canonical serializer (`sort_keys=True`, compact separators, no `default=str`).
- **Air-gapped.** Zero network imports in the runtime. No cloud APIs in the audit path. Pure stdlib Python 3.12+. A boundary test (AST scan) enforces this — you literally cannot add `import requests` to the audit engine.
- **Chain-sealed.** Every audit decision is appended to a SHA-256 Merkle chain (41,079+ blocks). The root re-derives on any host. A pre-push git hook runs chain verification + the full test suite before allowing any push, and requires a signed-off block in the last 20 chain blocks.
- **71 deception patterns** across 3 tiers (dialects, structural mechanics, linguistic markers), with R1-R7 gates that suppress false positives. Calibrated against 142 cases at 100% accuracy, 0 FP, 0 FN, F1=1.0.

The 4-gate pipeline:
1. Deception ontology (71 patterns) + Shannon entropy
2. BBFB engine (LAW multiplicative veto + GRACE quadratic penalty + FRUIT weighted product + CVS)
3. Optionality Lattice (a deception-adjusted optionality index — explicitly NOT a business valuation)
4. Decision gate (GO / REVIEW_REQUIRED / REFUSED / REJECT)

Every audit produces a court-ready affidavit under Australian Consumer Law Section 56 + Evidence Act 1995, with the Merkle chain proof attached.

**What's live:**
- GitHub repo (public, MIT): https://github.com/truthprojectofficial-max/truthasaservice
- Landing page: https://ordergetitright.com
- Tauri v2 desktop binary (Windows/macOS/Linux)
- Live Supabase backend (8 tables, RLS, SSL)
- Cloudflare Worker for update distribution

**What I'd like feedback on:**
1. The determinism model — is the canonical JSON + chain-seal approach sound, or am I missing edge cases?
2. The pattern ontology — 71 is a deliberate choice (calibration discipline, not pattern count). Is that the right tradeoff vs. a larger rule set?
3. The air-gap enforcement — the boundary test catches `import requests`, but are there other ways an audit engine could leak?

I'm a non-coder who built this with AI assistance over ~2.5 years. The repo has 411 passing tests and a 41,079-block chain that re-derives clean. I'm sharing it because I think the architecture (deterministic, air-gapped, chain-sealed) is more interesting than the specific patterns, and I'd rather someone use it or learn from it than have it sit on my machine.

Happy to answer questions. Not selling anything — MIT licensed, free to fork.

---

## 2. Hacker News post (Show HN)

**Title:** Show HN: Air-gapped deterministic deception-detection engine — 71 patterns, Merkle-sealed, pure Python

**Body:**

Order Get It Right (OGIR) reads business documents and flags deception patterns — vague promises, fake confidence, dodged responsibility, fabricated citations, authority mimicry. 71 patterns across 3 tiers, with structural gates (R1-R7) that suppress false positives.

The engineering constraints are the interesting part:

- Pure stdlib Python in the audit path (no network, no cloud, no dependencies). A boundary test enforces this.
- Every audit decision sealed to a SHA-256 Merkle chain. 41,079+ blocks, re-derivable root.
- Deterministic: canonical JSON, no random/time.time()/datetime.utcnow(). Same input always produces the same output.
- Pre-push git hook runs chain verification + full test suite (411 tests, ~180s) before any push, and requires a signed-off chain block in the last 20 blocks.
- 142-case calibration at 100% accuracy (0 FP, 0 FN, F1=1.0).
- Court-ready affidavits under Australian Consumer Law + Evidence Act 1995, with chain proof attached.

The 4-gate pipeline: Deception ontology (71 patterns + Shannon entropy) → BBFB (LAW/GRACE/FRUIT/CVS) → Optionality Lattice (deception-adjusted optionality index, not a valuation) → Decision.

I'm sharing it because the architecture (deterministic + air-gapped + chain-sealed) might be useful to others building audit/verification systems. MIT licensed. The repo is here: https://github.com/truthprojectofficial-max/truthasaservice

I built this with AI assistance as a non-coder over ~2.5 years. The chain and tests are real — `python -m src.verify_chain` re-derives the root, `python -m pytest tests/ -q` passes 411/411. Feedback on the determinism and chain model welcome.

---

## 3. GitHub Discussions welcome post

**Title:** Welcome — what would you use a deterministic deception-detection engine for?

**Body:**

OGIR (Order Get It Right) is now public and MIT-licensed. This is a place to ask questions, suggest use cases, and discuss the architecture.

**What it is:** an air-gapped, deterministic engine that reads business documents and flags 71 deception patterns. Every audit sealed to a SHA-256 Merkle chain. Court-ready affidavits.

**What I'd like to hear:**
- What documents would you run through it? (contracts, supplier emails, product claims, NDIA/DSP correspondence, tenancy agreements...)
- Which patterns matter most for your use case?
- Would you run it from source, the desktop binary, or an API?
- Anyone interested in porting the ontology to another language or integrating it into a larger workflow?

**Ground rules:**
- Be direct. No hedging. (The engine detects that.)
- The runtime is air-gapped and deterministic. If you want to add a feature that breaks that, explain why it's worth it.
- Read `AGENTS.md` and `CONTRIBUTING.md` before opening a PR. Every change is dual-witnessed: a Git commit AND a Merkle chain block.

Repo: https://github.com/truthprojectofficial-max/truthasaservice
Landing page: https://ordergetitright.com

---

## 4. Twitter/X thread

1/ I built a deterministic lie-detector for business documents. 71 deception patterns, Merkle-sealed, air-gapped, pure Python. MIT licensed. Here's the source. 🧵

2/ It reads contracts, warranties, supplier emails, product listings. Flags vague promises, fake confidence, dodged responsibility, fabricated citations. Each pattern has an ID, a severity, and the matched indicators shown.

3/ The engineering constraints: pure stdlib Python in the audit path (no network, no cloud). A boundary test enforces it — you can't add `import requests`. Deterministic: no random, no time.time(), canonical JSON. Same input = same output, always.

4/ Every audit decision is sealed to a SHA-256 Merkle chain. 41,079+ blocks. The root re-derives on any host. A pre-push hook runs chain verification + 411 tests before any push, and requires a signed-off block in the last 20 chain blocks.

5/ 142-case calibration at 100% accuracy, 0 false positives, 0 false negatives, F1=1.0. The 4-gate pipeline: Deception (71 patterns) → BBFB → Optionality Lattice → Decision. Court-ready affidavits under Australian Consumer Law.

6/ I'm a non-coder who built this with AI assistance over 2.5 years. The chain and tests are real — `python -m src.verify_chain` re-derives the root, `python -m pytest tests/ -q` passes 411/411. I'm sharing it because the architecture is more interesting than the patterns.

7/ Repo (public, MIT): https://github.com/truthprojectofficial-max/truthasaservice
Landing page: https://ordergetitright.com
Tauri desktop binary, live Supabase backend, Cloudflare Worker for updates.
MIT licensed. Free to fork. Feedback on the determinism and chain model welcome.

---

## 5. LinkedIn post

I've open-sourced a project I've been building for 2.5 years: Order Get It Right (OGIR) — a deterministic, air-gapped deception-detection engine for business documents.

It reads contracts, warranties, supplier emails, and product listings, and flags 71 specific deception patterns — vague promises, fake confidence, dodged responsibility, fabricated citations. Every audit decision is sealed to a SHA-256 Merkle chain (41,079+ blocks), producing court-ready affidavits under Australian Consumer Law.

The engineering model: pure stdlib Python (zero network in the audit path), deterministic (same input always produces the same output), and chain-sealed (a pre-push git hook runs chain verification + 411 tests before any push). 142-case calibration at 100% accuracy.

It's MIT licensed and public: https://github.com/truthprojectofficial-max/truthasaservice

I built this with AI assistance as a non-coder. The architecture (deterministic + air-gapped + chain-sealed) is what I think is worth sharing. If you work in audit, compliance, forensic linguistics, or verification systems, I'd value your feedback.

---

## Operator instructions for posting

These are ready to paste. The operator does the posting (the build agent
does not post to social media — that's an operator action). Recommended
order:

1. **GitHub Discussions** — post the welcome message first (creates a
   home for follow-up questions).
2. **Reddit** — r/programming or r/Python (largest dev audience, best
   feedback on the determinism model).
3. **Hacker News** — Show HN (high-signal dev audience, but read the
   Show HN guidelines first — no clickbait, the title above is factual).
4. **Twitter/X** — the thread (for reach).
5. **LinkedIn** — last (different audience, more business-oriented).

Do NOT post all of them on the same day — stagger over 2-3 days so each
post gets its own attention rather than splitting the audience.