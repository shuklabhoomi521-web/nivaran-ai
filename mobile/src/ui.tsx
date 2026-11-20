import React from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { c, s } from './theme';

export function Button({ label, onPress, kind = 'primary', disabled, busy }: { label: string; onPress: () => void; kind?: 'primary' | 'ghost'; disabled?: boolean; busy?: boolean }) {
  const off = disabled || busy;
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={label} disabled={off} onPress={onPress} style={[kind === 'primary' ? s.btn : s.btnGhost, off && s.btnOff]}>
      {busy ? <ActivityIndicator color={kind === 'primary' ? '#fff' : c.ink} /> : <Text style={kind === 'primary' ? s.btnText : s.btnGhostText}>{label}</Text>}
    </Pressable>
  );
}

export function Chip({ text, color }: { text: string; color: string }) {
  return (
    <View style={[s.chip, { borderColor: color }]}>
      <Text style={[s.chipText, { color }]}>{text}</Text>
    </View>
  );
}

export function Card({ title, children }: { title?: string; children: React.ReactNode }) {
  return (
    <View style={s.card}>
      {title ? <Text style={s.h2}>{title}</Text> : null}
      {children}
    </View>
  );
}

export function ErrorText({ message }: { message: string | null }) {
  return message ? <Text style={s.err} accessibilityLiveRegion="polite">{message}</Text> : null;
}
