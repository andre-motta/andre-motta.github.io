---
title: "tongs 1.0: Every Forge, One Place"
description: "tongs reached 1.0 with split diffs, crash-safe review drafts, an MCP server, a desktop beta, signed releases, a trailer, and a new home at tongs.tools."
date: "2026-09-27"
category: "Developer Tools"
tags: ["python", "tui", "github", "gitlab", "code-review", "mcp"]
slug: "tongs-1-0"
draft: false
featured: false
readTime: "6 min read"
---

[tongs](https://github.com/andre-motta/tongs) is 1.0. The first commit landed on July 18, 2026, and [1.0.0](https://www.tongs.tools/releases/v1.0.0/) shipped on September 10. Two patch releases followed today, so the version to install is [1.0.2](https://www.tongs.tools/releases/v1.0.2/):

```bash
pipx install tongs
```

It also has a [58-second trailer](https://www.youtube.com/watch?v=rqaEB2l_1w4) and a rebuilt home at [www.tongs.tools](https://www.tongs.tools). This post is mostly a tour.

## What it is

tongs is a keyboard-driven review inbox for GitHub pull requests and GitLab merge requests. It scans the repositories you already have checked out, reads their remotes, and gathers every open review into one list: what needs my review, what I opened, and what else is open. Credentials come from the `gh` and `glab` CLIs, `~/.netrc`, or the system keyring. tongs stores no tokens of its own.

I wrote about the design behind the shared inbox in [One Review Inbox for Two Forges](/blog/2026/tongs-one-review-inbox.html): normalize the nouns a reviewer can treat alike, and keep the verbs where each forge's rules change the outcome. That idea held up through 1.0. What changed is how much of the review loop now lives in one place.

## What 1.0 does

**Diffs you can actually review in.** Unified diffs with word-level highlights and syntax colors, or a split view with `v`. Comment on a line or a selection, reply to threads, resolve them where the forge allows, and write suggestions in your own editor.

**Review drafts that survive.** `Ctrl+G` starts a review. Comments collect in a local draft and submit once, as one review with a verdict. Quit or crash and the draft is still there. If a submission is interrupted halfway, tongs reconciles what the forge already received instead of sending it twice.

**Pipelines next to the code.** The pipeline tab drills from pipelines to jobs to a job log with search, and can retry or cancel jobs. `F2` sends a log to your editor as plain text.

**An MCP server.** With `pip install "tongs[mcp]"`, `tongs-mcp` exposes merge requests to AI assistants such as Claude Code and Codex over stdio, using the same forge configuration and credentials as the terminal app.

**A desktop app, in beta.** An optional Electron workspace over the same repositories, reviews, and drafts. You review on the diff: hover a line, and the composer opens under it. Pending comments carry a badge and stay editable in place until you submit. The terminal app remains the default, and plain `tongs` never downloads or starts the desktop app on its own.

**A plugin system**, a local SQLite cache with separate lifetimes for lists and diffs, and credentials that refresh themselves: since 1.0.1, a rotated or expired token is picked up on the next request instead of requiring a restart.

## Shipping it properly

`tongs --install-desktop` downloads the desktop archive attached to the matching GitHub Release and verifies its release manifest against a GitHub-managed Sigstore attestation before installing anything. Each release also carries an SBOM with its own attestation, `SHA256SUMS`, and unsigned beta Fedora RPMs.

In 1.0.2, every job that signs and publishes the desktop release, and the job that builds the PyPI packages, installs only hash-locked Python packages, including the build backend. The desktop archive builder installs only pinned, hash-checked RPMs with every package repository disabled. A test checks that every CI workflow keeps checkout credentials out of the working tree and has a timeout, so the rule cannot quietly erode.

## A trailer and a real home

A developer tool does not strictly need a trailer, but tongs has one. [It runs 58 seconds](https://www.youtube.com/watch?v=rqaEB2l_1w4) and came with a full brand kit: the steel tongs holding a glowing cube, the wordmark, and the "Every forge. One place." line.

[www.tongs.tools](https://www.tongs.tools) was rebuilt on Astro and Starlight. The homepage walks through the product with short looping demos on demo data, from "thirty-seven browser tabs across both forges" down to one terminal. The documentation lives in the repository and builds strictly: a broken page link or anchor fails the build. Every release has its own notes, and a known-issues page lists each open defect with the patch release planned to fix it.

## The first advisory

1.0.2 is also tongs' first security release, with two advisories. I found both in an AI-assisted review of the codebase run with frontier models, then verified and fixed them.

The more interesting one is [GHSA-4cw3-82cv-q28x](https://github.com/andre-motta/tongs/security/advisories/GHSA-4cw3-82cv-q28x). The MCP server accepted any hostname containing `github` or `gitlab`, looked up a token for it, and sent the request there. In the terminal app, a person picks which repositories to open, so a loose hostname rule looked like a convenience. Behind MCP, the tool calls are chosen by a language model that also reads merge request text, and untrusted text could steer a call toward a host like `github.attacker.example`. The same shortcut became a way to hand a token to someone else.

The fix does not depend on the model noticing anything. The MCP server now accepts only `github.com`, `gitlab.com`, and hosts listed in `config.toml`, and rejects everything else before any credential lookup or request. tongs also stopped guessing the forge type from hostnames everywhere, so a self-hosted instance is an explicit configuration choice. The second advisory, [GHSA-v7v3-jh3w-pj3h](https://github.com/andre-motta/tongs/security/advisories/GHSA-v7v3-jh3w-pj3h), stopped tongs from sending the password in the `default` entry of `~/.netrc` to a forge that no `machine` line names.

The lesson is small and general: when you put a model in front of an existing tool, every convenient default gets re-read by something that can be persuaded. If you run `tongs-mcp`, upgrade to 1.0.2.

## Not just mine anymore

Several fixes in 1.0.2 were planned for later patch releases and arrived early as community contributions. Thanks to [@GhostCoder6969](https://github.com/GhostCoder6969), [@tayfuryldz](https://github.com/tayfuryldz), and [@Tiyatrotist](https://github.com/Tiyatrotist) for their work. The [known-issues page](https://www.tongs.tools/releases/known-issues/) maps out 1.0.3 through 1.0.9, one group of fixes each.

If you review code across GitHub and GitLab and live in a terminal, give it a try:

```bash
pipx install tongs
tongs
```

Then tell me what breaks on the [issue tracker](https://github.com/andre-motta/tongs/issues).
