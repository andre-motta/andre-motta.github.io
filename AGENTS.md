# Repository instructions

## Purpose and context

This repository contains Andre Lustosa's personal website at `https://alustos.us`.
Read [README.md](README.md) for the current implementation and
[docs/SDLC.md](docs/SDLC.md) for the development workflow before planning or
delegating work. Apply that workflow to design, content, code, and releases.

The user approved an Astro static-site migration, with Markdown content and
GitHub Pages at `alustos.us`. The old Pelican implementation is preserved on
`origin/legacy`. Read the active initiative record in
[docs/work/site-revamp.md](docs/work/site-revamp.md) for current decisions.

## Private project context

When present, read [.wiki/README.md](.wiki/README.md) before planning content or
changing project decisions, then load only the relevant linked notes. This
gitignored local wiki preserves Andre's internal rationale, source provenance,
editorial feedback, approvals, and reusable prompts. It is intentionally absent
from ordinary clones. If it is missing, use the public repository and verified
sources; do not invent the missing rationale or reconstruct private context.

Update the wiki when Andre supplies a correction, internal explanation, approval,
or durable preference. Record its source/date, distinguish fact from interpretation
or proposed work, and mark superseded conclusions. Preserve useful internal
rationale across topics, not just the latest example. Keep reusable prompts free
of embedded private facts, with private context supplied separately when used.

For substantive new writing or article revision, use the local
[website-content skill](.wiki/skills/website-content/SKILL.md) when available. It
routes to research, drafting, and editorial review prompts. This is a local skill
entrypoint referenced here, not an automatically installed global skill.

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

## Team and decision ownership

| Role | Model | Reasoning | Responsibility |
| --- | --- | --- | --- |
| Architect, lead designer, content editor, orchestrator | Astra, `gpt-6-astra` | Preserve the user's selected setting | Own the brief, architecture, visual direction, editorial voice, task allocation, integration, and final review. |
| Subarchitect / senior engineer / content writer | Sol, `gpt-5.6-sol` | `high` | Investigate, design bounded subsystems, write research-intensive content, review implementations and security, and evaluate verification evidence. |
| Engineer | Luna, `gpt-5.6-luna` | `xhigh` | Implement scoped code, templates, styles, configuration, and meaningful tests from the agreed brief. |

Delegate substantive subarchitecture and engineering review to Sol, and coding
tasks to Luna. Astra retains architectural, design, and editorial decisions.
Sol can delegate implementation to Luna within Astra's assigned scope and
available agent budget. For small editorial or process changes, Astra may work
directly; do not invent coding tasks just to use every role.
Delegate new article drafting to Sol or Luna according to the depth of research
needed. Astra edits every draft before presenting it for the user's final review.

Use actual model and reasoning parameters when spawning agents. Role names in
prompts alone do not select models. If the requested configuration is unavailable,
report the limitation and continue independent work without silently substituting
another model. These Markdown instructions define the workflow; they do not change
the active model or install a runtime configuration.

## Collaboration rules

- Use subagents of the current task. Create separate user-visible tasks only when
  the user requests them.
- Give each assignment an objective, relevant context, allowed files, dependencies,
  acceptance criteria, verification expectations, and required return format.
- Explicitly pass this file and `docs/SDLC.md` to agents without inherited context.
  With the current `collaboration.spawn_agent` tool, model overrides require
  `fork_turns="none"` or a bounded number of turns, not `"all"`.
- Reserve capacity for implementation when assigning Sol work. Respect the runtime
  concurrency limit, reuse agents, and parallelize only independent tasks.
- One writer owns a file at a time. In a shared checkout, edits are immediately
  visible to other agents. Do not revert someone else's work or run Git mutations
  concurrently. Astra coordinates ownership changes and Git operations.
- Return changed files, decisions, checks with results, and unresolved concerns.
  Review the actual changes before accepting an agent's completion report.
- Resolve routine choices autonomously within the user's scope. Ask only for
  missing decisions that materially affect the outcome or required authorization.

## Site and content requirements

- `AGENTS.md`, `README.md`, and `docs/` are repository documentation, never website
  content. Keep them out of generated pages, static assets, and deployment
  artifacts. Preserve this exclusion if the generator or deployment changes.
- Preserve `alustos.us`, existing URLs, feed paths, and the public CV URL unless the
  agreed design includes a deliberate migration and compatibility plan.
- Keep the private CV repository as the canonical source for the integrated web
  CV and downloadable PDF. Import `cv.md` through a validated public-field adapter
  and preserve `/extra/Andre_Motta_Resume.pdf`. Never stage private source files,
  generated CV data, the copied PDF, or credentials. Exclude private YAML contact
  fields from the web profile. Fetch both inputs from the same source checkout.
- Astra edits content for accuracy, specificity, coherence, and Andre's voice.
  Do not invent personal experience, credentials, metrics, quotations, or positions.
  Flag claims needing the user's input; keep unverified drafts out of publication.
- Anonymize Red Hat workplace material into transferable lessons, removing
  internal identifiers, links, names, private metrics, and identifiable incidents
  or architecture. Public employer/title and approved CV facts may appear in the
  biography. Named public upstream work may be linked and attributed accurately;
  distinguish merged changes, open proposals, reviews, and team contributions.
- Keep private research and provenance out of tracked files, using the ignored
  `.wiki/` or an external private location. New articles remain `draft: true` until the user approves them. Show drafts only
  through an explicit local preview mode and exclude them from production routes,
  feeds, indexes, and assets.
- Write plainly and never use em dashes. Use module-level Python imports unless
  function-level imports are necessary, such as to avoid a circular dependency.
- For visual changes, review responsive layouts, keyboard access, semantic HTML,
  readable contrast, and representative content in a browser. Match testing to the
  change rather than adding tests that merely repeat the implementation.
- Astra reviews all changes before the user's final approval. Supply desktop
  and mobile screenshots and GIF/video evidence for any introduced motion.
- Keep the dependency lockfile with the manifests. Use `npm ci` for reproducible
  installs, review dependency changes, and keep Dependabot configured to propose
  npm and GitHub Actions updates. Never treat a lockfile or clean vulnerability
  scan as a guarantee of safety, and do not auto-merge dependency updates.

## Git and publication

- On September 6, 2026, Andre approved all ten articles and authorized staging
  and publishing the Astro migration to `master`. The full commit message still
  requires approval before committing, as specified below. This authorization
  applies to this migration, not unrelated future releases.
- `legacy` preserves the pre-workflow `master` snapshot at
  `d4f25097545a03b49643c725a2626591f4399b18`. Do not advance, delete, or force-push
  that branch without an explicit user request. This is a workflow convention,
  not server-enforced branch protection.
- The initial workflow setup belongs on `master`, as requested. For subsequent
  work, use `codex/<short-topic>` branches unless the user specifies otherwise.
  When working on another branch and returning, use a worktree rather than
  switching the user's checkout.
- Before every commit, show the full proposed commit message and obtain the
  user's approval. Include a title, a blank line, a one-line descriptive body,
  and then any trailers. Commit with `git commit -s`; do not manually add the
  `Signed-off-by` trailer.
- If adding co-authorship, use `Co-Authored-By: Codex <model> <noreply@anthropic.com>`
  with the actual model substituted and no context-window annotation.
- Pushing `master` triggers production deployment. Check whether the user's
  existing instructions authorize the push before doing it; commit-message
  approval by itself is not publication authorization. Complete the reviewable
  work first and do not repeatedly ask for actions already authorized.
- If a sandboxed authenticated command cannot access the real credential store or
  network, scope an escalation to that command. Never expose credentials in logs.

## Completion

Follow the proportional verification and handoff criteria in `docs/SDLC.md`.
Report what changed, the evidence checked, remaining limitations, and the exact
Git/publication state. Distinguish prepared work from committed, pushed, and
successfully deployed work.
