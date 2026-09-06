import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { isAbsolute, relative, resolve } from 'node:path';

export interface LectureColumn {
  title: string;
  items: string[];
}

export interface LectureSource {
  label: string;
  url: string;
}

export type LectureBlock =
  | { kind: 'text'; heading?: string; lines: string[]; callout?: string }
  | { kind: 'bullets'; heading?: string; items: string[] }
  | { kind: 'columns'; columns: LectureColumn[] }
  | { kind: 'table'; headers: string[]; rows: string[][]; headerless?: boolean }
  | { kind: 'flow'; items: string[] }
  | { kind: 'stats'; items: Array<{ value: string; label: string[] }> }
  | { kind: 'links'; links: LectureSource[] };

export interface LectureSlide {
  section: string;
  title: string;
  lead?: string;
  bullets?: string[];
  columns?: LectureColumn[];
  sources?: LectureSource[];
  blocks?: LectureBlock[];
}

export interface Lecture {
  slug: string;
  title: string;
  subtitle: string;
  event: string;
  date: string;
  author: string;
  articlePath: string;
  draft: boolean;
  slides: LectureSlide[];
  originalSlideCount?: number;
}

export interface LectureTranscript {
  slide: number;
  text: string[];
}

export interface PresenterCue {
  number: number;
  title: string;
  minutes: number;
  mainPoint: string;
  cues: string[];
  qualification: string;
  transition: string;
  articleSection: { title: string; href: string };
}

/** Draft lectures are available only in the explicit local preview mode. */
export function isLecturePreviewEnabled(): boolean {
  return import.meta.env.INCLUDE_DRAFTS === 'true' && (import.meta.env.DEV || import.meta.env.MODE === 'preview');
}

export function isLectureAvailable(item: Lecture): boolean {
  return !item.draft || isLecturePreviewEnabled();
}

export function lectureSlideCount(item: Lecture): number {
  return item.originalSlideCount ?? item.slides.length;
}

export function lectureSlideUrl(item: Lecture, slide: number): string {
  return `/talks/${item.slug}/slides/${slide}.png`;
}

export function lectureRoute(item: Lecture, variant: 'chooser' | 'original' | 'web'): string {
  if (variant === 'chooser') return `/talks/${item.slug}.html`;
  return `/talks/${item.slug}/${variant}.html`;
}

export function lecturePresenterRoute(item: Pick<Lecture, 'slug'>): string {
  return `/talks/${item.slug}/presenter.html`;
}

/**
 * Draft assets are generated locally. Approved lectures use their reviewed
 * assets from the checked-in presentation-assets/<slug> directory.
 */
export function lectureAssetDirectory(item: Lecture): string {
  return resolve(process.cwd(), item.draft ? '.generated/lecture' : 'presentation-assets', ...(item.draft ? [] : [item.slug]));
}

export function lectureAssetPath(item: Lecture, filename: string): string {
  const directory = lectureAssetDirectory(item);
  const assetPath = resolve(directory, filename);
  const pathFromDirectory = relative(directory, assetPath);
  if (pathFromDirectory.startsWith('..') || isAbsolute(pathFromDirectory)) {
    throw new Error(`Lecture asset path escapes the asset directory: ${filename}`);
  }
  return assetPath;
}

export function requireLectureAsset(item: Lecture, filename: string, kind = 'asset'): string {
  const assetPath = lectureAssetPath(item, filename);
  if (!existsSync(assetPath)) {
    const sourceDescription = item.draft ? '.generated/lecture' : `presentation-assets/${item.slug}`;
    throw new Error(`Missing lecture ${kind} "${filename}" in ${sourceDescription}. Prepare the reviewed lecture assets before building.`);
  }
  return assetPath;
}

export async function readLectureTranscript(item: Lecture): Promise<LectureTranscript[]> {
  const transcriptPath = lectureAssetPath(item, 'transcript.json');
  try {
    const parsed: unknown = JSON.parse(await readFile(transcriptPath, 'utf8'));
    if (!Array.isArray(parsed)) throw new Error('expected an array');
    const entries = parsed.map((entry, index) => {
      if (!entry || typeof entry !== 'object') throw new Error(`entry ${index + 1} is not an object`);
      const candidate = entry as { slide?: unknown; text?: unknown };
      if (!Number.isInteger(candidate.slide) || !Array.isArray(candidate.text) || !candidate.text.every((line) => typeof line === 'string')) {
        throw new Error(`entry ${index + 1} has an invalid slide or text field`);
      }
      return { slide: candidate.slide as number, text: candidate.text as string[] };
    });
    const expected = lectureSlideCount(item);
    const slideNumbers = new Set(entries.map((entry) => entry.slide));
    if (entries.length !== expected || slideNumbers.size !== expected || Array.from({ length: expected }, (_, index) => index + 1).some((number) => !slideNumbers.has(number))) {
      throw new Error(`expected one transcript entry for each of ${expected} slides, found ${entries.length}`);
    }
    return entries;
  } catch (error) {
    if (error instanceof Error && (error.message.startsWith('entry ') || error.message.startsWith('expected one transcript') || error.message === 'expected an array')) {
      throw new Error(`Invalid lecture transcript at ${transcriptPath}: ${error.message}`);
    }
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      throw new Error(`Missing lecture transcript at ${transcriptPath}. Prepare the reviewed lecture assets before building.`);
    }
    if (error instanceof Error) {
      throw new Error(`Invalid lecture transcript at ${transcriptPath}: ${error.message}`);
    }
    throw error;
  }
}

export async function readPresenterCues(item: Lecture): Promise<PresenterCue[]> {
  const cuesPath = lectureAssetPath(item, 'presenter-cues.json');
  try {
    const parsed: unknown = JSON.parse(await readFile(cuesPath, 'utf8'));
    if (!Array.isArray(parsed)) throw new Error('expected an array');
    const expected = lectureSlideCount(item);
    if (parsed.length !== expected) throw new Error(`expected one cue record for each of ${expected} slides, found ${parsed.length}`);
    return parsed.map((entry, index) => {
      if (!entry || typeof entry !== 'object') throw new Error(`entry ${index + 1} is not an object`);
      const candidate = entry as Record<string, unknown>;
      const number = candidate.number;
      const title = candidate.title;
      const minutes = candidate.minutes;
      const mainPoint = candidate.main_point;
      const cues = candidate.cues;
      const qualification = candidate.qualification;
      const transition = candidate.transition;
      const articleSection = candidate.article_section;
      if (!Number.isInteger(number) || number !== index + 1 || typeof title !== 'string' || title.trim() === '' || typeof minutes !== 'number' || !Number.isFinite(minutes) || minutes <= 0 || typeof mainPoint !== 'string' || mainPoint.trim() === '' || !Array.isArray(cues) || cues.length !== 4 || !cues.every((cue) => typeof cue === 'string' && cue.trim() !== '') || typeof qualification !== 'string' || qualification.trim() === '' || typeof transition !== 'string' || transition.trim() === '' || !articleSection || typeof articleSection !== 'object') {
        throw new Error(`entry ${index + 1} has invalid presenter cue fields`);
      }
      const article = articleSection as Record<string, unknown>;
      if (typeof article.title !== 'string' || article.title.trim() === '' || typeof article.href !== 'string' || !article.href.startsWith(`${item.articlePath}#`) || article.href.slice(item.articlePath.length + 1).trim() === '') throw new Error(`entry ${index + 1} has an invalid article section`);
      if (title !== item.slides[index]?.title) throw new Error(`entry ${index + 1} title does not match slide ${index + 1}`);
      return {
        number,
        title,
        minutes,
        mainPoint,
        cues: cues as string[],
        qualification,
        transition,
        articleSection: { title: article.title, href: article.href },
      };
    });
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      throw new Error(`Missing presenter cues at ${cuesPath}. Prepare the approved lecture assets before building.`);
    }
    if (error instanceof Error) throw new Error(`Invalid presenter cues at ${cuesPath}: ${error.message}`);
    throw error;
  }
}

export function transcriptForSlide(transcript: LectureTranscript[], slide: number): string[] {
  return transcript.find((entry) => entry.slide === slide)?.text ?? [];
}

export function slideNumber(value: string | number): number {
  const number = typeof value === 'number' ? value : Number.parseInt(value, 10);
  if (!Number.isInteger(number) || number < 1) throw new Error(`Invalid lecture slide number: ${value}`);
  return number;
}
