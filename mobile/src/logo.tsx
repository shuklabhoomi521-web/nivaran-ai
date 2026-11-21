import React from 'react';
import { Text, View } from 'react-native';
import Svg, { Circle, Defs, LinearGradient, Path, Stop } from 'react-native-svg';
import { c } from './theme';

/** The Nivaran mark: a tangled loop (the problem) that relaxes into one calm line (the remedy), ending in a settled dot.
 *  "Nivaran" means remedy or relief. Pastel pink to blue, with a brown dot. */
export function LogoMark({ size = 56 }: { size?: number }) {
  return (
    <Svg width={size} height={size * 0.62} viewBox="0 0 100 62" accessibilityLabel="Nivaran logo">
      <Defs>
        <LinearGradient id="nv" x1="0" y1="0" x2="1" y2="0">
          <Stop offset="0" stopColor="#E59AB5" />
          <Stop offset="0.55" stopColor="#B7A7D6" />
          <Stop offset="1" stopColor="#7FA3D6" />
        </LinearGradient>
      </Defs>
      <Path d="M6 38 C 4 8, 44 6, 38 32 C 33 54, 8 46, 22 28 C 32 16, 48 38, 62 31 L 88 31" stroke="url(#nv)" strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <Circle cx={92} cy={31} r={5.5} fill="#A67C5B" />
    </Svg>
  );
}

export function Logo({ size = 56, word = true, caption }: { size?: number; word?: boolean; caption?: string }) {
  return (
    <View style={{ alignItems: 'center', gap: 6 }}>
      <LogoMark size={size} />
      {word ? <Text style={{ fontSize: size * 0.42, fontWeight: '700', letterSpacing: 2, color: c.ink }}>NIVARAN</Text> : null}
      {caption ? <Text style={{ fontSize: 14, color: c.soft }}>{caption}</Text> : null}
    </View>
  );
}
