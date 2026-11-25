import React, { useCallback, useEffect, useState } from 'react';
import { RefreshControl, ScrollView, Text, View } from 'react-native';
import type { Api } from '../api';
import { ComplaintCard, useNexts } from '../cards';
import { greetingFor, niceNow } from '../greeting';
import { useT } from '../i18n';
import { Logo } from '../logo';
import { GlassSurface } from '../glass';
import { countCases, isOngoing } from '../profileUtil';
import { c, font, s } from '../theme';
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
  const counts = countCases(cases);
  const recent = [...cases].sort((a, b) => (a.created_on < b.created_on ? 1 : -1)).slice(0, 5);
  const nexts = useNexts(api, cases);

  return (
    <View style={s.screen}>
      <ScrollView contentContainerStyle={s.body} refreshControl={<RefreshControl refreshing={busy} onRefresh={load} />}>
        <View style={{ gap: 4, paddingTop: 4 }}>
          <Text style={{ fontFamily: font, fontSize: 26, fontWeight: '600', letterSpacing: -0.3, color: c.ink }}>{t(`greet.${greetingFor(now)}` as const)}{name ? `, ${name}` : ''}</Text>
          <Text style={s.soft}>{niceNow(now)}</Text>
        </View>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {([[counts.ongoing, t('kpi.open'), c.brand], [cases.filter((x) => x.state === 'new').length + cases.filter((x) => { const n = nexts[x.id]; return !!(n && n.action && n.action.days_overdue > 0 && x.state !== 'new' && isOngoing(x.state)); }).length, t('kpi.attention'), c.pink], [counts.escalated, t('kpi.escalated'), c.brown], [counts.resolved, t('kpi.resolved'), c.good]] as [number, string, string][]).map(([n, label, color]) => (
            <GlassSurface key={label} style={{ flexBasis: '47%', flexGrow: 1, paddingVertical: 12, paddingHorizontal: 14, borderTopWidth: 3, borderTopColor: color }}>
              <Text style={{ fontFamily: font, fontSize: 26, fontWeight: '600', color: c.ink }}>{n}</Text>
              <Text style={s.soft}>{label}</Text>
            </GlassSurface>
          ))}
        </View>
        <View style={s.row}>
          <View style={{ flex: 1 }}><Button label={t('nav.chat')} onPress={onChat} /></View>
          <View style={{ flex: 1 }}><Button label={t('nav.call')} kind="ghost" onPress={onCall} /></View>
        </View>
        <ErrorText message={err} />
        <Text style={[s.h2, { marginTop: 6, fontSize: 16 }]}>{t('home.recent')}</Text>
        {recent.length === 0 && !busy && !err ? <Text style={s.soft}>{t('home.none')}</Text> : null}
        {recent.map((item) => <ComplaintCard key={item.id} item={item} next={nexts[item.id]} onOpen={() => onOpen(item.id)} />)}
        {cases.length > 5 ? <Button label="See all my complaints" kind="ghost" onPress={onAll} /> : null}
        <View style={{ marginTop: 28, marginBottom: 12 }}><Logo size={44} caption={t('home.glad')} /></View>
      </ScrollView>
    </View>
  );
}
