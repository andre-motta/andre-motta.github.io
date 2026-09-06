export const SITE_URL = 'https://alustos.us';
export const FEED_PATH = '/feeds/all.atom.xml';

export function absoluteUrl(path: string): string {
  return new URL(path, SITE_URL).toString();
}

export function cleanDescription(value: string | undefined, fallback: string): string {
  const description = value?.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
  return (description || fallback).slice(0, 160);
}
