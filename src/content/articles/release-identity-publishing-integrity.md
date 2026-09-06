---
title: "A Release Has Three Trust Decisions"
description: "Version identity, permission to publish, and artifact integrity answer different questions. A release pipeline is trustworthy only when it connects all three."
date: "2026-09-06"
category: "Software Supply Chain"
tags: ["releases", "python", "oidc", "attestations", "supply-chain"]
slug: "release-identity-publishing-integrity"
draft: false
featured: false
readTime: "6 min read"
---

A package release can have an impeccable version number and still come from the wrong workflow. It can come from the approved workflow and still contain files that were replaced after the build. It can carry a valid signature and still contain vulnerable or malicious code.

Those failures are easy to blur together because release systems present one green outcome: published. The underlying decisions are different:

1. **Identity:** Which source state and version does this release represent?
2. **Authority:** Which machine identity was allowed to publish it?
3. **Integrity:** Are these the same files produced and authorized by that identity?

A good pipeline connects these decisions without pretending that one control answers all three.

## Give the release one identity

Many Python projects begin with a version string in `pyproject.toml`, a Git tag, and perhaps a container tag. Each is reasonable in isolation. Trouble begins when they can disagree.

A manual version bump creates redundant state. The repository may declare `1.4.0` before the `1.4.0` tag exists, or a tag may be pushed from a commit whose package metadata still says `1.3.2`. A build that produces both a wheel and a container has another opportunity to translate the version inconsistently.

The useful design move is to choose one release event as the authority and derive the other labels from it. In a tag-driven process, the tag identifies the intended source commit and the build backend derives Python package metadata from repository history. Untagged commits receive development versions. Other artifact ecosystems receive explicit, validated translations of the same identity.

That was the direction of the public [agentic-ci dynamic-version change](https://github.com/opendatahub-io/agentic-ci/pull/244), merged on July 14, 2026. A later [development-version fix](https://github.com/opendatahub-io/agentic-ci/pull/303), merged on August 3, made the fallback explicit as `.dev0`. The [Python version specification](https://packaging.python.org/en/latest/specifications/version-specifiers/#implicit-development-release-number) permits an omitted development number and normalizes `.dev` to `.dev0`; the reported rejection belonged to that particular build path. Emitting the normalized form avoids depending on every tool to perform the same normalization.

Tag-derived versions remove one synchronization problem, but a tag is still a name. Release evidence should also record the source commit and the digest of every built file. A useful identity record looks more like a tuple than a string:

```text
project + version + source revision + artifact digest
```

The human-facing version supports dependency resolution. The revision supports source investigation. The digest identifies exact bytes. Each field answers a different operational question.

## Replace stored release secrets with workload identity

Once the pipeline knows what it is releasing, it needs permission to publish. A long-lived PyPI API token answers that need, but it creates a second system for secret storage, rotation, leakage response, and maintainer offboarding.

[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) uses OpenID Connect instead. A CI provider issues a short-lived identity token containing claims about the running workload. PyPI matches those claims against a configured publisher and returns a project-scoped API token that lasts 15 minutes. The release job no longer needs a manually generated PyPI token stored in repository secrets.

The security improvement comes from changing the credential lifecycle. There is no durable release credential waiting to be copied from a settings page, exposed in a log, or forgotten after access changes. The workflow asks for authority when it needs it, and that authority expires quickly.

OIDC does not remove the trust decision. It relocates it into the publisher configuration and the CI workflow. PyPI's [security guidance](https://docs.pypi.org/trusted-publishers/security-model/) says that weaknesses in a registered workflow can be equivalent to credential compromise. If an attacker can alter or invoke the trusted release workflow under an accepted identity, short-lived credentials will faithfully authorize the attacker.

The release workflow therefore needs its own protection:

- grant `id-token: write` only to the publishing job
- bind the PyPI publisher to the intended repository and workflow
- use a protected deployment environment when the forge supports it
- review changes to the workflow as changes to a credential boundary
- keep build and test jobs from receiving publication authority

Trusted Publishing answers, “Was this upload authorized through the configured CI identity?” It does not answer, “Was the source good?” or “Are these the bytes we tested?”

## Bind the identity to the file

Digital attestations address the next gap. PyPI's [PEP 740 attestation support](https://docs.pypi.org/attestations/) binds each distribution file, such as a wheel or source archive, to a strong digest and a signing identity. A PyPI publish attestation can show that a particular file was uploaded through a particular Trusted Publisher.

That gives downstream verification a concrete subject. A verifier can compare the downloaded file's digest with the attested digest and inspect the publisher identity. PyPI's [publish-attestation specification](https://docs.pypi.org/attestations/publish/v1/) describes the result carefully as greater confidence in integrity, rather than proof that the project is trustworthy.

The distinction matters. A valid attestation can prove that vulnerable code came from the expected workflow without being modified afterward. It cannot decide whether maintainers reviewed the code, whether dependencies were appropriate, or whether the workflow itself was compromised. PyPI's [attestation security model](https://docs.pypi.org/attestations/security-model/) is explicit that provenance tells a consumer where a file came from, while trust in that source remains a separate decision.

Attestations become useful when somebody verifies them. Merely producing provenance adds metadata. A practical release contract says which identity consumers should expect, where verification occurs, and what a mismatch does. The answer might be an installation policy, an intake gate, or an alert when a project's publisher identity changes.

## Build once, then move the evidence with the artifact

The three decisions meet at artifact flow. A fragile pipeline tests one build, rebuilds during publication, and then attests whatever the second job produced. Even when both jobs use the same revision, time, network state, tool versions, and dependency indexes can change the bytes.

A stronger sequence is:

```text
select source revision
        ↓
derive and validate version
        ↓
build artifact once
        ↓
test that exact artifact
        ↓
approve publication
        ↓
publish and attest the same digest
```

The artifact, its identity record, and its test evidence travel together. Publication does not reconstruct the candidate. This reduces the number of states an operator must compare after a failure and makes promotion across channels possible without another build.

The controls also fail independently, which improves diagnosis. A version mismatch is an identity failure. An OIDC claim mismatch is an authority failure. A digest mismatch is an integrity failure. A vulnerable but correctly attested package is a validation or source-governance failure. Calling all four “release failures” loses the information needed to respond.

Release engineering becomes clearer when each control has one job. A tag and version make the release addressable. OIDC grants a narrowly scoped workflow permission to publish. An attestation binds exact files to that publishing identity. Tests, review, dependency policy, and reproducible-build work establish other forms of confidence. The pipeline earns trust by connecting those claims and preserving their boundaries.
