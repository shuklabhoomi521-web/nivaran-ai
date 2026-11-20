import { RUNG_LABEL } from './format';
import type { NextResponse, Rung, TrackedCase } from './types';

export interface PlannedReminder { id: string; title: string; body: string; at: Date }

/** Reminders to schedule for one case: one per step that is not done yet and whose date is still ahead (10:00 local time that day).
 *  The text is deliberately generic so nothing private shows on a lock screen: no company, no facts. */
export function planReminders(tc: Pick<TrackedCase, 'id' | 'state'>, next: Pick<NextResponse, 'reminders'>, now: Date): PlannedReminder[] {
  if (tc.state === 'resolved' || tc.state === 'closed') return [];
  const out: PlannedReminder[] = [];
  for (const r of next.reminders) {
    if (r.status !== 'upcoming') continue;
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(r.due_on);
    if (!m) continue;
    const at = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]), 10, 0, 0);
    if (at.getTime() <= now.getTime()) continue;
    out.push({ id: reminderId(tc.id, r.rung), title: 'Nivaran', body: `A step is due on one of your cases: ${RUNG_LABEL[r.rung as Rung].toLowerCase()}.`, at });
  }
  return out;
}

export function reminderId(caseId: string, rung: string): string {
  return `${caseId}:${rung}`;
}

export const ALL_RUNGS: Rung[] = ['first_contact', 'follow_up', 'grievance_officer', 'appellate', 'regulator'];
