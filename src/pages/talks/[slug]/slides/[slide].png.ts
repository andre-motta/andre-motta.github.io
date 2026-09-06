import { readFile } from 'node:fs/promises';
import type { APIRoute } from 'astro';
import { lecture } from '../../../../data/lecture';
import { isLectureAvailable, requireLectureAsset, slideNumber } from '../../../../lib/lectures';

export function getStaticPaths() {
  if (!isLectureAvailable(lecture)) return [];
  const total = lecture.originalSlideCount ?? lecture.slides.length;
  return Array.from({ length: total }, (_, index) => index + 1).map((slide) => ({
    params: { slug: lecture.slug, slide: String(slide) },
    props: { lecture },
  }));
}

export const GET: APIRoute = async ({ params }) => {
  const slide = slideNumber(params.slide ?? '');
  const filename = `slide-${String(slide).padStart(2, '0')}.png`;
  const path = requireLectureAsset(lecture, filename, 'slide image');
  return new Response(await readFile(path), {
    headers: {
      'Cache-Control': lecture.draft ? 'no-store' : 'public, max-age=0, must-revalidate',
      'Content-Type': 'image/png',
    },
  });
};
