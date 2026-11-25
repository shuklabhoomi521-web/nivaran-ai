import React, { useEffect, useState } from 'react';
import { AccessibilityInfo, StyleProp, StyleSheet, View, ViewStyle } from 'react-native';
import { c, s } from './theme';
import { SurfaceKind } from './surface';

/** Kept for compatibility with the older screens. The look is now flat and professional: solid white panels with a fine border.
 *  (The earlier glass and blur effects were removed on purpose.) */
export function useReduceTransparency(): boolean {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    let live = true;
    AccessibilityInfo.isReduceTransparencyEnabled?.().then((v) => { if (live) setReduce(!!v); }).catch(() => undefined);
    return () => { live = false; };
  }, []);
  return reduce;
}

export function useSurfaceKind(): SurfaceKind { return 'solid'; }

/** A panel. `tint` is a solid fill colour (used by the primary button); `radius` is capped so nothing looks bubbly. */
export function GlassSurface({ children, style, tint, radius = 10 }: { children?: React.ReactNode; style?: StyleProp<ViewStyle>; tint?: string; radius?: number }) {
  const r = radius >= 100 ? 6 : Math.min(radius, 10);
  const fill: ViewStyle = tint ? { backgroundColor: tint, borderColor: tint } : { backgroundColor: c.card, borderColor: c.line };
  return <View style={[{ borderRadius: r, borderWidth: 1, overflow: 'hidden' }, fill, tint ? null : (s.shadow as ViewStyle), style]}>{children}</View>;
}

/** Plain, calm page background. */
export function GlassBackground({ children }: { children: React.ReactNode }) {
  return <View style={[{ flex: 1, backgroundColor: c.bg }, StyleSheet.absoluteFill]}>{children}</View>;
}
