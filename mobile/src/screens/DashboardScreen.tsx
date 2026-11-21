import React, { useCallback, useEffect, useState } from 'react';
import { RefreshControl, ScrollView, Text, View } from 'react-native';
import type { Api } from '../api';
import { ComplaintCard, useNexts } from '../cards';
import { greetingFor, niceNow } from '../greeting';
import { useT } from '../i18n';
import { Logo } from '../logo';
import { c, s } from '../theme';
import type { TrackedCase } from '../types';
import { Button, ErrorText } from '../ui';


export default function DashboardScreen({ api, name, onOpen, onChat, onCall, onAll }: { api: Api; name: string; onOpen: (id: string) => void; onChat: () => void; onCall: () => void; onAll: () => void }) {
  const t = useT();
  const [now, setNow] = useState(new Date());
  const [cases, setCases] = useState<TrackedCase[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  const load = useCallback(async () => {
    setBusy(true);
    try { setCases(await api.listCases()); setErr(null); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }, [api]);
  useEffect(() => { void load(); }, [load]);
  const recent = [...cases].sort((a, b) => (a.created_on < b.created_on ? 1 : -1)).slice(0, 5);
  const nexts = useNexts(api, recent);

  return (
    <View style={s.screen}>
      <ScrollView contentContainerStyle={s.body} refreshControl={<RefreshControl refreshing={busy} onRefresh={load} />}>
        <View style={{ gap: 4, paddingTop: 6, paddingRight: 90 }}>
          <Text style={{ fontSize: 28, fontWeight: '700', color: c.ink }}>{t(`greet.${greetingFor(now)}` as const)}{name ? `, ${name}` : ''}</Text>
          <Text style={s.soft}>{niceNow(now)}</Text>
        </View>
        <View style={s.row}>
          <View style={{ flex: 1 }}><Button label={t('nav.chat')} onPress={onChat} /></View>
          <View style={{ flex: 1 }}><Button label={t('nav.call')} kind="ghost" onPress={onCall} /></View>
        </View>
        <ErrorText message={err} />
        <Text style={[s.h2, { marginTop: 8 }]}>{t('home.recent')}</Text>
        {recent.length === 0 && !busy && !err ? <Text style={s.soft}>{t('home.none')}</Text> : null}
        {recent.map((item) => <ComplaintCard key={item.id} item={item} next={nexts[item.id]} onOpen={() => onOpen(item.id)} />)}
        {cases.length > 5 ? <Button label="See all my complaints" kind="ghost" onPress={onAll} /> : null}
        <View style={{ marginTop: 28, marginBottom: 12 }}><Logo size={64} caption={t('home.glad')} /></View>
      </ScrollView>
    </View>
  );
}
