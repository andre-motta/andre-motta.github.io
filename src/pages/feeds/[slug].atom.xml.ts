import { getArticles, slugify } from '../../lib/articles';
import { atomFeed, feedResponse } from '../../lib/feed';

export async function getStaticPaths() {
  const articles = await getArticles();
  const categories = [...new Set(articles.map((article) => article.data.category))];
  return categories.map((category) => ({
    params: { slug: slugify(category) },
    props: { category },
  }));
}

export async function GET({ params, props }: { params: { slug?: string }; props: { category: string } }) {
  const articles = (await getArticles()).filter((article) => slugify(article.data.category) === params.slug);
  const category = props.category;
  return feedResponse(atomFeed(`${category} writing`, `/feeds/${params.slug}.atom.xml`, articles));
}
