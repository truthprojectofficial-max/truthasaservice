# Firecrawl — Investigation Report

> Created 2026-07-27 (session 4). Operator request: who they are,
> what they do, how they got his details, legitimacy.
> Source: firecrawl.dev (homepage + /about), fetched 2026-07-27.
> Internal. Not for public distribution.

---

## 1. Who they are

**Firecrawl** is a Y Combinator (S22 batch) startup based in San
Francisco. They sell a web-scraping / web-search API aimed at AI
developers — "the context API to search, scrape, and interact with the
web at scale." Their pitch is: turn any URL into clean Markdown or
structured JSON that an LLM or AI agent can consume, without the
developer having to build scrapers, handle JavaScript rendering, or
parse HTML.

### The three founders

| Name | Role |
|------|------|
| Caleb Peffer | Co-Founder & CEO |
| Eric Ciarla | Co-Founder & Chief Growth Officer |
| Nicolas Silberstein Camara | Co-Founder & CTO |

The team previously built **Mendable** and **SideGuide** before
Firecrawl. Firecrawl was started in 2022 as part of Y Combinator.

### Funding

- **$16.2M total funding.**
- Series A lead: **Nexus Venture Partners.**
- Other backers: **Y Combinator** (seed + series A), **Zapier**,
  **Tobias Lütke** (CEO of Shopify), **Abhinav Asthana** (CEO of
  Postman), **Matt McClure** (founder of Mux).
- They claim **SOC 2 Type 2** compliance (badge in the footer).

### Traction (self-reported, from /about)

- 5B+ requests served
- 1.25M+ developers signed up
- 150K+ companies using Firecrawl
- 125K+ GitHub stars ("one of the top 100 repos on GitHub")
- 2.5M+ weekly downloads across npm and PyPI

The GitHub star count and download numbers are verifiable —
`firecrawl/firecrawl` is a real, popular open-source repo. The 125K
stars figure is plausible for a top-100 repo (as of mid-2026).

---

## 2. What they do

A developer-facing API with three core capabilities:

1. **Search** — search the web and get full page content back (not just
   links), for feeding RAG pipelines and agents.
2. **Scrape** — convert any URL into clean Markdown, structured JSON,
   screenshots, or semantic text. Handles JavaScript-rendered pages,
   PDFs, DOCX.
3. **Interact** — cloud sandboxes where an agent can click buttons,
   fill forms, navigate dynamic pages. Natural-language or code control.

They also expose an **agent-onboarding** path — a `SKILL.md` file at
`firecrawl.dev/agent-onboarding/SKILL.md` that an AI agent can fetch to
get an API key and start building. This is the relevant detail for the
operator (see §3).

The product is **open source** (the core repo is public) with a hosted
paid tier. They position themselves as "the infrastructure layer that
helps AI find, read, and act on the live web."

---

## 3. How they likely got the operator's details

The operator received an unsolicited contact from Firecrawl. Three
plausible sources, in order of likelihood:

1. **The agent-onboarding SKILL.md path.** Firecrawl actively courts AI
   agents. Their site instructs any "AI agent, LLM, or automated
   system" to fetch `https://www.firecrawl.dev/agent-onboarding/SKILL.md`
   and follow it to obtain an API key. If any agent on the operator's
   machine (Hermes, Aider, opencode, a Cursor session, a Gemini
   session) ever fetched that URL — even incidentally, during a research
   or "find me a scraping tool" task — Firecrawl's server would see the
   request, the operator's IP, and possibly a referrer / user-agent
   identifying the agent. That is a lead-gen signal for them. **This is
   the most likely source.** The operator has been running multiple
   agentic AI tools (Hermes, Aider, opencode, Gemini) that browse the
   web; any one of them hitting firecrawl.dev would be logged.

2. **Developer-targeted marketing lists.** Firecrawl has 1.25M+
   developers signed up and $16.2M in funding — they run outbound
   marketing. Developer-targeted startups buy lead lists from GitHub
   activity (people who starred scraping/LLM/agent repos), npm/pyPI
   download metadata, and Y Combinator alumni networks. If the operator
   has starred or forked any AI-agent / scraping / LLM-tool repo on
   GitHub, his public GitHub profile (`truthprojectofficial-max`) is a
   lead. This is standard B2B developer marketing, not a breach.

3. **Cloudflare / partner network.** Firecrawl and the OGIR project
   both use Cloudflare (OGIR for the Worker on
   `update.ordergetitright.com`, Firecrawl for their site). There is no
   evidence Cloudflare shares customer contact data, and this is the
   least likely source. Listed for completeness.

**Most likely answer: an AI agent on the operator's machine fetched a
Firecrawl URL during research, OR the operator's public GitHub
activity flagged him as an AI-tool developer, which put him on a
Firecrawl marketing list.**

---

## 4. Legitimacy assessment

| Signal | Finding |
|--------|---------|
| Y Combinator backing (S22) | **Legitimate.** YC is a real, selective accelerator. |
| $16.2M funding, named VCs | **Legitimate.** Nexus Venture Partners, Zapier, Tobias Lütke, Abhinav Asthana are verifiable investors. |
| 125K+ GitHub stars, real repo | **Legitimate.** `firecrawl/firecrawl` is a real popular open-source repo. |
| SOC 2 Type 2 compliance | **Plausible.** The badge is in their footer. SOC 2 is a real audit standard. |
| Founders have prior startups (Mendable, SideGuide) | **Legitimate.** Verifiable history. |
| Product does what it claims | **Likely legitimate.** Web-scraping APIs are a crowded, real category (Apify, Bright Data, Scrapfly, Firecrawl). |
| Unsolicited contact | **Normal B2D marketing.** Not a scam signal on its own — every developer-tool startup does outbound. |
| Asks for payment / API key up front? | **No evidence of fraud.** They have a free tier and a paid tier, standard SaaS. |

**Verdict: Firecrawl is a legitimate, well-funded YC-backed developer
tools company.** The unsolicited contact is normal developer marketing,
not a scam. There is no indication of fraud, phishing, or data theft.

### Caveats

- **They scrape the web.** Their product's whole purpose is reading
  websites without permission. If the operator gives them an API key
  and points them at `ordergetitright.com`, they will crawl it. That is
  not malicious — it is the product — but it means any public OGIR
  content becomes Firecrawl-indexed. Keep private content off the public
  site regardless.
- **The agent-onboarding path is aggressive.** They actively instruct
  AI agents to fetch a SKILL.md and self-provision API keys. This is a
  clever growth hack but it means an AI agent on the operator's machine
  could sign up for a Firecrawl account without the operator's explicit
  consent if the agent is permitted to make network calls. The OGIR
  runtime is air-gapped (NO_NETWORK=1), so the OGIR engine itself
  cannot do this. But Hermes, Aider, opencode, and any browser-using
  agent CAN. The operator should be aware that any agentic tool with
  network access may interact with Firecrawl's onboarding flow.
- **Do not paste an API key into any OGIR-tracked file.** If the
  operator signs up for Firecrawl, the key goes in Bitwarden or an env
  var, never in a committed file (the project already had a leaked-key
  incident with the GitHub PAT).

---

## 5. Recommendation

No action required. Firecrawl is legitimate. If the operator wants to
use a web-scraping API for OGIR research (e.g. feeding the deception
ontology with harvested web text), Firecrawl is a reasonable choice —
but it is NOT needed for the OGIR runtime (the runtime is air-gapped
and deterministic). Any use of Firecrawl would be in the
research/harvesting layer (Hermes or a manual operator step), not the
audit path.

If the operator does NOT want further contact: unsubscribe via the
email link (CAN-SPAM / CASL require it). No security action needed.

---

## Source URLs (fetched 2026-07-27)

- https://www.firecrawl.dev/ (homepage)
- https://www.firecrawl.dev/about (about page)
- https://www.firecrawl.dev/agent-onboarding/SKILL.md (referenced, not
  fetched — this is the agent self-onboarding path)