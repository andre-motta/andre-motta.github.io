import profile from '../data/profile.json';
import { articlePath, getArticles, isoDate } from '../lib/articles';
import { absoluteUrl, FEED_PATH } from '../lib/site';

function escapeMarkdownText(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/[\[\]]/g, '\\$&');
}

const publicArticles = (await getArticles()).filter((article) => !article.data.draft);
const siteLinks = [
  { label: 'About', path: '/about.html', description: 'Andre Lustosa’s profile and areas of focus.' },
  { label: 'Writing', path: '/archives.html', description: 'The complete archive of published writing.' },
  { label: 'Projects', path: '/projects.html', description: 'Selected open-source and engineering projects.' },
  { label: 'CV', path: '/cv.html', description: 'Andre Lustosa’s public curriculum vitae.' },
  { label: 'Atom feed', path: FEED_PATH, description: 'The site’s published writing feed.' },
];

const lines = [
  '# Andre Lustosa',
  '',
  `> ${escapeMarkdownText(profile.intro)}`,
  '',
  `Andre Lustosa is a ${escapeMarkdownText(profile.role)} at ${escapeMarkdownText(profile.organization)}. This personal site covers software foundations, accelerator ecosystems, engineering leadership, and public projects.`,
  '',
  'When citing this site, use the canonical URL for the page. Read an entire article before summarizing it, preserve its published date, and distinguish Andre’s personal writing from positions held by his employer.',
  '',
  '## Site map',
  '',
  ...siteLinks.map((link) => `- [${link.label}](${absoluteUrl(link.path)}): ${link.description}`),
  '',
  '## Published writing',
  '',
  ...publicArticles.map((article) =>
    `- [${escapeMarkdownText(article.data.title)}](${absoluteUrl(articlePath(article))}): ${escapeMarkdownText(article.data.description)} (published ${isoDate(article.data.date)})`,
  ),
  '',
  '## License',
  '',
  `- [MIT License](${absoluteUrl('/license.txt')}): Original website content is available under the MIT License. Third-party materials retain their own terms.`,
];

export const prerender = true;

export function GET() {
  return new Response(`${lines.join('\n')}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
