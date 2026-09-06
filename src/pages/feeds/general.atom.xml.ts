import { atomFeed, feedResponse } from '../../lib/feed';

export function GET() {
  return feedResponse(atomFeed('General writing', '/feeds/general.atom.xml', []));
}
