import { readFile } from 'node:fs/promises';
import type { APIRoute } from 'astro';
import { lecture } from '../../../data/lecture';
import { isLectureAvailable, requireLectureAsset } from '../../../lib/lectures';

export function getStaticPaths() {
  if (!isLectureAvailable(lecture)) return [];
  return [{ params: { slug: lecture.slug }, props: { lecture } }];
}

export const GET: APIRoute = async () => {
  const path = requireLectureAsset(lecture, 'original.pdf', 'PDF');
  return new Response(await readFile(path), {
    headers: {
      'Cache-Control': lecture.draft ? 'no-store' : 'public, max-age=0, must-revalidate',
      'Content-Disposition': `inline; filename="${lecture.slug}-slides.pdf"`,
      'Content-Type': 'application/pdf',
    },
  });
};
