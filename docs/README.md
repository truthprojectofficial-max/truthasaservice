# OGIR Landing Page — GitHub Pages

> This folder is published via GitHub Pages at ordergetitright.com
> (CNAME file maps the custom domain). Free hosting, free HTTPS.
>
> To publish: push to the `gh-pages` branch or enable Pages in
> repo settings → Pages → Source → main /docs folder.
>
> The landing page is a single static HTML file. No build step.
> No JavaScript framework. Just HTML + CSS. Loads from any CDN edge.

## What's here

- `index.html` — the landing page (dark theme, matches the OGIR UI)
- `CNAME` — maps `ordergetitright.com` to GitHub Pages
- `favicon.ico` — the OGIR icon (copy from src-tauri/icons/)
- `robots.txt` — allows all crawlers

## What the landing page shows

1. Hero: "Order Get It Right — Truth as a Service"
2. What it is: forensic deception-detection for business documents
3. How it works: 4-gate pipeline (Deception → BBFB → Optionality → Decision)
4. Calibration: 134 cases, 100% accuracy, F1=1.0
5. Trust: Merkle chain, 40,870+ blocks, air-gapped, pure stdlib Python
6. Download: links to GitHub Releases (signed Tauri binary, when available)
7. Open source: MIT licensed, link to GitHub repo
8. Privacy: link to privacy policy
9. Contact: operator email
10. Footer: copyright, jurisdiction, operator name

## To enable GitHub Pages

1. Go to: github.com/truthprojectofficial-max/truthasaservice/settings/pages
2. Source: Deploy from a branch
3. Branch: main (or gh-pages) / /docs folder
4. Custom domain: ordergetitright.com
5. Enforce HTTPS: ON
6. Save

The CNAME file in this folder tells GitHub Pages to serve at
ordergetitright.com instead of truthprojectofficial-max.github.io.