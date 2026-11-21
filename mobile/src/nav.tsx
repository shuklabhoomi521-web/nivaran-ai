import React, { useState } from 'react';
import { Pressable, Text, View, useWindowDimensions } from 'react-native';
import { GlassSurface } from './glass';
import { layoutFor } from './layout';
import { LogoMark } from './logo';
import { c } from './theme';

export type Tab = 'home' | 'chat' | 'callhome' | 'complaints' | 'profile';
const ITEMS: { tab: Tab; label: string; hint: string }[] = [
  { tab: 'home', label: 'Home', hint: 'Your dashboard' },
  { tab: 'chat', label: 'Tell our AI in chat', hint: 'Type or speak your problem' },
  { tab: 'callhome', label: 'Tell our AI on a call', hint: 'Talk to it by voice' },
  { tab: 'complaints', label: 'My complaints', hint: 'Ongoing and resolved' },
  { tab: 'profile', label: 'My profile', hint: 'Your details and numbers' },
];

function Menu({ current, onGo }: { current: Tab | null; onGo: (t: Tab) => void }) {
  return (
    <View style={{ gap: 6 }}>
      {ITEMS.map((i) => {
        const on = current === i.tab;
        return (
          <Pressable key={i.tab} accessibilityRole="button" accessibilityState={{ selected: on }} accessibilityLabel={i.label} onPress={() => onGo(i.tab)}
            style={{ paddingVertical: 10, paddingHorizontal: 12, borderRadius: 12, backgroundColor: on ? 'rgba(74,111,165,0.16)' : 'transparent' }}>
            <Text style={{ fontSize: 15, fontWeight: on ? '700' : '600', color: on ? c.brand : c.ink }}>{i.label}</Text>
            <Text style={{ fontSize: 12, color: c.soft }}>{i.hint}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

function Brand() {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 18 }}>
      <LogoMark size={46} />
      <Text style={{ fontSize: 17, fontWeight: '700', letterSpacing: 2, color: c.ink }}>NIVARAN</Text>
    </View>
  );
}

/** Laptop: a permanent side bar. Phone and tablet: a top bar with a menu button that opens the side bar. */
export function AppFrame({ current, onGo, children }: { current: Tab | null; onGo: (t: Tab) => void; children: React.ReactNode }) {
  const { width } = useWindowDimensions();
  const [open, setOpen] = useState(false);
  const wide = layoutFor(width).kind === 'desktop';
  const go = (t: Tab) => { setOpen(false); onGo(t); };
  if (wide) {
    return (
      <View style={{ flex: 1, flexDirection: 'row', padding: 16, gap: 16 }}>
        <GlassSurface style={{ width: 260, padding: 18 }}><Brand /><Menu current={current} onGo={go} /></GlassSurface>
        <View style={{ flex: 1, alignItems: 'center' }}><View style={{ flex: 1, width: '100%', maxWidth: 820 }}>{children}</View></View>
      </View>
    );
  }
  return (
    <View style={{ flex: 1 }}>
      <View style={{ position: 'absolute', top: 12, right: 14, zIndex: 5 }}>
        <Pressable accessibilityRole="button" accessibilityLabel="Open the menu" onPress={() => setOpen(true)}>
          <GlassSurface radius={14} style={{ paddingVertical: 8, paddingHorizontal: 14 }}><Text style={{ fontSize: 15, fontWeight: '700', color: c.ink }}>☰ Menu</Text></GlassSurface>
        </Pressable>
      </View>
      <View style={{ flex: 1, maxWidth: layoutFor(width).maxWidth ?? undefined, width: '100%', alignSelf: 'center' }}>{children}</View>
      {open ? (
        <View style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, zIndex: 10, flexDirection: 'row' }}>
          <GlassSurface radius={0} style={{ width: 290, padding: 18, paddingTop: 54 }}><Brand /><Menu current={current} onGo={go} /></GlassSurface>
          <Pressable accessibilityRole="button" accessibilityLabel="Close the menu" onPress={() => setOpen(false)} style={{ flex: 1, backgroundColor: 'rgba(43,45,51,0.28)' }} />
        </View>
      ) : null}
    </View>
  );
}
