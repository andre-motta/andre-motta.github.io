# Analytics, crawler guidance, and LinkedIn writing

## Brief

Prepare free usage analytics for alustos.us, publishable crawler guidance, and a
repository-local skill for useful LinkedIn posts that point to full articles.
Preserve the approved Astro design, static GitHub Pages hosting, URLs, and private
content boundary. Andre authorized publication of this prepared work on
September 6, 2026, after approving the expanded llama.cpp article.

Andre confirmed on September 6, 2026 that search and training crawlers may access
the site and that its original content is MIT licensed. He wants useful technical
tidbits, his own voice, and compliance with LinkedIn guidance. His first planned
LinkedIn post will accompany a new article about local llama.cpp serving across
a home network and Tailscale. The expanded Fedora/Vulkan article received
editorial approval on September 6, 2026.

## Analytics recommendation

Research date: September 6, 2026. Recommend **hosted GoatCounter** for the first
release. It combines an open-source application with no hosting bill for a
personal site and avoids operating a database or service on the home network.
Andre selected GoatCounter and created his account during this task, providing
the public endpoint `https://alustosa.goatcounter.com/count`. The integration is
implemented and verified locally, ready for production review. Account dashboard settings have not
been inspected or changed.

| Option | Free service / software | Fit and limits |
| --- | --- | --- |
| [GoatCounter](https://www.goatcounter.com/) | Free hosted personal usage; open-source application | Best fit. Donation-supported, with reasonable-use terms rather than a numerical quota or SLA. |
| [Umami](https://umami.is/pricing) | Free hosted Hobby tier; MIT application | One site, 100K events/month, six-month retention. Confirm free-tier behavior above quota before relying on it. |
| [Cloudflare Web Analytics](https://developers.cloudflare.com/web-analytics/about/) | Free proprietary hosted service | Simple traffic and performance reporting, including for sites outside its proxy. No self-hosting option. |
| [Google Analytics](https://marketingplatform.google.com/about/analytics/terms/us/) | Free Standard service; proprietary | Richer event and acquisition reporting, with more configuration and privacy administration than this site needs. |
| [Plausible](https://plausible.io/self-hosted-web-analytics) | Free AGPL community edition; paid cloud | Self-hosting is possible, but requires a running service, database, TLS, backups, and updates. Cloud has no permanent free tier. |

Open source and zero operating cost are different properties. GitHub Pages serves
static files and cannot host an analytics backend. Self-hosted GoatCounter,
[Umami](https://docs.umami.is/docs/install), or
[Plausible CE](https://github.com/plausible/community-edition) would need separate
infrastructure and ongoing maintenance. A free hosted tier keeps that work outside
this repository, subject to its service terms.

GoatCounter's [terms](https://www.goatcounter.com/help/terms) explicitly include
personal sites within reasonable public usage. Its
[privacy documentation](https://www.goatcounter.com/help/privacy) describes no
cookies or persistent identifiers, aggregate tables by default, and temporary
in-memory processing for visit deduplication. Leave optional individual pageview
storage disabled. Keep the dashboard private unless Andre chooses otherwise.
Do not describe any tracker as collecting literally no data.

Umami's [Cloud FAQ](https://docs.umami.is/docs/cloud/faq) counts pageviews, events,
and stored event properties toward quota; its generic overage wording does not
clearly explain Hobby over-limit handling. Cloudflare's
[limits](https://developers.cloudflare.com/web-analytics/limits/) and
[FAQ](https://developers.cloudflare.com/web-analytics/faq/) document no custom
events or UTM support and retention/sampling limits, making it less suitable for
later campaign comparisons.

### Integration and activation

1. Provider selection and account creation are complete. The public counting
   endpoint is `https://alustosa.goatcounter.com/count`. No password or API key
   belongs in the repo or conversation.
2. Recommended account settings are a private dashboard, aggregate pageviews, and referrer reporting as
   the minimal starting configuration. Geography/device fields and PDF clicks
   are optional. Do not add session replay, identity, or behavioral profiles.
3. `src/components/Analytics.astro` adds the provider's script through
   `src/layouts/BaseLayout.astro`, rendered only for the normal production build.
   Its browser guard requires the canonical HTTPS host, and canonical paths omit
   query strings and fragments. Local previews and other hosts load no tracker. The script's
   public account code is not a secret. No npm dependency or CI secret is needed.
4. The integration uses GoatCounter's [official script](https://www.goatcounter.com/help/start):
   `https://gc.zgo.at/count.js` with `data-goatcounter` set to the account's HTTPS
   `/count` endpoint, loaded asynchronously with Astro `is:inline`. Do not copy a
   placeholder account code into the deployed site. No package or workflow changes
   were needed.
5. If desired, add `data-goatcounter-click="cv-pdf-download"` to the PDF links
   in About and CV. This measures a link click, not completion of a download or
   a PDF opened directly. [GoatCounter events](https://www.goatcounter.com/help/events)
6. Include `/privacy.html`, linked from the footer, describing the provider's
   data processing and the existing local theme preference. Review the concrete change, run Astro
   check/build/artifact validation, and confirm local previews emit no tracker.
7. After authorized publication, verify one production pageview and any enabled
   click event in the dashboard, inspect the browser request for unintended URL
   data, and confirm the site remains usable when the script is blocked.
   Removing the script and redeploying stops future client-side collection;
   provider-side retention/deletion is managed separately.

Andre considered a public visitor counter and agreed to omit it after design
review. No counter widget or public-count setting is part of this change.

Start with trends, popular articles, and referring sites. LinkedIn-origin visits
help evaluate the new posts, but ad blockers, disabled JavaScript, stripped
referrers, and bots limit accuracy. If campaign links are later requested, verify
which dimensions the chosen provider records before assigning UTM parameters.
Avoid query strings containing personal information. Client-side tracking does
not measure all crawler traffic and cannot serve as DDoS monitoring.

## Crawler decisions

Generate `/llms.txt` from the public profile and approved, non-draft articles,
including canonical HTML links, attribution guidance, and a link to the MIT
content license. Keep the list public-only even in preview. Do not export private
notes, source frontmatter, or skill instructions. The format is a
[community proposal](https://llmstxt.org/), not a guarantee that every AI tool
will discover or follow the file. Markdown mirrors can be considered later if
there is evidence of a need; the current guide links to readable static HTML.

`/robots.txt` allows all crawlers and asks supporting clients to wait ten seconds
between requests. Its comments request caching and backoff. It intentionally has
no training-agent blocklist, private-path inventory, or nonexistent sitemap URL.
The [Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html) is
voluntary and does not authorize access or enforce a request budget.
[Google ignores Crawl-delay](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec).
Allowing crawling does not waive the terms in `/license.txt`.

### Availability and abusive traffic

No static file can prevent a DDoS attack. GitHub Pages controls serving and may
rate-limit requests; its documented soft bandwidth limit is 100 GB per month.
The repository cannot configure per-client throttling on GitHub's servers.
[GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

If stronger controls are needed, evaluate a Cloudflare Free proxy in front of the
custom domain as a separate infrastructure change. Its standard DDoS protection
is available on the Free plan. This is a proprietary managed service, not an OSS
component running on Pages. Its analytics beacon alone provides no traffic
protection. [Cloudflare DDoS documentation](https://developers.cloudflare.com/ddos-protection/)

Before a proxy change, inspect the actual DNS and existing hosting configuration,
review the exact record changes, verify TLS to GitHub Pages, and preserve domain
verification and unrelated DNS records. Test article, feed, PDF, and crawler
access after cutover. Rollback restores the recorded DNS state. A proxy protects
traffic routed through it; GitHub's underlying Pages endpoint may remain reachable.
Rate-limit thresholds need actual traffic evidence and plan-specific capability
checks; a shared IP or asset burst must not automatically block legitimate users.
No DNS, firewall, proxy, or account settings have been changed by this work.

## LinkedIn skill

The reusable skill lives in `.agents/skills/linkedin-posts/`. It reads a complete
article, chooses a concrete technical angle, drafts a standalone takeaway and
canonical link, and checks claim status and voice. It distinguishes draft article
URLs from verified live pages. It produces copy for Andre to publish manually.
It does not create an automation or interact with his LinkedIn account.

The skill uses [LinkedIn's feed guidance](https://news.linkedin.com/2026/ImprovingTheFeed)
to favor substantive professional perspectives and avoid engagement bait. It
also avoids automated comments and engagement pods, consistent with
[LinkedIn's authenticity guidance](https://news.linkedin.com/2026/authentic-content-and-conversations).
Length and formatting defaults are editorial choices, not purported algorithm
rules. Engagement improvement is an experiment, not a promised result.

When Andre supplies results, compare equivalent observation windows and separate
impressions from useful replies and article visits. Keep performance records and
drafts private. Do not infer missing metrics or attribute causal effects from a
few posts. No posting schedule is imposed.

## Work items

- Astra: research integration, skill, licensing and crawler policy, article editing.
- Sol / high: free analytics comparison and technical review.
- Luna / xhigh: generated crawler guide and artifact checks.
- Sol / high: source-grounded llama.cpp article, deployment validation, and first
  LinkedIn draft under the new skill.

## Evidence and handoff

Prepared on `codex/analytics-crawlers-linkedin`:

- GoatCounter pageview integration and Privacy page, with no public visitor counter.
- Generated public-only `llms.txt`, permissive `robots.txt`, and original-content
  MIT license. The advisory delay does not provide DDoS protection.
- Repository-local LinkedIn skill and an editorially reviewed llama.cpp article
  approved for publication, including Fedora/Vulkan build and run instructions.
  The LinkedIn draft is kept in the private wiki for manual posting.

Checks on September 6, 2026:

- `npm run check`: 35 files, zero errors, warnings, or hints.
- `npm run build` and production artifact verifier passed. Existing published
  articles, feeds, domain, and CV remain present. After approval, the llama.cpp
  article is included in production routes, feeds, and llms.txt.
- `npm run build:preview` and preview artifact verifier passed, initially with
  one draft marker before article approval. Preview analytics exclusion and
  public-only discovery checks passed.
- A mocked Node browser environment checked the analytics loader: the canonical
  HTTPS host adds one asynchronous script with the supplied endpoint and a
  pathname-only payload; localhost, other hosts, HTTP, and a nonstandard port add
  none. No fake pageviews were sent to the provider.
- Skill structural validation and `git diff --check` passed. The skill is visible
  to Git through a narrow ignore exception, while private wiki files stay ignored.
- Desktop/mobile browser inspection covered the privacy notice, article heading,
  code examples, table, theme switching, links, and keyboard focus. No page-level
  horizontal overflow was observed at 390 pixels. The article carries `noindex,
  nofollow` in local preview. No new motion was introduced.
- Sol technical review completed; the article explicitly explains that plain LAN
  HTTP exposes both prompts and the API credential. No performance benchmark or
  current remote-client test is claimed.
- A private in-memory comparison against the supplied deployment context found
  no known credentials or private network identifiers in 156 source/generated
  files. Inputs and secret values were kept outside the public tree and logs.

The article is approved and production-eligible. Andre authorized pushing this
release so he can share its public URL on LinkedIn. The release branch has been
fast-forwarded to include the GitHub Actions update already on `origin/master`.
Final staging and commit-message approval precede the authorized push; no release
commit or deployment has occurred yet. No DNS or LinkedIn account action is part
of this release. Provider dashboard receipt still needs post-deployment
verification. Detailed research, conversation summaries, and private evidence
remain in the local wiki.
