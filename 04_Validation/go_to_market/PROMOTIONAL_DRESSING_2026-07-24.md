# OGIR Promotional Dressing + Public-Facing Tidy-Up

> Created 2026-07-24. Internal.
> What we do in layman's terms + the public-facing marketing arm.
> Not a sales team. Just a tidy, honest, professional front.
> Sealed to chain: `PROMOTIONAL_DRESSING_2026_07_24`

---

## PART 1: WHAT WE DO â€” in layman's terms

### The 30-second pitch (for anyone)

> "Order Get It Right is a tool that reads documents and tells you
> if the words are trying to trick you. It checks for 55 different
> patterns of deception â€” things like vague promises, fake
> confidence, and dodging responsibility. Every check is recorded
> to a tamper-proof digital ledger, so you can prove in court
> what was found and when."

### The 3-minute pitch (for a potential client)

> "You know when a supplier emails you and something feels off?
> The warranty terms are vague. The performance claims sound too
> good. The apology sounds rehearsed. You can't put your finger on
> it, but something's wrong.
>
> Order Get It Right reads that email â€” or that contract, or that
> invoice, or that product listing â€” and tells you exactly what
> flagged. Not just 'this is deceptive' but 'this sentence matched
> the Clarity Shield pattern because it used the word 'clearly'
> without citing any evidence.' 55 patterns, each one explained.
>
> You see the flagged patterns, you decide if it's deceptive or
> if there's a good explanation. If there is, you can submit your
> explanation and it gets recorded alongside the findings â€” it
> doesn't change the verdict, it adds your context.
>
> Every audit is sealed to a Merkle chain â€” a digital ledger that
> can't be altered without detection. If you need to take it to
> court, you get an affidavit with the chain proof that the audit
> was done on a specific date and hasn't been tampered with.
>
> It's open source. You can run it yourself. You can verify the
> chain yourself. You don't have to trust me â€” you trust the math."

### What we do (bullet points for the website)

- **Read documents and flag deception patterns** â€” 55 patterns,
  each one explained in plain English
- **Score the likelihood of deception** â€” 0% to 100%, with the
  reasoning shown
- **Generate court-ready affidavits** â€” under Australian Consumer
  Law Section 56 + Evidence Act 1995
- **Seal everything to a tamper-proof chain** â€” SHA-256 Merkle
  chain, 40,000+ blocks, verifiable by anyone
- **Let the client explain** â€” if something flagged but there's
  truth behind it, the client submits their explanation, sealed
  to the chain as their statement
- **Work fully offline** â€” zero network calls in the audit engine,
  no cloud AI, no data leaving your machine

### What we DON'T do (honesty builds trust)

- We DON'T give legal advice â€” we're a tool, not a lawyer
- We DON'T guarantee truth or falsehood â€” we flag patterns, you decide
- We DON'T replace a lawyer â€” we give your lawyer better evidence
- We DON'T store your data beyond the retention period (7 years)
- We DON'T sell your data â€” ever

---

## PART 2: PUBLIC-FACING TIDY-UP

### The "back and sides" â€” what needs trimming

| Area | Current state | What to do |
|------|--------------|------------|
| **GitHub repo** | Private, branch name `ogir-build-2026-07-18` | Make public (when ready), rename branch to `main`, add CONTRIBUTING.md |
| **README.md** | Stale (references 272 tests, old state) | Rewrite to match INDEX.md v2.0 (400 tests, 40k blocks, live Worker) |
| **Landing page** | `docs/index.html` written (dark theme, stats, pipeline) | Enable GitHub Pages â†’ Settings â†’ Pages â†’ /docs â†’ ordergetitright.com |
| **Repo description** | Empty | Set to: "Forensic deception-detection for business documents. 55 patterns, Merkle chain sealed, air-gapped, open source." |
| **Topics/tags** | None | Add: `forensics`, `audit`, `deception-detection`, `merkle-chain`, `tauri`, `python`, `open-source` |
| **GitHub profile** | `truthprojectofficial-max` | Add bio: "Verified Processor. Building OGIR â€” a forensic lie-detector for business documents." Add link to ordergetitright.com |
| **Social proof** | None yet | When you have real cases: add "134 cases audited, 100% accuracy" to the landing page (already true from calibration) |
| **Download page** | Links to GitHub Releases (no releases yet) | When cert arrives + v0.1.0 tagged: the release page will have the signed installer |
| **Email signature** | None | Add: "Justin Barnett | Order Get It Right â€” Verified Processor | ordergetitright.com" |
| **Business cards** | None | Print: name, title (Operator), "Order Get It Right", ordergetitright.com, phone, email. ~$20 for 100 at Vistaprint |
| **LinkedIn** | Unknown | Add a profile entry for OGIR if you have LinkedIn. "Founder & Operator at Order Get It Right" |

### The promotional dressing (subtle, honest, professional)

**NOT a sales team. Just professional presentation:**

1. **Landing page** (already written): dark theme, matches the
   product, shows the stats (55 patterns, 100% accuracy, 40k blocks,
   0 network imports), the 4-gate pipeline, the trust model, download
   links. No hype. No "revolutionary" or "game-changing". Just facts.

2. **GitHub repo**: clean README, CONTRIBUTING.md (welcome
   contributors), issues labeled `good-first-issue`, discussions
   enabled. Open source = free marketing in the dev community.

3. **Privacy Policy** published on the website (already written,
   needs to go to `docs/PRIVACY_POLICY.md` for GitHub Pages).

4. **Terms of Service** on the website (needs writing â€” see
   `LEGAL_HANDLING_2026-07-24.md`).

5. **Download page**: GitHub Releases with signed binaries. The
   auto-updater checks `update.ordergetitright.com` (already live).

6. **Community boards** (you mentioned placing on community boards):
   - Reddit: r/forensics, r/ausbusiness, r/smallbusinessaustralia
   - Whirlpool (AU forum): https://whirlpool.net.au â€” post in the
     "What's your side project?" or "Small business" threads
   - Product Hunt: https://producthunt.com â€” launch when v0.1.0 is
     signed and downloadable
   - Hacker News: https://news.ycombinator.com â€” "Show HN: OGIR,
     a forensic lie-detector for business documents"
   - Local SA: Whyalla community boards, SA business Facebook groups

### The messaging (consistent across all surfaces)

| Surface | Message |
|---------|---------|
| Landing page | "Verified Processor. Forensic deception-detection for business documents." |
| GitHub | "55 patterns, Merkle chain sealed, air-gapped, open source." |
| Community posts | "I built a tool that reads contracts/emails and flags 55 deception patterns. Open source, chain-sealed, works offline." |
| Business card | "Order Get It Right â€” ordergetitright.com" |
| Email sig | "Justin Barnett | Order Get It Right â€” Verified Processor" |

---

## PART 3: WHAT TO DO (in order)

1. [ ] Enable GitHub Pages (repo Settings â†’ Pages â†’ /docs â†’ ordergetitright.com)
2. [ ] Copy Privacy Policy to `docs/PRIVACY_POLICY.md`
3. [ ] Write Terms of Service (use termly.io template + OGIR clauses)
4. [ ] Rewrite README.md to match current state (400 tests, 40k blocks, live Worker)
5. [ ] Set GitHub repo description + topics
6. [ ] Update GitHub profile bio
7. [ ] Make repo public (when you're ready)
8. [ ] Print business cards (Vistaprint, ~$20)
9. [ ] Set up email signature
10. [ ] Post on community boards (Whirlpool, Reddit, local SA) â€” only AFTER the repo is public + the landing page is live + v0.1.0 is downloadable

---

**This document is internal marketing planning. Not sealed to the chain
until approved by the operator.**