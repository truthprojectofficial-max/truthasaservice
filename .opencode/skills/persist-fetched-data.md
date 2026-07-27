---
description: "Use after every webfetch, fetch_fetch, or web_search call. The fetched result lives only in context — context is ephemeral. Write the raw result to a file BEFORE you analyze it, summarize it, or act on it. If the session ends or context is compacted, the data is gone. Files are durable. Persist first, analyze second."
---

# Persist Fetched Data Skill

## Why this skill exists

In session 3 (2026-07-27), the agent fetched the Firecrawl website and
about page. The raw data lived in the session context. The operator
then said "STOP — sign off." The session ended. **The fetched data was
gone.** In session 4, the next agent had to re-fetch the same URLs
because the prior agent never wrote the raw result to a file.

Context is ephemeral. Files are durable. **Persist first, analyze
second.**

## The rule

After EVERY call to `webfetch`, `fetch_fetch`, `websearch`, or any tool
that retrieves content from the internet:

1. **Write the raw result to a file IMMEDIATELY** — before you analyze
   it, summarize it, write a report, or do anything else with it.
2. The file goes in `04_Validation/logs/fetched/`.
3. The filename is `<url-slug>-<date>.md` where `<url-slug>` is the URL
   with non-alphanumerics replaced by `-`, truncated to 60 chars, and
   `<date>` is the UTC date.
4. The file contains: the URL, the fetch timestamp, and the raw content
   (markdown or text, as returned by the fetch tool).
5. Then — and only then — you may analyze the content, write a report,
   or act on it.

## The pattern

```
WRONG:
  1. fetch URL
  2. analyze the content in context
  3. write a report
  4. session ends / context compacted
  5. data is GONE — next agent re-fetches

RIGHT:
  1. fetch URL
  2. write raw result to 04_Validation/logs/fetched/<slug>-<date>.md
  3. analyze the content (from the file, not from context)
  4. write a report
  5. session ends — data is on disk, next agent reads the file
```

## How to slug a URL

```
https://www.firecrawl.dev/about
  -> firecrawl-dev-about-2026-07-27.md

https://docs.firecrawl.dev/overview/introduction
  -> docs-firecrawl-dev-overview-introduction-2026-07-27.md
```

Rules:
- Strip the `https://` or `http://` prefix.
- Strip `www.`.
- Replace every non-alphanumeric char with `-`.
- Collapse consecutive `-` to a single `-`.
- Truncate to 60 chars.
- Append `-YYYY-MM-DD` (UTC date).

## What to write in the file

```markdown
# Fetched: <full URL>

> Fetched: <UTC timestamp> by <agent> (<model>)
> Tool: <webfetch | fetch_fetch | websearch>

---

<raw content as returned by the fetch tool>
```

Nothing else. No analysis, no summary, no interpretation. The raw
content only. Analysis goes in a separate report file (e.g.
`04_Validation/architecture_assessment/FIRECRAWL_INVESTIGATION_2026-07-27.md`).

## When NOT to use this skill

- When you fetch a URL and the result is empty or an error (e.g. 404).
  Log the error to the session log instead (see the `session_logger.py`
  script), but don't create a fetched-data file for a failed fetch.
- When the operator explicitly says "just look it up, don't write a
  file." Respect the operator's instruction. But note in the session
  log that the fetch was not persisted, so the next agent knows.

## The hard truth

If you fetch data and don't persist it, and the session ends, **you
have wasted the operator's time and network bandwidth.** The next agent
has to re-fetch the same URL. That is a DD-071 (Work-Claim Without
Evidence) failure: you claimed to have fetched the data, but there is
no evidence on disk. The engine you just built detects this exact
pattern in the texts it audits. Don't reproduce it in the build session.