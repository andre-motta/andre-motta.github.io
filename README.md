# Andre Lustosa's website

An Astro static site for [alustos.us](https://alustos.us), hosted on GitHub Pages.
It brings together technical writing, public projects, and a readable CV with a
PDF download. The original Pelican site is preserved on `origin/legacy`.

## Development workflow

Read [AGENTS.md](AGENTS.md) and [docs/SDLC.md](docs/SDLC.md). Astra leads
architecture, design, editorial review, and orchestration. Sol on High handles
subarchitecture, content investigation, and senior/security review. Luna on xhigh
handles implementation. Current work is described in
[the revamp brief](docs/work/site-revamp.md).

Changes require editorial review and explicit release authorization under that
workflow. Repository documentation is never included in the website artifact.

## Local development

Use Node.js 22.12 or newer and Python 3.11 or newer. Python is used only for the
CV adapter and checks, with no third-party Python dependencies.

```bash
npm ci
python scripts/import-cv.py --source-dir ../personal_cv --output .generated/cv.json --pdf-destination public/extra/Andre_Motta_Resume.pdf
npm run dev:preview -- --host 127.0.0.1 --port 4321
```

Open [the local preview](http://localhost:4321). This explicit preview includes
draft articles. It must not be deployed. Use `npm run dev` to preview only content
eligible for publication.

Without access to the private CV repository, generate synthetic test data with
`python scripts/import-cv.py --fixture --output .generated/cv.json`. The fixture
contains no real CV or PDF and is intended for contributor/Dependabot checks.

## Writing

Articles live in `src/content/articles/` and use YAML metadata:

```yaml
---
title: "A specific engineering decision"
description: "The question, tradeoffs, and evidence the article develops."
date: "2026-09-06"
category: "Software Engineering"
tags: ["architecture", "reliability"]
slug: "a-specific-engineering-decision"
draft: true
featured: false
readTime: "6 min read"
---
```

Keep new writing as a draft until the user's editorial approval. Article URLs
remain `/blog/<year>/<slug>.html`. Publication dates should reflect actual
publication, rather than the date of a historical contribution discussed in an
article. Do not change an already published date or slug without a URL plan.

Write about meaningful decisions and tradeoffs. Small changes can supply evidence
for a larger argument; they do not automatically merit separate articles. Name
and link public upstream work accurately, and generalize internal Red Hat work
without identifiable details. Keep private research out of tracked files and site artifacts; the ignored
`.wiki/` preserves local context for agents.

## CV

`andre-motta/personal_cv` remains the source of truth. The build imports its
`cv.md` into validated, temporary public data for `/cv.html` and copies the PDF to
`/extra/Andre_Motta_Resume.pdf`. Both inputs come from one checkout. The import
discards the private YAML header and fails on unexpected Markdown structure.

The raw source, `.generated/` data, private checkout, and copied PDF are ignored
by Git. They must never be staged. The website includes the generated CV page and
the intentional PDF download, not the source Markdown or private fields.

## Validation and builds

```bash
python scripts/test_import_cv.py
npm run check
npm run build
python scripts/verify_site.py --output output
```

For a fixture-only build, the verifier accepts `--allow-missing-cv`. Release
validation requires the real PDF. The normal build excludes drafts. To inspect a
static draft build locally, use `npm run build:preview`, which writes
`output-preview/`, then verify it with `--output output-preview --preview`.

## Deployment and dependencies

The workflow in `.github/workflows/site.yml` builds pull requests using public
fixtures. Only trusted events on `master` can fetch the private CV and deploy.
Pushes to `master`, manual dispatch, and `cv-updated` repository dispatch retain
the existing deployment behavior. A usable read-only `PERSONAL_CV_REPO_TOKEN`
secret with access to the CV repository is required for releases.

Production builds upload only `output/`. `public/CNAME` preserves `alustos.us`.
Do not publish until the user has approved the concrete result and authorized
publication.

The Atom feed at `/feeds/all.atom.xml` and category feeds are static XML generated
with each build. Feed readers poll these files on GitHub Pages; no server process
or scheduled Action is needed. Feeds contain article summaries and links, with
the same draft visibility rules as the rest of the site.

`package-lock.json` records the dependency graph, and CI uses `npm ci`.
Dependabot proposes npm and GitHub Actions updates for review. See
[docs/DEPENDENCIES.md](docs/DEPENDENCIES.md) for the policy and the separate
repository settings needed for security updates. Repository installs disable
dependency lifecycle scripts by default through `.npmrc`; run only the explicit
project commands documented above when generating or checking the site.

## Structure

- `src/content/articles/`: Markdown writing
- `src/data/`: public profile and project descriptions
- `src/layouts/`, `src/pages/`, `src/styles/`: Astro presentation and routes
- `public/`: intentional static assets
- `scripts/`: CV import, fixtures, and artifact validation
- `docs/`: repository-only workflow and decision records

## License

Content © Andre Lustosa.
