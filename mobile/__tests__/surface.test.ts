import { surfaceKind } from '../src/surface';

describe('which glass to draw', () => {
  it('uses real liquid glass only on iOS 26 or newer', () => {
    expect(surfaceKind({ os: 'ios', nativeGlass: true, reduceTransparency: false })).toBe('native');
    expect(surfaceKind({ os: 'ios', nativeGlass: false, reduceTransparency: false })).toBe('blur');
  });
  it('uses a frosted blur on Android and a CSS blur in a browser', () => {
    expect(surfaceKind({ os: 'android', nativeGlass: false, reduceTransparency: false })).toBe('blur');
    expect(surfaceKind({ os: 'web', nativeGlass: false, reduceTransparency: false })).toBe('web');
  });
  it('always goes opaque when the person asked to reduce transparency', () => {
    for (const os of ['ios', 'android', 'web']) {
      expect(surfaceKind({ os, nativeGlass: true, reduceTransparency: true })).toBe('solid');
    }
  });
});
