import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, Pressable, RefreshControl, Text, View } from 'react-native';
import type { Api } from '../api';
import { STATE_COLOR, caseTitle, categoryLabel, prettyDate } from '../format';
import { s, c } from '../theme';
import type { TrackedCase } from '../types';
import { Button, Chip, ErrorText } from '../ui';

export default function CasesScreen({ api, onOpen, onNew }: { api: Api; onOpen: (id: string) => void; onNew: () => void }) {
  const [cases, setCases] = useState<TrackedCase[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setBusy(true);
    try {
      setCases(await api.listCases());
      setErr(null);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }, [api]);

  useEffect(() => { void load(); }, [load]);

  return (
    <View style={s.screen}>
      <View style={s.header}>
        <Text style={s.title}>My cases</Text>
      </View>
      <View style={{ paddingHorizontal: 16, gap: 10 }}>
        <Button label="New case" onPress={onNew} />
        <ErrorText message={err} />
      </View>
      <FlatList
        data={cases}
        keyExtractor={(x) => x.id}
        contentContainerStyle={s.body}
        refreshControl={<RefreshControl refreshing={busy} onRefresh={load} />}
        ListEmptyComponent={<Text style={s.soft}>{busy || err ? '' : 'No cases yet. Tap "New case" and tell us the problem once, in your own words.'}</Text>}
        renderItem={({ item }) => (
          <Pressable accessibilityRole="button" accessibilityLabel={caseTitle(item.company, item.state)} onPress={() => onOpen(item.id)} style={[s.card, { marginBottom: 10 }]}>
            <Text style={s.h2}>{item.company}</Text>
            <Chip text={caseTitle(item.company, item.state).split(' · ')[1]} color={STATE_COLOR[item.state]} />
            <Text style={s.soft}>{categoryLabel(item.category)} · started {prettyDate(item.created_on)} · {item.events.length} update{item.events.length === 1 ? '' : 's'}</Text>
            <Text style={[s.soft, { color: c.ink }]} numberOfLines={2}>{item.problem_summary}</Text>
          </Pressable>
        )}
      />
    </View>
  );
}
