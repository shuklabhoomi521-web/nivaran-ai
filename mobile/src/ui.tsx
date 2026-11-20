import React from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { GlassSurface, useSurfaceKind } from './glass';
import { c, s } from './theme';

export function Button({ label, onPress, kind = 'primary', disabled, busy }: { label: string; onPress: () => void; kind?: 'primary' | 'ghost'; disabled?: boolean; busy?: boolean }) {
  const off = disabled || busy;
  const solid = useSurfaceKind() === 'solid';
  const primary = kind === 'primary';
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={label} accessibilityState={{ disabled: !!off, busy: !!busy }} disabled={off} onPress={onPress}
      style={({ pressed }) => [off && s.btnOff, pressed && { opacity: 0.8, transform: [{ scale: 0.99 }] }]}>
      <GlassSurface radius={14} tint={primary ? (solid ? c.brand : 'rgba(29,78,216,0.88)') : undefined} style={s.btnInner}>
        {busy ? <ActivityIndicator color={primary ? '#fff' : c.ink} /> : <Text style={primary ? s.btnText : s.btnGhostText}>{label}</Text>}
      </GlassSurface>
    </Pressable>
  );
}

export function Chip({ text, color }: { text: string; color: string }) {
  return (
    <View style={{ alignSelf: 'flex-start' }}>
      <GlassSurface radius={999} style={[s.chip, { borderColor: color }]}>
        <Text style={[s.chipText, { color }]}>{text}</Text>
      </GlassSurface>
    </View>
  );
}

export function Card({ title, children }: { title?: string; children: React.ReactNode }) {
  return (
    <GlassSurface style={s.card}>
      {title ? <Text style={s.h2}>{title}</Text> : null}
      {children}
    </GlassSurface>
  );
}

export function ErrorText({ message }: { message: string | null }) {
  return message ? (
    <GlassSurface radius={12} tint="rgba(255,235,235,0.7)" style={{ padding: 10 }}>
      <Text style={s.err} accessibilityLiveRegion="polite">{message}</Text>
    </GlassSurface>
  ) : null;
}
