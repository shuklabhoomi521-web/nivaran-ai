/** Pure sizing rules so the same app fits a phone, a tablet and a laptop window (Mac or Windows browser). */
export type LayoutKind = 'phone' | 'tablet' | 'desktop';

export function layoutFor(width: number): { kind: LayoutKind; maxWidth: number | null; gutter: number } {
  if (width >= 1024) return { kind: 'desktop', maxWidth: 820, gutter: 24 };
  if (width >= 700) return { kind: 'tablet', maxWidth: 680, gutter: 16 };
  return { kind: 'phone', maxWidth: null, gutter: 0 };
}
