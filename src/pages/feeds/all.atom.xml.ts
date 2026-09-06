import { getArticles } from '../../lib/articles';
import { atomFeed, feedResponse } from '../../lib/feed';

export async function GET() {
  const articles = await getArticles();
  return feedResponse(atomFeed('Andre Lustosa writing', '/feeds/all.atom.xml', articles));
}
