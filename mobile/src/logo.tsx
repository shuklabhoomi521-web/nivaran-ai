import React from 'react';
import { Text, View } from 'react-native';
import Svg, { Circle, Defs, LinearGradient, Path, Rect, Stop } from 'react-native-svg';
import { c, font } from './theme';

/** The Nivaran mark: ONE unbroken ribbon that draws the letter N. It starts as a small knot (the tangled problem),
 *  rises as the left stem, glides down the diagonal and climbs the right stem to a settled warm dot (the remedy).
 *  "Nivaran" means remedy or relief. Deep navy tile, pale steel-blue ribbon, warm brown dot. */
export function LogoMark({ size = 56 }: { size?: number }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 100 100" accessibilityLabel="Nivaran logo">
      <Defs>
        <LinearGradient id="ribbon" x1="0" y1="1" x2="1" y2="0">
          <Stop offset="0" stopColor="#E9C9B0" />
          <Stop offset="0.45" stopColor="#B9CCE4" />
          <Stop offset="1" stopColor="#FFFFFF" />
        </LinearGradient>
      </Defs>
      <Rect x={2.5} y={2.5} width={95} height={95} rx={22} fill="#1B3354" stroke="#3F5A82" strokeWidth={2} />
      <Path d="M36 84 C 8 90 6 52 28 58 C 46 63 38 90 26 70 C 23 62 29 56 29 42 L 29 27 C 47 44 56 61 71 76 L 71 33"
        stroke="url(#ribbon)" strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <Circle cx={71} cy={22} r={7} fill="#C9A27A" />
    </Svg>
  );
}

export function Logo({ size = 56, word = true, caption }: { size?: number; word?: boolean; caption?: string }) {
  return (
    <View style={{ alignItems: 'center', gap: 8 }}>
      <LogoMark size={size} />
      {word ? <Text style={{ fontFamily: font, fontSize: Math.max(13, size * 0.24), fontWeight: '700', letterSpacing: 3, color: c.ink }}>NIVARAN</Text> : null}
      {caption ? <Text style={{ fontFamily: font, fontSize: 13, color: c.soft }}>{caption}</Text> : null}
    </View>
  );
}
