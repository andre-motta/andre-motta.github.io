# Dependency maintenance

This site is deployed as static files without a Node.js server. Build dependencies
still run during development and CI, and the JavaScript they emit can run in a
visitor's browser. A compromised build dependency could alter the deployed
artifact or read data available to the build job.

## Reproducible installs

Commit `package.json` and `package-lock.json` together. Use `npm ci` in CI and
for release checks. It fails when the manifest and lockfile disagree and installs
the versions and integrity metadata recorded in the lockfile. Do not hand-edit
the lockfile.

The lockfile prevents ordinary version drift. It does not establish that a
package is trustworthy or free of vulnerabilities. Review dependency changes,
run the site checks, and treat `npm audit` as one source of known-vulnerability
information rather than a safety certificate.

The project `.npmrc` sets `ignore-scripts=true`, disabling dependency lifecycle
scripts during installation. Explicit commands such as `npm run build` and
`npm run check` still execute their requested scripts. Do not enable install
scripts globally to accommodate a new dependency; review the specific need first.

All site packages are build tools and belong in `devDependencies`. Add a package
only when the site needs it, and prefer the platform or Astro capability already
in use. For a dependency pull request:

1. Read the release notes and inspect changes to both manifest and lockfile.
2. Check for new package sources and install scripts.
3. Run `npm ci`, `npm run test:cv`, `npm run cv:fixture`, `npm run check`,
   `npm run build`, and `npm run verify -- --allow-missing-cv`. A release check
   uses the real CV import and does not allow the PDF to be missing.
4. Review representative rendered pages and the production artifact when the
   update can affect output.
5. Merge only after review. Dependency pull requests are never auto-merged.

## Dependabot policy

`.github/dependabot.yml` checks npm and GitHub Actions each Monday. It groups
routine npm minor and patch releases and groups routine Actions releases to keep
review volume small. npm majors remain separate because they usually need focused
migration review. Cooldowns give new routine releases time to settle. GitHub
applies cooldowns only to version updates, so security updates are not delayed by
this policy.

Once the configuration file reaches the default branch, it enables Dependabot
version updates. Dependabot alerts and Dependabot security updates are separate
repository settings. Keep both enabled so known vulnerable dependencies can
produce prompt update pull requests. Do not add `target-branch` to the
configuration because that would prevent these entries from customizing security
updates for the default branch.

Pin every external GitHub Action to a full commit SHA and keep its release tag in
a same-line comment, for example:

```yaml
- uses: actions/checkout@0123456789abcdef0123456789abcdef01234567 # v6
```

Dependabot updates the SHA and its version comment together. A tag by itself can
move; a full commit SHA is the immutable workflow reference. The SHA makes the
selected code stable, but it does not establish that the action is safe. GitHub
also does not create Dependabot alerts for Actions pinned to SHAs, so review the
weekly Actions update pull requests and upstream advisories promptly.

## Private CV boundary

CI must install dependencies before checking out the private CV source. Pull
request builds, including Dependabot pull requests, use synthetic public fixtures
and receive no private-repository token or private CV input. Never use
`pull_request_target` to build pull-request code.

Dependency lifecycle scripts are disabled, and Astro runs only after the private
checkout is removed. Steps in one job still do not form a hard isolation boundary.
The build tools, Actions, and CV adapter remain trusted code. A future design
requiring separate job isolation can import the CV in a job that runs no npm
code, removes its private checkout, and transfers only sanitized JSON and the
public PDF to the build job.

The trusted release build checks out only the required CV files with a read-only
credential and `persist-credentials: false`. The import step validates an
allowlist of public fields and fails on unexpected fields. The deployment
artifact must exclude the private checkout, raw Markdown and YAML data, generated
intermediate data, credentials, drafts, and repository documentation.

The private CV repository remains a trusted release input. Checking the PDF
header catches an accidental wrong file, but does not prove that the PDF is safe
or contains only intended public information. Review changes in that repository
with the same care as changes to this site's public content.

## Repository settings

The workflow should set `contents: read` at the top level. Only the Pages deploy
job receives `pages: write` and `id-token: write`. Keep the repository's default
workflow token read-only and prevent workflows from creating or approving pull
requests unless a future workflow has a reviewed need for that authority.

Keep the dependency graph, Dependabot alerts, Dependabot security updates, secret
scanning, and push protection enabled in the repository settings. These settings
are not established by `dependabot.yml` and should be verified after the migration
lands.

Primary references:

- [npm `package-lock.json` documentation](https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json/)
- [npm `ci` documentation](https://docs.npmjs.com/cli/commands/npm-ci/)
- [GitHub Dependabot configuration](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configuring-dependabot-version-updates)
- [GitHub Dependabot update optimization](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/optimizing-pr-creation-version-updates)
- [GitHub Actions secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub Pages custom workflow requirements](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
