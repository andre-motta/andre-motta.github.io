---
title: "When Code Is Cheap, Review the Claims"
description: "Agents made code and the claims about it cheap to produce. Review has to move from reading prose to checking evidence that could have failed."
date: "2026-09-26"
category: "AI Engineering"
tags: ["agents", "code-review", "testing", "quality"]
slug: "review-the-claims-not-the-prose"
draft: false
featured: false
readTime: "8 min read"
---

Most of the changes I review now were written with an agent, including many of my own. The diffs are usually tidy. Names are reasonable, the style matches the codebase, and the description is complete and confident. The failures I catch have moved somewhere else.

They sit in context and in claims. A change lands in the wrong layer, touches files it did not need, or repairs a symptom that was misdiagnosed. The description says the change was tested. A thread is marked addressed. A check reports success. An automated reviewer returns PASS. Each of those statements is now as cheap to produce as the code, and a reviewer who reads them as evidence is reviewing prose. What review should ask for instead is evidence, specifically evidence that could have failed.

## A PASS describes what was checked

I learned this on my own pull request. [rhai-org-pulse #1526](https://github.com/red-hat-data-services/rhai-org-pulse/pull/1526) restored a workflow that files a Jira request and triggers a GitLab pipeline. The repository runs an AI review on each push. It returned PASS twice on the first day, and again after later fixes, while a credential problem described below was still in the code.

Three days in, a human reviewer asked a short question: did you test this? The pipeline call combined parts of two different GitLab APIs and would not have worked with either. My answer was no. I had put the integration together as a starting point before a long weekend and had not exercised it. The same review round found two more bugs by reading the code against the documentation: the Jira user lookup read a response shape the API does not return, and a cooldown was recorded before creation succeeded, which blocked retries after a failure.

The automated review had praised the test suite: 59 unit tests and an integration test. Some of those tests mocked the Jira response in the wrong shape, so they passed against the bug. They could not have failed. The human reviewer checked the calls against the API documentation and asked the question the diff could not answer: had this ever run?

The fixes were ordinary. The more useful part of my reply was a statement of limits: local tests and browser checks passed, but I had not created a live ticket or triggered a live pipeline. A later question about which token the call used exposed the remaining problem. The fallback tokens only had read access, so pipeline creation would have failed silently in production. That became a dedicated credential and an explicit "not triggered" result when it is missing.

## Ask for evidence that could have failed

A check is evidence only if it would have failed when the change was wrong. That property is the one most often missing from generated tests and probes.

On [openshell #54](https://github.com/opendatahub-io/openshell/pull/54), a container build added a probe to confirm that a linker pin prevented crashes in name-service lookups. I asked for a negative control:

> This probe has no negative control, so it cannot distinguish "pin works" from "libnss_systemd never loaded anyway".

If a later base image stopped loading that module for an unrelated reason, the pinned probe would still pass, and so would an unpinned one. I suggested building the probe without the pin and asserting that it crashes. The author found that this would have broken the arm64 build: the unpinned probe crashes on x86_64 but not on aarch64 with the same glibc. He replaced it with a fake name-service module that behaves the same on both architectures and also fails when the module cannot load. Then he showed the guard failing when the pin object had no constructor and when the fake module was missing. The check now has failing cases, and they were observed.

The same test applies to smaller cases:

- A test that skips when an import fails hides exactly the regression it exists to catch. Let the error surface.
- A test that asserts current behavior, including known-bad behavior, locks in the bug.
- A report that exits zero with an empty failure list can look complete when it is not. On [fromager #1314](https://github.com/python-wheel-build/fromager/pull/1314) I attached a short reproduction showing exactly that for resolution-only failures and asked for a test that pins the contract down.
- A change to edge-case handling should run against a real package with that edge case. On [fromager #1289](https://github.com/python-wheel-build/fromager/pull/1289) my approval came with a request to try it against a real package on PyPI before releasing. Another reviewer ran old and new builds side by side against a real package and posted a before-and-after table, which is the kind of evidence the request was for.

## Treat instructions as code with a nondeterministic interpreter

Skills, prompts, and agent instructions are now part of what gets reviewed. They fail differently from code. A contradiction in code produces a consistent wrong answer that a test can catch. A contradiction in instructions produces an answer that depends on which sentence the model weighs on that run.

On [python-package-skills #31](https://github.com/opendatahub-io/python-package-skills/pull/31), a license table, a mapping rule, and a special case disagreed about one license:

> The verdict for the same input can flip between runs depending on which sentence the model weighs.

The author made the table authoritative. The same review found a package-naming rule repeated in three places, and the rule was wrong: it missed the lowercasing step of PEP 503 normalization, so a plugin for a mixed-case package would silently never load. The correction had to land in all three copies or the instructions would contradict each other. One authoritative statement, referenced elsewhere, is the instruction-level equivalent of not duplicating a constant.

When an output must satisfy a guarantee, instructions are the wrong enforcement point. On [knowledge-skills #7](https://github.com/opendatahub-io/knowledge-skills/pull/7) I suggested moving a structured verdict into a script the skill calls, so the format is guaranteed rather than requested. The model decides, and deterministic code records and validates the decision.

## Weigh automated findings against context the bot lacks

Automated reviewers catch real issues on my own pull requests. On [agentic-ci #327](https://github.com/opendatahub-io/agentic-ci/pull/327) the bot found that a tag lookup only read the first page of registry results and that a deduplication set was not updated when extra endpoints were added. I fixed both. On [agentic-ci #432](https://github.com/opendatahub-io/agentic-ci/pull/432) it noticed that a running gateway would not pick up a changed configuration, which became a fix and a test.

The same pull requests also show findings that needed weighing rather than obeying. On #327 the bot recommended pinning our images to digests. For third-party images that is good advice. Here we control the registry repository and build the images ourselves, so the pin added churn without changing who we trust. On #432 a finding about cleaning up a stale sandbox assumed state that cannot survive between runs, because each job runs in an ephemeral container.

Scope needs the same judgment. On [agentic-ci #427](https://github.com/opendatahub-io/agentic-ci/pull/427) the bot flagged a weakness in how a kept sandbox is reused. It was reasonable hardening, but the code path was untouched, only reachable with a local development flag, and the change under review reduced exposure. I said it belonged in its own change. A diff that absorbs every good idea stops being reviewable, and agents are generous with good ideas.

In each case the useful review work was stating the context the bot could not see: who controls the images, how long state lives, and what the change is for. The next reader then knows why a finding was taken or declined.

## I review with AI too

Several of the longer reviews linked above were drafted with AI assistance. The tools are good at reading a large diff against a contract, tracing a value across files, and producing a minimal reproduction. AI is here to help us be more productive, but I still double check its findings before they go out under my name.

Checking does not make every finding right. On the openshell review, one of my findings was wrong: I called a linker flag redundant, and the author reproduced a link failure showing that it was not. The fix for a wrong review finding is the same as for a wrong claim in a pull request: a run that settles it.

## Ownership does not dilute

Whoever submits a change owns it, however much of it they typed. When an author does not know whether something works, the description should say so. My reply on the pull request above was more useful because it listed what I had not verified.

This costs time, and the cost should match the risk. A documentation fix can merge on green checks. A change that touches credentials, an external API, or a release path needs evidence of the live behavior, or an explicit statement that it has not been observed.

The volume of generated code will keep growing. So I spend review time on the claims that matter and ask each one for the run that could have proven it wrong.
