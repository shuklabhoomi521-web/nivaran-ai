import React, { useState } from 'react';
import { Pressable, Text, View, useWindowDimensions } from 'react-native';
import { useT, type Key } from './i18n';
import { layoutFor } from './layout';
import { LogoMark } from './logo';
import { c, font } from './theme';

export type Tab = 'home' | 'chat' | 'callhome' | 'complaints' | 'profile';
const ITEMS: { tab: Tab; label: Key; hint: Key }[] = [
  { tab: 'home', label: 'nav.home', hint: 'nav.home.hint' },
  { tab: 'chat', label: 'nav.chat', hint: 'nav.chat.hint' },
  { tab: 'callhome', label: 'nav.call', hint: 'nav.call.hint' },
  { tab: 'complaints', label: 'nav.complaints', hint: 'nav.complaints.hint' },
  { tab: 'profile', label: 'nav.profile', hint: 'nav.profile.hint' },
];

function Menu({ current, onGo }: { current: Tab | null; onGo: (t: Tab) => void }) {
  const t = useT();
  return (
    <View style={{ gap: 2 }}>
      {ITEMS.map((i) => {
        const on = current === i.tab;
        return (
          <Pressable key={i.tab} accessibilityRole="button" accessibilityState={{ selected: on }} accessibilityLabel={t(i.label)} onPress={() => onGo(i.tab)}
            style={{ paddingVertical: 10, paddingHorizontal: 14, borderRadius: 8, borderLeftWidth: 3, borderLeftColor: on ? '#C9A27A' : 'transparent', backgroundColor: on ? 'rgba(255,255,255,0.10)' : 'transparent' }}>
            <Text style={{ fontFamily: font, fontSize: 14.5, fontWeight: on ? '600' : '500', color: on ? '#FFFFFF' : '#C9D3E3' }}>{t(i.label)}</Text>
            <Text style={{ fontFamily: font, fontSize: 12, color: '#8D9BB3', marginTop: 1 }}>{t(i.hint)}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

function Brand({ dark = true }: { dark?: boolean }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
      <LogoMark size={36} />
      <View>
        <Text style={{ fontFamily: font, fontSize: 15, fontWeight: '700', letterSpacing: 2.5, color: dark ? '#FFFFFF' : c.ink }}>NIVARAN</Text>
        <Text style={{ fontFamily: font, fontSize: 11, color: dark ? '#8D9BB3' : c.soft, marginTop: 1 }}>Customer care, resolved</Text>
      </View>
    </View>
  );
}

/** Laptop: a permanent dark side bar. Phone and tablet: a clean top bar with a menu button that opens the same side bar. */
export function AppFrame({ current, onGo, children }: { current: Tab | null; onGo: (t: Tab) => void; children: React.ReactNode }) {
  const { width } = useWindowDimensions();
  const t = useT();
  const [open, setOpen] = useState(false);
  const wide = layoutFor(width).kind === 'desktop';
  const go = (tab: Tab) => { setOpen(false); onGo(tab); };
  const rail = <View style={{ width: 268, backgroundColor: c.navy, paddingVertical: 22, paddingHorizontal: 14, gap: 26 }}><View style={{ paddingHorizontal: 6 }}><Brand /></View><Menu current={current} onGo={go} /></View>;
  if (wide) {
    return (
      <View style={{ flex: 1, flexDirection: 'row' }}>
        {rail}
        <View style={{ flex: 1, alignItems: 'center' }}><View style={{ flex: 1, width: '100%', maxWidth: 900, paddingTop: 8 }}>{children}</View></View>
      </View>
    );
  }
  return (
    <View style={{ flex: 1 }}>
      <View style={{ height: 58, backgroundColor: c.navy, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16 }}>
        <Brand />
        <Pressable accessibilityRole="button" accessibilityLabel="Open the menu" onPress={() => setOpen(true)} style={{ paddingVertical: 8, paddingHorizontal: 12, borderRadius: 8, borderWidth: 1, borderColor: 'rgba(255,255,255,0.35)' }}>
          <Text style={{ fontFamily: font, fontSize: 14, fontWeight: '600', color: '#fff' }}>{t('nav.menu')}</Text>
        </Pressable>
      </View>
      <View style={{ flex: 1, maxWidth: layoutFor(width).maxWidth ?? undefined, width: '100%', alignSelf: 'center' }}>{children}</View>
      {open ? (
        <View style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, zIndex: 10, flexDirection: 'row' }}>
          <View style={{ width: 290, backgroundColor: c.navy, paddingTop: 22, paddingHorizontal: 14, gap: 26 }}><View style={{ paddingHorizontal: 6 }}><Brand /></View><Menu current={current} onGo={go} /></View>
          <Pressable accessibilityRole="button" accessibilityLabel="Close the menu" onPress={() => setOpen(false)} style={{ flex: 1, backgroundColor: 'rgba(14,27,48,0.45)' }} />
        </View>
      ) : null}
    </View>
  );
}
