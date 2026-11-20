import { BlurView } from 'expo-blur';
import { GlassView, isLiquidGlassAvailable } from 'expo-glass-effect';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useState } from 'react';
import { AccessibilityInfo, Platform, StyleProp, StyleSheet, View, ViewStyle } from 'react-native';
import { SurfaceKind, surfaceKind } from './surface';

let nativeGlass = false;
try { nativeGlass = Platform.OS === 'ios' && isLiquidGlassAvailable(); } catch { nativeGlass = false; }

export function useReduceTransparency(): boolean {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    let live = true;
    AccessibilityInfo.isReduceTransparencyEnabled?.().then((v) => { if (live) setReduce(!!v); }).catch(() => undefined);
    const sub = AccessibilityInfo.addEventListener?.('reduceTransparencyChanged', (v: boolean) => setReduce(!!v));
    return () => { live = false; sub?.remove?.(); };
  }, []);
  return reduce;
}

export function useSurfaceKind(): SurfaceKind {
  const reduceTransparency = useReduceTransparency();
  return surfaceKind({ os: Platform.OS, nativeGlass, reduceTransparency });
}

const EDGE = 'rgba(255,255,255,0.75)';

/** A pane of liquid glass. `tint` colours it (for a primary button); `children` sit on top. */
export function GlassSurface({ children, style, tint, radius = 18 }: { children?: React.ReactNode; style?: StyleProp<ViewStyle>; tint?: string; radius?: number }) {
  const kind = useSurfaceKind();
  const shape: ViewStyle = { borderRadius: radius, overflow: 'hidden' };
  if (kind === 'native') {
    return <GlassView glassEffectStyle="regular" tintColor={tint} style={[shape, style]}>{children}</GlassView>;
  }
  if (kind === 'blur') {
    return (
      <BlurView intensity={45} tint="light" style={[shape, styles.edge, tint ? { backgroundColor: tint } : styles.milk, style]}>{children}</BlurView>
    );
  }
  if (kind === 'web') {
    const web = { backdropFilter: 'blur(22px) saturate(170%)', WebkitBackdropFilter: 'blur(22px) saturate(170%)', boxShadow: '0 8px 30px rgba(40,50,120,0.14), inset 0 1px 0 rgba(255,255,255,0.8)' };
    return <View style={[shape, styles.edge, tint ? { backgroundColor: tint } : styles.milk, web as unknown as ViewStyle, style]}>{children}</View>;
  }
  return <View style={[shape, styles.solid, tint ? { backgroundColor: tint } : null, style]}>{children}</View>;   // reduce transparency: opaque and high contrast
}

/** The colourful backdrop that makes the glass visible. Opaque soft colour when transparency is reduced. */
export function GlassBackground({ children }: { children: React.ReactNode }) {
  const kind = useSurfaceKind();
  if (kind === 'solid') return <View style={[StyleSheet.absoluteFill, { backgroundColor: '#f1f3f6', flex: 1 }]}>{children}</View>;
  return (
    <View style={{ flex: 1, overflow: 'hidden' }}>
      <LinearGradient colors={['#cfe0ff', '#e6d8ff', '#ffe0ec']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={StyleSheet.absoluteFill} />
      <View pointerEvents="none" style={[styles.blob, { top: -70, right: -60, backgroundColor: 'rgba(99,179,255,0.55)' }]} />
      <View pointerEvents="none" style={[styles.blob, { top: 320, left: -110, backgroundColor: 'rgba(190,140,255,0.45)' }]} />
      <View pointerEvents="none" style={[styles.blob, { bottom: -90, right: -40, backgroundColor: 'rgba(255,150,190,0.5)' }]} />
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  edge: { borderWidth: 1, borderColor: EDGE },
  milk: { backgroundColor: 'rgba(255,255,255,0.42)' },
  solid: { backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#c9ced6' },
  blob: { position: 'absolute', width: 260, height: 260, borderRadius: 130 },
});
