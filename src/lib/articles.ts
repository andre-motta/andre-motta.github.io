import { getCollection, type CollectionEntry } from 'astro:content';

export type ArticleEntry = CollectionEntry<'articles'>;

const previewDrafts =
  import.meta.env.INCLUDE_DRAFTS === 'true' &&
  (import.meta.env.DEV || import.meta.env.MODE === 'preview');

export async function getArticles(): Promise<ArticleEntry[]> {
  const articles = await getCollection('articles', ({ data }) => previewDrafts || !data.draft);
  return articles.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export function articlePath(article: ArticleEntry): string {
  return `/blog/${article.data.date.getUTCFullYear()}/${article.data.slug}.html`;
}

export function categorySlug(category: string): string {
  return slugify(category);
}

export function categoryPath(category: string): string {
  return `/category/${categorySlug(category)}.html`;
}

export function tagSlug(tag: string): string {
  return slugify(tag);
}

export function tagPath(tag: string): string {
  return `/tag/${tagSlug(tag)}.html`;
}

export function slugify(value: string): string {
  return value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  }).format(date);
}

export function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export function relatedArticles(current: ArticleEntry, articles: ArticleEntry[]): ArticleEntry[] {
  const currentTags = new Set(current.data.tags.map((tag) => tag.toLowerCase()));
  return articles
    .filter((article) => article.id !== current.id)
    .map((article) => {
      const sharedTags = article.data.tags.filter((tag) => currentTags.has(tag.toLowerCase())).length;
      const sameCategory = article.data.category === current.data.category ? 1 : 0;
      return { article, score: sharedTags * 2 + sameCategory };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || b.article.data.date.getTime() - a.article.data.date.getTime())
    .slice(0, 3)
    .map(({ article }) => article);
}
