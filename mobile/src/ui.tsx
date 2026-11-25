import React from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { GlassSurface } from './glass';
import { c, s } from './theme';

export function Button({ label, onPress, kind = 'primary', disabled, busy }: { label: string; onPress: () => void; kind?: 'primary' | 'ghost'; disabled?: boolean; busy?: boolean }) {
  const off = disabled || busy;
  const primary = kind === 'primary';
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={label} accessibilityState={{ disabled: !!off, busy: !!busy }} disabled={off} onPress={onPress}
      style={({ pressed }) => [off && s.btnOff, pressed && { opacity: 0.85 }]}>
      <GlassSurface radius={8} tint={primary ? c.navy : undefined} style={s.btnInner}>
        {busy ? <ActivityIndicator color={primary ? '#fff' : c.navy} /> : <Text style={primary ? s.btnText : s.btnGhostText}>{label}</Text>}
      </GlassSurface>
    </Pressable>
  );
}

/** A small status badge: tinted background, thin border, coloured text. */
export function Chip({ text, color }: { text: string; color: string }) {
  return (
    <View style={{ alignSelf: 'flex-start', borderRadius: 6, borderWidth: 1, borderColor: color, backgroundColor: color + '14', paddingHorizontal: 9, paddingVertical: 3 }}>
      <Text style={[s.chipText, { color }]}>{text}</Text>
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
    <View style={{ borderRadius: 8, borderWidth: 1, borderColor: '#E4C3CD', backgroundColor: '#FBF2F5', padding: 10 }}>
      <Text style={s.err} accessibilityLiveRegion="polite">{message}</Text>
    </View>
  ) : null;
}
