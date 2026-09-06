import { absoluteUrl, SITE_URL } from './site';
import { articlePath, type ArticleEntry } from './articles';

export function escapeXml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export function atomFeed(title: string, feedPath: string, articles: ArticleEntry[]): string {
  const updated = articles[0]?.data.date ?? new Date(0);
  const feedUrl = absoluteUrl(feedPath);
  const feedId = feedPath === '/feeds/all.atom.xml' ? `${SITE_URL}/` : feedUrl;
  const entries = articles.map((article) => {
    const url = absoluteUrl(articlePath(article));
    const tags = article.data.tags.map((tag) => `<category term="${escapeXml(tag)}" />`).join('');
    return `<entry><title>${escapeXml(article.data.title)}</title><id>${url}</id><link href="${url}" /><updated>${article.data.date.toISOString()}</updated><published>${article.data.date.toISOString()}</published><summary>${escapeXml(article.data.description)}</summary>${tags}</entry>`;
  }).join('');
  return `<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>${escapeXml(title)}</title><id>${escapeXml(feedId)}</id><link href="${escapeXml(feedUrl)}" rel="self" type="application/atom+xml" /><link href="${SITE_URL}/" /><updated>${updated.toISOString()}</updated><author><name>Andre Lustosa</name></author>${entries}</feed>`;
}

export function feedResponse(body: string): Response {
  return new Response(body, {
    headers: {
      'Content-Type': 'application/atom+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
}
