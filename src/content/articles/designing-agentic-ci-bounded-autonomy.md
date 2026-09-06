---
title: "Bounded Autonomy Requires Separate Control Planes"
description: "Agentic automation remains governable when model choice, execution, policy, and evidence are separate interfaces with independent owners and tests."
date: "2026-09-06"
category: "AI Engineering"
tags: ["agents", "ci", "security", "architecture", "automation"]
slug: "designing-agentic-ci-bounded-autonomy"
draft: false
featured: false
readTime: "6 min read"
---

An agent can inspect a failure, propose a patch, run tests, and prepare a pull request. The attractive part is the reasoning loop. The dangerous part is that every verb crosses a different trust boundary.

Reading a log, executing a command, writing a repository, using a credential, and publishing a change should not inherit one broad permission called “agent access.” The system stays governable when four concerns remain separate:

1. **Reasoning:** which model or harness decides what to try
2. **Execution:** where commands run and which resources they can reach
3. **Policy:** which actions and effects are allowed
4. **Evidence:** what a reviewer can inspect before accepting the result

I maintain the public [agentic-ci](https://github.com/opendatahub-io/agentic-ci) project. Its contribution and review history offers concrete examples of these boundaries evolving independently. The broader lesson is architectural: autonomy is easier to expand when authority does not live inside model prompts.

## Keep the harness replaceable

The harness manages the conversation with a model, tool calls, context, and output parsing. Different harnesses have different strengths and release cadences. They should be replaceable without redesigning sandbox policy or teaching every workflow a new execution protocol.

A stable runner contract can express:

```text
task + workspace + allowed capabilities + limits
        ↓
execution result + changed files + evidence + requested effects
```

The contract does not need to expose every feature of every harness. It needs to preserve the facts required by the policy and review layers. Exit status, time bounds, changed paths, network use, produced artifacts, and external effect requests matter more than a vendor-specific transcript format.

[agentic-ci #369](https://github.com/opendatahub-io/agentic-ci/pull/369), merged on September 1, 2026, adopted new harness images. That kind of change should alter the reasoning implementation while leaving release gates and sandbox invariants recognizable. Version updates remain meaningful, but semantic verification matters more than proving that an image tag changed.

## Make the sandbox an execution policy

A sandbox is sometimes treated as a container image with an agent installed. The image is only the mechanism. The policy describes what the process may do.

A useful execution policy covers:

- mounted paths and write scopes
- network destinations and protocols
- injected credentials and their lifetimes
- process, time, and memory limits
- allowed tools and external services
- durable outputs and cleanup behavior

[agentic-ci #327](https://github.com/opendatahub-io/agentic-ci/pull/327), merged on August 11, installed the OpenShell CLI from a published container artifact. [agentic-ci #330](https://github.com/opendatahub-io/agentic-ci/pull/330), merged two days later, built a sandbox from the project's agentic base image. The specific images will change. The durable question is whether the same policy can be stated and enforced across those implementations.

This separation prevents a common failure: declaring a runtime “secure” because it uses a sandbox product while leaving mounts, egress, and credentials implicit. Reviewers need the effective policy, not the brand name of the mechanism.

## Give deterministic code veto power

Model reasoning is useful for ambiguous diagnosis and repair. Some release decisions have crisp predicates: tests passed, required files changed, schema is valid, license is acceptable, artifact digest matches, approval exists. Deterministic code should enforce those conditions.

The agent may explain why a failed test is irrelevant. The gate should still fail until the policy explicitly permits that exception. The agent may propose a new dependency. A resolver and scanner should still produce the dependency evidence. This keeps persuasion separate from authority.

Policy exceptions need the same structure as ordinary decisions: scope, owner, reason, expiry or review trigger, and visible effect on the final result. An exception hidden in a prompt is difficult to audit and easy to copy.

## Treat skills as privileged interfaces

Agent skills package repeatable procedures such as repository inspection, license checks, onboarding, or failure analysis. They improve consistency, but they also expand the executable surface. A skill can parse untrusted content, call a CLI, write files, or request credentials.

The public [python-package-skills](https://github.com/opendatahub-io/python-package-skills) repository makes this interface visible. The initial builder-onboarding skill arrived in [pull request #1](https://github.com/opendatahub-io/python-package-skills/pull/1). The [security-audit skill in #3](https://github.com/opendatahub-io/python-package-skills/pull/3) and [packaging-investigation skill in #4](https://github.com/opendatahub-io/python-package-skills/pull/4) separate two tasks that consume different evidence and produce different decisions. Both changes merged on July 14, 2026.

A skill contract should state:

- required inputs and trusted context
- permitted tools and write locations
- expected structured outputs
- external effects it may request
- failure states and uncertainty
- tests or evaluations that exercise behavior

Static validation can catch malformed metadata, missing resources, and disallowed paths. Behavioral evaluation is needed for more consequential questions: does the skill refuse an unsafe input, preserve a dry-run boundary, cite the source it summarized, and report partial failure accurately?

Path handling deserves particular attention. [agentic-ci #361](https://github.com/opendatahub-io/agentic-ci/pull/361), merged on August 26, added support for Git subdirectory marketplace sources. A subdirectory feature changes the trust boundary because user-controlled source paths can influence what is copied or executed. Normalization, containment checks, and explicit roots belong in code, not prompt instructions.

## Model external effects as state transitions

“Create a pull request” is not one atomic tool call. Authentication may succeed while the push fails. The branch may be pushed while PR creation fails. A retry may encounter an already-existing branch or PR.

Represent the operation as states:

```text
prepared → validated → branch_pushed → proposal_created → verified
                    ↘ failed_with_recovery_context
```

Each transition should be idempotent where practical and return enough identifiers for recovery. Before retrying, the orchestrator inspects current state rather than assuming the previous attempt did nothing. This is ordinary distributed-systems work applied to agent tools.

The same rule applies to cancellation and cleanup. A timed-out model call should not leave an unknown child process, mounted credential, or half-written result that the next run mistakes for success.

## Design evidence for review, not surveillance

A complete raw transcript is often too large and too sensitive to be the primary review surface. A useful run record connects the decision to inspectable facts:

- task and source revision
- declared policy and granted capabilities
- tool calls that changed state
- file and artifact digests
- tests and deterministic gate results
- external identifiers such as branch or pull-request URLs
- unresolved uncertainty and partial failures

The model's narrative can help a reviewer understand the work, but the narrative should point to these records. Evidence also needs retention and redaction rules. Capturing every environment variable or command output can turn observability into credential leakage.

This architecture creates a safe direction for growth. A new model can improve diagnosis without gaining more credentials. A new sandbox can strengthen isolation without rewriting project policy. A new skill can add a capability through a tested contract. A team can grant a new external effect by adding one state machine and one review gate.

Useful autonomy is specific authority with visible consequences. Separate control planes make that authority understandable, testable, and reversible. They let the reasoning layer remain flexible while the system around it decides what may happen and records what actually did.
