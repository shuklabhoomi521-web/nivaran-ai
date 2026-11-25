import React, { useCallback, useEffect, useState } from 'react';
import { Pressable, RefreshControl, ScrollView, Text, View } from 'react-native';
import type { Api } from '../api';
import { ComplaintCard, useNexts } from '../cards';
import { GlassSurface } from '../glass';
import { useT } from '../i18n';
import { countCases, isOngoing, isResolved } from '../profileUtil';
import { c, s } from '../theme';
import type { TrackedCase } from '../types';
import { Button, ErrorText } from '../ui';

export default function ComplaintsScreen({ api, onOpen, onChat }: { api: Api; onOpen: (id: string) => void; onChat: () => void }) {
  const t = useT();
  const [cases, setCases] = useState<TrackedCase[]>([]);
  const [tab, setTab] = useState<'ongoing' | 'resolved'>('ongoing');
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => {
    setBusy(true);
    try { setCases(await api.listCases()); setErr(null); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }, [api]);
  useEffect(() => { void load(); }, [load]);
  const nexts = useNexts(api, cases);
  const n = countCases(cases);
  const shown = cases.filter((x) => (tab === 'ongoing' ? isOngoing(x.state) : isResolved(x.state))).sort((a, b) => (a.created_on < b.created_on ? 1 : -1));
  return (
    <View style={s.screen}>
      <View style={s.header}><Text style={s.title}>{t('cmp.title')}</Text></View>
      <View style={[s.row, { paddingHorizontal: 16, paddingBottom: 8 }]}>
        {([['ongoing', `${t('cmp.ongoing')} (${n.ongoing})`], ['resolved', `${t('cmp.resolved')} (${n.resolved + n.closed})`]] as const).map(([k, label]) => (
          <Pressable key={k} accessibilityRole="button" accessibilityState={{ selected: tab === k }} onPress={() => setTab(k)} style={{ flex: 1 }}>
            <GlassSurface radius={8} tint={tab === k ? c.navy : undefined} style={s.btnInner}>
              <Text style={tab === k ? s.btnText : s.btnGhostText}>{label}</Text>
            </GlassSurface>
          </Pressable>
        ))}
      </View>
      <ScrollView contentContainerStyle={s.body} refreshControl={<RefreshControl refreshing={busy} onRefresh={load} />}>
        <ErrorText message={err} />
        {shown.length === 0 && !busy && !err ? (
          <View style={{ gap: 10 }}>
            <Text style={s.soft}>{tab === 'ongoing' ? 'No ongoing complaints.' : 'No resolved complaints yet.'}</Text>
            {tab === 'ongoing' ? <Button label="Tell our AI in chat" onPress={onChat} /> : null}
          </View>
        ) : null}
        {shown.map((item) => <ComplaintCard key={item.id} item={item} next={nexts[item.id]} onOpen={() => onOpen(item.id)} />)}
        <Text style={[s.soft, { color: c.soft }]}>Follow-up dates come from the Nivaran schedule (day 3, 7 and 15 after the last contact). Nivaran prepares each follow-up and waits for your approval before anything is sent.</Text>
      </ScrollView>
    </View>
  );
}
