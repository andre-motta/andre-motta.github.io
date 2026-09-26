# Analytics and crawler guidance

Operational reference for analytics, crawler files, and traffic controls.

## Analytics

### Setup

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

The site intentionally has no public visitor counter widget or public-count setting.

Start with trends, popular articles, and referring sites. LinkedIn-origin visits
help evaluate the new posts, but ad blockers, disabled JavaScript, stripped
referrers, and bots limit accuracy. If campaign links are later requested, verify
which dimensions the chosen provider records before assigning UTM parameters.
Avoid query strings containing personal information. Client-side tracking does
not measure all crawler traffic and cannot serve as DDoS monitoring.


## Crawler guidance

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
No DNS, firewall, proxy, or account-level traffic controls are configured today.
