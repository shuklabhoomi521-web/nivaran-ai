import { firstName, greetingFor, niceNow } from '../src/greeting';
import { ageOn, countCases, dobToInput, isOngoing, isResolved, parseDob } from '../src/profileUtil';

test('greeting follows the hour', () => {
  expect(greetingFor(new Date(2026, 11, 5, 4, 59))).toBe('night');
  expect(greetingFor(new Date(2026, 11, 5, 5, 0))).toBe('morning');
  expect(greetingFor(new Date(2026, 11, 5, 12, 0))).toBe('afternoon');
  expect(greetingFor(new Date(2026, 11, 5, 17, 0))).toBe('evening');
  expect(greetingFor(new Date(2026, 11, 5, 22, 0))).toBe('night');
});
test('nice date and time', () => {
  expect(niceNow(new Date(2026, 11, 5, 19, 5))).toBe('Saturday, 5 December 2026 · 7:05 pm');
  expect(niceNow(new Date(2026, 11, 5, 0, 7))).toBe('Saturday, 5 December 2026 · 12:07 am');
});
test('first name', () => { expect(firstName('  Asha  Rao ')).toBe('Asha'); expect(firstName(null)).toBe(''); });
test('date of birth parsing', () => {
  expect(parseDob('15/06/2000')).toBe('2000-06-15');
  expect(parseDob('5-6-2000')).toBe('2000-06-05');
  expect(parseDob('31/02/2000')).toBeNull();
  expect(parseDob('2000-06-15')).toBeNull();
  expect(parseDob('')).toBeNull();
  expect(dobToInput('2000-06-15')).toBe('15/06/2000');
});
test('age', () => {
  expect(ageOn('2008-12-05', new Date(2026, 11, 5))).toBe(18);
  expect(ageOn('2008-12-06', new Date(2026, 11, 5))).toBe(17);
});
test('status counts', () => {
  const cs = (['new', 'waiting', 'escalated', 'resolved', 'resolved', 'closed'] as const).map((state) => ({ state }));
  expect(countCases(cs)).toEqual({ total: 6, ongoing: 3, resolved: 2, escalated: 1, closed: 1 });
  expect(isOngoing('waiting')).toBe(true); expect(isResolved('closed')).toBe(true); expect(isResolved('new')).toBe(false);
});

import { followUpText } from '../src/format';
const act = (rung: string, due_on: string, days_overdue: number) => ({ action: { rung, due_on, days_overdue } as never, reminders: [] });
test('follow-up wording', () => {
  expect(followUpText(act('grievance_officer', '2026-12-12', 0), 'waiting')).toBe('Next follow-up on 12 Dec 2026: Grievance officer');
  expect(followUpText(act('follow_up', '2026-12-08', 2), 'waiting')).toBe('Follow-up overdue since 8 Dec 2026: Follow-up');
  expect(followUpText(act('first_contact', '2026-12-05', 0), 'new')).toContain('approval');
  expect(followUpText(null, 'waiting')).toBe('No follow-up planned');
  expect(followUpText(null, 'resolved')).toBe('Solved');
});

import { followUpLine } from '../src/format';
import { translate, type Key } from '../src/i18n';
test('follow-up line is translated and filled in', () => {
  const t = (l: 'en' | 'hi' | 'ta') => (k: Key) => translate(l, k);
  expect(followUpLine(t('en'), act('grievance_officer', '2026-12-12', 0), 'waiting')).toBe('Next follow-up on 12 Dec 2026: Grievance officer');
  expect(followUpLine(t('hi'), act('follow_up', '2026-12-08', 2), 'waiting')).toBe('8 Dec 2026 से फ़ॉलो-अप बाकी: फ़ॉलो-अप');
  expect(followUpLine(t('ta'), null, 'resolved')).toBe('தீர்ந்தது');
  expect(followUpLine(t('hi'), act('first_contact', '2026-12-05', 0), 'new')).not.toContain('{');
});
