import type { Action, CallEvent, CallPreview, CheckResponse, ConsentNotice, Draft, TranscribeResponse, NextResponse, PortalKit, Profile, TrackedCase, UnderstandResponse, UnderstoodCase } from './types';

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

function detailText(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const d = (body as { detail: unknown }).detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return d.map((x) => (x && typeof x === 'object' && 'msg' in x ? String((x as { msg: unknown }).msg) : String(x))).join('; ');
  }
  return fallback;
}

export function makeApi(baseUrl: string, fetchImpl: typeof fetch = fetch, timeoutMs = 25000, token?: string) {
  const base = baseUrl.replace(/\/+$/, '');

  async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    let res: Response;
    try {
      res = await fetchImpl(`${base}${path}`, {
        method,
        headers: {
          ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: ctrl.signal,
      });
    } catch {
      throw new ApiError(`Cannot reach the Nivaran server at ${base}. Is it running, and is your phone on the same Wi-Fi?`);
    } finally {
      clearTimeout(timer);
    }
    let json: unknown = null;
    try {
      json = await res.json();
    } catch {
      json = null;
    }
    if (!res.ok) throw new ApiError(detailText(json, `The server answered with an error (${res.status}).`), res.status);
    return json as T;
  }

  return {
    understand: (message: string) => request<UnderstandResponse>('POST', '/cases/understand', { message }),
    transcribe: (audioB64: string, mimeType: string, language: string | null = null) =>
      request<TranscribeResponse>('POST', '/speech/transcribe', { audio_b64: audioB64, mime_type: mimeType, language }),
    callPreview: (id: string, language: string) => request<CallPreview>('GET', `/tracked-cases/${id}/call/preview?language=${encodeURIComponent(language)}`),
    startCall: (id: string, language: string) => request<{ call_id: string; mode: string }>('POST', `/tracked-cases/${id}/call`, { language, confirm: true }),
    hangUp: (id: string, callId: string) => request<{ ended: boolean }>('POST', `/tracked-cases/${id}/call/${callId}/hangup`),
    callEvents: (id: string, since: number) => request<CallEvent[]>('GET', `/tracked-cases/${id}/call/events?since=${since}`),
    consentNotice: () => request<ConsentNotice>('GET', '/tracked-cases/consent-notice'),
    createCase: (c: UnderstoodCase, userName: string | null, consent: boolean, adult: boolean) =>
      request<TrackedCase>('POST', '/tracked-cases', { case: c, user_name: userName, consent, adult }),
    listCases: () => request<TrackedCase[]>('GET', '/tracked-cases'),
    getCase: (id: string) => request<TrackedCase>('GET', `/tracked-cases/${id}`),
    nextStep: (id: string) => request<NextResponse>('GET', `/tracked-cases/${id}/next`),
    addNote: (id: string, on: string, text: string, docket: string | null) =>
      request<TrackedCase>('POST', `/tracked-cases/${id}/events`, { on, kind: 'note', text, docket }),
    markContacted: (id: string, on: string, rung: string, channel: string, text: string) =>
      request<TrackedCase>('POST', `/tracked-cases/${id}/events`, { on, kind: 'contacted', rung, channel, text }),
    finish: (id: string, on: string, kind: 'resolved' | 'closed') => request<TrackedCase>('POST', `/tracked-cases/${id}/events`, { on, kind }),
    makeDraft: (id: string) => request<Draft>('POST', `/tracked-cases/${id}/drafts`),
    editDraft: (draftId: string, subject: string, body: string) => request<Draft>('PATCH', `/drafts/${draftId}`, { subject, body }),
    approveDraft: (draftId: string) => request<Draft>('POST', `/drafts/${draftId}/approve`),
    rejectDraft: (draftId: string) => request<Draft>('POST', `/drafts/${draftId}/reject`),
    sendDraft: (draftId: string) => request<{ draft: Draft; case: TrackedCase }>('POST', `/drafts/${draftId}/send`),
    portalKit: (id: string) => request<PortalKit>('GET', `/tracked-cases/${id}/portal-kit`),
    checkReplies: (id: string) => request<CheckResponse>('POST', `/tracked-cases/${id}/check-replies`),
    getProfile: async () => (await request<{ profile: Profile | null }>('GET', '/profile')).profile,
    saveProfile: async (p: Profile) => (await request<{ profile: Profile }>('PUT', '/profile', p)).profile,
    deleteProfile: () => request<{ deleted: boolean }>('DELETE', '/profile'),
    deleteCase: (id: string) => request<{ deleted: string }>('DELETE', `/tracked-cases/${id}`),
  };
}

export type Api = ReturnType<typeof makeApi>;
export type { Action };
