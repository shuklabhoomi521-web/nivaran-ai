import type { Action, CaseState, Reminder, Rung } from './types';

export const RUNG_LABEL: Record<Rung, string> = {
  first_contact: 'First message',
  follow_up: 'Follow-up',
  grievance_officer: 'Grievance officer',
  appellate: 'Appellate authority',
  regulator: "Regulator's portal",
};

export const STATE_LABEL: Record<CaseState, string> = {
  new: 'Not sent yet',
  waiting: 'Waiting for a reply',
  escalated: 'Escalated',
  resolved: 'Solved',
  closed: 'Closed',
};

export const STATE_COLOR: Record<CaseState, string> = {
  new: '#5b6470', waiting: '#b26a00', escalated: '#b3261e', resolved: '#1b7f3b', closed: '#5b6470',
};

export const GOAL_LABEL: Record<string, string> = {
  refund: 'a refund', repair: 'a repair', replace: 'a replacement', cancel: 'cancellation', info: 'information', other: 'a resolution',
};

export function categoryLabel(c: string): string {
  return c.replace(/_/g, ' ').replace(/^./, (m) => m.toUpperCase());
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** "2026-12-05" -> "5 Dec 2026" (no time zones involved). */
export function prettyDate(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return iso;
  return `${Number(m[3])} ${MONTHS[Number(m[2]) - 1]} ${m[1]}`;
}

export function reminderLabel(r: Reminder): string {
  const when = prettyDate(r.due_on);
  if (r.status === 'done') return `${RUNG_LABEL[r.rung]}: done`;
  if (r.status === 'closed') return `${RUNG_LABEL[r.rung]}: not needed`;
  if (r.status === 'due') return `${RUNG_LABEL[r.rung]}: due since ${when}`;
  return `${RUNG_LABEL[r.rung]}: on ${when}`;
}

export function actionHeadline(a: Action): string {
  const base = RUNG_LABEL[a.rung];
  if (a.days_overdue > 0) return `${base} (${a.days_overdue} day${a.days_overdue === 1 ? '' : 's'} late)`;
  return base;
}

/** One safe line for a list: never shows the facts, only company and state. */
export function caseTitle(company: string, state: CaseState): string {
  return `${company} · ${STATE_LABEL[state]}`;
}

export function todayIso(d: Date = new Date()): string {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

/** "2026-12-05" + 2 days -> "2026-12-07" (calendar days, no time zones). */
export function addDays(iso: string, days: number): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return iso;
  const d = new Date(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3]) + days));
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())}`;
}
