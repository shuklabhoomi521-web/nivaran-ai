export type SurfaceKind = 'native' | 'blur' | 'web' | 'solid';

/** Which kind of glass to draw. Pure so it can be tested.
 *  - native: Apple's real liquid glass (iOS 26 or newer)
 *  - blur:   a frosted blur on other phones
 *  - web:    CSS backdrop blur in a browser
 *  - solid:  an opaque card, used when the person turned on "Reduce Transparency" (accessibility) */
export function surfaceKind(opts: { os: string; nativeGlass: boolean; reduceTransparency: boolean }): SurfaceKind {
  if (opts.reduceTransparency) return 'solid';
  if (opts.os === 'web') return 'web';
  if (opts.os === 'ios' && opts.nativeGlass) return 'native';
  return 'blur';
}
