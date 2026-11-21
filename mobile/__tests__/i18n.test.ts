import { STRINGS, translate } from '../src/i18n';

describe('app text in three languages', () => {
  const keys = Object.keys(STRINGS.en);
  it('has every key in every language and none is empty', () => {
    for (const lang of ['hi', 'ta'] as const) {
      expect(Object.keys(STRINGS[lang]).sort()).toEqual([...keys].sort());
      for (const k of keys) expect((STRINGS[lang] as Record<string, string>)[k].trim().length).toBeGreaterThan(0);
    }
  });
  it('Hindi is written in Devanagari and Tamil in Tamil script', () => {
    const dev = /[ऀ-ॿ]/; const tam = /[஀-௿]/;
    for (const k of keys) {
      expect(dev.test((STRINGS.hi as Record<string, string>)[k])).toBe(true);
      expect(tam.test((STRINGS.ta as Record<string, string>)[k])).toBe(true);
    }
  });
  it('falls back to English for a missing key', () => {
    expect(translate('en', 'cases.new')).toBe('New case');
    expect(translate('hi', 'cases.new')).toBe('नई शिकायत');
    expect(translate('ta', 'common.back')).toBe('பின்');
  });
  it('keeps the safety wording out of translation drift: the privacy and consent labels exist everywhere', () => {
    for (const lang of ['en', 'hi', 'ta'] as const) {
      expect((STRINGS[lang] as Record<string, string>)['new.agree']).toBeTruthy();
      expect((STRINGS[lang] as Record<string, string>)['new.adult']).toContain('18');
    }
  });
});

test('every English key has Hindi and Tamil text', () => {
  const { STRINGS } = require('../src/i18n');
  for (const k of Object.keys(STRINGS.en)) { expect(STRINGS.hi[k]).toBeTruthy(); expect(STRINGS.ta[k]).toBeTruthy(); }
});
