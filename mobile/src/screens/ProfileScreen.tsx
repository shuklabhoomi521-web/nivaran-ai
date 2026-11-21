import React, { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import type { Api } from '../api';
import { useT } from '../i18n';
import { dobToInput, countCases, type Counts } from '../profileUtil';
import { GlassSurface } from '../glass';
import { c, s } from '../theme';
import type { Profile } from '../types';
import { Button, Card, ErrorText } from '../ui';

const GENDER_TEXT: Record<string, string> = { female: 'Female', male: 'Male', non_binary: 'Non-binary', prefer_not_to_say: 'Prefer not to say' };

function Tile({ n, label, color }: { n: number; label: string; color: string }) {
  return (
    <GlassSurface style={{ flexBasis: '47%', flexGrow: 1, padding: 14, gap: 2 }}>
      <Text style={{ fontSize: 30, fontWeight: '700', color }}>{n}</Text>
      <Text style={s.soft}>{label}</Text>
    </GlassSurface>
  );
}

export default function ProfileScreen({ api, profile, onEdit, onSignOut }: { api: Api; profile: Profile; onEdit: () => void; onSignOut?: () => void }) {
  const t = useT();
  const [counts, setCounts] = useState<Counts | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { api.listCases().then((cs) => setCounts(countCases(cs))).catch((e) => setErr((e as Error).message)); }, [api]);
  const rows: [string, string][] = [
    ['Name', profile.full_name], ['Gender', GENDER_TEXT[profile.gender] ?? profile.gender], ['Date of birth', dobToInput(profile.date_of_birth)],
    ['Mobile', profile.phone ?? 'Not given'], ['Email', profile.email ?? 'Not given'], ['City', profile.city ?? 'Not given'],
  ];
  return (
    <View style={s.screen}>
      <View style={s.header}><Text style={s.title}>{t('prof.title')}</Text></View>
      <ScrollView contentContainerStyle={s.body}>
        <Text style={s.h2}>{t('prof.numbers')}</Text>
        <ErrorText message={err} />
        {counts ? (
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 12 }}>
            <Tile n={counts.total} label={t('prof.total')} color={c.ink} />
            <Tile n={counts.ongoing} label={t('prof.ongoing')} color={c.brand} />
            <Tile n={counts.resolved} label={t('prof.resolved')} color={c.good} />
            <Tile n={counts.escalated} label={t('prof.escalated')} color={c.pink} />
            <Tile n={counts.closed} label={t('prof.stopped')} color={c.grey} />
          </View>
        ) : <Text style={s.soft}>{err ? '' : 'Loading…'}</Text>}
        <Card title={t('prof.details')}>
          {rows.map(([k, v]) => (<View key={k} style={{ flexDirection: 'row', gap: 8 }}><Text style={[s.soft, { width: 110 }]}>{k}</Text><Text style={[s.text, { flex: 1 }]}>{v}</Text></View>))}
          <Button label={t('prof.edit')} kind="ghost" onPress={onEdit} />
        </Card>
        {onSignOut ? <Button label={t('prof.signout')} kind="ghost" onPress={onSignOut} /> : null}
      </ScrollView>
    </View>
  );
}
