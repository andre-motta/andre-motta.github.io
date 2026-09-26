# Website development workflow

This repository uses the `agent-sdlc` skill, version 0.2.3, with Claude Code.
Andre is the CTO. The Claude Code session orchestrates and owns architecture,
design, editorial review, and integration, as described in
[CLAUDE.md](../CLAUDE.md). This file is the project profile the skill reads.

## Profile

| Setting | Value |
| --- | --- |
| Skill version | `agent-sdlc` 0.2.3 (workflow based) |
| Tracker | GitHub Issues on `andre-motta/andre-motta.github.io`: one parent issue with a checklist per initiative, one issue per item, PRs or commits reference `Fixes #N`. Public-safe wording only. |
| Dependency links | Dependabot PRs; see [DEPENDENCIES.md](DEPENDENCIES.md) |
| Default branch, integration branch, upstream path | `master`. Integration branch `claude/<initiative>`. After Andre's sign-off, the orchestrator pushes directly to `master` (approved exception, below). |
| Worktree root (outside the repo) | `../andre-motta.github.io.worktrees/`; checkpoint at `../andre-motta.github.io.worktrees/CHECKPOINT.md` |
| Setup | `npm ci`, then the CV import below (or the fixture) |
| Focused checks | `npm run check`; `python scripts/test_import_cv.py` when the importer changes; `git diff --check` |
| Integrated checks | `npm run check && npm run build && python scripts/verify_site.py --output output`, plus the preview build and verifiers when drafts or lectures change, and `python scripts/verify_lecture.py` for lecture changes |
| Local CI reproduction | What pull requests run: `npm ci && npm audit --audit-level=high && python scripts/test_import_cv.py && python scripts/import-cv.py --fixture --output .generated/cv.json && npm run check && npm run build && python scripts/verify_site.py --output output --allow-missing-cv` |
| Required platforms | Linux with Node.js 22.12+ and Python 3.11+. Browser checks in current Chromium at desktop and 390px mobile widths. |
| Default evidence level | `automated`. Visual changes add desktop and mobile screenshots, plus GIF/video for motion. |
| Resource limits (`rules` arg) | See [Workflow rules](#workflow-rules) |
| Upstream path and approved exceptions | Direct push to `master` after Andre's sign-off; no PR required |
| Publication side effects | A push to `master` deploys production through `.github/workflows/site.yml` |

Adoption: Andre approved migrating from the Codex-based 0.1.0 workflow on
September 26, 2026. Reconciled rules:

- The Astra, Sol, and Luna model roles are replaced by the Claude Code
  orchestrator and the skill's `sdlc-engineer` and `sdlc-reviewer` roles. Agents
  inherit the session model.
- `docs/work/` initiative records are retired. Git and GitHub Issues are the
  record; past records moved to the private wiki. Public operational knowledge
  from them now lives in [LECTURES.md](LECTURES.md) and [DISCOVERY.md](DISCOVERY.md).
- The skill defaults to no screenshots. This profile keeps desktop and mobile
  screenshots, plus motion recordings, for visual changes.
- The skill defaults to PRs for upstream changes. Andre approved direct pushes
  to `master` once he signs off on a change. Dependabot and external
  contributions still arrive as PRs.
- Branches use `claude/<topic>` instead of `codex/<topic>`. `AGENTS.md` became
  `CLAUDE.md`, and the LinkedIn skill moved to `.claude/skills/`.

## Lanes

Most work on this site is fast lane: an article edit, a copy fix, a dependency
review, a small style fix. The orchestrator does it directly, runs the checks
from the table below, shows the commit message, and pushes after sign-off.

Use the skill's workflow lifecycle (discover, design, deliver, review, accept)
for multi-item or risky work: a new site section, routing or deployment changes,
CV import changes, or several articles at once. Design starts with a thin slice
Andre can preview locally.

Articles follow the local website-content skill when present. Drafts stay
`draft: true`; Andre approves each article individually. The orchestrator
edits every delegated draft before Andre sees it.

## Workflow rules

Pass these as the workflows' `rules` argument:

```text
- Read CLAUDE.md and docs/SDLC.md first. Never read, copy, or stage .wiki/ unless the assignment says so; never put its content in src/, public/, or output.
- Never stage .cv-source/, .generated/, public/extra/Andre_Motta_Resume.pdf, output/, or output-preview/.
- Do not change the approved design baseline, URLs, feed paths, or the CV URL outside the item spec.
- New or changed articles keep draft: true unless the spec says Andre approved them.
- No em dashes in prose or commit messages. Module-level Python imports.
- Use npm ci, never npm install, unless the item changes dependencies.
- Never push, open PRs, or touch remote branches. The orchestrator publishes.
- Run one build at a time per worktree; builds are small, no other resource limits.
```

## Checks by change

| Change | Expected evidence |
| --- | --- |
| Process or documentation only | Read for consistency; verify local links, commands, and Git rules; run `git diff --check`. No site build required when build inputs are unchanged. |
| Content | Review facts, voice, metadata, links, and rendered pages; build the site. |
| Templates, styles, or behavior | Build; inspect representative desktop and mobile pages, keyboard navigation, focus, contrast, overflow, and links; exercise changed behavior; screenshots. |
| Configuration, dependencies, or deployment | Run relevant build/configuration checks; inspect generated paths, feeds, `CNAME`, and CV handling; assess credentials and deployment permissions. |

Setup and validation from the repository root:

```bash
npm ci
python scripts/test_import_cv.py
python scripts/import-cv.py --source-dir ../personal_cv --output .generated/cv.json --pdf-destination public/extra/Andre_Motta_Resume.pdf
npm run check
npm run build
python scripts/verify_site.py --output output
```

Use `npm ci` with the committed lockfile, not a floating dependency install. The
CV adapter uses the Python standard library; there is no Python package
installation step. Keep `package.json` and `package-lock.json` together. See
[dependency maintenance](DEPENDENCIES.md) for update policy and CI security.

For a local draft preview:

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

## Release

The orchestrator checks the final diff, acceptance criteria, review findings, and
design and editorial quality. Confirm the branch and staged file list, then
present the full commit message for approval under `CLAUDE.md`. After Andre signs
off, commit with `-s` and push to `master`.

Before a push to `master`, account for the production impact:

- Repository material (`CLAUDE.md`, `README.md`, `docs/`, and `.claude/`) must
  never be included in website pages or deployment artifacts. Astro generates
  explicit routes from `src/` and copies only intentional static assets from
  `public/`; deployment uploads only `output/`, and `scripts/verify_site.py`
  rejects these paths. Check that this remains true after build or hosting changes.
- `.github/workflows/site.yml` deploys on pushes to `master` and also supports
  manual dispatch and the `cv-updated` repository-dispatch event.
- The deploy requires a usable `PERSONAL_CV_REPO_TOKEN` secret and Pages access;
  the workflow's reference alone does not prove either is configured correctly.
- `public/CNAME` must produce `alustos.us` in the published artifact.
- Existing article, page, feed, and CV paths need to keep working or have an
  intentional migration plan.

After publication, watch the Actions run in the background and check the affected
live pages, navigation, and assets. If verification is unavailable, report
deployment as unverified rather than complete. For a release failure, identify
the last working release and prepare a focused correction or revert for sign-off.
Do not reset `master` or move `legacy` as an automatic rollback.

`legacy` is a source snapshot, not a frozen deployment artifact: the original
Pelican build used a separately maintained CV and dependencies with minimum
version constraints. Rebuilding that branch later is not guaranteed to reproduce
every byte of the original published site.

## Close and resume

Work is ready when the acceptance criteria are met, relevant checks pass,
material review findings are resolved, and the orchestrator has completed the
design and editorial review appropriate to the change. Release completion
additionally requires the push and successful deployment verification.

For initiatives, keep the uncommitted checkpoint file at the worktree root,
rewritten at handoffs. On resume, reconcile it with git and GitHub Issues. End
with the result, verification, limitations, and whether work is prepared,
committed, pushed, or deployed.
