export type PresenterMode = 'original' | 'web';

export const PRESENTER_PROTOCOL_VERSION = 1;

export interface PresenterFragment {
  session?: string;
  mode: PresenterMode;
  slide: number;
}

export interface PresenterStateMessage {
  version: typeof PRESENTER_PROTOCOL_VERSION;
  type: 'state' | 'heartbeat';
  session: string;
  mode: PresenterMode;
  slide: number;
  total: number;
  sequence: number;
}

export interface PresenterReadyMessage {
  version: typeof PRESENTER_PROTOCOL_VERSION;
  type: 'ready';
  session: string;
  mode: PresenterMode;
}

export interface PresenterCommandMessage {
  version: typeof PRESENTER_PROTOCOL_VERSION;
  type: 'command';
  command: 'setSlide' | 'previous' | 'next' | 'first' | 'last';
  session: string;
  mode: PresenterMode;
  slide?: number;
  sequence: number;
}

export interface PresenterEndedMessage {
  version: typeof PRESENTER_PROTOCOL_VERSION;
  type: 'ended';
  session: string;
  mode: PresenterMode;
}

export type PresenterMessage = PresenterStateMessage | PresenterReadyMessage | PresenterCommandMessage | PresenterEndedMessage;

export function presenterChannelName(slug: string, mode: PresenterMode, session: string): string {
  return `alustos-lecture-presenter:${slug}:${mode}:${session}`;
}

export function presenterFragment(fragment: PresenterFragment): string {
  const params = new URLSearchParams({ mode: fragment.mode, slide: String(fragment.slide) });
  if (fragment.session) params.set('session', fragment.session);
  return `#${params.toString()}`;
}

export function parsePresenterFragment(hash: string): PresenterFragment | null {
  const params = new URLSearchParams(hash.replace(/^#/, ''));
  const mode = params.get('mode');
  const slide = Number(params.get('slide'));
  if ((mode !== 'original' && mode !== 'web') || !Number.isInteger(slide) || slide < 1) return null;
  const session = params.get('session') || undefined;
  if (session && !/^[A-Za-z0-9_-]{8,128}$/.test(session)) return null;
  return { session, mode, slide };
}

export function createPresenterSession(): string | null {
  const cryptoApi = globalThis.crypto;
  if (!cryptoApi) return null;
  if (typeof cryptoApi.randomUUID === 'function') return cryptoApi.randomUUID();
  const bytes = new Uint8Array(16);
  cryptoApi.getRandomValues(bytes);
  return Array.from(bytes, (value) => value.toString(16).padStart(2, '0')).join('');
}

export function parsePresenterMessage(value: unknown, expected: { session: string; mode: PresenterMode }): PresenterMessage | null {
  if (!value || typeof value !== 'object') return null;
  const message = value as Record<string, unknown>;
  if (message.version !== PRESENTER_PROTOCOL_VERSION || message.session !== expected.session || message.mode !== expected.mode || typeof message.type !== 'string') return null;
  if (message.type === 'ready' || message.type === 'ended') return message as unknown as PresenterMessage;
  if (message.type === 'state' || message.type === 'heartbeat') {
    if (!Number.isInteger(message.slide) || !Number.isInteger(message.total) || !Number.isInteger(message.sequence) || Number(message.slide) < 1 || Number(message.total) < 1 || Number(message.slide) > Number(message.total) || Number(message.sequence) < 0) return null;
    return message as unknown as PresenterMessage;
  }
  if (message.type === 'command' && ['previous', 'next', 'first', 'last'].includes(message.command as string)) {
    if (!Number.isInteger(message.sequence) || Number(message.sequence) < 0) return null;
    return message as unknown as PresenterMessage;
  }
  if (message.type === 'command' && message.command === 'setSlide') {
    if (!Number.isInteger(message.slide) || !Number.isInteger(message.sequence) || Number(message.slide) < 1 || Number(message.sequence) < 0) return null;
    return message as unknown as PresenterMessage;
  }
  return null;
}

export function validSlide(slide: number, total: number): boolean {
  return Number.isInteger(slide) && slide >= 1 && slide <= total;
}
