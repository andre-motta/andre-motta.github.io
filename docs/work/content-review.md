# Editorial review

Andre approved all ten articles on September 6, 2026, including the five final
revisions below. All are now eligible for production builds (`draft: false`).
Astra reviewed each article for a substantial engineering argument, clear tradeoffs,
accurate attribution, and public-safe evidence. Small implementation changes serve
as examples within a larger argument rather than separate tutorial topics.

## Scope and consolidation

The initial review consolidated 18 drafts into 11 articles. Following final
feedback, the library contains ten articles. The compatibility-matrix essay was
withdrawn, and the old welcome post now redirects to About.
Overlapping essays on hermetic builds, runtime policy, skills, failure evidence,
and decision records were merged. The generic ownership essay and standalone
fleet-monitor piece were held. Projects can be represented without requiring an
article for every change.

The release material now explains release identity, publishing authority, and
artifact integrity. A separate article argues for a useful early PyPI release,
including the maintenance commitment and PyPI's prohibition on empty placeholders.

## Article inventory

| Article | Main argument | Status |
| --- | --- | --- |
| Testing the Package Beyond the Source Tree | Test delivered artifacts and disabled paths | Andre approved |
| One Review Inbox for Two Forges | Unify the review task while preserving provider semantics | Andre approved |
| Bounded Autonomy Requires Separate Control Planes | Separate reasoning, execution, policy, and evidence | Andre approved |
| Build Pipelines Should Explain Their Decisions | Preserve evidence for release decisions and maintenance | Andre approved |
| A Release Has Three Trust Decisions | Connect identity, OIDC authority, and attested bytes | Andre approved |
| How to Trace an Agent That Can Crash or Be Killed | Lifecycle ownership, completion evidence, and recovery limits | Astra reviewed; Andre approved |
| A Linux Updater Is a Deployment Transaction | Artifact-set activation, authority, health, and recovery | Astra reviewed; Andre approved |
| When Repeated Release Work Deserves a Shared Stream | Worked example of shared release policy and independent qualification | Astra reviewed; Andre approved |
| Hermetic Builds Begin at the Acquisition Boundary | Controlled acquisition, construction, and SBOM evidence | Astra reviewed; Andre approved |
| The Case for Publishing a Useful Package Early | Real early releases and the cost of distribution-name conflicts | Astra reviewed; Andre approved |

Astra reviewed the final revisions on September 6, 2026, after both writing and
research agents finished. Production and preview checks passed. Andre separately authorized staging and publishing the migration to master. The
full commit message must still be approved before committing.

## Research coverage

Public GitHub research covers June 1, 2025 through September 6, 2026:

- 95 authored public pull requests: 70 merged, 5 open, 20 closed without merge.
- 66 returned authored issue records. GitHub reported 69 but returned 66 through
  REST and GraphQL; the unexplained discrepancy is retained in the private research.
- 114 formal review submissions across 113 pull requests.
- 111 issue/PR conversation comments across 92 objects, excluding formal review
  bodies and inline review comments.
- 239 commit contributions across 26 repositories in GitHub's contribution graph.

These categories overlap. They are evidence of different activities, not additive
impact scores. Commit contributions cannot be classified as direct pushes from
that graph. Open and closed-unmerged proposals must never be described as shipped
upstream changes. Project maintainership comes from Andre's explicit confirmation,
not contribution counts.

Raw evidence and internal-work provenance remain outside tracked files and site
artifacts, including in the intentionally gitignored local `.wiki/`.
Internal workplace material is generalized. Article citations link to the relevant
public upstream discussions and primary technical documentation.
