---
title: "A Linux Updater Is a Deployment Transaction"
description: "Safe self-updates preserve a compatible installed set through staging, validation, privileged activation, startup checks, and recovery."
date: "2026-09-06"
category: "Software Engineering"
tags: ["linux", "deployment", "desktop", "reliability", "open-source"]
slug: "linux-updater-preserve-last-working-install"
draft: false
featured: false
readTime: "6 min read"
---

A desktop updater looks simple when the application is one file. The model breaks when an application, privileged helper, launcher, and metadata must agree on a version. Each file can be intact while the installed set is inconsistent.

The useful abstraction is a deployment transaction. It stages one candidate release, checks that the candidate is acceptable as a set, activates it through the narrowest required authority, and preserves enough state to recover when the next launch fails.

I contributed the Linux installation and update path to [LOA Logs](https://github.com/snoww/loa-logs). The current code improves interrupted-download behavior and startup availability. The fuller transaction described later is a recommended extension, not a claim about what those pull requests already provide.

## The unit of deployment is the release set

Suppose release `v2.4.0` contains these artifacts:

```text
loa-logs.AppImage
nineveh
start-loa.sh
release metadata
```

The application may expect a protocol added to the `v2.4.0` helper. The helper may expect command-line flags supplied by the new launcher. If the first download succeeds and the second fails, every file on disk can be intact while the installation as a whole is broken.

The updater needs one candidate identity that binds the artifacts together. A release manifest records artifact names, sizes, digests, compatibility constraints, and the launcher format that understands it. The updater stages that manifest as one unit.

That produces a more useful state machine:

```text
ACTIVE(v2.3)
  -> STAGING(v2.4)
  -> VALIDATED(v2.4)
  -> ACTIVATING(v2.4)
  -> VERIFYING(v2.4)
  -> ACTIVE(v2.4)
```

Any failure before activation should leave `v2.3` selected. Any failure after activation should leave enough information to select `v2.3` again or present a precise recovery instruction. “Latest version downloaded” is not a state because it says nothing about compatibility or which files are currently in use.

## What the current LOA path establishes

The merged LOA Logs Linux path installs and updates the AppImage and `nineveh`, manages the helper through `pkexec`, and preserves user data on uninstall. Downloads go to temporary paths before `mv` places them at their destinations. If GitHub is unavailable, the launcher uses the installed binaries. It also provides visible warnings, idempotent cleanup, safe argument handling, and bounded logs. The public implementation is recorded in [LOA Logs #211](https://github.com/snoww/loa-logs/pull/211) and [#212](https://github.com/snoww/loa-logs/pull/212).

These changes keep a partial transfer away from the installed file and prevent a release-service outage from automatically becoming an application outage. The launcher retains recent logs, cleanup can run again safely, and argument arrays preserve boundaries without reparsing a constructed shell command.

Per-file replacement and release-set activation solve different problems. A rename can keep a half-written file out of use, but two separate renames leave a window in which the application and helper come from different releases. The extension below closes that window and adds explicit decisions about authenticity, health, and recovery.

## A stronger design stages without privilege

The next step is to separate download authority from install authority. Network access and release parsing can happen as the desktop user in a private staging directory. The privileged operation should receive an identified candidate and perform only changes that require elevation.

A clean protocol looks like this:

```text
discover -> download -> validate -> authorize -> activate -> verify -> retain
```

Select a specific release rather than repeatedly resolving “latest.” Download every artifact into a user-owned candidate directory. Then check required files, sizes, digests, compatibility rules, and the manifest format.

Digest validation detects corruption relative to the manifest. It does not authenticate the manifest. A threat model that includes a compromised distribution path needs a trusted signature or equivalent provenance policy with defined roots.

Only after initial validation should the updater request elevation. The privileged helper should copy the candidate into a private directory owned by the privileged account, then validate that copy against the expected manifest and activate only that copy. A descriptor-based protocol that provides the same check/use guarantee is another option. Rechecking a path in user-owned staging is insufficient because the input can change between validation and installation. The helper should also reject unexpected paths and avoid shell reinterpretation.

## Activate one compatible set

Versioned installation directories make the transaction visible:

```text
/opt/loa-logs/releases/v2.3.0/
/opt/loa-logs/releases/v2.4.0/
/opt/loa-logs/current -> releases/v2.3.0/
```

The updater copies or installs the complete candidate under `releases/v2.4.0`, verifies the installed files, and then changes the `current` selection. At startup, the launcher resolves that pointer once and pins the resulting release directory for the entire run. The AppImage and helper both come from that pinned directory. A later launch can select a newly activated release without mixing components inside an in-progress run.

The pointer change is the commit point, but its guarantees depend on the filesystem and how readers resolve it. If files must live on separate filesystems, use an activation journal and an explicit recovery procedure.

Privilege also changes the cleanup rule. User-owned staging files can be removed by the launcher. Root-owned release directories should be removed only by the narrow helper after the active, retained, and in-use versions are known. An updater must not garbage-collect a release pinned by a running launcher. Broad recursive cleanup under a privileged prefix is an avoidable risk.

## Verify before retiring the previous release

Define a bounded health contract appropriate to the application. It might check that the application starts, the helper reports a compatible protocol version, required local resources open, and no immediate fatal error appears.

If verification fails, the updater can reselect the previous retained directory and record `activation_failed`. It should not delete the failed candidate immediately. The manifest, logs, selected versions, and health result are the evidence needed to diagnose why an individually valid artifact set failed in its real environment.

Rollback has limits. An older binary may not understand migrated data, and a helper may change state outside the release directory. Irreversible migrations need backup or forward-repair plans rather than a false “undo” button.

Retention should be explicit: keep the active release, the last known working release, and perhaps one failed candidate until evidence is collected. Garbage collection runs after a successful launch and must never infer ownership from neighboring user data.

## Know when startup updates are the wrong policy

Checking the network on every launch fits a user-managed desktop tool that values convenience and can continue with an installed copy. It is a poor fit for disconnected environments, controlled fleets, metered links, or installations whose operators require staged rollout and an approved maintenance window.

The transaction model still applies, but discovery should be separate from launch. An administrator or package repository can deliver the artifact set. Policy can pin a channel, require manual promotion, cache candidates, or disable network access. The updater should respect the deployment authority of its environment.

## Choose the guarantees before choosing the script

The design can be reviewed as six questions:

1. What exact artifact set is compatible?
2. What evidence makes a candidate valid and, separately, authentic?
3. Which step requires privilege, and what does that authority accept?
4. What is the activation commit point?
5. What health contract decides that the new release works?
6. Which previous state remains recoverable after each failure?

The current LOA Logs path answers part of this model: it stages individual downloads, keeps installed binaries available when update discovery fails, narrows helper management through `pkexec`, and preserves useful cleanup and logging behavior. A versioned, manifest-driven activation protocol would extend those properties to the full multi-artifact release.

Thinking in transactions does not require a heavyweight package manager. It requires naming the candidate, keeping compatibility as a set property, separating validation from authorization, and defining recovery before the updater changes the active installation. Once those decisions are explicit, the shell code becomes an implementation of a deployment contract instead of a sequence of hopeful file operations.
