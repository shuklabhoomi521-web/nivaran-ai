import { CALL_LANGUAGES, actionHeadline, addDays, nextSince, caseTitle, categoryLabel, prettyDate, reminderLabel, todayIso } from '../src/format';
import type { Action, Reminder } from '../src/types';

const action = (over: Partial<Action>): Action => ({
  rung: 'follow_up', due_on: '2026-12-08', days_overdue: 0, channel: 'email', target_label: 'x', target_value: null,
  source_url: null, source_quote: null, reason: '', fell_back_from: null, note: null, ...over,
});

describe('format helpers', () => {
  it('formats dates without time zone surprises', () => {
    expect(prettyDate('2026-12-05')).toBe('5 Dec 2026');
    expect(prettyDate('2027-01-31')).toBe('31 Jan 2027');
    expect(prettyDate('not a date')).toBe('not a date');
  });
  it('labels the ladder in plain words', () => {
    const r = (status: Reminder['status']): Reminder => ({ rung: 'grievance_officer', due_on: '2026-12-12', status });
    expect(reminderLabel(r('upcoming'))).toBe('Grievance officer: on 12 Dec 2026');
    expect(reminderLabel(r('due'))).toBe('Grievance officer: due since 12 Dec 2026');
    expect(reminderLabel(r('done'))).toBe('Grievance officer: done');
    expect(reminderLabel(r('closed'))).toBe('Grievance officer: not needed');
  });
  it('says how late a step is', () => {
    expect(actionHeadline(action({ days_overdue: 0 }))).toBe('Follow-up');
    expect(actionHeadline(action({ days_overdue: 1 }))).toBe('Follow-up (1 day late)');
    expect(actionHeadline(action({ days_overdue: 4 }))).toBe('Follow-up (4 days late)');
  });
  it('list titles show only company and state, never the facts', () => {
    expect(caseTitle('Swiggy', 'waiting')).toBe('Swiggy · Waiting for a reply');
  });
  it('adds days across month and year ends', () => {
    expect(addDays('2026-12-30', 2)).toBe('2027-01-01');
    expect(addDays('2026-02-27', 2)).toBe('2026-03-01');
  });
  it('category and today helpers', () => {
    expect(categoryLabel('food_delivery')).toBe('Food delivery');
    expect(todayIso(new Date(2026, 11, 5))).toBe('2026-12-05');
  });
});

describe('call helpers', () => {
  it('moves the transcript cursor forward only', () => {
    expect(nextSince([], 3)).toBe(3);
    expect(nextSince([{ n: 4 }, { n: 6 }, { n: 5 }], 3)).toBe(6);
    expect(nextSince([{ n: 1 }], 3)).toBe(3);
  });
  it('offers the four call languages the backend accepts', () => {
    expect(CALL_LANGUAGES.map((l) => l.code)).toEqual(['en-IN', 'hi-IN', 'ta-IN', 'hinglish']);
  });
});
