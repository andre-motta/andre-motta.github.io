# Website revamp

## Brief

Build a personal website that reflects Andre Lustosa's work as a principal
software engineer and team lead: strong design, useful navigation, substantial
technical writing, and an up-to-date web CV with a PDF download.

The audience includes engineering peers, upstream collaborators, prospective
teammates, and readers interested in software foundations and technical
leadership. Prioritize the work and the writing over generic portfolio claims.

## Decisions

- User approved Astro on September 6, 2026. Generate a static site for GitHub
  Pages at `alustos.us`. The mention of GitLab hosting was corrected by the user.
- Preserve the current PDF URL, article URLs, About URL, and feed paths.
- Use the private CV as the canonical source. Import only approved public fields
  into the web CV; keep the source, private header data, and credentials out of
  the public repository and deployed artifact.
- Visual direction: confident editorial typography, crisp neutral surfaces,
  restrained red accents, generous spacing, and deliberate light/dark themes.
- Follow the system color preference on first visit; use light when no preference
  is available. A visitor's explicit theme selection may override the system.
- Astra approves architecture, design, content, and integration before the user
  performs final approval. Provide desktop/mobile screenshots, plus GIF/video
  evidence for any animation or transition introduced.
- New writing remains draft content for local review until individually approved. Production builds must
  exclude drafts, workflow documentation, and private research material.
- No commits, pushes, or publication until the user explicitly requests them and
  the relevant approval requirements are met.

## Work items

| Owner | Scope | Status |
| --- | --- | --- |
| Astra | Architecture, design direction, CV/editorial integration, final review | Design and all ten articles approved |
| Sol / high | Public contribution research since June 2025 and sourced articles | Complete; all ten articles approved |
| Sol / high | Generalized engineering and leadership essays from work records | Reviewed and consolidated into the final slate |
| Luna / xhigh | Astro implementation, CV import, responsive layouts, validation | Implemented and verified |

## Content policy

Name and link public upstream contributions with accurate attribution and status.
Distinguish authorship, review, and team work. Open proposals are not merged work.
State the observation date when discussing changing contribution status.

Red Hat workplace material must be generalized into transferable lessons. Do not
publish internal identifiers, URLs, coworkers or customer names, private metrics,
identifiable incident details, unpublished plans, or internal architecture.
Public employer/title information and the approved CV biography remain useful
context. Private provenance records stay outside tracked files and published artifacts.

The user explicitly identified `opendatahub-io/openshell` as the Red Hat-maintained
midstream of `NVIDIA/OpenShell` for secure downstream builds. This public
relationship may be named and explained; distinguish midstream integration from
upstream contributions and continue excluding private implementation details.

Andre confirmed that he is a maintainer of `opendatahub-io/agentic-ci`. Use
"Maintainer" on the project page and that context in relevant articles.
He also confirmed his role as midstream maintainer of
`opendatahub-io/openshell`; this does not imply maintainership of NVIDIA upstream.

## Initial review evidence

This records the initial review before the final article feedback below.

- Original source snapshot: `origin/legacy` at
  `d4f25097545a03b49643c725a2626591f4399b18`.
- Astro content collections and GitHub Pages deployment verified against official
  [content documentation](https://docs.astro.build/en/guides/content-collections/)
  and [hosting documentation](https://docs.astro.build/en/guides/deploy/github/).
- Fresh `npm ci` with dependency lifecycle scripts disabled: passed; 279 packages
  audited with zero known vulnerabilities at verification time.
- `npm run check`: zero errors, warnings, or hints across 26 files.
- CV importer: 16 tests passed, including private header exclusion, invalid
  inputs, symlink rejection, destination aliases, partial writes, and cleanup.
- Production build and artifact verifier passed. All 11 draft routes and their
  feed/index references are excluded; repository documentation and private
  intermediates are excluded; original routes, CNAME, and PDF are present.
- Preview build and verifier passed with all 11 drafts plus the original welcome
  article. The integrated Projects page contains 11 projects.
- A separate public-fixture build passed without access to the private CV or PDF.
- Atom XML parsed successfully: one production entry and 12 preview entries;
  category feeds have distinct identities.
- Browser checks covered six page types at desktop and mobile widths, archive
  search and topic filtering, keyboard skip navigation, system theme changes,
  explicit preference persistence, JavaScript-disabled dark rendering, and PDF
  download. All 11 new articles fit widths of 320, 390, and 768 pixels.
- Astra inspected desktop/mobile screenshots, article layouts, the web CV,
  About, Projects, and the dark homepage. No animation was introduced.
- Sol's verifier mutation checks rejected draft leakage, documentation, symlinks,
  unsafe JavaScript URLs, and local path traversal. Material findings were fixed.
- Security settings on GitHub remain unchanged. Enabling Dependabot security
  update PRs and hardening repository-level Actions/secret settings remain
  proposed release follow-ups. Local Dependabot version-update configuration,
  full Action SHA pins, lockfile, and disabled install scripts are prepared.
- Editorial coverage and consolidation are recorded in
  [content-review.md](content-review.md). Raw research remains outside tracked files.

## Release and handoff

Working branch: `codex/site-revamp`. Andre approved the design and all ten articles,
then explicitly authorized staging and publishing the migration to `master`.
Prepare the complete staged change and obtain full commit-message approval before
committing. Publish by fast-forwarding master without rewriting legacy history.
The initial `legacy` snapshot is the only remote change made before this release.

## Final feedback follow-up, September 6, 2026

Andre approved the design and implementation. AGENTS.md preserves that baseline
and points future agents to an intentionally gitignored `.wiki/` with context,
provenance, editorial decisions, reusable prompts, and a local content skill.
The artifact verifier rejects `.wiki` paths in generated output.

Five articles are approved. Three essays were rewritten and two received requested
additions; Astra reviewed and integrated all five revisions for final user review.
The compatibility-matrix article was withdrawn. The welcome route redirects to
About, old introduction/meta/general archives redirect to Writing, and the legacy
General feed remains valid and empty.

Current verification: Astro check passed across 32 files with zero errors, warnings,
or hints. Production and preview builds and artifact verification passed. The
production main feed has five entries; the preview has ten with five draft markers.
Neither includes the old welcome article. The withdrawn article and private wiki
are absent from the generated artifacts. The local content skill passed validation,
wiki files are ignored and untracked, and git diff --check passed.

This supersedes the earlier article counts and pending-design status. No commit,
push, or deployment was performed for these revisions.

## Release authorization, September 6, 2026

Andre approved all five revised articles and authorized staging a new commit and
publishing the new website on master. All ten articles now have `draft: false`.
The legacy Pelican templates, configuration, content, requirements, and workflow
are removed from the new tree; the original source remains in Git history and
on `legacy`. Remote master and legacy were both verified at the preserved
`d4f25097545a03b49643c725a2626591f4399b18` revision before staging. GitHub Pages
uses workflow deployment with `alustos.us`, and the required CV secret name exists.
Secret-name presence does not prove the token's current validity; the deployment
run must verify authenticated CV retrieval and publication.

Release preparation checks passed after all approvals: Astro check reports zero
errors, warnings, and hints across 32 files; the production build and artifact
verifier pass, with all ten articles in the main Atom feed and no draft markers.
The staged migration has no Pelican runtime, theme, or content tree and excludes
private wiki, CV source/intermediates, copied PDF, and generated site output.
The staged whitespace check passes. Commit and deployment remain pending the
required full commit-message approval and subsequent execution.
