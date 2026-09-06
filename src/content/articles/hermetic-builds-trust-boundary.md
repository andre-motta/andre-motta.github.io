---
title: "Hermetic Builds Begin at the Acquisition Boundary"
description: "A build becomes explainable when every network-dependent input is acquired explicitly, recorded, and separated from the steps that construct the artifact."
date: "2026-09-06"
category: "Software Supply Chain"
tags: ["build-systems", "hermeticity", "containers", "supply-chain", "openshell"]
slug: "hermetic-builds-trust-boundary"
draft: false
featured: false
readTime: "8 min read"
---

A build can be deterministic on a developer's laptop and still fail in a controlled pipeline because the source code was never its complete input. A package manager contacts an index. A compiler downloads a target. A code generator fetches a tool. A nested script runs `curl`. Each step quietly expands the set of systems that may influence the artifact.

Closing the network without finding those paths produces a frustrating series of missing-file failures. Leaving it open produces an artifact whose inputs are difficult to enumerate. The architectural task is to define an acquisition boundary: all external material enters before construction, through mechanisms that can record what was selected.

## Start with input channels, not tool names

A dependency manifest is only one input channel. A useful inventory follows every process that can obtain executable code or artifact content:

- operating-system packages and repository metadata
- language packages and build requirements
- compiler toolchains, targets, and standard libraries
- source archives and Git repositories
- generated code and generator binaries
- container base images and copied artifacts
- install scripts that download auxiliary tools
- architecture-specific assets selected at build time

This inventory should be mechanical. Search build definitions and scripts for network clients, package-manager commands, Git operations, bootstrap installers, and dynamic URLs. Then run the build with the network denied and treat each failure as evidence of an unmodeled input.

The result is more than a list of URLs. It is a map of authority. If a nested build script can choose a new version from a live index, that script participates in dependency resolution whether or not the main manifest acknowledges it.

## Separate acquisition from construction

The clean boundary has two phases.

During acquisition, network access is allowed through controlled tooling. The system resolves declared requirements, downloads content-addressed or checksummed artifacts, records source locations and selected versions, and places the results in a known store.

During construction, the network is unavailable. The build can read source plus the acquired store and write its outputs. Any attempt to fetch another input fails.

```text
declared sources
      ↓
controlled acquisition
      ↓
recorded local input set
      ↓
network-isolated construction
      ↓
artifact + evidence
```

That split turns “the internet” from an implicit dependency into a reviewed interface. It also creates a useful failure classification. An acquisition failure means the declared source cannot be resolved under policy. A construction failure that requests the network means the input model is incomplete. Those problems have different owners and different fixes.

## A concrete midstream case

The public [Open Data Hub OpenShell repository](https://github.com/opendatahub-io/openshell) is a Red Hat-maintained midstream of [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell) used for downstream secure builds. I am a maintainer of that midstream. The repository provides a visible example of adapting an upstream project to a controlled build environment while keeping the upstream relationship explicit.

The gateway and supervisor are Rust binaries. Their build path needs Cargo dependencies and target support for more than one architecture. [OpenShell midstream pull request #1](https://github.com/opendatahub-io/openshell/pull/1), merged on July 28, 2026, added hermetic container build definitions for those services. The construction stage consumes prefetched Cargo content rather than resolving dependencies from the public network.

The command-line client crosses a different boundary. It is distributed as a Python package, but its build uses generated protocol stubs and its release path needs to work from a source distribution, not only from a populated Git checkout. [OpenShell midstream pull request #22](https://github.com/opendatahub-io/openshell/pull/22), merged on August 10, added the hermetic CLI container path and coordinated its prefetched inputs.

The public changes show why “make the build offline” is too coarse a task. Rust crates, Python build requirements, generated files, and architecture targets have distinct acquisition mechanisms. The right boundary is shared, while the manifests and adapters remain ecosystem-specific.

They also show the responsibility of a midstream. A midstream can carry secure-build integration and downstream policy while proposals travel upstream. It should make those adaptations visible and keep their relationship to upstream source reviewable.

## Generated files are part of the source contract

Generated code exposes an especially common hidden assumption. A repository checkout may contain generated files left by a developer or generated by an earlier build step. A published source archive may omit them. If the generator or schema compiler is unavailable during an isolated build, the archive cannot reproduce a working wheel.

That issue appeared in [NVIDIA OpenShell issue #2596](https://github.com/NVIDIA/OpenShell/issues/2596). The reported source-distribution path produced a wheel without the protocol stubs needed at runtime. [Upstream pull request #2598](https://github.com/NVIDIA/OpenShell/pull/2598) proposes committing the generated stubs so the source archive contains the material required to build the wheel. Both remain open as of September 6, 2026.

There are two sound policies for generated content:

1. Ship the generated files in the source distribution and verify that regeneration produces no diff.
2. Ship the generator plus every required input and make generation an explicit, offline-capable build step.

The choice depends on reviewability, generator stability, archive size, and support expectations. The unsound state is depending on files that appear in one source form and disappear in another.

## Record enough to answer later questions

Hermetic construction prevents an undeclared network fetch. It does not by itself prove that acquired inputs were good. The evidence should record:

- the source revision and release identity
- base image digests
- package names, versions, sources, and hashes
- source archives or Git revisions
- toolchain and target identities
- declared exceptions and why they exist
- output artifact digests

This lets reviewers ask concrete questions. Did the build use the approved source? Did a mirror change the bytes? Did the toolchain move? Did two architectures receive equivalent policy?

Checksums establish content integrity relative to an expected digest. Signatures and attestations can bind content to identities or provenance. Review and dependency policy decide whether those identities and inputs are acceptable. Hermeticity supports those controls by making the input set finite; it does not replace them.

## Keep acquired, built, and shipped inventories distinct

A software bill of materials (SBOM) is useful at this boundary when its subject and lifecycle point are explicit. One manifest should not silently stand in for three different inventories:

- The acquired inventory records every external artifact admitted to the build, including transitive packages, compilers, generators, build backends, and other build-only inputs.
- The built inventory describes the components present in the produced artifact after compilation, vendoring, generation, linking, and copying.
- The shipped inventory describes the exact release objects that leave the pipeline, after packaging, stripping, or selection for a particular platform.

The records should link the source revision and build event to exact output digests. The [SPDX 3.0.1 Build profile](https://spdx.github.io/spdx-spec/v3.0.1/model/Build/Build/) can relate a build to its inputs, outputs, host, and tools. For a released archive, the [SPDX package checksum](https://spdx.github.io/spdx-spec/v2.3/package-information/#710-package-checksum-field) identifies the specific blob the record describes. CycloneDX can represent [direct and transitive dependency relationships](https://cyclonedx.org/specification/overview/#dependencies), while its [formulation model](https://cyclonedx.org/specification/overview/#formulation) can describe the declared or observed work that produced or deployed a component.

These views are related, but they should differ honestly. A compiler belongs in the acquired inventory even when none of its files ship. A statically linked or vendored library belongs in the built and shipped views even when the runtime package manager cannot see it. Comparing the inventories makes those transformations explicit instead of treating absence from the final filesystem as absence from the supply chain.

An SBOM is still a claim produced by an observation method. A manifest-only scanner can miss dynamically selected inputs, copied binaries, vendored code, or architecture-specific branches. A digest binds the record to particular bytes; it does not authenticate where those bytes came from or show that another build will reproduce them. When coverage is uncertain, say so. CycloneDX [compositions](https://cyclonedx.org/specification/overview/#compositions) can mark component and dependency coverage as complete, incomplete, or unknown.

The three inventories strengthen hermetic-build evidence when they are captured at the acquisition, construction, and release boundaries and tied together. They do not make the build hermetic by themselves. Network isolation and a complete input model establish that property; the linked records make the claim inspectable later.

## Choose the level of reproducibility you can defend

Several claims are often collapsed into “reproducible build”:

- the same declared versions can be resolved again
- the same input artifacts can be retrieved again
- the build can run without the public network
- repeated builds produce identical bytes

Each level needs additional control. A lock file may stabilize versions while leaving artifacts mutable or unavailable. Prefetching may preserve inputs without eliminating timestamps and nondeterministic ordering. Offline construction may still produce different bytes. Byte-for-byte reproducibility is valuable, but the earlier levels already improve diagnosis and policy enforcement when named accurately.

Hermetic build work becomes tractable when the team asks one question: where is each external input allowed to enter? Acquisition makes those choices under policy. Construction consumes the recorded result without opening new channels. Once that boundary is real, failures become explanations of missing inputs, and release evidence can describe what shaped the artifact instead of merely reporting that the build passed.
