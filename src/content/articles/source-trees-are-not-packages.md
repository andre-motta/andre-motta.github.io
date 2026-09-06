---
title: "Testing the Package Beyond the Source Tree"
description: "Several upstream fixes point to one packaging rule: exercise built artifacts, disabled paths, and dependency boundaries directly."
date: "2026-09-06"
category: "Software Engineering"
tags: ["python", "packaging", "build-systems", "open-source"]
slug: "source-trees-are-not-packages"
draft: false
featured: true
readTime: "5 min read"
---

A source checkout is an unusually forgiving place to test software. It contains generated files, development dependencies, repository metadata, and paths that disappear when the project becomes a wheel or source distribution. Several upstream packaging problems I worked on since mid-2025 had different symptoms, but the same underlying shape: the code was correct in the repository and wrong at the boundary where users actually received it.

Python delivery usually crosses at least three transformations:

```text
repository checkout → source distribution → wheel → installed runtime
```

Each arrow can remove files, change import paths, invoke a different build backend, or select a different optional feature. Testing only the checkout verifies the most generous representation. A strong package contract tests every representation that users or downstream builders actually consume.

The smallest example was in pretty-yaml. Its tests expected an exception name that included the source-tree module prefix. That detail changed when the tests ran from a built wheel. The fix in [pretty-yaml #48](https://github.com/mk-fg/pretty-yaml/pull/48), merged on July 10, 2025, changed two assertions so the same suite could run against either form. The production code did not change. The test had accidentally encoded the layout of the repository.

The same boundary can hide files rather than names. In ROCm aiter, setting `PREBUILD_KERNELS=1` failed because the build copied several source directories into an intermediate package but omitted `gradlib`. [aiter #1097](https://github.com/ROCm/aiter/pull/1097), merged on September 29, 2025, added the missing directory copy. A companion change, [aiter #1099](https://github.com/ROCm/aiter/pull/1099), merged a day earlier, made the build respect an explicit `MAX_JOBS` value instead of replacing it with an automatic calculation. These are both build-contract problems: an option promises a behavior, and the packaging code must preserve every input needed to honor it.

Generated code makes that contract harder to see. NVIDIA OpenShell's Python package generated protobuf and gRPC stubs through its development task graph, but the generated files were ignored by Git. A checkout prepared through the project workflow worked. A PEP 517 build that started from the source archive produced a wheel with an empty `_proto` package. My proposed fix in [NVIDIA OpenShell #2598](https://github.com/NVIDIA/OpenShell/pull/2598) tracks the generated stubs and adds a freshness check that regenerates them and fails on a diff. As of September 6, 2026, the upstream pull request is open, so this is a proposed solution rather than accepted upstream behavior. This upstream proposal is separate from my merged packaging work in Red Hat's public [OpenShell midstream](https://github.com/opendatahub-io/openshell).

The important choice there is not simply whether generated code belongs in Git. The invariant is that the published source archive must contain everything a standard build frontend needs. If generation requires repository-only tools or files, either the archive has to include the generated output or the build backend has to perform generation from declared inputs. A freshness check closes the second half of the loop by preventing checked-in output from drifting away from its schema.

Optional compilation paths create another kind of artifact boundary. In TorchCodec, the implementation used when AVIF support was disabled did not match the declaration in the header. The enabled path accepted a `num_threads` parameter; the disabled stub did not. That difference survived compilation far enough to become an undefined symbol when importing the shared library. [TorchCodec #1671](https://github.com/meta-pytorch/torchcodec/pull/1671) added the missing parameter and merged on August 24, 2026. It was a two-line fix to a path that was easy to miss if every build enabled AVIF.

Version boundaries can be just as sharp. CUDA Python 13.0 and 13.1 share a major version, but some device-resource declarations exist only in 13.1 and later. The build passed only the major version into Cython, so compile-time guards could not distinguish the two APIs. [CUDA Python #2700](https://github.com/NVIDIA/cuda-python/pull/2700) proposes passing both major and minor versions and tightening only the guards around 13.1-specific types. As of September 6, 2026, that pull request remains open. Its status matters: the diagnosis and patch are public, but upstream has not accepted the change.

Imports themselves can cross the boundary unexpectedly. A RapidOCR asset-preparation script needed two lightweight utility modules. Importing them through the package executed `rapidocr/__init__.py`, which pulled in OpenCV and other runtime dependencies that the preparation step did not need. [RapidOCR #710](https://github.com/RapidAI/RapidOCR/pull/710) proposed bypassing that eager package initialization. The maintainers closed it without merging, so it belongs in the record as an investigated approach, not a shipped fix.

These cases suggest a practical test matrix for packages:

1. Build a source distribution from a clean checkout.
2. Build the wheel from that source distribution, not directly from Git.
3. Install the wheel into an environment without development-only dependencies.
4. Import the package and run entry points from outside the repository.
5. Exercise disabled optional features as deliberately as enabled ones.
6. Test the oldest and newest dependency versions that share a compatibility range.
7. Set resource-control variables explicitly and verify that the build respects them.

The matrix should preserve failure location. A source-distribution build failure means the published source contract is incomplete. A wheel-install failure points to metadata or dependency selection. An import failure after installation points to missing runtime files, loader behavior, or ABI compatibility. A disabled-feature failure indicates that compile-time variants do not satisfy one interface. Reporting only “packaging failed” throws away the boundary that narrows the diagnosis.

There is a cost to exercising every representation. Building an sdist and rebuilding a wheel adds time; native and accelerator variants add scarce infrastructure. Use risk to choose cadence. The cheap source-to-wheel path belongs on every packaging change. Expensive architecture and feature combinations can run on a release gate or schedule, provided the support contract says what evidence is current.

The lesson I infer from this work is that packaging failures are often accurate reports about an untested system boundary. The missing file, wrong symbol, surprising import, and ignored environment variable are different clues. They all ask the same question: what did the build assume would still be present after the repository disappeared?
