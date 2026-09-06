# Website development workflow

## Operating model

Andre owns product goals and the personal facts and opinions published in his
name. Astra is the architect, lead designer, content editor, and orchestrator.
Sol on `high` supplies subarchitecture, security review, and research-intensive
content writing. Luna on
`xhigh` implements scoped engineering tasks. Exact model IDs and standing rules
are in [AGENTS.md](../AGENTS.md).

The normal flow is:

```text
Andre's goal
    -> Astra: brief, architecture, design and editorial direction
    -> Sol: technical investigation, work breakdown and acceptance criteria
    -> Luna: implementation and focused verification
    -> Sol: technical review and verification assessment
    -> Astra: integrated design, content and release review
    -> approved commit and authorized publication
```

Astra can dispatch Luna directly for a well-defined task. Sol can coordinate Luna
within an assigned subsystem. All work returns to Astra for integration. These
are responsibilities, not a requirement to launch a new agent at every stage.
Keep one concise work record for substantial initiatives; small changes can use
the task conversation. Do not require separate documents or human approvals for
each stage when the user's existing brief is sufficient.

## 1. Frame the work

Astra turns the user's goal into a brief covering:

- Audience, intended outcome, scope, and explicit exclusions.
- User journeys and content needs, including facts or assets still needed.
- Constraints, acceptance criteria, and observable success measures.
- Open decisions, assumptions, dependencies, and publication intent.

Inspect the current implementation before estimating or allocating work. If the
goal is not yet supplied, establish process and record known context without
inventing the site's future direction. Keep independent work moving while
clarifying consequential unknowns.

For larger initiatives, maintain `docs/work/<topic>.md` using the compact format
below. Record only public-safe project information, since this repository is
public. Update it when scope changes and at meaningful handoffs.

```markdown
# <Initiative>

## Brief
Audience, outcome, scope, exclusions, constraints, acceptance criteria.

## Decisions
Architecture, design and editorial choices; rationale; open questions.

## Work items
Owner/model, allowed files, dependencies, acceptance criteria, status.

## Evidence
Commands and results, browser observations, review findings and resolution.

## Release and handoff
Git state, authorization, deployment result, remaining work, next action.
```

## 2. Define architecture, design, and content

Astra owns information architecture, visual hierarchy, typography, spacing,
navigation, responsive behavior, and editorial voice. Establish representative
pages and content before scaling implementation. Astra reviews each result before the
user performs final approval. Provide desktop/mobile screenshots and GIF/video
evidence for any motion. Never mistake a local preview for publication approval. Design should make Andre's
work and writing easy to understand and navigate.

Sol investigates technical feasibility, build and hosting constraints, URL
compatibility, maintenance cost, and failure modes. Return a recommendation with
tradeoffs and a bounded implementation breakdown. Astra resolves decisions that
span subsystems or change the user experience. Record significant stack, routing,
or deployment decisions and migration consequences in the initiative record.

For content, distinguish verified facts, author-provided opinions, and open
questions. Cite sources for external factual claims when appropriate. Preserve
the meaning of Andre's statements while improving structure and clarity. Keep
new articles in `src/content/articles/` with `draft: true` until the user approves
them. Use the explicit local preview to review drafts. Production routes, indexes,
feeds, and assets must exclude them.

## 3. Delegate implementation

Use this assignment contract for Sol and Luna:

```text
Role / model / reasoning:
Objective and user outcome:
Read first: AGENTS.md, docs/SDLC.md, relevant brief and source files
Decisions already made and constraints:
Allowed files and areas outside scope:
Dependencies and interface agreements:
Acceptance criteria:
Required verification:
Return: changed files, rationale, evidence, unresolved concerns
Git authority: no commit, push, checkout, merge, or reset; Astra coordinates Git
```

Luna implements within the agreed scope and runs the applicable checks. Escalate
design ambiguities to Sol or Astra instead of silently changing architecture.
Sol reviews implementation and assigns concrete corrections back to Luna.

Parallel assignments need disjoint file ownership and stable interfaces. Reserve
an available slot for a worker before asking Sol to delegate. With four available
slots, Astra plus one Sol plus up to two Luna agents is a possible allocation,
not a fixed requirement. If capacity is full, queue work or reuse an agent. Stop
or redirect obsolete assignments when the brief changes.

## 4. Verify and review

Luna supplies implementation evidence, Sol evaluates technical correctness, and
Astra evaluates the integrated result against the brief. Reviewers inspect the
diff and evidence, not just the agent summary. Record findings with affected
files, user impact, and a concrete correction. Resolve material findings before
declaring the work ready.

Select checks by what changed:

| Change | Expected evidence |
| --- | --- |
| Process or documentation only | Read for consistency; verify local links, commands, model settings, and Git rules; run `git diff --check`. No site build required when build inputs are unchanged. |
| Content | Review facts, voice, metadata, links, and rendered pages; build the site. |
| Templates, styles, or behavior | Build; inspect representative desktop and mobile pages, keyboard navigation, focus, contrast, overflow, and links; exercise changed behavior. |
| Configuration, dependencies, or deployment | Run relevant build/configuration checks; inspect generated paths, feeds, `CNAME`, and CV handling; assess credentials and deployment permissions. |

Current setup and validation from the repository root:

```bash
npm ci
python scripts/test_import_cv.py
python scripts/import-cv.py --source-dir ../personal_cv --output .generated/cv.json --pdf-destination public/extra/Andre_Motta_Resume.pdf
npm run check
npm run build
python scripts/verify_site.py --output output
```

Use `npm ci` with the committed-intended lockfile, not a floating dependency
install. The CV adapter uses the Python standard library; there is no Python
package installation step. Keep `package.json` and `package-lock.json` together.
See [dependency maintenance](DEPENDENCIES.md) for update policy and CI security.

For a local draft preview, use:

```bash
npm run dev:preview -- --host 127.0.0.1 --port 4321
```

For a static preview artifact, use `npm run build:preview` and
`python scripts/verify_site.py --output output-preview --preview`. Keep previews
local, including screenshots and recordings. Never upload the draft preview as
the Pages artifact. Only the normal production build belongs in `output/`.

If the private CV is unavailable, `python scripts/import-cv.py --fixture --output
.generated/cv.json` uses a synthetic test fixture. A fixture build checks the
rendering path but is not a releasable CV. Pass `--allow-missing-cv` to the artifact
verifier only for that fixture build. Restore the real CV before user review or
release. Never fabricate a downloadable PDF to make a release check pass.

The deployment fetches `cv.md` and `Andre_Motta_Resume.pdf` from the same checkout
of `andre-motta/personal_cv@main`. The adapter discards private YAML fields and
validates approved professional sections. Install dependencies before fetching
that source; remove the private checkout after import and before the Astro build.
Untrusted pull requests and Dependabot builds receive only the public fixture.

Never stage `.cv-source/`, `.generated/`, or copied PDFs. Review the staged paths:

```bash
git diff --cached --name-only -- .cv-source .generated public/extra/Andre_Motta_Resume.pdf content/extra/Andre_Motta_Resume.pdf
```

Do not add a test suite for trivial reversible changes or claim checks that were
not run. Once appropriate checks pass, repeat them only for a new change, failure,
or unresolved concern. If the stack changes, update these commands and evidence
requirements in the same work.

## 5. Release

Astra checks the final diff, acceptance criteria, Sol's technical findings, and
design/editorial quality. Confirm the active branch and staged file list, then
present the full commit message for approval under `AGENTS.md`. After approval,
commit with `-s`. Keep commits coherent and describe the resulting behavior.

Before an authorized push to `master`, account for the production impact:

- Repository documentation (`AGENTS.md`, `README.md`, and `docs/`) must never be
  included in website pages or deployment artifacts. Astro generates explicit routes
  from `src/` and copies only intentional static assets from `public/`; deployment
  uploads only `output/`, keeping these documents outside the published site. Check that this remains true after build or hosting changes.
- `.github/workflows/site.yml` deploys on pushes to `master` and also supports
  manual dispatch and the `cv-updated` repository-dispatch event.
- The deploy requires a usable `PERSONAL_CV_REPO_TOKEN` secret and Pages access;
  the workflow's reference alone does not prove either is configured correctly.
- `public/CNAME` must produce `alustos.us` in the published artifact.
- Existing article, page, feed, and CV paths need to keep working or have an
  intentional migration plan.

After publication, check the Actions result and the affected live pages,
navigation, and assets. If verification is unavailable, report deployment as
unverified rather than complete. For a release failure, identify the last working
release and prepare a focused correction or revert for the applicable commit
approval. Do not reset `master` or move `legacy` as an automatic rollback.

`legacy` is a source snapshot, not a frozen deployment artifact: the workflow
used a separately maintained CV and dependencies with minimum version
constraints in the original Pelican build. Rebuilding that branch later is not guaranteed to reproduce every
byte of the original published site.

## 6. Close and resume

Work is ready when the acceptance criteria are met, relevant checks are recorded,
material review findings are resolved, and Astra has completed the design and
editorial review appropriate to the change. Release completion additionally
requires the authorized push and successful deployment verification.

End with the result, verification, limitations, and whether work is prepared,
committed, pushed, or deployed. Keep the work record current so a later session
can resume from decisions and evidence rather than reconstructing the conversation.

## Codex documentation

Repository guidance follows the official
[AGENTS.md discovery mechanism](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
Model selection must use supported runtime controls, as described in the official
[subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).
The role assignments and lifecycle above are this project's policy, chosen by
Andre, rather than defaults imposed by Codex.
