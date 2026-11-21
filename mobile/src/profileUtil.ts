import type { CaseState, TrackedCase } from './types';

export const GENDERS: { code: string; label: string }[] = [
  { code: 'female', label: 'Female' }, { code: 'male', label: 'Male' }, { code: 'non_binary', label: 'Non-binary' }, { code: 'prefer_not_to_say', label: 'Prefer not to say' },
];

/** "15/06/2000" (or 15-06-2000, 15.6.2000) -> "2000-06-15"; null when it is not a real calendar date. */
export function parseDob(text: string): string | null {
  const m = /^\s*(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})\s*$/.exec(text);
  if (!m) return null;
  const [d, mo, y] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const dt = new Date(Date.UTC(y, mo - 1, d));
  if (dt.getUTCFullYear() !== y || dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== d) return null;
  return `${y}-${String(mo).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}

export function dobToInput(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
}

export function ageOn(iso: string, today: Date): number {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return 0;
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  return today.getFullYear() - y - ((today.getMonth() + 1 < mo || (today.getMonth() + 1 === mo && today.getDate() < d)) ? 1 : 0);
}

export interface Counts { total: number; ongoing: number; resolved: number; escalated: number; closed: number }

/** Ongoing = still open (not sent, waiting, escalated). Escalated is also counted inside ongoing. */
export function countCases(cases: Pick<TrackedCase, 'state'>[]): Counts {
  const n = (...st: CaseState[]) => cases.filter((c) => st.includes(c.state)).length;
  return { total: cases.length, ongoing: n('new', 'waiting', 'escalated'), resolved: n('resolved'), escalated: n('escalated'), closed: n('closed') };
}

export function isOngoing(state: CaseState): boolean { return state === 'new' || state === 'waiting' || state === 'escalated'; }
export function isResolved(state: CaseState): boolean { return state === 'resolved' || state === 'closed'; }
