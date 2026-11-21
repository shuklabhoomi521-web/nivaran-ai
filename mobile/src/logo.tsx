import React from 'react';
import { Text, View } from 'react-native';
import Svg, { Circle, Defs, LinearGradient, Path, Rect, Stop } from 'react-native-svg';
import { c } from './theme';

/** The Nivaran mark: ONE unbroken ribbon that draws the letter N.
 *  It starts as a small knot (the tangled problem), rises as the left stem, glides down the diagonal without a single corner,
 *  and climbs the right stem to a settled brown dot (the remedy). "Nivaran" means remedy or relief.
 *  Colours: pastel pink flowing into pastel blue, with a brown dot, on a soft grey-blue tile. */
export function LogoMark({ size = 56 }: { size?: number }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 100 100" accessibilityLabel="Nivaran logo">
      <Defs>
        <LinearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
          <Stop offset="0" stopColor="#E9EEF7" />
          <Stop offset="1" stopColor="#F4E6EC" />
        </LinearGradient>
        <LinearGradient id="ribbon" x1="0" y1="1" x2="1" y2="0">
          <Stop offset="0" stopColor="#E08FAE" />
          <Stop offset="0.5" stopColor="#B7A3D4" />
          <Stop offset="1" stopColor="#6F9BD3" />
        </LinearGradient>
      </Defs>
      <Rect x={2} y={2} width={96} height={96} rx={26} fill="url(#tile)" stroke="#FFFFFF" strokeWidth={2} />
      <Path d="M36 84 C 8 90 6 52 28 58 C 46 63 38 90 26 70 C 23 62 29 56 29 42 L 29 27 C 47 44 56 61 71 76 L 71 33"
        stroke="url(#ribbon)" strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <Circle cx={71} cy={22} r={7} fill="#A67C5B" />
    </Svg>
  );
}

export function Logo({ size = 56, word = true, caption }: { size?: number; word?: boolean; caption?: string }) {
  return (
    <View style={{ alignItems: 'center', gap: 8 }}>
      <LogoMark size={size} />
      {word ? <Text style={{ fontSize: size * 0.3, fontWeight: '700', letterSpacing: 3, color: c.ink }}>NIVARAN</Text> : null}
      {caption ? <Text style={{ fontSize: 14, color: c.soft }}>{caption}</Text> : null}
    </View>
  );
}
