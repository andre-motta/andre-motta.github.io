# Repository instructions

## Purpose and context

This repository contains Andre Lustosa's personal website at `https://alustos.us`.
Read [README.md](README.md) for the current implementation and
[docs/SDLC.md](docs/SDLC.md) for the development workflow and project profile
before planning or delegating work. Apply that workflow to design, content, code,
and releases.

The site is a static Astro build with Markdown content, hosted on GitHub Pages at
`alustos.us`. The old Pelican implementation is preserved on `origin/legacy`.

## Private project context

When present, read [.wiki/README.md](.wiki/README.md) before planning content or
changing project decisions, then load only the relevant linked notes. This
gitignored local wiki preserves Andre's internal rationale, source provenance,
editorial feedback, approvals, past initiative records, and reusable prompts. It
is intentionally absent from ordinary clones. If it is missing, use the public
repository and verified sources; do not invent the missing rationale or
reconstruct private context.

Update the wiki when Andre supplies a correction, internal explanation, approval,
or durable preference. Record its source/date, distinguish fact from interpretation
or proposed work, and mark superseded conclusions. Preserve useful internal
rationale across topics, not just the latest example. Keep reusable prompts free
of embedded private facts, with private context supplied separately when used.

For substantive new writing or article revision, use the local
[website-content skill](.wiki/skills/website-content/SKILL.md) when available. It
routes to research, drafting, and editorial review prompts. This is a local skill
entrypoint referenced here, not an automatically installed skill. The tracked
[linkedin-posts skill](.claude/skills/linkedin-posts/SKILL.md) prepares LinkedIn
posts from published articles.

The wiki is context for agents, not publication input or authorization for external
actions. Never stage it, force-add it, copy it into `src/` or `public/`, or include
it in build artifacts. Private knowledge may explain a decision without being
safe to describe publicly. Inspect the generated artifact for this boundary.

## Approved design baseline

Andre approved the site's design and implementation on September 6, 2026. Keep
the Astro architecture, editorial visual style, AL branding, responsive layouts,
and system-aware light/dark behavior as the baseline. Content work is not a reason
to redesign the site or replace its stack. Make requested changes and necessary
fixes within that baseline; get Andre's direction before discretionary redesign.
Design approval and article approval do not authorize committing or publishing.

## Roles and decision ownership

Andre is the CTO and owns product goals and the personal facts and opinions
published in his name. The Claude Code session is the orchestrator: architect,
lead designer, content editor, and final reviewer. It owns the brief, visual
direction, editorial voice, task allocation, integration, and Git operations.

Initiatives follow the installed `agent-sdlc` skill (see
[docs/SDLC.md](docs/SDLC.md)). Its workflows run the `sdlc-engineer` role for
implementation and the `sdlc-reviewer` role for independent review. Research-heavy
article drafting may go to a subagent; the orchestrator edits every draft before
presenting it for Andre's review. Agents inherit the session model; override the
model or effort for a stage only with a concrete reason. Small editorial,
content, or process changes use the fast lane with no subagents.

## Collaboration rules

- Give each delegated assignment an objective, relevant context, owned paths,
  dependencies, acceptance criteria, checks, and risk tier. Point agents without
  inherited context at this file and `docs/SDLC.md`.
- Pass project constraints to workflows through their `rules` argument, as listed
  in the profile. Keep long specs in a scratchpad file and pass a pointer.
- One writer owns a file at a time. Item work happens in its own worktree under
  the profile's worktree root, never in Andre's checkout. The orchestrator owns
  integration and all Git mutations outside item worktrees.
- Review the actual diff and evidence before accepting an agent's completion report.
- Resolve routine choices autonomously within the user's scope. Batch material
  decisions for Andre as structured questions with a recommended option.

## Site and content requirements

- `CLAUDE.md`, `README.md`, `docs/`, and `.claude/` are repository material, never
  website content. Keep them out of generated pages, static assets, and deployment
  artifacts. Preserve this exclusion if the generator or deployment changes.
- Preserve `alustos.us`, existing URLs, feed paths, and the public CV URL unless the
  agreed design includes a deliberate migration and compatibility plan.
- Keep the private CV repository as the canonical source for the integrated web
  CV and downloadable PDF. Import `cv.md` through a validated public-field adapter
  and preserve `/extra/Andre_Motta_Resume.pdf`. Never stage private source files,
  generated CV data, the copied PDF, or credentials. Exclude private YAML contact
  fields from the web profile. Fetch both inputs from the same source checkout.
- The orchestrator edits content for accuracy, specificity, coherence, and
  Andre's voice. Do not invent personal experience, credentials, metrics,
  quotations, or positions. Flag claims needing the user's input; keep unverified
  drafts out of publication.
- Anonymize Red Hat workplace material into transferable lessons, removing
  internal identifiers, links, names, private metrics, and identifiable incidents
  or architecture. Public employer/title and approved CV facts may appear in the
  biography. Named public upstream work may be linked and attributed accurately;
  distinguish merged changes, open proposals, reviews, and team contributions.
- Keep private research, provenance, and process records out of tracked files,
  using the ignored `.wiki/` or an external private location. GitHub issues and
  PRs carry public-safe scope and evidence only.
- New articles remain `draft: true` until the user approves them. Show drafts only
  through an explicit local preview mode and exclude them from production routes,
  feeds, indexes, and assets.
- Write plainly and never use em dashes. Use module-level Python imports unless
  function-level imports are necessary, such as to avoid a circular dependency.
- For visual changes, review responsive layouts, keyboard access, semantic HTML,
  readable contrast, and representative content in a browser. Match testing to the
  change rather than adding tests that merely repeat the implementation.
- For changes to templates, styles, or layout, supply desktop and mobile
  screenshots before Andre's final approval, plus GIF/video evidence for any
  introduced motion.
- Keep the dependency lockfile with the manifests. Use `npm ci` for reproducible
  installs, review dependency changes, and keep Dependabot configured to propose
  npm and GitHub Actions updates. Never treat a lockfile or clean vulnerability
  scan as a guarantee of safety, and do not auto-merge dependency updates.

## Git and publication

- `legacy` preserves the pre-Astro `master` snapshot at
  `d4f25097545a03b49643c725a2626591f4399b18`. Do not advance, delete, or force-push
  that branch without an explicit user request. This is a workflow convention,
  not server-enforced branch protection.
- Use `claude/<short-topic>` branches unless the user specifies otherwise. Never
  switch branches in Andre's checkout; use worktrees under the profile's worktree
  root.
- Before every commit, show the full proposed commit message and obtain the
  user's approval. Include a title, a blank line, a one-line descriptive body,
  and then any trailers. Commit with `git commit -s`; do not manually add the
  `Signed-off-by` trailer. Local commits in item worktrees made by workflows are
  integration scaffolding; the commits that reach `master` follow this rule.
- If adding co-authorship, use `Co-Authored-By: Claude <model> <noreply@anthropic.com>`
  with the actual model substituted and no context-window annotation.
- Approved exception to the skill's PR default (Andre, September 26, 2026): once
  Andre signs off on a change, push it directly to `master` without opening a PR.
  Without that sign-off, do not push `master`. Pushing `master` triggers
  production deployment, so verify the deploy afterward. Tags, releases, and
  repository settings changes still need their own authorization.
- If a sandboxed authenticated command cannot access the real credential store or
  network, scope an escalation to that command. Never expose credentials in logs.

## Completion

Follow the proportional verification and handoff criteria in `docs/SDLC.md`.
Report what changed, the evidence checked, remaining limitations, and the exact
Git/publication state. Distinguish prepared work from committed, pushed, and
successfully deployed work.
