import { planReminders, reminderId } from '../src/reminderPlan';
import type { NextResponse } from '../src/types';

const next = (statuses: Array<'done' | 'due' | 'upcoming' | 'closed'>): Pick<NextResponse, 'reminders'> => ({
  reminders: (['first_contact', 'follow_up', 'grievance_officer', 'appellate', 'regulator'] as const).map((rung, i) => ({
    rung, due_on: ['2026-12-05', '2026-12-08', '2026-12-12', '2026-12-20', '2026-12-20'][i], status: statuses[i],
  })),
});
const NOW = new Date(2026, 11, 6, 9, 0, 0);          // 6 Dec 2026, 09:00 local

describe('reminder planning', () => {
  it('schedules only steps that are still ahead, at 10:00 local time', () => {
    const plan = planReminders({ id: 'c1', state: 'waiting' }, next(['done', 'upcoming', 'upcoming', 'upcoming', 'upcoming']), NOW);
    expect(plan.map((p) => p.id)).toEqual(['c1:follow_up', 'c1:grievance_officer', 'c1:appellate', 'c1:regulator']);
    expect(plan[0].at.getFullYear()).toBe(2026);
    expect(plan[0].at.getMonth()).toBe(11);
    expect(plan[0].at.getDate()).toBe(8);
    expect(plan[0].at.getHours()).toBe(10);
  });
  it('skips done and due steps and dates already in the past', () => {
    const plan = planReminders({ id: 'c1', state: 'waiting' }, next(['done', 'due', 'upcoming', 'upcoming', 'upcoming']), new Date(2026, 11, 12, 11, 0, 0));
    expect(plan.map((p) => p.id)).toEqual(['c1:appellate', 'c1:regulator']);
  });
  it('plans nothing for a solved or closed case', () => {
    expect(planReminders({ id: 'c1', state: 'resolved' }, next(['upcoming', 'upcoming', 'upcoming', 'upcoming', 'upcoming']), NOW)).toEqual([]);
    expect(planReminders({ id: 'c1', state: 'closed' }, next(['upcoming', 'upcoming', 'upcoming', 'upcoming', 'upcoming']), NOW)).toEqual([]);
  });
  it('keeps the text generic: no company, no facts on a lock screen', () => {
    const [p] = planReminders({ id: 'c1', state: 'new' }, next(['upcoming', 'upcoming', 'upcoming', 'upcoming', 'upcoming']), new Date(2026, 11, 1));
    expect(p.title).toBe('Nivaran');
    expect(p.body).toBe('A step is due on one of your cases: first message.');
    expect(reminderId('c1', 'follow_up')).toBe('c1:follow_up');
  });
});
