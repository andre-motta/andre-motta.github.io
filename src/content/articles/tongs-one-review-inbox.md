---
title: "One Review Inbox for Two Forges"
description: "tongs treats code review as one terminal workflow across GitHub and GitLab, then designs each layer around the differences that remain."
date: "2026-09-06"
category: "Developer Tools"
tags: ["python", "tui", "github", "gitlab", "code-review"]
slug: "tongs-one-review-inbox"
draft: false
featured: false
readTime: "5 min read"
---

Code review is conceptually the same on GitHub and GitLab: find work waiting for you, understand the change, inspect discussion, check automation, and leave a decision. The APIs and vocabulary are different enough that the usual tools still split that work into separate places. I created [tongs](https://github.com/andre-motta/tongs) to make the review loop feel like one terminal workflow while keeping those forge differences explicit inside the implementation.

The project starts with local repositories. tongs scans a configurable directory, reads Git remotes, identifies their forges and hosts, then uses the existing `gh` and `glab` CLI authentication. That has two useful consequences. The application does not need its own token store, and a developer's local checkout becomes the source of truth for which projects belong in the inbox. This is a deliberate product boundary: tongs organizes work the developer has already chosen to check out, rather than trying to become another global forge search engine.

The inbox has three questions built into it: what needs my review, what did I open, and what else is open in this repository? Those become separate views over the same internal model. A user can then scope the inbox to one repository without changing tools or reconstructing a search query. The design treats the application as a queue for review work.

Normalizing the list is the easy part. The harder boundary appears when a reviewer opens a change. GitHub and GitLab represent discussions, review states, CI, and merge readiness differently. tongs puts a forge adapter behind a common client interface, but it does not pretend that every capability has identical semantics. For example, GitLab supports revoking approval directly. GitHub's review model behaves differently. The UI can present the relevant action while the adapter preserves the forge-specific contract.

That distinction suggests a test for cross-provider abstractions. Normalize nouns when the user can safely treat them alike. Preserve verbs when the provider's rules affect the outcome. A pull request and merge request can share a list row. Approval, thread resolution, draft review submission, and merge eligibility need capability-aware behavior.

The internal model therefore needs more than a lowest-common-denominator record. It can expose shared fields plus declared capabilities:

```text
review item
  identity, author, revision, files, status
  capabilities
    can_resolve_thread
    can_revoke_approval
    supports_draft_review
    merge_requirements
```

The UI can remain consistent while unavailable or different actions remain honest. Adding a forge becomes an exercise in implementing and testing capabilities, not filling null fields until the adapter compiles.

The diff view is the center of the workflow. It combines a file tree, syntax-highlighted hunks, word-level changes, folded context, and inline discussion markers. Review actions stay close to the code: select one or more lines, write a comment in a docked editor, reply to an existing thread, resolve it where the forge allows, or prepare a suggestion in an external editor. The public [README](https://github.com/andre-motta/tongs/blob/main/README.md) documents the current behavior and key bindings.

A terminal interface has a specific performance constraint. Rendering a large diff is not useful if it blocks input while it fetches every discussion and pipeline. tongs uses lazy loading and parallel requests, and it stores API responses in a local SQLite cache. List results and diffs have different time-to-live values because their change rates are different. Read operations can use cached values, while mutations invalidate related entries. The cache uses the asynchronous `aiosqlite` API so database calls can be awaited, and WAL mode allows readers and a writer to make progress with less lock contention.

CI is part of review, so it cannot be reduced to a colored badge. The pipeline view has three levels: pipeline, jobs grouped by stage, and the selected job's log. ANSI output is rendered in the terminal, and a reviewer can search the complete log or open it in an editor. Cancel and retry operations use an explicit second keypress. The same confirmation pattern protects merge, close, and discussion-resolution actions.

That distinction between navigation and mutation is one of the design choices I would carry to other terminal tools. Fast keys are valuable for moving through information. State-changing keys need a small amount of friction that is visible, consistent, and easy to cancel. Requiring a second keypress helps guard against an accidental merge without adding a modal dialog to every action.

The plugin system extends the same boundary. Python entry points can register commands, screens, and lifecycle hooks. The application's MCP server is packaged as a plugin rather than wired into the core. The public `claude-fleet-monitor` project can also appear as a tongs screen. That makes the plugin contract something the project itself uses, which tends to expose missing interfaces earlier than a sample extension would.

A plugin boundary also creates authority questions. A screen that only reads normalized review data needs less trust than a command that can merge, retry CI, or invoke an external tool. Registration should describe capabilities, and the host should provide a constrained context instead of handing every plugin raw clients and credentials. The same principle applies to the MCP interface: expose task-level operations with validation and confirmation semantics, rather than a generic authenticated escape hatch.

Failures need provider identity too. A rate limit, stale cache entry, permission denial, and unsupported action may all appear as “could not load review,” but they imply different recovery. The adapter should return a typed failure that preserves the forge response and indicates whether a retry, reauthentication, refresh, or capability fallback is appropriate. Otherwise the common interface removes exactly the information an operator needs.

As of September 6, 2026, tongs is a public MIT-licensed Python project with releases on PyPI. Its architecture is still evolving, including an open proposal for batch review submission in [issue #16](https://github.com/andre-motta/tongs/issues/16). That proposal is a useful example of a feature that cannot be treated as a shared button until each forge's draft-review semantics are understood.

The broader design lesson is that unification should happen at the user's task boundary. A reviewer wants one inbox and one mental model. The implementation still needs to respect every place where GitHub and GitLab disagree. A useful abstraction removes repeated work without erasing the behavior that makes each backend correct.
