import React, { useEffect, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import type { Api } from './api';
import { STATE_COLOR, categoryLabel, followUpLine, prettyDate } from './format';
import { GlassSurface } from './glass';
import { fill, useT, type Key } from './i18n';
import { c, font, s } from './theme';
import type { NextResponse, TrackedCase } from './types';
import { isOngoing } from './profileUtil';
import { Chip } from './ui';

/** Loads the next-step info for each ongoing case (one small request each). */
export function useNexts(api: Api, cases: TrackedCase[]): Record<string, NextResponse | null> {
  const [m, setM] = useState<Record<string, NextResponse | null>>({});
  useEffect(() => {
    let live = true;
    cases.filter((x) => isOngoing(x.state)).forEach((x) => {
      api.nextStep(x.id).then((n) => { if (live) setM((o) => ({ ...o, [x.id]: n })); }).catch(() => { if (live) setM((o) => ({ ...o, [x.id]: null })); });
    });
    return () => { live = false; };
  }, [api, cases]);
  return m;
}

/** One complaint as a clean row: a coloured status edge, company, summary, and the next follow-up in plain words. */
export function ComplaintCard({ item, next, onOpen }: { item: TrackedCase; next: NextResponse | null | undefined; onOpen: () => void }) {
  const t = useT();
  const ongoing = isOngoing(item.state);
  const line = ongoing && next === undefined ? t('fu.checking') : followUpLine(t, next ?? null, item.state);
  const status = t(`state.${item.state}` as Key);
  const late = !!(next && next.action && next.action.days_overdue > 0 && ongoing);
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={`${item.company} · ${status}`} onPress={onOpen} style={{ marginBottom: 10 }}>
      <GlassSurface style={{ flexDirection: 'row' }}>
        <View style={{ width: 4, backgroundColor: STATE_COLOR[item.state] }} />
        <View style={[s.card, { flex: 1, gap: 6 }]}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
            <Text style={[s.h2, { fontSize: 16 }]}>{item.company}</Text>
            <Chip text={status} color={STATE_COLOR[item.state]} />
          </View>
          <Text style={[s.soft, { color: c.ink }]} numberOfLines={2}>{item.problem_summary}</Text>
          <Text style={{ fontFamily: font, fontSize: 13, fontWeight: '600', color: late ? c.bad : c.brand }}>{line}</Text>
          <Text style={s.soft}>{categoryLabel(item.category)} · {fill(t('fu.started'), { date: prettyDate(item.created_on) })}</Text>
        </View>
      </GlassSurface>
    </Pressable>
  );
}
